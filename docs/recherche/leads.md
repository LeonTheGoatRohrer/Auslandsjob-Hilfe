# Recherche: Leads – kleine Betriebe ohne Ausschreibung finden

> Stand: 28.10.2026. Grundlage: [`config/profil.yaml`](../../config/profil.yaml), [`01-kriterien.md`](../01-kriterien.md).
> „Geprüft“ heißt hier: Seite bzw. API am 28.10.2026 selbst abgerufen. Alles mit *(ungeprüft)* stammt aus Vorwissen
> und muss vor dem Einbau verifiziert werden.

## Kurzfazit

1. **Es gibt keine eine Lead-Datenbank.** Gute Leads entstehen aus drei Schichten: (a) *kuratierte Verzeichnisse*
   (Verbände, Fartøyvern, Heritage Crafts, 伝統的工芸品-Produktionsgebiete) liefern wenige, aber sehr passende Betriebe;
   (b) *offene Geodaten* (OSM, Overture) liefern die Breite; (c) *Anreicherung* (Website-Crawl + LLM) macht daraus Karten.
2. **OpenStreetMap allein reicht nicht**, besonders nicht in Japan: nur 5 Bootsbauer in ganz Japan getaggt, nur ~9 %
   der Handwerks-Einträge haben eine Website, 0,4 % eine E-Mail (siehe Messung unten).
3. **Overture Maps Places** ist die beste kostenlose Massenquelle (≈ 88 Mio. Orte, Felder `websites`, `emails`,
   `phones`, `socials`, offene Lizenz, monatlich). **Google Places** nur gezielt zur Anreicherung – Website-Feld
   kostet Enterprise-Tarif, E-Mail liefert Google gar nicht.
4. **Skandinavien (v. a. Norwegen/Dänemark) ist für den Nutzer am realistischsten**: EWR → kein Visum, kein
   Arbeitsrechtproblem, Englisch fast überall, und es gibt staatlich geförderte Holzboot-Werkstätten
   (Fartøyvernsentre) und Lehrbetriebe.
5. **Japan ist das Wunschziel, aber die Englisch-Hürde ist real.** Ein direkter Kaltkontakt per englischer Mail an
   einen Familienbetrieb ohne englische Website wird meist unbeantwortet bleiben. Erfolgversprechender: Mittler
   (Gemeinde-CIR, Präfektur-Handwerksstellen, Douglas Brooks für Holzbootbau), Programme mit englischer
   Betreuung (Toma House, AIR_J) und Betriebe, die selbst schon englische Inhalte haben – plus Mail **zweisprachig
   (Japanisch + Englisch)**, vom LLM vorformuliert und vom Nutzer geprüft.

---

## Messung: OpenStreetMap / Overpass (selbst abgefragt)

Abfrage über `https://overpass-api.de/api/interpreter` (Ländergebiet per `ISO3166-1`, alle Objekttypen, nur `out tags`):

```overpassql
[out:json][timeout:180];
area["ISO3166-1"="JP"][admin_level=2]->.a;
nwr["craft"~"^(boatbuilder|blacksmith|carpenter|joiner|cabinet_maker|pottery|glassblower|luthier|musical_instrument|sailmaker|shipwright|metal_construction|woodcarver|basket_maker)$"](area.a);
out tags;
```

Für einzelne Regionen besser per Bounding Box oder Präfektur-/Fylke-Relation (`area["name:en"="Okinawa Prefecture"]`)
und `out center tags;` (liefert Koordinaten auch für Flächen).

| Land | Treffer gesamt | mit Website | mit E-Mail | Verteilung (Auszug) |
|---|---|---|---|---|
| Japan | 2 472 | 214 (9 %) | 9 (0,4 %) | carpenter 1 928 (fast nur 大工/Bauunternehmen), metal_construction 259, pottery 205, blacksmith 26, boatbuilder **5**, glassblower 5, musical_instrument 7 |
| Norwegen | 97 | 39 (40 %) | 13 (13 %) | carpenter 38, metal_construction 12, blacksmith 10, pottery 10, boatbuilder 8, sailmaker 6, glassblower 3 |

Reine Zählung (`out count;`) nur für die „engen“ Handwerke (boatbuilder, blacksmith, pottery, glassblower, luthier,
musical_instrument, sailmaker, shipwright – also ohne carpenter/joiner/metal_construction):

| Land | Treffer (enge Handwerke) |
|---|---|
| Japan | 250 |
| Neuseeland | 95 |
| Dänemark | 93 |
| Norwegen | 43 |

Australien, Großbritannien, Schweden, Island, Finnland konnten nicht gezählt werden: der öffentliche Overpass-Server
antwortete wiederholt mit **502 / 429 (Rate-Limit)** bzw. Timeout. Für das Tool heißt das: Abfragen klein halten (Region statt
ganzes Land), Pausen ≥ 60 s, `User-Agent` setzen, Ergebnisse cachen – oder für den Einmal-Durchlauf gleich einen
**Geofabrik-Länderextrakt** (`.osm.pbf`) lokal mit `osmium tags-filter` / `pyosmium` auswerten (kein Rate-Limit).

Erkenntnisse aus den Daten:

- `craft=carpenter` ist in Japan unbrauchbar (Bauhandwerk) → nur `boatbuilder`, `blacksmith`, `pottery`,
  `glassblower`, `luthier`, `musical_instrument`, `basket_maker` verwenden; dazu `shop=knives`, `tourism=attraction`
  + `craft` und Namens-Regex (`造船|船大工|鍛冶|窯|工房`) ergänzen.
- Japanische Handwerks-POIs ballen sich auf **Okinawa** (Yachimun-Töpfereien, Ryukyu-Glas) – dort hat ein lokaler
  Mapper systematisch erfasst. Das ist ein Datenartefakt, kein Abbild der Realität.
- Brauchbar sind die Treffer trotzdem als **Ausgangsliste**: z. B. 名栗カヌー工房 (Holzkanu-Werkstatt, Saitama),
  タケフナイフビレッジ (Messerschmiede-Kooperative, Fukui), Risør Trebåtbyggeri (Norwegen) kamen direkt aus OSM.
- Größenordnung realistisch: **pro Land einige Dutzend bis wenige Hundert relevante Roh-Leads**, nach Filter
  (Website vorhanden, passendes Handwerk, abseits Großstadt) eher 10–50.

---

## Quellen-Tabelle

Passung: ★★★ = liefert direkt sehr passende Betriebe, ★★ = gute Breite / Zusatzquelle, ★ = nur ergänzend.

### Offene Daten & APIs

| Name | URL | Region | Handwerk | Zugriff technisch | Datenfelder | Kosten | Passung |
|---|---|---|---|---|---|---|---|
| OpenStreetMap via Overpass | https://overpass-turbo.eu (Test), API `overpass-api.de/api/interpreter` | weltweit | alle `craft=*` (Liste: https://taginfo.openstreetmap.org/keys/craft) | HTTP-POST, JSON; Rate-Limit (selbst erlebt: 502/429) | Name, Koordinaten, `website`, `email`, `phone`, `opening_hours`, teils `name:en` | frei, ODbL (Quellenangabe) | ★★ |
| OSM-Länderextrakte (Geofabrik) | https://download.geofabrik.de *(ungeprüft)* | weltweit | wie oben | `.osm.pbf` herunterladen, lokal filtern (osmium/pyosmium) | wie oben | frei | ★★ (für Einmal-Durchlauf besser als Overpass) |
| Overture Maps Places | https://docs.overturemaps.org/guides/places/ | weltweit, ≈ 88 Mio. Orte | über `taxonomy`/`basic_category` (seit 09/2026, ersetzt `categories`) | GeoParquet auf S3/Azure, direkt mit DuckDB per Bounding Box; Python-CLI `overturemaps` | Namen, Adresse, `websites`, `emails`, `phones`, `socials`, `confidence` | frei (CDLA Permissive 2.0 / Apache 2.0), monatliche Releases | ★★★ (beste Massenquelle; Vollständigkeit laut Doku „niedrig“) |
| Foursquare OS Places | https://opensource.foursquare.com/os-places/ | weltweit, 100 Mio.+ POIs | 1 000+ Kategorien | Download (places.foursquare.com); Lizenz auf Seite nicht genannt – vor Nutzung prüfen *(früher Apache 2.0, ungeprüft)* | Name, Kategorie, Adresse, Website/Telefon *(Schema ungeprüft)* | frei | ★★ (Abgleich/Ergänzung zu Overture) |
| Google Places API (New) | https://developers.google.com/maps/billing-and-pricing/pricing | weltweit, beste Abdeckung Japan | Freitextsuche („boat builder“, „船大工“) | REST, API-Key + Billing-Konto | Text Search Pro: Name, Adresse, Typ; **`websiteUri`/Telefon nur Enterprise-SKU**; keine E-Mail | Text Search Pro 5 000/Monat frei, dann 32 $/1 000; Text Search/Place Details Enterprise 1 000/Monat frei, dann 35 $ bzw. 20 $/1 000; IDs-only gratis. AGB: Inhalte (außer `place_id`) nicht dauerhaft speichern *(Cache-Regel ungeprüft)* | ★★ (gezielt zum Verifizieren/Anreichern der Top-Leads, nicht als Massenquelle) |

### Japan

| Name | URL | Region | Handwerk | Zugriff technisch | Datenfelder | Kosten | Passung |
|---|---|---|---|---|---|---|---|
| 伝統的工芸品 (METI-Liste, rund 240 Handwerke) / 伝統的工芸品産業振興協会 | https://kougeihin.jp, https://kyokai.kougeihin.jp | ganz Japan | alle traditionellen Handwerke | HTML, Japanisch (beim Test 503 – Server instabil) | Handwerk, Produktionsgebiet, 産地組合 | frei | ★★★ als **Landkarte**: welches Handwerk wo; Kontakt dann über das 産地組合 |
| Präfektur-Seiten zu 伝統的工芸品 / 産地組合 | z. B. https://www.pref.niigata.lg.jp/sec/shogyoshinko/1293144423860.html, https://www.pref.nagano.lg.jp/mono/sangyo/shokogyo/seikatsu/kogehin.html, https://www.pref.toyama.jp/documents/45540/kyogikaimeibo.pdf | je Präfektur | regionale Handwerke | HTML/PDF, Japanisch, je Präfektur anders | Handwerk, Ort, Verband, teils Tel./Adresse | frei | ★★★ (Verbände vermitteln Betriebe; Japanisch nötig) |
| ニッポン手仕事図鑑 – 伝統工芸インターン | https://nippon-teshigoto.jp/news_event/intern-list | ganz Japan | Keramik, Bambus, Färberei u. a. | HTML, Japanisch; Formular je Programm | Programm, Betrieb, Zeitraum | frei | ★★ (echte Nachwuchs-Praktika bei Betrieben; zielt auf japanische Kunststudierende, kein Englisch) |
| AIR_J (Residency-Datenbank Japan) | https://air-j.info/en/ | ganz Japan | Kunst/Handwerk (z. B. Shigaraki-Keramik, Sado-Island-Residency) | HTML, **Englisch** | Programm, Ort, Bewerbungszeitraum | frei; Programme teils kostenpflichtig | ★★ |
| Toma House AIR (Kintsugi, Hyōgu) | https://tomaunrestored.com/artistresidency/ | Nara | Urushi/Kintsugi, Rollbildmontage | Bewerbung, **Englisch** | 4 Wochen; Unterkunft, Lehrer, Werkzeug gestellt; Reise, Essen selbst | keine Programmgebühr genannt | ★★ (Kurs-Charakter, 4 statt 6–8 Wochen) |
| WWOOF Japan | https://www.wwoofjapan.com | ganz Japan | Höfe, teils Handwerker-Hosts | Login + Mitgliedsgebühr | Host-Profile | Gebühr | ★ (laut Konzept vorerst ausgeschlossen; manuell als Fundgrube für Handwerker-Hosts nutzbar) |
| 地域おこし協力隊 | – | ländliches Japan | Regionalentwicklung | – | – | – | ✗ (setzt Wohnsitz in Japan und mehrjährige Verpflichtung voraus – nicht machbar) |

### Skandinavien & europäische Inseln

| Name | URL | Region | Handwerk | Zugriff technisch | Datenfelder | Kosten | Passung |
|---|---|---|---|---|---|---|---|
| Norwegische Fartøyvernsentre (Riksantikvaren-Netz; Hardanger, Bredalsholmen, Nordnorsk i Gratangen) | https://fartoyvern.no, https://www.bredalsholmen.no | Norwegen | Holzboote, Takelage, Schmiede | einzelne Websites, Norwegisch, teils Englisch | Werkstätten, Stellen („Ledige stillingar“), Kontakt | frei | ★★★ |
| Skibsbevaringsfonden | https://skibsbevaringsfonden.dk | Dänemark | geschützte Holzschiffe, deren Eigner und Werften | HTML, Dänisch | Schiffsregister, Werften *(Feldumfang ungeprüft)* | frei | ★★★ (führt zu kleinen Holzwerften, z. B. Svendborg) |
| Lokale Handwerkervereine / Lehrbetriebslisten (z. B. Håndverkerforeningen i Trondheim) | https://handverk.no/medlemmer/ | Norwegen | ~20 Gewerke | HTML | Mitgliedsbetriebe | frei | ★ |
| „Godkjent lærebedrift“-Kennzeichnung | – (auf Betriebs-Websites, z. B. Risør Trebåtbyggeri) | Norwegen | alle | Textsuche beim Website-Crawl | Signal: Betrieb bildet aus | – | ★★ als **Bewertungssignal** |

### UK, Australien, Neuseeland

| Name | URL | Region | Handwerk | Zugriff technisch | Datenfelder | Kosten | Passung |
|---|---|---|---|---|---|---|---|
| Heritage Crafts Association – Makers Directory, Red List, matchMAKER | https://heritagecrafts.org.uk/makers/craft-directory/, https://heritagecrafts.org.uk/skills/redlist/, https://heritagecrafts.org.uk/matchmaker/ | UK | bedrohte Handwerke, filterbar nach Material | HTML | Maker-Profil mit Link zur eigenen Website | frei | ★★ (Visum UK für Mitarbeit schwierig – siehe Visa-Recherche) |
| British Artist Blacksmiths Association | https://www.baba.org.uk | UK | Schmiede | HTML *(Mitgliederliste ungeprüft)* | Mitglieder | frei | ★ |
| ABANA (Artist-Blacksmith's Association of North America) | https://abana.org | USA/Kanada, Affiliates | Schmiede | HTML | Affiliate-Gruppen | frei | ★ |
| National Historic Ships UK | https://www.nationalhistoricships.org.uk | UK | historische Schiffe, Werften | HTML *(Skills-/Werftverzeichnis ungeprüft)* | Register | frei | ★ |
| Wooden Boat Centre Tasmania | https://www.woodenboatcentre.com | Franklin, TAS | Holzbootbau | HTML | Kurse, Restaurierung, Volunteer-Seite | Kurse kostenpflichtig | ★★ (als Knotenpunkt der tasmanischen Holzboot-Szene) |
| NZ Traditional Boat Building School / Classic Yacht Association | https://nztbs.org.nz, https://classicyacht.org.nz | Auckland | Holzboote | HTML | Kurse, Volunteers, Kontakte | frei (Kurse gegen Gebühr) | ★★ |
| Sydney Heritage Fleet | https://www.shf.org.au | Sydney | Schiffsrestaurierung, Shipwright-Werkstatt | HTML | Volunteering | frei | ★ (Stadt, Volunteer-lastig) |

### Mittler (keine Datenbank, aber Türöffner)

| Name | URL | Region | Wofür | Passung |
|---|---|---|---|---|
| Douglas Brooks (US-Bootsbauer, Lehrling bei ~9 japanischen Meistern, Bücher zum japanischen Holzbootbau) | https://www.douglasbrooksboatbuilding.com | Japan (Sado, Gifu, Himi, Kuma-Fluss, Biwa-See) | kennt die letzten traditionellen 船大工 persönlich; eine höfliche Anfrage, ob er einen Kontakt empfehlen kann | ★★★ |
| Coordinators for International Relations (CIR, JET-Programm) in Präfektur- und Gemeindeämtern | https://jetprogramme.org (beim Test Wartungsseite) | Japan | sprechen Englisch, kennen lokale Betriebe, übersetzen/vermitteln | ★★★ |
| Lokale 観光協会 (Tourismusverbände) und 商工会 (Handels-/Gewerbekammern) | je Gemeinde | Japan | listen Werkstätten mit 体験 (Schnupperangebot) = Betriebe, die Besucher gewohnt sind | ★★ |

---

## Kontaktdaten, Größe und Englisch – wie man rankommt

| Feld | Woher | Bemerkung |
|---|---|---|
| **Website** | OSM `website`/`contact:website`, Overture `websites`, Google `websiteUri` (Enterprise) | Japan: viele Betriebe nur mit Instagram/Facebook – `socials` aus Overture mitnehmen |
| **E-Mail** | 1) OSM/Overture `email(s)`; 2) Website-Crawl: `mailto:`-Links, Seiten `/contact`, `/お問い合わせ`, `/kontakt`, `/om-oss`; 3) Impressum/特定商取引法に基づく表記 (Pflichtangabe bei Online-Shops in Japan, enthält meist E-Mail) | Viele japanische Betriebe haben **nur ein Kontaktformular** → Karte markiert „nur Formular“, Entwurf zum Einfügen ins Formular. Keine kostenpflichtigen E-Mail-Finder (Hunter u. ä.) nötig. |
| **Größe** | LLM liest „Über uns“/会社概要 (従業員数 = Mitarbeiterzahl), Fotos, Gründungsjahr; Norwegen/Dänemark: öffentliche Firmenregister (Brønnøysund, CVR) *(ungeprüft)* | Signal „Familienbetrieb / 1–10 Personen“ ist gewollt |
| **Englisch** | `<html lang>`, englische Seitenversion, `name:en` in OSM, englische Posts auf Instagram, Google-Rezensionen auf Englisch, ausländische Besucher in Rezensionen | Score 0–3: 0 = nur Japanisch, 1 = englischer Menüpunkt, 2 = englische Inhalte, 3 = Betrieb wirbt mit englischen Workshops |
| **Ausbildungs-Signal** | Text enthält „apprentice“, „lærling“, „godkjent lærebedrift“, „弟子“, „後継者募集“, „volunteer“ | starker Plus-Punkt: der Betrieb ist Lernende gewohnt |
| **Technik-Bedarf (Tauschwert)** | Website veraltet/kein Shop, „CNC“, „digitalisering“, Maschinenpark | Ansatzpunkt für die Mail („ich kann Ihnen bei … helfen“) |

**Technisches Hindernis:** Manche Seiten sind hinter Cloudflare-Bot-Schutz (z. B. naguri-canoe.com lieferte nur die
„Just a moment…“-Seite). Solche Leads nicht umgehen, sondern als „manuell öffnen“ markieren.

## Englisch-Hürde (Japan) – Bewertung

- **Hoch.** In der OSM-Stichprobe hat nur ein Bruchteil der japanischen Handwerks-Einträge einen englischen Namen;
  die geprüften Betriebsseiten (Takefu, Kumagawa, Inamine-Glas) sind ganz oder überwiegend japanisch.
  Traditionelle Meister erwarten zudem oft, dass Lehrlinge schweigend zusehen – der Sprachnachteil wirkt in der
  Werkstatt selbst weniger als bei der Anbahnung und im Alltag.
- **Konsequenz für das Tool:**
  1. Englisch-Score als eigenes Kriterium (fließt in „Realisierbarkeit“).
  2. Mail **zweisprachig**: kurzer, höflicher japanischer Teil (Keigo, vom LLM erzeugt) + englische Fassung.
     Nutzer muss offen sagen, dass er kein Japanisch spricht.
  3. Bei Score 0 lieber über Mittler (CIR der Gemeinde, 産地組合, Douglas Brooks) gehen als direkt.
  4. Vorrang für Orte mit Erfahrung mit Ausländern: Okinawa, Sado, Mashiko, Arita, Seki, Echizen/Takefu.
- **Skandinavien/AU/NZ/UK:** Englisch kein Problem.

---

## Empfohlene Lead-Strategie (in Schritten)

1. **Raster festlegen** (Handwerk × Region): z. B. Holzbootbau × {Norwegen-Westküste, dänische Inseln,
   Tasmanien, NZ-Nordinsel, japanische Küste}; Schmiede × {Echizen, Seki, Sakai, Miki}; Keramik × {Okinawa,
   Mashiko, Arita}; Glas × {Okinawa, Norwegen}. Daraus Bounding Boxes und Suchbegriffe (Englisch + Landessprache)
   ableiten.
2. **Kuratierte Quellen zuerst** (wenige, hohe Qualität): Fartøyvernsentre, Skibsbevaringsfonden, Heritage Crafts,
   Präfektur-Listen der 伝統的工芸品 mit 産地組合, AIR_J, NZTBS/Wooden Boat Centre. Pro Quelle ein einfacher
   HTML-Adapter; Japan-Seiten per LLM übersetzen und strukturieren.
3. **Breite aus offenen Daten:** Overture Places (DuckDB über die Raster-Boxen, Kategorie + Namens-Regex) und
   OSM-Länderextrakt bzw. kleine Overpass-Abfragen. Zusammenführen, Duplikate per Name + Distanz < 200 m entfernen.
4. **Grobfilter ohne LLM:** Website oder Social-Link vorhanden; Kategorie passt; keine Großunternehmen
   (z. B. 函館どつく = Großwerft raus, Luxusyacht-Werften raus); Großstadtkerne abwerten.
5. **Anreichern (LLM):** Website crawlen (Startseite, Über uns, Kontakt, max. ~5 Seiten), Bilder sammeln,
   Felder extrahieren: Handwerk, Größe, Familienbetrieb ja/nein, Englisch-Score, Ausbildungs-Signal,
   Technik-Ansatzpunkt, E-Mail/Formular, Unterkunft in der Nähe. Nur für die ~10 % besten zusätzlich Google
   Places (Enterprise) zum Verifizieren von Website/Telefon/Bewertungen – im Freikontingent (1 000/Monat) machbar.
6. **Bewerten** gegen `profil.yaml` wie Ausschreibungen, zusätzlich: Realisierbarkeit (Visum/EWR, Englisch,
   Erreichbarkeit), „Ist Lernende gewohnt?“.
7. **Mail-Entwurf** je Lead: konkret auf Betrieb bezogen (ein Boot/Objekt von der Website nennen), Zeitraum
   Mai–Juli 2027, 6–8 Wochen, keine Bezahlung nötig, Unterkunft reicht, Technik-Angebot passend zum
   Technik-Ansatzpunkt; Japan zweisprachig. Versand manuell.
8. **Mittler-Spur parallel** (Japan): eine Handvoll Mails an CIRs der Zielgemeinden, 産地組合 und Douglas Brooks
   – nicht mit „Jobanfrage“, sondern „Wen könnte ich fragen?“. Das erzeugt neue Leads, die in keiner Datenbank stehen.
9. **Zeitplan:** Kaltanfragen bei kleinen Betrieben brauchen Vorlauf; Mails ab ca. Dezember 2026 / Jänner 2027
   versenden, damit für Mai 2027 noch Zeit für Visum (Japan: Working Holiday) und Rückfragen bleibt.

---

## Stichprobe: konkrete Beispiel-Betriebe

Alle Links am 28.10.2026 geprüft, sofern nicht anders vermerkt. „Passung“ = grobe Einschätzung, nicht angefragt.

| # | Betrieb | Ort | Handwerk | Warum passend | Hürden | Link |
|---|---|---|---|---|---|---|
| 1 | **Risør Trebåtbyggeri A/S** | Risør, Norwegen | Holzbootbau & Restaurierung klassischer Holzboote | kleiner Betrieb, **godkjent lærebedrift**, bietet zusätzlich CNC/3D-Modellierung/Digitalisierung an → idealer Tauschwert für Informatik/Elektronik | Website nur Norwegisch (Englisch in NO üblich) | http://woodenboat.net/ |
| 2 | **Hardanger fartøyvernsenter** (Hardanger Maritime Center) | Norheimsund, Hardangerfjord | Holzbootbau, Takelage, Schmiede | lebende Werkstatt für historische Schiffe, Teil von Hardanger og Voss museum; Fjord-Lage | Museum = eher Volunteer/Praktikum als Lohn; Stellenliste vorhanden | https://fartoyvern.no |
| 3 | **Bredalsholmen Dokk og Fartøyvernsenter** | Kristiansand, Norwegen | Dock & Restaurierung historischer Schiffe (auch Stahl) | echte Werftarbeit, 150 Jahre Werft, „vern gjennom bruk“, englische Seite | eher größer, Stadtrand | https://www.bredalsholmen.no |
| 4 | **J. Ring-Andersen Skibsværft** | Frederiksø, Svendborg (Dänemark) | Holzschiffbau seit 1867, ~200 Holzschiffe gebaut | eine der traditionsreichsten Holzwerften Europas, Inselhafen | Dänisch-Seite; Größe unbekannt | https://www.ring-andersen.dk |
| 5 | **Glasshytta Blåst** | Norwegen (Ort aus OSM, Website ohne Inhalte im Abruf) | Glasbläserei | kleine Glashütte aus OSM-Liste | Website lieferte kaum Text → manuell prüfen | https://www.blaast.no |
| 6 | **Fiolinmaker Magnus Nedregård** | Norwegen | Geigenbau | Einzelwerkstatt (OSM `craft=luthier`) | Einzelperson → evtl. zu klein für 6–8 Wochen | https://www.nedregard.net *(Inhalt ungeprüft)* |
| 7 | **名栗カヌー工房 (Naguri Canoe Workshop)** | Hannō-Naguri, Saitama, Japan | Holzkanus aus lokalem Zedernholz (西川材) | einer von nur 5 OSM-Bootsbauern Japans; ländliches Tal, Holzbootbau | Cloudflare blockt automatischen Abruf; Japanisch; nahe Tokio (weniger „abgelegen“) | https://naguri-canoe.com |
| 8 | **タケフナイフビレッジ (Takefu Knife Village)** | Echizen, Fukui, Japan | Schmiede (Echizen-uchihamono, 伝統的工芸品) | Kooperative mehrerer Messerschmiede unter einem Dach, teils englisch, Besucher gewohnt; Präfektur Fukui hat Förderprogramm für angehende Handwerker | Kontakt per Telefon/Formular, keine E-Mail sichtbar | https://www.takefu-knifevillage.jp |
| 9 | **Okinawa-Yachimun-Töpfereien (z. B. 常秀陶器工房, 陶器工房 壹, 金城陶器所)** | Okinawa, Japan | Keramik (Tsuboya-/Yachimun) | kleine Familien-Brennöfen, Insel, gut in OSM erfasst; Okinawa ist ausländische Besucher gewohnt | Japanisch; Familienbetriebe nehmen selten Externe | http://www.tsunehidekobo.com/, https://www.toukikoubou1.com/, https://k-yoshi-toki.jimdofree.com/ *(Inhalte ungeprüft)* |
| 10 | **Toma House AIR** | Nara, Japan | Kintsugi/Urushi, Hyōgu | englischsprachig, Unterkunft + Unterricht gestellt, staatlich (Agency for Cultural Affairs) beauftragt | nur 4 Wochen, Bewerbung als „Artist“; Essen/Reise selbst | https://tomaunrestored.com/artistresidency/ |
| 11 | **Creative Residency Arita** | Arita, Saga, Japan | Porzellan | englische Koordination, Kontakt zu Porzellan-Handwerkern | **schließt Studierende aus, verlangt Berufserfahrung** in Kunst/Design; Unterkunft ~60 000 ¥/Monat → für Nutzer derzeit eher nicht erfüllbar | https://cri-arita.com/apply/criteria |
| 12 | **Douglas Brooks** (Mittler, kein Betrieb) | Vermont, USA / Japan | japanischer Holzbootbau | persönliche Kontakte zu den letzten 船大工 (Sado-Taraibune, Gifu-Kormoranboote, Himi, Kuma-Fluss) | keine Garantie; höflich und kurz anfragen | https://www.douglasbrooksboatbuilding.com |
| 13 | **Wooden Boat Centre – Tasmania** | Franklin, Huon Valley, TAS | Holzbootbau, Restaurierung | Zentrum der tasmanischen Holzboot-Szene, Volunteer-Seite, ländlich am Huon River; Working-Holiday-Visum AU möglich | Kurse kosten Geld – nur Volunteer/Werkstatt-Mitarbeit anfragen, nicht Kurs buchen | https://www.woodenboatcentre.com |
| 14 | **NZ Traditional Boat Building School** | Auckland (Percy Vos Shed) | Holzbootbau | gemeinnützig, von Volunteers getragen, braucht Unterstützung; Knoten zu NZ-Holzbootbauern (Classic Yacht Association) | Stadt; Kurse kostenpflichtig | https://nztbs.org.nz |
| 15 | **Sydney Heritage Fleet** | Sydney | Schiffsrestaurierung, Shipwright-Werkstatt | echte Restaurierungsarbeit an historischen Schiffen | Großstadt, Volunteer-Organisation | https://www.shf.org.au |

Bewusst **aussortiert** nach Prüfung: Salthouse Boatbuilders (NZ, Luxus-Motoryachten), 函館どつく (Großwerft),
宙吹ガラス房虹 (Okinawa, „一子相伝“ – Wissen bleibt in der Familie), 球磨川くだり (Bootstouren-Betreiber, kein Bootsbau
auf der Seite erwähnt).

## Offene Punkte für die Umsetzung

- Overture-Taxonomie nach passenden `basic_category`-Werten durchsuchen (z. B. Bootsbau, Schmiede, Töpferei) – nicht geprüft.
- Overpass-Zählung für AU, SE, GB, IS, FI nachholen (lokal über Geofabrik-Extrakt).
- Google-Places-AGB zu Speicherdauer verbindlich nachlesen, bevor Daten gecacht werden.
- Visa-Fragen (Japan Working Holiday, UK, AU) → siehe die Visa-Recherche in `docs/recherche/`.
