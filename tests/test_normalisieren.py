from pipeline.normalisieren import normalisiere


def roh(quelle, angebote):
    return {"quelle": quelle, "abgerufen": "2026-11-01T06:00:00", "anzahl": len(angebote), "angebote": angebote}


def anzeige(quelle, quelle_id, **felder):
    a = {"quelle": quelle, "quelle_id": quelle_id, "url": f"https://{quelle}.example/{quelle_id}",
         "titel": "Gårdsarbeider sommer 2027", "organisation": "Lofoten Gård AS", "ort": "Leknes", "region": "",
         "beschreibung": "x", "frist": "", "extra": {}}
    a.update(felder)
    return a


def test_schluessel_und_hash():
    [a] = normalisiere([roh("nav", [anzeige("nav", "abc")])])
    assert a["key"] == "nav:abc" and len(a["inhalts_hash"]) == 16 and a["status_quelle"] == "offen"
    [b] = normalisiere([roh("nav", [anzeige("nav", "abc", frist="2027-02-01")])])
    assert b["inhalts_hash"] != a["inhalts_hash"]


def test_dublette_ueber_quellen_wird_zusammengefasst():
    angebote = normalisiere([roh("nav", [anzeige("nav", "1")]),
                             roh("eures", [anzeige("eures", "9", titel="GÅRDSARBEIDER, Sommer 2027!")])])
    assert len(angebote) == 1 and angebote[0]["auch_bei"] == ["https://eures.example/9"]


def test_gleiche_quelle_ist_keine_dublette():
    angebote = normalisiere([roh("nav", [anzeige("nav", "1"), anzeige("nav", "2")])])
    assert len(angebote) == 2


def test_beschreibung_wird_gekuerzt():
    [a] = normalisiere([roh("nav", [anzeige("nav", "1", beschreibung="x" * 5000)])])
    assert len(a["beschreibung"]) == 4000
