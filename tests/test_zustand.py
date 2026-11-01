from pipeline.zustand import MAX_FEHLVERSUCHE, aktualisiere


def angebot(key="nav:1", **felder):
    quelle, quelle_id = key.split(":")
    a = {"key": key, "quelle": quelle, "quelle_id": quelle_id, "titel": "Sommerjob", "organisation": "Hof",
         "ort": "Lofoten", "region": "", "beschreibung": "Arbeit auf dem Hof", "frist": "", "extra": {},
         "inhalts_hash": "h1", "status_quelle": "offen"}
    a.update(felder)
    return a


def test_neu_dann_unveraendert():
    z = {}
    lauf1 = aktualisiere(z, [angebot()], "2026-11-01", {"nav": True}, {})
    assert lauf1["neu"] == ["nav:1"] and z["nav:1"]["status"] == "offen"
    lauf2 = aktualisiere(z, [angebot()], "2026-11-02", {"nav": True}, {})
    assert lauf2["neu"] == lauf2["geaendert"] == lauf2["geschlossen"] == []
    assert z["nav:1"]["zuletzt_gesehen"] == "2026-11-02"


def test_aenderung_wird_mit_feldern_protokolliert():
    z = {}
    aktualisiere(z, [angebot()], "2026-11-01", {}, {})
    lauf = aktualisiere(z, [angebot(frist="2027-01-31", inhalts_hash="h2")], "2026-11-02", {}, {})
    assert lauf["geaendert"] == [{"key": "nav:1", "felder": ["frist"]}]
    assert z["nav:1"]["aenderungen"] == [{"datum": "2026-11-02", "feld": "frist", "alt": "", "neu": "2027-01-31"}]


def test_quelle_meldet_geschlossen():
    z = {}
    aktualisiere(z, [angebot()], "2026-11-01", {}, {})
    lauf = aktualisiere(z, [angebot(status_quelle="geschlossen", geschlossen_grund="Status EXPIRED")],
                        "2026-11-02", {}, {})
    assert lauf["geschlossen"] == [{"key": "nav:1", "grund": "Status EXPIRED"}]
    assert z["nav:1"]["status"] == "geschlossen"


def test_nicht_mehr_gelistet_nur_bei_vollstaendigem_lauf():
    z = {}
    aktualisiere(z, [angebot()], "2026-11-01", {}, {})
    aktualisiere(z, [], "2026-11-02", {"nav": False}, {})
    assert z["nav:1"]["status"] == "offen"
    lauf = aktualisiere(z, [], "2026-11-03", {"nav": True}, {})
    assert z["nav:1"]["status"] == "geschlossen" and lauf["geschlossen"][0]["grund"] == "nicht mehr gelistet"


def test_abruffehler_schliesst_nie():
    z = {}
    aktualisiere(z, [angebot()], "2026-11-01", {"nav": True}, {})
    for tag in range(MAX_FEHLVERSUCHE):
        lauf = aktualisiere(z, [], f"2026-11-0{tag + 2}", {"nav": True}, {"nav:1": "Exceeded 30 redirects"})
        assert lauf["abruf_fehler"] == ["nav:1"] and lauf["geschlossen"] == []
    assert z["nav:1"]["status"] == "unbekannt" and z["nav:1"]["fehlversuche"] == MAX_FEHLVERSUCHE
    aktualisiere(z, [angebot()], "2026-11-09", {"nav": True}, {})
    assert z["nav:1"]["status"] == "offen" and z["nav:1"]["fehlversuche"] == 0
