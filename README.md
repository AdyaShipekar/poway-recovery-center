# Poway Recovery Center

Static multi-page website.

## Run locally
Open `index.html` in a browser, or run:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Structure
- `index.html` — homepage
- `resources.html` — Mood Room, reflection wall, resource directory
- `programs.html` — programs and interactive meeting schedule
- `about.html` — organization information
- `login.html` — login interface
- `sass/styles.scss` — complete source styling
- `css/styles.css` — browser-ready compiled stylesheet
- `js/` — page behavior

The login, meeting reservations, and reflection wall are front-end demonstrations using browser localStorage. The Mood Room uses a local supportive categorizer and Apple Music search links; no API keys or user data are transmitted.
