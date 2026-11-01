"use strict";

// ---------- Beschriftungen ----------
const BEZAHLUNG = {
  lohn: "Lohn", taschengeld: "Taschengeld", unterkunft_gegen_arbeit: "Unterkunft gegen Arbeit",
  unbezahlt: "Unbezahlt", kostet_geld: "Kostet Geld", unklar: "Kosten unklar",
};
const UNTERKUNFT = {
  beim_betrieb: "Beim Betrieb", crew_haus: "Crew-Haus", schiff: "An Bord",
  selbst_organisieren: "Selbst organisieren", unklar: "Unklar",
};
const ENGLISCH = { ja: "Englisch ja", teilweise: "Englisch teilweise", nein: "Kein Englisch", nicht_angegeben: "Sprache nicht angegeben" };
const VERPFLEGUNG = { ja: "inkl. Verpflegung", true: "inkl. Verpflegung", nein: "ohne Verpflegung", false: "" };
const VISUM = {
  machbar: "Visum machbar", "working_holiday_nötig": "Working Holiday nötig", mit_auflagen: "Visum mit Auflagen",
  unklar: "Visum unklar", verboten: "Visum: nicht erlaubt",
};
const SPARTE = { ausschreibung: "Ausschreibung", lead: "Lead – direkt anfragen" };
const HERKUNFT = { "vorläufig": "Von Hand recherchiert", automatisch: "Automatisch gesammelt" };
const KRITERIUM = {
  "außergewöhnlichkeit": "Außergewöhnlichkeit", "authentizität": "Authentizität", menschen: "Menschen",
  lernen: "Lernen", praktische_arbeit: "Praktische Arbeit", sinn: "Sinn", ort: "Ort",
  abenteuer: "Abenteuer", eigener_beitrag: "Eigener Beitrag", finanzierung: "Finanzierung",
  realisierbarkeit: "Realisierbarkeit",
};

const HERZ = `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 21s-7.5-4.6-9.6-9.1C.9 8.6 2.9 4.5 6.7 4.5c2.1 0 3.6 1.1 4.3 2.5h2c.7-1.4 2.2-2.5 4.3-2.5 3.8 0 5.8 4.1 4.3 7.4C19.5 16.4 12 21 12 21z"/></svg>`;

// ---------- Zustand ----------
const S = {
  angebote: [], bewertungen: {}, kategorien: {}, kernkriterien: {}, quellen: [],
  kaputt: new Set(),              // Bild-URLs, die nicht laden
  filter: ladeFilter(),
  dg: null,                       // {modus, liste, index, bild}
};

function standardFilter() {
  return { kategorie: null, sparte: [], status: [], bezahlung: [], unterkunft: [], englisch: [], visum: [],
           land: "", nurUnbewertet: false, ausgeschlossene: false, geschlossene: false, sort: "passung" };
}
function ladeFilter() {
  try { return { ...standardFilter(), ...JSON.parse(localStorage.getItem("filter") || "{}") }; }
  catch { return standardFilter(); }
}
function speichereFilter() {
  try { localStorage.setItem("filter", JSON.stringify(S.filter)); } catch { /* egal */ }
}

// ---------- Hilfen ----------
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const schoen = (key) => (key || "").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
const bew = (id) => S.bewertungen[id] || {};
const nachId = (id) => S.angebote.find((a) => a.id === id);
const katName = (key) => (S.kategorien[key]?.name || schoen(key)).replace(/^\S+\s/, "");
const katEmoji = (key) => (S.kategorien[key]?.name || "").split(" ")[0];
const farbe = (key) => `var(--k-${key}, var(--tinte))`;
const kostetGeld = (a) => a.bezahlung === "kostet_geld" || (a.gebuehr_eur ?? 0) > 0;
const bilderVon = (a) => (a.bilder || []).filter((b) => !S.kaputt.has(b.url));
const tageSeit = (iso) => (Date.now() - new Date(iso)) / 864e5;
const istGeschlossen = (a) => a.zustand?.status === "geschlossen";
const istNeu = (a) => !!a.zustand && tageSeit(a.zustand.erstmals_gesehen) <= 7;
const istGeaendert = (a) => (a.zustand?.aenderungen || []).some((x) => tageSeit(x.datum) <= 14);
const datumKurz = (iso) => iso ? new Date(iso).toLocaleDateString("de-AT", { day: "numeric", month: "short", year: "numeric" }) : "";

function dauerText(a) {
  if (!a.dauer_wochen) return "Unbekannt";
  const [von, bis] = a.dauer_wochen;
  return von === bis ? `${von} Wochen` : `${von}–${bis} Wochen`;
}
function gebuehrText(a) {
  if (a.gebuehr_eur) return `Kostet ca. ${a.gebuehr_eur} €`;
  return "Kostet Geld – Höhe prüfen";
}

// ---------- Daten laden / speichern ----------
// Die Verbindung bricht auf manchen Rechnern gelegentlich ab (z. B. Web-Scanner des Virenschutzes)
async function holeJson(url, optionen = {}) {
  for (let versuch = 1; ; versuch++) {
    try {
      const antwort = await fetch(url, { cache: "no-store", ...optionen });
      if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
      return await antwort.json();
    } catch (fehler) {
      if (versuch >= 4) throw fehler;
      await new Promise((r) => setTimeout(r, 400 * versuch));
    }
  }
}

async function lade() {
  const d = await holeJson("/api/daten");
  Object.assign(S, d);
  render();
}

async function speichere(id, felder) {
  S.bewertungen[id] = { ...bew(id), ...felder };
  aktualisiereKopf();
  S.bewertungen[id] = await holeJson("/api/bewertung", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, ...felder }),
  });
}

// ---------- Filtern ----------
function gefiltert({ ohneKategorie = false } = {}) {
  const f = S.filter;
  const passt = (liste, wert) => liste.length === 0 || liste.includes(wert);
  const ergebnis = S.angebote.filter((a) =>
    (f.ausgeschlossene || a.ausschluss.length === 0) && (f.geschlossene || !istGeschlossen(a)) &&
    (ohneKategorie || !f.kategorie || a.kategorie === f.kategorie || (a.tags || []).includes(f.kategorie)) &&
    passt(f.sparte, a.sparte) && passt(f.status, a.status) && passt(f.bezahlung, a.bezahlung) && passt(f.unterkunft, a.unterkunft) &&
    passt(f.englisch, a.englisch) && passt(f.visum, a.visum) &&
    (!f.land || a.land === f.land) &&
    (!f.nurUnbewertet || bew(a.id).rating == null));
  if (f.sort === "rating") {
    ergebnis.sort((x, y) => (bew(y.id).rating ?? -1) - (bew(x.id).rating ?? -1) || y.passung - x.passung);
  }
  return ergebnis; // Server liefert bereits nach Passung sortiert
}

// ---------- Kopfzeile ----------
function aktualisiereKopf() {
  const bewertet = S.angebote.filter((a) => bew(a.id).rating != null).length;
  const gemerkt = S.angebote.filter((a) => bew(a.id).liked).length;
  document.getElementById("fortschritt").textContent = `${bewertet} von ${S.angebote.length} bewertet`;
  document.getElementById("zahl-favoriten").textContent = gemerkt;
  const view = aktuelleView();
  document.querySelectorAll(".tabs a").forEach((a) => {
    if (a.dataset.view === view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
}

function aktuelleView() {
  const h = location.hash.slice(1);
  return ["uebersicht", "favoriten", "quellen"].includes(h) ? h : "uebersicht";
}

// ---------- Render: Übersicht ----------
function render() {
  aktualisiereKopf();
  const view = aktuelleView();
  const main = document.getElementById("inhalt");
  if (view === "favoriten") main.innerHTML = renderFavoriten();
  else if (view === "quellen") main.innerHTML = renderQuellen();
  else main.innerHTML = renderUebersicht();
  if (S.dg) renderDurchgehen();
}

function renderUebersicht() {
  const liste = gefiltert();
  const basis = S.angebote.filter((a) => a.ausschluss.length === 0 && (S.filter.geschlossene || !istGeschlossen(a)));
  const ausgeschlossen = S.angebote.length - basis.length;
  const zaehle = (k) => basis.filter((a) => a.kategorie === k || (a.tags || []).includes(k)).length;

  const flaggen = [
    `<button class="flagge flagge-alle" data-aktion="kategorie" data-wert="" aria-pressed="${!S.filter.kategorie}">
       <strong>Alle</strong><span>${basis.length} Angebote</span></button>`,
    ...Object.keys(S.kategorien).map((k) => `
      <button class="flagge ${S.filter.kategorie ? "gedimmt" : ""}" style="--farbe:${farbe(k)}"
              data-aktion="kategorie" data-wert="${k}" aria-pressed="${S.filter.kategorie === k}">
        <strong>${katEmoji(k)} ${esc(katName(k))}</strong><span>${zaehle(k)} Angebote</span>
      </button>`),
  ].join("");

  return `
    <section class="hero">
      <div>
        <h1>Welche zwei Monate erzählst du noch mit 50?</h1>
        <p>${basis.length} Angebote, sortiert danach, wie gut sie zu deinen Kriterien passen.
           Wähle eine Kategorie und Filter – oder geh einfach alle der Reihe nach durch.</p>
      </div>
      <div class="hero-knoepfe">
        <button class="knopf knopf-haupt" data-aktion="durchgehen">Angebote durchgehen</button>
        <button class="knopf" data-aktion="zufall">Zufälliges Angebot</button>
      </div>
    </section>
    <section class="flaggen" aria-label="Kategorien">${flaggen}</section>
    <div class="raster">
      ${renderFilter(ausgeschlossen)}
      <section>
        <div class="ergebnis-kopf">
          <h2>${liste.length} ${liste.length === 1 ? "Angebot" : "Angebote"}${S.filter.kategorie ? ` in ${esc(katName(S.filter.kategorie))}` : ""}</h2>
          <p>${S.filter.sort === "rating" ? "Nach deiner Bewertung sortiert" : "Beste Passung zuerst"}</p>
        </div>
        ${liste.length ? `<div class="karten">${liste.map(renderKarte).join("")}</div>`
          : `<div class="leer"><h2>Keine Angebote für diese Filter</h2>
               <p>Entferne einen Filter oder <button class="filter-reset" data-aktion="reset">setze alle zurück</button>.</p></div>`}
      </section>
    </div>`;
}

function chipGruppe(titel, feld, labels) {
  const werte = [...new Set(S.angebote.map((a) => a[feld]).filter(Boolean))];
  if (werte.length < 2) return "";
  return `<fieldset><legend>${titel}</legend><div class="chips">
    ${werte.map((w) => `<button class="chip-knopf" data-aktion="chip" data-feld="${feld}" data-wert="${esc(w)}"
        aria-pressed="${S.filter[feld].includes(w)}">${esc(labels[w] || schoen(w))}</button>`).join("")}
  </div></fieldset>`;
}

function renderFilter(ausgeschlossen) {
  const laender = [...new Set(S.angebote.map((a) => a.land))].sort((a, b) => a.localeCompare(b, "de"));
  return `<aside class="filter" aria-label="Filter">
    ${chipGruppe("Art", "sparte", SPARTE)}
    ${chipGruppe("Herkunft", "status", HERKUNFT)}
    ${chipGruppe("Bezahlung", "bezahlung", BEZAHLUNG)}
    ${chipGruppe("Unterkunft", "unterkunft", UNTERKUNFT)}
    ${chipGruppe("Sprache im Betrieb", "englisch", ENGLISCH)}
    ${chipGruppe("Visum", "visum", VISUM)}
    <fieldset><legend>Land</legend>
      <select data-aktion="land" aria-label="Land">
        <option value="">Alle Länder</option>
        ${laender.map((l) => `<option ${S.filter.land === l ? "selected" : ""}>${esc(l)}</option>`).join("")}
      </select></fieldset>
    <fieldset><legend>Sortierung</legend>
      <select data-aktion="sort" aria-label="Sortierung">
        <option value="passung" ${S.filter.sort === "passung" ? "selected" : ""}>Beste Passung</option>
        <option value="rating" ${S.filter.sort === "rating" ? "selected" : ""}>Meine Bewertung</option>
      </select></fieldset>
    <fieldset><legend>Anzeigen</legend>
      <label class="schalter"><input type="checkbox" data-aktion="nurUnbewertet" ${S.filter.nurUnbewertet ? "checked" : ""}> Nur noch nicht bewertete</label>
      <label class="schalter"><input type="checkbox" data-aktion="ausgeschlossene" ${S.filter.ausgeschlossene ? "checked" : ""}> Ausgeschlossene zeigen (${ausgeschlossen})</label>
      <label class="schalter"><input type="checkbox" data-aktion="geschlossene" ${S.filter.geschlossene ? "checked" : ""}> Geschlossene zeigen (${S.angebote.filter(istGeschlossen).length})</label>
    </fieldset>
    <button class="filter-reset" data-aktion="reset">Alle Filter zurücksetzen</button>
  </aside>`;
}

function bildOderPlatzhalter(a, bild, klasse = "") {
  if (bild) {
    return `<img class="${klasse}" src="${esc(bild.url)}" data-url="${esc(bild.url)}" alt="" loading="lazy"
             referrerpolicy="no-referrer" onerror="bildFehler(this)" onload="bildPruefen(this)">`;
  }
  return `<div class="platzhalter-bild">${esc(a.ort || a.land)}</div>`;
}

function renderKarte(a) {
  const b = bew(a.id);
  const bild = bilderVon(a)[0];
  return `
  <article class="karte ${a.ausschluss.length ? "ausgeschlossen" : ""}" style="--farbe:${farbe(a.kategorie)}">
    <div class="karte-bild">
      ${bildOderPlatzhalter(a, bild)}
      <span class="kat-label">${katEmoji(a.kategorie)} ${esc(katName(a.kategorie))}</span>
      ${kostetGeld(a) ? `<div class="warnband">⚠ ${esc(gebuehrText(a))}</div>`
        : a.bezahlung === "unklar" ? `<span class="hinweis-unklar">Kosten unklar</span>` : ""}
    </div>
    <button class="herz-knopf" data-aktion="like" data-id="${a.id}" aria-pressed="${!!b.liked}"
            aria-label="${b.liked ? "Nicht mehr merken" : "Merken"}">${HERZ}</button>
    <div class="karte-inhalt">
      <h3>${esc(a.titel)}</h3>
      <p class="org">${esc(a.organisation)}</p>
      <p class="ort">${esc(a.land)}${a.region ? `, ${esc(a.region)}` : ""}</p>
      <div class="tags">
        <span class="tag ${["lohn", "taschengeld"].includes(a.bezahlung) ? "tag-gut" : a.bezahlung === "kostet_geld" ? "tag-schlecht" : ""}">${esc(BEZAHLUNG[a.bezahlung] || a.bezahlung)}</span>
        <span class="tag">${esc(dauerText(a))}</span>
        ${a.sparte === "lead" ? `<span class="tag">Lead</span>` : ""}
        ${istGeschlossen(a) ? `<span class="tag tag-schlecht">Geschlossen</span>` : istNeu(a) ? `<span class="tag tag-neu">Neu</span>` : ""}
        ${istGeaendert(a) && !istGeschlossen(a) ? `<span class="tag tag-neu">Geändert</span>` : ""}
        ${a.englisch === "nein" ? `<span class="tag tag-schlecht">Kein Englisch</span>` : ""}
        ${a.visum === "working_holiday_nötig" ? `<span class="tag">Working Holiday</span>` : ""}
      </div>
      ${b.notiz ? `<p class="org">„${esc(b.notiz.slice(0, 90))}${b.notiz.length > 90 ? "…" : ""}“</p>` : ""}
      ${a.ausschluss.length ? `<p class="ausschluss-hinweis">Ausgeschlossen: ${esc(a.ausschluss.join(", "))}</p>` : ""}
      <div class="karte-fuss">
        <span class="passung"><b>${a.passung}</b><small>Passung</small></span>
        ${b.rating != null ? `<span class="mein-rating">Du: ${b.rating}/10</span>` : ""}
      </div>
    </div>
    <button class="karte-oeffnen" data-aktion="oeffnen" data-id="${a.id}" aria-label="${esc(a.titel)} öffnen"></button>
  </article>`;
}

function renderFavoriten() {
  const liste = S.angebote.filter((a) => bew(a.id).liked)
    .sort((x, y) => (bew(y.id).rating ?? -1) - (bew(x.id).rating ?? -1) || y.passung - x.passung);
  return `
    <h1 class="seitentitel">Gemerkt</h1>
    <p class="seitentext">Alles, was du mit dem Herz markiert hast – deine besten Bewertungen zuerst.</p>
    ${liste.length ? `<p><button class="knopf knopf-haupt" data-aktion="favoriten-durchgehen">Gemerkte durchgehen</button></p>
       <div class="karten">${liste.map(renderKarte).join("")}</div>`
      : `<div class="leer"><h2>Noch nichts gemerkt</h2>
           <p>Tippe beim Durchgehen auf das Herz oder drücke <kbd>H</kbd>, dann landet das Angebot hier.</p>
           <p><button class="knopf knopf-haupt" data-aktion="durchgehen">Angebote durchgehen</button></p></div>`}`;
}

function renderQuellen() {
  const gruppen = {};
  for (const q of S.quellen) ((gruppen[q.bereich] ||= {})[q.abschnitt] ||= []).push(q);
  const zeile = (titel, wert) => wert ? `<div><dt>${titel}</dt><dd>${esc(wert)}</dd></div>` : "";
  return `
    <h1 class="seitentitel">Quellen</h1>
    ${Object.keys(S.zaehlung || {}).length ? `
      <h2 class="quellen-bereich">Automatisch gesammelt</h2>
      <p class="seitentext">Echte Zahlen aus dem letzten Lauf der Sammler: alles, was die Suche geliefert hat, was den Vorfilter überstanden hat und was Claude als relevant eingestuft hat.</p>
      <div class="quellen-liste">
        ${Object.entries(S.zaehlung).map(([quelle, z]) => {
          const relevant = S.angebote.filter((a) => a.id.startsWith(`${quelle}-`)).length;
          return `<div class="quelle"><h4>${esc(quelle)}</h4>
            <dl class="quelle-fakten">
              <div><dt>Gesammelt</dt><dd>${z.roh}</dd></div>
              <div><dt>Nach Vorfilter</dt><dd>${z.kandidaten}</dd></div>
              <div><dt>Relevant (Claude)</dt><dd>${relevant}</dd></div>
              <div><dt>Abgerufen</dt><dd>${esc(z.abgerufen.replace("T", " ").slice(0, 16))}</dd></div>
              ${z.offen != null ? `<div><dt>Letzter Lauf</dt><dd>${z.offen} offen · ${z.neu} neu · ${z.geaendert} geändert · ${z.geschlossen} geschlossen${z.abruf_fehler ? ` · ${z.abruf_fehler} Abruffehler` : ""}</dd></div>` : ""}
              <div><dt>Aussortiert</dt><dd>${esc(Object.entries(z.ausgeschlossen).map(([g, n]) => `${g}: ${n}`).join(", ") || "–")}</dd></div>
            </dl></div>`;
        }).join("")}
      </div>` : ""}
    <h2 class="quellen-bereich">Recherchierte Quellen</h2>
    <p class="seitentext">${S.quellen.length} Quellen aus der Recherche (docs/recherche/). Mengen sind Schätzungen, „passend“ heißt: Zeitraum, Dauer, Gebühr und Visum passen grob.</p>
    ${Object.entries(gruppen).map(([bereich, abschnitte]) => `
      <h2 class="quellen-bereich">${esc(bereich)}</h2>
      ${Object.entries(abschnitte).map(([abschnitt, liste]) => `
        <h3 class="quellen-abschnitt">${esc(abschnitt)}</h3>
        <div class="quellen-liste">
          ${liste.map((q) => `
            <div class="quelle">
              <h4>${q.url ? `<a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(q.name)}</a>` : esc(q.name)}</h4>
              ${q.fokus ? `<p>${esc(q.fokus)}</p>` : ""}
              <dl class="quelle-fakten">
                ${zeile("Angebote", q.gesamt)}${zeile("Passend", q.passend)}${zeile("Kosten", q.kosten)}
                ${zeile("Zugriff", q.zugriff)}${zeile("Einschätzung", q.passung)}
              </dl>
            </div>`).join("")}
        </div>`).join("")}`).join("")}`;
}

// ---------- Durchgehen ----------
function starteDurchgehen(modus, liste, index = 0) {
  if (!liste.length) { alert("Keine Angebote für die aktuellen Filter."); return; }
  S.dg = { modus, liste, index, bild: 0 };
  document.body.style.overflow = "hidden";
  renderDurchgehen();
  document.getElementById("durchgehen").scrollTop = 0;
}

function zufallsId(ausser = []) {
  const pool = gefiltert().map((a) => a.id);
  const frisch = pool.filter((id) => !ausser.includes(id));
  const auswahl = frisch.length ? frisch : pool;
  return auswahl[Math.floor(Math.random() * auswahl.length)];
}

function schritt(richtung) {
  const dg = S.dg;
  if (dg.modus === "zufall" && richtung > 0 && dg.index === dg.liste.length - 1) {
    const id = zufallsId(dg.liste.slice(-10));
    if (id) dg.liste.push(id);
  }
  const neu = dg.index + richtung;
  if (neu < 0 || neu >= dg.liste.length) return;
  dg.index = neu; dg.bild = 0;
  renderDurchgehen();
  document.getElementById("durchgehen").scrollTop = 0;
}

function schliesseDurchgehen() {
  S.dg = null;
  document.getElementById("durchgehen").hidden = true;
  document.body.style.overflow = "";
  render();
}

function ring(wert) {
  const umfang = 2 * Math.PI * 42;
  return `<svg class="ring" viewBox="0 0 100 100" role="img" aria-label="Passung ${wert} von 100">
    <circle cx="50" cy="50" r="42" fill="none" stroke="var(--linie)" stroke-width="9"/>
    <circle cx="50" cy="50" r="42" fill="none" stroke="var(--tinte)" stroke-width="9" stroke-linecap="round"
      stroke-dasharray="${(umfang * wert) / 100} ${umfang}" transform="rotate(-90 50 50)"/>
    <text x="50" y="61" text-anchor="middle">${wert}</text></svg>`;
}

function renderDurchgehen() {
  const dg = S.dg;
  const el = document.getElementById("durchgehen");
  const a = nachId(dg.liste[dg.index]);
  const b = bew(a.id);
  const bilder = bilderVon(a);
  dg.bild = Math.min(dg.bild, Math.max(bilder.length - 1, 0));
  const bild = bilder[dg.bild];
  const modusText = { reihe: "Angebote durchgehen", zufall: "Zufällige Angebote", favoriten: "Gemerkte durchgehen" }[dg.modus];
  const gesamt = dg.modus === "zufall" ? null : dg.liste.length;
  const maps = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${a.ort}, ${a.land}`)}`;

  const beleg = (feld) => !a.zitate ? "" : a.zitate[feld] ? `<q class="beleg" title="Wörtlich aus der Anzeige">${esc(a.zitate[feld])}</q>`
    : `<small class="offen">nicht angegeben – vor Anfrage prüfen</small>`;
  const fakt = (titel, wert, zusatz = "", felder = []) => `<div><dt>${titel}</dt><dd>${esc(wert)}${zusatz ? `<small>${esc(zusatz)}</small>` : ""}${felder.map(beleg).join("")}</dd></div>`;
  const abschnitt = (titel, text, klasse = "", extra = "") => text ? `<div class="abschnitt ${klasse}"><h3>${titel}</h3><p>${esc(text)}</p>${extra}</div>` : "";
  const z = a.zustand;
  const zustandText = !z ? "" : `<div class="vorlaeufig zustand ${istGeschlossen(a) ? "geschlossen" : ""}">
      ${istGeschlossen(a) ? `<b>Geschlossen</b>${z.geschlossen_grund ? ` (${esc(z.geschlossen_grund)})` : ""}. ` : istNeu(a) ? `<b>Neu</b> seit ${datumKurz(z.erstmals_gesehen)}. ` : ""}
      Erstmals gesehen ${datumKurz(z.erstmals_gesehen)}, zuletzt geprüft ${datumKurz(z.zuletzt_gesehen)}${a.abgerufen ? `, Anzeige abgerufen ${datumKurz(a.abgerufen)}` : ""}.
      ${(z.aenderungen || []).length ? `<ul>${z.aenderungen.map((x) => `<li>${datumKurz(x.datum)}: ${esc(x.feld)} „${esc(x.alt || "–")}“ → „${esc(x.neu || "–")}“</li>`).join("")}</ul>` : ""}
      ${(a.auch_bei || []).length ? `<div>Auch bei: ${a.auch_bei.map((u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(new URL(u).hostname)}</a>`).join(", ")}</div>` : ""}
    </div>`;

  const kriterien = Object.entries(S.kernkriterien).map(([k, info]) => {
    const w = a.kriterien?.[k];
    if (w == null) return "";
    return `<div class="kriterium ${info.gewicht >= 3 ? "wichtig" : ""}" title="${esc(info.frage)} (Gewicht ${info.gewicht})">
      <span>${KRITERIUM[k] || schoen(k)}</span><span class="balken"><span style="width:${w * 10}%"></span></span><b>${w}</b></div>`;
  }).join("");

  el.hidden = false;
  el.innerHTML = `
    <div class="dg-leiste">
      <button class="knopf knopf-klein" data-aktion="schliessen">Zur Übersicht</button>
      <span class="dg-modus">${modusText}</span>
      ${gesamt ? `<span class="dg-balken" aria-hidden="true"><span style="width:${((dg.index + 1) / gesamt) * 100}%"></span></span>
                  <span class="dg-zaehler">${dg.index + 1} von ${gesamt}</span>` : `<span class="dg-balken" aria-hidden="true"></span>`}
    </div>
    <div class="dg-raster" style="--farbe:${farbe(a.kategorie)}">
      <article>
        <div class="galerie-haupt">
          ${bildOderPlatzhalter(a, bild)}
          ${bild ? `<span class="galerie-quelle">Bild: ${esc(bild.quelle)}</span>` : ""}
        </div>
        ${bilder.length > 1 ? `<div class="galerie-leiste">${bilder.map((x, i) => `
          <button data-aktion="bild" data-wert="${i}" aria-current="${i === dg.bild}" aria-label="Bild ${i + 1}">
            <img src="${esc(x.url)}" data-url="${esc(x.url)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="bildFehler(this)" onload="bildPruefen(this)"></button>`).join("")}</div>` : ""}

        <header class="dg-titel">
          <p class="ortzeile">${esc(a.ort)}</p>
          <h2>${esc(a.titel)}</h2>
          <p class="org">${esc(a.organisation)}, ${esc(a.land)}${a.region ? ` (${esc(a.region)})` : ""}</p>
          <div class="dg-labels">
            <span class="kat-label">${katEmoji(a.kategorie)} ${esc(katName(a.kategorie))}${a.unterpunkt ? `: ${esc(schoen(a.unterpunkt))}` : ""}</span>
            ${a.sparte === "lead" ? `<span class="kat-label lead-label">Lead – direkt anfragen</span>` : ""}
            ${(a.tags || []).map((t) => `<span class="tag">${esc(S.kategorien[t] ? katName(t) : schoen(t))}</span>`).join("")}
          </div>
        </header>

        ${kostetGeld(a) ? `<div class="warnband statisch" style="margin-top:18px">⚠ ${esc(gebuehrText(a))}. ${esc(a.bezahlung_text || "")}</div>` : ""}
        ${a.ausschluss.length ? `<div class="vorlaeufig" style="border-color:var(--herz);color:var(--herz)">Durch deine harten Kriterien ausgeschlossen: ${esc(a.ausschluss.join(", "))}</div>` : ""}
        ${a.status === "vorläufig" ? `<div class="vorlaeufig">Angaben vorläufig: aus der ersten Recherche, noch nicht beim Anbieter bestätigt. Vor einer Anfrage auf der Website prüfen.</div>` : ""}
        ${a.status === "automatisch" ? `<div class="vorlaeufig">Automatisch gesammelt aus ${esc(a.quelle)}${a.veroeffentlicht ? `, veröffentlicht ${esc(a.veroeffentlicht)}` : ""}${a.frist ? `, Bewerbungsfrist ${esc(a.frist)}` : ""}. Originaltitel: „${esc(a.originaltitel)}“. Zusammenfassung und Bewertung stammen von Claude – die Originalanzeige ist maßgeblich; belegte Angaben stehen als Zitat unter dem jeweiligen Fakt.</div>` : ""}
        ${zustandText}

        <dl class="fakten">
          ${fakt("Dauer", dauerText(a), a.dauer_text, ["dauer"])}
          ${fakt("Bezahlung", BEZAHLUNG[a.bezahlung] || a.bezahlung, a.bezahlung_text, ["bezahlung", "gebuehr"])}
          ${fakt("Unterkunft", UNTERKUNFT[a.unterkunft] || a.unterkunft, VERPFLEGUNG[a.verpflegung] ?? "", ["unterkunft", "verpflegung"])}
          ${fakt("Sprache", ENGLISCH[a.englisch] || a.englisch, "", ["englisch"])}
          ${fakt("Visum", VISUM[a.visum] || a.visum, [a.visum_regel_text, a.visum_text].filter(Boolean).join(" "))}
          ${fakt("Art", SPARTE[a.sparte] || a.sparte)}
        </dl>

        <div class="abschnitte">
          ${abschnitt("Was du dort machst", a.beschreibung)}
          ${abschnitt("Was du lernst", a.lernen)}
          ${abschnitt("Wo deine Technik hilft", a.beitrag)}
          ${abschnitt("Voraussetzungen", a.voraussetzungen, "", beleg("voraussetzungen"))}
          ${abschnitt("Haken", a.haken, "haken")}
          ${a.website_beschreibung ? `<div class="abschnitt"><h3>Von der Website</h3><p class="zitat">${esc(a.website_beschreibung)}</p></div>` : ""}
          ${abschnitt("Über den Ort", a.ort_info)}
        </div>

        <div class="links">
          ${a.website ? `<a class="knopf knopf-haupt knopf-klein" href="${esc(a.website)}" target="_blank" rel="noopener">Website öffnen</a>` : ""}
          ${a.angebot_url && a.angebot_url !== a.website ? `<a class="knopf knopf-klein" href="${esc(a.angebot_url)}" target="_blank" rel="noopener">Zum Angebot</a>` : ""}
          <a class="knopf knopf-klein" href="${maps}" target="_blank" rel="noopener">Auf der Karte</a>
          ${a.ort_link ? `<a class="knopf knopf-klein" href="${esc(a.ort_link)}" target="_blank" rel="noopener">Ort auf Wikipedia</a>` : ""}
        </div>
      </article>

      <aside class="panel">
        <div class="panel-block">
          <div class="ring-zeile">${ring(a.passung)}<p>${esc(a.warum || "")}</p></div>
          <div class="kriterien">${kriterien}</div>
        </div>
        <div class="panel-block">
          <h3>Wie gut gefällt es dir?</h3>
          <div class="rating" role="group" aria-label="Bewertung 1 bis 10">
            ${Array.from({ length: 10 }, (_, i) => i + 1).map((n) =>
              `<button data-aktion="rating" data-wert="${n}" aria-pressed="${b.rating === n}">${n}</button>`).join("")}
          </div>
          <div class="rating-skala"><span>gar nicht</span><span>unbedingt</span></div>
          <button class="knopf merken-knopf" data-aktion="like" data-id="${a.id}" aria-pressed="${!!b.liked}">
            ${HERZ} ${b.liked ? "Gemerkt" : "Merken"}</button>
          <textarea class="notiz" data-aktion="notiz" placeholder="Deine Notiz: Was reizt dich, was spricht dagegen, was willst du fragen?">${esc(b.notiz || "")}</textarea>
          <div class="gespeichert" id="gespeichert"></div>
        </div>
        <div class="dg-nav">
          <button class="knopf" data-aktion="zurueck" ${dg.index === 0 ? "disabled" : ""}>Vorheriges</button>
          <button class="knopf knopf-haupt" data-aktion="weiter"
            ${dg.modus !== "zufall" && dg.index === dg.liste.length - 1 ? "disabled" : ""}>${dg.modus === "zufall" ? "Nächstes zufällige" : "Nächstes"}</button>
        </div>
        <p class="tastenhilfe">Tasten: <kbd>1</kbd>–<kbd>9</kbd>, <kbd>0</kbd> = 10, <kbd>H</kbd> merken, <kbd>←</kbd> <kbd>→</kbd> blättern, <kbd>Esc</kbd> schließen</p>
      </aside>
    </div>`;
}

// ---------- Ereignisse ----------
function bildFehler(img) {
  S.kaputt.add(img.dataset.url);
  const btn = img.closest(".galerie-leiste button");
  if (btn) { btn.remove(); return; }
  if (S.dg && img.closest("#durchgehen")) { renderDurchgehen(); return; }
  img.outerHTML = `<div class="platzhalter-bild"></div>`;
}
window.bildFehler = bildFehler;
// Winzige Bilder (Icons, Tracking-Pixel) wie kaputte behandeln
window.bildPruefen = (img) => { if (img.naturalWidth < 200) bildFehler(img); };

async function toggleLike(id, knopf) {
  const neu = !bew(id).liked;
  await speichere(id, { liked: neu });
  if (S.dg) renderDurchgehen();
  if (!S.dg || aktuelleView() === "favoriten") render(); else {
    document.querySelectorAll(`.herz-knopf[data-id="${id}"]`).forEach((k) => k.setAttribute("aria-pressed", neu));
  }
  const ziel = S.dg ? document.querySelector(".merken-knopf") : knopf;
  ziel?.classList.add("puls");
}

document.addEventListener("click", async (e) => {
  const t = e.target.closest("[data-aktion]");
  if (!t || t.tagName === "SELECT" || t.tagName === "INPUT" || t.tagName === "TEXTAREA") return;
  const f = S.filter;
  switch (t.dataset.aktion) {
    case "kategorie": f.kategorie = t.dataset.wert || null; break;
    case "chip": {
      const liste = f[t.dataset.feld];
      const i = liste.indexOf(t.dataset.wert);
      i >= 0 ? liste.splice(i, 1) : liste.push(t.dataset.wert);
      break;
    }
    case "reset": S.filter = standardFilter(); break;
    case "durchgehen": {
      const liste = gefiltert();
      const ersterOffen = liste.findIndex((a) => bew(a.id).rating == null);
      starteDurchgehen("reihe", liste.map((a) => a.id), Math.max(ersterOffen, 0));
      return;
    }
    case "zufall": { const id = zufallsId(); if (id) starteDurchgehen("zufall", [id]); else starteDurchgehen("zufall", []); return; }
    case "favoriten-durchgehen":
      starteDurchgehen("favoriten", S.angebote.filter((a) => bew(a.id).liked).map((a) => a.id)); return;
    case "oeffnen": {
      const liste = aktuelleView() === "favoriten" ? S.angebote.filter((a) => bew(a.id).liked) : gefiltert();
      const ids = liste.map((a) => a.id);
      starteDurchgehen(aktuelleView() === "favoriten" ? "favoriten" : "reihe", ids, Math.max(ids.indexOf(t.dataset.id), 0));
      return;
    }
    case "like": e.stopPropagation(); await toggleLike(t.dataset.id, t); return;
    case "schliessen": schliesseDurchgehen(); return;
    case "weiter": schritt(1); return;
    case "zurueck": schritt(-1); return;
    case "bild": S.dg.bild = Number(t.dataset.wert); renderDurchgehen(); return;
    case "rating": await setzeRating(Number(t.dataset.wert)); return;
    default: return;
  }
  speichereFilter();
  render();
});

document.addEventListener("change", (e) => {
  const t = e.target;
  const aktion = t.dataset.aktion;
  if (aktion === "land" || aktion === "sort") S.filter[aktion] = t.value;
  else if (aktion === "nurUnbewertet" || aktion === "ausgeschlossene" || aktion === "geschlossene") S.filter[aktion] = t.checked;
  else return;
  speichereFilter();
  render();
});

let notizTimer;
document.addEventListener("input", (e) => {
  if (e.target.dataset.aktion !== "notiz" || !S.dg) return;
  const id = S.dg.liste[S.dg.index];
  const text = e.target.value;
  const status = document.getElementById("gespeichert");
  status.textContent = "Wird gespeichert …";
  clearTimeout(notizTimer);
  notizTimer = setTimeout(async () => {
    try { await speichere(id, { notiz: text }); status.textContent = "Notiz gespeichert"; }
    catch { status.textContent = "Notiz nicht gespeichert – läuft der Server noch?"; }
  }, 500);
});

async function setzeRating(n) {
  const id = S.dg.liste[S.dg.index];
  await speichere(id, { rating: bew(id).rating === n ? null : n });
  renderDurchgehen();
}

document.addEventListener("keydown", async (e) => {
  if (!S.dg || e.target.matches?.("textarea, input, select") || e.ctrlKey || e.metaKey || e.altKey) return;
  if (/^[0-9]$/.test(e.key)) { await setzeRating(e.key === "0" ? 10 : Number(e.key)); }
  else if (e.key === "h" || e.key === "H") { await toggleLike(S.dg.liste[S.dg.index]); }
  else if (e.key === "ArrowRight") schritt(1);
  else if (e.key === "ArrowLeft") schritt(-1);
  else if (e.key === "Escape") schliesseDurchgehen();
  else return;
  e.preventDefault();
});

window.addEventListener("hashchange", render);

lade().catch(() => {
  document.getElementById("inhalt").innerHTML = `<div class="leer" style="margin-top:40px">
    <h2>Daten konnten nicht geladen werden</h2>
    <p>Starte den Server mit <kbd>python app/server.py</kbd> und öffne dann <a href="http://localhost:8765">localhost:8765</a>.</p></div>`;
});
