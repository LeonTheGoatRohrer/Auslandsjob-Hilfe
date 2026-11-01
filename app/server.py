"""Lokaler Server für die Review-App.

    python app/server.py      →  http://localhost:8765

GET  /api/daten       Angebote (kuratiert + gesammelt, bewertet + gefiltert), Bewertungen, Kategorien, Quellen
POST /api/bewertung   {id, rating?, liked?, notiz?}  →  daten/aufbereitet/bewertungen.json
"""

import gzip
import json
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))
from pipeline.ranking import bewerte, lade_profil  # noqa: E402

STATIC = BASIS / "app" / "static"
ANGEBOTE_ANGEREICHERT = BASIS / "daten" / "aufbereitet" / "angebote.json"
ANGEBOTE_KURATIERT = BASIS / "daten" / "kuratiert" / "angebote.json"
QUELLEN = BASIS / "daten" / "kuratiert" / "quellen.json"
GESAMMELT = BASIS / "daten" / "aufbereitet" / "gesammelt.json"
KANDIDATEN = BASIS / "daten" / "aufbereitet" / "kandidaten.json"
BEWERTUNGEN = BASIS / "daten" / "aufbereitet" / "bewertungen.json"
PORT = 8765


def lies_json(pfad, standard):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else standard


def daten():
    profil = lade_profil()
    quelle = ANGEBOTE_ANGEREICHERT if ANGEBOTE_ANGEREICHERT.exists() else ANGEBOTE_KURATIERT
    return {
        "angebote": bewerte(lies_json(quelle, []) + lies_json(GESAMMELT, []), profil),
        "zaehlung": lies_json(KANDIDATEN, {}).get("zaehlung", {}),
        "bewertungen": lies_json(BEWERTUNGEN, {}),
        "kategorien": profil["kategorien"],
        "kernkriterien": profil["kernkriterien"],
        "quellen": lies_json(QUELLEN, []),
    }


def speichere_bewertung(eingabe):
    bewertungen = lies_json(BEWERTUNGEN, {})
    eintrag = bewertungen.setdefault(eingabe["id"], {})
    for feld in ("rating", "liked", "notiz"):
        if feld in eingabe:
            eintrag[feld] = eingabe[feld]
    eintrag["geaendert"] = datetime.now().isoformat(timespec="seconds")
    BEWERTUNGEN.parent.mkdir(parents=True, exist_ok=True)
    tmp = BEWERTUNGEN.with_suffix(".tmp")
    tmp.write_text(json.dumps(bewertungen, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(BEWERTUNGEN)
    return eintrag


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def sende_json(self, inhalt, status=200):
        body = json.dumps(inhalt, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        if "gzip" in self.headers.get("Accept-Encoding", ""):
            body = gzip.compress(body)
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/daten":
            self.sende_json(daten())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/bewertung":
            self.sende_json({"fehler": "unbekannter Pfad"}, 404)
            return
        laenge = int(self.headers.get("Content-Length", 0))
        eingabe = json.loads(self.rfile.read(laenge))
        self.sende_json(speichere_bewertung(eingabe))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print(f"Auslandsjob-Hilfe läuft auf http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
