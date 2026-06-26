"""
app.py – Hauptdatei: "Die Sueben Transformation"
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
    page_title="Die Sueben Transformation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Datenbank initialisieren (einmalig beim ersten Start)
db.init_db()

# Globales CSS für Dark Mode & sportliches Design
st.markdown(f"""
<style>
  /* ── Basis Dark Mode ──────────────────────────────────────────────────── */
  .stApp {{
    background-color: {config.BG_DARK};
    color: #E2E8F0;
  }}
  .block-container {{
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1100px;
  }}

  /* ── Header-Banner ────────────────────────────────────────────────────── */
  .app-header {{
    background: linear-gradient(135deg, #1a0a00 0%, #2d1200 50%, #1a0a00 100%);
    border: 1px solid {config.BRAND_COLOR}44;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }}
  .app-header::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, {config.BRAND_COLOR}11 0%, transparent 60%);
    pointer-events: none;
  }}
  .app-title {{
    font-size: 2.2rem;
    font-weight: 900;
    color: {config.BRAND_COLOR};
    letter-spacing: -0.02em;
    margin: 0;
    text-shadow: 0 0 30px {config.BRAND_COLOR}66;
  }}
  .app-subtitle {{
    font-size: 0.95rem;
    color: #94A3B8;
    margin: 0.2rem 0 0 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}

  /* ── Metrikkarten ─────────────────────────────────────────────────────── */
  .metric-card {{
    background: {config.CARD_BG};
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: border-color 0.2s;
  }}
  .metric-card:hover {{
    border-color: {config.BRAND_COLOR}66;
  }}
  .metric-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {config.BRAND_COLOR};
    line-height: 1;
  }}
  .metric-label {{
    font-size: 0.75rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
  }}
  .metric-sub {{
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 0.15rem;
  }}

  /* ── Fortschrittsbalken ───────────────────────────────────────────────── */
  .progress-bar-wrap {{
    background: #2D3748;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin: 0.4rem 0;
  }}
  .progress-bar-fill {{
    height: 100%;
    border-radius: 999px;
    transition: width 0.5s ease;
  }}

  /* ── Mahlzeiten-Slot ──────────────────────────────────────────────────── */
  .meal-slot {{
    background: {config.CARD_BG};
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
  }}
  .meal-slot-title {{
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
  }}

  /* ── Warnbox (Sjard-Tipp) ─────────────────────────────────────────────── */
  .warn-box {{
    background: {config.WARNING_COLOR}18;
    border-left: 3px solid {config.WARNING_COLOR};
    border-radius: 0 6px 6px 0;
    padding: 0.5rem 0.8rem;
    font-size: 0.82rem;
    color: {config.WARNING_COLOR};
    margin-top: 0.4rem;
  }}
  .plateau-box {{
    background: {config.ERROR_COLOR}15;
    border: 1px solid {config.ERROR_COLOR}66;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
  }}
  .foto-box {{
    background: #7C3AED18;
    border: 1px solid #7C3AED88;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin: 0.8rem 0;
  }}
  .success-box {{
    background: {config.SUCCESS_COLOR}15;
    border: 1px solid {config.SUCCESS_COLOR}66;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin: 0.8rem 0;
  }}

  /* ── Streak-Anzeige ───────────────────────────────────────────────────── */
  .streak-display {{
    font-size: 4rem;
    font-weight: 900;
    color: {config.BRAND_COLOR};
    text-align: center;
    line-height: 1;
    text-shadow: 0 0 40px {config.BRAND_COLOR}88;
  }}
  .streak-label {{
    text-align: center;
    font-size: 0.85rem;
    color: #64748B;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}

  /* ── Abschnitts-Header ────────────────────────────────────────────────── */
  .section-header {{
    font-size: 0.7rem;
    font-weight: 800;
    color: {config.BRAND_COLOR};
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid {config.BRAND_COLOR}33;
  }}

  /* ── Streamlit-Widgets anpassen ───────────────────────────────────────── */
  div[data-testid="stNumberInput"] input,
  div[data-testid="stTextInput"] input {{
    background-color: #1A2035 !important;
    border: 1px solid #2D3748 !important;
    color: #E2E8F0 !important;
    border-radius: 6px !important;
  }}
  div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    background-color: #1A2035 !important;
    border: 1px solid #2D3748 !important;
  }}
  .stButton > button {{
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
  }}
  .stButton > button[kind="primary"] {{
    background: {config.BRAND_COLOR} !important;
    border: none !important;
    color: white !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    background: #c44008 !important;
    box-shadow: 0 4px 20px {config.BRAND_COLOR}44 !important;
    transform: translateY(-1px) !important;
  }}
  div[data-testid="stCheckbox"] label {{
    color: #CBD5E1 !important;
  }}
  .stTabs [data-baseweb="tab-list"] {{
    background-color: {config.CARD_BG} !important;
    border-radius: 8px !important;
    padding: 0.3rem !important;
    gap: 0.2rem !important;
  }}
  .stTabs [data-baseweb="tab"] {{
    border-radius: 6px !important;
    color: #64748B !important;
    font-weight: 600 !important;
  }}
  .stTabs [aria-selected="true"] {{
    background-color: {config.BRAND_COLOR} !important;
    color: white !important;
  }}
  div[data-testid="stSeparator"] {{
    border-color: #2D3748 !important;
  }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION-STATE INITIALISIERUNG
# ══════════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialisiert alle Session-State-Variablen."""
    heute = date.today()
    vorhandener_log = db.load_daily_log(heute)

    # Mahlzeiten-Slots (Liste von Dicts)
    if "slots" not in st.session_state:
        if vorhandener_log and vorhandener_log["mahlzeiten"]:
            st.session_state.slots = vorhandener_log["mahlzeiten"]
        else:
            st.session_state.slots = [
                {"name": f"Mahlzeit {i+1}", "kcal": 0.0, "protein": 0.0}
                for i in range(config.STANDARD_SLOTS)
            ]

    # Tagesformular-Defaults aus vorhandenem Log
    if "form_loaded" not in st.session_state:
        st.session_state.form_loaded = True
        if vorhandener_log:
            st.session_state.gewicht   = vorhandener_log.get("gewicht_kg")   or config.STARTGEWICHT_KG
            st.session_state.schlaf    = vorhandener_log.get("schlaf_std")   or 7.5
            st.session_state.schritte  = bool(vorhandener_log.get("habit_schritte"))
            st.session_state.wasser    = bool(vorhandener_log.get("habit_wasser"))
            st.session_state.training  = bool(vorhandener_log.get("habit_training"))
            st.session_state.neat      = bool(vorhandener_log.get("habit_neat"))
            st.session_state.clean     = bool(vorhandener_log.get("habit_clean"))
            st.session_state.creatin   = vorhandener_log.get("supp_creatin_g") or config.CREATINE_DEFAULT_G
            st.session_state.omega3    = vorhandener_log.get("supp_omega3_g")  or config.OMEGA3_DEFAULT_G
            st.session_state.vitamine  = bool(vorhandener_log.get("supp_vitamine"))
            st.session_state.bauch_cm  = vorhandener_log.get("bauch_cm") or 0.0
            st.session_state.brust_cm  = vorhandener_log.get("brust_cm") or 0.0
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
            st.session_state.bauch_cm  = 0.0
            st.session_state.brust_cm  = 0.0

    if "gespeichert_heute" not in st.session_state:
        st.session_state.gespeichert_heute = vorhandener_log is not None


init_session_state()

# ══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN FÜR UI-ELEMENTE
# ══════════════════════════════════════════════════════════════════════════════

def fortschrittsbalken(wert: float, ziel: float, farbe: str, einheit: str = "") -> str:
    pct = min((wert / ziel) * 100, 100) if ziel > 0 else 0
    return f"""
    <div class='progress-bar-wrap'>
      <div class='progress-bar-fill' style='width:{pct:.1f}%;background:{farbe};'></div>
    </div>
    <div style='display:flex;justify-content:space-between;font-size:0.78rem;color:#64748B;'>
      <span>{wert:.0f}{einheit}</span><span>Ziel: {ziel:.0f}{einheit}</span>
    </div>
    """


def makro_karte(label: str, wert: float, ziel: float, einheit: str, farbe: str) -> str:
    pct = min((wert / ziel) * 100, 100) if ziel > 0 else 0
    return f"""
    <div class='metric-card'>
      <div class='metric-value' style='color:{farbe};font-size:1.5rem;'>{wert:.0f}<span style='font-size:0.8rem;color:#64748B;'>{einheit}</span></div>
      <div class='metric-label'>{label}</div>
      <div class='progress-bar-wrap' style='margin-top:0.4rem;'>
        <div class='progress-bar-fill' style='width:{pct:.1f}%;background:{farbe};'></div>
      </div>
      <div class='metric-sub'>{pct:.0f}% von {ziel:.0f}{einheit}</div>
    </div>
    """


def berechne_slot_summen() -> tuple[float, float]:
    kcal    = sum(s.get("kcal",    0) for s in st.session_state.slots)
    protein = sum(s.get("protein", 0) for s in st.session_state.slots)
    return kcal, protein


# ══════════════════════════════════════════════════════════════════════════════
# APP-HEADER
# ══════════════════════════════════════════════════════════════════════════════

heute    = date.today()
tag_nr   = logic.berechne_tag_nummer(heute)
alle_logs = db.load_all_logs()
streak   = logic.berechne_streak(alle_logs)
kcal_ziel = db.get_kcal_ziel()

st.markdown(f"""
<div class='app-header'>
  <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;'>
    <div>
      <div class='app-title'>⚡ Die Sueben Transformation</div>
      <div class='app-subtitle'>90 Tage bis zur Bestform &nbsp;|&nbsp; FC Suebia Edition</div>
    </div>
    <div style='display:flex;gap:1.5rem;align-items:center;'>
      <div style='text-align:center;'>
        <div style='font-size:2.5rem;font-weight:900;color:{config.BRAND_COLOR};line-height:1;'>{tag_nr}</div>
        <div style='font-size:0.65rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;'>von 90 Tagen</div>
      </div>
      <div style='text-align:center;'>
        <div style='font-size:2.5rem;font-weight:900;color:{config.SUCCESS_COLOR};line-height:1;'>🔥 {streak}</div>
        <div style='font-size:0.65rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;'>Streak</div>
      </div>
      <div style='text-align:center;'>
        <div style='font-size:1.3rem;font-weight:700;color:#94A3B8;line-height:1;'>{heute.strftime("%d.%m.%Y")}</div>
        <div style='font-size:0.65rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;'>{heute.strftime("%A")}</div>
      </div>
    </div>
  </div>
  <div style='margin-top:1rem;'>
    <div class='progress-bar-wrap' style='height:6px;'>
      <div class='progress-bar-fill' style='width:{(tag_nr/90)*100:.1f}%;background:linear-gradient(90deg,{config.BRAND_COLOR},{config.WARNING_COLOR});'></div>
    </div>
    <div style='font-size:0.72rem;color:#475569;margin-top:0.3rem;text-align:right;'>{90-tag_nr} Tage verbleibend</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_checkin, tab_progress = st.tabs([
    "📋  Daily Check-In",
    "📊  Progress Hub",
])

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1: DAILY CHECK-IN                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_checkin:

    # ── Foto-Erinnerung ──────────────────────────────────────────────────────
    if logic.foto_erinnerung_aktiv(alle_logs) and tag_nr > 0:
        st.markdown(f"""
        <div class='foto-box'>
          📸 <strong>14-Tage-Foto-Check!</strong> &nbsp;
          Tag {tag_nr} – Zeit für deine Fortschrittsfotos! Halte deine Transformation fest.
        </div>
        """, unsafe_allow_html=True)

    # ── Plateau-Warnung & Schaltfläche ───────────────────────────────────────
    gewichtsverlauf = db.get_gewichts_verlauf()
    plateau = logic.pruefe_plateau(gewichtsverlauf)
    if plateau:
        st.markdown(f"""
        <div class='plateau-box'>
          ⚠️ <strong>Stagnation erkannt!</strong> Dein Gewicht hat sich in den letzten 3 Wochen
          um weniger als {config.PLATEAU_DELTA_KG} kg verändert. Kein Grund zur Panik –
          das ist normal! Bereit für den nächsten Schritt?
        </div>
        """, unsafe_allow_html=True)
        if st.button(
            f"🔧 Kalorien um 5% senken (–{config.KCAL_REDUKTION} kcal)",
            type="primary",
            key="plateau_btn"
        ):
            db.senke_kcal_ziel(config.KCAL_REDUKTION, config.KH_REDUKTION_G)
            kcal_ziel = db.get_kcal_ziel()
            st.success(f"✅ Neues Kalorienziel: {kcal_ziel:.0f} kcal | KH: {db.get_kh_ziel():.0f} g")
            st.rerun()

    # ── A. MORGENS ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>A — Morgens · Schnelle Kennzahlen</div>", unsafe_allow_html=True)

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
    st.markdown("<div class='section-header'>B — Ernährung · Makro-Tracking</div>", unsafe_allow_html=True)

    # Makro-Übersichts-Dashboard (live aktualisiert)
    kcal_summe, protein_summe = berechne_slot_summen()
    kh_ziel_aktuell = db.get_kh_ziel()

    kcal_pct, kcal_farbe = logic.berechne_kcal_fortschritt(kcal_summe, kcal_ziel)
    prot_pct = min((protein_summe / config.PROTEIN_ZIEL_G) * 100, 100)
    prot_farbe = config.SUCCESS_COLOR if prot_pct >= 100 else (config.WARNING_COLOR if prot_pct >= 80 else config.ERROR_COLOR)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(makro_karte("Kalorien", kcal_summe, kcal_ziel, "kcal", kcal_farbe), unsafe_allow_html=True)
    with m2:
        st.markdown(makro_karte("Protein", protein_summe, config.PROTEIN_ZIEL_G, "g", prot_farbe), unsafe_allow_html=True)
    with m3:
        # Restliche Kapazität visualisieren
        rest_kcal = max(0, kcal_ziel - kcal_summe)
        rest_farbe = config.SUCCESS_COLOR if rest_kcal > 200 else config.WARNING_COLOR
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-value' style='color:{rest_farbe};font-size:1.5rem;'>{rest_kcal:.0f}<span style='font-size:0.8rem;color:#64748B;'>kcal</span></div>
          <div class='metric-label'>Noch verfügbar</div>
          <div class='metric-sub'>Ziel: {kcal_ziel:.0f} kcal</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")  # Abstand

    # ── Schnellauswahl ───────────────────────────────────────────────────────
    st.markdown("**🔍 Schnellauswahl – Lieblingslebensmittel**")
    food_optionen = ["— Lebensmittel wählen —"] + [f["name"] for f in config.QUICK_FOODS]

    qcol1, qcol2, qcol3 = st.columns([3, 2, 1])
    with qcol1:
        selected_food = st.selectbox(
            "Lebensmittel",
            options=food_optionen,
            label_visibility="collapsed",
            key="quick_food_select",
        )
    with qcol2:
        slot_optionen = [f"Mahlzeit {i+1}" for i in range(len(st.session_state.slots))]
        selected_slot = st.selectbox(
            "Zu Mahlzeit",
            options=slot_optionen,
            label_visibility="collapsed",
            key="quick_slot_select",
        )
    with qcol3:
        if st.button("➕ Hinzufügen", use_container_width=True):
            if selected_food != "— Lebensmittel wählen —":
                # Lebensmitteldaten finden
                food_data = next(
                    (f for f in config.QUICK_FOODS if f["name"] == selected_food), None
                )
                if food_data:
                    slot_idx = int(selected_slot.split(" ")[-1]) - 1
                    st.session_state.slots[slot_idx]["kcal"]    += food_data["kcal"]
                    st.session_state.slots[slot_idx]["protein"] += food_data["protein"]
                    if not st.session_state.slots[slot_idx]["name"] or \
                       st.session_state.slots[slot_idx]["name"].startswith("Mahlzeit"):
                        st.session_state.slots[slot_idx]["name"] = food_data["name"]
                    st.rerun()

    # Info-Zeile für gewähltes Lebensmittel
    if selected_food != "— Lebensmittel wählen —":
        food_info = next((f for f in config.QUICK_FOODS if f["name"] == selected_food), None)
        if food_info:
            st.caption(
                f"📊 {food_info['name']}: **{food_info['kcal']} kcal** | **{food_info['protein']} g Protein**"
            )

    st.write("")  # Abstand

    # ── Mahlzeiten-Slots ─────────────────────────────────────────────────────
    for i, slot in enumerate(st.session_state.slots):
        with st.container():
            st.markdown(f"<div class='meal-slot-title'>🍽 Mahlzeit {i+1}</div>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns([3, 2, 2])
            with sc1:
                name = st.text_input(
                    "Bezeichnung",
                    value=slot.get("name", f"Mahlzeit {i+1}"),
                    key=f"slot_name_{i}",
                    label_visibility="collapsed",
                    placeholder=f"z.B. Frühstück...",
                )
                st.session_state.slots[i]["name"] = name
            with sc2:
                kcal_val = st.number_input(
                    "kcal",
                    min_value=0.0,
                    max_value=5000.0,
                    step=5.0,
                    value=float(slot.get("kcal", 0)),
                    key=f"slot_kcal_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.slots[i]["kcal"] = kcal_val
            with sc3:
                protein_val = st.number_input(
                    "Protein (g)",
                    min_value=0.0,
                    max_value=500.0,
                    step=1.0,
                    value=float(slot.get("protein", 0)),
                    key=f"slot_prot_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.slots[i]["protein"] = protein_val

            # Sjard-Tipp anzeigen, wenn Eintrag vorhanden aber Protein niedrig
            if kcal_val > 0 and protein_val < config.PROTEIN_SLOT_WARN:
                st.markdown(
                    f"<div class='warn-box'>💡 Sjard-Tipp: Erhöhe das Protein für optimalen Muskelschutz! "
                    f"(Ziel ≥ {config.PROTEIN_SLOT_WARN}g pro Mahlzeit)</div>",
                    unsafe_allow_html=True,
                )
            st.write("")

    # Weiteren Slot hinzufügen
    if st.button("➕ Weiteren Slot hinzufügen", use_container_width=False):
        n = len(st.session_state.slots) + 1
        st.session_state.slots.append({"name": f"Mahlzeit {n}", "kcal": 0.0, "protein": 0.0})
        st.rerun()

    # ── C. ABENDS: HABITS ────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>C — Abends · Habits & Supplements</div>", unsafe_allow_html=True)

    st.markdown("**✅ Tägliche Gewohnheiten**")

    hab_col1, hab_col2 = st.columns(2)
    with hab_col1:
        h_schritte = st.checkbox(
            f"🚶 {config.HABIT_SCHRITTE_ZIEL:,} Schritte erreicht".replace(",", "."),
            value=st.session_state.schritte,
            key="cb_schritte",
        )
        h_wasser = st.checkbox(
            f"💧 {config.WASSER_ZIEL_LITER} Liter Wasser getrunken",
            value=st.session_state.wasser,
            key="cb_wasser",
        )
        h_training = st.checkbox(
            "🏋️ Krafttraining absolviert",
            value=st.session_state.training,
            key="cb_training",
        )
    with hab_col2:
        h_neat = st.checkbox(
            "🪜 NEAT-Fokus (Treppen, Stehschreibtisch)",
            value=st.session_state.neat,
            key="cb_neat",
        )
        h_clean = st.checkbox(
            "🥗 Clean Eating eingehalten (80/20)",
            value=st.session_state.clean,
            key="cb_clean",
        )

    # Habits-Fortschrittsbalken
    habits_erreicht = sum([h_schritte, h_wasser, h_training, h_neat, h_clean])
    hab_pct = (habits_erreicht / 5) * 100
    hab_farbe = config.SUCCESS_COLOR if hab_pct >= 80 else (config.WARNING_COLOR if hab_pct >= 60 else config.ERROR_COLOR)
    st.markdown(
        f"<div style='font-size:0.8rem;color:#64748B;margin-top:0.3rem;'>"
        f"Habits: {habits_erreicht}/5"
        f"</div>"
        f"{fortschrittsbalken(habits_erreicht, 5, hab_farbe, '')}",
        unsafe_allow_html=True
    )

    # ── Supplements ──────────────────────────────────────────────────────────
    st.write("")
    st.markdown("**💊 Supplements**")

    sup_col1, sup_col2, sup_col3 = st.columns([2, 2, 3])
    with sup_col1:
        s_creatin = st.number_input(
            "Creatin Monohydrat (g)",
            min_value=0.0, max_value=20.0, step=0.5,
            value=float(st.session_state.creatin),
            key="input_creatin",
        )
    with sup_col2:
        s_omega3 = st.number_input(
            "Omega 3 (g)",
            min_value=0.0, max_value=20.0, step=0.5,
            value=float(st.session_state.omega3),
            key="input_omega3",
        )
    with sup_col3:
        s_vitamine = st.checkbox(
            "🧡 Vitamine & Zink genommen (D3/K2, Multi, Zink)",
            value=st.session_state.vitamine,
            key="cb_vitamine",
        )

    # ── Wöchentliche Messungen (Sonntags oder manuell) ───────────────────────
    st.write("")
    ist_sonntag = logic.ist_sonntag(heute)
    messung_aktiv = st.checkbox(
        "📏 Wöchentliche Körpermessungen erfassen"
        + (" (Sonntags-Messung! 📅)" if ist_sonntag else ""),
        value=ist_sonntag,
        key="cb_messung",
    )
    if messung_aktiv:
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            bauch_cm = st.number_input(
                "Bauchumfang (cm)",
                min_value=50.0, max_value=200.0, step=0.5,
                value=float(st.session_state.bauch_cm) if st.session_state.bauch_cm else 80.0,
                key="input_bauch",
            )
        with m_col2:
            brust_cm = st.number_input(
                "Brustumfang (cm)",
                min_value=50.0, max_value=200.0, step=0.5,
                value=float(st.session_state.brust_cm) if st.session_state.brust_cm else 95.0,
                key="input_brust",
            )
    else:
        bauch_cm = None
        brust_cm = None

    # ── SPEICHERN ────────────────────────────────────────────────────────────
    st.write("")
    st.divider()

    # Zeige gespeichert-Meldung, falls bereits gespeichert
    if st.session_state.gespeichert_heute:
        st.markdown(
            f"<div class='success-box'>✅ Heutiger Tag bereits gespeichert – du kannst die Daten "
            f"jederzeit überschreiben.</div>",
            unsafe_allow_html=True,
        )

    save_btn = st.button(
        "💾  Heutigen Tag speichern",
        type="primary",
        use_container_width=True,
        key="save_btn",
    )

    if save_btn:
        # Slot-Werte aktualisieren (Nummer-Inputs werden direkt in session_state gespiegelt)
        mahlzeiten = [
            {
                "name":    st.session_state.get(f"slot_name_{i}", f"Mahlzeit {i+1}"),
                "kcal":    st.session_state.get(f"slot_kcal_{i}", 0.0),
                "protein": st.session_state.get(f"slot_prot_{i}", 0.0),
            }
            for i in range(len(st.session_state.slots))
        ]

        habits = {
            "schritte": h_schritte,
            "wasser":   h_wasser,
            "training": h_training,
            "neat":     h_neat,
            "clean":    h_clean,
        }
        supplements = {
            "creatin_g": s_creatin,
            "omega3_g":  s_omega3,
            "vitamine":  s_vitamine,
        }

        db.save_daily_log(
            log_date    = heute,
            gewicht_kg  = gewicht,
            schlaf_std  = schlaf,
            mahlzeiten  = mahlzeiten,
            habits      = habits,
            supplements = supplements,
            bauch_cm    = bauch_cm,
            brust_cm    = brust_cm,
        )

        st.session_state.gespeichert_heute = True
        st.session_state.slots = mahlzeiten  # Slots aus Widgets synchronisieren

        # Konfetti-Animation & Erfolgsmeldung
        kcal_ok  = sum(m["kcal"]    for m in mahlzeiten) <= kcal_ziel
        prot_ok  = sum(m["protein"] for m in mahlzeiten) >= config.PROTEIN_ZIEL_G
        if kcal_ok and prot_ok:
            st.balloons()
            st.success("🎉 Perfekt! Kalorien UND Protein im Ziel – Sjard wäre stolz auf dich!")
        elif kcal_ok:
            st.success("✅ Gespeichert! Kalorien stimmen – vergiss das Protein beim nächsten Mal nicht!")
        elif prot_ok:
            st.warning("⚠️ Gespeichert! Protein erreicht – aber Achtung: Kalorien überschritten!")
        else:
            st.info("💾 Gespeichert! Morgen wieder angreifen – du schaffst das!")
        st.rerun()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2: PROGRESS HUB                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_progress:

    if len(alle_logs) == 0:
        st.info("Noch keine Daten vorhanden. Starte mit deinem ersten Check-In!")
    else:
        # ── Streak & Statistik-Karten ─────────────────────────────────────────
        st.markdown("<div class='section-header'>Übersicht</div>", unsafe_allow_html=True)

        # Streak-Anzeige
        streak_col, days_col, avg_col, best_col = st.columns(4)

        with streak_col:
            st.markdown(
                f"<div class='streak-display'>🔥 {streak}</div>"
                f"<div class='streak-label'>Aktuelle Streak</div>",
                unsafe_allow_html=True,
            )

        with days_col:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='metric-value'>{len(alle_logs)}</div>
              <div class='metric-label'>Tage geloggt</div>
              <div class='metric-sub'>von 90 gesamt</div>
            </div>
            """, unsafe_allow_html=True)

        # Durchschnittsgewicht letzte 7 Tage
        gew_verlauf = db.get_gewichts_verlauf()
        if gew_verlauf:
            letzte_7 = [r["gewicht_kg"] for r in gew_verlauf[-7:] if r["gewicht_kg"]]
            avg_gew  = sum(letzte_7) / len(letzte_7) if letzte_7 else 0
            with avg_col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.6rem;'>{avg_gew:.1f}<span style='font-size:0.8rem;color:#64748B;'>kg</span></div>
                  <div class='metric-label'>Ø Gewicht (7d)</div>
                  <div class='metric-sub'>Start: {config.STARTGEWICHT_KG} kg</div>
                </div>
                """, unsafe_allow_html=True)

            # Gesamte Veränderung
            delta = avg_gew - config.STARTGEWICHT_KG
            delta_str = f"{'–' if delta < 0 else '+'}{abs(delta):.1f} kg"
            delta_farbe = config.SUCCESS_COLOR if delta < 0 else config.ERROR_COLOR
            with best_col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.6rem;color:{delta_farbe};'>{delta_str}</div>
                  <div class='metric-label'>Gesamt-Veränderung</div>
                  <div class='metric-sub'>seit {config.STARTDATUM.strftime("%d.%m.%Y")}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Gewichtskurve ─────────────────────────────────────────────────────
        if gew_verlauf:
            st.markdown("<div class='section-header'>Gewichtsverlauf</div>", unsafe_allow_html=True)

            df_gew = pd.DataFrame(gew_verlauf)
            df_gew["log_date"] = pd.to_datetime(df_gew["log_date"])
            df_gew = df_gew.sort_values("log_date")

            gewichte_liste = df_gew["gewicht_kg"].tolist()
            glatt = logic.gleitender_durchschnitt(gewichte_liste, fenster=7)
            df_gew["avg_7d"] = glatt

            fig_gew = go.Figure()

            # Tägliche Messwerte (zittrige Linie)
            fig_gew.add_trace(go.Scatter(
                x=df_gew["log_date"],
                y=df_gew["gewicht_kg"],
                name="Tagesgewicht",
                mode="lines+markers",
                line=dict(color="#475569", width=1, dash="dot"),
                marker=dict(size=4, color="#64748B"),
                hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.1f} kg</b><extra></extra>",
            ))

            # 7-Tage-Glättung (fette Linie)
            df_avg = df_gew.dropna(subset=["avg_7d"])
            if not df_avg.empty:
                fig_gew.add_trace(go.Scatter(
                    x=df_avg["log_date"],
                    y=df_avg["avg_7d"],
                    name="7-Tage-Durchschnitt",
                    mode="lines",
                    line=dict(color=config.BRAND_COLOR, width=3),
                    hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.2f} kg</b> (Ø7d)<extra></extra>",
                ))

            # Startgewicht-Referenzlinie
            fig_gew.add_hline(
                y=config.STARTGEWICHT_KG,
                line=dict(color="#374151", width=1, dash="dash"),
                annotation_text=f"Start {config.STARTGEWICHT_KG} kg",
                annotation_font=dict(color="#6B7280", size=11),
            )

            fig_gew.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", size=12),
                legend=dict(
                    bgcolor="rgba(30,33,48,0.8)",
                    bordercolor="#2D3748",
                    borderwidth=1,
                    font=dict(size=11),
                ),
                xaxis=dict(
                    gridcolor="#1E2A3A",
                    showgrid=True,
                    tickformat="%d.%m",
                ),
                yaxis=dict(
                    gridcolor="#1E2A3A",
                    showgrid=True,
                    title="Gewicht (kg)",
                    tickformat=".1f",
                ),
                margin=dict(l=0, r=0, t=20, b=0),
                hovermode="x unified",
            )
            st.plotly_chart(fig_gew, use_container_width=True)

        # ── Umfangskurve ──────────────────────────────────────────────────────
        umfangs_verlauf = db.get_umfangs_verlauf()
        if umfangs_verlauf:
            st.markdown("<div class='section-header'>Körpermaße</div>", unsafe_allow_html=True)

            df_um = pd.DataFrame(umfangs_verlauf)
            df_um["log_date"] = pd.to_datetime(df_um["log_date"])

            fig_um = go.Figure()
            if df_um["bauch_cm"].notna().any():
                fig_um.add_trace(go.Scatter(
                    x=df_um["log_date"],
                    y=df_um["bauch_cm"],
                    name="Bauchumfang",
                    mode="lines+markers",
                    line=dict(color=config.BRAND_COLOR, width=2),
                    marker=dict(size=6),
                    hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.1f} cm</b><extra>Bauch</extra>",
                ))
            if df_um["brust_cm"].notna().any():
                fig_um.add_trace(go.Scatter(
                    x=df_um["log_date"],
                    y=df_um["brust_cm"],
                    name="Brustumfang",
                    mode="lines+markers",
                    line=dict(color=config.SUCCESS_COLOR, width=2),
                    marker=dict(size=6),
                    hovertemplate="%{x|%d.%m.%Y}: <b>%{y:.1f} cm</b><extra>Brust</extra>",
                ))

            fig_um.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", size=12),
                legend=dict(
                    bgcolor="rgba(30,33,48,0.8)",
                    bordercolor="#2D3748",
                    borderwidth=1,
                ),
                xaxis=dict(gridcolor="#1E2A3A", tickformat="%d.%m"),
                yaxis=dict(gridcolor="#1E2A3A", title="Umfang (cm)"),
                margin=dict(l=0, r=0, t=20, b=0),
                hovermode="x unified",
            )
            st.plotly_chart(fig_um, use_container_width=True)

        # ── Letzte 14 Tage Übersicht (Tabelle) ───────────────────────────────
        st.markdown("<div class='section-header'>Letzte 14 Tage</div>", unsafe_allow_html=True)

        letzte_logs = alle_logs[-14:][::-1]  # Neueste zuerst
        if letzte_logs:
            tabellen_data = []
            for log in letzte_logs:
                datum = log["log_date"]
                tabellen_data.append({
                    "Datum":         datum,
                    "Gewicht (kg)":  f"{log['gewicht_kg']:.1f}" if log.get("gewicht_kg") else "–",
                    "kcal":          f"{log['kcal_gesamt']:.0f}" if log.get("kcal_gesamt") else "–",
                    "Protein (g)":   f"{log['protein_gesamt']:.0f}" if log.get("protein_gesamt") else "–",
                    "Schlaf (h)":    f"{log['schlaf_std']:.1f}" if log.get("schlaf_std") else "–",
                    "Habits ✓":      sum([
                        bool(log.get("habit_schritte")),
                        bool(log.get("habit_wasser")),
                        bool(log.get("habit_training")),
                        bool(log.get("habit_neat")),
                        bool(log.get("habit_clean")),
                    ]),
                })

            df_table = pd.DataFrame(tabellen_data)
            st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Habits ✓": st.column_config.ProgressColumn(
                        "Habits",
                        min_value=0,
                        max_value=5,
                        format="%d/5",
                    ),
                },
            )

        # ── Aktuelle Ziele anzeigen ───────────────────────────────────────────
        st.markdown("<div class='section-header'>Aktuelle Ziele</div>", unsafe_allow_html=True)
        kh_aktuell = db.get_kh_ziel()
        ziel_cols = st.columns(4)
        ziel_daten = [
            ("🔥 Kalorien", f"{kcal_ziel:.0f} kcal", f"TDEE: {config.TDEE_KCAL} kcal"),
            ("💪 Protein",  f"{config.PROTEIN_ZIEL_G} g",        "2,3g/kg Körpergew."),
            ("🍞 Kohlenh.",  f"{kh_aktuell:.0f} g",  "Richtwert"),
            ("🫒 Fett",      f"{config.FETT_RICHTWERT_G} g", "Richtwert"),
        ]
        for col, (label, wert, sub) in zip(ziel_cols, ziel_daten):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                  <div class='metric-value' style='font-size:1.3rem;'>{wert}</div>
                  <div class='metric-label'>{label}</div>
                  <div class='metric-sub'>{sub}</div>
                </div>
                """, unsafe_allow_html=True)
