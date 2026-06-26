"""
config.py – Alle Konstanten und Konfigurationswerte der App.
Hier anpassen, um Ziele global zu ändern.
"""

from datetime import date

# ── Nutzer-Profil ────────────────────────────────────────────────────────────
STARTDATUM        = None  # Wird dynamisch aus der Datenbank geladen
STARTGEWICHT_KG   = 69.5
GROESSE_CM        = 173
ALTER_JAHRE       = 39
CHALLENGE_TAGE    = 90

# ── Energie-Ziele (Sjard Roscher Prinzipien) ────────────────────────────────
TDEE_KCAL         = 2490          # Erhaltungskalorien (PAL 1,55)
KCAL_ZIEL         = 1993          # 80 % des TDEE → tägliche Obergrenze
PROTEIN_ZIEL_G    = 160           # 2,3 g pro kg Körpergewicht
KH_RICHTWERT_G    = 214           # Orientierungswert Kohlenhydrate
FETT_RICHTWERT_G  = 55            # Orientierungswert Fett

# ── Plateau-Logik ───────────────────────────────────────────────────────────
PLATEAU_MIN_TAGE  = 21            # Mindestanzahl geloggter Tage für Prüfung
PLATEAU_DELTA_KG  = 0.2           # Unter diesem Delta → Stagnation
KCAL_REDUKTION    = 125           # Kalorienschnitt bei Plateau (kcal)
KH_REDUKTION_G    = 31            # KH-Schnitt bei Plateau (g)

# ── Habits / Supplements ────────────────────────────────────────────────────
HABIT_SCHRITTE_ZIEL   = 10_000   # Schritte-Tagesziel
WASSER_ZIEL_LITER     = 3.5      # Tägliches Wasserziel
CREATINE_DEFAULT_G    = 5.0
OMEGA3_DEFAULT_G      = 3.0

# ── Lieblingslebensmittel für Schnellauswahl ────────────────────────────────
QUICK_FOODS: list[dict] = [
    {"name": "Pink Lady Apfel (1 Stk)",           "kcal": 95,  "protein": 0.5},
    {"name": "Körniger Frischkäse (200 g)",        "kcal": 204, "protein": 26.0},
    {"name": "Ei (1 Stk, Gr. M)",                  "kcal": 75,  "protein": 7.0},
    {"name": "Nudeln (100 g, ungekocht)",           "kcal": 350, "protein": 12.0},
    {"name": "Beeren-Mix (150 g)",                  "kcal": 75,  "protein": 1.5},
    {"name": "Dunkle Schokolade (20 g)",            "kcal": 110, "protein": 1.5},
    {"name": "Gesalzene Erdnüsse (30 g)",           "kcal": 185, "protein": 8.0},
    {"name": "Erdnuss Flips (30 g)",                "kcal": 160, "protein": 4.0},
    {"name": "Cola Zero / Super-Pop (500 ml)",      "kcal": 1,   "protein": 0.0},
]

# ── Slot-System ─────────────────────────────────────────────────────────────
STANDARD_SLOTS    = 4             # Standard-Anzahl Mahlzeiten-Slots
PROTEIN_SLOT_WARN = 30            # Unterhalb dieses Wertes → Sjard-Tipp

# ── Wöchentliche Messungen ──────────────────────────────────────────────────
FOTO_ERINNERUNG_TAGE = 14         # Alle N Tage Foto-Erinnerung

# ── Design-Konstanten ────────────────────────────────────────────────────────
BRAND_COLOR       = "#E8500A"     # Haupt-Akzentfarbe (Orange)
SUCCESS_COLOR     = "#22C55E"     # Grün für erreichte Ziele
WARNING_COLOR     = "#EAB308"     # Gelb für Warnungen
ERROR_COLOR       = "#EF4444"     # Rot für Grenzwert-Überschreitung
BG_DARK           = "#0F1117"     # Haupt-Hintergrund (Dark Mode)
CARD_BG           = "#1E2130"     # Karten-Hintergrund
