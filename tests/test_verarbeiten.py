import json
import shutil
from pathlib import Path

from pipeline.verarbeiten import verarbeite

FIXTURES = Path(__file__).parent / "fixtures" / "roh"


def test_zwei_identische_laeufe_erzeugen_keine_aenderungen(tmp_path):
    roh, aus = tmp_path / "roh", tmp_path / "aus"
    shutil.copytree(FIXTURES, roh)
    lauf1, kandidaten1 = verarbeite(roh, aus, "2026-11-01T06:00:00+00:00")
    assert len(lauf1["neu"]) == 16 and 0 < len(kandidaten1) < 16
    lauf2, kandidaten2 = verarbeite(roh, aus, "2026-11-02T06:00:00+00:00")
    assert lauf2["neu"] == lauf2["geaendert"] == lauf2["geschlossen"] == lauf2["abruf_fehler"] == []
    assert [k["key"] for k in kandidaten1] == [k["key"] for k in kandidaten2]
    zustand = json.loads((aus / "zustand.json").read_text(encoding="utf-8"))
    assert all(z["zuletzt_gesehen"].startswith("2026-11-02") for z in zustand.values())
    zaehlung = json.loads((aus / "kandidaten.json").read_text(encoding="utf-8"))["zaehlung"]["nav"]
    assert set(zaehlung) >= {"roh", "kandidaten", "abgerufen", "ausgeschlossen", "offen", "neu"}


def test_geschlossenes_angebot_ist_kein_kandidat(tmp_path):
    roh, aus = tmp_path / "roh", tmp_path / "aus"
    shutil.copytree(FIXTURES, roh)
    _, kandidaten = verarbeite(roh, aus, "2026-11-01T06:00:00+00:00")
    key = kandidaten[0]["key"]
    quelle, quelle_id = key.split(":")
    datei = roh / f"{quelle}.json"
    inhalt = json.loads(datei.read_text(encoding="utf-8"))
    for a in inhalt["angebote"]:
        if a["quelle_id"] == quelle_id:
            a["status_quelle"], a["geschlossen_grund"] = "geschlossen", "Frist abgelaufen"
    datei.write_text(json.dumps(inhalt, ensure_ascii=False), encoding="utf-8")
    lauf, kandidaten2 = verarbeite(roh, aus, "2026-11-02T06:00:00+00:00")
    assert lauf["geschlossen"] == [{"key": key, "grund": "Frist abgelaufen"}]
    assert key not in [k["key"] for k in kandidaten2]
