"""Gemeinsame Helfer für alle Sammler.

Jeder Sammler liefert eine Liste von Roh-Angeboten in diesem Format:
    quelle, quelle_id, url, titel, organisation, ort, region, land, land_code,
    beschreibung, veroeffentlicht, frist, extra (dict mit quellspezifischen Feldern),
    optional status_quelle ("geschlossen") + geschlossen_grund, wenn die Quelle das Ende meldet
und speichert sie mit speichere() nach daten/roh/<quelle>.json. Dort stehen außerdem:
    vollstaendig  True, wenn der Lauf alle aktiven Anzeigen der Quelle gelistet hat
                  (dann gilt "nicht mehr dabei" als geschlossen)
    fehler        {key: text} für Anzeigen, deren Abruf gescheitert ist (zählt nie als geschlossen)
"""

import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import truststore

truststore.inject_into_ssl()  # Windows-Zertifikatsspeicher (Antivirus-HTTPS-Scan)

BASIS = Path(__file__).resolve().parent.parent
ROH = BASIS / "daten" / "roh"
HEADERS = {"User-Agent": "Mozilla/5.0 (Auslandsjob-Hilfe, persoenliches Recherche-Tool)"}

_letzter_abruf = 0.0


class AbrufFehler(Exception):
    """Netz, Timeout, Redirect-Schleife, 429 erschöpft, 5xx – die Anzeige kann noch existieren."""


class NichtGefunden(AbrufFehler):
    """404 / 410 – die Quelle kennt die Anzeige nicht (mehr)."""


def hole(url, pause=1.0, **kwargs):
    """GET mit Mindestabstand zwischen Anfragen, damit wir keine Seite überlasten."""
    global _letzter_abruf
    headers = {**HEADERS, **kwargs.pop("headers", {})}
    for versuch in range(5):
        warten = pause - (time.monotonic() - _letzter_abruf)
        if warten > 0:
            time.sleep(warten)
        _letzter_abruf = time.monotonic()
        try:
            antwort = requests.get(url, headers=headers, timeout=60, **kwargs)
        except requests.ConnectionError as fehler:
            if versuch == 4:
                raise AbrufFehler(f"Verbindung: {fehler}") from fehler
            time.sleep(15 * (versuch + 1))
            continue
        except requests.RequestException as fehler:  # Timeout, zu viele Redirects, ungültige URL
            raise AbrufFehler(str(fehler)) from fehler
        if antwort.status_code != 429:  # 429 = zu viele Anfragen → warten und nochmal
            break
        time.sleep(int(antwort.headers.get("Retry-After", 0)) or 15 * (versuch + 1))
    if antwort.status_code in (404, 410):
        raise NichtGefunden(f"HTTP {antwort.status_code}")
    if antwort.status_code >= 400:
        raise AbrufFehler(f"HTTP {antwort.status_code}")
    return antwort


def text_aus_html(roh):
    """HTML grob zu lesbarem Text."""
    roh = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", roh or "", flags=re.S | re.I)
    roh = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>", "\n", roh, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", roh))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", text)).strip()


def lade_roh(quelle):
    """Zuletzt gespeicherter Stand der Quelle als {quelle_id: angebot}, leer wenn noch keiner da ist."""
    pfad = ROH / f"{quelle}.json"
    if not pfad.exists():
        return {}
    return {a["quelle_id"]: a for a in json.loads(pfad.read_text(encoding="utf-8"))["angebote"]}


def speichere(quelle, angebote, vollstaendig=False, fehler=None, behalte_alte=False):
    """Schreibt daten/roh/<quelle>.json.

    behalte_alte: früher gespeicherte Anzeigen bleiben erhalten, wenn der Lauf nur Änderungen liefert
    (inkrementelle Feeds). Bereits als geschlossen gespeicherte fallen dabei weg – sie wurden schon verarbeitet.
    """
    jetzt = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for a in angebote:
        a["abgerufen"] = jetzt
    if behalte_alte:
        alt = {k: a for k, a in lade_roh(quelle).items() if a.get("status_quelle") != "geschlossen"}
        alt.update({a["quelle_id"]: a for a in angebote})
        angebote = list(alt.values())
    ROH.mkdir(parents=True, exist_ok=True)
    pfad = ROH / f"{quelle}.json"
    inhalt = {"quelle": quelle, "abgerufen": jetzt, "anzahl": len(angebote), "vollstaendig": vollstaendig,
              "fehler": fehler or {}, "angebote": angebote}
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False, indent=1), encoding="utf-8")
    geschlossen = sum(1 for a in angebote if a.get("status_quelle") == "geschlossen")
    print(f"{quelle}: {len(angebote)} Angebote ({geschlossen} geschlossen, {len(fehler or {})} Abruffehler)"
          f" → {pfad.relative_to(BASIS) if pfad.is_relative_to(BASIS) else pfad}")
