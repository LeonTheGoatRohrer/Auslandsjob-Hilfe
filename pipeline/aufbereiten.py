"""Führt Kandidaten, KI-Bewertungen (llm_cache/, von der Claude-Code-Routine geschrieben) und Zustand zusammen, wendet die Regeln an
und schreibt die Daten für App und Benachrichtigung.

    python -m pipeline.aufbereiten

Liest    daten/aufbereitet/kandidaten.json, llm_cache/<quelle>.json, zustand.json, bewertungen.json, config/profil.yaml
Schreibt daten/aufbereitet/gesammelt.json   relevante Angebote im Format der App (mit Passung, Ausschluss, Zitaten)
         daten/aufbereitet/treffer.json     was n8n melden darf: Treffer über der Passungsschwelle + geschlossene Gemerkte
         daten/aufbereitet/status.json      Kennzahlen für den n8n-Wächter (letzter Lauf, offene Bewertungen, Abruffehler)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS))
from pipeline.anreichern import wiki_infos  # noqa: E402
from pipeline.ranking import bewerte, lade_profil  # noqa: E402
from pipeline.routine import lies_cache, status as offen_zaehlen  # noqa: E402

AUS = BASIS / "daten" / "aufbereitet"
QUELLNAMEN = {"nav": "NAV / arbeidsplassen.no", "jobtech": "Platsbanken (JobTech)",
              "backpacker": "Backpacker Job Board", "tamu": "Texas A&M Natural Resources Job Board",
              "demo": "Demo-Quelle"}
ZITATFELDER = ("dauer", "bezahlung", "gebuehr", "unterkunft", "verpflegung", "englisch", "voraussetzungen")


def lies_json(pfad, standard):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else standard


def zustand_kurz(z):
    return {"erstmals_gesehen": z["erstmals_gesehen"], "zuletzt_gesehen": z["zuletzt_gesehen"], "status": z["status"],
            "geschlossen_grund": z.get("geschlossen_grund"), "aenderungen": z.get("aenderungen", [])[-5:]}


def zusammenfuehren(a, b, z):
    """Kandidat + KI-Bewertung + Zustand → Angebot im Format der App."""
    angebot = {k: v for k, v in b.items() if k not in ("id", "relevant", "inhalts_hash", "profil_hash")}
    if isinstance(angebot.get("verpflegung"), bool):  # alte Cache-Einträge ohne Zitate
        angebot["verpflegung"] = "ja" if angebot["verpflegung"] else "nein"
    if "zitate" in b:  # neue Bewertungen tragen Belege; alte ohne Zitate zeigen keine Hinweise
        angebot["zitate"] = {f: (b["zitate"] or {}).get(f) for f in ZITATFELDER}
        angebot["nicht_angegeben"] = [f for f in ZITATFELDER if not angebot["zitate"][f]]
    else:
        angebot["zitate"], angebot["nicht_angegeben"] = None, []
    angebot.update({
        "id": a["key"].replace(":", "-", 1), "key": a["key"], "organisation": a["organisation"] or "Unbekannt",
        "sparte": "ausschreibung", "land": a["land"], "land_code": a["land_code"],
        "website": a["url"], "angebot_url": a["url"], "auch_bei": a.get("auch_bei", []), "kontakt": None,
        "status": "automatisch", "quelle": QUELLNAMEN.get(a["quelle"], a["quelle"]),
        "veroeffentlicht": a["veroeffentlicht"], "frist": a["frist"], "originaltitel": a["titel"],
        "abgerufen": a.get("abgerufen"), "inhalts_hash": a["inhalts_hash"],
        "zustand": zustand_kurz(z),
    })
    return angebot


def aufbereiten(aus_ordner=AUS, profil=None, wiki=wiki_infos):
    profil = profil or lade_profil()
    kandidaten = lies_json(aus_ordner / "kandidaten.json", {"kandidaten": []})["kandidaten"]
    cache = lies_cache(aus_ordner)
    zustand = lies_json(aus_ordner / "zustand.json", {})
    bewertungen = lies_json(aus_ordner / "bewertungen.json", {})
    vorher = {g["id"]: g for g in lies_json(aus_ordner / "gesammelt.json", [])}

    gesammelt = []
    for a in kandidaten:
        b = cache.get(a["key"])
        if not b or not b.get("relevant"):
            continue
        angebot = zusammenfuehren(a, b, zustand[a["key"]])
        alt = vorher.get(angebot["id"], {})
        if alt.get("ort_wiki") == angebot.get("ort_wiki") and "bilder" in alt:
            angebot.update({k: alt[k] for k in ("bilder", "ort_info", "ort_link") if k in alt})
        elif angebot.get("ort_wiki"):
            try:
                infos = wiki(angebot["ort_wiki"])
                angebot["bilder"] = infos.pop("bilder")
                angebot.update(infos)
            except Exception:
                pass  # ohne Ortsbild weiter
        gesammelt.append(angebot)
    # Angebote, die in diesem Lauf nicht als Kandidat vorkommen, bleiben mit ihrem letzten Stand sichtbar:
    # geschlossene (keine Kandidaten mehr) und offene aus inkrementellen Quellen wie NAV, die nur Änderungen liefern.
    kandidaten_keys = {a["key"] for a in kandidaten}
    for gid, alt in vorher.items():
        z = zustand.get(alt.get("key"))
        if z and alt["key"] not in kandidaten_keys:
            gesammelt.append({**alt, "zustand": zustand_kurz(z)})
    bewerte(gesammelt, profil)

    schwelle = profil.get("benachrichtigung", {}).get("passung_min", 60)
    treffer = [{"id": g["id"], "key": g["key"], "titel": g["titel"], "organisation": g["organisation"],
                "land": g["land"], "ort": g.get("ort"), "passung": g["passung"], "url": g["angebot_url"],
                "bezahlung": g.get("bezahlung"), "dauer_text": g.get("dauer_text"), "haken": g.get("haken"),
                "nicht_angegeben": g["nicht_angegeben"], "inhalts_hash": g["inhalts_hash"],
                "geaendert_felder": sorted({ae["feld"] for ae in g["zustand"]["aenderungen"]})}
               for g in gesammelt if g["passung"] >= schwelle and not g["ausschluss"] and g["zustand"]["status"] == "offen"]
    geschlossen_gemerkt = [{"id": gid, "key": key, "status": z["status"], "grund": z.get("geschlossen_grund")}
                           for key, z in zustand.items() if z["status"] == "geschlossen"
                           for gid in [key.replace(":", "-", 1)] if bewertungen.get(gid, {}).get("liked")]
    ausgabe = {"datum": datetime.now(timezone.utc).isoformat(timespec="seconds"), "passung_min": schwelle,
               "treffer": treffer, "geschlossen_gemerkt": geschlossen_gemerkt}

    (aus_ordner / "gesammelt.json").write_text(json.dumps(gesammelt, ensure_ascii=False, indent=1), encoding="utf-8")
    (aus_ordner / "treffer.json").write_text(json.dumps(ausgabe, ensure_ascii=False, indent=1), encoding="utf-8")
    (aus_ordner / "status.json").write_text(json.dumps(status(aus_ordner), ensure_ascii=False, indent=1), encoding="utf-8")
    return gesammelt, ausgabe


def status(aus_ordner):
    """Kennzahlen, an denen der n8n-Wächter erkennt, ob die Kette läuft."""
    kandidaten = lies_json(aus_ordner / "kandidaten.json", {})
    laeufe = lies_json(aus_ordner / "bewertungslaeufe.json", [])
    zaehlung = lies_json(aus_ordner / "aenderungen.json", {}).get("zaehlung", {})
    offen, gesamt = offen_zaehlen(aus_ordner)
    return {"datum": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "letzter_sammellauf": kandidaten.get("datum"), "kandidaten": gesamt, "unbewertet": offen,
            "letzte_bewertung": laeufe[-1]["datum"] if laeufe else None,
            "letzte_bewertung_fehler": laeufe[-1]["fehler"] if laeufe else [],
            "quellen": {q: {"abgerufen": z.get("abgerufen"), "abruf_fehler": z.get("abruf_fehler", 0), "offen": z.get("offen")}
                        for q, z in zaehlung.items()}}


def main():
    gesammelt, ausgabe = aufbereiten()
    unbewertet, _ = offen_zaehlen(AUS)
    print(f"{len(gesammelt)} relevante Angebote → daten/aufbereitet/gesammelt.json ({unbewertet} Kandidaten noch ohne KI-Bewertung)")
    print(f"{len(ausgabe['treffer'])} Treffer ab Passung {ausgabe['passung_min']}, "
          f"{len(ausgabe['geschlossen_gemerkt'])} gemerkte geschlossen → daten/aufbereitet/treffer.json")


if __name__ == "__main__":
    main()
