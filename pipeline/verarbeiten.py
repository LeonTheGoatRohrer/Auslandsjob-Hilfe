"""Ein Verarbeitungslauf ohne KI: Rohdaten → normalisieren → Zustand fortschreiben → vorfiltern.

    python -m pipeline.verarbeiten

Liest    daten/roh/*.json
Schreibt daten/aufbereitet/zustand.json      Zustand je Angebot über alle Läufe
         daten/aufbereitet/aenderungen.json  neu / geändert / geschlossen / Abruffehler dieses Laufs
         daten/aufbereitet/kandidaten.json   offene Angebote, die den Vorfilter bestehen (Eingabe für die KI-Bewertung)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))
from pipeline.normalisieren import normalisiere  # noqa: E402
from pipeline.vorfilter import grund_zum_ausschluss  # noqa: E402
from pipeline.zustand import aktualisiere  # noqa: E402


def lies_json(pfad, standard):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else standard


def schreibe_json(pfad, inhalt):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False, indent=1), encoding="utf-8")


def verarbeite(roh_ordner, aus_ordner, datum=None):
    datum = datum or datetime.now(timezone.utc).isoformat(timespec="seconds")
    roh_dateien = [lies_json(p, None) for p in sorted(Path(roh_ordner).glob("*.json"))]
    angebote = normalisiere(roh_dateien)
    vollstaendig = {r["quelle"]: bool(r.get("vollstaendig")) for r in roh_dateien}
    fehler = {k: t for r in roh_dateien for k, t in (r.get("fehler") or {}).items()}

    zustand_pfad = Path(aus_ordner) / "zustand.json"
    zustand = lies_json(zustand_pfad, {})
    lauf = aktualisiere(zustand, angebote, datum, vollstaendig, fehler)

    kandidaten, ausgeschlossen = [], {}
    for a in angebote:
        z = zustand[a["key"]]
        grund = "Geschlossen" if z["status"] == "geschlossen" else grund_zum_ausschluss(a)
        if grund:
            ausgeschlossen.setdefault(a["quelle"], {}).setdefault(grund, 0)
            ausgeschlossen[a["quelle"]][grund] += 1
        else:
            a["zustand"] = {k: z[k] for k in ("erstmals_gesehen", "zuletzt_gesehen", "status")}
            kandidaten.append(a)

    for r in roh_dateien:
        q = r["quelle"]
        lauf["zaehlung"].setdefault(q, {})
        lauf["zaehlung"][q].update({"roh": r["anzahl"], "abgerufen": r["abgerufen"],
                                    "ausgeschlossen": ausgeschlossen.get(q, {}),
                                    "kandidaten": sum(1 for a in kandidaten if a["quelle"] == q)})

    schreibe_json(zustand_pfad, zustand)
    schreibe_json(Path(aus_ordner) / "aenderungen.json", lauf)
    schreibe_json(Path(aus_ordner) / "kandidaten.json", {"datum": datum, "zaehlung": lauf["zaehlung"],
                                                          "kandidaten": kandidaten})
    return lauf, kandidaten


def main():
    lauf, kandidaten = verarbeite(BASIS / "daten" / "roh", BASIS / "daten" / "aufbereitet")
    for q, z in lauf["zaehlung"].items():
        print(f"{q:12} roh {z.get('roh', 0):5}  offen {z['offen']:5}  neu {z['neu']:4}  geändert {z['geaendert']:3}  "
              f"geschlossen {z['geschlossen']:3}  Fehler {z['abruf_fehler']:2}  → {z.get('kandidaten', 0):4} Kandidaten")
    print(f"\n{len(kandidaten)} Kandidaten → daten/aufbereitet/kandidaten.json")


if __name__ == "__main__":
    main()
