# MANAR Feature Matrix — Build 2

| Area | Available locally | Important boundary |
|---|---|---|
| Translator | Language selectors, swap, text counts, formatting, copy/edit UI, text download, file import | Real translation engine is not connected |
| Language choices | 30+ interface choices | None are verified model coverage |
| Documents | TXT, MD, CSV, JSON, SRT, VTT, HTML, XML import up to 5 MB; preview; segmentation; TXT export | PDF/DOCX/OCR are not implemented |
| Projects | Create, edit, delete, search, status, language pair, due date, task count | Local browser only; no shared team server |
| Translation memory | Add, search, delete, import/export JSON | No fuzzy matching engine yet |
| Glossary | Add terms, context, search, remove, CSV export | Not automatically enforced by a translation model |
| QA | Compare numbers, placeholders, HTML tags and optional text-length ratio | Mechanical checks do not judge meaning, style or correctness |
| Subtitles | SRT/VTT structural checks, cleanup, download | No audio transcription or automatic translation |
| Text tools | Case changes, cleanup, duplicate removal, sorting, sentence splitting, counts, reverse lines, download | Browser-side text operations |
| Admin console | Local metrics, language-choice listing, audit events, project shortcuts, backup import/export | No authentication, authorization or server-side administration |
| History/settings | Optional local history, local data clearing, text size and backup | Local storage is not encrypted and can be cleared by the browser |

## Data safety

All project and terminology data is stored in the current browser's local storage. It does not automatically sync to another device. Export a backup before clearing browser data. Never treat the local Admin console as a secure production admin panel.
