# Security notes

## Current scope

This is a static browser application with no server, account system, API keys, or file uploads. User-provided glossary text is rendered with `textContent`, not interpolated into HTML. Browser storage operations are guarded against unavailable/full storage.

## Known limitations

- `localStorage` is not encrypted and is not suitable for secrets.
- No automated security scan or cross-browser audit has been run as part of this phase.
- The external font import can be removed to eliminate that third-party request.
- No Content Security Policy or production hosting headers are configured because no deployment is configured.

## Before production

Review dependencies, add suitable security headers/CSP, test XSS and storage edge cases, check accessibility, test mobile browsers, and re-assess the threat model if APIs, accounts, models, or uploads are added. Do not claim the application is fully secure without testing.
