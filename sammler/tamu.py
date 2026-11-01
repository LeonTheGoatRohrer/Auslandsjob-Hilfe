"""Texas A&M Natural Resources Job Board – nur internationale Stellen (USA ist ohne Visum nicht machbar).

    python -m sammler.tamu
"""

import re

from sammler.gemeinsam import hole, speichere, text_aus_html

BASIS_URL = "https://jobs.rwfm.tamu.edu"
FELDER = ["Application Deadline", "Published", "Starting Date", "Ending Date", "Hours per Week", "Salary",
          "Education Required", "Experience Required", "Location"]


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
    angebote = []
    for i in ids:
        try:
            angebote.append(umwandeln(i, text_aus_html(hole(f"{BASIS_URL}/view-job/?id={i}", pause=3).text)))
        except Exception as fehler:
            print(f"  {i}: {fehler}")
    return angebote


def umwandeln(job_id, text):
    def feld(name):
        m = re.search(rf"{name}:\s*\n+\s*(.+)", text)
        return m.group(1).strip() if m else ""
    titel = text.split("|")[0].strip()
    org = re.search(re.escape(titel) + r"\s*\n+\s*(.+?)\s*\n", text[text.find("SPONSORS AND PARTNERS"):])
    beschreibung = text.split("\n Description", 1)[-1].split("\n View Location", 1)[0].strip()
    ort = feld("Location")
    return {
        "quelle": "tamu", "quelle_id": job_id, "url": f"{BASIS_URL}/view-job/?id={job_id}",
        "titel": titel, "organisation": re.sub(r"\s*\(.*", "", org.group(1)) if org else "",
        "ort": ort, "region": "", "land": ort.split(",")[-1].strip(), "land_code": "",
        "beschreibung": beschreibung[:4000],
        "veroeffentlicht": feld("Published"), "frist": feld("Application Deadline"),
        "extra": {f.lower().replace(" ", "_"): feld(f) for f in FELDER[2:8]},
    }


if __name__ == "__main__":
    speichere("tamu", sammle())
