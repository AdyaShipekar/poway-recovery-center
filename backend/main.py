"""
Poway Recovery Center - Flask backend

Modeled on the Open Coding Society flask repository (__init__.py, model/user.py,
api/user.py, api/authorize.py and main.py), combined into this single file.

Run it with:
    python backend/main.py

On start it creates the user management database (backend/instance/volumes/user_management.db),
adds the default users, and serves the API on http://localhost:8587
"""
import os
import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, Blueprint, request, current_app, g, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


# Load environment variables from backend/.env, no matter which folder main.py is run from
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


# ----------------------------------------------------------------------------
# App setup (OCS __init__.py)
# ----------------------------------------------------------------------------

# Setup of key Flask object (app); instance folder lives in backend/instance
app = Flask(__name__, instance_path=os.path.join(basedir, 'instance'))

# Configure Flask Port, default to 8587 which is the same as Open Coding Society flask
app.config['FLASK_PORT'] = int(os.environ.get('FLASK_PORT') or 8587)

# Allowed servers for cross-origin resource sharing (CORS)
allowed_origins = [
    'http://localhost:4000',
    'http://127.0.0.1:4000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://adyashipekar.github.io',  # Deployed GitHub Pages site
]
# Any other deployed frontend(s), comma separated in .env
allowed_origins += [o.strip() for o in (os.environ.get('ALLOWED_ORIGINS') or '').split(',') if o.strip()]

cors = CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Admin defaults
app.config['ADMIN_USER'] = os.environ.get('ADMIN_USER') or 'Adya Shipekar'
app.config['ADMIN_UID'] = os.environ.get('ADMIN_UID') or 'adyashipekar'
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL') or 'adya.shipekar1@gmail.com'
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD') or os.environ.get('DEFAULT_PASSWORD') or 'password'
# Password given to every other seeded user until they change it on their profile page
app.config['DEFAULT_PASSWORD'] = os.environ.get('DEFAULT_PASSWORD') or 'password'
# Members created on first run: (name, uid, role). Each starting password is read from
# <FIRSTNAME>_PASSWORD in .env (e.g. ANIKA_PASSWORD), falling back to DEFAULT_PASSWORD.
app.config['MEMBERS'] = [
    ('Anika Seksaria', 'anikaseksaria', 'Admin'),
    ('Jailene Tang', 'jailenetang', 'Admin'),
    ('Joan Kim', 'joankim', 'User'),
    ('Ainsley Albert', 'ainsleyalbert', 'User'),
    ('Samanvi Yachareni', 'samanviyachareni', 'User'),
]

# Browser settings
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'prc-flask-secret-key-set-SECRET_KEY-in-env'
app.config['JWT_TOKEN_NAME'] = os.environ.get('JWT_TOKEN_NAME') or 'jwt_python_flask'
app.config['JWT_TOKEN_MAX_AGE'] = int(os.environ.get('JWT_TOKEN_MAX_AGE') or 604800)  # 1 week
# Production = frontend on GitHub Pages + backend on its own HTTPS domain,
# which needs SameSite=None; Secure cookies (same switch OCS uses)
app.config['IS_PRODUCTION'] = (os.environ.get('IS_PRODUCTION') or 'false').lower() == 'true'

# Database settings - SQLite in backend/instance/volumes/ (OCS layout)
dbName = 'user_management'
os.makedirs(os.path.join(app.instance_path, 'volumes'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(app.instance_path, 'volumes', dbName + '.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ----------------------------------------------------------------------------
# User model (OCS model/user.py)
# ----------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PHONE_PATTERN = re.compile(r'^\+?[\d\s().-]{7,20}$')
UID_PATTERN = re.compile(r'^[A-Za-z0-9._-]{3,40}$')


class User(db.Model):
    """
    User Model

    Attributes:
        id (Column): Primary key.
        _name (Column): The user's full name.
        _uid (Column): Unique username, used to log in.
        _email (Column): Optional unique email address, can also be used to log in.
        _phone (Column): Optional phone number.
        _password (Column): Hashed password.
        _role (Column): "User" or "Admin".
        token_version (Column): Bumped on password change so older login tokens stop working.
        created_at (Column): When the account was created.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _email = db.Column(db.String(255), unique=True, nullable=True)
    _phone = db.Column(db.String(32), unique=False, nullable=True)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    token_version = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, name, uid, password=None, email=None, phone=None, role="User"):
        self._name = name
        self._uid = uid.strip().lower()
        self._email = email.strip().lower() if email else None
        self._phone = phone.strip() if phone else None
        self._role = role
        self.token_version = 0
        self.set_password(password or app.config['DEFAULT_PASSWORD'])

    @property
    def name(self):
        return self._name

    @property
    def uid(self):
        return self._uid

    @property
    def email(self):
        return self._email

    @property
    def phone(self):
        return self._phone

    @property
    def role(self):
        return self._role

    def is_admin(self):
        return self._role == "Admin"

    def set_password(self, password):
        """ Hash the password and invalidate any login tokens issued before the change """
        self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)
        self.token_version = (self.token_version or 0) + 1

    def is_password(self, password):
        return check_password_hash(self._password, password)

    @staticmethod
    def validate(name=None, uid=None, email=None, phone=None, password=None):
        """ Returns an error message for the first invalid field supplied, or None """
        if name is not None and not name.strip():
            return 'Name is required'
        if uid is not None and not UID_PATTERN.match(uid.strip()):
            return 'Username must be 3-40 letters, numbers, dots, dashes or underscores'
        if email and not EMAIL_PATTERN.match(email.strip()):
            return 'Please enter a valid email address'
        if phone and not PHONE_PATTERN.match(phone.strip()):
            return 'Please enter a valid phone number'
        if password is not None and len(password) < 6:
            return 'Password must be at least 6 characters'
        return None

    def create(self):
        """ Add the user to the database; returns None if the username or email is taken """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "email": self.email or "",
            "phone": self.phone or "",
            "role": self.role,
            "is_admin": self.is_admin(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def update(self, inputs):
        """ Update name, email and/or phone from a dict; returns None if the email is taken """
        if 'name' in inputs:
            self._name = inputs['name'].strip()
        if 'email' in inputs:
            self._email = inputs['email'].strip().lower() or None
        if 'phone' in inputs:
            self._phone = inputs['phone'].strip() or None
        try:
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        db.session.delete(self)
        db.session.commit()


def initUsers():
    """
    Create the database tables and the default users.
    New users are created with their starting password; existing users keep their
    password and profile, but get the role listed here.
    """
    with app.app_context():
        db.create_all()
        seeds = [(app.config['ADMIN_USER'], app.config['ADMIN_UID'], 'Admin',
                  app.config['ADMIN_PASSWORD'], app.config['ADMIN_EMAIL'])]
        for name, uid, role in app.config['MEMBERS']:
            password = os.environ.get(name.split()[0].upper() + '_PASSWORD') or app.config['DEFAULT_PASSWORD']
            seeds.append((name, uid, role, password, None))

        for name, uid, role, password, email in seeds:
            user = User.query.filter_by(_uid=uid).first()
            if user is None:
                User(name=name, uid=uid, email=email, password=password, role=role).create()
            elif user.role != role:
                user._role = role
                db.session.commit()


# ----------------------------------------------------------------------------
# Authorization (OCS api/authorize.py)
# ----------------------------------------------------------------------------

def token_required(roles=None):
    '''
    Guards API endpoints with the JWT stored in the request cookie.
    Sets g.current_user for the decorated function.
      401 / Unauthorized: token missing, invalid, expired, or user no longer exists
      403 / Forbidden: user does not have one of the required roles
    '''
    if isinstance(roles, str):
        roles = [roles]

    def decorator(func_to_guard):
        @wraps(func_to_guard)
        def decorated(*args, **kwargs):
            token = request.cookies.get(current_app.config["JWT_TOKEN_NAME"])
            if not token:
                return {"message": "Authentication Token is missing!", "data": None, "error": "Unauthorized"}, 401
            try:
                data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            except jwt.PyJWTError:
                return {"message": "Your session has expired. Please log in again.", "data": None, "error": "Unauthorized"}, 401

            user = User.query.filter_by(_uid=data.get("_uid")).first()
            if user is None or data.get("token_version") != user.token_version:
                return {"message": "Invalid Authentication token!", "data": None, "error": "Unauthorized"}, 401
            if roles and user.role not in roles:
                return {"message": "Insufficient permissions.", "data": None, "error": "Forbidden"}, 403

            g.current_user = user
            return func_to_guard(*args, **kwargs)
        return decorated
    return decorator


# ----------------------------------------------------------------------------
# User API (OCS api/user.py)
# ----------------------------------------------------------------------------

user_api = Blueprint('user_api', __name__, url_prefix='/api')
api = Api(user_api)


def set_token_cookie(resp, token, max_age):
    if current_app.config["IS_PRODUCTION"]:
        resp.set_cookie(current_app.config["JWT_TOKEN_NAME"], token, max_age=max_age,
                        secure=True, httponly=True, path='/', samesite='None')
    else:
        resp.set_cookie(current_app.config["JWT_TOKEN_NAME"], token, max_age=max_age,
                        secure=False, httponly=True, path='/', samesite='Lax')
    return resp


def login_response(user, status=200):
    token = jwt.encode(
        {
            "_uid": user.uid,
            "token_version": user.token_version,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=current_app.config["JWT_TOKEN_MAX_AGE"]),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    resp = jsonify({"message": f"Authentication for {user.uid} successful", "user": user.read()})
    resp.status_code = status
    return set_token_cookie(resp, token, current_app.config["JWT_TOKEN_MAX_AGE"])


class UserAPI:
    class _ID(Resource):  # Current user identification
        @token_required()
        def get(self):
            return jsonify(g.current_user.read())

    class _CRUD(Resource):  # Users API operation for Create, Read, Update, Delete
        def post(self):
            """ Sign up: create a new account and log it in """
            body = request.get_json(silent=True) or {}
            fields = {k: (body.get(k) or '').strip() for k in ('name', 'uid', 'email', 'phone')}
            password = body.get('password') or ''

            error = User.validate(password=password, **fields)
            if error:
                return {"message": error}, 400

            user = User(password=password, **fields).create()
            if user is None:
                return {"message": "That username or email is already registered"}, 409
            return login_response(user, 201)

        @token_required("Admin")
        def get(self):
            """ Admin only: list every user """
            return jsonify([user.read() for user in User.query.order_by(User.id).all()])

        @token_required()
        def put(self):
            """ Update the current user's name, email, phone and/or password """
            user = g.current_user
            body = request.get_json(silent=True) or {}
            updates = {k: str(body[k]) for k in ('name', 'email', 'phone') if k in body}

            error = User.validate(**updates)
            if error:
                return {"message": error}, 400

            new_password = body.get('new_password')
            if new_password:
                if not user.is_password(body.get('current_password') or ''):
                    return {"message": "Current password is incorrect"}, 403
                error = User.validate(password=new_password)
                if error:
                    return {"message": error}, 400
                user.set_password(new_password)

            if user.update(updates) is None:
                return {"message": "That email is already registered to another account"}, 409
            # Password changes bump token_version, so hand back a fresh login cookie
            return login_response(user) if new_password else jsonify(user.read())

        @token_required("Admin")
        def delete(self):
            """ Admin only: delete a user by uid """
            body = request.get_json(silent=True) or {}
            user = User.query.filter_by(_uid=(body.get('uid') or '').lower()).first()
            if user is None:
                return {"message": "User not found"}, 404
            if user.id == g.current_user.id:
                return {"message": "Admins cannot delete their own account"}, 400
            user.delete()
            return {"message": f"Deleted user {user.uid}"}

    class _Security(Resource):  # Login and logout
        def post(self):
            """ Log in with username (or email) and password """
            body = request.get_json(silent=True) or {}
            uid = (body.get('uid') or '').strip().lower()
            if not uid:
                return {"message": "User ID is missing"}, 401
            password = body.get('password')
            if not password:
                return {"message": "Password is missing"}, 401

            user = User.query.filter((User._uid == uid) | (User._email == uid)).first()
            if user is None or not user.is_password(password):
                return {"message": "Invalid user id or password"}, 401
            return login_response(user)

        def delete(self):
            """ Log out by expiring the token cookie """
            return set_token_cookie(jsonify({"message": "Logged out"}), '', 0)

    api.add_resource(_ID, '/id')
    api.add_resource(_CRUD, '/user')
    api.add_resource(_Security, '/authenticate')


app.register_blueprint(user_api)


@app.route('/')
def index():
    return jsonify({"service": "Poway Recovery Center API", "status": "ok"})


# Create the database and default users whenever the app starts (python main.py or gunicorn)
initUsers()

if __name__ == "__main__":
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Server running: http://localhost:{app.config['FLASK_PORT']}")
    app.run(debug=True, host="0.0.0.0", port=app.config['FLASK_PORT'], use_reloader=False)
