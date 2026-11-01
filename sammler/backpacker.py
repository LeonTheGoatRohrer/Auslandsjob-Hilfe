"""Backpacker Job Board (Australien) – Stellen-Sitemap (laut robots.txt erlaubt) + JSON-LD je Stellenseite.

    python -m sammler.backpacker

Geladene Stellenseiten liegen in daten/roh/cache/backpacker/ und werden nach CACHE_TAGE erneut geholt, damit
Änderungen auffallen. Die Sitemap listet alle offenen Stellen (vollstaendig=True): was nicht mehr darin steht,
gilt als geschlossen. Ein gescheiterter Abruf (z. B. Redirect-Schleife bei URLs mit Emojis) wird als Fehler
gemeldet und die zwischengespeicherte Fassung weiterverwendet.
"""

import json
import re
import time
from datetime import datetime, timedelta, timezone

from sammler.gemeinsam import ROH, AbrufFehler, NichtGefunden, hole, speichere, text_aus_html

SITEMAP = "https://www.backpackerjobboard.com.au/sitemapXMLJobs.xml"
CACHE = ROH / "cache" / "backpacker"
MAX_ALTER_TAGE = 60  # ältere Einträge sind meist schon vergeben
CACHE_TAGE = 14


def sammle():
    sitemap = hole(SITEMAP).text
    eintraege = re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", sitemap)
    grenze = datetime.now(timezone.utc) - timedelta(days=MAX_ALTER_TAGE)
    aktuell = [url for url, mod in eintraege if datetime.fromisoformat(mod) >= grenze]
    print(f"  Sitemap: {len(eintraege)} Stellen, {len(aktuell)} jünger als {MAX_ALTER_TAGE} Tage")

    CACHE.mkdir(parents=True, exist_ok=True)
    angebote, fehler, geladen = [], {}, 0
    for i, url in enumerate(aktuell, 1):
        job_id = re.search(r"/job/(\d+)/", url).group(1)
        datei = CACHE / f"{job_id}.json"
        frisch = datei.exists() and time.time() - datei.stat().st_mtime < CACHE_TAGE * 86400
        posting = json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else None
        if not frisch:
            try:
                posting = job_posting(hole(url, pause=1.5).text)
                datei.write_text(json.dumps(posting, ensure_ascii=False), encoding="utf-8")
                geladen += 1
            except NichtGefunden:
                if posting:
                    angebote.append({**umwandeln(job_id, url, posting), "status_quelle": "geschlossen",
                                     "geschlossen_grund": "Seite nicht mehr vorhanden"})
                datei.unlink(missing_ok=True)
                continue
            except AbrufFehler as f:
                fehler[f"backpacker:{job_id}"] = str(f)
                print(f"  {url}: {f}")
        if posting:
            angebote.append(umwandeln(job_id, url, posting))
        if i % 100 == 0:
            print(f"  {i}/{len(aktuell)}")
    print(f"  {geladen} Seiten neu geladen")
    speichere("backpacker", angebote, vollstaendig=True, fehler=fehler)


def job_posting(seite):
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', seite, re.S):
        daten = json.loads(block)
        if daten.get("@type") == "JobPosting":
            return daten
    return None


def umwandeln(job_id, url, p):
    adresse = ((p.get("jobLocation") or {}).get("address") or {}) if isinstance(p.get("jobLocation"), dict) else {}
    organisation = p.get("hiringOrganization") or {}
    return {
        "quelle": "backpacker", "quelle_id": job_id, "url": url,
        "titel": (p.get("title") or "").strip("* "), "organisation": organisation.get("name", ""),
        "ort": adresse.get("addressLocality", ""), "region": adresse.get("addressRegion", ""),
        "land": "Australien", "land_code": "AU",
        "beschreibung": text_aus_html(p.get("description", ""))[:4000],
        "veroeffentlicht": (p.get("datePosted") or "")[:10], "frist": (p.get("validThrough") or "")[:10],
        "extra": {"anstellung": p.get("employmentType"), "lohn": p.get("baseSalary")},
    }


if __name__ == "__main__":
    sammle()
