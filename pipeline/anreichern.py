"""Reichert kuratierte Angebote mit Website-Infos und Bildern an.

    python pipeline/anreichern.py

Liest  daten/kuratiert/angebote.json
Holt   je Angebot: Titel, Beschreibung und Bilder der Website (og:image + große <img>)
       sowie ein Ortsbild aus Wikipedia (Feld ort_wiki)
Schreibt daten/aufbereitet/angebote.json
"""

import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
import truststore

truststore.inject_into_ssl()  # Windows-Zertifikatsspeicher nutzen (nötig z. B. hinter Antivirus-HTTPS-Scan)

BASIS = Path(__file__).resolve().parent.parent
EINGABE = BASIS / "daten" / "kuratiert" / "angebote.json"
AUSGABE = BASIS / "daten" / "aufbereitet" / "angebote.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Auslandsjob-Hilfe, persoenliches Recherche-Tool)"}
MAX_WEBSITE_BILDER = 4
UNPASSENDE_BILDER = re.compile(r"logo|icon|sprite|favicon|avatar|badge|banner-ad|pixel|\.svg|\.gif", re.I)


class SeitenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.bilder, self.titel, self._im_titel = {}, [], "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            schluessel = a.get("property") or a.get("name")
            if schluessel and a.get("content"):
                self.meta.setdefault(schluessel.lower(), a["content"])
        elif tag == "img":
            src = a.get("src") or a.get("data-src")
            if src and not src.startswith("data:"):
                self.bilder.append(src)
        elif tag == "title":
            self._im_titel = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._im_titel = False

    def handle_data(self, data):
        if self._im_titel:
            self.titel += data


def website_infos(url):
    antwort = requests.get(url, headers=HEADERS, timeout=20)
    antwort.raise_for_status()
    p = SeitenParser()
    p.feed(antwort.text)

    bilder = []
    og = p.meta.get("og:image") or p.meta.get("twitter:image")
    if og and not UNPASSENDE_BILDER.search(og):
        bilder.append(urljoin(antwort.url, og))
    for src in p.bilder:
        voll = urljoin(antwort.url, src)
        if not UNPASSENDE_BILDER.search(voll) and voll not in bilder:
            bilder.append(voll)
        if len(bilder) >= MAX_WEBSITE_BILDER:
            break

    return {
        "website_ok": True,
        "website_titel": (p.meta.get("og:title") or p.titel).strip(),
        "website_beschreibung": (p.meta.get("og:description") or p.meta.get("description") or "").strip(),
        "bilder": [{"url": b, "quelle": "Website"} for b in bilder],
    }


def wiki_infos(titel):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(titel, safe='')}"
    for versuch in range(3):  # Wikipedia liefert bei vielen Abrufen hintereinander gelegentlich leere Antworten
        try:
            daten = requests.get(url, headers=HEADERS, timeout=20).json()
            break
        except ValueError:
            if versuch == 2:
                raise
            time.sleep(3)
    bild = (daten.get("originalimage") or daten.get("thumbnail") or {}).get("source")
    if bild:
        bild = re.sub(r"/\d+px-", "/1280px-", bild)  # Wikimedia-Thumbnails auf handliche Größe
    return {
        "ort_info": daten.get("extract", ""),
        "ort_link": daten.get("content_urls", {}).get("desktop", {}).get("page"),
        "bilder": [{"url": bild, "quelle": "Wikipedia"}] if bild else [],
    }


def anreichern(angebot):
    bilder = []
    if angebot.get("website"):
        try:
            infos = website_infos(angebot["website"])
            bilder += infos.pop("bilder")
            angebot.update(infos)
        except Exception as fehler:  # Website down, blockiert, Timeout – Angebot trotzdem behalten
            angebot["website_ok"] = False
            print(f"  Website nicht erreichbar: {fehler}", file=sys.stderr)
    if angebot.get("ort_wiki"):
        try:
            infos = wiki_infos(angebot["ort_wiki"])
            bilder += infos.pop("bilder")
            angebot.update(infos)
        except Exception as fehler:
            print(f"  Wikipedia fehlgeschlagen: {fehler}", file=sys.stderr)
    angebot["bilder"] = bilder
    return angebot


def main():
    angebote = json.loads(EINGABE.read_text(encoding="utf-8"))
    for a in angebote:
        print(f"{a['id']} …")
        anreichern(a)
        print(f"  {len(a['bilder'])} Bilder, Website {'ok' if a.get('website_ok') else 'FEHLER'}")
    AUSGABE.parent.mkdir(parents=True, exist_ok=True)
    AUSGABE.write_text(json.dumps(angebote, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(angebote)} Angebote → {AUSGABE.relative_to(BASIS)}")


if __name__ == "__main__":
    main()
