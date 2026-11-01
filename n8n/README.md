# n8n-Workflows

Vier Workflows, als JSON exportiert und in n8n (Cloud oder selbst gehostet) importierbar. Alles Deterministische
(Sammeln, Regeln, Zustand, Ranking) läuft als Python in GitHub Actions; n8n übernimmt Zeitplan, KI-Bewertung,
Benachrichtigung und Fehlerpfad.

```
W1 Dirigent          Zeitplan 06:00 ──► GitHub: workflow_dispatch sammeln.yml
                        (Actions sammelt, verarbeitet, committet, ruft Webhook W2)
W2 Bewerten          Webhook ──► offene Kandidaten ──► Claude (Stapel à 8) ──► Zitate prüfen
                        ──► llm_cache/<quelle>.json + lauf_kosten.json ins Repo
                        ──► Rest? eigenen Webhook erneut ──► sonst workflow_dispatch aufbereiten.yml
                        (Actions bereitet auf, committet, ruft Webhook W3)
W3 Benachrichtigen   Webhook ──► treffer.json gegen benachrichtigt.json ──► Telegram ──► benachrichtigt.json
W4 Fehler            Error Trigger ──► Telegram
```

## Import

1. In n8n: *Workflows → Import from file*, nacheinander `W1_dirigent.json`, `W2_bewerten.json`,
   `W3_benachrichtigen.json`, `W4_fehler.json`.
2. Credentials anlegen (Namen müssen zu den Knoten passen, sonst im Knoten neu zuordnen):

   | Name in den Workflows | Typ | Inhalt |
   |---|---|---|
   | `GitHub PAT (Authorization)` | Header Auth | Name `Authorization`, Wert `Bearer <fine-grained PAT>`. Rechte nur für dieses Repo: *Contents: Read and write*, *Actions: Read and write*. |
   | `Anthropic API (x-api-key)` | Header Auth | Name `x-api-key`, Wert = API-Key von console.anthropic.com |
   | `Auftrag-Secret (X-Auftrag-Secret)` | Header Auth | Name `X-Auftrag-Secret`, Wert = selbst gewähltes langes Geheimnis. Derselbe Wert kommt als Secret `N8N_WEBHOOK_SECRET` ins GitHub-Repo. |
   | `Telegram Bot` | Telegram API | Bot-Token von @BotFather |

3. Im Knoten **Konfiguration** von W1, W2, W3: `owner`, `repo`, `branch` prüfen; in W2 `fortsetzen_url` auf die
   Produktions-URL des eigenen Webhooks setzen (steht im Webhook-Knoten, Form `https://<konto>.app.n8n.cloud/webhook/auslandsjob-bewerten`);
   in W3 und W4 `telegram_chat_id` bzw. `chatId` eintragen (eigene Chat-ID, z. B. über @userinfobot).
4. W4 in den Einstellungen von W1–W3 als *Error workflow* eintragen.
5. GitHub-Repo → *Settings → Secrets and variables → Actions*:
   `N8N_WEBHOOK_BEWERTEN` = Produktions-URL des W2-Webhooks, `N8N_WEBHOOK_BENACHRICHTIGEN` = die von W3,
   `N8N_WEBHOOK_SECRET` = das Geheimnis aus Schritt 2.
6. W1–W4 aktivieren.

## Datenvertrag zwischen Actions und n8n

- Actions → W2: `POST <webhook>` mit `{lauf_id, commit, zaehlung}`; Header `X-Auftrag-Secret`.
- W2 liest aus dem Repo: `daten/aufbereitet/kandidaten.json`, `config/profil.yaml`, `config/prompt_bewertung.md`,
  `daten/aufbereitet/llm_cache/<quelle>.json`. Es bewertet nur Kandidaten ohne Eintrag oder mit anderem
  `inhalts_hash`/`profil_hash`, höchstens `max_stapel × stapel_groesse` je Ausführung (Cloud-Testphase: 180 s Limit),
  und ruft sich über `fortsetzen_url` selbst wieder auf, bis nichts mehr offen ist.
- W2 schreibt je Quelle `llm_cache/<quelle>.json` (Einträge mit `inhalts_hash`, `profil_hash`, `bewertet_am`, `modell`,
  `zitate`, `zitate_ungueltig`) und hängt an `lauf_kosten.json` an (Tokens, Kosten in USD, Fehler je Lauf).
- Zitate, die nicht wörtlich in der Anzeige stehen, werden auf `null` gesetzt und in `zitate_ungueltig` vermerkt;
  das Feld zählt dann in der App als „nicht angegeben“.
- Actions (aufbereiten) → W3: `POST <webhook>` mit `{lauf_id, commit, treffer}`.
- W3 meldet nur, was in `benachrichtigt.json` noch nicht steht (neu), einen anderen `inhalts_hash` hat (geändert)
  oder ein gemerktes Angebot ist, das geschlossen wurde. Ohne Neuigkeit keine Nachricht.

## Wiederaufnahme

- Bewertung abgebrochen: W2-Webhook erneut aufrufen (`curl -X POST <url> -H "X-Auftrag-Secret: …" -d '{"lauf_id":"manuell"}'`).
  Bereits bewertete Kandidaten werden nicht erneut geschickt.
- Aufbereitung oder Nachricht fehlgeschlagen: `aufbereiten.yml` im Actions-Tab manuell starten; W3 entprellt über `benachrichtigt.json`.
- Alles neu bewerten (z. B. nach Prompt-Änderung): `config/profil.yaml` ändern reicht nicht, der Prompt ist nicht im Hash.
  Dann `daten/aufbereitet/llm_cache/` leeren oder im Workflow den Vergleich kurz aussetzen.

## Simulation ohne n8n

Die Code-Knoten lassen sich mit Node.js gegen die echten Repo-Daten durchspielen (siehe `docs/04-betrieb.md`).
