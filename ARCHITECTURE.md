# Architecture — Phase 1

The current implementation is intentionally small and static:
- `index.html`: semantic page structure and views.
- `src/styles/main.css`: design tokens, responsive layout and visual styles.
- `src/app.js`: view switching, form interactions and browser-local persistence.

No backend or translation service exists yet. The translate button is deliberately a capability boundary: it validates basic input and reports that no verified engine is connected. A future translation module should expose a small interface such as `translate(text, sourceLanguage, targetLanguage, options)` and return explicit errors for unsupported pairs; UI code should not depend on one model implementation.

Potential future modules should be added only when implemented: translation engine adapter, language registry, model loader/cache, quality checks, document import/export, and tests. Avoid empty placeholder files.
