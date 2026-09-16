# Ecomerce Service (FastAPI Backend)

A production-style FastAPI backend with async PostgreSQL, email-OTP login, JWT auth,
profile management with image upload, and multi-language (i18n) support.

## Tech Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy (async)** + **asyncpg** — PostgreSQL
- **Pydantic v2** / **pydantic-settings** — validation & config
- **python-jose** — JWT access tokens
- **bcrypt** — password hashing
- **smtplib** — OTP emails (Gmail SMTP)

## Project Structure

```
app/
  main.py                    # FastAPI app, lifespan (creates tables), static file mount
  api/
    router.py                # aggregates all routers
    deps.py                  # get_current_user (JWT auth), get_language (i18n)
    endpoints/
      registration.py        # POST /registration
      auth.py                # POST /login, POST /login/verify-otp
      profile.py             # GET/PUT /profile, POST /profile/image
      translations.py        # GET /Translations/{code}
  core/
    config.py                # Settings (.env driven)
    security.py               # password hashing, JWT create/decode
    mail.py                   # SMTP email sending (HTML, OTP template)
    i18n.py                    # translation loading/resolution
    logging.py
  db/
    session.py                 # async engine/session, get_db dependency
    base.py                    # SQLAlchemy DeclarativeBase
  models/
    user.py                    # User table
    otp.py                      # LoginOTP table
  schemas/                     # pydantic request/response models
  repositories/                # DB access layer (per model)
  services/                    # business logic layer
  locales/
    en.json, nl.json, de.json          # internal API message translations
    content/en.json, nl.json, de.json  # static site-content translations
tests/
migrations/                    # Alembic scaffold (not actively used yet, see Known Gaps)
uploads/                       # uploaded profile images (gitignored), served at /static
```

**Request flow / layering:**
`endpoint` (HTTP layer) → `service` (business logic) → `repository` (DB queries) → `model` (ORM table).
`schemas` define request/response shapes; `core` and `db` are shared utilities every layer can use.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # or requirements.txt for prod-only deps
cp .env.example .env                  # then fill in real values, see below
```

### Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@host:5432/dbname` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime (default 60) |
| `OTP_EXPIRE_MINUTES` | Login OTP lifetime (default 5) |
| `MAIL_SERVER` / `MAIL_PORT` | SMTP server, default `smtp.gmail.com:587` |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | SMTP login — for Gmail/Google Workspace, `MAIL_PASSWORD` **must** be an [App Password](https://myaccount.google.com/apppasswords) (16 chars, no spaces), not the normal account password |
| `MAIL_FROM` | Sender address (display name is hardcoded as "Ottogusto Support Team" in `core/mail.py`) |

### Database

Create the Postgres database/role yourself (e.g. via `createdb`/`psql` or pgAdmin4). On startup,
`app/main.py`'s lifespan hook runs `Base.metadata.create_all`, which creates any **missing** tables
automatically — but it does **not** alter existing tables. See Known Gaps below.

### Run

```bash
uvicorn app.main:app --reload
```

Docs: `http://127.0.0.1:8000/docs`

## API Endpoints

### Registration
- `POST /registration` — body: `name`, `email`, `address`, `password`, `confirm_password`.
  Hashes password, defaults `is_active=true`, returns the created user (no password).

### Auth (email + password → OTP → JWT)
- `POST /login` — body: `email`, `password`. Verifies credentials, generates a 6-digit OTP
  (expires in `OTP_EXPIRE_MINUTES`), emails it, returns a confirmation message.
- `POST /login/verify-otp` — body: `email`, `otp_code`. Validates the OTP (correct/unused/not expired),
  returns `{"access_token": "...", "token_type": "bearer"}`.

### Profile (protected — `Authorization: Bearer <access_token>`)
- `GET /profile` — current user's info.
- `PUT /profile` — update `name` and/or `address` (at least one required).
- `POST /profile/image` — multipart upload (JPEG/PNG/WEBP, max 5MB); serves the saved
  image at `/static/profile_images/<file>`.

### Translations (static content, public)
- `GET /Translations/{code}` — `code` is `en`, `nl`, or `de`. Returns a flat JSON object of
  site-content strings (footer links, hero banners, invoice notes, etc.) read from
  `app/locales/content/{code}.json`. Edit those files directly to add/change content — no
  deploy-time DB step required.

## Multi-language (i18n) for API messages

Error/success messages from the endpoints above (not the `/Translations` content) are translated
via `app/core/i18n.py` + `app/locales/{en,nl,de}.json`. Language is resolved per-request in this
priority order:

1. `?lang=nl` query parameter
2. `Accept-Language` header
3. default: `en`

Unsupported codes silently fall back to English. This also affects the OTP email body/subject.

**Known limitation:** pydantic field validators (e.g. "passwords do not match") run during request
parsing, before the language dependency resolves, so those specific messages stay in English.

## Known Gaps / Next Steps

- **No real Alembic migrations yet.** Tables are created via `Base.metadata.create_all` on startup,
  which only adds missing tables — it will NOT add new columns to existing tables. If you add/change
  a model field, you must manually `ALTER TABLE` (or set up real Alembic migrations, scaffold already
  present in `migrations/`).
- **No role/admin system.** All authenticated users have equal access; there's no way to restrict
  an action to admins only.
- Image validation is by declared `Content-Type` + byte size only (no deep file-content sniffing).
