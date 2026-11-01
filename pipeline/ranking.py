"""Filtern und Bewerten der Angebote gegen config/profil.yaml und config/visa.yaml."""

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config"

EU_EWR_CH = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV",
             "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "CH"}

# Welche Visa-Regel für welche Art der Bezahlung gilt
REGELFELD = {"lohn": "bezahlt", "taschengeld": "bezahlt", "unterkunft_gegen_arbeit": "gegen_unterkunft",
             "unklar": "gegen_unterkunft", "unbezahlt": "volunteering", "kostet_geld": "volunteering"}
FELDTEXT = {"bezahlt": "Bezahlte Arbeit", "gegen_unterkunft": "Arbeit gegen Unterkunft", "volunteering": "Volunteering"}
REGELTEXT = {"erlaubt": "erlaubt", "nur_mit_working_holiday": "nur mit Working-Holiday-Visum",
             "nur_mit_visum": "nur mit eigenem Visum (meist mit Sponsor)",
             "nur_gemeinnuetzig": "nur bei gemeinnützigen Organisationen, mit Auflagen",
             "nur_mit_permit": "nur mit lokaler Arbeitserlaubnis", "verboten": "nicht erlaubt",
             "unsicher": "rechtlich unklar"}
VISUM_STATUS = {"erlaubt": "machbar", "nur_mit_working_holiday": "working_holiday_nötig", "verboten": "verboten"}


def lade_profil():
    return yaml.safe_load((CONFIG / "profil.yaml").read_text(encoding="utf-8"))


def lade_visa():
    regeln = {}
    for r in yaml.safe_load((CONFIG / "visa.yaml").read_text(encoding="utf-8"))["regeln"]:
        for land in (r["land"] if isinstance(r["land"], list) else [r["land"]]):
            regeln[land] = r
    for land in EU_EWR_CH:
        regeln.setdefault(land, regeln["EU_EWR_CH"])
    return regeln


def visum_pruefen(angebot, visa):
    """Setzt visum/visum_regel_text aus den Visa-Regeln, falls das Land bekannt ist."""
    angebot.setdefault("visum", "unklar")
    regel = visa.get(angebot.get("land_code"))
    feld = REGELFELD.get(angebot.get("bezahlung"))
    if not regel or not feld or feld not in regel:
        return
    wert = regel[feld]
    angebot["visum"] = VISUM_STATUS.get(wert, "mit_auflagen" if wert != "unsicher" else "unklar")
    text = f"{FELDTEXT[feld]}: {REGELTEXT[wert]}."
    wh = regel.get("working_holiday") or {}
    if wert == "nur_mit_working_holiday" and wh.get("verfuegbar"):
        kosten = f"ca. {wh['kosten_eur']} €" if "kosten_eur" in wh else "Kosten prüfen"
        mal = "nur einmal im Leben" if wh.get("nutzbar_mal") == 1 else f"{wh.get('nutzbar_mal', '?')}× im Leben"
        text += f" Working Holiday: {kosten}, {mal}."
    angebot["visum_regel_text"] = text


def ausschlussgruende(angebot, profil):
    """Harte Kriterien: liefert eine Liste von Gründen, leer = passt."""
    gruende = []
    gebuehr = angebot.get("gebuehr_eur")
    if gebuehr is not None and gebuehr > profil["max_programmgebühr_eur"]:
        gruende.append(f"Gebühr ca. {gebuehr} € (Grenze {profil['max_programmgebühr_eur']} €)")

    dauer = angebot.get("dauer_wochen")
    if dauer:
        moeglich = profil["zeitraum"]["dauer_wochen"]["möglich"]
        maximal = profil["zeitraum"]["dauer_wochen"]["max"]
        if dauer[1] < moeglich[0]:
            gruende.append(f"zu kurz (max. {dauer[1]} Wochen)")
        if dauer[0] > maximal:
            gruende.append(f"zu lang (mind. {dauer[0]} Wochen)")

    if angebot.get("visum") == "verboten":
        gruende.append("Visum: so in diesem Land nicht legal möglich")
    return gruende


def passung(angebot, profil):
    """Gewichteter Mittelwert der Kernkriterien (0–10) als Wert 0–100."""
    werte = angebot.get("kriterien", {})
    summe = gewichte = 0
    for name, info in profil["kernkriterien"].items():
        if name in werte:
            summe += werte[name] * info["gewicht"]
            gewichte += info["gewicht"]
    return round(summe / gewichte * 10) if gewichte else 0


def bewerte(angebote, profil):
    visa = lade_visa()
    for a in angebote:
        visum_pruefen(a, visa)
        a["passung"] = passung(a, profil)
        a["ausschluss"] = ausschlussgruende(a, profil)
    angebote.sort(key=lambda a: a["passung"], reverse=True)
    return angebote
