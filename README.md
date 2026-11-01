# Auslandsjob-Hilfe

Persönliches Tool, um weltweit die eine außergewöhnliche Auslandserfahrung für 2027 zu finden:
Angebote aus vielen Quellen sammeln, gegen meine Kriterien bewerten und die besten als Karten
zum schnellen Durcharbeiten (Bewertung 1–10) aufbereiten. Seit November 2026 läuft die Suche automatisch:
GitHub Actions sammelt und filtert, n8n lässt Claude bewerten und meldet neue Treffer per Telegram.

## Dokumente

- [docs/01-kriterien.md](docs/01-kriterien.md) – was ich suche (Originaltext)
- [docs/02-konzept.md](docs/02-konzept.md) – wie das Tool funktionieren soll
- [docs/03-quellen.md](docs/03-quellen.md) – Liste der Quellen
- [docs/04-betrieb.md](docs/04-betrieb.md) – Automatisierung: Ablauf, Dienste, Kosten, Wiederanlauf, Demo
- [config/profil.yaml](config/profil.yaml) – Kriterien in maschinenlesbarer Form
- [n8n/README.md](n8n/README.md) – die vier n8n-Workflows und ihr Datenvertrag

## Struktur

```
docs/       Anforderungen, Konzept, Quellen, Betrieb
config/     Suchprofil, Visa-Regeln, Bewertungs-Prompt
sammler/    ein Adapter pro Quelle (Feed / API / Sitemap / HTML), inkrementell und fehlertolerant
pipeline/   normalisieren → Zustand (neu/geändert/geschlossen) → Vorfilter → Aufbereitung + Ranking
n8n/        Workflows: Zeitplan, KI-Bewertung mit Claude, Telegram, Fehler
app/        Review-Oberfläche (Karten, Belege, Zustand, 1–10-Bewertung)
tests/      pytest, Fixtures aus echten Rohdaten, Demo-Quelle
daten/      roh/ = Rohdaten je Quelle (nicht im Git), aufbereitet/ = Zustand, Kandidaten, Bewertungen (im Git)
```

## Ablauf eines Laufs

```
n8n W1 (06:00) ─► Actions „Sammeln“: Sammler → normalisieren → Zustand → Vorfilter → Commit ─► Webhook
n8n W2: offene Kandidaten → Claude Sonnet 5.5 (Stapel à 8, Zitat je Fakt) → llm_cache/ ins Repo ─► Actions „Aufbereiten“
Actions „Aufbereiten“: Regeln (Visum, Dauer, Gebühr), Passung → gesammelt.json, treffer.json → Commit ─► Webhook
n8n W3: neue / geänderte Treffer, geschlossene Gemerkte → Telegram          n8n W4: Fehler → Telegram
```

## Lokal starten

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest                 # Tests
git pull                         # neuesten Datenstand holen
python app/server.py             # dann http://localhost:8765 öffnen
```

Deine Bewertungen, Herzen und Notizen landen in `daten/aufbereitet/bewertungen.json`. Die Datei ist im Git,
damit die Pipeline geschlossene gemerkte Angebote melden kann: nach einer Session `git commit` und `git push`.

### Pipeline von Hand

```
python -m sammler.nav            # Norwegen (erster Lauf liest den ganzen Feed, danach nur ab Cursor)
python -m sammler.jobtech        # Schweden
python -m sammler.backpacker     # Australien (Seiten-Cache, Erneuerung nach 14 Tagen)
python -m sammler.tamu           # Texas A&M, nur internationale Stellen
python -m pipeline.verarbeiten   # normalisieren, Zustand fortschreiben, Vorfilter → kandidaten.json
python -m pipeline.aufbereiten   # KI-Bewertungen aus llm_cache/ + Regeln → gesammelt.json, treffer.json
python pipeline/anreichern.py    # kuratierte Angebote: Website-Infos und Bilder (nach Änderungen an daten/kuratiert/)
```

Die KI-Bewertung selbst läuft in n8n (Workflow W2); lokal gibt es dafür keinen Ersatz.
Für Sommer 2027 lohnt sich ein voller Lauf ab Jänner 2027 – vorher sind die meisten Saisonstellen noch nicht ausgeschrieben.
