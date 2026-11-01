// Spielt die Code-Knoten von W2 (Wächter) und W3 (Benachrichtigen) mit den echten Repo-Daten durch:  node n8n/simulation.js
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');
const lies = (datei) => JSON.parse(fs.readFileSync(path.join(repo, datei), 'utf8'));
const code = (wf, name) => lies('n8n/' + wf).nodes.find((n) => n.name === name).parameters.jsCode;
const konfig = (wf) => Object.fromEntries(lies('n8n/' + wf).nodes.find((n) => n.name === 'Konfiguration')
  .parameters.assignments.assignments.map((a) => [a.name, a.value]));
const fuehreAus = (js, input, ausgaben) => new Function('$input', '$', 'Buffer', js)(
  { all: () => input, first: () => input[0] }, (n) => ({ all: () => ausgaben[n], first: () => ausgaben[n][0] }), Buffer);

// W2 Wächter: echter Status, dann ein künstlich veralteter
const status = lies('daten/aufbereitet/status.json');
const w2 = (s) => fuehreAus(code('W2_waechter.json', 'Auffälligkeiten prüfen'), [{ json: s }], {})[0].json;
let r = w2(status);
console.log('W2 echter Status: warnen', r.warnen, '\n' + r.text);
r = w2({ ...status, letzter_sammellauf: '2026-01-01T00:00:00Z', unbewertet: 5, letzte_bewertung: null,
  quellen: { nav: { abgerufen: new Date().toISOString(), abruf_fehler: 0 } } });
console.log('W2 veraltet: warnen', r.warnen, 'anzahl', r.anzahl);
r = w2({ ...status, letzter_sammellauf: new Date().toISOString(), unbewertet: 0, letzte_bewertung_fehler: [],
  quellen: { nav: { abgerufen: new Date().toISOString(), abruf_fehler: 0 } } });
console.log('W2 alles gut: warnen', r.warnen);

// W3 Benachrichtigen: erster Lauf meldet, zweiter Lauf mit gleichem Stand meldet nichts
const ausgaben = { Konfiguration: [{ json: konfig('W3_benachrichtigen.json') }],
  'Treffer lesen': [{ json: lies('daten/aufbereitet/treffer.json') }] };
const w3 = (alt) => fuehreAus(code('W3_benachrichtigen.json', 'Auswählen und Text bauen'), [{ json: alt }], ausgaben)[0].json;
const erster = w3({ error: { message: '404' } });
console.log('W3 erster Lauf: senden', erster.senden, 'anzahl', erster.anzahl);
const zweiter = w3({ sha: 'x', content: erster.content_b64 });
console.log('W3 zweiter Lauf: senden', zweiter.senden, 'anzahl', zweiter.anzahl);
