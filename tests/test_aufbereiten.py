import json

from pipeline.aufbereiten import aufbereiten
from pipeline.ranking import lade_profil


def kandidat(key, **felder):
    quelle, quelle_id = key.split(":")
    a = {"key": key, "quelle": quelle, "quelle_id": quelle_id, "url": f"https://x/{quelle_id}", "titel": "T",
         "organisation": "Org", "ort": "Risør", "region": "", "land": "Norwegen", "land_code": "NO",
         "beschreibung": "8 weeks, NOK 190 per hour, room provided", "veroeffentlicht": "", "frist": "",
         "extra": {}, "inhalts_hash": "h1", "abgerufen": "2026-11-01T06:00:00+00:00"}
    a.update(felder)
    return a


def bewertung(key, passung_hoch=True, **felder):
    b = {"id": key, "relevant": True, "titel": "Helfer Holzwerft", "kategorie": "handwerk", "unterpunkt": "bootsbau_werften",
         "tags": [], "ort": "Risør", "region": "Agder", "ort_wiki": None, "dauer_wochen": [8, 8], "dauer_text": "8 Wochen",
         "bezahlung": "lohn", "bezahlung_text": "NOK 190/h", "gebuehr_eur": None, "unterkunft": "beim_betrieb",
         "verpflegung": "nicht_angegeben", "englisch": "ja",
         "zitate": {"dauer": "8 weeks", "bezahlung": "NOK 190 per hour", "unterkunft": "room provided"},
         "beschreibung": "…", "lernen": "…", "beitrag": "…", "haken": "–", "voraussetzungen": "nicht angegeben",
         "kriterien": {k: (9 if passung_hoch else 2) for k in lade_profil()["kernkriterien"]}, "warum": "…"}
    b.update(felder)
    return b


def schreibe(aus, kandidaten, cache, zustand, bewertungen=None):
    (aus / "kandidaten.json").write_text(json.dumps({"kandidaten": kandidaten}), encoding="utf-8")
    (aus / "llm_cache").mkdir(exist_ok=True)
    (aus / "llm_cache" / "demo.json").write_text(json.dumps(cache), encoding="utf-8")
    (aus / "zustand.json").write_text(json.dumps(zustand), encoding="utf-8")
    (aus / "bewertungen.json").write_text(json.dumps(bewertungen or {}), encoding="utf-8")


def zustand(key, status="offen", aenderungen=()):
    return {"quelle": key.split(":")[0], "erstmals_gesehen": "2026-11-01", "zuletzt_gesehen": "2026-11-01",
            "inhalts_hash": "h1", "status": status, "geschlossen_grund": None, "fehlversuche": 0,
            "aenderungen": list(aenderungen)}


def test_treffer_zitate_und_nicht_angegeben(tmp_path):
    schreibe(tmp_path, [kandidat("demo:1"), kandidat("demo:2"), kandidat("demo:3")],
             {"demo:1": bewertung("demo:1"), "demo:2": bewertung("demo:2", passung_hoch=False),
              "demo:3": bewertung("demo:3", relevant=False)},
             {"demo:1": zustand("demo:1", aenderungen=[{"datum": "d", "feld": "frist", "alt": "", "neu": "x"}]),
              "demo:2": zustand("demo:2"), "demo:3": zustand("demo:3")})
    gesammelt, ausgabe = aufbereiten(tmp_path, wiki=lambda t: {"bilder": []})
    assert [g["id"] for g in gesammelt] == ["demo-1", "demo-2"]
    assert gesammelt[0]["zitate"]["bezahlung"] == "NOK 190 per hour"
    assert gesammelt[0]["nicht_angegeben"] == ["gebuehr", "verpflegung", "englisch", "voraussetzungen"]
    assert gesammelt[0]["visum"] == "machbar" and gesammelt[0]["passung"] == 90
    assert [t["id"] for t in ausgabe["treffer"]] == ["demo-1"]
    assert ausgabe["treffer"][0]["geaendert_felder"] == ["frist"]
    assert json.loads((tmp_path / "treffer.json").read_text(encoding="utf-8"))["passung_min"] == 60


def test_alte_cache_eintraege_und_geschlossene_gemerkte(tmp_path):
    alt = bewertung("demo:1", verpflegung=True)
    del alt["zitate"]
    schreibe(tmp_path, [kandidat("demo:1")], {"demo:1": alt},
             {"demo:1": zustand("demo:1"), "demo:9": zustand("demo:9", status="geschlossen")},
             {"demo-9": {"liked": True}})
    gesammelt, ausgabe = aufbereiten(tmp_path, wiki=lambda t: {"bilder": []})
    assert gesammelt[0]["verpflegung"] == "ja" and gesammelt[0]["zitate"] is None and gesammelt[0]["nicht_angegeben"] == []
    assert ausgabe["geschlossen_gemerkt"] == [{"id": "demo-9", "key": "demo:9", "status": "geschlossen", "grund": None}]


def test_geschlossene_bleiben_sichtbar(tmp_path):
    schreibe(tmp_path, [kandidat("demo:1")], {"demo:1": bewertung("demo:1")}, {"demo:1": zustand("demo:1")})
    aufbereiten(tmp_path, wiki=lambda t: {"bilder": []})
    schreibe(tmp_path, [], {"demo:1": bewertung("demo:1")},
             {"demo:1": {**zustand("demo:1", status="geschlossen"), "geschlossen_grund": "nicht mehr gelistet"}})
    gesammelt, ausgabe = aufbereiten(tmp_path, wiki=lambda t: {"bilder": []})
    assert [g["id"] for g in gesammelt] == ["demo-1"]
    assert gesammelt[0]["zustand"]["status"] == "geschlossen" and gesammelt[0]["zustand"]["geschlossen_grund"] == "nicht mehr gelistet"
    assert ausgabe["treffer"] == []
