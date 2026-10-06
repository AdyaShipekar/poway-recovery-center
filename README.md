# Poway Recovery Center

Multi-page website deployed with GitHub Pages. User accounts are handled by a separate Flask backend, [poway-recovery-center-api](https://github.com/AdyaShipekar/poway-recovery-center-api). This is the same split as the Open Coding Society [pages](https://github.com/Open-Coding-Society/pages) (frontend) and [flask](https://github.com/Open-Coding-Society/flask) (backend) repos.

## Run locally
Clone both repos next to each other, then start each one:
```bash
cd poway-recovery-center-api
make            # creates .venv, installs requirements, starts the API on http://localhost:8587

cd ../poway-recovery-center
make            # starts the site on http://localhost:4000
```
Then visit `http://localhost:4000` and log in. `make stop` in either repo stops that server.

The site still works without the backend running, but logging in, signing up, and the profile page show that the server can't be reached.

## Structure
- `index.html`: homepage
- `resources.html`: Mood Room, reflection wall, resource directory
- `programs.html`: programs and interactive meeting schedule (calendar)
- `about.html`: organization information
- `login.html` / `signup.html`: log in / create an account (backed by the API)
- `profile.html`: edit name, email, phone and password; links to the calendar, resources, and programs
- `sass/styles.scss`: complete source styling
- `css/styles.css`: browser-ready compiled stylesheet
- `js/`: page behavior
- `js/api/config.js`: backend address (`pythonURI`), `fetchOptions`, and `login()`, following Open Coding Society pages
- `js/api/login.js`: checks `/api/id` on every page and switches "Log In" to "My Profile"
- `js/api/profile.js`: profile update, member list, and logout helpers
- `.github/workflows/jekyll-gh-pages.yml`: builds the site with `bundle exec jekyll build` (same Jekyll as `make`) and deploys it to GitHub Pages

## Deploying
Every push to `main` runs `.github/workflows/jekyll-gh-pages.yml`, which publishes the site to https://adyashipekar.github.io/poway-recovery-center/ (repo Settings → Pages → Source must be "GitHub Actions").

GitHub Pages only serves static files, so the API has to be deployed separately (see the poway-recovery-center-api README). Once it's running on HTTPS, set that address as `deployedPythonURI` in `js/api/config.js` and push.

The meeting reservations and reflection wall still use browser localStorage. The Mood Room uses a local supportive categorizer and Apple Music search links.
