# Privacy notes

## Phase 1 data flow

- Source text stays in the page and is not sent to a translation API by this app.
- Glossary entries are stored in this browser's `localStorage`.
- The history preference is stored locally. Saving translation history is not yet implemented because real translation is not yet available.
- The optional Google Fonts CSS import makes a network request to a third party when the stylesheet loads. Remove that import for a stricter no-third-party-request setup.
- Browser storage is not encrypted by this application and may be accessible to people using the same browser profile/device.

## User controls

Use **Settings → Clear local data** to clear glossary and history. Browser/site-data controls can remove all local MANAR data. Avoid entering sensitive text on shared devices.

## Future requirements

Before adding analytics, accounts, remote translation, or document uploads, document what data leaves the device, purpose, retention, processors, security controls, and user consent/notice. Do not place secrets in frontend code.
