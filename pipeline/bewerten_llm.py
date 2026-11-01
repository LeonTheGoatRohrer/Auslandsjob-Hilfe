"""Bewertet die Kandidaten aus dem Vorfilter mit Claude (über die Claude-Code-CLI, also dein Abo).

    python pipeline/bewerten_llm.py            # alle noch nicht bewerteten Kandidaten
    python pipeline/bewerten_llm.py --max 16   # nur ein paar, zum Testen
    python pipeline/bewerten_llm.py --export ORDNER   # Aufträge als Dateien schreiben (für Bewertung ohne CLI)
    python pipeline/bewerten_llm.py --import ORDNER   # Antworten (*.antwort.json) übernehmen

Liest    daten/aufbereitet/kandidaten.json, config/profil.yaml
Merkt    daten/aufbereitet/llm_cache.json   (schon bewertete werden nicht nochmal geschickt)
Schreibt daten/aufbereitet/gesammelt.json  (nur Angebote, die Claude als relevant einstuft)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))
from pipeline.anreichern import wiki_infos  # noqa: E402

KANDIDATEN = BASIS / "daten" / "aufbereitet" / "kandidaten.json"
CACHE = BASIS / "daten" / "aufbereitet" / "llm_cache.json"
AUSGABE = BASIS / "daten" / "aufbereitet" / "gesammelt.json"
PROFIL = BASIS / "config" / "profil.yaml"
QUELLNAMEN = {"nav": "NAV / arbeidsplassen.no", "jobtech": "Platsbanken (JobTech)",
              "backpacker": "Backpacker Job Board", "tamu": "Texas A&M Natural Resources Job Board"}
STAPEL = 8

AUFTRAG = """Du bewertest Stellenangebote für eine Person, die 2027 für 6–12 Wochen (Start Ende April bis Mitte Juni)
eine außergewöhnliche Auslandserfahrung sucht. Profil und Kriterien (YAML):

{profil}

Kurz zusammengefasst: Österreicher, 20 Jahre (2027), Deutsch + Englisch, HTL-Informatik/Elektronik (Python, ESP32,
Sensorik, 3D-Druck) als Tauschwert. Sucht echte praktische Arbeit mit Einheimischen (Handwerk, Schiffe, Naturschutz,
Farmen, Werkstätten, abgelegene Orte), keine Büro-/Hotel-/Gastro-Routine, kein Voluntourism, keine Gebühren.

Für jedes Angebot unten liefere ein JSON-Objekt. Antworte NUR mit einem JSON-Array, ohne Text davor oder danach.
Felder:
- id: wie angegeben
- relevant: true, wenn sich die Person das ernsthaft anschauen sollte; false bei klar unpassend
  (Routine-Hotel/Gastro, Büro, lange Festanstellung, Qualifikation unerreichbar, Voluntourism mit hoher Gebühr)
- titel: kurzer deutscher Titel der Tätigkeit
- kategorie: einer von {kategorien}
- unterpunkt: passender Unterpunkt dieser Kategorie (Schlüssel aus dem Profil)
- tags: 0–3 weitere Kategorie- oder Unterpunkt-Schlüssel
- ort, region: deutsch geschrieben
- ort_wiki: Titel des englischen Wikipedia-Artikels zum Ort oder zur Region (z. B. "Lofoten"), sonst null
- dauer_wochen: [min, max] in Wochen oder null, wenn unbekannt
- dauer_text: ein kurzer Satz zur Dauer/Saison
- bezahlung: lohn | taschengeld | unterkunft_gegen_arbeit | unbezahlt | kostet_geld | unklar
- bezahlung_text: ein Satz (Lohnhöhe, falls genannt)
- gebuehr_eur: Zahl, falls die Person etwas zahlen muss, sonst null
- unterkunft: beim_betrieb | crew_haus | schiff | selbst_organisieren | unklar
- verpflegung: true/false
- englisch: ja | teilweise | nein (reicht Englisch für die Arbeit?)
- beschreibung: 2–3 Sätze auf Deutsch, was man konkret macht
- lernen, beitrag, haken, voraussetzungen: je ein kurzer deutscher Satz
  (beitrag = wo die technischen Fähigkeiten helfen könnten; haken = ehrlicher Nachteil, z. B. Zeitraum passt nicht)
- kriterien: Objekt mit den 11 Kernkriterien aus dem Profil als Schlüssel, je ganze Zahl 0–10. Sei streng:
  gewöhnliche Jobs bekommen bei außergewöhnlichkeit und abenteuer niedrige Werte.
- warum: ein Satz, warum das zur Person passt oder nicht

Angebote:
{angebote}"""


def profil_kurz():
    p = yaml.safe_load(PROFIL.read_text(encoding="utf-8"))
    teile = {k: p[k] for k in ("zeitraum", "kernkriterien", "kategorien", "finanzierung_rangfolge", "abwerten")}
    return yaml.safe_dump(teile, allow_unicode=True, sort_keys=False), list(p["kategorien"])


def frage_claude(prompt):
    ergebnis = subprocess.run(
        ["claude", "-p", "--model", "sonnet", "--output-format", "json", "--tools", "", "--no-session-persistence"],
        input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=600)
    antwort = json.loads(ergebnis.stdout)
    if antwort.get("is_error"):
        raise RuntimeError(antwort.get("result"))
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", antwort["result"].strip())
    return json.loads(text)


def fuer_prompt(a):
    return {"id": f"{a['quelle']}:{a['quelle_id']}", "titel": a["titel"], "organisation": a["organisation"],
            "ort": a["ort"], "region": a["region"], "land": a["land"], "veroeffentlicht": a["veroeffentlicht"],
            "frist": a["frist"], "extra": a["extra"], "beschreibung": a["beschreibung"][:2500]}


def zusammenfuehren(a, b):
    """Roh-Angebot + Claude-Bewertung → Angebot im Format der App."""
    angebot = {k: v for k, v in b.items() if k not in ("id", "relevant")}
    angebot.update({
        "id": f"{a['quelle']}-{a['quelle_id']}", "organisation": a["organisation"] or "Unbekannt",
        "sparte": "ausschreibung", "land": a["land"], "land_code": a["land_code"],
        "website": a["url"], "angebot_url": a["url"], "kontakt": None,
        "status": "automatisch", "quelle": QUELLNAMEN[a["quelle"]], "veroeffentlicht": a["veroeffentlicht"],
        "frist": a["frist"], "originaltitel": a["titel"],
    })
    return angebot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=None, help="höchstens so viele neue Kandidaten bewerten")
    parser.add_argument("--export", type=Path, help="Aufträge als Textdateien in diesen Ordner schreiben")
    parser.add_argument("--import", dest="importieren", type=Path, help="*.antwort.json aus diesem Ordner übernehmen")
    parser.add_argument("--stapel", type=int, default=STAPEL, help="Angebote pro Auftrag")
    args = parser.parse_args()

    kandidaten = json.loads(KANDIDATEN.read_text(encoding="utf-8"))["kandidaten"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if args.importieren:
        for datei in sorted(args.importieren.glob("*.antwort.json")):
            for b in json.loads(datei.read_text(encoding="utf-8")):
                cache[b["id"]] = b
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    offen = [a for a in kandidaten if f"{a['quelle']}:{a['quelle_id']}" not in cache][:args.max]
    profil, kategorien = profil_kurz()
    print(f"{len(kandidaten)} Kandidaten, {len(offen)} noch nicht bewertet")

    stapel_groesse = args.stapel
    auftraege = [AUFTRAG.format(profil=profil, kategorien=" | ".join(kategorien), angebote=json.dumps(
        [fuer_prompt(a) for a in offen[i:i + stapel_groesse]], ensure_ascii=False, indent=1))
        for i in range(0, len(offen), stapel_groesse)]
    if args.export:
        args.export.mkdir(parents=True, exist_ok=True)
        for n, prompt in enumerate(auftraege, 1):
            (args.export / f"auftrag_{n:02}.txt").write_text(prompt, encoding="utf-8")
        print(f"{len(auftraege)} Aufträge → {args.export}")
        return

    for i, prompt in enumerate(auftraege if not args.importieren else []):
        try:
            for b in frage_claude(prompt):
                cache[b["id"]] = b
        except Exception as fehler:
            print(f"  Stapel {i + 1} fehlgeschlagen: {fehler}")
            continue
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  Stapel {i + 1}/{len(auftraege)} bewertet")

    gesammelt = []
    for a in kandidaten:
        b = cache.get(f"{a['quelle']}:{a['quelle_id']}")
        if b and b.get("relevant"):
            angebot = zusammenfuehren(a, b)
            if angebot.get("ort_wiki"):
                try:
                    infos = wiki_infos(angebot["ort_wiki"])
                    angebot["bilder"] = infos.pop("bilder")
                    angebot.update(infos)
                except Exception:
                    pass  # ohne Ortsbild weiter
            gesammelt.append(angebot)
    AUSGABE.write_text(json.dumps(gesammelt, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(gesammelt)} relevante Angebote → {AUSGABE.relative_to(BASIS)}")


if __name__ == "__main__":
    main()
