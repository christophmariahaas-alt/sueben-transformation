"""
app.py – Hauptdatei: "PROJECT H90"
Starten mit: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from typing import Optional

import config
import database as db
import logic

# ══════════════════════════════════════════════════════════════════════════════
# SEITEN-KONFIGURATION & GLOBALES CSS
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="PROJECT H90",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

db.init_db()

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,300&display=swap');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

  /* ── Basis: Weiß auf Schwarz ─────────────────────────────────────────── */
  html, body, .stApp {
    background-color: #F7F5F2 !important;
    color: #0A0A0A !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1080px !important;
  }

  /* ── App Header ──────────────────────────────────────────────────────── */
  .app-header {
    background: #0A0A0A;
    border-radius: 20px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 60px rgba(0,0,0,0.15), 0 0 0 1px rgba(184,255,0,0.08);
  }
  .app-title {
    font-size: 3.6rem;
    font-weight: 400;
    letter-spacing: 0.04em;
    margin: 0;
    color: #FFFFFF;
    font-family: 'Bebas Neue', sans-serif;
    line-height: 0.9;
  }
  .app-title span {
    color: #B8FF00;
  }
  .app-subtitle {
    font-size: 0.65rem;
    color: #3A3A3A;
    margin: 0.7rem 0 0 0;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Metric Cards ────────────────────────────────────────────────────── */
  .metric-card {
    background: #FFFFFF;
    border: none;
    border-radius: 16px;
    padding: 1.5rem 1rem;
    text-align: center;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .metric-card:hover {
    box-shadow: 0 8px 32px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.06);
  }
  .metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #0A0A0A;
    line-height: 1;
    letter-spacing: -0.03em;
    font-family: 'DM Sans', sans-serif;
  }
  .metric-label {
    font-size: 0.6rem;
    color: #AAAAAA;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-top: 0.65rem;
    font-weight: 600;
  }
  .metric-sub {
    font-size: 0.75rem;
    color: #CCCCCC;
    margin-top: 0.3rem;
  }

  /* ── Progress Bar ────────────────────────────────────────────────────── */
  .progress-bar-wrap {
    background: #EFEFEF;
    border-radius: 999px;
    height: 3px;
    overflow: hidden;
    margin: 0.7rem 0 0.3rem 0;
  }
  .progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
  }

  /* ── Mahlzeiten ──────────────────────────────────────────────────────── */
  .meal-slot-header {
    font-size: 0.6rem;
    font-weight: 700;
    color: #BBBBBB;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    margin-bottom: 0.9rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #F0F0F0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .meal-slot-header::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #E0E0E0;
    flex-shrink: 0;
  }
  .meal-field-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #BBBBBB;
    margin-bottom: 0.25rem;
    display: block;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  /* ── Info-Boxen ──────────────────────────────────────────────────────── */
  .warn-box {
    background: #FFFBF0;
    border-left: 2px solid #D4A800;
    border-radius: 0 10px 10px 0;
    padding: 0.7rem 1rem;
    font-size: 0.8rem;
    color: #8A6F00;
    margin-top: 0.5rem;
  }
  .plateau-box {
    background: #FFF8F8;
    border: 1px solid #F0DADA;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 1rem 0;
    color: #8A4A4A;
    font-size: 0.9rem;
  }
  .foto-box {
    background: #F8F8FF;
    border: 1px solid #E0E0F0;
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    margin: 0.8rem 0;
    color: #666688;
    font-size: 0.88rem;
  }
  .success-box {
    background: #F6FBF6;
    border: 1px solid #D0E8D0;
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    margin: 0.8rem 0;
    color: #3A6A3A;
    font-size: 0.88rem;
  }

  /* ── Streak ──────────────────────────────────────────────────────────── */
  .streak-display {
    font-size: 3.8rem;
    font-weight: 700;
    color: #0A0A0A;
    text-align: center;
    line-height: 1;
    letter-spacing: -0.04em;
    font-family: 'DM Sans', sans-serif;
  }
  .streak-label {
    text-align: center;
    font-size: 0.62rem;
    color: #BBB;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-weight: 600;
  }

  /* ── Section Header ──────────────────────────────────────────────────── */
  .section-header {
    font-size: 0.6rem;
    font-weight: 700;
    color: #AAAAAA;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    margin: 2.2rem 0 1.2rem 0;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid #EBEBEB;
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }
  .section-header::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #B8FF00;
    flex-shrink: 0;
    box-shadow: 0 0 8px #B8FF0088;
  }

  /* ── Start Screen ────────────────────────────────────────────────────── */
  .start-screen {
    background: #FFFFFF;
    border: none;
    border-radius: 20px;
    padding: 3.5rem 2.5rem;
    text-align: center;
    margin: 3rem auto;
    max-width: 560px;
    box-shadow: 0 4px 40px rgba(0,0,0,0.08);
  }
  .start-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: #0A0A0A;
    margin-bottom: 0.8rem;
    letter-spacing: -0.03em;
  }
  .start-sub {
    color: #999;
    font-size: 0.92rem;
    margin-bottom: 2.5rem;
    line-height: 1.75;
  }

  /* ── Inputs ──────────────────────────────────────────────────────────── */
  div[data-testid="stNumberInput"] input,
  div[data-testid="stTextInput"] input,
  div[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E8E8 !important;
    color: #0A0A0A !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-family: 'DM Sans', sans-serif !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
  }
  div[data-testid="stNumberInput"] input:focus,
  div[data-testid="stTextInput"] input:focus {
    border-color: #0A0A0A !important;
    box-shadow: 0 0 0 2px rgba(10,10,10,0.06) !important;
  }
  div[data-testid="stNumberInput"] label,
  div[data-testid="stTextInput"] label,
  div[data-testid="stDateInput"] label {
    color: #AAAAAA !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* ── Buttons ─────────────────────────────────────────────────────────── */
  .stButton > button {
    border-radius: 10px !important;
    font-weight: 400 !important;
    letter-spacing: 0.12em !important;
    font-size: 1.1rem !important;
    padding: 0.7rem 1.6rem !important;
    min-height: 2.8rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Bebas Neue', sans-serif !important;
    text-transform: uppercase !important;
    width: 100% !important;
  }
  .stButton > button[kind="primary"] {
    background: #0A0A0A !important;
    border: none !important;
    color: #FFFFFF !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important;
    letter-spacing: 0.15em !important;
    font-weight: 400 !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.18) !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #1A1A1A !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(0,0,0,0.22) !important;
    color: #FFFFFF !important;
  }
  .stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E0E0E0 !important;
    color: #888 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
  }
  .stButton > button[kind="secondary"]:hover {
    border-color: #AAAAAA !important;
    color: #0A0A0A !important;
  }

  /* ── Checkboxen ──────────────────────────────────────────────────────── */
  div[data-testid="stCheckbox"] label {
    color: #555 !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  div[data-testid="stCheckbox"] input:checked + div {
    background-color: #B8FF00 !important;
    border-color: #B8FF00 !important;
  }

  /* ── Tabs ────────────────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    background-color: #EEECE9 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.35rem !important;
    gap: 0.2rem !important;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    color: #BBBBBB !important;
    font-weight: 400 !important;
    font-size: 1.15rem !important;
    letter-spacing: 0.12em !important;
    font-family: 'Bebas Neue', sans-serif !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s ease !important;
  }
  .stTabs [aria-selected="true"] {
    background-color: #0A0A0A !important;
    color: #FFFFFF !important;
    font-weight: 400 !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.15) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
  }

  /* ── Expander ────────────────────────────────────────────────────────── */
  div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #EBEBEB !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04) !important;
  }
  div[data-testid="stExpander"] summary {
    color: #AAAAAA !important;
    font-size: 0.78rem !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* ── Divider ─────────────────────────────────────────────────────────── */
  hr {
    border-color: #EBEBEB !important;
    margin: 1.8rem 0 !important;
  }

  /* ── Dataframe ───────────────────────────────────────────────────────── */
  div[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border: 1px solid #EBEBEB !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04) !important;
  }

  /* ── Selectbox ───────────────────────────────────────────────────────── */
  div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E8E8 !important;
    border-radius: 10px !important;
  }

  /* ── Caption / Info Text ─────────────────────────────────────────────── */
  .stCaption, div[data-testid="stCaptionContainer"] {
    color: #BBBBBB !important;
    font-family: 'DM Sans', sans-serif !important;
  }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STARTDATUM LADEN
# ══════════════════════════════════════════════════════════════════════════════

startdatum = db.get_startdatum()
heute      = date.today()

# ── START-SCREEN: Challenge noch nicht gestartet ─────────────────────────────
if startdatum is None:
    st.markdown(f"""
    <div class='app-header'>
      <div class='app-title'>⚡ PROJECT H90</div>
      <div class='app-subtitle'>90 Tage bis zur Bestform &nbsp;|&nbsp; FC Suebia Edition</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='start-screen'>
      <div class='start-title'>🏁 Bereit für die 90-Tage-Challenge?</div>
      <div class='start-sub'>
        Klicke auf den Button um die Challenge offiziell zu starten.<br>
        Das heutige Datum wird als Tag 1 gesetzt.<br><br>
        <strong style='color:#888;'>Startgewicht: {config.STARTGEWICHT_KG} kg &nbsp;·&nbsp;
        Ziel: {config.KCAL_ZIEL} kcal &nbsp;·&nbsp; {config.PROTEIN_ZIEL_G}g Protein</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Challenge jetzt starten", type="primary", use_container_width=True):
            db.set_startdatum(heute)
            st.success(f"✅ Challenge gestartet! Tag 1 von 90 – los geht's!")
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# DATUM-PICKER & SESSION-STATE
# ══════════════════════════════════════════════════════════════════════════════

# Datum-Picker: erlaubt Nachträge für vergangene Tage
max_datum = heute
min_datum = startdatum

# Wenn das gewählte Datum sich ändert, alles neu laden
if "gewaehltes_datum" not in st.session_state:
    st.session_state.gewaehltes_datum = heute
if "letztes_datum" not in st.session_state:
    st.session_state.letztes_datum = heute


def lade_log_fuer_datum(ziel_datum: date):
    """Lädt einen vorhandenen Log-Eintrag und setzt Session-State."""
    vorhandener_log = db.load_daily_log(ziel_datum)

    if vorhandener_log and vorhandener_log["mahlzeiten"]:
        st.session_state.slots = vorhandener_log["mahlzeiten"]
    else:
        st.session_state.slots = [
            {"name": f"Mahlzeit {i+1}", "kcal": 0.0, "protein": 0.0}
            for i in range(config.STANDARD_SLOTS)
        ]

    if vorhandener_log:
        st.session_state.gewicht   = vorhandener_log.get("gewicht_kg")  or config.STARTGEWICHT_KG
        st.session_state.schlaf    = vorhandener_log.get("schlaf_std")  or 7.5
        st.session_state.schritte  = bool(vorhandener_log.get("habit_schritte"))
        st.session_state.wasser    = bool(vorhandener_log.get("habit_wasser"))
        st.session_state.training  = bool(vorhandener_log.get("habit_training"))
        st.session_state.neat      = bool(vorhandener_log.get("habit_neat"))
        st.session_state.clean     = bool(vorhandener_log.get("habit_clean"))
        st.session_state.creatin   = vorhandener_log.get("supp_creatin_g") or config.CREATINE_DEFAULT_G
        st.session_state.omega3    = vorhandener_log.get("supp_omega3_g")  or config.OMEGA3_DEFAULT_G
        st.session_state.vitamine  = bool(vorhandener_log.get("supp_vitamine"))
        st.session_state.gespeichert = True
    else:
        st.session_state.gewicht   = config.STARTGEWICHT_KG
        st.session_state.schlaf    = 7.5
        st.session_state.schritte  = False
        st.session_state.wasser    = False
        st.session_state.training  = False
        st.session_state.neat      = False
        st.session_state.clean     = False
        st.session_state.creatin   = config.CREATINE_DEFAULT_G
        st.session_state.omega3    = config.OMEGA3_DEFAULT_G
        st.session_state.vitamine  = False
        st.session_state.gespeichert = False


# Beim ersten Laden initialisieren
if "gespeichert" not in st.session_state or "slots" not in st.session_state:
    lade_log_fuer_datum(heute)

# ══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════════════════════

def fortschrittsbalken(wert: float, ziel: float, farbe: str, einheit: str = "") -> str:
    pct = min((wert / ziel) * 100, 100) if ziel > 0 else 0
    balken = "linear-gradient(90deg,#E0E0E0,#0A0A0A)" if pct >= 100 else "linear-gradient(90deg,#EFEFEF,#AAAAAA)"
    return f"""
    <div class='progress-bar-wrap'>
      <div class='progress-bar-fill' style='width:{pct:.1f}%;background:{balken};'></div>
    </div>
    <div style='display:flex;justify-content:space-between;font-size:0.73rem;margin-top:0.25rem;'>
      <span style='color:#888;'>{wert:.0f}{einheit}</span>
      <span style='color:#CCC;'>/ {ziel:.0f}{einheit}</span>
    </div>
    """


def makro_karte(label: str, wert: float, ziel: float, einheit: str, farbe: str) -> str:
    pct = min((wert / ziel) * 100, 100) if ziel > 0 else 0
    dot   = "#B8FF00" if pct >= 100 else ("#AAAAAA" if pct >= 80 else "#E0E0E0")
    balken = "linear-gradient(90deg,#3A4A00,#B8FF00)" if pct >= 100 else "linear-gradient(90deg,#F0F0F0,#CCCCCC)"
    return f"""
    <div class='metric-card'>
      <div style='display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.1rem;'>
        <div style='width:5px;height:5px;border-radius:50%;background:{dot};flex-shrink:0;'></div>
        <div class='metric-value'>
          {wert:.0f}<span style='font-size:0.72rem;color:#CCC;font-weight:400;margin-left:3px;'>{einheit}</span>
        </div>
      </div>
      <div class='metric-label'>{label}</div>
      <div class='progress-bar-wrap'>
        <div class='progress-bar-fill' style='width:{pct:.1f}%;background:{balken};'></div>
      </div>
      <div class='metric-sub'>{pct:.0f} %</div>
    </div>
    """


def berechne_slot_summen() -> tuple[float, float]:
    kcal    = sum(s.get("kcal",    0) for s in st.session_state.slots)
    protein = sum(s.get("protein", 0) for s in st.session_state.slots)
    return kcal, protein


# ══════════════════════════════════════════════════════════════════════════════
# APP-HEADER
# ══════════════════════════════════════════════════════════════════════════════

alle_logs  = db.load_all_logs()
streak     = logic.berechne_streak(alle_logs)
tag_nr     = logic.berechne_tag_nummer(heute, startdatum)
kcal_ziel  = db.get_kcal_ziel()

st.markdown(f"""
<div class='app-header'>
  <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem;'>
    <div>
      <div class='app-title'>PROJECT <span>H90</span></div>
      <div class='app-subtitle'>90 Days to Peak Performance &nbsp;&nbsp;·&nbsp;&nbsp; FC Suebia Edition</div>
    </div>
    <div style='display:flex;gap:2.5rem;align-items:center;'>
      <div style='text-align:center;'>
        <div style='font-size:2.2rem;font-weight:700;color:#FFFFFF;line-height:1;letter-spacing:-0.04em;font-family:DM Sans,sans-serif;'>{tag_nr}</div>
        <div style='font-size:0.58rem;color:#444;text-transform:uppercase;letter-spacing:0.22em;margin-top:0.4rem;font-weight:600;'>von 90</div>
      </div>
      <div style='width:1px;height:2.5rem;background:#222;'></div>
      <div style='text-align:center;'>
        <div style='font-size:2.2rem;font-weight:700;color:#FFFFFF;line-height:1;letter-spacing:-0.04em;font-family:DM Sans,sans-serif;'>{streak}</div>
        <div style='font-size:0.58rem;color:#444;text-transform:uppercase;letter-spacing:0.22em;margin-top:0.4rem;font-weight:600;'>Streak</div>
      </div>
      <div style='width:1px;height:2.5rem;background:#222;'></div>
      <div style='text-align:right;'>
        <div style='font-size:0.95rem;font-weight:500;color:#777;line-height:1;font-family:DM Sans,sans-serif;'>{heute.strftime("%d.%m.%Y")}</div>
        <div style='font-size:0.58rem;color:#444;text-transform:uppercase;letter-spacing:0.18em;margin-top:0.4rem;font-weight:600;'>{heute.strftime("%A")}</div>
      </div>
    </div>
  </div>
  <div style='margin-top:1.8rem;'>
    <div style='background:#1E1E1E;border-radius:999px;height:2px;overflow:hidden;'>
      <div style='width:{(tag_nr/90)*100:.1f}%;height:100%;background:linear-gradient(90deg,#3A4A00,#B8FF00);border-radius:999px;box-shadow:0 0 8px #B8FF0066;'></div>
    </div>
    <div style='font-size:0.6rem;color:#333;margin-top:0.5rem;text-align:right;letter-spacing:0.15em;font-weight:600;'>{90-tag_nr} TAGE VERBLEIBEND</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_checkin, tab_progress = st.tabs([
    "Daily Check-In",
    "Progress Hub",
])

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1: DAILY CHECK-IN                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_checkin:

    # ── Datum-Picker ─────────────────────────────────────────────────────────
    dp_col1, dp_col2 = st.columns([2, 3])
    with dp_col1:
        ziel_datum = st.date_input(
            "📅 Eintrag für Tag:",
            value=st.session_state.gewaehltes_datum,
            min_value=min_datum,
            max_value=max_datum,
            key="datum_picker",
            format="DD.MM.YYYY",
        )

    # Datum geändert → Formular neu laden
    if ziel_datum != st.session_state.letztes_datum:
        st.session_state.letztes_datum    = ziel_datum
        st.session_state.gewaehltes_datum = ziel_datum
        lade_log_fuer_datum(ziel_datum)
        st.rerun()

    with dp_col2:
        tag_nr_anzeige = logic.berechne_tag_nummer(ziel_datum, startdatum)
        ist_heute = ziel_datum == heute
        if ist_heute:
            st.markdown(f"<div style='padding-top:1.8rem;color:#64748B;font-size:0.9rem;'>📌 Heute · Tag {tag_nr_anzeige} von 90</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding-top:1.8rem;color:{config.WARNING_COLOR};font-size:0.9rem;'>✏️ Nachtrag · Tag {tag_nr_anzeige} von 90</div>", unsafe_allow_html=True)

    st.divider()

    # ── Foto-Erinnerung ──────────────────────────────────────────────────────
    if logic.foto_erinnerung_aktiv(alle_logs, startdatum):
        st.markdown(f"""
        <div class='foto-box'>
          📸 <strong>14-Tage-Foto-Check!</strong> &nbsp;
          Tag {tag_nr} – Zeit für deine Fortschrittsfotos!
        </div>
        """, unsafe_allow_html=True)

    # ── Plateau-Warnung ──────────────────────────────────────────────────────
    gewichtsverlauf = db.get_gewichts_verlauf()
    if logic.pruefe_plateau(gewichtsverlauf):
        st.markdown(f"""
        <div class='plateau-box'>
          ⚠️ <strong>Stagnation erkannt!</strong> Dein Gewicht hat sich kaum verändert –
          bereit für den nächsten Schritt?
        </div>
        """, unsafe_allow_html=True)
        if st.button(
            f"🔧 Kalorien um 5% senken (–{config.KCAL_REDUKTION} kcal)",
            type="primary", key="plateau_btn"
        ):
            db.senke_kcal_ziel(config.KCAL_REDUKTION, config.KH_REDUKTION_G)
            kcal_ziel = db.get_kcal_ziel()
            st.success(f"✅ Neues Kalorienziel: {kcal_ziel:.0f} kcal")
            st.rerun()

    # ── A. MORGENS ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Morgens &nbsp;·&nbsp; Schnelle Kennzahlen</div>", unsafe_allow_html=True)

    col_g, col_s = st.columns(2)
    with col_g:
        gewicht = st.number_input(
            "⚖️ Gewicht (kg)",
            min_value=40.0, max_value=200.0, step=0.1,
            value=float(st.session_state.gewicht),
            key="input_gewicht",
            help="Morgens nüchtern nach dem Toilettengang messen",
        )
    with col_s:
        schlaf = st.number_input(
            "😴 Schlafdauer (Stunden)",
            min_value=0.0, max_value=24.0, step=0.25,
            value=float(st.session_state.schlaf),
            key="input_schlaf",
        )

    # ── B. ERNÄHRUNG ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Ernährung &nbsp;·&nbsp; Makro-Tracking</div>", unsafe_allow_html=True)

    # Live-Makro-Übersicht
    kcal_summe, protein_summe = berechne_slot_summen()
    kcal_pct, kcal_farbe = logic.berechne_kcal_fortschritt(kcal_summe, kcal_ziel)
    prot_pct   = min((protein_summe / config.PROTEIN_ZIEL_G) * 100, 100)
    prot_farbe = config.SUCCESS_COLOR if prot_pct >= 100 else (config.WARNING_COLOR if prot_pct >= 80 else config.ERROR_COLOR)
    rest_kcal  = max(0, kcal_ziel - kcal_summe)
    rest_farbe = config.SUCCESS_COLOR if rest_kcal > 200 else config.WARNING_COLOR

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(makro_karte("Kalorien gesamt", kcal_summe, kcal_ziel, " kcal", kcal_farbe), unsafe_allow_html=True)
    with m2:
        st.markdown(makro_karte("Protein gesamt", protein_summe, config.PROTEIN_ZIEL_G, " g", prot_farbe), unsafe_allow_html=True)
    with m3:
        rest_dot = "#B8FF00" if rest_kcal > 200 else "#AAAAAA"
        st.markdown(f"""
        <div class='metric-card'>
          <div style='display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-bottom:0.1rem;'>
            <div style='width:5px;height:5px;border-radius:50%;background:{rest_dot};flex-shrink:0;'></div>
            <div class='metric-value'>
              {rest_kcal:.0f}<span style='font-size:0.72rem;color:#CCC;font-weight:400;margin-left:3px;'>kcal</span>
            </div>
          </div>
          <div class='metric-label'>Noch verfügbar</div>
          <div class='progress-bar-wrap'>
            <div class='progress-bar-fill' style='width:{min((rest_kcal/kcal_ziel)*100,100):.1f}%;background:linear-gradient(90deg,#F0F0F0,#CCCCCC);'></div>
          </div>
          <div class='metric-sub'>von {kcal_ziel:.0f} kcal</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ── Mahlzeiten-Slots ─────────────────────────────────────────────────────
    for i, slot in enumerate(st.session_state.slots):
        st.markdown(f"<div class='meal-slot-header'>Mahlzeit {i+1}</div>", unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns([3, 2, 2])
        with sc1:
            name = st.text_input(
                "Bezeichnung",
                value=slot.get("name", f"Mahlzeit {i+1}"),
                key=f"slot_name_{i}",
                placeholder="z.B. Frühstück, Mittagessen...",
            )
            st.session_state.slots[i]["name"] = name

        with sc2:
            st.markdown("<span class='meal-field-label'>Kalorien (kcal)</span>", unsafe_allow_html=True)
            kcal_val = st.number_input(
                "kcal",
                min_value=0.0, max_value=5000.0, step=5.0,
                value=float(slot.get("kcal", 0)),
                key=f"slot_kcal_{i}",
                label_visibility="collapsed",
            )
            st.session_state.slots[i]["kcal"] = kcal_val

        with sc3:
            st.markdown("<span class='meal-field-label'>Protein (g)</span>", unsafe_allow_html=True)
            protein_val = st.number_input(
                "Protein (g)",
                min_value=0.0, max_value=500.0, step=1.0,
                value=float(slot.get("protein", 0)),
                key=f"slot_prot_{i}",
                label_visibility="collapsed",
            )
            st.session_state.slots[i]["protein"] = protein_val

        # Sjard-Tipp bei niedrigem Protein
        if kcal_val > 0 and protein_val < config.PROTEIN_SLOT_WARN:
            st.markdown(
                f"<div class='warn-box'>💡 Sjard-Tipp: Erhöhe das Protein! "
                f"(Ziel ≥ {config.PROTEIN_SLOT_WARN}g pro Mahlzeit)</div>",
                unsafe_allow_html=True,
            )

        st.write("")

    if st.button("+ Weiteren Slot hinzufügen"):
        n = len(st.session_state.slots) + 1
        st.session_state.slots.append({"name": f"Mahlzeit {n}", "kcal": 0.0, "protein": 0.0})
        st.rerun()

    # ── C. ABENDS: HABITS ────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Abends &nbsp;·&nbsp; Habits & Supplements</div>", unsafe_allow_html=True)

    st.markdown("**✅ Tägliche Gewohnheiten**")
    hab_col1, hab_col2 = st.columns(2)
    with hab_col1:
        h_schritte = st.checkbox(f"{config.HABIT_SCHRITTE_ZIEL:,} Schritte".replace(",", "."), value=st.session_state.schritte, key="cb_schritte")
        h_wasser   = st.checkbox(f"{config.WASSER_ZIEL_LITER} Liter Wasser",                   value=st.session_state.wasser,    key="cb_wasser")
        h_training = st.checkbox("Krafttraining absolviert",                                    value=st.session_state.training,  key="cb_training")
    with hab_col2:
        h_neat  = st.checkbox("NEAT-Fokus (Treppen, Stehschreibtisch)", value=st.session_state.neat,  key="cb_neat")
        h_clean = st.checkbox("Clean Eating eingehalten (80/20)",        value=st.session_state.clean, key="cb_clean")

    habits_erreicht = sum([h_schritte, h_wasser, h_training, h_neat, h_clean])
    hab_farbe = config.SUCCESS_COLOR if habits_erreicht >= 4 else (config.WARNING_COLOR if habits_erreicht >= 3 else config.ERROR_COLOR)
    st.markdown(
        f"<div style='font-size:0.8rem;color:#64748B;margin-top:0.3rem;'>Habits: {habits_erreicht}/5</div>"
        + fortschrittsbalken(habits_erreicht, 5, hab_farbe),
        unsafe_allow_html=True
    )

    # ── Supplements ──────────────────────────────────────────────────────────
    st.write("")
    st.markdown("**💊 Supplements**")
    sup_col1, sup_col2, sup_col3 = st.columns(3)
    with sup_col1:
        s_creatin = st.number_input("Creatin (g)", min_value=0.0, max_value=20.0, step=0.5, value=float(st.session_state.creatin), key="input_creatin")
    with sup_col2:
        s_omega3  = st.number_input("Omega 3 (g)", min_value=0.0, max_value=20.0, step=0.5, value=float(st.session_state.omega3),  key="input_omega3")
    with sup_col3:
        st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
        s_vitamine = st.checkbox("Vitamine & Zink (D3/K2, Multi, Zink)", value=st.session_state.vitamine, key="cb_vitamine")

    # ── SPEICHERN ────────────────────────────────────────────────────────────
    st.write("")
    st.divider()

    if st.session_state.gespeichert:
        label = "heute" if ziel_datum == heute else f"den {ziel_datum.strftime('%d.%m.%Y')}"
        st.markdown(
            f"<div class='success-box'>✅ Eintrag für {label} bereits gespeichert – du kannst jederzeit überschreiben.</div>",
            unsafe_allow_html=True,
        )

    btn_label = "Tag speichern" if ziel_datum == heute else f"Nachtrag {ziel_datum.strftime('%d.%m.')} speichern"
    if st.button(btn_label, type="primary", use_container_width=True, key="save_btn"):
        mahlzeiten = [
            {
                "name":    st.session_state.get(f"slot_name_{i}", f"Mahlzeit {i+1}"),
                "kcal":    st.session_state.get(f"slot_kcal_{i}", 0.0),
                "protein": st.session_state.get(f"slot_prot_{i}", 0.0),
            }
            for i in range(len(st.session_state.slots))
        ]
        habits = {
            "schritte": h_schritte, "wasser": h_wasser,
            "training": h_training, "neat": h_neat, "clean": h_clean,
        }
        supplements = {
            "creatin_g": s_creatin, "omega3_g": s_omega3, "vitamine": s_vitamine,
        }

        db.save_daily_log(
            log_date=ziel_datum, gewicht_kg=gewicht, schlaf_std=schlaf,
            mahlzeiten=mahlzeiten, habits=habits, supplements=supplements,
        )
        st.session_state.gespeichert = True
        st.session_state.slots = mahlzeiten

        kcal_ok = sum(m["kcal"]    for m in mahlzeiten) <= kcal_ziel
        prot_ok = sum(m["protein"] for m in mahlzeiten) >= config.PROTEIN_ZIEL_G
        if kcal_ok and prot_ok:
            st.balloons()
            st.success("🎉 Perfekt! Kalorien UND Protein im Ziel – Sjard wäre stolz!")
        elif kcal_ok:
            st.success("✅ Gespeichert! Kalorien stimmen – morgen mehr Protein!")
        elif prot_ok:
            st.warning("⚠️ Gespeichert! Protein top – aber Kalorien überschritten!")
        else:
            st.info("💾 Gespeichert! Morgen wieder angreifen!")
        st.rerun()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2: PROGRESS HUB                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_progress:

    # ── Einstellungen (immer sichtbar) ────────────────────────────────────────
    with st.expander("⚙️ Einstellungen"):
        st.markdown("**Challenge zurücksetzen**")
        st.caption("Setzt das Startdatum zurück sodass die Challenge neu gestartet werden kann. Deine bisherigen Log-Einträge bleiben erhalten.")
        if st.button("🔄 Startdatum zurücksetzen", key="reset_btn"):
            db.set_setting("startdatum", "")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Startdatum zurückgesetzt – du kannst die Challenge neu starten.")
            st.rerun()

    if len(alle_logs) == 0:
        st.info("Noch keine Daten vorhanden. Starte mit deinem ersten Check-In!")
    else:
        st.markdown("<div class='section-header'>Übersicht</div>", unsafe_allow_html=True)

        streak_col, days_col, avg_col, best_col = st.columns(4)
        with streak_col:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='streak-display'>{streak}</div>
              <div class='streak-label'>Streak</div>
            </div>
            """, unsafe_allow_html=True)
        with days_col:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='metric-value'>{len(alle_logs)}</div>
              <div class='metric-label'>Tage geloggt</div>
              <div class='metric-sub'>von 90 gesamt</div>
            </div>
            """, unsafe_allow_html=True)

        gew_verlauf = db.get_gewichts_verlauf()
        if gew_verlauf:
            letzte_7 = [r["gewicht_kg"] for r in gew_verlauf[-7:] if r["gewicht_kg"]]
            avg_gew  = sum(letzte_7) / len(letzte_7) if letzte_7 else 0
            delta    = avg_gew - config.STARTGEWICHT_KG
            delta_str  = f"{'–' if delta < 0 else '+'}{abs(delta):.1f} kg"
            delta_farbe = config.SUCCESS_COLOR if delta < 0 else config.ERROR_COLOR

            with avg_col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.6rem;'>{avg_gew:.1f}<span style='font-size:0.8rem;color:#64748B;'>kg</span></div>
                  <div class='metric-label'>Ø Gewicht (7d)</div>
                  <div class='metric-sub'>Start: {config.STARTGEWICHT_KG} kg</div>
                </div>
                """, unsafe_allow_html=True)
            with best_col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.6rem;color:{delta_farbe};'>{delta_str}</div>
                  <div class='metric-label'>Gesamt-Veränderung</div>
                  <div class='metric-sub'>seit Start</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Gewichtskurve ─────────────────────────────────────────────────────
        if gew_verlauf:
            st.markdown("<div class='section-header'>Gewichtsverlauf</div>", unsafe_allow_html=True)

            df_gew = pd.DataFrame(gew_verlauf)
            df_gew["log_date"] = pd.to_datetime(df_gew["log_date"])
            df_gew = df_gew.sort_values("log_date")
            df_gew["avg_7d"] = logic.gleitender_durchschnitt(df_gew["gewicht_kg"].tolist(), 7)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_gew["log_date"], y=df_gew["gewicht_kg"],
                name="Tagesgewicht", mode="lines+markers",
                line=dict(color="#475569", width=1, dash="dot"),
                marker=dict(size=4, color="#64748B"),
                hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.1f} kg</b><extra></extra>",
            ))
            df_avg = df_gew.dropna(subset=["avg_7d"])
            if not df_avg.empty:
                fig.add_trace(go.Scatter(
                    x=df_avg["log_date"], y=df_avg["avg_7d"],
                    name="7-Tage-Durchschnitt", mode="lines",
                    line=dict(color=config.BRAND_COLOR, width=3),
                    hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.2f} kg</b> (Ø7d)<extra></extra>",
                ))
            fig.add_hline(
                y=config.STARTGEWICHT_KG,
                line=dict(color="#374151", width=1, dash="dash"),
                annotation_text=f"Start {config.STARTGEWICHT_KG} kg",
                annotation_font=dict(color="#6B7280", size=11),
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", size=12),
                legend=dict(bgcolor="rgba(30,33,48,0.8)", bordercolor="#2D3748", borderwidth=1),
                xaxis=dict(gridcolor="#1E2A3A", tickformat="%d.%m"),
                yaxis=dict(gridcolor="#1E2A3A", title="Gewicht (kg)", tickformat=".1f"),
                margin=dict(l=0, r=0, t=20, b=0),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Letzte 14 Tage Tabelle ────────────────────────────────────────────
        st.markdown("<div class='section-header'>Letzte 14 Tage</div>", unsafe_allow_html=True)
        letzte_logs = alle_logs[-14:][::-1]
        if letzte_logs:
            tabellen_data = []
            for log in letzte_logs:
                tabellen_data.append({
                    "Datum":        log["log_date"],
                    "Gewicht (kg)": f"{log['gewicht_kg']:.1f}" if log.get("gewicht_kg") else "–",
                    "kcal":         f"{log['kcal_gesamt']:.0f}" if log.get("kcal_gesamt") else "–",
                    "Protein (g)":  f"{log['protein_gesamt']:.0f}" if log.get("protein_gesamt") else "–",
                    "Schlaf (h)":   f"{log['schlaf_std']:.1f}" if log.get("schlaf_std") else "–",
                    "Habits":       sum([
                        bool(log.get("habit_schritte")), bool(log.get("habit_wasser")),
                        bool(log.get("habit_training")), bool(log.get("habit_neat")),
                        bool(log.get("habit_clean")),
                    ]),
                })
            st.dataframe(
                pd.DataFrame(tabellen_data),
                use_container_width=True, hide_index=True,
                column_config={
                    "Habits": st.column_config.ProgressColumn("Habits", min_value=0, max_value=5, format="%d/5"),
                },
            )

        # ── Aktuelle Ziele ────────────────────────────────────────────────────
        st.markdown("<div class='section-header'>Aktuelle Ziele</div>", unsafe_allow_html=True)
        kh_aktuell = db.get_kh_ziel()
        ziel_cols  = st.columns(4)
        for col, (label, wert, sub) in zip(ziel_cols, [
            ("🔥 Kalorien", f"{kcal_ziel:.0f} kcal", f"TDEE: {config.TDEE_KCAL} kcal"),
            ("💪 Protein",  f"{config.PROTEIN_ZIEL_G} g", "2,3g/kg Körpergew."),
            ("🍞 Kohlenhydrate", f"{kh_aktuell:.0f} g", "Richtwert"),
            ("🫒 Fett",     f"{config.FETT_RICHTWERT_G} g", "Richtwert"),
        ]):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.3rem;'>{wert}</div>
                  <div class='metric-label'>{label}</div>
                  <div class='metric-sub'>{sub}</div>
                </div>
                """, unsafe_allow_html=True)

