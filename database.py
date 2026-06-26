"""
database.py – Datenbankschicht mit automatischem Backend-Wechsel:
  - Lokal (kein Secret gesetzt): SQLite
  - Cloud (Streamlit Secrets gesetzt): PostgreSQL (Supabase)
"""

import json
import os
from datetime import date
from pathlib import Path
from typing import Optional

import streamlit as st

# ── Backend erkennen ─────────────────────────────────────────────────────────

def _use_postgres() -> bool:
    """True wenn DATABASE_URL in Streamlit Secrets hinterlegt ist."""
    try:
        return bool(st.secrets.get("DATABASE_URL"))
    except Exception:
        return False


def _get_pg_conn():
    """PostgreSQL-Verbindung über Supabase DATABASE_URL."""
    import psycopg2
    import psycopg2.extras
    url = st.secrets["DATABASE_URL"]
    if "sslmode" not in url:
        url += "?sslmode=require"
    conn = psycopg2.connect(url)
    return conn


def _get_sqlite_conn():
    """SQLite-Verbindung für lokale Nutzung."""
    import sqlite3
    DB_PATH = Path(__file__).parent / "sueben_transformation.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ══════════════════════════════════════════════════════════════════════════════
# INITIALISIERUNG
# ══════════════════════════════════════════════════════════════════════════════

def init_db() -> None:
    """Erstellt alle Tabellen beim ersten Start."""
    if _use_postgres():
        _init_postgres()
    else:
        _init_sqlite()


def _init_sqlite() -> None:
    import sqlite3
    conn = _get_sqlite_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_date        TEXT PRIMARY KEY,
            gewicht_kg      REAL,
            schlaf_std      REAL,
            mahlzeiten_json TEXT DEFAULT '[]',
            kcal_gesamt     REAL DEFAULT 0,
            protein_gesamt  REAL DEFAULT 0,
            habit_schritte  INTEGER DEFAULT 0,
            habit_wasser    INTEGER DEFAULT 0,
            habit_training  INTEGER DEFAULT 0,
            habit_neat      INTEGER DEFAULT 0,
            habit_clean     INTEGER DEFAULT 0,
            supp_creatin_g  REAL DEFAULT 5.0,
            supp_omega3_g   REAL DEFAULT 3.0,
            supp_vitamine   INTEGER DEFAULT 0,
            bauch_cm        REAL,
            brust_cm        REAL,
            kcal_ziel_heute REAL,
            erstellt_am     TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('kcal_ziel', '1993')")
    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('kh_ziel', '214')")
    conn.commit()
    conn.close()


def _init_postgres() -> None:
    conn = _get_pg_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_date        TEXT PRIMARY KEY,
            gewicht_kg      REAL,
            schlaf_std      REAL,
            mahlzeiten_json TEXT DEFAULT '[]',
            kcal_gesamt     REAL DEFAULT 0,
            protein_gesamt  REAL DEFAULT 0,
            habit_schritte  INTEGER DEFAULT 0,
            habit_wasser    INTEGER DEFAULT 0,
            habit_training  INTEGER DEFAULT 0,
            habit_neat      INTEGER DEFAULT 0,
            habit_clean     INTEGER DEFAULT 0,
            supp_creatin_g  REAL DEFAULT 5.0,
            supp_omega3_g   REAL DEFAULT 3.0,
            supp_vitamine   INTEGER DEFAULT 0,
            bauch_cm        REAL,
            brust_cm        REAL,
            kcal_ziel_heute REAL,
            erstellt_am     TEXT DEFAULT (now()::text)
        );
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    cur.execute("INSERT INTO settings (key, value) VALUES ('kcal_ziel', '1993') ON CONFLICT (key) DO NOTHING")
    cur.execute("INSERT INTO settings (key, value) VALUES ('kh_ziel', '214') ON CONFLICT (key) DO NOTHING")
    conn.commit()
    cur.close()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

def get_setting(key: str) -> Optional[str]:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return row[0] if row else None
    else:
        conn = _get_sqlite_conn()
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        conn.close()
        return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (key, value)
        )
        conn.commit(); cur.close(); conn.close()
    else:
        conn = _get_sqlite_conn()
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit(); conn.close()


def get_kcal_ziel() -> float:
    val = get_setting("kcal_ziel")
    return float(val) if val else 1993.0


def get_kh_ziel() -> float:
    val = get_setting("kh_ziel")
    return float(val) if val else 214.0


def senke_kcal_ziel(reduktion_kcal: float, reduktion_kh_g: float) -> None:
    set_setting("kcal_ziel", str(round(get_kcal_ziel() - reduktion_kcal, 1)))
    set_setting("kh_ziel",   str(round(get_kh_ziel()   - reduktion_kh_g, 1)))


def get_startdatum() -> Optional[date]:
    """Gibt das gespeicherte Startdatum zurück, oder None wenn noch nicht gestartet."""
    val = get_setting("startdatum")
    if val and len(val) == 10:
        try:
            return date.fromisoformat(val)
        except ValueError:
            return None
    return None


def set_startdatum(d: date) -> None:
    """Setzt das Startdatum der Challenge (einmalig)."""
    set_setting("startdatum", d.isoformat())


# ══════════════════════════════════════════════════════════════════════════════
# TAGES-LOGS SPEICHERN & LADEN
# ══════════════════════════════════════════════════════════════════════════════

def save_daily_log(
    log_date: date,
    gewicht_kg: float,
    schlaf_std: float,
    mahlzeiten: list,
    habits: dict,
    supplements: dict,
    bauch_cm: Optional[float] = None,
    brust_cm: Optional[float] = None,
) -> None:
    kcal_gesamt    = sum(m.get("kcal", 0)    for m in mahlzeiten)
    protein_gesamt = sum(m.get("protein", 0) for m in mahlzeiten)
    params = (
        log_date.isoformat(), gewicht_kg, schlaf_std,
        json.dumps(mahlzeiten), kcal_gesamt, protein_gesamt,
        int(habits.get("schritte", 0)), int(habits.get("wasser", 0)),
        int(habits.get("training", 0)), int(habits.get("neat", 0)),
        int(habits.get("clean", 0)),
        supplements.get("creatin_g", 5.0), supplements.get("omega3_g", 3.0),
        int(supplements.get("vitamine", 0)),
        bauch_cm, brust_cm, get_kcal_ziel(),
    )

    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_logs
              (log_date, gewicht_kg, schlaf_std, mahlzeiten_json, kcal_gesamt,
               protein_gesamt, habit_schritte, habit_wasser, habit_training,
               habit_neat, habit_clean, supp_creatin_g, supp_omega3_g,
               supp_vitamine, bauch_cm, brust_cm, kcal_ziel_heute)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (log_date) DO UPDATE SET
              gewicht_kg=EXCLUDED.gewicht_kg, schlaf_std=EXCLUDED.schlaf_std,
              mahlzeiten_json=EXCLUDED.mahlzeiten_json, kcal_gesamt=EXCLUDED.kcal_gesamt,
              protein_gesamt=EXCLUDED.protein_gesamt, habit_schritte=EXCLUDED.habit_schritte,
              habit_wasser=EXCLUDED.habit_wasser, habit_training=EXCLUDED.habit_training,
              habit_neat=EXCLUDED.habit_neat, habit_clean=EXCLUDED.habit_clean,
              supp_creatin_g=EXCLUDED.supp_creatin_g, supp_omega3_g=EXCLUDED.supp_omega3_g,
              supp_vitamine=EXCLUDED.supp_vitamine, bauch_cm=EXCLUDED.bauch_cm,
              brust_cm=EXCLUDED.brust_cm, kcal_ziel_heute=EXCLUDED.kcal_ziel_heute
        """, params)
        conn.commit(); cur.close(); conn.close()
    else:
        conn = _get_sqlite_conn()
        conn.execute("""
            INSERT OR REPLACE INTO daily_logs
              (log_date, gewicht_kg, schlaf_std, mahlzeiten_json, kcal_gesamt,
               protein_gesamt, habit_schritte, habit_wasser, habit_training,
               habit_neat, habit_clean, supp_creatin_g, supp_omega3_g,
               supp_vitamine, bauch_cm, brust_cm, kcal_ziel_heute)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, params)
        conn.commit(); conn.close()


def _row_to_dict(row, keys: list) -> dict:
    """Konvertiert DB-Zeile (Tuple oder sqlite3.Row) in Dict."""
    if hasattr(row, "keys"):
        d = dict(row)
    else:
        d = dict(zip(keys, row))
    d["mahlzeiten"] = json.loads(d.get("mahlzeiten_json") or "[]")
    return d


_LOG_KEYS = [
    "log_date","gewicht_kg","schlaf_std","mahlzeiten_json","kcal_gesamt",
    "protein_gesamt","habit_schritte","habit_wasser","habit_training",
    "habit_neat","habit_clean","supp_creatin_g","supp_omega3_g",
    "supp_vitamine","bauch_cm","brust_cm","kcal_ziel_heute","erstellt_am"
]


def load_daily_log(log_date: date) -> Optional[dict]:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM daily_logs WHERE log_date = %s", (log_date.isoformat(),))
        row = cur.fetchone()
        keys = [d[0] for d in cur.description]
        cur.close(); conn.close()
        return _row_to_dict(row, keys) if row else None
    else:
        conn = _get_sqlite_conn()
        row = conn.execute("SELECT * FROM daily_logs WHERE log_date = ?", (log_date.isoformat(),)).fetchone()
        conn.close()
        return _row_to_dict(row, _LOG_KEYS) if row else None


def load_all_logs() -> list:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM daily_logs ORDER BY log_date ASC")
        rows = cur.fetchall()
        keys = [d[0] for d in cur.description]
        cur.close(); conn.close()
        return [_row_to_dict(r, keys) for r in rows]
    else:
        conn = _get_sqlite_conn()
        rows = conn.execute("SELECT * FROM daily_logs ORDER BY log_date ASC").fetchall()
        conn.close()
        return [_row_to_dict(r, _LOG_KEYS) for r in rows]


def get_gewichts_verlauf() -> list:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT log_date, gewicht_kg FROM daily_logs WHERE gewicht_kg IS NOT NULL ORDER BY log_date ASC"
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [{"log_date": r[0], "gewicht_kg": r[1]} for r in rows]
    else:
        conn = _get_sqlite_conn()
        rows = conn.execute(
            "SELECT log_date, gewicht_kg FROM daily_logs WHERE gewicht_kg IS NOT NULL ORDER BY log_date ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_umfangs_verlauf() -> list:
    if _use_postgres():
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT log_date, bauch_cm, brust_cm FROM daily_logs "
            "WHERE bauch_cm IS NOT NULL OR brust_cm IS NOT NULL ORDER BY log_date ASC"
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [{"log_date": r[0], "bauch_cm": r[1], "brust_cm": r[2]} for r in rows]
    else:
        conn = _get_sqlite_conn()
        rows = conn.execute(
            "SELECT log_date, bauch_cm, brust_cm FROM daily_logs "
            "WHERE bauch_cm IS NOT NULL OR brust_cm IS NOT NULL ORDER BY log_date ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
