# Admin Console Guide — Build 2

The Admin console is accessed from the left navigation.

## What administrators can do in this build

- Review local counts for projects, glossary entries, translation-memory entries and audit events.
- Create a project and then manage its status, due date, language pair and task count in **Miradi**.
- Export the local workspace as a JSON backup.
- Import a MANAR workspace backup with `formatVersion: 2`; the interface asks before replacing current project, glossary, memory and history data.
- Review the local audit list and clear it if needed.
- Inspect interface language options and their explicitly unverified model status.

## Security boundary

This is a browser-local prototype. The admin navigation is not protected by server authentication, user roles or access control. Anyone using the same browser profile can open it and local data may be modified through browser developer tools. Do not deploy it as a public admin system. A production release requires server-side identity, authorization on every API operation, shared database, input validation, audit integrity and security review.
