"""KI-Bewertung durch eine Claude-Code-Routine (Cloud-Agent über das Abo, ohne API-Key).

Die Routine ist selbst das Sprachmodell. Dieses Skript erledigt alles Deterministische drumherum:

    python -m pipeline.routine vorbereiten [--max 48] [--stapel 8]   offene Kandidaten → daten/arbeit/auftrag_NN.md
    python -m pipeline.routine uebernehmen [--modell NAME]            daten/arbeit/antwort_NN.json prüfen → llm_cache/
    python -m pipeline.routine status                                 wie viele Kandidaten auf eine Bewertung warten

Offen ist ein Kandidat ohne Bewertung, mit geändertem Inhalt (inhalts_hash) oder nach einer Änderung an Profil
oder Prompt (profil_hash). Bewertungen aus der Zeit vor den Zitaten (Oktober 2026, ohne inhalts_hash) gelten weiter,
solange der Zustand keine Änderung der Anzeige meldet.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASIS = Path(__file__).resolve().parent.parent
AUS = BASIS / "daten" / "aufbereitet"
ARBEIT = BASIS / "daten" / "arbeit"
PROFIL = BASIS / "config" / "profil.yaml"
PROMPT = BASIS / "config" / "prompt_bewertung.md"
PROFIL_TEILE = ("zeitraum", "person", "max_programmgebühr_eur", "kernkriterien", "kategorien",
                "finanzierung_rangfolge", "abwerten", "regionen_bevorzugt", "fähigkeiten_tauschwert")
ENUMS = {"bezahlung": ["lohn", "taschengeld", "unterkunft_gegen_arbeit", "unbezahlt", "kostet_geld", "unklar"],
         "unterkunft": ["beim_betrieb", "crew_haus", "schiff", "selbst_organisieren", "unklar"],
         "verpflegung": ["ja", "nein", "nicht_angegeben"],
         "englisch": ["ja", "teilweise", "nein", "nicht_angegeben"]}
MAX_BESCHREIBUNG = 2500


def lies_json(pfad, standard):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else standard


def schreibe_json(pfad, inhalt):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def lies_cache(aus_ordner=AUS):
    """KI-Bewertungen liegen je Quelle in llm_cache/<quelle>.json."""
    cache = {}
    for pfad in sorted((aus_ordner / "llm_cache").glob("*.json")):
        cache.update(lies_json(pfad, {}))
    return cache


def profil_hash(profil_text, prompt_text):
    return hashlib.sha256((profil_text + "\n---\n" + prompt_text).encode("utf-8")).hexdigest()[:16]


def offene(kandidaten, cache, zustand, p_hash):
    def braucht_bewertung(k):
        e = cache.get(k["key"])
        if not e:
            return True
        if "inhalts_hash" not in e:  # Altbestand: nur neu, wenn die Anzeige sich seither geändert hat
            return bool(zustand.get(k["key"], {}).get("aenderungen"))
        return e["inhalts_hash"] != k["inhalts_hash"] or e.get("profil_hash") != p_hash
    return [k for k in kandidaten if braucht_bewertung(k)]


def _prompt(vorlage, profil_text, stapel):
    profil = yaml.safe_load(profil_text)
    auszug = yaml.safe_dump({k: profil[k] for k in PROFIL_TEILE if k in profil}, allow_unicode=True, sort_keys=False)
    angebote = [{"id": a["key"], "titel": a["titel"], "organisation": a["organisation"], "ort": a["ort"],
                 "region": a["region"], "land": a["land"], "veroeffentlicht": a["veroeffentlicht"], "frist": a["frist"],
                 "extra": a["extra"], "beschreibung": a["beschreibung"][:MAX_BESCHREIBUNG]} for a in stapel]
    return (vorlage.replace("{profil}", auszug).replace("{kategorien}", " | ".join(profil["kategorien"]))
            .replace("{angebote}", json.dumps(angebote, ensure_ascii=False, indent=1)))


def vorbereiten(maximal=48, stapel_groesse=8, aus_ordner=AUS, arbeit=ARBEIT):
    profil_text, vorlage = PROFIL.read_text(encoding="utf-8"), PROMPT.read_text(encoding="utf-8")
    kandidaten = lies_json(aus_ordner / "kandidaten.json", {"kandidaten": []})["kandidaten"]
    zustand = lies_json(aus_ordner / "zustand.json", {})
    alle_offen = offene(kandidaten, lies_cache(aus_ordner), zustand, profil_hash(profil_text, vorlage))
    jetzt = alle_offen[:maximal]
    arbeit.mkdir(parents=True, exist_ok=True)
    for alt in arbeit.glob("*"):
        alt.unlink()
    for n, i in enumerate(range(0, len(jetzt), stapel_groesse), 1):
        stapel = jetzt[i:i + stapel_groesse]
        (arbeit / f"auftrag_{n:02}.md").write_text(_prompt(vorlage, profil_text, stapel), encoding="utf-8")
        schreibe_json(arbeit / f"auftrag_{n:02}.json", {a["key"]: a for a in stapel})
    return len(jetzt), len(alle_offen)


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def pruefe(b, kandidat, kernkriterien):
    """Eine Bewertung prüfen und bereinigen. Liefert (eintrag, None) oder (None, grund)."""
    if not isinstance(b, dict) or not isinstance(b.get("relevant"), bool):
        return None, "relevant fehlt"
    kriterien = b.get("kriterien")
    if not isinstance(kriterien, dict) or not set(kernkriterien) <= set(kriterien):
        return None, "kriterien unvollständig"
    try:
        b["kriterien"] = {k: max(0, min(10, int(kriterien[k]))) for k in kernkriterien}
    except (TypeError, ValueError):
        return None, "kriterien nicht ganzzahlig"
    for feld, werte in ENUMS.items():
        if b.get(feld) not in werte:
            b[feld] = werte[-1]  # unklar / nicht_angegeben
    beschreibung = _norm(kandidat["beschreibung"])
    zitate = b.get("zitate") if isinstance(b.get("zitate"), dict) else {}
    ungueltig = [f for f, z in zitate.items() if z and _norm(z) not in beschreibung]
    b["zitate"] = {f: (None if f in ungueltig else z) for f, z in zitate.items()}
    b["zitate_ungueltig"] = ungueltig
    return b, None


def uebernehmen(modell="claude-sonnet-5-5", aus_ordner=AUS, arbeit=ARBEIT):
    profil_text, vorlage = PROFIL.read_text(encoding="utf-8"), PROMPT.read_text(encoding="utf-8")
    p_hash = profil_hash(profil_text, vorlage)
    kernkriterien = list(yaml.safe_load(profil_text)["kernkriterien"])
    jetzt = datetime.now(timezone.utc).isoformat(timespec="seconds")
    neu, fehler, verworfen = {}, [], []
    auftraege = sorted(arbeit.glob("auftrag_*.json"))
    for auftrag in auftraege:
        stapel = lies_json(auftrag, {})
        antwort = auftrag.with_name(auftrag.name.replace("auftrag_", "antwort_"))
        if not antwort.exists():
            fehler.append(f"{antwort.name}: fehlt")
            continue
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", antwort.read_text(encoding="utf-8").strip())
        try:
            liste = json.loads(text)
        except json.JSONDecodeError as f:
            fehler.append(f"{antwort.name}: kein gültiges JSON ({f})")
            continue
        for b in liste if isinstance(liste, list) else []:
            kandidat = stapel.get(b.get("id")) if isinstance(b, dict) else None
            if kandidat is None:
                verworfen.append(f"{antwort.name}: unbekannte id {b.get('id') if isinstance(b, dict) else repr(b)}")
                continue
            eintrag, grund = pruefe(b, kandidat, kernkriterien)
            if grund:
                verworfen.append(f"{kandidat['key']}: {grund}")
                continue
            eintrag.update(inhalts_hash=kandidat["inhalts_hash"], profil_hash=p_hash, bewertet_am=jetzt, modell=modell)
            neu[kandidat["key"]] = eintrag
        fehlend = [k for k in stapel if k not in neu]
        if fehlend:
            fehler.append(f"{antwort.name}: keine gültige Bewertung für {', '.join(fehlend)}")

    for quelle in sorted({k.split(":")[0] for k in neu}):
        pfad = aus_ordner / "llm_cache" / f"{quelle}.json"
        cache = lies_json(pfad, {})
        cache.update({k: v for k, v in neu.items() if k.startswith(quelle + ":")})
        schreibe_json(pfad, cache)
    protokoll = lies_json(aus_ordner / "bewertungslaeufe.json", [])
    protokoll.append({"datum": jetzt, "modell": modell, "auftraege": len(auftraege), "bewertet": len(neu),
                      "verworfen": len(verworfen), "zitate_ungueltig": sum(len(e["zitate_ungueltig"]) for e in neu.values()),
                      "fehler": fehler})
    schreibe_json(aus_ordner / "bewertungslaeufe.json", protokoll[-500:])
    return neu, verworfen, fehler


def status(aus_ordner=AUS):
    profil_text, vorlage = PROFIL.read_text(encoding="utf-8"), PROMPT.read_text(encoding="utf-8")
    kandidaten = lies_json(aus_ordner / "kandidaten.json", {"kandidaten": []})["kandidaten"]
    zustand = lies_json(aus_ordner / "zustand.json", {})
    return len(offene(kandidaten, lies_cache(aus_ordner), zustand, profil_hash(profil_text, vorlage))), len(kandidaten)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="befehl", required=True)
    v = sub.add_parser("vorbereiten")
    v.add_argument("--max", type=int, default=48)
    v.add_argument("--stapel", type=int, default=8)
    u = sub.add_parser("uebernehmen")
    u.add_argument("--modell", default="claude-sonnet-5-5")
    sub.add_parser("status")
    args = parser.parse_args()

    if args.befehl == "vorbereiten":
        jetzt, gesamt = vorbereiten(args.max, args.stapel)
        auftraege = (jetzt + args.stapel - 1) // args.stapel
        print(f"{jetzt} von {gesamt} offenen Kandidaten in {auftraege} Aufträgen → daten/arbeit/auftrag_NN.md")
    elif args.befehl == "uebernehmen":
        neu, verworfen, fehler = uebernehmen(args.modell)
        print(f"{len(neu)} Bewertungen übernommen → daten/aufbereitet/llm_cache/")
        for zeile in verworfen + fehler:
            print(f"  FEHLER {zeile}")
        if fehler or verworfen:
            sys.exit(1)
    else:
        offen, gesamt = status()
        print(f"{offen} von {gesamt} Kandidaten warten auf eine Bewertung")


if __name__ == "__main__":
    main()
