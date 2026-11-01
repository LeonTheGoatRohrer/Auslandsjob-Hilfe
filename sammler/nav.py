"""NAV Stillingsfeed (Norwegen) – offizieller Daten-Feed mit öffentlichem Token.

    python -m sammler.nav

Der Feed ist ein Änderungsprotokoll seit 2023 in Seiten zu 1000 Einträgen. Der erste Lauf liest alle Seiten
(ca. 5000, dauert), danach merkt sich daten/aufbereitet/nav_cursor.json die zuletzt gelesene Seite und jeder
weitere Lauf liest nur ab dort. Details werden nur für aktive Anzeigen geholt, deren Titel nach Saison-, Land-,
Meer- oder Handwerksarbeit klingt. Meldet der Feed für eine gespeicherte Anzeige einen anderen Status als ACTIVE,
wird sie als geschlossen gespeichert.
"""

import json
import re

from sammler.gemeinsam import BASIS, AbrufFehler, NichtGefunden, hole, lade_roh, speichere, text_aus_html

FEED = "https://pam-stilling-feed.nav.no"
CURSOR = BASIS / "daten" / "aufbereitet" / "nav_cursor.json"
TITEL_PASST = re.compile(
    r"sommer|sesong|fisk|havbruk|oppdrett|gård|landbruk|båt|verft|hytte|fjell|natur|rein|smed|snekker|tømrer|"
    r"svalbard|lofoten|turist|guide|skipper|matros|dekk|summer|season|farm|boat|fish|lodge|english", re.I)


def token():
    return hole(f"{FEED}/api/publicToken").text.split(":", 1)[1].strip()


def sammle():
    auth = {"Authorization": f"Bearer {token()}"}
    cursor = json.loads(CURSOR.read_text(encoding="utf-8")) if CURSOR.exists() else {}
    url = f"/api/v1/feed/{cursor['seite']}" if cursor.get("seite") else "/api/v1/feed"
    stand, seiten, letzte_seite = {}, 0, None
    while url:
        seite = hole(FEED + url, headers=auth, pause=0.3).json()
        for item in seite["items"]:
            stand[item["id"]] = item["_feed_entry"]
        letzte_seite, url, seiten = seite["id"], seite.get("next_url"), seiten + 1
        if seiten % 200 == 0:
            print(f"  {seiten} Feed-Seiten, {len(stand)} Anzeigen")
    bekannt = lade_roh("nav")
    aktiv = [e for e in stand.values() if e["status"] == "ACTIVE"]
    passend = [e for e in aktiv if TITEL_PASST.search(e["title"])]
    beendet = [e for e in stand.values() if e["status"] != "ACTIVE" and e["uuid"] in bekannt]
    print(f"  {seiten} Seiten, {len(stand)} Einträge, {len(aktiv)} aktiv, {len(passend)} mit passendem Titel, "
          f"{len(beendet)} bekannte beendet")

    angebote, fehler = [], {}
    for e in passend:
        try:
            ad = hole(f"{FEED}/api/v1/feedentry/{e['uuid']}", headers=auth, pause=0.5).json()["ad_content"]
            angebote.append(umwandeln(ad))
        except NichtGefunden:
            if e["uuid"] in bekannt:
                angebote.append({**bekannt[e["uuid"]], "status_quelle": "geschlossen", "geschlossen_grund": "nicht mehr abrufbar"})
        except AbrufFehler as f:
            fehler[f"nav:{e['uuid']}"] = str(f)
            print(f"  {e['uuid']}: {f}")
    for e in beendet:
        angebote.append({**bekannt[e["uuid"]], "status_quelle": "geschlossen", "geschlossen_grund": f"Status {e['status']}"})

    speichere("nav", angebote, vollstaendig=False, fehler=fehler, behalte_alte=True)
    if letzte_seite:
        CURSOR.write_text(json.dumps({"seite": letzte_seite}), encoding="utf-8")


def umwandeln(ad):
    ort = (ad.get("workLocations") or [{}])[0]
    return {
        "quelle": "nav", "quelle_id": ad["uuid"],
        "url": ad.get("link") or f"https://arbeidsplassen.nav.no/stillinger/stilling/{ad['uuid']}",
        "titel": ad.get("title", ""), "organisation": (ad.get("employer") or {}).get("name", ""),
        "ort": (ort.get("city") or ort.get("municipal") or "").title(), "region": (ort.get("county") or "").title(),
        "land": "Norwegen", "land_code": "NO",
        "beschreibung": text_aus_html(ad.get("description", ""))[:4000],
        "veroeffentlicht": (ad.get("published") or "")[:10], "frist": ad.get("applicationDue") or "",
        "extra": {"anstellung": ad.get("engagementtype"), "umfang": ad.get("extent"), "start": ad.get("starttime"),
                  "beruf": ad.get("jobtitle") or "", "website": (ad.get("employer") or {}).get("homepage"),
                  "kategorien": [f"{c.get('level1')}/{c.get('level2')}" for c in ad.get("occupationCategories") or []]},
    }


if __name__ == "__main__":
    sammle()
