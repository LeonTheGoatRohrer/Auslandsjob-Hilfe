# Betrieb der Automatisierung

Stand: 2026-11-01. Ergänzt [02-konzept.md](02-konzept.md): Dort steht das Was, hier das Wie des automatischen Laufs.

## Aufgabenteilung

| Schicht | Was | Warum dort |
|---|---|---|
| **Python in GitHub Actions** | Sammler, Normalisieren, Dubletten, Zustand je Angebot, Vorfilter, Regeln (Visum, Dauer, Gebühr), Passung | deterministisch, mit Tests, versioniert; kein Server nötig |
| **n8n** (Cloud oder selbst gehostet) | Zeitplan, KI-Bewertung mit Claude, Zitatprüfung, Kostenprotokoll, Telegram, Fehlerpfad | Ereignisse, Integrationen und Mensch-in-der-Schleife; Laufhistorie sichtbar |
| **Git-Repo** | alle Zustände als JSON unter `daten/aufbereitet/` | reicht für ein Profil und wenige tausend Angebote; jede Änderung ist ein Commit |
| **Review-App lokal** | Durchsehen, Bewerten, Merken | wie bisher; liest den Repo-Stand |

## Ein Lauf im Detail

1. **n8n W1** startet täglich um 06:00 (Europe/Vienna) den Actions-Workflow `sammeln.yml` (`workflow_dispatch`).
2. **Actions „Sammeln“** (`.github/workflows/sammeln.yml`): Rohdaten und Seiten-Cache kommen aus dem Actions-Cache
   (`daten/roh` ist nicht im Repo). Jeder Sammler läuft einzeln; fällt einer aus, bleibt sein alter Stand und der Lauf
   geht weiter (Warnung im Log). Danach `pipeline/verarbeiten.py`: normalisieren (`key`, `inhalts_hash`, Dubletten),
   Zustand fortschreiben (`zustand.json`), Vorfilter → `kandidaten.json`, Laufprotokoll `aenderungen.json`.
   Commit, dann `POST` an den n8n-Webhook W2 mit `lauf_id`, Commit-SHA und Zählung.
3. **n8n W2** liest Kandidaten, Profil, Prompt und `llm_cache/<quelle>.json` aus dem Repo, bewertet nur Kandidaten
   ohne Eintrag oder mit anderem `inhalts_hash`/`profil_hash`, in Stapeln à 8 über die Anthropic-API
   (Modell im Knoten „Konfiguration“, Standard Sonnet 5.5). Zitate müssen wörtlich in der Anzeige stehen, sonst werden
   sie verworfen und das Feld gilt als „nicht angegeben“. Ergebnisse gehen per GitHub-API ins Repo, Kosten nach
   `lauf_kosten.json`. Bleibt Rest, ruft W2 seinen eigenen Webhook erneut auf; sonst startet es `aufbereiten.yml`.
4. **Actions „Aufbereiten“**: `pipeline/aufbereiten.py` führt Kandidaten, Bewertungen und Zustand zusammen, wendet
   `ranking.py` an (Visa-Regeln, Dauerfenster, Gebührengrenze, gewichtete Passung) → `gesammelt.json` (App) und
   `treffer.json` (Treffer ab `benachrichtigung.passung_min`, geschlossene gemerkte Angebote). Commit, `POST` an W3.
5. **n8n W3** vergleicht `treffer.json` mit `benachrichtigt.json`: neu (unbekannte ID), geändert (anderer Hash),
   geschlossen (gemerkt und zu). Nur dann eine Telegram-Nachricht; danach `benachrichtigt.json` fortschreiben.
6. **n8n W4** meldet jeden Fehler in W1–W3 per Telegram mit Workflow, Knoten und Link zur Ausführung.

## Zustandsmodell (`zustand.json`)

| Ereignis | Wirkung |
|---|---|
| Angebot zum ersten Mal gesehen | `erstmals_gesehen`, Status `offen`, in `aenderungen.json → neu` |
| gesehen, `inhalts_hash` gleich | nur `zuletzt_gesehen` |
| gesehen, Hash anders | Feld-Diff in `aenderungen[]` (alt/neu, auf 200 Zeichen gekürzt), KI bewertet neu |
| Quelle meldet Ende (NAV-Status, JobTech `removed`, Seite 404) | Status `geschlossen` mit Grund |
| vollständig gelisteter Lauf enthält Angebot nicht mehr (Backpacker-Sitemap, TAMU, Demo) | `geschlossen`, Grund „nicht mehr gelistet“ |
| Abruf gescheitert (Timeout, 5xx, Redirect-Schleife) | `fehlversuche + 1`, Status bleibt; ab 3 → `unbekannt`; nie `geschlossen` |
| wieder gesehen | zurück auf `offen`, Fehlversuche 0 |

Geschlossene Angebote sind keine Kandidaten mehr, bleiben aber mit letztem Stand in `gesammelt.json` und in der App
(Schalter „Geschlossene zeigen“).

## Belege und „nicht angegeben“

Jede KI-Bewertung trägt `zitate` für Dauer, Bezahlung, Gebühr, Unterkunft, Verpflegung, Englisch und
Voraussetzungen. Die App zeigt das Zitat unter dem jeweiligen Fakt; fehlt es, steht dort „nicht angegeben – vor
Anfrage prüfen“. Arbeitsberechtigung kommt nicht aus der Anzeige, sondern aus `config/visa.yaml` (Regel) und wird
mit Regeltext angezeigt. Bewertungen aus der Zeit vor den Zitaten (Oktober 2026) zeigen keine Hinweise; sie werden
beim nächsten Lauf neu bewertet, sobald sich die Anzeige oder das Profil ändert, oder nach Leeren von `llm_cache/`.

## Dienste, Zugänge, Kosten

| Dienst | Zugang | Kosten (Stand 2026-11-01) |
|---|---|---|
| GitHub Actions | öffentliches Repo, Secrets `N8N_WEBHOOK_BEWERTEN`, `N8N_WEBHOOK_BENACHRICHTIGEN`, `N8N_WEBHOOK_SECRET` | öffentlich: kostenlos (recherchiert); privat: 2.000 Freiminuten/Monat, ein Lauf braucht 5–40 Min. |
| n8n Cloud | Testphase (1.000 Ausführungen), danach Starter 20 €/Monat bei Jahreszahlung (Preisseite) | 0 € in der Testphase; selbst gehostet unter Community-Lizenz 0 € + Server |
| Anthropic API | Key in n8n-Credential; Modell und Preise im Knoten „Konfiguration“ | Sonnet 5.5: 2 $/10 $ je Mio. Token (Modelltabelle vom 2026-10-06). Schätzung: Vollauf aller ~490 Kandidaten ≈ 2–3 $, Tageslauf Cent-Beträge. Ist-Werte in `lauf_kosten.json`. |
| Telegram | Bot-Token (@BotFather), Chat-ID | 0 € |
| GitHub PAT (fine-grained) | nur dieses Repo: Contents RW, Actions RW; in n8n als Header-Auth | 0 € |

Ausführungen je Lauf in n8n: W1 1, W2 1 + eine je Fortsetzung (24 Kandidaten je Ausführung), W3 1. Bei täglichem
Lauf und wenigen neuen Angeboten ≈ 3–5 Ausführungen/Tag, also ≈ 100–150/Monat.

## Wiederanlauf und Fehlerbilder

- **Sammler fällt aus**: Lauf läuft weiter, alter Stand der Quelle bleibt, keine Schließungen aus dieser Quelle.
- **Actions-Lauf bricht ab**: nichts committet, nächster Lauf beginnt beim letzten Stand. Manuell: Actions-Tab → „Sammeln“ → Run workflow.
- **W2 bricht ab** (API-Fehler, Limit): W4 meldet es; bereits geschriebene Cache-Dateien bleiben; Webhook erneut aufrufen, nur Offenes wird bewertet.
- **Commit-Konflikt** (409 beim Schreiben): W2 wiederholt den Knoten; Actions macht `git pull --rebase` vor dem Push; `concurrency: pipeline` verhindert parallele Läufe.
- **Doppelte Nachricht**: ausgeschlossen über `benachrichtigt.json` (ID + Hash + Ereignis).
- **NAV-Cursor kaputt**: `daten/aufbereitet/nav_cursor.json` löschen → nächster Lauf liest den Feed vollständig (ca. 5.000 Seiten, ~30 Min.).
- **Alles neu bewerten**: `daten/aufbereitet/llm_cache/` leeren und committen.

## Demo: gefunden → belegt → bewertet → angezeigt → geändert → geschlossen

Die Demo-Quelle (`sammler/demo.py`, `tests/fixtures/demo_quelle.json`) liefert zwei erfundene Angebote.

1. Actions „Sammeln“ mit Eingabe `demo = true` starten (oder lokal `DEMO_QUELLE=1 python -m sammler.demo && python -m pipeline.verarbeiten`).
   → `aenderungen.json` zeigt `demo:werft-1`, `demo:station-2` unter `neu`; W2 bewertet sie mit Zitaten; W3 meldet sie als neue Treffer.
2. In `tests/fixtures/demo_quelle.json` die Frist von `werft-1` ändern, committen, Lauf wiederholen.
   → `geaendert` mit Feld `frist`; die Karte trägt „Geändert“; Nachricht „geänderte Treffer“.
3. `werft-1` aus der Datei entfernen, Lauf wiederholen.
   → `geschlossen` mit Grund „nicht mehr gelistet“; Karte „Geschlossen“; ist das Angebot gemerkt, meldet W3 die Schließung.
4. Lauf ohne `demo` → Demo-Rohdatei wird entfernt; die Demo-Angebote bleiben als geschlossen im Zustand.

Ohne n8n lassen sich die Code-Knoten von W2/W3 prüfen: `node n8n/simulation.js` (nutzt die echten Repo-Daten und eine
gefälschte Claude-Antwort mit einem erfundenen Zitat, das verworfen werden muss).

## Bekannte Grenzen

- Dublettenerkennung über Quellen greift erst, wenn eine überlappende Quelle (z. B. EURES) angebunden ist.
- n8n Cloud in der Testphase: 180 s je Ausführung, daher höchstens 3 Claude-Stapel je Ausführung (`max_stapel`).
- Backpacker-Seiten werden nur alle 14 Tage neu geladen; Änderungen dort fallen entsprechend verzögert auf.
- JobTech: Suchbegriffe sind fest; neue Anzeigen außerhalb der Begriffe werden nicht gefunden.
- Mehrere Profile sind vorbereitet (Profil-Hash im Cache), aber nicht umgesetzt (ein `profil.yaml`, eine `bewertungen.json`).
