# n8n-Workflows

Vier Workflows, als JSON exportiert und in der n8n-Cloud-Instanz `summerjobs.app.n8n.cloud` angelegt (Stand 2026-11-01).
Alles Deterministische (Sammeln, Regeln, Zustand, Ranking) läuft als Python in GitHub Actions, die KI-Bewertung als
Claude-Code-Routine über das Abo. n8n übernimmt Zeitplan, Benachrichtigung, Überwachung und Fehlerpfad.

```
W1 Dirigent          06:00 Wien ──► GitHub: workflow_dispatch sammeln.yml
                        (Actions sammelt, verarbeitet, bereitet auf, committet, ruft Webhook W3)
Routine (claude.ai)  07:00 Wien ──► bewertet offene Kandidaten ──► pusht llm_cache/
                        (Push startet Actions „Aufbereiten“, das ruft Webhook W3)
W3 Benachrichtigen   Webhook ──► treffer.json gegen benachrichtigt.json ──► E-Mail ──► benachrichtigt.json
W2 Wächter           09:00 Wien ──► status.json ──► E-Mail nur bei Auffälligkeiten
W4 Fehler            Error Trigger ──► E-Mail
```

| Workflow | ID in n8n |
|---|---|
| W1 Dirigent | `NIH8EQK1DEo5ltzG` |
| W2 Wächter | `qqjsrgrPHTrGvS89` |
| W3 Benachrichtigen | `h4FCsxtoYnSZQRfz` |
| W4 Fehler | `4uUXYTzugTjCzqLo` |

## Einrichten

Stand 2026-11-02 erledigt: Zugänge „GitHub account“ (fine-grained PAT nur für dieses Repo, *Contents* und *Actions*
Read and write) ist angelegt und mit allen Knoten verbunden. Benachrichtigt wird per E-Mail über Gmail an
leonrohrer06@gmail.com (Empfänger im Knoten „Konfiguration“ von W2/W3 bzw. im Gmail-Knoten von W4).
Die Repo-Secrets `N8N_WEBHOOK_BENACHRICHTIGEN` und `N8N_WEBHOOK_SECRET` sind gesetzt.

Offen bzw. bei einer Neueinrichtung:

1. Gmail verbinden: einen der Gmail-Knoten öffnen, bei *Credential* „Create new“ → „Sign in with Google“,
   danach denselben Zugang in den beiden anderen Gmail-Knoten auswählen.
2. W4 veröffentlichen, dann in den Einstellungen von W1–W3 W4 als *Error workflow* auswählen.
3. W1, W2, W3 veröffentlichen.

**Absenderprüfung in W3:** Der Webhook ist ohne n8n-Credential erreichbar. Der Knoten **Absender prüfen** lässt nur
Aufrufe durch, deren Header `X-Auftrag-Secret` den gleichen SHA-256-Hash hat wie das Repo-Secret `N8N_WEBHOOK_SECRET`.
In n8n steht nur der Hash, nicht das Secret. Wird das Secret erneuert, muss der Hash im Knoten mitgeändert werden
(`python -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.read().strip().encode()).hexdigest())"`).

## Datenvertrag

- Actions → W3: `POST <webhook>` mit `{lauf_id, commit, treffer}` und Header `X-Auftrag-Secret`. Ohne gesetztes
  Repo-Secret überspringt Actions den Schritt; ein falscher Header endet in W3 still am Knoten „Absender prüfen“.
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
