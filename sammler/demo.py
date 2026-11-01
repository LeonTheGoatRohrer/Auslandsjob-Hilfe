"""Demo-Quelle: liest Angebote aus einer Datei statt aus dem Netz, um den Ablauf
"gefunden → geändert → geschlossen" reproduzierbar vorzuführen.

    DEMO_QUELLE=1 python -m sammler.demo            # liest tests/fixtures/demo_quelle.json
    python -m sammler.demo                          # ohne Variable: entfernt daten/roh/demo.json

Die Datei enthält eine Liste von Angeboten im Rohformat (siehe sammler/gemeinsam.py). Vorhandene
Angebote in der Datei gelten als offen, entfernte als geschlossen (vollstaendig=True).
"""

import json
import os

from sammler.gemeinsam import BASIS, ROH, speichere

DATEI = BASIS / "tests" / "fixtures" / "demo_quelle.json"


def sammle():
    if os.environ.get("DEMO_QUELLE") != "1":
        (ROH / "demo.json").unlink(missing_ok=True)
        print("demo: aus (DEMO_QUELLE nicht gesetzt)")
        return
    angebote = json.loads(DATEI.read_text(encoding="utf-8"))
    for a in angebote:
        a.setdefault("quelle", "demo")
    speichere("demo", angebote, vollstaendig=True)


if __name__ == "__main__":
    sammle()
