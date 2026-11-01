# Auslandsjob-Hilfe

Persönliches Tool, um weltweit die eine außergewöhnliche Auslandserfahrung für 2027 zu finden:
Angebote aus vielen Quellen sammeln, gegen meine Kriterien bewerten und die besten ~100 als Karten
zum schnellen Durcharbeiten (Bewertung 1–10) aufbereiten.

## Dokumente

- [docs/01-kriterien.md](docs/01-kriterien.md) – was ich suche (Originaltext)
- [docs/02-konzept.md](docs/02-konzept.md) – wie das Tool funktionieren soll
- [docs/03-quellen.md](docs/03-quellen.md) – Liste der Quellen
- [config/profil.yaml](config/profil.yaml) – Kriterien in maschinenlesbarer Form

## Struktur

```
docs/       Anforderungen, Konzept, Quellen
config/     Suchprofil und Gewichtung
sammler/    ein Adapter pro Quelle (Scraper / API)
pipeline/   Vereinheitlichen, Filtern, Bewerten
app/        Review-Oberfläche (Karten, 1–10-Bewertung)
daten/      roh/ = Rohdaten je Quelle, aufbereitet/ = Datenbank (nicht im Git)
```

## Starten

```
pip install -r requirements.txt
python pipeline/anreichern.py   # Websites + Bilder holen (nach Änderungen an daten/kuratiert/)
python pipeline/quellen_aus_recherche.py   # Quellen-Tabellen aus docs/recherche/ für die App übernehmen
python app/server.py            # dann http://localhost:8765 öffnen
```

Deine Bewertungen, Herzen und Notizen landen in `daten/aufbereitet/bewertungen.json`.

### Automatisch sammeln

```
python -m sammler.nav            # Norwegen (langsam, die Suche drosselt)
python -m sammler.jobtech        # Schweden
python -m sammler.backpacker     # Australien (Seiten werden zwischengespeichert)
python -m sammler.tamu           # Texas A&M, nur internationale Stellen
python pipeline/vorfilter.py     # ohne KI aussortieren → kandidaten.json
python pipeline/bewerten_llm.py  # Claude bewertet (braucht angemeldete Claude-CLI)
```

Danach den Server neu starten. Für Sommer 2027 lohnt sich ein neuer Lauf ab Jänner 2027 – vorher sind
die meisten Saisonstellen noch nicht ausgeschrieben.

## Stand

Erster Prototyp: kuratierte Startdaten (vorläufig) + Review-App. Automatisches Scraping folgt.
