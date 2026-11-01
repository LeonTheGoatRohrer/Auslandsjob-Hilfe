"""Texas A&M Natural Resources Job Board – nur internationale Stellen (USA ist ohne Visum nicht machbar).

    python -m sammler.tamu

Die Suchliste enthält alle internationalen Stellen (vollstaendig=True).
"""

import re

from sammler.gemeinsam import AbrufFehler, hole, speichere, text_aus_html

BASIS_URL = "https://jobs.rwfm.tamu.edu"
FELDER = ["Application Deadline", "Published", "Starting Date", "Ending Date", "Hours per Week", "Salary",
          "Education Required", "Experience Required", "Location"]
# Ländernamen im Ortsfeld → ISO-Code; US-Bundesstaaten werden als USA erkannt (Visum dort nicht machbar)
LAENDER = {
    "South Africa": "ZA", "Costa Rica": "CR", "Peru": "PE", "Belize": "BZ", "Australia": "AU", "Panama": "PA",
    "Malaysia": "MY", "Mexico": "MX", "México": "MX", "Singapore": "SG", "Nigeria": "NG", "Nicaragua": "NI",
    "Kenya": "KE", "Tanzania": "TZ", "Madagascar": "MG", "Ecuador": "EC", "Brazil": "BR", "Namibia": "NA",
    "Indonesia": "ID", "Philippines": "PH", "Thailand": "TH", "Canada": "CA", "New Zealand": "NZ", "Norway": "NO",
    "Iceland": "IS", "Greece": "GR", "Spain": "ES", "Portugal": "PT", "Chile": "CL", "Argentina": "AR",
    "Colombia": "CO", "Bolivia": "BO", "Honduras": "HN", "Guatemala": "GT", "Mozambique": "MZ", "Seychelles": "SC",
    "Fiji": "FJ", "Japan": "JP", "United Kingdom": "GB", "Scotland": "GB", "Germany": "DE", "France": "FR",
    "Italy": "IT", "Botswana": "BW", "Zambia": "ZM", "Uganda": "UG", "Ghana": "GH", "India": "IN", "Nepal": "NP",
    "Papua New Guinea": "PG", "Galapagos": "EC", "United States": "US", "Puerto Rico": "US", "Hawaii": "US",
    "Alaska": "US", "California": "US", "Texas": "US", "Florida": "US", "Utah": "US", "Wyoming": "US",
    "New Mexico": "US", "Washington": "US", "Illinois": "US", "Indiana": "US", "Mississippi": "US", "New York": "US",
    "Arkansas": "US", "North Carolina": "US", "Colorado": "US", "Oregon": "US", "Montana": "US", "Arizona": "US",
}


def sammle():
    ids, seite = [], 1
    while True:
        liste = hole(f"{BASIS_URL}/search/", params={"location-type": "0", "PageSize": "50", "PageNum": seite}).text
        neu = [i for i in dict.fromkeys(re.findall(r"/view-job/\?id=(\d+)", liste)) if i not in ids]
        if not neu:
            break
        ids += neu
        seite += 1
    print(f"  {len(ids)} internationale Stellen")
    angebote, fehler = [], {}
    for i in ids:
        try:
            angebote.append(umwandeln(i, text_aus_html(hole(f"{BASIS_URL}/view-job/?id={i}", pause=3).text)))
        except AbrufFehler as f:
            fehler[f"tamu:{i}"] = str(f)
            print(f"  {i}: {f}")
    speichere("tamu", angebote, vollstaendig=True, fehler=fehler)


def land_aus_ort(ort):
    for name, code in LAENDER.items():
        if re.search(rf"\b{re.escape(name)}\b", ort):
            return (name if code != "US" or name == "United States" else "USA"), code
    return ort.split(",")[-1].strip(" )"), ""


def umwandeln(job_id, text):
    def feld(name):
        m = re.search(rf"{name}:\s*\n+\s*(.+)", text)
        return m.group(1).strip() if m else ""
    titel = text.split("|")[0].strip()
    org = re.search(re.escape(titel) + r"\s*\n+\s*(.+?)\s*\n", text[text.find("SPONSORS AND PARTNERS"):])
    beschreibung = text.split("\n Description", 1)[-1].split("\n View Location", 1)[0].strip()
    ort = feld("Location")
    land, land_code = land_aus_ort(ort)
    return {
        "quelle": "tamu", "quelle_id": job_id, "url": f"{BASIS_URL}/view-job/?id={job_id}",
        "titel": titel, "organisation": re.sub(r"\s*\(.*", "", org.group(1)) if org else "",
        "ort": ort, "region": "", "land": land, "land_code": land_code,
        "beschreibung": beschreibung[:4000],
        "veroeffentlicht": feld("Published"), "frist": feld("Application Deadline"),
        "extra": {f.lower().replace(" ", "_"): feld(f) for f in FELDER[2:8]},
    }


if __name__ == "__main__":
    sammle()
