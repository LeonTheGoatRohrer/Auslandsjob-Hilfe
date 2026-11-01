# Recherche: Maritime, Naturschutz-, Expeditions- und Forschungsstations-Quellen

Stand: 2026-10-28 · Bereich: Kampagnen- und Forschungsschiffe, Tall Ships, Crew-Börsen, Werften, Meeresschutz, Feldassistenz-Jobbörsen, Insel- und Forschungsstationen, Wiederaufforstung, Expeditionen.
Nicht abgedeckt (andere Sessions): allgemeine Plattformen (Workaway, Worldpackers, EU-Programme), unausgeschriebene Handwerksbetriebe, Visa.

## Wie verlässlich diese Datei ist

Die Recherche wurde früh abgebrochen (Websuche durch einen Hook blockiert, dann Auftrag „jetzt schreiben“). Darum gilt:

- **✔ geprüft (2026-10-28):** direkt abgerufen. Das sind nur **Conservation Job Board** (Startseite + robots.txt), **Texas A&M Job Board** (Startseite, /search/ antwortet mit HTTP 200, kein robots.txt), die robots.txt von **Crewseekers, FindACrew, Ornithology Exchange, Sail Training International, Workaway**. Die Volunteer-Seite von Sea Shepherd Global unter `/get-involved/volunteer/` liefert 404 (URL hat sich geändert) und robots.txt ebenfalls 404.
- **UNSICHER:** alles andere stammt aus Vorwissen (Stand bis 2025/26). Gebühren, Mindestdauer, Mindestalter und URLs müssen vor Verwendung nachgeprüft werden. Mengenangaben sind **Schätzungen in Größenordnungen**, keine Zählungen.

„Passend“ heißt in den Schätzungen: 6–12 Wochen, Start Ende April–Mitte Juni 2027, Gebühr ≤ 500 €, mit 18 ohne Studium/Tauchschein/STCW erreichbar, Englisch reicht.

## Kennzeichnung der Finanzierung

- **BEZAHLT**: Lohn oder Stipendium
- **FREI**: keine Gebühr, Unterkunft (und meist Essen) gegen Arbeit
- **KOSTENTEILUNG**: keine Gebühr, aber Bordkasse/Essen selbst (typisch 10–30 €/Tag auf Yachten)
- **GEBÜHR ≤ 500 €**: kleine Gebühr, im Rahmen, trotzdem markieren
- **⚠ VOLUNTOURISM / GEBÜHR > 500 €**: zahlender Anbieter, Gebühr wird genannt. Laut Profil faktisch Ausschluss.

---

## 1. Übersichtstabelle

Spalten: **Art** J = Jobbörse/Verzeichnis, O = einzelne Organisation · **Angebote ges.** = geschätzte Zahl offener Angebote bzw. pro Saison · **passend** = davon geschätzt fürs Profil passend · **Zugriff** = technischer Weg für das Tool.

### 1a. Jobbörsen und Verzeichnisse (für automatisches Sammeln relevant)

| Quelle | URL | Fokus / Region | Art | Dauer typ. | Finanzierung | Alter / Voraussetzungen | Angebote ges. | passend | Zugriff (Felder) | Passung |
|---|---|---|---|---|---|---|---|---|---|---|
| **Conservation Job Board** ✔ | conservationjobboard.com | Naturschutz, v. a. USA; Filter „International“ | J | Saisonstellen 2–6 Monate | gemischt: BEZAHLT, Paid Internship, „Unpaid“ | oft Studium/Erfahrung; Filter „0–1 Jahr Erfahrung“ vorhanden | ✔ ca. 450 offen (272 Permanent, 80 Temporary, 54 AmeriCorps, 25 Paid Internship, 6 Unpaid …); International ✔ ca. 11 | 0–5 pro Saison | HTML ohne Login; robots.txt erlaubt alles außer mailto, Sitemap `/sitemap.xml` ✔; kein RSS gefunden (`/feed` → 404) ✔. Felder ✔: Titel, Organisation, Ort/Region, Jobtyp, Gehalt (Freitext), Deadline (optional), Mindesterfahrung, relatives Postingalter | mittel: viel US-Inland, wenig International |
| **Texas A&M WFSC / Natural Resources Job Board** ✔ (Existenz) | jobs.rwfm.tamu.edu | Wildlife/Fisheries, USA + international, viele Field-Tech- und Volunteer-Stellen | J | 1–6 Monate | gemischt, auch „Volunteer“ mit Unterkunft | Field Techs oft Studium; Volunteer-Stellen teils ohne | UNSICHER: ~1.000–1.500 offen, ~50–100 international | 5–20 pro Saison | HTML, `/search/` HTTP 200 ✔, kein robots.txt (404) ✔; RSS UNSICHER. Felder (UNSICHER): Titel, Agency, Ort, Gehalt, Start, Ende, Bewerbungsfrist, Tags | **hoch** als Sammelquelle für internationale Feldassistenz (Vogelberingung, Schildkröten, Primaten) |
| **Ornithology Exchange – Jobs** | ornithologyexchange.org/jobs | Vogel-Feldarbeit weltweit (Seevogel-Inseln, Beringungsstationen) | J | 1–4 Monate, Brutsaison Apr–Aug | BEZAHLT oder FREI, selten Gebühr | oft keine Vorkenntnisse für Volunteers | UNSICHER: ~100–200 offen | 5–15 | HTML (Invision-Forum), robots.txt erreichbar ✔; Forum-Software hat meist RSS pro Kategorie (UNSICHER) | **hoch**: Timing Brutsaison passt genau |
| **ECOLOG-L** (Ecological Society of America) | listserv.umd.edu/archives/ecolog-l.html | Ökologie-Jobs, Field Assistants weltweit | J (Mailingliste) | variabel | gemischt | variabel | UNSICHER: 20–50 Posts/Woche | 2–10 pro Saison | E-Mail-Abo; Web-Archiv HTML (LISTSERV) | mittel: unstrukturiert, LLM-Parsing nötig |
| **Society for Marine Mammalogy – Jobs** | marinemammalscience.org | Wal-/Delfinforschung | J | 1–6 Monate | gemischt, viele zahlende „Field Courses“ | oft Studium | UNSICHER: 20–50 | 0–3 | HTML | niedrig–mittel |
| **Sail Training International** | sailtraininginternational.org | Traditionssegler/Sail-Training weltweit, Tall Ships Races | J (Verzeichnis + Events) | Törns 1–4 Wochen | Trainees zahlen meist ⚠, Zuschüsse für 15–25-Jährige bei Tall Ships Races | 16–25 für Zuschüsse, keine Segelerfahrung nötig | UNSICHER: ~200 Schiffe im Verzeichnis | 0–3 (bezahlte/freie Crew-Plätze selten) | HTML (WordPress), robots.txt erlaubt alles außer /wp-admin/ ✔; WordPress → `/feed/` vermutlich vorhanden (UNSICHER) | mittel: gutes Schiffsverzeichnis für Direktanfragen |
| **Crewseekers** | crewseekers.net | Yacht-Crew weltweit, Überführungen | J | Tage bis Monate | KOSTENTEILUNG bis BEZAHLT (Überführungen); Crew-Mitgliedschaft kostet (UNSICHER ~£50–100/Jahr) | Anfänger möglich | UNSICHER: einige Hundert Skipper-Anzeigen | 10–30 | HTML, robots.txt ✔ vorhanden (Inhalt ohne Disallow-Zeilen am Anfang); Details hinter Mitgliedschaft (UNSICHER) | mittel: echtes Leben an Bord, aber Qualität/Seriosität schwankt |
| **FindACrew** | findacrew.net | Yacht- und Superyacht-Crew | J | Tage bis Monate | KOSTENTEILUNG bis BEZAHLT; Basis gratis, Premium kostet | Anfänger möglich | UNSICHER: 1.000+ Profile/Anzeigen | 10–40 | JS-lastig, Login für Kontakt (UNSICHER); robots.txt `User-agent: *` ✔ | mittel |
| **Crewbay** | crewbay.com | Yacht-Crew, gratis | J | variabel | KOSTENTEILUNG / FREI | Anfänger möglich | UNSICHER: Hunderte | 5–20 | HTML, Login für Kontakt (UNSICHER) | mittel |
| **Yotspot / YaCrew / Bluewater** (Superyacht) | yotspot.com, yacrew.com | Superyachten Mittelmeer (Sommersaison Mai–Sep) | J | Saison 3–6 Monate | BEZAHLT (gut), Kost+Logis an Bord | **STCW Basic Safety + ENG1** Pflicht (Kurs ca. 1.000 €, 1 Woche) | UNSICHER: Tausende | 0–5 (Saisonlänge zu lang, Service-Job) | JS + Login | niedrig–mittel: bezahlt, aber eher „Hotel auf See“ |
| **Vereniging Beroepschartervaart / Bruine Vloot** (NL) | UNSICHER | Niederländische Traditionssegler (Wattenmeer, IJsselmeer) | J/Verband | Saison Apr–Okt | BEZAHLT (Deckhand/„maat“), Kost+Logis | 18+, Niederländisch oft gewünscht | UNSICHER: Dutzende Schiffe | 2–10 | HTML / Vacaturebanken | mittel–hoch: echte bezahlte Arbeit auf Segelschiff, Saison passt; Sprache prüfen |

### 1b. Schiffe und maritime Organisationen

| Quelle | URL | Fokus / Region | Art | Dauer typ. | Finanzierung | Alter / Voraussetzungen | Angebote | passend | Zugriff | Passung |
|---|---|---|---|---|---|---|---|---|---|---|
| **Sea Shepherd Global** | seashepherdglobal.org (Volunteer-Seite verschoben, 404 ✔) | Kampagnenschiffe gegen illegale Fischerei, v. a. Westafrika, Mittelmeer, Pazifik | O | UNSICHER: meist ab 3 Monaten | FREI (Kost+Logis an Bord), Anreise selbst | 18+ (UNSICHER), Englisch; Deck, Maschine, Elektrik, Koch gesucht | ~8–10 Schiffe, Crew-Pool statt Einzelstellen | Bewerbung 1 (Pool) | Bewerbungsformular, keine Listings | **hoch**: Kern des Wunsches; Mindestdauer mit 6–12 Wochen klären |
| **Sea Shepherd Origins / nationale Sea-Shepherd-Ableger** (nach Spaltung 2022) | UNSICHER | wie oben | O | UNSICHER | FREI (UNSICHER) | UNSICHER | wenige | 0–1 | Formular | mittel–hoch, nachprüfen |
| **Greenpeace Schiffe** | greenpeace.org | Kampagnenschiffe | O | Verträge | BEZAHLT | Profi-Seeleute, **STCW** nötig | wenige | 0 | Karriereportal | niedrig: ohne Qualifikation nicht erreichbar |
| **Mercy Ships** | mercyships.org | Krankenhausschiff, Westafrika | O | 2 Wochen bis Jahre | ⚠ Crew zahlt eigene Kosten (UNSICHER, Größenordnung mehrere Hundert USD/Monat) | 18+; Deck/Maschine/IT-Rollen | Dutzende Rollen | 0–2 | Karriereportal (JS) | mittel: echte Arbeit, aber Gebühr; nicht Naturschutz |
| **Schmidt Ocean Institute** | schmidtocean.org | Forschungsschiff *Falkor (too)*, weltweit | O | Fahrten 2–5 Wochen | Studenten-Kojen gratis (UNSICHER) | i. d. R. Studierende | einige pro Jahr | 0–1 | HTML-Ausschreibungen | niedrig: Studium nötig |
| **NOAA Ship Volunteers / Teacher at Sea** | omao.noaa.gov | US-Forschungsschiffe | O | 1–4 Wochen | FREI | meist US-Bürger, Teacher at Sea nur Lehrkräfte | wenige | 0 | HTML | niedrig |
| **Deutsche Forschungsschiffe (GEOMAR, AWI)** | geomar.de, awi.de | Nord-/Ostsee, Polar | O | 2–6 Wochen | Hilfskraft-Kojen über Unis | Studierende | wenige | 0 | Uni-intern | niedrig |
| **Sail-Cargo: Tres Hombres / Fairtransport, Timbercoast (Avontuur), Grain de Sail** | fairtransport.eu, timbercoast.com | Frachtsegler Atlantik/Karibik | O | Etappen 2–8 Wochen | ⚠ Trainees zahlen (UNSICHER: grob 50–100 €/Tag); Werft-Refit-Volunteers teils FREI | 18+, keine Erfahrung nötig | wenige Kojen | 0–2 (Refit-Volunteering im Winter/Frühjahr) | HTML/Formular | mittel: einmalig, aber kostet; Werft-Refit gratis anfragen |
| **Bark Europa, Picton Castle, Statsraad Lehmkuhl, Alexander von Humboldt II** | barkeuropa.com u. a. | Tall Ships, Ozeanpassagen | O | 1–8 Wochen | ⚠ Voyage Crew zahlt (Europa: Tausende €); Stammcrew/Deckhands BEZAHLT oder FREI, aber mit Erfahrung | 18+ | wenige | 0–2 | HTML | mittel: Werftzeiten/Winterpflege als Volunteer anfragen |
| **Deutsche Traditionsschiffe (ehrenamtliche Crews, z. B. Thor Heyerdahl, Clipper DJS)** | UNSICHER | Ost-/Nordsee | O | Wochenenden bis Wochen | Vereinsbeitrag, sonst FREI | Vereinsmitgliedschaft | — | 0 | — | niedrig: kein Auslandsaufenthalt |
| **Tall Ships Races 2027** (STI) | sailtraininginternational.org | Regatta-Serie Europa, Sommer | Event | 1–4 Wochen pro Etappe | ⚠ Trainee-Gebühr, Zuschüsse für Jugendliche | 15–25 | einige Hundert Kojen | 0–3 bei Zuschuss | HTML | mittel: Route/Termine 2027 UNSICHER, prüfen |

### 1c. Meeresschutz (Schildkröten, Korallen, Haie, Mantas, Wale, Fischerei)

| Quelle | URL | Fokus / Region | Art | Dauer typ. | Finanzierung | Alter / Voraussetzungen | passend | Zugriff | Passung |
|---|---|---|---|---|---|---|---|---|---|
| **ARCHELON** | archelon.gr | Meeresschildkröten, Griechenland (Zakynthos, Kreta, Peloponnes) | O | min. 4 Wochen, Saison Mai–Okt | GEBÜHR ≤ 500 € (UNSICHER: einmalige Teilnahmegebühr ~250–350 €, Zelt-Camp, Essen selbst) | 18+, Englisch | 1 (Bewerbung) | Formular, HTML | **hoch**: Saisonbeginn Mai passt genau, echte Feldarbeit, günstig |
| **Wildlife Sense** | wildlifesense.com | Schildkröten, Kefalonia | O | 4+ Wochen | UNSICHER: Gebühr im mittleren dreistelligen Bereich | 18+ | 1 | Formular | mittel–hoch, Gebühr prüfen |
| **MEDASSET / DEKAMER / Schildkrötenprojekte Türkei, Zypern** | UNSICHER | Mittelmeer | O | 4–12 Wochen | gemischt | 18+ | 1–3 | Formular | mittel, nachprüfen |
| **Projekte auf Kap Verde (z. B. BIOS.CV, Project Biodiversity)** | UNSICHER | Schildkröten, Boa Vista/Sal | O | 1–3 Monate, Saison Jul–Okt | Volunteers teils Gebühr, Research Assistants BEZAHLT | UNSICHER | 0–2 | Ausschreibung oft auf Texas A&M Board | mittel: Saison beginnt eher Juli |
| **Sea Turtle Conservancy – Research Assistants Tortuguero** | conserveturtles.org | Costa Rica, Saison Mär–Okt | O | 3 Monate | BEZAHLT/Stipend (UNSICHER); Volunteer-Programm ⚠ zahlend | Research Assistants meist mit Studium | 0–1 | über Jobbörsen | mittel |
| **Coral Restoration Foundation** | coralrestoration.org | Korallen, Florida Keys | O | Internship ~3 Monate | FREI/unbezahlt, Unterkunft UNSICHER | Tauchschein (mind. Advanced) nötig, US-Visum (J-1?) UNSICHER | 0–1 | HTML | niedrig–mittel: Tauchschein + Visum |
| **Reef Renewal Bonaire** | reefrenewalbonaire.org | Korallen, Karibik (NL-Überseegebiet → EU-Bürger einfach) | O | Wochen | UNSICHER: Taucher-Volunteers zahlen Tauchkosten | Tauchschein | 0–1 | HTML | mittel |
| **Bimini Biological Field Station (Sharklab)** | biminisharklab.com | Haie, Bahamas | O | 4+ Wochen | ⚠ Volunteers zahlen (UNSICHER, Größenordnung ~1.000 USD/Monat) | 18+ | 0 | Formular | niedrig wegen Gebühr, sonst Traumprojekt |
| **Manta Trust / Marine Megafauna Foundation** | mantatrust.org, marinemegafauna.org | Mantas, Malediven / Mosambik | O | Internships | ⚠ Gebühr (UNSICHER, vierstellig) | Tauchschein | 0 | HTML | niedrig |
| **Tethys Research Institute** | tethys.org | Wale, Mittelmeer (Ligurisches Meer, Griechenland) | O | 1-Wochen-Fahrten | ⚠ Gebühr (UNSICHER, ~700–1.000 €/Woche) | 18+ | 0 | HTML | niedrig: echte Forschung, aber zahlend |
| **Fischereibeobachter (Observer-Programme)** | z. B. NOAA, AFMA, MRAG | Fischereischiffe weltweit | O | Einsätze Wochen–Monate | BEZAHLT, gut | Studium Biologie o. ä., Training | 0 | Karriereportale | niedrig: mit 18 nicht erreichbar |

**Zahlende Voluntourism-Anbieter im Meeresbereich – ausdrücklich ⚠ und abzuwerten** (Gebühren aus Vorwissen, UNSICHER, Größenordnung pro 4 Wochen):
GVI (~2.000–4.000 €), Frontier (~1.500–3.000 €), Projects Abroad (~2.500–4.000 €), Blue Ventures (~2.500–3.500 €), Operation Wallacea (~2.000–4.000 € + Flug), Biosphere Expeditions (~2.000 € pro 1–2 Wochen), Earthwatch (~2.000–4.000 € pro 1–2 Wochen), Marine Conservation Cambodia (~1.000–1.500 €/Monat), Coral Gardeners (Programm zahlend), Cape Eleuthera Institute (zahlend), Global Vision International und ähnliche.
→ Diese im Tool nur als Kategorie „⚠ zahlender Anbieter“ führen, Gebühr prominent anzeigen.

### 1d. Vogelwarten, Inselstationen, Nationalparks (Feldarbeit an Land)

| Quelle | URL | Fokus / Region | Art | Dauer typ. | Finanzierung | Alter / Voraussetzungen | passend | Zugriff | Passung |
|---|---|---|---|---|---|---|---|---|---|
| **Verein Jordsand – Vogelwärter/Inselbetreuung** | jordsand.de | Vogelschutzinseln Nord-/Ostsee (z. B. Scharhörn, Neuwerk, Greifswalder Oie) | O | UNSICHER: meist 3–6 Monate, teils kürzer | FREI (Unterkunft auf der Insel), Taschengeld bei BFD/FÖJ | 18+ | 1–2 | HTML, Bewerbung | **hoch**: allein/zu zweit auf einer Insel leben; Mindestdauer klären; aber Deutschland, kein Ausland |
| **Mellumrat** | mellumrat.de | Vogelwärter auf Mellum, Minsener Oog, Wangerooge-Ost | O | UNSICHER: Saison Mär–Okt, Abschnitte von Wochen | FREI + evtl. Verpflegungsgeld | 18+ | 1–2 | HTML | **hoch** (wie oben, Deutschland) |
| **Schutzstation Wattenmeer** | schutzstation-wattenmeer.de | Wattenmeer, Halligen | O | Praktikum 2–3 Monate (UNSICHER), sonst FÖJ/BFD 12 Monate | FREI (Unterkunft) | 18+ | 1 | HTML | mittel–hoch (Deutschland) |
| **UK Bird Observatories (Fair Isle, North Ronaldsay, Skokholm, Bardsey u. a.)** | birdobscouncil.org.uk | Schottland/Wales, abgelegene Inseln | O (Verzeichnis + Einzel) | Saison Apr–Okt, Volunteers 2–8 Wochen | FREI (Unterkunft), Assistant Wardens BEZAHLT | 18+, Beringung lernbar; UK-Visum für Volunteers seit Brexit prüfen (Visa-Session) | 2–6 | HTML je Station | **hoch**: abgelegene Inseln, Brutsaison passt |
| **RSPB Residential Volunteering** | rspb.org.uk | UK-Reservate inkl. Inseln | O | 2–12+ Wochen | FREI (Unterkunft) | 18+ (UNSICHER) | 2–5 | HTML, Volunteer-Portal (JS?) | hoch, Visa-Frage UK |
| **Skandinavische Beringungsstationen (Ottenby, Falsterbo, Jomfruland u. a.)** | z. B. ottenby.se | Schweden/Norwegen | O | Frühjahrs-/Herbstzug | FREI (UNSICHER) | Beringungserfahrung oft gewünscht | 1–3 | HTML, oft nur Landessprache | mittel–hoch: Zugzeit Mai passt, Herbst besser |
| **Churchill Northern Studies Centre** | churchillscience.ca | Subarktis, Kanada (Eisbären-Gebiet) | O | UNSICHER: Wochen bis Monate | FREI (Kost+Logis gegen Arbeit, UNSICHER) | 18+ | 1 | HTML | **hoch**: abgelegene Station, praktische Arbeit; Kanada-WHV oder eTA prüfen |
| **Arktis-Feldassistenz (Zackenberg/Grönland, Svalbard, Alaska Maritime NWR Seevogelinseln)** | via Texas A&M / Ornithology Exchange | Arktischer Sommer Mai–Aug | J/O | 6–12 Wochen | BEZAHLT oder FREI | oft Erfahrung, US-Stellen Visum-Problem | 1–5 | über Jobbörsen | **hoch** wenn erreichbar: Saison passt perfekt zum Zeitraum |
| **NZ Department of Conservation – Volunteers** | doc.govt.nz | Neuseeland, Inseln, Hütten | O | Tage bis Wochen (UNSICHER) | FREI | Working Holiday Visa möglich | 1–3 | HTML, Volunteer-Liste | mittel: oft kurz; Mai = NZ-Herbst |
| **Galápagos: Charles Darwin Foundation** | darwinfoundation.org | Galápagos | O | UNSICHER: eher 6 Monate | UNSICHER | oft Studium | 0–1 | HTML | niedrig–mittel |
| **Seychellen: Island Conservation Society, Nature Seychelles, Cousine Island, Save Our Seas D'Arros** | UNSICHER | Inselstationen Indischer Ozean | O | 1–6 Monate | gemischt: teils ⚠ Gebühr (Nature Seychelles), Research Assistants teils BEZAHLT | oft Studium/Tauchschein | 0–2 | HTML | mittel, Einzelprüfung nötig |
| **Falklands Conservation, Ascension/St Helena** | falklandsconservation.com | Südatlantik | O | Südsommer (Okt–Mär) | gemischt | — | 0 | HTML | niedrig: Saison passt nicht |

### 1e. Tropische Forschungsstationen, Wiederaufforstung, Expeditionen

| Quelle | URL | Fokus / Region | Art | Dauer | Finanzierung | Voraussetzungen | passend | Zugriff | Passung |
|---|---|---|---|---|---|---|---|---|---|
| **Cocha Cashu Biological Station** | cochacashu.sandiegozooglobal.org (UNSICHER) | Amazonas, Peru | O | 2–3 Monate | UNSICHER (früher FREI für Field Assistants) | Englisch/Spanisch | 0–1 | HTML | hoch, falls weiterhin gratis |
| **Conservación Amazónica – Los Amigos / Wayqecha** | UNSICHER | Peru | O | 1–3 Monate | UNSICHER, teils Gebühr | — | 0–1 | HTML | mittel |
| **Danau Girang Field Centre** | dgfc.org (UNSICHER) | Borneo, Malaysia | O | 1–3 Monate | UNSICHER, vermutlich Gebühr | — | 0–1 | HTML | mittel |
| **Centre ValBio** | centrevalbio.org | Madagaskar | O | variabel | UNSICHER | oft Studium | 0–1 | HTML | mittel |
| **OTS La Selva / Smithsonian STRI** | tropicalstudies.org, stri.si.edu | Costa Rica / Panama | O | Monate | Research Assistants BEZAHLT | Studium | 0 | HTML / über Jobbörsen | niedrig |
| **Trees for Life (Schottland)** | treesforlife.org.uk | Wiederaufforstung | O | Volunteer-Wochen | ⚠ Gebühr pro Woche (UNSICHER) | 18+ | 0 | HTML | niedrig |
| **Wiederaufforstung allgemein** | — | — | — | — | meist über Workaway/Worldpackers (andere Session) | — | — | — | Hinweis: echte Aufforstungs-NGOs nehmen selten Kurzzeit-Volunteers gratis; viel Voluntourism |
| **Expeditionen: British Exploring Society, Raleigh International, Scientific Exploration Society** | britishexploring.org u. a. | weltweit | O | 3–6 Wochen | ⚠ Gebühr (vierstellig) | 16–25 | 0 | HTML | niedrig wegen Gebühr |

---

## 2. Notizen

1. **Die besten echten Angebote stehen fast nie auf großen Plattformen.** Sea Shepherd, Vogelinseln, Beringungsstationen, Forschungsstationen nehmen Bewerbungen über eigene Formulare an. Für das Tool heißt das: diese Organisationen als **feste „Direktbewerbungs-Karten“** anlegen (jährlich prüfen), nicht scrapen.
2. **Automatisch sammelbar sind im Wesentlichen vier Quellen:** Texas A&M Job Board, Conservation Job Board (beide HTML, ohne Login; CJB mit Sitemap), Ornithology Exchange (Forum, evtl. RSS) und ECOLOG-L (Mail/Archiv). Crew-Börsen sind hinter Login bzw. JS und rechtlich heikler (AGB vor Scraping prüfen).
3. **Saison passt hervorragend für die Nordhalbkugel:** Seevogel-Brutsaison (Mai–Aug), Schildkröten im Mittelmeer (Mai–Okt), Arktis-Feldsaison (Jun–Aug), Traditionssegler-Saison (Apr–Okt). Südhalbkugel-Projekte (Antarktis, Falklands, NZ-Sommer) passen schlecht.
4. **Größte Hürden:** (a) Mindestdauer – viele freie Volunteer-Stellen wollen 3–6 Monate; 6–12 Wochen aktiv anfragen. (b) Studium – Feld-Assistenzstellen verlangen oft „Bachelor oder Studium“; die ESP32-/Datenlogger-Fähigkeit ist hier ein echtes Argument. (c) Visa für USA/UK/Kanada → Visa-Session. (d) Qualifikationen: Tauchschein (Korallen/Mantas), STCW Basic Safety (bezahlte Yachtjobs). STCW (~1 Woche, ~1.000 €) wäre die eine Investition, die viele maritime Türen öffnet.
5. **Voluntourism-Erkennung fürs LLM:** Signalwörter „programme fee“, „contribution“, „includes airport pickup“, „weekly fee“, „adventure“, „make a difference“; starre Starttermine jeden Montag; keine Anforderungen außer Bezahlung. Gegenmerkmale echter Mitarbeit: Bewerbungsfrist, Anforderungen/Erfahrung, Stipendium/Lohn, „field technician/assistant“.
6. **Kostenteilung auf Yachten** (Bordkasse) ist keine Programmgebühr, sollte aber als eigene Kategorie markiert werden (6 Wochen × 20 €/Tag ≈ 840 € → überschreitet die 500-€-Grenze rechnerisch).

---

## 3. Mengenschätzung: maximal erreichbare passende Angebote (Saison Mai–Juli 2027)

Alle Zahlen UNSICHER und grob; „passend“ = Zeitraum, Dauer, Gebühr ≤ 500 €, ohne Studium machbar.

| Quellengruppe | passend (grob) |
|---|---|
| Texas A&M Job Board | 5–20 |
| Ornithology Exchange | 5–15 |
| Conservation Job Board | 0–5 |
| ECOLOG-L + Marine-Mammal-Board | 2–13 |
| Crew-Börsen Yachten (Crewseekers, FindACrew, Crewbay) – meist Kostenteilung | 25–90 |
| Traditionssegler-Deckhand (NL/Skandinavien), Sail-Cargo-Refit | 2–12 |
| Einzelorganisationen Schiffe (Sea Shepherd u. a.) | 1–4 |
| Meeresschutz-Einzelorganisationen (ARCHELON u. a.) | 3–8 |
| Vogelwarten/Inseln/Stationen (Jordsand, Mellumrat, UK-Observatorien, RSPB, Skandinavien, Churchill, Arktis) | 8–25 |
| Tropische Stationen | 0–4 |
| **Summe „maximal erreichbar“** | **ca. 50–195**, davon **ca. 25–100 ohne Yacht-Kostenteilung**; wirklich starke Treffer (Schiff/Insel/Station, gratis, Saison passt) realistisch **15–40** |

---

## 4. Priorisierte Top-10 (Quellen)

1. **Sea Shepherd Global (Crew-Bewerbung)** – genau die Wunscherfahrung, gratis an Bord; einzige Unsicherheit ist die Mindestdauer. Früh (Ende 2026) bewerben, Elektronik-/Maschinenraumhilfe anbieten.
2. **Texas A&M Natural Resources Job Board** – größte maschinell lesbare Quelle für internationale Feldassistenz, viele unbezahlte Stellen mit Unterkunft; erster Scraper-Kandidat.
3. **Ornithology Exchange Jobs** – Seevogel-Inseln und Beringungsstationen, Timing passt zur Brutsaison, oft ohne Vorkenntnisse.
4. **UK Bird Observatories (Fair Isle, North Ronaldsay, Skokholm …)** – abgelegene Inseln, gratis Unterkunft, echte Datenerhebung; Visa nachprüfen.
5. **ARCHELON** – Saisonstart Mai, 4+ Wochen, kleine Gebühr im Rahmen, echte Feldarbeit mit Schildkröten.
6. **Churchill Northern Studies Centre** – subarktische Forschungsstation, Kost/Logis gegen Arbeit, Technik gut einsetzbar.
7. **Arktis-Feldassistenz (über Jobbörsen)** – Saison deckt Mai–August ab, extrem außergewöhnlich; schwer, aber lohnt den Filter.
8. **Niederländische/skandinavische Traditionssegler als Deckhand** – bezahlte echte Arbeit auf Segelschiff, Saison passt; Sprache und Ausschreibungsquellen nachprüfen.
9. **Crew-Börsen (Crewseekers, Crewbay, FindACrew)** – Ozean-Überführung (z. B. Atlantik Mai/Juni Karibik→Europa) bedeutet Wochen auf See; Kostenteilung markieren, Seriosität prüfen.
10. **Verein Jordsand / Mellumrat** – Leben auf einer Vogelinsel, gratis; Abzug, weil Deutschland statt Ausland und evtl. längere Mindestdauer. Gute Rückfalloption.

---

## 5. Konkrete Organisationen, die besonders gut passen (Direktanfrage)

| Organisation | Warum | Was klären |
|---|---|---|
| Sea Shepherd Global | Schiff + Mission + gratis | Mindestdauer 6–12 Wochen akzeptiert? Aktuelle Bewerbungs-URL |
| ARCHELON (Griechenland) | Saison Mai, günstig, echte Feldarbeit | aktuelle Gebühr, Mindestdauer |
| Fair Isle Bird Observatory (Shetland) | entlegenste bewohnte Insel UK, Volunteers/Assistants | UK-Visum für Volunteers |
| North Ronaldsay Bird Observatory (Orkney) | Inselstation, Volunteers gratis | Visum, Dauer |
| Skokholm Island (Wales, Wildlife Trust of South and West Wales) | Seevogelinsel, Langzeit-Volunteers | Visum, Dauer |
| Churchill Northern Studies Centre (Kanada) | subarktische Station, Arbeit gegen Kost/Logis | aktuelles Volunteer-Programm |
| Verein Jordsand (Scharhörn, Neuwerk u. a.) | Vogelwärter auf Insel | Mindestdauer |
| Mellumrat (Mellum, Minsener Oog) | Vogelwärter auf unbewohnter Insel | Saisonabschnitte |
| Tres Hombres / Fairtransport (NL) | Frachtsegler; Werft-Refit gratis anfragen | ob Refit-Volunteers Frühjahr 2027 gesucht |
| Timbercoast / Avontuur | Frachtsegler, Werftarbeit | wie oben |
| Cocha Cashu Biological Station (Peru) | Amazonas-Station, Field Assistants | ob noch gebührenfrei |
| Coral Restoration Foundation (USA) | Korallen + Technik | Tauchschein, J-1-Visum → eher später |

Hinweis für die Technik-Ecke: Bei Stationen und Inseln das Angebot „ich baue/repariere Datenlogger, Wetterstation, Wildkamera-Netz, Nestwaagen mit ESP32“ aktiv in der Bewerbung nennen – das ist bei kleinen Teams ein echter Tauschwert.
