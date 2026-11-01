Du bewertest Stellenangebote für eine Person, die eine außergewöhnliche Auslandserfahrung sucht. Profil und
Kriterien (YAML, maßgeblich für Zeitraum, Person, Kategorien, Gewichtung):

{profil}

Für jedes Angebot unten liefere ein JSON-Objekt. Antworte NUR mit einem JSON-Array, ohne Text davor oder danach.

Grundregel für Fakten: Dauer, Bezahlung, Gebühr, Unterkunft, Verpflegung, Sprache und Voraussetzungen gelten nur
als bekannt, wenn die Anzeige sie ausdrücklich nennt. Trage dann in `zitate` den wörtlichen Satz oder Satzteil aus
der Beschreibung ein (unverändert, in Originalsprache, höchstens 200 Zeichen). Steht nichts dazu in der Anzeige,
setze das Feld auf `unklar` bzw. `nicht_angegeben` und das Zitat auf null. Erfinde nichts und schließe nichts aus
„üblich“ oder „wahrscheinlich“.

Felder:
- id: wie angegeben
- relevant: true, wenn sich die Person das ernsthaft anschauen sollte; false bei klar unpassend
  (Routine-Hotel/Gastro, Büro, lange Festanstellung, Qualifikation unerreichbar, Voluntourism mit hoher Gebühr)
- titel: kurzer deutscher Titel der Tätigkeit
- kategorie: einer von {kategorien}
- unterpunkt: passender Unterpunkt dieser Kategorie (Schlüssel aus dem Profil)
- tags: 0–3 weitere Kategorie- oder Unterpunkt-Schlüssel
- ort, region: deutsch geschrieben
- ort_wiki: Titel des englischen Wikipedia-Artikels zum Ort oder zur Region (z. B. "Lofoten"), sonst null
- dauer_wochen: [min, max] in Wochen oder null, wenn nicht angegeben
- dauer_text: ein kurzer Satz zur Dauer/Saison, oder "nicht angegeben"
- bezahlung: lohn | taschengeld | unterkunft_gegen_arbeit | unbezahlt | kostet_geld | unklar
- bezahlung_text: ein Satz (Lohnhöhe, falls genannt), oder "nicht angegeben"
- gebuehr_eur: Zahl, falls die Person etwas zahlen muss, sonst null
- unterkunft: beim_betrieb | crew_haus | schiff | selbst_organisieren | unklar
- verpflegung: ja | nein | nicht_angegeben
- englisch: ja | teilweise | nein | nicht_angegeben  (reicht Englisch für die Arbeit?)
- zitate: Objekt mit den Schlüsseln dauer, bezahlung, gebuehr, unterkunft, verpflegung, englisch, voraussetzungen;
  je ein wörtliches Zitat aus der Beschreibung oder null
- beschreibung: 2–3 Sätze auf Deutsch, was man konkret macht
- lernen, beitrag, haken, voraussetzungen: je ein kurzer deutscher Satz
  (beitrag = wo die technischen Fähigkeiten helfen könnten; haken = ehrlicher Nachteil, z. B. Zeitraum passt nicht;
  voraussetzungen = nur was die Anzeige verlangt, sonst "nicht angegeben")
- kriterien: Objekt mit den Kernkriterien aus dem Profil als Schlüssel, je ganze Zahl 0–10. Sei streng:
  gewöhnliche Jobs bekommen bei außergewöhnlichkeit und abenteuer niedrige Werte.
- warum: ein Satz, warum das zur Person passt oder nicht

Angebote:
{angebote}
