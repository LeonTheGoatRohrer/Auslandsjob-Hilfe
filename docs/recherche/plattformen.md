# Allgemeine Job-, Jugend- und Volunteer-Plattformen

> Stand: 28.10.2026. Bereich: EU- und Jugendprogramme, Working-Holiday-Jobbörsen, saisonale und ländliche Jobbörsen,
> NGO-Jobbörsen und kostenlose Work-Exchange-Portale ohne Login. Maritime, Naturschutz- und Forschungsquellen sowie
> unausgeschriebene Betriebe stehen in den anderen Dateien in `docs/recherche/`.
>
> **Was geprüft wurde:** `robots.txt` von ca. 55 Domains direkt abgerufen; APIs per Testaufruf geprüft, wo es ohne
> Registrierung ging (JobTech, NAV, ReliefWeb, Job Bank, EURES). Was nicht direkt geprüft wurde, ist als **UNSICHER**
> markiert. Die Angebotszahlen sind **grobe Schätzungen** aus Erfahrungswerten und Seitengröße, nicht gezählt.
>
> **„Passend“** heißt in dieser Datei: Dauer 6–12 Wochen möglich (oder verhandelbar), Start Mai bis Juni 2027, keine
> oder kleine Gebühr, praktische Arbeit, Visum für Österreicher realistisch (siehe `visa.md`). Ob ein Angebot
> wirklich gut ist (Außergewöhnlichkeit, Authentizität …), entscheidet erst die LLM-Bewertung. Die Zahl derer,
> die das schaffen, ist deutlich kleiner (siehe Summe am Ende).

## Wichtig vorab (aus `visa.md`)

- Working Holiday (WH) für Österreicher gibt es u. a. für **Japan, Australien (417), Neuseeland, Kanada (IEC), Südkorea,
  Taiwan, Hongkong und Argentinien**, jeweils 18–30 Jahre.
- Ohne WH-Visum ist **Arbeit gegen Kost und Logis** in Neuseeland, Australien (außer echtem Non-Profit-Volunteering)
  und Kanada **nicht erlaubt**. Die Jobbörsen dieser Länder lohnen sich deshalb nur, wenn das WH-Visum beantragt wird.
- **Saisonlage Mai–Juli:** Auf der Südhalbkugel (AU/NZ) ist dann Herbst/Winter. Das heißt Rebschnitt und
  Zitrus-/Kiwi-Ernte, im Norden Australiens Trockenzeit mit Hochsaison auf Rinderstationen. In Skandinavien und auf
  Island beginnt die Sommersaison: Farmen, Fischverarbeitung, Hütten, Natur.

## Übersichtstabelle

Zugriff: **API** = offizielle Schnittstelle · **RSS** = Feed · **Sitemap** = XML-Sitemap mit Angebots-URLs ·
**HTML** = Seiten parsen · **JS** = nur mit Browser-Rendering · ⛔ = robots.txt/AGB verbieten automatisierten Zugriff.

| # | Quelle | Fokus | Angebote gesamt (Schätzung) | davon passend (Schätzung) | Zugang | Technischer Zugriff | Passung | Gebühren üblich? |
|---|---|---|---|---|---|---|---|---|
| **EU / Jugend** |
| 1 | [EURES](https://eures.europa.eu) | Alle Stellen EU/EWR (aus nationalen Arbeitsämtern) | 2–3 Mio. | 300–1.000 (Saisonarbeit Skandinavien, Inseln, Alpen, Landwirtschaft, Englisch möglich) | öffentlich | Interne REST-Suche (`jv-search`), **ab 2025 evtl. mit Authentifizierung (UNSICHER)**; robots.txt verbietet nur `/search/`; Sitemap vorhanden | mittel | nein |
| 2 | [Europäisches Solidaritätskorps – Volunteering-Datenbank](https://youth.europa.eu/go-abroad/volunteering/opportunities_en) | Freiwilligenplätze bei akkreditierten Organisationen, 18–30 J. | 1.000–2.000 (UNSICHER) | 50–200 (Kurzzeit 2 Wo.–2 Mon. und Teams) | Liste öffentlich; **Bewerbung nur mit EU-Login + ESC-Registrierung** | HTML/JS (Drupal); **keine öffentliche API gefunden**; robots.txt erlaubt alles außer `/search/` | **hoch** (realisierbar, kostenlos) | **nein**: Reise, Unterkunft, Essen und Taschengeld werden gezahlt |
| 3 | [Eurodesk Opportunity Finder](https://programmes.eurodesk.eu) | Aggregator für Jugendprogramme, Stipendien, Freiwilligendienste | einige Hundert | 10–30 | öffentlich | HTML; robots.txt: **alles erlaubt** | mittel | gemischt |
| 4 | Workcamp-Netzwerke: [SCI](https://www.sci.ngo), [Alliance](https://www.alliance-network.eu), [workcamps.info](https://www.workcamps.info) | Internationale Workcamps und Medium-Term-Volunteering (MTV, 1–6 Mon.) | 2.000–3.000 Camps/Jahr | 20–80 (nur MTV oder aneinandergehängte Camps; Camps dauern meist 2–3 Wochen) | öffentlich, Bewerbung über nationale Partner (SCI Österreich, Grenzenlos) | SCI: **Cloudflare-Bot-Schutz (403)**; Alliance und workcamps.info: WordPress, Sitemap, robots.txt offen | mittel | **ja, klein**: Teilnahme ca. 100–300 €, teils Extra-Gebühr vor Ort |
| 5 | [Jugendportal.at](https://www.jugendportal.at) / [Grenzenlos](https://grenzenlos.or.at) | Österreichische Info- und Vermittlungsstellen (ESC, Workcamps) | < 100 | 5–20 | öffentlich | WordPress, Sitemap, robots.txt offen | mittel (eher Wegweiser als Angebotsquelle) | Grenzenlos: Vermittlungsgebühr (Höhe UNSICHER) |
| **Saisonal / ländlich, Europa** |
| 6 | [arbeidsplassen.nav.no](https://arbeidsplassen.nav.no) (Norwegen) | Alle Stellen in Norwegen inkl. Sommerjobs, Fischverarbeitung, Landwirtschaft | 15.000–25.000 | 20–100 | öffentlich | **Offizielle Feed-API** `pam-stilling-feed.nav.no` mit **öffentlichem Token** (abrufbar unter `/api/publicToken`, geprüft); robots.txt erlaubt alles | mittel–hoch | nein |
| 7 | [Platsbanken / JobTech](https://jobsearch.api.jobtechdev.se) (Schweden) | Alle Stellen in Schweden | 40.000–60.000 | 20–100 | öffentlich | **Offene API ohne Key** (Testaufruf liefert JSON, geprüft) | mittel (meist Schwedisch) | nein |
| 8 | [Työmarkkinatori](https://tyomarkkinatori.fi) (Finnland) | Alle Stellen in Finnland | 30.000–50.000 | 10–50 | öffentlich | robots.txt sperrt `/api/`; offene Daten-API existiert evtl. separat (**UNSICHER**) | niedrig–mittel | nein |
| 9 | [Jobnet.dk](https://job.jobnet.dk) (Dänemark) | Alle Stellen in Dänemark, auch Färöer/Grönland? (UNSICHER) | 20.000–40.000 | 10–40 | öffentlich | HTML; API **UNSICHER** | niedrig–mittel | nein |
| 10 | [Alfred.is](https://alfred.is) (Island) | Isländische Jobbörse inkl. Sommer-, Farm- und Tourismusjobs | 500–1.500 | 10–50 | öffentlich | Sitemap; robots.txt sperrt `/api/*` und Filter-Parameter, Detailseiten erlaubt | mittel–hoch (Ort außergewöhnlich) | nein |
| 11 | [France Travail](https://francetravail.io) (Frankreich) | Alle Stellen, auch „saisonnier agricole“ | 700.000–900.000 | 50–200 | öffentlich; API mit kostenloser Registrierung | **Offizielle API „Offres d'emploi“** (OAuth, kostenlos; Registrierung nicht getestet) | niedrig–mittel (Französisch; Weinlese erst Aug./Sep.) | nein |
| 12 | [Anyworkanywhere](https://www.anyworkanywhere.com) | UK/weltweit: Saisonjobs und Volunteering, viele Visa-Infos | einige Hundert | 10–40 | öffentlich | HTML; robots.txt **sperrt `*.html` und Suche** fast komplett ⛔ | niedrig–mittel | teils |
| **Working Holiday – Australien** (Visum 417 nötig) |
| 13 | [Backpacker Job Board](https://www.backpackerjobboard.com.au) | Farm, Station, Weinbau, regionale Jobs, oft mit Unterkunft | 1.000–3.000 aktiv | 100–400 | öffentlich (Bewerbung mit Konto) | **Sitemap `sitemapXMLJobs.xml`** (erlaubt); robots.txt sperrt `/search`, `/api/` und Feeds | **hoch** (bezahlt + Unterkunft; Hostel-Jobs abwerten) | nein (Vorsicht: einzelne „Job-Agenturen“ verlangen Gebühren) |
| 14 | [Workforce Australia](https://www.workforceaustralia.gov.au) (inkl. Harvest-Trail-Jobs) | Staatliche Jobbörse | 100.000+ | 100–500 | öffentlich | robots.txt: **`User-agent: * Disallow: /`** ⛔; keine öffentliche API gefunden (UNSICHER) | mittel | nein |
| 15 | [Seek](https://www.seek.com.au) (AU, auch NZ) | Größte Jobbörse AU/NZ | 200.000+ (AU) | 100–500 | öffentlich | robots.txt sperrt **`*/job/` und alle Query-URLs** ⛔; GraphQL gesperrt; keine API für Jobsuchende → nur manuell oder per E-Mail-Alert | mittel (Werkstatt- und Farmjobs regional) | nein |
| 16 | [Gumtree AU](https://www.gumtree.com.au) | Kleinanzeigen, auch Farm- und Gelegenheitsjobs | 5.000–20.000 Jobs | 50–200 | öffentlich | HTML; robots.txt sperrt Suche und JSON ⛔ (Kategorieseiten erlaubt) | niedrig–mittel (viele Scams) | nein |
| 17 | [Jora](https://au.jora.com), [Indeed](https://au.indeed.com) | Aggregatoren | sehr groß | (Duplikate der obigen) | öffentlich | Jora: **`Disallow: /`** für alle ⛔; Indeed: AGB verbieten Scraping ⛔ | niedrig (Duplikate) | nein |
| **Working Holiday – Neuseeland** (WH-Visum, nur 100 Plätze/Jahr) |
| 18 | [PickNZ](https://www.picknz.co.nz) | Ernte, Packhaus, **Rebschnitt (Juni–Aug.)** | 100–300 | 30–100 | öffentlich | WordPress, Yoast-Sitemap, robots.txt offen | mittel–hoch | nein |
| 19 | [Work the Seasons](https://www.worktheseasons.co.nz) | Staatliches Saisonjob-Portal (MSD) | 100–400 | 30–100 | öffentlich | robots.txt leer (= erlaubt); HTML/JS (UNSICHER) | mittel–hoch | nein |
| 20 | [Backpacker Board NZ](https://www.backpackerboard.co.nz) | Backpacker-Jobs, Farm, Hostel | 200–600 | 30–100 | öffentlich | robots.txt leer (= erlaubt); HTML | mittel | nein |
| 21 | [Trade Me Jobs](https://www.trademe.co.nz/a/jobs) | Größte NZ-Jobbörse | 10.000–20.000 | 50–150 | öffentlich | API **seit 04/2026 nur für gewerbliche Verkäufer**, Jobs-API über `api-jobs@trademe.co.nz`; robots.txt erlaubt Detailseiten, sperrt Suche; Sitemap | mittel | nein |
| **Working Holiday – Kanada** (IEC-Lotterie) |
| 22 | [Job Bank](https://www.jobbank.gc.ca) | Staatliche Jobbörse, auch Farm, Fischerei, Lodges | 80.000–120.000 | 50–300 | öffentlich | **Atom-Feed** `/jobsearch/feed/jobSearchRSSfeed?...` (geprüft, liefert Einträge); robots.txt: Crawl-delay 5 | mittel (Visum per Lotterie unsicher) | nein |
| **Working Holiday – Asien** |
| 23 | [Work24 / Worknet](https://www.work24.go.kr) (Südkorea) | Staatliche Jobbörse | 100.000+ | 5–30 | öffentlich | **Open-API** über data.go.kr mit Key (UNSICHER, nicht getestet); Sitemap; Koreanisch | niedrig (Sprache; WH H-1 max. 25 Std./Woche) | nein |
| 24 | [WH-Info-Center Korea](https://whic.mofa.go.kr) | Infos und Jobbörse für WH (Jobbörse UNSICHER) | < 200 | 5–20 | öffentlich | robots.txt erlaubt `/whic/`, `/ger/` | niedrig–mittel | nein |
| 25 | Japanische Agrar-Jobbörsen (z. B. あぐりナビ / Agri-Navi, 農業求人) | Kurzzeit-Farmjobs **1–3 Monate mit Unterkunft** | einige Tausend (UNSICHER) | 20–100 (UNSICHER) | öffentlich | **nicht geprüft**; Japanisch | **hoch** (Dorf, Einheimische, mit WH Japan) – **zuerst prüfen** | nein |
| 26 | Resort-Baito-Portale (リゾートバイト, z. B. Dive) | Saisonjobs mit Unterkunft in Resorts/Inseln | einige Tausend | 20–100 | öffentlich | nicht erreichbar beim Test (Verbindungsfehler); JS (UNSICHER) | niedrig–mittel (meist Hotel/Gastro, aber abgelegene Orte) | nein (Vermittler) |
| 27 | [GaijinPot Jobs](https://jobs.gaijinpot.com) | Jobs für Ausländer in Japan | 1.000–3.000 | 0–10 | öffentlich | **Akamai-Bot-Schutz (403)** ⛔ | niedrig (Unterricht, IT, Städte) | nein |
| 28 | [JAWHM](https://www.jawhm.or.jp) | Japan Association for Working Holiday Makers | < 100 | 0–10 | Mitgliedschaft (UNSICHER) | robots.txt offen | niedrig | **ja** (Mitgliedsbeitrag, Höhe UNSICHER) |
| 29 | Taiwan: [youthtaiwan.net](https://www.youthtaiwan.net), [104.com.tw](https://www.104.com.tw) | WH-Infos bzw. größte Jobbörse | 104: sehr groß | 0–20 | öffentlich | youthtaiwan nicht erreichbar; 104: **403 (Bot-Schutz)** ⛔; Chinesisch | niedrig | nein |
| **NGO-Jobbörsen** |
| 30 | [Idealist](https://www.idealist.org) | NGO-Jobs, Praktika und **Volunteer-Angebote** weltweit | 10.000–20.000 | 20–80 (Volunteer mit Unterkunft, international) | öffentlich | robots.txt offen (nur Google-Extended von `/careers/` ausgesperrt); Sitemap; alte API leitet um (302) → **keine öffentliche API (UNSICHER)**; Seiten JS-lastig | mittel | teils (Voluntourism-Anbieter filtern) |
| 31 | [ReliefWeb Jobs](https://reliefweb.int/jobs) | Humanitäre Jobs | 2.000–4.000 | 0–10 | öffentlich | **API v2**, braucht seit 2025 **genehmigten `appname`** (geprüft: 403 ohne); v1 abgeschaltet | niedrig (Profi-Stellen mit Abschluss) | nein |
| 32 | [UN Volunteers](https://app.unv.org) | UN-Freiwillige (Youth 18–29) | einige Hundert | 0–5 | Login | SPA + Incapsula-Bot-Schutz ⛔ | niedrig (meist 6–12 Mon., Abschluss nötig) | nein |
| 33 | [Impactpool](https://www.impactpool.org), [DevNetJobs](https://devnetjobs.org), [NGO Jobs in Africa](https://ngojobsinafrica.com) | Entwicklungszusammenarbeit | je 1.000–5.000 | 0–10 | öffentlich | Sitemaps; robots.txt offen | niedrig | nein |
| **Nationale Volunteer-Börsen** |
| 34 | [GoVolunteer](https://govolunteer.com.au) (AU), [volunteer.ca](https://volunteer.ca), [Volunteering NZ](https://www.volunteeringnz.org.nz) | Lokales Ehrenamt | je Tausende | 5–30 (Naturschutz-Einsätze mit Unterkunft) | öffentlich | GoVolunteer: Cloudflare ⛔; volunteer.ca: Crawl-delay 10; NZ: Sitemap | niedrig–mittel (meist stundenweise, lokal) | nein |
| **Kostenlose Work-Exchange-Portale ohne Login-Pflicht** |
| 35 | [Volunteer South America](https://www.volunteersouthamerica.net) (+ Schwesterseiten) | Verzeichnis **kostenloser oder günstiger** Projekte in Lateinamerika | 300–600 Einträge | 30–100 | öffentlich | Sitemap, robots.txt offen; reines HTML | **mittel–hoch** (lokale Organisationen; Gebühren angegeben) | teils klein (Kost-Beitrag) |
| 36 | [Volunteers Base](https://www.volunteersbase.com) | Kostenloses Verzeichnis von Volunteer-Projekten | 1.000–3.000 | 30–100 | öffentlich | Sitemap-Index, robots.txt offen | mittel (Qualität schwankt) | teils |
| 37 | [Workingtraveller](https://workingtraveller.com) | Work Exchange, für Volunteers kostenlos | einige Tausend Hosts (UNSICHER) | 30–100 | Liste öffentlich, Kontakt mit Login (UNSICHER) | robots.txt offen; Struktur nicht geprüft | mittel | nein |
| 38 | [Hippohelp](https://hippohelp.com) | Kostenlose Work-Exchange-Karte | einige Tausend Hosts (UNSICHER) | 30–100 | Karte öffentlich, Details/Kontakt mit Login (UNSICHER) | WordPress, robots.txt offen; Karte per AJAX/JS | mittel | nein |
| 39 | [Grassroots Volunteering](https://www.grassrootsvolunteering.org) | Verzeichnis lokaler Low-Cost-Projekte | 500–1.000 | 20–60 | öffentlich | **403 für Bots** ⛔ (manuell) | mittel–hoch | teils klein |
| **Ausgeschlossen / niedrig (nur zur Vollständigkeit)** |
| 40 | [CoolWorks](https://www.coolworks.com), [Backdoor Jobs](https://www.backdoorjobs.com) | US-Saisonjobs | Tausende | 0 | öffentlich | CoolWorks: Sitemap; Backdoor: Mod_Security-Block | niedrig – **ohne J-1-Visum nicht realisierbar** | Programmgebühren für J-1 |
| 41 | [ErasmusIntern](https://erasmusintern.org) | Erasmus-Praktika | Tausende | 0–10 | Login | Cloudflare ⛔ | niedrig (Büro-Praktika; Erasmus+ setzt Studium oder Lehre voraus) | nein |
| 42 | [Bundesagentur Jobsuche](https://www.arbeitsagentur.de/jobsuche) (DE) | Alle Stellen in DE | 1 Mio. | wenige | öffentlich | Inoffizielle, gut dokumentierte API (jobsuche.api.bund.dev); robots.txt offen | niedrig (Deutschland nicht außergewöhnlich) | nein |
| 43 | Workaway, WWOOF, HelpX, Worldpackers | Work Exchange | sehr groß | sehr viele | **Bezahlte Mitgliedschaft** | Workaway: robots.txt sperrt `/api/`, Profile per Sitemap öffentlich (nur Teaser) | – vorerst ausgeschlossen (Projektentscheidung) | Mitgliedschaft 40–60 € |

## Notizen je Quelle

**1 EURES.** Größter Pool, enthält NAV-, Platsbanken- und Jobnet-Stellen größtenteils doppelt. Ein EURES-Flag
markiert Stellen, die ausdrücklich Leute aus anderen EU-Ländern suchen. Vielversprechende Filter: Saisonarbeit,
Landwirtschaft, Fischerei, Island, Norwegen, Färöer, Kanaren, Azoren. Die interne Such-API (`jv-search`) wurde früher
offen genutzt; laut EURES-Hinweis gibt es seit 2025 eine Version „mit verbesserter Authentifizierung“. Mein
POST-Testaufruf auf den alten Endpunkt lieferte 404 → Zugriffsweg **UNSICHER**, vor dem Bau im Browser-Netzwerk-Tab
nachsehen. Felder: Titel, Ort, Vertragsart, Arbeitszeit, Sprache, Beschreibung; **kein strukturiertes Gehalt**, keine
Unterkunft (steht im Freitext).

**2 Europäisches Solidaritätskorps (ESC).** Beste Quelle für „kostenlos und realistisch“: Reise, Unterkunft, Essen,
Taschengeld und Versicherung sind gedeckt. Es gibt drei Formate. Individuelles Volunteering dauert meist 2–12 Monate,
Kurzzeit 2 Wochen bis 2 Monate; dafür gibt es eigene Plätze für Jugendliche mit weniger Möglichkeiten (UNSICHER, ob
das hier zutrifft). Bei „Volunteering Teams“ arbeiten Gruppen 2 Wochen bis 2 Monate an einem Projekt, oft
Naturschutz, Kulturerbe oder Renovierung. **Viele Plätze liegen nicht in der öffentlichen Datenbank**, sondern werden
direkt über die Entsende-Organisation vergeben (in Österreich z. B. Grenzenlos, SCI, Jugendinfos). Die Datenbank lädt
die Liste per JS; eine Daten-API wurde nicht gefunden. Felder: Ort, Zeitraum, Dauer, Thema, Organisation, Deadline.
Authentizität schwankt; manche Plätze sind Büro- oder Kinderbetreuung.

**4 Workcamps.** Klassische Camps dauern 2–3 Wochen und passen so nicht. Interessant sind zwei Wege: **MTV/LTV**
(1–6 Monate, bei vielen Partnern gelistet) und zwei bis drei Camps hintereinander in einer Region. Typische
Arbeit: Renovierung, Trockenmauern, Naturschutz, Archäologie. Die Gebühr liegt meist unter 500 €, muss aber
markiert werden. Island und die Färöer haben viele Naturschutz-Camps (SEEDS, WF; diese gehören eher zur
Naturschutz-Session).

**6 NAV (Norwegen).** Technisch die sauberste Quelle: Die offizielle Feed-API mit öffentlichem Token liefert alle
Stellen als JSON (Titel, Arbeitgeber, Ort, Beschreibung, Fristen, Beschäftigungsart). Der Token rotiert und muss
regelmäßig neu von `/api/publicToken` geholt werden. Suchbegriffe: „sommerjobb“, „gårdsarbeider“,
„fiskeindustri“/Lofoten, „seter“. Norwegisch ist oft gefordert; Englisch-Angebote sind seltener.

**7 JobTech (Schweden).** Offene API, kein Key nötig, Freitextsuche, viele strukturierte Felder (Beschäftigungsart,
Dauer, Arbeitszeit, Sprache). Es gibt auch eine historische und eine Stream-API. Suchbegriffe: „säsong“,
„lantbruk“, „fjäll“, „sommarjobb“.

**10 Alfred.is (Island).** Klein, aber im Sommer viele Jobs in abgelegenen Orten (Farmen, Gästehäuser,
Fischverarbeitung), oft mit Unterkunft und auf Englisch. Per Sitemap und Detailseiten lesbar.

**13 Backpacker Job Board (AU).** Für Australien die beste Kombination aus Passung und erlaubtem Zugriff: Die
Jobs-Sitemap steht ausdrücklich in robots.txt. Viele Anzeigen nennen Lohn, Unterkunft, Dauer und „88 days“
(Zweitvisum-tauglich). Vorsicht bei Hostel-Jobs und Lockangeboten von Arbeitsvermittlern. Für Mai bis Juli: Mango-
und Zitrusernte in QLD und NT, Rinderstationen (Jackaroo/Jillaroo, Werkstatt), Rebschnitt in Victoria und South
Australia.

**14/15 Workforce Australia und Seek.** Viele passende Jobs, aber robots.txt verbietet das automatische Abrufen
(Workforce komplett, Seek bei den Job-Seiten). Empfehlung: nicht scrapen, sondern **E-Mail-Jobalerts** einrichten und
diese Mails einlesen, oder die Seiten manuell sichten.

**18–21 Neuseeland.** Mai bis Juli ist das Ende der Kiwi-Ernte und Beginn des **Rebschnitts** (Marlborough, Central
Otago, Hawke's Bay). PickNZ und Backpacker Board lassen sich laut robots.txt abrufen. Das WH-Visum ist auf 100 Plätze
begrenzt, deshalb nur mittlere Priorität.

**22 Job Bank (Kanada).** Der Atom-Feed ist geprüft und funktioniert (Filter per URL-Parameter, z. B. Provinz und
Alter der Anzeige). Er liefert Titel, Link und Kurzbeschreibung; Details stehen auf der Detailseite (Lohn, Dauer,
„seasonal“). Crawl-delay 5 s einhalten. Passung hängt an der IEC-Lotterie.

**25 Japanische Agrar-Jobbörsen.** Nicht geprüft, aber vom Profil her der interessanteste Punkt in Asien: Farmen
suchen dort ausdrücklich Kurzzeit-Hilfen für 1–3 Monate, mit Unterkunft und Lohn. Das passt zu WH Japan (kostenlos)
und zum Wunsch „Dorf, Einheimische“. Sprache: Japanisch, Anzeigen per LLM übersetzbar. **Nächster Schritt:**
Portale identifizieren und robots.txt prüfen (Abgrenzung zur Lead-Session: hier geht es um ausgeschriebene Stellen).

**30 Idealist.** Der Filter „Volunteer Opportunities“ plus „international“ liefert NGO-Plätze. Viele davon sind
kostenpflichtige Voluntourism-Anbieter, die Gebühr muss also extrahiert und markiert werden. Die frühere öffentliche
API ist offenbar abgeschaltet (302). Seiten per Sitemap auffindbar.

**31 ReliefWeb.** Saubere API, braucht aber seit 2025 einen genehmigten `appname` (kostenlos beantragbar). Inhaltlich
kaum passend (Fachstellen). Nur anbinden, wenn der Aufwand minimal bleibt.

**35–39 Work-Exchange ohne Login.** Volunteer South America ist ein kuratiertes Verzeichnis „free or low-cost“ und
damit eher eine Lead-Liste lokaler Projekte mit Kontaktadressen als eine Stellenbörse. Für Hippohelp und
Workingtraveller ist **UNSICHER**, wie viel ohne Login sichtbar ist; vor dem Anbinden die AGB lesen.

## Summe „maximal erreichbare passende Angebote“

Summe der Spalte „passend“ über alle Quellen, **die automatisiert angebunden werden dürfen**
(ohne ⛔, ohne Ausgeschlossene):

| Gruppe | Quellen | passend (Schätzung) |
|---|---|---|
| EU / Jugend | 1–5 | 385–1.330 |
| Europa saisonal | 6–11 | 120–540 |
| Australien | 13 | 100–400 |
| Neuseeland | 18–21 | 140–450 |
| Kanada | 22 | 50–300 |
| Asien | 23–26, 28 | 50–260 |
| NGO / Volunteer | 30, 31, 33, 34 (ohne GoVolunteer) | 25–130 |
| Work Exchange | 35–38 | 120–400 |
| **Brutto** | | **≈ 1.000–3.800** |

- Nach **Duplikaten** (EURES enthält NAV, Platsbanken und Jobnet zu großen Teilen; NZ-Portale überschneiden sich) und
  ohne Länder, deren **Visum nicht beantragt** wird (realistisch ist z. B. nur ein bis zwei WH-Länder), bleiben
  grob **600–2.000 Angebote**, die die harten Filter bestehen.
- Davon erfüllen vermutlich nur **5–10 %** die Kernkriterien wirklich gut (außergewöhnlich, authentisch, mit
  Einheimischen): also **ca. 50–200 starke Kandidaten** aus diesem Bereich. Das reicht für die geplanten Top 100,
  zusammen mit den Maritim-, Naturschutz- und Lead-Quellen.
- Nicht automatisiert, aber manuell oder per Alert-Mail lohnend: Seek, Workforce Australia, Gumtree AU,
  Grassroots Volunteering (zusätzlich ca. 250–1.200 passende, viele davon Duplikate).

## Top 10 – zuerst anbinden

| Rang | Quelle | Warum |
|---|---|---|
| 1 | **Backpacker Job Board (AU)** | Größter Pool bezahlter Jobs mit Unterkunft im Zielzeitraum (Stationen, Ernte, Rebschnitt); Jobs-Sitemap ausdrücklich erlaubt; Felder Lohn, Unterkunft und Dauer stehen meist im Text. |
| 2 | **ESC-Volunteering-Datenbank** | Einzige große Quelle, bei der alles kostenlos ist und das Visum kein Thema; Teams und Kurzzeit passen in die Dauer. Zugriff per HTML/JS – Adapter etwas aufwendiger. |
| 3 | **NAV-Feed (Norwegen)** | Offizielle API mit öffentlichem Token, vollständige Daten, Skandinavien ist Wunschregion; geringster Bauaufwand. |
| 4 | **JobTech (Schweden)** | Offene API ohne Key; gleicher Adapter-Typ wie NAV; Sommer- und Saisonjobs auf dem Land. |
| 5 | **EURES** | Deckt den Rest der EU ab (Inseln, Überseegebiete, Alpen, Island). Zugriffsweg erst klären (Authentifizierung 2025, UNSICHER); danach hohe Reichweite. |
| 6 | **Japanische Agrar-Jobbörsen** | Profilnächste Asien-Quelle (Dorf, 1–3 Monate, Unterkunft, WH Japan kostenlos); vor dem Bau Portale und robots.txt prüfen. |
| 7 | **Job Bank Kanada** | Funktionierender Atom-Feed, sehr wenig Aufwand; Farm-, Fischerei- und Lodge-Jobs; Nutzen hängt an der IEC-Lotterie. |
| 8 | **PickNZ + Backpacker Board NZ** | Beide erlaubt und HTML-einfach; Rebschnitt-Saison passt genau. Das NZ-Visum (100 Plätze) macht es unsicher. |
| 9 | **Alfred.is (Island)** | Klein, aber außergewöhnlicher Ort, Englisch üblich, Sommerstart passt; Sitemap erlaubt. |
| 10 | **Volunteer South America / Volunteers Base** | Kostenlose Verzeichnisse lokaler Low-Cost-Projekte (Lateinamerika und weltweit) ohne Login; Sitemaps offen. Liefert eher Leads, mit sichtbaren Gebühren. |

**Bewusst nicht in den Top 10:** Seek und Workforce Australia (robots.txt verbietet es → Alert-Mails), Idealist
(viel Voluntourism, keine API; Platz 11), Workcamps (Dauer passt selten; Platz 12), ReliefWeb (sauber, aber kaum
passend).

## Offene Punkte / UNSICHER

- EURES: aktueller Such-Endpunkt und ob ein Login oder Key nötig ist.
- ESC-Datenbank: Daten-Endpunkt hinter der JS-Liste; ob Kurzzeit-Plätze dort überhaupt gelistet sind.
- Hippohelp, Workingtraveller: Was ist ohne Login sichtbar, was erlauben die AGB?
- Japanische Agrar- und Resort-Portale, Work24-API, Taiwan: nicht geprüft.
- Alle Angebotszahlen sind Schätzungen; beim ersten Adapterlauf echte Zahlen erfassen und hier nachtragen.
