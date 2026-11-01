"""Gemeinsame Helfer für alle Sammler.

Jeder Sammler liefert eine Liste von Roh-Angeboten in diesem Format:
    quelle, quelle_id, url, titel, organisation, ort, region, land, land_code,
    beschreibung, veroeffentlicht, frist, extra (dict mit quellspezifischen Feldern)
und speichert sie mit speichere() nach daten/roh/<quelle>.json.
"""

import html
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import truststore

truststore.inject_into_ssl()  # Windows-Zertifikatsspeicher (Antivirus-HTTPS-Scan)

BASIS = Path(__file__).resolve().parent.parent
ROH = BASIS / "daten" / "roh"
HEADERS = {"User-Agent": "Mozilla/5.0 (Auslandsjob-Hilfe, persoenliches Recherche-Tool)"}

_letzter_abruf = 0.0


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
        except requests.ConnectionError:
            if versuch == 4:
                raise
            time.sleep(15 * (versuch + 1))
            continue
        if antwort.status_code != 429:  # 429 = zu viele Anfragen → warten und nochmal
            break
        time.sleep(int(antwort.headers.get("Retry-After", 0)) or 15 * (versuch + 1))
    antwort.raise_for_status()
    return antwort


def text_aus_html(roh):
    """HTML grob zu lesbarem Text."""
    roh = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", roh or "", flags=re.S | re.I)
    roh = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>", "\n", roh, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", roh))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", text)).strip()


def speichere(quelle, angebote):
    ROH.mkdir(parents=True, exist_ok=True)
    pfad = ROH / f"{quelle}.json"
    inhalt = {"quelle": quelle, "abgerufen": datetime.now().isoformat(timespec="seconds"),
              "anzahl": len(angebote), "angebote": angebote}
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{quelle}: {len(angebote)} Angebote → {pfad.relative_to(BASIS)}")
