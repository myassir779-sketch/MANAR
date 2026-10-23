# MANAR progress

## Current build
- 20 JavaScript tests pass.
- 6 Python tests pass (including password hashing/token checks and local API behavior).
- JavaScript syntax checks pass.
- Shared API starter added: SQLite database, roles (admin/client/translator), PBKDF2 password hashing, signed one-day bearer tokens, admin bootstrap, job intake/status updates, translator profile listing, audit events.
- API smoke test passed: bootstrap admin, register client, submit job.

## Not yet complete
- The existing browser UI has not been fully migrated from localStorage to the shared API.
- Production HTTPS hosting has not been deployed; no public URL exists.
- API still needs rate limiting, email verification/reset, token revocation, full organization-level authorization, operational monitoring, backup/restore drills and production hardening.
- AI translation works only with a supported engine and installed language pair; no claim of universal language coverage.
- Grammar/QA engine is not yet fully integrated or validated across all languages.
- Do not accept confidential documents or real paid customer work until launch blockers are closed.
