"""Vorfilter ohne KI: wirft offensichtlich unpassende Roh-Angebote raus, bevor Claude bewertet.

    python pipeline/vorfilter.py

Liest  daten/roh/*.json
Schreibt daten/aufbereitet/kandidaten.json  (Kandidaten + Zählung je Quelle)
"""

import json
import re
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
ROH = BASIS / "daten" / "roh"
AUSGABE = BASIS / "daten" / "aufbereitet" / "kandidaten.json"

# Berufe, die laut Profil nicht gesucht sind (Pflege, Büro, IT, Verkauf, Gastro-Kern, Lehre, Management)
UNPASSEND = re.compile(
    r"nurse|sjuksköterska|sykepleier|undersköterska|helsefag|vårdbiträde|läkare|lege\b|doctor|physician|veterin|"
    r"teacher|lärare|lærer|pedagog|förskol|barnehagelærer|"
    r"personlig assistent|stödassistent|elevassistent|boendestöd|"
    r"sales|säljare|selger|butik|cashier|kassa|account|ekonom|regnskap|controller|"
    r"developer|utvecklare|utvikler|programm|software|it-|data analyst|consultant|konsulent|rådgiver|"
    r"manager|chef\b|leder\b|kökschef|köksmästare|hovmästare|director|"
    r"receptionist|resepsjon|waiter|waitress|servitör|servitør|barista|bartender|housekeep|städ|lokalvård|renhold|"
    r"cleaner|cleaning|kock|kokk|\bcook\b|\bchef\b|dishwash|kitchen hand|"
    r"taxi|truck driver|lastbilsförare|lagerarbet|warehouse|call cent|kundtjänst|kundeservice",
    re.I)

# JobTech: Anstellungsdauer, die nicht in 6–12 Wochen passt
ZU_LANG = {"Tills vidare", "6 månader eller längre", "6 månader – upp till 12 månader", "12 månader – upp till 2 år",
           "Upp till 10 dagar"}

# Lokalsprache ausdrücklich Pflicht
SPRACHE_PFLICHT = re.compile(
    r"(flytande|goda kunskaper i|behärska[rs]?|krav på) svenska|svenska i tal och skrift|"
    r"norsk (muntlig og skriftlig|skriftlig og muntlig)|beherske norsk|snakke norsk|flytende norsk|norskkunnskaper",
    re.I)


ENGLISCH_GENANNT = re.compile(r"english|engelska|engelsk", re.I)

# Backpacker Job Board: viele Stadtjobs – dort braucht es ein Signal für ländliche oder passende Arbeit
LAENDLICH = re.compile(
    r"farm|station hand|cattle|sheep|outback|remote|rural|vineyard|winery|orchard|harvest|prun|boat|marine|"
    r"fishing|deckhand|island|workshop|mechanic|weld|fabricat|machinery|tractor|irrigation|horse|stable|"
    r"conservation|national park|bush|forestry|tree plant|au pair|nanny|governess", re.I)
STADTJOB = re.compile(
    r"forklift|warehouse|removalist|call cent|customer service|recruit|graphic|model|event|cafe|bakery|florist|"
    r"dispatch|promot|fundrais|door to door|telephone|marketing|retail|labourers? \(?(brisbane|sydney|melbourne|perth)",
    re.I)


def ist_englisch(text):
    """Grobe Spracherkennung: englische Füllwörter gegen skandinavische."""
    woerter = re.findall(r"[a-zåäöæø]+", text.lower())
    en = sum(w in {"the", "and", "you", "with", "we", "for", "our", "will"} for w in woerter)
    nord = sum(w in {"och", "og", "du", "vi", "för", "med", "som", "är", "er", "til", "på"} for w in woerter)
    return en > 2 * nord and en >= 5


def grund_zum_ausschluss(a):
    titel = f"{a['titel']} {a['extra'].get('beruf', '')}"
    if UNPASSEND.search(titel):
        return "Beruf passt nicht"
    if a["quelle"] == "jobtech" and a["extra"].get("dauer") in ZU_LANG:
        return "Dauer"
    if a["quelle"] == "backpacker" and (STADTJOB.search(a["titel"])
                                        or not LAENDLICH.search(f"{a['titel']} {a['beschreibung']}")):
        return "Stadtjob / kein ländlicher Bezug"
    if a["quelle"] == "nav" and a["extra"].get("anstellung") == "Fast":
        return "Dauer"
    if SPRACHE_PFLICHT.search(a["beschreibung"]):
        return "Lokalsprache Pflicht"
    if a["quelle"] in ("nav", "jobtech") and not (ist_englisch(f"{a['titel']} {a['beschreibung']}")
                                                   or ENGLISCH_GENANNT.search(a["beschreibung"])):
        return "Anzeige nicht auf Englisch"
    return None


def main():
    kandidaten, zaehlung = [], {}
    for datei in sorted(ROH.glob("*.json")):
        roh = json.loads(datei.read_text(encoding="utf-8"))
        gruende = {}
        for a in roh["angebote"]:
            grund = grund_zum_ausschluss(a)
            if grund:
                gruende[grund] = gruende.get(grund, 0) + 1
            else:
                kandidaten.append(a)
        uebrig = roh["anzahl"] - sum(gruende.values())
        zaehlung[roh["quelle"]] = {"roh": roh["anzahl"], "kandidaten": uebrig, "abgerufen": roh["abgerufen"],
                                   "ausgeschlossen": gruende}
        print(f"{roh['quelle']:12} {roh['anzahl']:5} roh → {uebrig:4} Kandidaten   {gruende}")
    AUSGABE.parent.mkdir(parents=True, exist_ok=True)
    AUSGABE.write_text(json.dumps({"zaehlung": zaehlung, "kandidaten": kandidaten}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(f"\n{len(kandidaten)} Kandidaten → {AUSGABE.relative_to(BASIS)}")


if __name__ == "__main__":
    main()
