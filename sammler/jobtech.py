"""JobTech / Platsbanken (Schweden) – offene Such-Schnittstelle ohne Schlüssel.

    python -m sammler.jobtech

Die Suche über feste Begriffe ist keine vollständige Liste (vollstaendig=False). Bekannte Anzeigen, die die
Suche nicht mehr liefert, werden einzeln über /ad/{id} geprüft: 404 oder "removed" = geschlossen.
"""

from sammler.gemeinsam import AbrufFehler, NichtGefunden, hole, lade_roh, speichere

SUCHE = "https://jobsearch.api.jobtechdev.se/search"
ANZEIGE = "https://jobsearch.api.jobtechdev.se/ad/"
SEITE = 100

# Schwedische Suchbegriffe für Saison-, Land-, Meer- und Handwerksarbeit
BEGRIFFE = ["sommarjobb", "säsongsjobb", "säsong", "sommarvikarie", "skärgård", "fjäll", "fjällstation",
            "lantbruk", "gård", "jordbruk", "fiske", "vattenbruk", "båtbyggare", "båtvarv", "varv", "smed",
            "renskötsel", "naturvård", "naturbevakare", "stuga"]


def sammle():
    gefunden = {}
    for begriff in BEGRIFFE:
        start = 0
        while True:
            daten = hole(SUCHE, params={"q": begriff, "limit": SEITE, "offset": start}, pause=0.3).json()
            for h in daten["hits"]:
                gefunden.setdefault(h["id"], umwandeln(h))
            start += SEITE
            if not daten["hits"] or start >= min(daten["total"]["value"], 2000):
                break
        print(f"  {begriff}: {daten['total']['value']} Treffer, gesamt bisher {len(gefunden)}")

    fehler = {}
    for quelle_id, alt in lade_roh("jobtech").items():
        if quelle_id in gefunden or alt.get("status_quelle") == "geschlossen":
            continue
        try:
            h = hole(ANZEIGE + quelle_id, pause=0.3).json()
            gefunden[quelle_id] = umwandeln(h) if not h.get("removed") else {
                **alt, "status_quelle": "geschlossen", "geschlossen_grund": f"entfernt am {(h.get('removed_date') or '')[:10]}"}
        except NichtGefunden:
            gefunden[quelle_id] = {**alt, "status_quelle": "geschlossen", "geschlossen_grund": "nicht mehr abrufbar"}
        except AbrufFehler as f:
            fehler[f"jobtech:{quelle_id}"] = str(f)
            gefunden[quelle_id] = alt
    speichere("jobtech", list(gefunden.values()), vollstaendig=False, fehler=fehler)


def umwandeln(h):
    adr = h.get("workplace_address") or {}
    label = lambda feld: (h.get(feld) or {}).get("label", "")
    angebot = {
        "quelle": "jobtech", "quelle_id": h["id"], "url": h.get("webpage_url", ""),
        "titel": h.get("headline", ""), "organisation": (h.get("employer") or {}).get("name", ""),
        "ort": adr.get("municipality") or adr.get("city") or "", "region": adr.get("region") or "",
        "land": "Schweden", "land_code": "SE",
        "beschreibung": ((h.get("description") or {}).get("text") or "")[:4000],
        "veroeffentlicht": (h.get("publication_date") or "")[:10], "frist": (h.get("application_deadline") or "")[:10],
        "extra": {"dauer": label("duration"), "arbeitszeit": label("working_hours_type"),
                  "beruf": label("occupation"), "lohnart": label("salary_type"),
                  "lohn": h.get("salary_description") or ""},
    }
    if h.get("removed"):
        angebot.update(status_quelle="geschlossen", geschlossen_grund=f"entfernt am {(h.get('removed_date') or '')[:10]}")
    return angebot


if __name__ == "__main__":
    sammle()
