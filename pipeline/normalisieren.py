"""Rohdaten aller Quellen in eine Liste bringen, Schlüssel und Hash vergeben, Dubletten über Quellen zusammenfassen.

Jedes Angebot bekommt:
    key           "quelle:quelle_id" – stabiler Schlüssel für Zustand und LLM-Cache
    inhalts_hash  sha256 über die inhaltlichen Felder – ändert sich, wenn die Anzeige geändert wurde
    dublette_key  normalisiert aus Organisation + Titel + Ort – gleich bei derselben Stelle auf zwei Portalen
    auch_bei      URLs anderer Quellen mit derselben Stelle (nur beim behaltenen Exemplar)
"""

import hashlib
import json
import re
import unicodedata

MAX_BESCHREIBUNG = 4000  # wie in den Sammlern; der KI-Prompt kürzt später selbst
HASH_FELDER = ("titel", "organisation", "ort", "region", "beschreibung", "frist", "extra")


def _normal(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def inhalts_hash(a):
    roh = json.dumps([a.get(f) for f in HASH_FELDER], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(roh.encode("utf-8")).hexdigest()[:16]


def dublette_key(a):
    teile = [_normal(a.get("organisation")), _normal(a.get("titel")), _normal(a.get("ort"))]
    return "|".join(teile) if teile[0] and teile[1] else None


def normalisiere(roh_dateien):
    """roh_dateien: Liste der geladenen daten/roh/<quelle>.json-Inhalte. Liefert die Angebotsliste."""
    angebote, nach_dublette = [], {}
    for roh in roh_dateien:
        for a in roh["angebote"]:
            a = dict(a)
            a["beschreibung"] = (a.get("beschreibung") or "")[:MAX_BESCHREIBUNG]
            a["key"] = f"{a['quelle']}:{a['quelle_id']}"
            a["inhalts_hash"] = inhalts_hash(a)
            a["dublette_key"] = dublette_key(a)
            a.setdefault("status_quelle", "offen")
            erstes = nach_dublette.get(a["dublette_key"]) if a["dublette_key"] else None
            if erstes is not None and erstes["quelle"] != a["quelle"]:
                erstes.setdefault("auch_bei", []).append(a["url"])
                continue
            if a["dublette_key"]:
                nach_dublette.setdefault(a["dublette_key"], a)
            angebote.append(a)
    return angebote
