import json
import os

import pytest
import requests

from sammler import demo, gemeinsam
from sammler.tamu import land_aus_ort


class Antwort:
    def __init__(self, status, text="ok"):
        self.status_code, self.text, self.headers = status, text, {}


def test_hole_uebersetzt_fehler(monkeypatch):
    monkeypatch.setattr(gemeinsam.time, "sleep", lambda s: None)
    monkeypatch.setattr(requests, "get", lambda *a, **k: Antwort(404))
    with pytest.raises(gemeinsam.NichtGefunden):
        gemeinsam.hole("https://x")
    monkeypatch.setattr(requests, "get", lambda *a, **k: Antwort(503))
    with pytest.raises(gemeinsam.AbrufFehler):
        gemeinsam.hole("https://x")

    def schleife(*a, **k):
        raise requests.TooManyRedirects("Exceeded 30 redirects.")
    monkeypatch.setattr(requests, "get", schleife)
    with pytest.raises(gemeinsam.AbrufFehler) as info:
        gemeinsam.hole("https://x")
    assert not isinstance(info.value, gemeinsam.NichtGefunden)
    monkeypatch.setattr(requests, "get", lambda *a, **k: Antwort(200, "inhalt"))
    assert gemeinsam.hole("https://x").text == "inhalt"


def test_speichere_behaelt_alte_und_vergisst_geschlossene(tmp_path, monkeypatch):
    monkeypatch.setattr(gemeinsam, "ROH", tmp_path)
    gemeinsam.speichere("q", [{"quelle_id": "1", "titel": "a"}, {"quelle_id": "2", "titel": "b"}])
    gemeinsam.speichere("q", [{"quelle_id": "2", "titel": "b2", "status_quelle": "geschlossen"},
                              {"quelle_id": "3", "titel": "c"}], behalte_alte=True)
    stand = gemeinsam.lade_roh("q")
    assert set(stand) == {"1", "2", "3"} and stand["2"]["status_quelle"] == "geschlossen"
    gemeinsam.speichere("q", [], behalte_alte=True)
    assert set(gemeinsam.lade_roh("q")) == {"1", "3"}
    inhalt = json.loads((tmp_path / "q.json").read_text(encoding="utf-8"))
    assert inhalt["vollstaendig"] is False and inhalt["fehler"] == {} and all(a["abgerufen"] for a in inhalt["angebote"])


def test_land_aus_ort():
    assert land_aus_ort("Limpopo (South Africa)") == ("South Africa", "ZA")
    assert land_aus_ort("Olowalu (Hawaii)") == ("USA", "US")
    assert land_aus_ort("Kekoldi Indigenous Reserve (Costa Rica)") == ("Costa Rica", "CR")
    assert land_aus_ort("remote work allowed") == ("remote work allowed", "")


def test_demo_quelle(tmp_path, monkeypatch):
    monkeypatch.setattr(gemeinsam, "ROH", tmp_path)
    monkeypatch.setattr(demo, "ROH", tmp_path)
    monkeypatch.setitem(os.environ, "DEMO_QUELLE", "1")
    demo.sammle()
    inhalt = json.loads((tmp_path / "demo.json").read_text(encoding="utf-8"))
    assert inhalt["vollstaendig"] is True and len(inhalt["angebote"]) == 2
    assert all(a["quelle"] == "demo" for a in inhalt["angebote"])
    monkeypatch.delitem(os.environ, "DEMO_QUELLE")
    demo.sammle()
    assert not (tmp_path / "demo.json").exists()
