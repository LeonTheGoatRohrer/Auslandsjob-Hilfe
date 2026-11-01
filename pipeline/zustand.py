"""Zustand je Angebot über Läufe hinweg: neu, unverändert, geändert, geschlossen, Abruf gescheitert.

zustand.json:  { key: { quelle, erstmals_gesehen, zuletzt_gesehen, inhalts_hash, status, geschlossen_grund,
                        fehlversuche, aenderungen: [ {datum, feld, alt, neu} ] } }
status:  offen | geschlossen | unbekannt   (unbekannt = mehrfach nicht abrufbar, aber nie als geschlossen gemeldet)

Ein Abruffehler setzt nie auf geschlossen. Geschlossen wird nur, wenn die Quelle das sagt (status_quelle)
oder wenn ein vollständig gelisteter Lauf das Angebot nicht mehr enthält.
"""

MAX_FEHLVERSUCHE = 3
DIFF_FELDER = ("titel", "organisation", "ort", "region", "frist", "beschreibung", "extra")
KURZ = 200


def _kurz(wert):
    text = wert if isinstance(wert, str) else str(wert)
    return text[:KURZ]


def aktualisiere(zustand, angebote, datum, vollstaendig, fehler):
    """Wendet einen Lauf auf den Zustand an (in place) und liefert die Änderungen des Laufs.

    angebote:     normalisierte Angebote dieses Laufs (mit status_quelle offen|geschlossen, geschlossen_grund)
    vollstaendig: {quelle: bool} – hat der Sammler alle aktiven Anzeigen der Quelle gelistet?
    fehler:       {key: fehlertext} – Angebote, deren Abruf gescheitert ist
    """
    lauf = {"datum": datum, "neu": [], "geaendert": [], "geschlossen": [], "abruf_fehler": []}
    gesehen = set()

    for a in angebote:
        key = a["key"]
        gesehen.add(key)
        z = zustand.get(key)
        if z is None:
            z = zustand[key] = {"quelle": a["quelle"], "erstmals_gesehen": datum, "zuletzt_gesehen": datum,
                                "inhalts_hash": a["inhalts_hash"], "status": "offen", "geschlossen_grund": None,
                                "fehlversuche": 0, "aenderungen": [], "letzter_stand": _stand(a)}
            lauf["neu"].append(key)
        else:
            z["zuletzt_gesehen"], z["fehlversuche"] = datum, 0
            if z["inhalts_hash"] != a["inhalts_hash"]:
                felder = [f for f in DIFF_FELDER if z.get("letzter_stand", {}).get(f) != _stand(a).get(f)]
                z["aenderungen"] += [{"datum": datum, "feld": f, "alt": z.get("letzter_stand", {}).get(f),
                                      "neu": _stand(a).get(f)} for f in felder]
                z["inhalts_hash"], z["letzter_stand"] = a["inhalts_hash"], _stand(a)
                lauf["geaendert"].append({"key": key, "felder": felder})
            if z["status"] != "offen" and a.get("status_quelle", "offen") == "offen":
                z["status"], z["geschlossen_grund"] = "offen", None  # wieder da
        if a.get("status_quelle") == "geschlossen" and z["status"] != "geschlossen":
            _schliesse(z, lauf, key, a.get("geschlossen_grund") or "von der Quelle als beendet gemeldet")

    for key, text in fehler.items():
        z = zustand.get(key)
        if z is None:
            continue
        z["fehlversuche"] += 1
        z["letzter_fehler"] = text
        if z["fehlversuche"] >= MAX_FEHLVERSUCHE and z["status"] == "offen":
            z["status"] = "unbekannt"
        lauf["abruf_fehler"].append(key)

    for key, z in zustand.items():
        if key in gesehen or key in fehler or z["status"] == "geschlossen":
            continue
        if vollstaendig.get(z["quelle"]):
            _schliesse(z, lauf, key, "nicht mehr gelistet")

    lauf["zaehlung"] = _zaehlung(zustand, lauf)
    return lauf


def _stand(a):
    return {f: _kurz(a.get(f)) for f in DIFF_FELDER}


def _schliesse(z, lauf, key, grund):
    z["status"], z["geschlossen_grund"] = "geschlossen", grund
    lauf["geschlossen"].append({"key": key, "grund": grund})


def _zaehlung(zustand, lauf):
    quellen = sorted({z["quelle"] for z in zustand.values()})
    def anzahl(liste, quelle):
        return sum(1 for e in liste if (e["key"] if isinstance(e, dict) else e).startswith(quelle + ":"))
    return {q: {"offen": sum(1 for z in zustand.values() if z["quelle"] == q and z["status"] == "offen"),
                "neu": anzahl(lauf["neu"], q), "geaendert": anzahl(lauf["geaendert"], q),
                "geschlossen": anzahl(lauf["geschlossen"], q), "abruf_fehler": anzahl(lauf["abruf_fehler"], q)}
            for q in quellen}
