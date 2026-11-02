# Betrieb der Automatisierung

Stand: 2026-11-01. Ergänzt [02-konzept.md](02-konzept.md): Dort steht das Was, hier das Wie des automatischen Laufs.

## Aufgabenteilung

| Schicht | Was | Warum dort |
|---|---|---|
| **Python in GitHub Actions** | Sammler, Normalisieren, Dubletten, Zustand je Angebot, Vorfilter, Regeln (Visum, Dauer, Gebühr), Passung | deterministisch, mit Tests, versioniert; kein Server nötig |
| **Claude-Code-Routine** (claude.ai, Abo) | KI-Bewertung offener Kandidaten mit Zitaten | kein API-Key nötig; `pipeline/routine.py` bereitet Aufträge vor und prüft die Antworten |
| **n8n** (Cloud oder selbst gehostet) | Zeitplan, E-Mail-Benachrichtigung, Wächter, Fehlerpfad | Ereignisse, Integrationen, Überwachung; Laufhistorie sichtbar |
| **Git-Repo** | alle Zustände als JSON unter `daten/aufbereitet/` | reicht für ein Profil und wenige tausend Angebote; jede Änderung ist ein Commit |
| **Review-App lokal** | Durchsehen, Bewerten, Merken | wie bisher; liest den Repo-Stand |

## Ein Lauf im Detail

1. **n8n W1** startet täglich um 06:00 (Europe/Vienna) den Actions-Workflow `sammeln.yml` (`workflow_dispatch`).
2. **Actions „Sammeln“** (`.github/workflows/sammeln.yml`): Rohdaten und Seiten-Cache kommen aus dem Actions-Cache
   (`daten/roh` ist nicht im Repo). Jeder Sammler läuft einzeln; fällt einer aus, bleibt sein alter Stand und der Lauf
   geht weiter (Warnung im Log). Danach `pipeline/verarbeiten.py` (normalisieren, Zustand, Vorfilter → `kandidaten.json`,
   `aenderungen.json`) und `pipeline/aufbereiten.py` (Regeln, Passung → `gesammelt.json`, `treffer.json`, `status.json`).
   Schließungen und Änderungen sind damit sofort sichtbar, auch ohne neue KI-Bewertung. Commit, dann `POST` an W3.
3. **Claude-Code-Routine** „Auslandsjob: KI-Bewertung neuer Angebote“ (täglich 06:00 UTC = 07:00 Wien im Winter,
   08:00 im Sommer, Modell Sonnet 5.5, ohne Connectoren): `python -m pipeline.routine vorbereiten --max 48` schreibt
   die offenen Kandidaten in Aufträgen à 8 nach `daten/arbeit/`. Die Routine bewertet jeden Auftrag nach
   `config/prompt_bewertung.md`, `python -m pipeline.routine uebernehmen` prüft die Antworten (Pflichtfelder,
   Wertelisten, Kriterien 0–10, Zitate wörtlich in der Anzeige, sonst verworfen) und schreibt `llm_cache/<quelle>.json`
   sowie `bewertungslaeufe.json`. Die Routine committet nur diese Dateien und pusht auf `main`; darf sie das nicht,
   pusht sie auf ihren Arbeitsbranch `claude/…`.
4. **Actions „Aufbereiten“** startet durch den Push (`llm_cache/**`). Kam er von einem `claude/…`-Branch, übernimmt der
   Workflow die Bewertungsdateien nach `main` und löscht den Branch. Danach Aufbereitung wie in Schritt 2, Commit, `POST` an W3.
5. **n8n W3** vergleicht `treffer.json` mit `benachrichtigt.json`: neu (unbekannte ID), geändert (anderer Hash),
   geschlossen (gemerkt und zu). Nur dann eine E-Mail; danach `benachrichtigt.json` fortschreiben.
6. **n8n W2** prüft um 09:00 `status.json` und meldet nur Auffälligkeiten (siehe unten).
7. **n8n W4** meldet jeden Fehler in W1–W3 per E-Mail mit Workflow, Knoten und Link zur Ausführung.

Offen ist ein Kandidat für die Routine, wenn er keine Bewertung hat, sein `inhalts_hash` sich geändert hat oder
`profil.yaml` bzw. der Bewertungs-Prompt geändert wurden (`profil_hash` über beide Dateien). Bewertungen aus Oktober
2026 ohne Zitate gelten weiter, bis der Zustand eine Änderung der Anzeige meldet.

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

Jede neue KI-Bewertung trägt `zitate` für Dauer, Bezahlung, Gebühr, Unterkunft, Verpflegung, Englisch und
Voraussetzungen. Die App zeigt das Zitat unter dem jeweiligen Fakt; fehlt es, steht dort „nicht angegeben – vor
Anfrage prüfen“. Arbeitsberechtigung kommt nicht aus der Anzeige, sondern aus `config/visa.yaml` (Regel) und wird
mit Regeltext angezeigt. Bewertungen aus der Zeit vor den Zitaten (Oktober 2026) zeigen keine Hinweise; sie werden
neu bewertet, sobald sich die Anzeige, das Profil oder der Prompt ändert, oder nach Leeren von `llm_cache/`.

## Dienste, Zugänge, Kosten

| Dienst | Zugang | Kosten (Stand 2026-11-01) |
|---|---|---|
| GitHub (privates Repo) | Secrets `N8N_WEBHOOK_BENACHRICHTIGEN`, `N8N_WEBHOOK_SECRET` | Actions in privaten Repos: 2.000 Freiminuten/Monat (recherchiert); ein Sammellauf braucht 5–40 Min. |
| Claude-Code-Routine | claude.ai-Abo; GitHub-Zugriff der Claude-App auf das Repo | keine Zusatzkosten, verbraucht Abo-Nutzung; höchstens 48 Bewertungen je Lauf |
| n8n Cloud | Testphase (1.000 Ausführungen), danach Starter 20 €/Monat bei Jahreszahlung (Preisseite) | 0 € in der Testphase; selbst gehostet unter Community-Lizenz 0 € + Server |
| Gmail | in n8n einmal „Sign in with Google“ (OAuth), Empfänger im Knoten „Konfiguration“ | 0 € |
| GitHub PAT (fine-grained) | nur dieses Repo: Contents RW, Actions RW; in n8n als Credential „GitHub API“ | 0 € |

n8n-Ausführungen je Tag: W1 1, W2 1, W3 1–2. Das sind etwa 100 im Monat.

## Wächter (n8n W2)

Meldet per E-Mail, wenn in `status.json` eines davon zutrifft; sonst schweigt er:

- letzter Sammellauf älter als 30 h (W1 aus, Actions fehlgeschlagen, Zeitplan nach 60 Tagen ohne Aktivität deaktiviert)
- offene Kandidaten und keine Routine-Bewertung seit 30 h (Routine pausiert, fehlgeschlagen, Abo-Limit erreicht)
- Fehler im letzten Bewertungslauf
- eine Quelle seit mehr als 3 Tagen nicht neu abgerufen (Sammler fällt dauerhaft aus)
- Abruffehler im letzten Lauf (zählen nicht als geschlossen)

## Wiederanlauf und Fehlerbilder

- **Sammler fällt aus**: Lauf läuft weiter, alter Stand der Quelle bleibt, keine Schließungen aus dieser Quelle; W2 meldet es nach 3 Tagen.
- **Actions-Lauf bricht ab**: nichts committet, nächster Lauf beginnt beim letzten Stand. Manuell: W1 manuell starten oder Actions-Tab → „Sammeln“.
- **Routine fällt aus oder bricht ab**: Bewertungen werden erst beim Übernehmen geschrieben, ein Abbruch hinterlässt nichts Halbes. Unter https://claude.ai/code/routines „Run now“; bewertet wird nur, was noch offen ist.
- **Antworten der Routine fehlerhaft**: `uebernehmen` übernimmt die gültigen, verwirft den Rest mit Grund; verworfene bleiben offen und kommen im nächsten Lauf wieder. Fehler stehen in `bewertungslaeufe.json` und lösen den Wächter aus.
- **Commit-Konflikt**: Actions und Routine machen `git pull --rebase` vor dem Push; `concurrency: pipeline` verhindert parallele Actions-Läufe.
- **Doppelte Nachricht**: ausgeschlossen über `benachrichtigt.json` (ID + Hash + Ereignis).
- **NAV-Cursor kaputt**: `daten/aufbereitet/nav_cursor.json` löschen → nächster Lauf liest den Feed vollständig (ca. 5.000 Seiten, ~30 Min.).
- **Alles neu bewerten**: Prompt oder Profil ändern genügt; oder `daten/aufbereitet/llm_cache/` leeren. Die Routine arbeitet den Bestand in Schritten von 48 ab.

## Demo: gefunden → belegt → bewertet → angezeigt → geändert → geschlossen

Die Demo-Quelle (`sammler/demo.py`, `tests/fixtures/demo_quelle.json`) liefert zwei erfundene Angebote.

1. Actions „Sammeln“ mit Eingabe `demo = true` starten (oder lokal `DEMO_QUELLE=1 python -m sammler.demo && python -m pipeline.verarbeiten`).
   → `aenderungen.json` zeigt `demo:werft-1`, `demo:station-2` unter `neu`; die Routine bewertet sie mit Zitaten
   (sofort per „Run now“); W3 meldet sie als neue Treffer.
2. In `tests/fixtures/demo_quelle.json` die Frist von `werft-1` ändern, committen, Lauf wiederholen.
   → `geaendert` mit Feld `frist`; die Karte trägt „Geändert“; Nachricht „geänderte Treffer“.
3. `werft-1` aus der Datei entfernen, Lauf wiederholen.
   → `geschlossen` mit Grund „nicht mehr gelistet“; Karte „Geschlossen“; ist das Angebot gemerkt, meldet W3 die Schließung.
4. Lauf ohne `demo` → Demo-Rohdatei wird entfernt; die Demo-Angebote bleiben als geschlossen im Zustand.

Ohne n8n lassen sich die Code-Knoten von W2/W3 prüfen: `node n8n/simulation.js`. Die Prüfung der Routine-Antworten
(erfundenes Zitat wird verworfen, unvollständige Bewertung bleibt offen) decken die Tests in `tests/test_routine.py` ab.

## Bekannte Grenzen

- Dublettenerkennung über Quellen greift erst, wenn eine überlappende Quelle (z. B. EURES) angebunden ist.
- Die Routine läuft per Zeitplan (Cron in UTC, Sommerzeit verschiebt sie um eine Stunde), nicht direkt nach dem Sammellauf.
- Der Abo-Verbrauch der Routine ist nicht in Euro messbar; `bewertungslaeufe.json` zählt nur Angebote und Fehler.
- Backpacker-Seiten werden nur alle 14 Tage neu geladen; Änderungen dort fallen entsprechend verzögert auf.
- JobTech: Suchbegriffe sind fest; neue Anzeigen außerhalb der Begriffe werden nicht gefunden.
- Mehrere Profile sind vorbereitet (Profil-Hash im Cache), aber nicht umgesetzt (ein `profil.yaml`, eine `bewertungen.json`).
