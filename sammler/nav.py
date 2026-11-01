"""NAV Stillingsfeed (Norwegen) – offizieller Daten-Feed mit öffentlichem Token.

    python -m sammler.nav

Der Feed ist ein Änderungsprotokoll seit 2023: Wir lesen alle Seiten, behalten den letzten Stand je Anzeige,
und holen Details nur für aktive Anzeigen, deren Titel nach Saison-, Land-, Meer- oder Handwerksarbeit klingt.
"""

import re

from sammler.gemeinsam import hole, speichere, text_aus_html

FEED = "https://pam-stilling-feed.nav.no"
TITEL_PASST = re.compile(
    r"sommer|sesong|fisk|havbruk|oppdrett|gård|landbruk|båt|verft|hytte|fjell|natur|rein|smed|snekker|tømrer|"
    r"svalbard|lofoten|turist|guide|skipper|matros|dekk|summer|season|farm|boat|fish|lodge|english", re.I)


def token():
    return hole(f"{FEED}/api/publicToken").text.split(":", 1)[1].strip()


def sammle():
    auth = {"Authorization": f"Bearer {token()}"}
    stand, url, seiten = {}, "/api/v1/feed", 0
    while url:
        seite = hole(FEED + url, headers=auth, pause=0.3).json()
        for item in seite["items"]:
            stand[item["id"]] = item["_feed_entry"]
        url, seiten = seite.get("next_url"), seiten + 1
        if seiten % 200 == 0:
            print(f"  {seiten} Feed-Seiten, {len(stand)} Anzeigen")
    aktiv = [e for e in stand.values() if e["status"] == "ACTIVE"]
    passend = [e for e in aktiv if TITEL_PASST.search(e["title"])]
    print(f"  {len(stand)} Anzeigen im Feed, {len(aktiv)} aktiv, {len(passend)} mit passendem Titel")

    angebote = []
    for e in passend:
        try:
            ad = hole(f"{FEED}/api/v1/feedentry/{e['uuid']}", headers=auth, pause=0.5).json()["ad_content"]
            angebote.append(umwandeln(ad))
        except Exception as fehler:
            print(f"  {e['uuid']}: {fehler}")
    return angebote


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
    speichere("nav", sammle())
