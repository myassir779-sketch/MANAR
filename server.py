#!/usr/bin/env python3
"""MANAR local web server with an optional Argos Translate adapter.

No network API is called. Translation runs locally only when Argos Translate and
an installed source/target language package are present.
"""
from __future__ import annotations
import json
import mimetypes
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
MAX_BODY = 200_000
HOST = os.environ.get("MANAR_HOST", "127.0.0.1")
PORT = int(os.environ.get("MANAR_PORT", "4173"))

def get_argos_languages():
    try:
        from argostranslate import translate
        return translate.get_installed_languages(), None
    except Exception:
        return [], "Argos Translate haijasakinishwa. Soma docs/LOCAL_TRANSLATION.md."

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        # Keep logs minimal; do not log request bodies or user text.
        print(f"[MANAR] {self.address_string()} - {fmt % args}")

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            langs, error = get_argos_languages()
            codes = sorted({lang.code for lang in langs})
            pairs = []
            for source in langs:
                for target in getattr(source, "translations", []):
                    pairs.append({"source": source.code, "target": target.to_lang.code})
            self.send_json(200, {
                "ok": True, "service": "MANAR local translation bridge",
                "engine": "argos-translate" if langs else None,
                "engineReady": bool(langs), "installedLanguages": codes,
                "installedPairs": pairs, "message": error or (
                    "Angalau lugha moja imewekwa; angalia jozi zinazopatikana."
                    if langs else "Hakuna modeli za tafsiri zilizowekwa bado."
                )
            })
            return
        if path.startswith("/api/"):
            self.send_json(404, {"ok": False, "error": "ENDPOINT_NOT_FOUND"})
            return
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/translate":
            self.send_json(404, {"ok": False, "error": "ENDPOINT_NOT_FOUND"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if size <= 0 or size > MAX_BODY:
            self.send_json(413, {"ok": False, "error": "INVALID_BODY_SIZE",
                                 "message": "Ombi halina maudhui au ni kubwa mno."})
            return
        try:
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "INVALID_JSON",
                                 "message": "Maombi hayana JSON sahihi."})
            return
        text = payload.get("text")
        source = payload.get("sourceLanguage")
        target = payload.get("targetLanguage")
        if not isinstance(text, str) or not text.strip():
            self.send_json(400, {"ok": False, "error": "EMPTY_INPUT",
                                 "message": "Weka maandishi ya kutafsiri kwanza."})
            return
        if len(text) > 50_000:
            self.send_json(413, {"ok": False, "error": "TEXT_TOO_LONG",
                                 "message": "Kikomo ni herufi 50,000 kwa ombi."})
            return
        if not isinstance(source, str) or not isinstance(target, str):
            self.send_json(400, {"ok": False, "error": "LANGUAGE_REQUIRED",
                                 "message": "Chagua lugha ya chanzo na lengwa."})
            return
        if source == "auto":
            self.send_json(422, {"ok": False, "error": "DETECTION_UNAVAILABLE",
                                 "message": "Utambuzi wa lugha haujaunganishwa. Chagua lugha ya chanzo mwenyewe."})
            return
        if source == target:
            self.send_json(422, {"ok": False, "error": "SAME_LANGUAGE",
                                 "message": "Chagua lugha mbili tofauti."})
            return
        try:
            from argostranslate import translate
            langs = translate.get_installed_languages()
            from_lang = next((x for x in langs if x.code == source), None)
            to_lang = next((x for x in langs if x.code == target), None)
            if from_lang is None or to_lang is None:
                self.send_json(503, {"ok": False, "error": "MODEL_UNAVAILABLE",
                                     "message": f"Modeli ya {source} → {target} haipo kwenye kifaa hiki."})
                return
            pair = from_lang.get_translation(to_lang)
            if pair is None:
                self.send_json(503, {"ok": False, "error": "PAIR_UNAVAILABLE",
                                     "message": f"Jozi ya {source} → {target} haijawekwa. Hakuna tafsiri iliyotengenezwa."})
                return
            translated = pair.translate(text)
            if not isinstance(translated, str) or not translated.strip():
                self.send_json(502, {"ok": False, "error": "EMPTY_MODEL_OUTPUT",
                                     "message": "Modeli haikutoa matokeo yanayoweza kutumika."})
                return
            self.send_json(200, {"ok": True, "translation": translated,
                                 "sourceLanguage": source, "targetLanguage": target,
                                 "engine": "Argos Translate (local)"})
        except ImportError:
            self.send_json(503, {"ok": False, "error": "ENGINE_NOT_INSTALLED",
                                 "message": "Argos Translate haijasakinishwa. Soma docs/LOCAL_TRANSLATION.md."})
        except Exception:
            self.send_json(500, {"ok": False, "error": "TRANSLATION_FAILED",
                                 "message": "Tafsiri imeshindikana. Hakuna matokeo yaliyokubaliwa."})

if __name__ == "__main__":
    print(f"MANAR inaendesha kwenye http://{HOST}:{PORT}")
    print("Hii ni local development server. Usiiweke wazi kwa internet bila backend hardening.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
