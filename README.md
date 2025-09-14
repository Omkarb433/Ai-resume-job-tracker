# AI-Powered Resume Builder & Job Matcher (Django)

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env  # put your keys
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Visit http://127.0.0.1:8000/
- Login (top-right via /admin for now) then fill **Profile**.
- Add a **Job** (paste JD) → see **ATS** & **Match Score**.
- Export **PDF** from the header.
- Use **Improve Text** form or the inline one on the score page.

### Notes
- `services/ai.py` currently returns a trivial transformation. Replace with a real AI call (OpenAI, etc.).
- Switch SQLite to Postgres for production.
- Add authentication UI or use Django Allauth if needed.
