# MANAR: checklist before inviting real customers

## Current status

The current project is a tested local-first prototype, not a production multi-user service. Automated checks cover selected UI, validation and API behavior; they do not prove all features work under real traffic.

## Do not launch the current build for real customer work until all blockers are closed

- [ ] Add a shared server-side database and migrations.
- [ ] Add authenticated accounts and server-enforced roles (admin, organization/client, translator).
- [ ] Enforce organization-level access boundaries on every server operation.
- [ ] Replace browser-local translator, organization and job records with shared server storage.
- [ ] Add translator application review, assignment workflow, client status view and notifications.
- [ ] Integrate an actual translation engine and only advertise verified language pairs.
- [ ] Add QA/grammar tooling; show warnings as suggestions, not guarantees.
- [ ] Add document upload protections, file size/type limits, malware scanning, and safe text extraction before accepting client files.
- [ ] Add rate limiting, CSRF protections where applicable, secure headers, secret management, audit trails and error monitoring.
- [ ] Test backup and restore, privacy/deletion requests, accessibility, mobile layouts, and concurrency.
- [ ] Deploy to an owner-controlled account, enable HTTPS, and run smoke tests on the public URL.

## Free-tier deployment warning

A static host can publish the current interface as a public demo, but it cannot turn browser-local data into a shared database or provide secure multi-user accounts. Do not accept confidential translation files or promise live AI translation on a static demo. Free plans have limits and can change; check current terms before deployment.

## Suggested staged rollout

1. Private demo with synthetic/sample data.
2. Small invited pilot after authentication, database and access-control checks pass.
3. Public launch after model/QA coverage, privacy, backup/restore and production smoke tests pass.

## Newly added shared API starter

`api_server.py` adds SQLite persistence, password hashing (PBKDF2-HMAC-SHA256), signed bearer tokens, role-filtered job reads, translator profile reads, admin bootstrap, status changes, and audit events. It is not yet integrated into every browser UI workflow and is not sufficient by itself for a public production launch. See `docs/SHARED_API.md`.
