# MANAR shared API (starter backend)

This repo now includes `api_server.py`, a standard-library SQLite API for shared accounts, translator profiles, jobs, status changes, and audit events. It is a starter backend, not yet a complete production SaaS and the current browser UI still uses browser-local records for several screens. Do not represent those screens as synchronized across users until the UI is wired to these endpoints.

## Local setup

Use Python 3.11+ and set secrets in your shell (do not commit them):

```bash
# Linux/macOS
export MANAR_TOKEN_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export MANAR_ADMIN_SETUP_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python api_server.py
```

Windows PowerShell:

```powershell
$env:MANAR_TOKEN_SECRET = python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:MANAR_ADMIN_SETUP_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
python api_server.py
```

The API listens on `http://127.0.0.1:4174` by default. Health: `GET /api/health`. Bootstrap the first admin once using `POST /api/admin/bootstrap` with JSON `setupKey`, `email`, `name`, and a password of at least 16 characters. Remove `MANAR_ADMIN_SETUP_KEY` from the environment immediately after setup. The endpoint refuses to create a second admin.

## Available endpoints

- `POST /api/register` — client or translator account; password minimum 12 characters. Translator requires `nativeLanguage` and `languages`.
- `POST /api/login` — returns a one-day signed bearer token.
- `GET /api/me` — authenticated profile.
- `GET /api/jobs` — role-filtered job list.
- `POST /api/jobs` — authenticated client/admin submits a job.
- `POST /api/jobs/{id}/status` — admin-only status changes.
- `GET /api/translators` — translator directory.

Include `Authorization: Bearer <token>` for protected endpoints. The token secret must be 32+ characters. Database path can be changed with `MANAR_DB_PATH`.

## Before public launch — mandatory

This API must run behind a correctly configured HTTPS reverse proxy. It still needs production rate limiting, verified email, password reset, stronger session lifecycle/revocation, full organization-scoped permissions, translator application/assignment workflows, persistent-volume/backup verification, monitoring, and integration into all UI views. Translation engine and grammar QA must be separately installed/configured and tested for each advertised language pair. A free static host alone cannot run this API. Do not accept confidential client files until upload scanning, retention/deletion, and privacy procedures are implemented.
