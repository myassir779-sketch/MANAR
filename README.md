# MANAR

MANAR is a cost-conscious, browser-first translation workspace. This repository is **Phase 1**: it establishes a responsive interface and working local glossary/settings. It does **not** yet perform real machine translation.

## Current status

- Responsive HTML/CSS/JavaScript interface.
- Source/target language selectors and swap control.
- Input character counter, clear control, adjustable source text size, and honest unavailable-engine messaging.
- Optional local-history preference (history saving is not connected to translations yet).
- Local glossary stored in browser `localStorage`.
- Local data clearing and privacy/cost/security documentation.
- No backend, API key, paid API, payment gateway, subscription, or deployment configured.

## Run locally

No third-party package install is required. Open `index.html` in a modern browser through a local static server (ES modules work most reliably on localhost). Node.js 18+ can run the built-in test suite with `npm test`; no `npm install` is needed. Some browser features (such as clipboard access) may require localhost or HTTPS.

## Project layout

- `index.html` — application markup.
- `src/styles/main.css` — responsive visual system.
- `src/app.js` — navigation and local interactions.
- `src/config/languages.js` — explicit language registry; all pairs remain unverified.
- `src/services/translation/translator.js` — safe translation boundary; refuses to invent output.
- `src/services/storage/local-storage.js` — guarded browser-storage helpers.
- `src/services/language-detection/`, `src/services/model-loader/`, `src/services/connectivity/` — safe service boundaries that do not guess or download models.
- `src/utils/` — text validation helpers.
- `src/features/` — feature scope and implementation notes.
- `tests/` — Node built-in tests for registry, storage, translation boundary, structure, and a basic XSS regression check.
- `docs/` — architecture, deployment, supported-language and troubleshooting notes.
- `tests/` — manual Phase 1 test checklist.

## Important translation limitation

Language options in this starter are interface choices only. No language pair is currently verified for actual translation. The translate action intentionally does not invent a result or send text to an external service. Phase 2 must select and verify a specific model, its license, runtime compatibility, language directions, resource requirements, and test quality before enabling translation.

## Cost promise

No paid services are configured or activated by this code. Review `COST_POLICY.md` before adding any external service. No live hosting or public URL has been created or verified.

## Current release status (important)

This release is a **local prototype**, not a fully deployed multi-user service. Translator profiles, organizations, incoming jobs and other workspace data are stored in the current browser's local storage; they are not automatically shared with other people or computers. Do not enter confidential client material until a secure server and privacy controls are deployed.

The language directory lists languages but does not guarantee that an AI translation model exists for every language pair. The optional local Argos bridge requires Argos Translate and the exact model packages to be installed. Grammar QA and document-processing capabilities must be tested and connected before being advertised as production-ready.

### Run locally

- Install Node.js 18 or newer.
- From this folder run `npm test` and `npm run check`.
- For the optional Python API, run `python server.py` (install the optional dependencies/model separately as documented in `docs/LOCAL_TRANSLATION.md`).
- Open `index.html` in a browser for the local workspace. For browser/API integration, serve it from a local HTTP server as described in the deployment docs.

See `PROGRESS.md`, `docs/DEPLOYMENT.md`, `docs/LOCAL_TRANSLATION.md` and `SECURITY.md` before any public deployment.


## Before public launch

Read [`docs/GO-LIVE-BLOCKERS.md`](docs/GO-LIVE-BLOCKERS.md). This build is a local-first prototype; static hosting publishes a demo only and does not provide shared records, secure multi-user accounts, or a production translation engine. Do not use it for confidential customer work until the blockers are closed.

## Shared API starter (new)

A small SQLite-backed API is included in `api_server.py` for shared accounts, translator profiles, and job intake. Setup and security limitations are documented in [`docs/SHARED_API.md`](docs/SHARED_API.md). **This is not yet a public-launch-ready full-stack deployment**: several existing UI screens still store data in the browser and must be wired to the API; production hosting, HTTPS, email verification, rate limits, backups, translation models, and grammar QA need configuration and verification.
