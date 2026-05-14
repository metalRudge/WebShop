# Webshop — Phase 1

Minimal Django scaffold serving a single Hello World / project-start page.
SQLite for the database, Tailwind via the Play CDN for a lightweight visual
baseline. Nothing more.

## Requirements

- Python 3.10+
- Django 5+ (tested on 6.0)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Then open <http://localhost:8000/>.

The Django admin is mounted at `/admin/`. Create a superuser if you want to
log in:

```bash
python manage.py createsuperuser
```

## Project layout

```
webshop_phase1/
├── manage.py
├── db.sqlite3                # created on first `migrate`
├── webshop/                  # project package (settings, root urls, wsgi/asgi)
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── pages/                    # single app for the Phase 1 homepage
    ├── apps.py
    ├── urls.py
    ├── views.py
    └── templates/pages/home.html
```

A single `pages` app keeps things conventional and DRY. Routes live in
`pages/urls.py` and are mounted at the project root in `webshop/urls.py`.

## Phase roadmap

- **Phase 1 — Hello World (this commit).** Working Django project, single
  homepage, Tailwind-ready baseline, SQLite.
- **Phase 2 — Navbar & Footer.** Introduce a `base.html` template with
  shared navbar and footer; `pages/home.html` will extend it.
- **Phase 3 — Categories & Search.** Catalog app with category models,
  list/detail views, and a search form.
- **Phase 4 — Auth.** User accounts and JWT auth for API clients.
- **Phase 5 — Cart.** Cart state on the client via `sessionStorage`, with
  a server-side checkout-time validation pass.
- **Phase 6 — Checkout.** Order model, payment hook, order confirmation.
- **Phase 7 — Admin dashboard.** Staff-facing dashboard beyond the default
  Django admin.

## Intentionally deferred (do NOT bypass — handle in their phase)

These concerns are out of scope for Phase 1 and must be implemented
properly in the phases they belong to. Do not paper over them now.

- **CORS.** Will be configured (likely via `django-cors-headers`) when a
  separate frontend or API consumer is introduced.
- **CSRF.** Django's CSRF middleware is already active. When AJAX/JWT
  endpoints are added, follow Django's CSRF guidance for SPA clients —
  do not disable middleware globally.
- **JWT auth.** Planned for Phase 4 (e.g. `djangorestframework-simplejwt`).
  Do not add ad-hoc token logic before then.
- **`sessionStorage` cart.** Planned for Phase 5. Cart state will live in
  the browser's `sessionStorage`; server endpoints will validate and
  reconcile at checkout. Do not stub a cart in Phase 1.
- **Tailwind build pipeline.** Phase 1 uses the Play CDN for speed. A
  proper `tailwindcss` build (or `django-tailwind`) lands when the
  navbar/footer come in.
- **Production settings.** `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, and
  the generated `SECRET_KEY` are dev defaults. Replace before any deploy.

## Deployment notes

- Start command: `python manage.py runserver 0.0.0.0:8000` for local dev,
  or `gunicorn webshop.wsgi:application --bind 0.0.0.0:8000` for prod.
- Default port: `8000`.
- Database: SQLite file at `db.sqlite3` next to `manage.py`. No external
  database setup is required for Phase 1. PostgreSQL migration is a
  later-phase task.
- No Docker in Phase 1.
