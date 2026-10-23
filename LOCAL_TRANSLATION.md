# Local translation engine (optional)

MANAR's web workspace runs without paid APIs. The `server.py` bridge can use
Argos Translate when it and a compatible language-pair package are installed.
No model is bundled, and no pair is claimed to be supported until the model is
installed and tested.

## Start the local workspace

Requires Python 3.10+:

```bash
python server.py
```

Open `http://127.0.0.1:4173`. Keep the server bound to localhost for personal use.

## Enable local translation

In a Python virtual environment:

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements-optional.txt
```

Then install an Argos language package for the exact source/target pair from a
trusted source and verify that its license allows your intended use. Model
packages can be large and may have separate licenses. Do not install a package
until you have reviewed its provenance, language pair, license, size, and
hardware requirements. The app's `/api/health` endpoint lists installed pairs.
Restart `server.py` after installing packages.

For a source-to-target pair to work, Argos must have a direct translation package
for that pair. This adapter does not invent translations, use paid services, or
silently call an online provider. Automatic language detection is not yet wired
to a verified detector, so choose the source language explicitly.

## Important production limits

The included server is for localhost development, not public deployment. It has
no accounts, team permissions, TLS, rate limiting, persistent server database,
or production-grade audit controls. Do not expose it directly to the internet.
