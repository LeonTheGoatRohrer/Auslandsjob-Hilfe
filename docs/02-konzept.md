# Konzept

## Ziel des Tools

Aus möglichst allen weltweiten Quellen Angebote einsammeln, gegen [die Kriterien](01-kriterien.md)
bewerten und mir die besten ~100 so vorlegen, dass ich sie schnell durcharbeiten kann
(Karte für Karte, Bewertung 1–10). Meine Bewertungen fließen zurück und verbessern das Ranking.

## Ablauf (Pipeline)

```
 Quellen ──► Sammeln ──► Vereinheitlichen ──► Filtern ──► Bewerten ──► Review-App
 (Portale,   (Scraper,   (ein gemeinsames     (harte      (LLM gegen   (Karten,
  Listen,     APIs,       Datenformat,         Kriterien)  profil.yaml) 1–10, Notizen)
  Betriebe)   RSS)        Duplikate raus)                       ▲            │
                                                                └─ Feedback ─┘
```

1. **Sammeln** – pro Quelle ein eigener Adapter. Rohdaten werden unverändert gespeichert,
   damit man später neu auswerten kann, ohne neu zu scrapen.
2. **Vereinheitlichen** – alle Angebote in ein gemeinsames Format bringen
   (Titel, Organisation, Ort, Zeitraum, Dauer, Bezahlung, Unterkunft, Kosten, Beschreibung, Link).
   Viele Felder stehen nur im Freitext → hier hilft ein LLM beim Extrahieren.
3. **Filtern** – harte Ausschlüsse aus `profil.yaml` (Zeitraum, Gebühren, Visum).
4. **Bewerten** – je Kernkriterium 0–10 plus kurze Begründung; daraus ein gewichteter Gesamtwert.
5. **Review** – die Top-N als Karten; ich bewerte 1–10, markiere „merken / verwerfen“, schreibe Notizen.
6. **Feedback** – meine Bewertungen justieren die Gewichte bzw. dienen dem LLM als Beispiele.

## Zwei Arten von Treffern

| Typ | Beschreibung | Beispiel |
|---|---|---|
| **Ausschreibung** | Offiziell ausgeschriebene Stelle / Volunteer-Platz | Crew-Stelle auf Forschungsschiff, Farmjob in Australien |
| **Lead** | Betrieb ohne Ausschreibung, den man direkt anfragen kann | Kleiner Bootsbauer in Japan, Schmiede in Norwegen |

Gerade die Wunsch-Beispiele (japanischer Bootsbauer, kleine Werkstatt) sind fast nie
ausgeschrieben. Leads brauchen eine eigene Suchstrategie (Verzeichnisse, Verbände, Karten-Daten,
Handwerkskammern) und am Ende eine Anfrage-Mail statt einer Bewerbung.

## Kategorien

Sieben Hauptkategorien (Details und Unterpunkte in `config/profil.yaml`):
💰 Bezahlte Jobs · ⚡ Extrem & Mission · 🔨 Handwerk lernen · 🌿 Natur & Forschung ·
🌊 Meer & Schiffe · 🏯 Kultur & Gemeinschaft · 🔧 Technik einbringen.

Jedes Angebot hat eine Hauptkategorie plus Tags aus anderen Kategorien. Darüber liegen
Querfilter: Bezahlung (inkl. rot markiertem „kostet Geld“), Unterkunft, Englisch im Betrieb,
Visum, Region, Dauer.

## Anreichern

Ein Angebot auf einem Portal ist meist nur ein Anriss. Für jeden Treffer, der die Filter übersteht:
Website der Organisation / des Betriebs besuchen, konkrete Fakten ziehen (Größe, Ort, Unterkunft,
Sprache, Kontakt-E-Mail), Bilder sammeln. Ziel: Ich sitze nur noch vor der Karte und muss nicht
selbst weitersuchen.

## Kontakt-E-Mails

Für Treffer, die ich gut bewerte, wird automatisch ein **Entwurf** einer Anfrage-Mail erstellt
(Englisch, auf den Betrieb zugeschnitten): Interesse, Zeitraum, keine Bezahlung nötig – Unterkunft
reicht, technischer Hintergrund als Tauschwert. **Versendet wird nie automatisch** – ich prüfe und
schicke selbst.

## Festgelegt

- Läuft **lokal** auf meinem Rechner.
- **Kosten sichtbar machen:** Jede Gebühr wird auf der Karte deutlich markiert; Obergrenze 500 €.
- **Keine Login-/Bezahlplattformen** (Workaway, WWOOF, …) vorerst.
- Erst ein **gründlicher Einmal-Durchlauf**, später regelmäßige Aktualisierung.
- Ausschreibungen und Leads sind **getrennte Sparten**.

## Bewusst (noch) nicht festgelegt

Technologie, LLM-Anbindung, Scraping-Werkzeuge – nach der Quellen-Recherche (`docs/recherche/`).
