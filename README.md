# Poway Recovery Center

Multi-page website (`/`, deployed with GitHub Pages) plus a Flask backend (`backend/`) for user accounts, modeled on the Open Coding Society [pages](https://github.com/Open-Coding-Society/pages) + [flask](https://github.com/Open-Coding-Society/flask) setup.

## Run locally
```bash
make            # creates .venv, installs requirements, starts the API (port 8587) and the site (port 4000)
make stop       # stops both
```

Then visit `http://localhost:4000` and log in.

To run only the backend by hand:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py      # creates backend/instance/volumes/user_management.db and starts the API
```

### Accounts
`backend/main.py` creates these users when it starts (the list is `MEMBERS` in `main.py`). Existing users keep their password and profile; only their role is updated to match the list.

| Name | Username | Role |
| --- | --- | --- |
| Adya Shipekar | `adyashipekar` (or adya.shipekar1@gmail.com) | Admin |
| Anika Seksaria | `anikaseksaria` | Admin |
| Jailene Tang | `jailenetang` | Admin |
| Joan Kim | `joankim` | User |
| Ainsley Albert | `ainsleyalbert` | User |
| Samanvi Yachareni | `samanviyachareni` | User |

Starting passwords come from `backend/.env`: `ADMIN_PASSWORD` for the site admin and `<FIRSTNAME>_PASSWORD` for each member (e.g. `JOAN_PASSWORD`). That file is not committed to git. Anyone can change their password, email, and phone number from their profile page.

## Structure
- `index.html` — homepage
- `resources.html` — Mood Room, reflection wall, resource directory
- `programs.html` — programs and interactive meeting schedule (calendar)
- `about.html` — organization information
- `login.html` / `signup.html` — log in / create an account (backed by the Flask API)
- `profile.html` — edit name, email, phone and password; links to the calendar, resources, and programs
- `sass/styles.scss` — complete source styling
- `css/styles.css` — browser-ready compiled stylesheet
- `js/` — page behavior
- `js/api/config.js` — backend address (`pythonURI`), `fetchOptions`, and `login()`, following Open Coding Society pages
- `js/api/login.js` — checks `/api/id` on every page and switches "Log In" to "My Profile"
- `js/api/profile.js` — profile update, member list, and logout helpers
- `requirements.txt` — Python dependencies (points to `backend/requirements.txt`)
- `backend/main.py` — the whole Flask backend in one file: app/CORS/database config, `User` model, `@token_required` JWT cookie guard, REST API, and default users
- `backend/.env` — secret key and passwords (not committed)
- `backend/Dockerfile`, `backend/docker-compose.yml` — production server (gunicorn on port 8587), same setup as Open Coding Society flask
- `.github/workflows/jekyll-gh-pages.yml` — builds the site with `bundle exec jekyll build` (same Jekyll as `make`) and deploys it to GitHub Pages
- `backend/instance/volumes/user_management.db` — SQLite database (created on first run, not committed)

## API
| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/authenticate` | Log in `{uid, password}` (uid can be the username or email); sets an httpOnly JWT cookie |
| DELETE | `/api/authenticate` | Log out |
| GET | `/api/id` | Current user's profile |
| POST | `/api/user` | Sign up `{name, uid, email?, phone?, password}` and log in |
| PUT | `/api/user` | Update `{name, email, phone}` and/or `{current_password, new_password}` |
| GET | `/api/user` | Admin only: list every user |
| DELETE | `/api/user` | Admin only: delete a user `{uid}` |

## Deploying
**Frontend:** every push to `main` runs `.github/workflows/jekyll-gh-pages.yml`, which publishes the site to https://adyashipekar.github.io/poway-recovery-center/ (repo Settings → Pages → Source must be "GitHub Actions").

**Backend:** GitHub Pages only serves static files, so `backend/` runs on a server, like Open Coding Society flask:
```bash
cd backend
cp /path/to/your/.env .env     # SECRET_KEY, ADMIN_PASSWORD, DEFAULT_PASSWORD, IS_PRODUCTION=true
docker compose up -d --build   # serves the API on port 8587; database is kept in backend/instance/
```
Put it behind HTTPS (e.g. nginx + certbot, as in OCS `nginx_flask_8587.conf`), then set that https address as `deployedPythonURI` in `js/api/config.js` and push. Until then the live site works normally but shows that accounts are not available yet.

The meeting reservations and reflection wall still use browser localStorage. The Mood Room uses a local supportive categorizer and Apple Music search links.
