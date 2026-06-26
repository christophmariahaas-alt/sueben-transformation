"""
logic.py – Berechnungslogik: Streak, Plateau-Erkennung, gleitender Durchschnitt.
"""

from datetime import date, timedelta
from typing import Optional
import config


def berechne_tag_nummer(heute: date = None, startdatum: date = None) -> int:
    """Wie viele Tage seit Startdatum (inkl. heute)? Min. 1, Max. 90."""
    if heute is None:
        heute = date.today()
    if startdatum is None:
        return 1
    delta = (heute - startdatum).days + 1
    return max(1, min(delta, config.CHALLENGE_TAGE))


def berechne_streak(logs: list[dict]) -> int:
    """
    Berechnet die aktuelle ununterbrochene Tages-Streak
    (aufeinanderfolgende Tage mit gespeichertem Eintrag bis heute).
    """
    if not logs:
        return 0
    log_dates = {l["log_date"] for l in logs}
    streak = 0
    check = date.today()
    while check.isoformat() in log_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


def gleitender_durchschnitt(werte: list[float], fenster: int = 7) -> list[Optional[float]]:
    """Berechnet einen einfachen gleitenden Durchschnitt."""
    result: list[Optional[float]] = []
    for i in range(len(werte)):
        if i < fenster - 1:
            result.append(None)
        else:
            fenster_werte = werte[i - fenster + 1 : i + 1]
            result.append(round(sum(fenster_werte) / fenster, 2))
    return result


def pruefe_plateau(gewichtsverlauf: list[dict]) -> bool:
    """
    Plateau-Erkennung nach Sjard Roscher:
    - Mindestens PLATEAU_MIN_TAGE Einträge
    - Gleitender 7-Tage-Schnitt heute vs. vor 14 Tagen < 0,2 kg Unterschied
    Gibt True zurück, wenn Stagnation erkannt wurde.
    """
    if len(gewichtsverlauf) < config.PLATEAU_MIN_TAGE:
        return False

    gewichte = [r["gewicht_kg"] for r in gewichtsverlauf if r["gewicht_kg"] is not None]
    if len(gewichte) < 14:
        return False

    avg_now  = sum(gewichte[-7:]) / 7
    avg_past = sum(gewichte[-21:-14]) / 7 if len(gewichte) >= 21 else sum(gewichte[:7]) / 7

    delta = avg_past - avg_now  # Positiv = Gewichtsverlust
    return delta < config.PLATEAU_DELTA_KG


def foto_erinnerung_aktiv(logs: list[dict], startdatum: date = None) -> bool:
    """True, wenn heute ein 14-Tage-Foto-Check-In fällig ist."""
    tag_nr = berechne_tag_nummer(startdatum=startdatum)
    return tag_nr > 0 and (tag_nr % config.FOTO_ERINNERUNG_TAGE == 0)


def ist_sonntag(heute: date = None) -> bool:
    if heute is None:
        heute = date.today()
    return heute.weekday() == 6


def berechne_kcal_fortschritt(kcal_gesamt: float, kcal_ziel: float) -> tuple[float, str]:
    """
    Gibt (Prozentwert 0-100, Statusfarbe) zurück.
    Grün < 85%, Gelb 85-100%, Rot > 100%.
    """
    pct = min((kcal_gesamt / kcal_ziel) * 100, 150) if kcal_ziel > 0 else 0
    if pct <= 85:
        color = config.SUCCESS_COLOR
    elif pct <= 100:
        color = config.WARNING_COLOR
    else:
        color = config.ERROR_COLOR
    return pct, color
