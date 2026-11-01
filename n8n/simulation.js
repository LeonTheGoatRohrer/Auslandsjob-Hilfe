// Simuliert die Code-Knoten von W2/W3 mit den echten Repo-Daten und einer gefälschten Claude-Antwort:  node n8n/simulation.js
const fs = require('fs'); const path = require('path');
const repo = path.resolve(__dirname, '..');
const w2 = JSON.parse(fs.readFileSync(repo + '/n8n/W2_bewerten.json', 'utf8'));
const js = n => w2.nodes.find(x => x.name === n).parameters.jsCode;
const b64 = p => Buffer.from(fs.readFileSync(p)).toString('base64');
const cfg = Object.fromEntries(w2.nodes.find(n => n.name === 'Konfiguration').parameters.assignments.assignments.map(a => [a.name, a.value]));
const kand = JSON.parse(fs.readFileSync(repo + '/daten/aufbereitet/kandidaten.json', 'utf8'));
const outputs = {
  'Konfiguration': [{ json: cfg }],
  'Kandidaten lesen': [{ json: kand }],
  'Profil lesen': [{ json: { data: fs.readFileSync(repo + '/config/profil.yaml', 'utf8') } }],
  'Prompt lesen': [{ json: { data: fs.readFileSync(repo + '/config/prompt_bewertung.md', 'utf8') } }],
  'Webhook': [{ json: { body: { lauf_id: '123' } } }],
};
const run = (name, input) => new Function('$input', '$', 'Buffer', js(name))(
  { all: () => input, first: () => input[0] }, n => ({ all: () => outputs[n], first: () => outputs[n][0] }), Buffer);

outputs['Cache-Dateien bestimmen'] = run('Cache-Dateien bestimmen', []);
console.log('Quellen:', outputs['Cache-Dateien bestimmen'].map(i => i.json.quelle));
const cacheItems = outputs['Cache-Dateien bestimmen'].map(i => {
  const p = `${repo}/daten/aufbereitet/llm_cache/${i.json.quelle}.json`;
  return fs.existsSync(p) ? { json: { name: i.json.quelle + '.json', sha: 'sha-' + i.json.quelle, content: b64(p) } } : { json: { error: { message: '404' } } };
});
outputs['Aufträge bauen'] = run('Aufträge bauen', cacheItems);
const a0 = outputs['Aufträge bauen'][0].json;
console.log('Aufträge:', outputs['Aufträge bauen'].length, 'offen gesamt:', a0.offen_gesamt, 'rest:', a0.rest, 'leer:', !!a0.leer);
console.log('Prompt enthält kategorien:', /bezahlte_jobs \| extrem_mission/.test(a0.prompt), 'Länge', a0.prompt.length);
// gefälschte Claude-Antwort: für jeden Kandidaten im ersten Stapel ein Objekt, ein Zitat echt, eins erfunden
const antworten = outputs['Aufträge bauen'].map((auf, idx) => {
  const liste = Object.values(auf.json.kandidaten).map(k => ({ id: k.key, relevant: true, titel: 'T', kategorie: 'handwerk', unterpunkt: 'holz', tags: [],
    ort: k.ort, region: k.region, ort_wiki: null, dauer_wochen: null, dauer_text: 'nicht angegeben', bezahlung: 'unklar', bezahlung_text: 'nicht angegeben',
    gebuehr_eur: null, unterkunft: 'unklar', verpflegung: 'vielleicht', englisch: 'ja',
    zitate: { dauer: null, bezahlung: k.beschreibung.slice(10, 40), gebuehr: null, unterkunft: 'DIESES ZITAT STEHT NICHT IM TEXT', verpflegung: null, englisch: null, voraussetzungen: null },
    beschreibung: '…', lernen: '…', beitrag: '…', haken: '…', voraussetzungen: 'nicht angegeben',
    kriterien: { außergewöhnlichkeit: 5 }, warum: '…' }));
  if (idx === 1) return { json: { error: { message: 'timeout' } } };
  return { json: { content: [{ type: 'text', text: '```json\n' + JSON.stringify(liste) + '\n```' }], usage: { input_tokens: 9000, output_tokens: 2500 } } };
});
outputs['Antworten prüfen'] = run('Antworten prüfen', antworten);
for (const it of outputs['Antworten prüfen']) {
  const eintraege = JSON.parse(Buffer.from(it.json.content_b64, 'base64').toString('utf8'));
  const neu = Object.values(eintraege).filter(e => e.bewertet_am);
  console.log(it.json.quelle, 'sha', it.json.sha, 'einträge', Object.keys(eintraege).length, 'neu', neu.length,
    'beispiel:', neu[0] && { verpflegung: neu[0].verpflegung, zitate_ungueltig: neu[0].zitate_ungueltig, bezahlung_zitat: neu[0].zitate.bezahlung });
  console.log('  zusammenfassung', { bewertet: it.json.bewertet, verworfen: it.json.verworfen, fehler: it.json.fehler, kosten_usd: it.json.kosten_usd, rest: it.json.rest });
}
outputs['Kostenprotokoll ergänzen'] = run('Kostenprotokoll ergänzen', [{ json: { error: { message: '404' } } }]);
console.log('Kosten:', JSON.parse(Buffer.from(outputs['Kostenprotokoll ergänzen'][0].json.content_b64, 'base64').toString('utf8')));
// W3
const w3 = JSON.parse(fs.readFileSync(repo + '/n8n/W3_benachrichtigen.json', 'utf8'));
const js3 = w3.nodes.find(x => x.name === 'Auswählen und Text bauen').parameters.jsCode;
const cfg3 = Object.fromEntries(w3.nodes.find(n => n.name === 'Konfiguration').parameters.assignments.assignments.map(a => [a.name, a.value]));
const treffer = JSON.parse(fs.readFileSync(repo + '/daten/aufbereitet/treffer.json', 'utf8'));
const o3 = { 'Konfiguration': [{ json: cfg3 }], 'Treffer lesen': [{ json: treffer }] };
const run3 = input => new Function('$input', '$', 'Buffer', js3)({ all: () => input, first: () => input[0] }, n => ({ all: () => o3[n], first: () => o3[n][0] }), Buffer)[0].json;
const r1 = run3([{ json: { error: { message: '404' } } }]);
console.log('W3 erster Lauf: senden', r1.senden, 'anzahl', r1.anzahl, '\n' + r1.text.slice(0, 600));
const r2 = run3([{ json: { sha: 'x', content: r1.content_b64 } }]);
console.log('W3 zweiter Lauf: senden', r2.senden, 'anzahl', r2.anzahl);
