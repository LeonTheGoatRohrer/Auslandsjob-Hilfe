# n8n-Workflows

Vier Workflows, als JSON exportiert und in der n8n-Cloud-Instanz `summerjobs.app.n8n.cloud` angelegt (Stand 2026-11-01).
Alles Deterministische (Sammeln, Regeln, Zustand, Ranking) läuft als Python in GitHub Actions, die KI-Bewertung als
Claude-Code-Routine über das Abo. n8n übernimmt Zeitplan, Benachrichtigung, Überwachung und Fehlerpfad.

```
W1 Dirigent          06:00 Wien ──► GitHub: workflow_dispatch sammeln.yml
                        (Actions sammelt, verarbeitet, bereitet auf, committet, ruft Webhook W3)
Routine (claude.ai)  07:00 Wien ──► bewertet offene Kandidaten ──► pusht llm_cache/
                        (Push startet Actions „Aufbereiten“, das ruft Webhook W3)
W3 Benachrichtigen   Webhook ──► treffer.json gegen benachrichtigt.json ──► Telegram ──► benachrichtigt.json
W2 Wächter           09:00 Wien ──► status.json ──► Telegram nur bei Auffälligkeiten
W4 Fehler            Error Trigger ──► Telegram
```

| Workflow | ID in n8n |
|---|---|
| W1 Dirigent | `NIH8EQK1DEo5ltzG` |
| W2 Wächter | `qqjsrgrPHTrGvS89` |
| W3 Benachrichtigen | `h4FCsxtoYnSZQRfz` |
| W4 Fehler | `4uUXYTzugTjCzqLo` |

## Einrichten

1. Credentials in n8n anlegen und in den Knoten auswählen. In der Instanz heißen sie „GitHub account“ und „Telegram account“ und sind bereits mit allen Knoten verbunden; der Name selbst ist egal:

   | Name in den Workflows | Typ | Inhalt |
   |---|---|---|
   | `GitHub Auslandsjob` | GitHub API | Access Token = fine-grained PAT nur für dieses Repo: *Contents: Read and write*, *Actions: Read and write*. |
   | `Auftrag-Secret (X-Auftrag-Secret)` | Header Auth | Name `X-Auftrag-Secret`, Wert = selbst gewähltes langes Geheimnis; derselbe Wert als Repo-Secret `N8N_WEBHOOK_SECRET`. |
   | `Telegram Bot` | Telegram API | Bot-Token von @BotFather |

2. In W2, W3 (Knoten **Konfiguration**) und W4 (Knoten **Telegram: Fehler melden**) die eigene Telegram-Chat-ID statt `DEINE_TELEGRAM_CHAT_ID` eintragen.
3. W4 veröffentlichen, dann in den Einstellungen von W1–W3 W4 als *Error workflow* auswählen.
4. Im GitHub-Repo unter *Settings → Secrets and variables → Actions*:
   `N8N_WEBHOOK_BENACHRICHTIGEN` = `https://summerjobs.app.n8n.cloud/webhook/auslandsjob-benachrichtigen`,
   `N8N_WEBHOOK_SECRET` = das Geheimnis aus Schritt 1.
5. W1, W2, W3 veröffentlichen.

## Datenvertrag

- Actions → W3: `POST <webhook>` mit `{lauf_id, commit, treffer}` und Header `X-Auftrag-Secret`. Ohne gesetztes Secret
  überspringt Actions den Schritt.
- W3 meldet nur, was in `benachrichtigt.json` noch nicht steht (neu), einen anderen `inhalts_hash` hat (geändert)
  oder ein gemerktes Angebot ist, das geschlossen wurde. Ohne Neuigkeit keine Nachricht. Danach schreibt W3
  `benachrichtigt.json` per GitHub-API zurück.
- W2 liest `status.json` (von `pipeline/aufbereiten.py`) und warnt bei: Sammellauf älter als 30 h, offene Kandidaten
  und keine Routine-Bewertung seit 30 h, Fehler im letzten Bewertungslauf, Quelle seit über 3 Tagen nicht neu
  abgerufen, Abruffehler im letzten Lauf.

## Simulation ohne n8n

`node n8n/simulation.js` spielt die Code-Knoten von W2 und W3 gegen die echten Repo-Daten durch: der Wächter mit
dem aktuellen, einem veralteten und einem gesunden Status; die Benachrichtigung zweimal hintereinander, wobei der
zweite Lauf nichts melden darf.
