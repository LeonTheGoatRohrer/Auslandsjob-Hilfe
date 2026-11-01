"""Liest die Quellen-Tabellen aus docs/recherche/*.md und schreibt daten/kuratiert/quellen.json.

    python pipeline/quellen_aus_recherche.py
"""

import json
import re
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
DATEIEN = {"plattformen.md": "Jobbörsen & Programme", "maritim-naturschutz.md": "Maritim & Naturschutz",
           "leads.md": "Leads (Betriebe finden)"}
AUSGABE = BASIS / "daten" / "kuratiert" / "quellen.json"

# Spaltenkopf (Teilstring, klein) → Feld; erste passende Regel gewinnt
SPALTEN = [("passend", "passend"), ("gesamt", "gesamt"), ("angebote", "gesamt"), ("url", "url"),
           ("quelle", "name"), ("name", "name"), ("organisation", "name"), ("fokus", "fokus"),
           ("handwerk", "fokus"), ("wofür", "fokus"), ("zugriff", "zugriff"), ("passung", "passung"),
           ("finanzierung", "kosten"), ("kosten", "kosten"), ("gebühr", "kosten"), ("zugang", "zugang")]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Tabellen, die Zusammenfassungen statt Quellen enthalten
KEINE_QUELLEN = re.compile(r"Summe|Top|Konkrete|Mengenschätzung|Kontaktdaten|Kennzeichnung|Stichprobe|Messung")


def sauber(text):
    return LINK.sub(r"\1", text).replace("**", "").replace("✔", "").strip()


def zellen(zeile):
    return [z.strip() for z in zeile.strip().strip("|").split("|")]


def lies(datei, bereich):
    quellen, abschnitt, kopf = [], bereich, None
    for zeile in (BASIS / "docs" / "recherche" / datei).read_text(encoding="utf-8").splitlines():
        if zeile.startswith("#"):
            abschnitt, kopf = zeile.lstrip("# ").strip(), None
        elif not zeile.startswith("|"):
            kopf = None
        elif kopf is None:
            kopf = []
            for name in zellen(zeile):
                feld = next((f for k, f in SPALTEN if k in name.lower()), None)
                kopf.append(feld if feld not in kopf else None)
        elif set(zeile) <= set("|-: ") or KEINE_QUELLEN.search(abschnitt):
            continue
        else:
            werte = zellen(zeile)
            if len(werte) < len(kopf) - 1 or sum(1 for w in werte if w) < 3:
                continue  # Gruppen-Zeile wie "| **EU / Jugend** |"
            eintrag = {"bereich": bereich, "abschnitt": re.sub(r"^\d+[a-z]?\.\s*", "", abschnitt), "datei": datei}
            for feld, wert in zip(kopf, werte):
                if not feld:
                    continue
                if feld in ("name", "url") and "url" not in eintrag:
                    link = LINK.search(wert) or re.search(r"https?://\S+", wert)
                    if link:
                        eintrag["url"] = link.group(2) if link.re is LINK else link.group(0).rstrip(",")
                eintrag.setdefault(feld, sauber(wert))
            if eintrag.get("url"):
                url = eintrag["url"].split()[0].rstrip(",;")
                url = url if url.startswith("http") else "https://" + url
                if "." in url:
                    eintrag["url"] = url
                else:
                    del eintrag["url"]
            if eintrag.get("name"):
                quellen.append(eintrag)
    return quellen


def main():
    quellen = [q for datei, bereich in DATEIEN.items() for q in lies(datei, bereich)]
    AUSGABE.write_text(json.dumps(quellen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(quellen)} Quellen → {AUSGABE.relative_to(BASIS)}")


if __name__ == "__main__":
    main()
