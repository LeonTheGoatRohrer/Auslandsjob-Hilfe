import json

import pytest

from pipeline import routine


def kandidat(key, beschreibung="Eight weeks from May. NOK 190 per hour. Room in the crew house.", hash_="h1"):
    quelle, qid = key.split(":")
    return {"key": key, "quelle": quelle, "quelle_id": qid, "titel": "T", "organisation": "O", "ort": "Risør",
            "region": "", "land": "Norwegen", "veroeffentlicht": "", "frist": "", "extra": {},
            "beschreibung": beschreibung, "inhalts_hash": hash_}


def antwort(key, **felder):
    b = {"id": key, "relevant": True, "bezahlung": "lohn", "unterkunft": "crew_haus", "verpflegung": "vielleicht",
         "englisch": "ja", "kriterien": {k: 7 for k in routine.yaml.safe_load(routine.PROFIL.read_text(encoding="utf-8"))["kernkriterien"]},
         "zitate": {"bezahlung": "NOK 190  per hour", "unterkunft": "Zimmer gibt es auch", "dauer": None}}
    b.update(felder)
    return b


@pytest.fixture
def ordner(tmp_path):
    aus, arbeit = tmp_path / "aus", tmp_path / "arbeit"
    (aus / "llm_cache").mkdir(parents=True)
    return aus, arbeit


def schreibe(aus, kandidaten, cache=None, zustand=None):
    (aus / "kandidaten.json").write_text(json.dumps({"kandidaten": kandidaten}), encoding="utf-8")
    (aus / "llm_cache" / "nav.json").write_text(json.dumps(cache or {}), encoding="utf-8")
    (aus / "zustand.json").write_text(json.dumps(zustand or {}), encoding="utf-8")


def test_offene_altbestand_hash_und_profil():
    k = [kandidat("nav:1"), kandidat("nav:2"), kandidat("nav:3", hash_="neu"), kandidat("nav:4"), kandidat("nav:5")]
    cache = {"nav:1": {"relevant": True},                                        # Altbestand, unverändert
             "nav:2": {"relevant": True},                                        # Altbestand, Anzeige geändert
             "nav:3": {"inhalts_hash": "h1", "profil_hash": "p"},                # Inhalt geändert
             "nav:4": {"inhalts_hash": "h1", "profil_hash": "alt"}}              # Profil oder Prompt geändert
    zustand = {"nav:2": {"aenderungen": [{"feld": "frist"}]}}
    assert [x["key"] for x in routine.offene(k, cache, zustand, "p")] == ["nav:2", "nav:3", "nav:4", "nav:5"]


def test_vorbereiten_und_uebernehmen(ordner):
    aus, arbeit = ordner
    schreibe(aus, [kandidat(f"nav:{i}") for i in range(10)])
    assert routine.vorbereiten(maximal=9, stapel_groesse=8, aus_ordner=aus, arbeit=arbeit) == (9, 10)
    assert sorted(p.name for p in arbeit.iterdir()) == ["auftrag_01.json", "auftrag_01.md", "auftrag_02.json", "auftrag_02.md"]
    prompt = (arbeit / "auftrag_01.md").read_text(encoding="utf-8")
    assert '"id": "nav:0"' in prompt and "kernkriterien" in prompt and "{angebote}" not in prompt

    (arbeit / "antwort_01.json").write_text("```json\n" + json.dumps([antwort(f"nav:{i}") for i in range(8)]) + "\n```",
                                            encoding="utf-8")
    neu, verworfen, fehler = routine.uebernehmen(aus_ordner=aus, arbeit=arbeit)
    assert len(neu) == 8 and verworfen == [] and fehler == ["antwort_02.json: fehlt"]
    e = json.loads((aus / "llm_cache" / "nav.json").read_text(encoding="utf-8"))["nav:0"]
    assert e["zitate"]["bezahlung"] == "NOK 190  per hour" and e["zitate"]["unterkunft"] is None
    assert e["zitate_ungueltig"] == ["unterkunft"] and e["verpflegung"] == "nicht_angegeben"
    assert e["inhalts_hash"] == "h1" and len(e["profil_hash"]) == 16 and e["modell"] == "claude-sonnet-5-5"
    protokoll = json.loads((aus / "bewertungslaeufe.json").read_text(encoding="utf-8"))
    assert protokoll[-1]["bewertet"] == 8 and protokoll[-1]["zitate_ungueltig"] == 8

    # nach dem Übernehmen ist nur noch der neunte und zehnte Kandidat offen
    assert routine.vorbereiten(maximal=48, aus_ordner=aus, arbeit=arbeit) == (2, 2)


def test_ungueltige_antworten_werden_verworfen(ordner):
    aus, arbeit = ordner
    schreibe(aus, [kandidat("nav:1"), kandidat("nav:2"), kandidat("nav:3")])
    routine.vorbereiten(aus_ordner=aus, arbeit=arbeit)
    kaputt = antwort("nav:2")
    del kaputt["kriterien"]
    (arbeit / "antwort_01.json").write_text(json.dumps([antwort("nav:1"), kaputt, antwort("nav:99")]), encoding="utf-8")
    neu, verworfen, fehler = routine.uebernehmen(aus_ordner=aus, arbeit=arbeit)
    assert list(neu) == ["nav:1"]
    assert verworfen == ["nav:2: kriterien unvollständig", "antwort_01.json: unbekannte id nav:99"]
    assert fehler == ["antwort_01.json: keine gültige Bewertung für nav:2, nav:3"]

    (arbeit / "antwort_01.json").write_text("kein json", encoding="utf-8")
    neu, _, fehler = routine.uebernehmen(aus_ordner=aus, arbeit=arbeit)
    assert neu == {} and fehler[0].startswith("antwort_01.json: kein gültiges JSON")
