"""
backend/database.py
Centralized, thread-safe database management layer for HydroThermal Nexus-AI.
Handles all SQLite operations: telemetry, audit, alerts, user sessions.
"""

import sqlite3
import hashlib
import os
import uuid
import datetime
import pandas as pd
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

DB_AUDIT   = "nexus_audit.db"
DB_STORAGE = "nexus_storage.db"
DB_AUTH    = "nexus_auth.db"


@contextmanager
def get_conn(db_path: str):
    """Thread-safe SQLite connection context manager."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────
# SCHEMA MIGRATION HELPER
# ──────────────────────────────────────────────
def _col_names(conn, table: str) -> set:
    """Returns the set of column names for a given table."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"] for r in rows}


def _migrate_schemas():
    """
    Safely migrates existing tables to the new schema.
    Uses ALTER TABLE ADD COLUMN — safe to run on every startup.
    Handles the legacy 'user' column → 'username' rename for audit_logs.
    """
    with get_conn(DB_AUDIT) as conn:
        # ── audit_logs ──────────────────────────────────────────────
        if "audit_logs" in {r["name"] for r in
                            conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            cols = _col_names(conn, "audit_logs")

            # Add 'username' if missing
            if "username" not in cols:
                conn.execute("ALTER TABLE audit_logs ADD COLUMN username TEXT")
                # Copy legacy 'user' value into new 'username' column if it existed
                if "user" in cols:
                    conn.execute("UPDATE audit_logs SET username = \"user\" WHERE username IS NULL")

            # Add 'role' if missing
            if "role" not in cols:
                conn.execute("ALTER TABLE audit_logs ADD COLUMN role TEXT")

            # Add 'ip_hint' if missing
            if "ip_hint" not in cols:
                conn.execute("ALTER TABLE audit_logs ADD COLUMN ip_hint TEXT")

        # ── alerts ──────────────────────────────────────────────────
        if "alerts" in {r["name"] for r in
                        conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            cols = _col_names(conn, "alerts")
            for col, typedef in [("ack_by", "TEXT"), ("ack_at", "TEXT"),
                                  ("channel", "TEXT"), ("severity", "TEXT")]:
                if col not in cols:
                    conn.execute(f"ALTER TABLE alerts ADD COLUMN {col} {typedef}")

    with get_conn(DB_STORAGE) as conn:
        # ── telemetry_logs ───────────────────────────────────────────
        if "telemetry_logs" in {r["name"] for r in
                                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            cols = _col_names(conn, "telemetry_logs")
            for col, typedef in [("pressure_psi", "REAL"), ("thermal_temp_c", "REAL")]:
                if col not in cols:
                    conn.execute(f"ALTER TABLE telemetry_logs ADD COLUMN {col} {typedef}")


# ──────────────────────────────────────────────
# SCHEMA INITIALIZATION
# ──────────────────────────────────────────────
def initialize_all_databases():
    """Creates all database tables if they don't exist, then migrates schema."""
    with get_conn(DB_AUTH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'Viewer',
                email         TEXT,
                created_at    TEXT,
                last_login    TEXT,
                login_attempts INTEGER DEFAULT 0,
                locked_until  TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token         TEXT PRIMARY KEY,
                username      TEXT NOT NULL,
                role          TEXT NOT NULL,
                created_at    TEXT,
                expires_at    TEXT
            )
        """)

    with get_conn(DB_AUDIT) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT,
                username     TEXT,
                role         TEXT,
                action       TEXT,
                anomaly_type TEXT,
                details      TEXT,
                ip_hint      TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp    TEXT,
                severity     TEXT,
                channel      TEXT,
                title        TEXT,
                message      TEXT,
                acknowledged INTEGER DEFAULT 0,
                ack_by       TEXT,
                ack_at       TEXT
            )
        """)

    with get_conn(DB_STORAGE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp      TEXT,
                electricity_kwh REAL,
                water_litres   REAL,
                outdoor_temp_c REAL,
                humidity_pct   REAL,
                pressure_psi   REAL,
                thermal_temp_c REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS esg_metrics (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                date           TEXT,
                co2_saved_kg   REAL DEFAULT 0.0,
                water_saved_l  REAL DEFAULT 0.0,
                energy_saved_kwh REAL DEFAULT 0.0,
                esg_score      REAL DEFAULT 0.0
            )
        """)

    # Run migration after table creation to add any missing columns
    _migrate_schemas()



# ──────────────────────────────────────────────
# USER MANAGEMENT
# ──────────────────────────────────────────────
def _hash_password(password: str) -> str:
    """SHA-256 based password hash with application salt."""
    salt = "NexusAI_Sec_2026_$"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def seed_default_users():
    """Seeds or updates default demo users to guarantee valid credentials."""
    with get_conn(DB_AUTH) as conn:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_users = [
            ("admin",     "Admin@Nexus2026!",  "Admin",    "admin@nexus.ai"),
            ("operator1", "Operator@2026#",    "Operator", "ops@nexus.ai"),
            ("viewer1",   "Viewer@View123",    "Viewer",   "view@nexus.ai"),
        ]
        for uname, pwd, role, email in default_users:
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (uname,)).fetchone()
            pwd_hash = _hash_password(pwd)
            if existing:
                conn.execute(
                    "UPDATE users SET password_hash = ?, role = ?, email = ? WHERE username = ?",
                    (pwd_hash, role, email, uname)
                )
            else:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role, email, created_at) VALUES (?,?,?,?,?)",
                    (uname, pwd_hash, role, email, now)
                )


def register_user(username: str, password: str, role: str = "Viewer", email: str = "") -> tuple:
    """
    Registers a new user account safely.
    Hashes password with SHA-256 + salt, checks for duplicate usernames,
    inserts user record into auth database, and records an audit log.
    Returns (success: bool, message: str).
    """
    valid_roles = {"Viewer", "Operator", "Admin"}
    if role not in valid_roles:
        role = "Viewer"

    with get_conn(DB_AUTH) as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,)
        ).fetchone()
        if existing:
            return False, f"Username '{username}' is already registered. Please choose another or sign in."

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pwd_hash = _hash_password(password)
        conn.execute(
            "INSERT INTO users (username, password_hash, role, email, created_at) VALUES (?,?,?,?,?)",
            (username, pwd_hash, role, email, now)
        )

    log_audit(username, role, "USER_REGISTER", "None", f"New user account registered ({role}).")
    return True, f"Account for '{username}' registered successfully! You can now sign in."


def validate_user(username: str, password: str) -> Optional[Dict]:
    """Validates credentials and returns user dict or None."""
    with get_conn(DB_AUTH) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return None
        # Check lockout
        if row["locked_until"]:
            lock_time = datetime.datetime.strptime(row["locked_until"], "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() < lock_time:
                return None
        # Check password
        if row["password_hash"] == _hash_password(password):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "UPDATE users SET last_login=?, login_attempts=0, locked_until=NULL WHERE username=?",
                (now, username)
            )
            return {"username": row["username"], "role": row["role"], "email": row["email"]}
        else:
            attempts = (row["login_attempts"] or 0) + 1
            locked_until = None
            if attempts >= 5:
                lock_dt = datetime.datetime.now() + datetime.timedelta(minutes=15)
                locked_until = lock_dt.strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "UPDATE users SET login_attempts=?, locked_until=? WHERE username=?",
                (attempts, locked_until, username)
            )
            return None


def create_session(username: str, role: str) -> str:
    """Creates a new session token valid for 8 hours."""
    token = str(uuid.uuid4())
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(hours=8)
    with get_conn(DB_AUTH) as conn:
        conn.execute(
            "INSERT INTO sessions (token, username, role, created_at, expires_at) VALUES (?,?,?,?,?)",
            (token, username, role,
             now.strftime("%Y-%m-%d %H:%M:%S"),
             exp.strftime("%Y-%m-%d %H:%M:%S"))
        )
    return token


def validate_session(token: str) -> Optional[Dict]:
    """Validates session token and returns user info or None."""
    with get_conn(DB_AUTH) as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE token=?", (token,)
        ).fetchone()
        if not row:
            return None
        exp = datetime.datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() > exp:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            return None
        return {"username": row["username"], "role": row["role"]}


def revoke_session(token: str):
    """Revokes (deletes) a session token on logout."""
    with get_conn(DB_AUTH) as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))


# ──────────────────────────────────────────────
# AUDIT LOGGING
# ──────────────────────────────────────────────
def log_audit(username: str, role: str, action: str, anomaly_type: str = "None", details: str = ""):
    """Appends an immutable audit record."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(DB_AUDIT) as conn:
        conn.execute(
            "INSERT INTO audit_logs (timestamp, username, role, action, anomaly_type, details) VALUES (?,?,?,?,?,?)",
            (ts, username, role, action, anomaly_type, details)
        )


def get_audit_logs(limit: int = 200) -> pd.DataFrame:
    with get_conn(DB_AUDIT) as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM audit_logs ORDER BY id DESC LIMIT {limit}", conn
        )
    return df


def clear_audit_logs():
    with get_conn(DB_AUDIT) as conn:
        conn.execute("DELETE FROM audit_logs")


# ──────────────────────────────────────────────
# ALERT MANAGEMENT
# ──────────────────────────────────────────────
def save_alert(severity: str, channel: str, title: str, message: str):
    """Persists alert to database."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(DB_AUDIT) as conn:
        conn.execute(
            "INSERT INTO alerts (timestamp, severity, channel, title, message) VALUES (?,?,?,?,?)",
            (ts, severity, channel, title, message)
        )


def get_alerts(limit: int = 100) -> pd.DataFrame:
    with get_conn(DB_AUDIT) as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM alerts ORDER BY id DESC LIMIT {limit}", conn
        )
    return df


def acknowledge_alert(alert_id: int, username: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(DB_AUDIT) as conn:
        conn.execute(
            "UPDATE alerts SET acknowledged=1, ack_by=?, ack_at=? WHERE id=?",
            (username, ts, alert_id)
        )


# ──────────────────────────────────────────────
# TELEMETRY
# ──────────────────────────────────────────────
def save_telemetry(electricity: float, water: float, outdoor_temp: float,
                   humidity: float, pressure: float, thermal_temp: float):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(DB_STORAGE) as conn:
        conn.execute(
            """INSERT INTO telemetry_logs
               (timestamp, electricity_kwh, water_litres, outdoor_temp_c, humidity_pct, pressure_psi, thermal_temp_c)
               VALUES (?,?,?,?,?,?,?)""",
            (ts, electricity, water, outdoor_temp, humidity, pressure, thermal_temp)
        )


def get_telemetry(hours: int = 24) -> pd.DataFrame:
    cutoff = (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(DB_STORAGE) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM telemetry_logs WHERE timestamp >= ? ORDER BY timestamp ASC",
            conn, params=(cutoff,)
        )
    return df


# ──────────────────────────────────────────────
# ESG METRICS
# ──────────────────────────────────────────────
def upsert_esg(co2: float, water: float, energy: float, score: float):
    today = datetime.date.today().strftime("%Y-%m-%d")
    with get_conn(DB_STORAGE) as conn:
        row = conn.execute("SELECT id FROM esg_metrics WHERE date=?", (today,)).fetchone()
        if row:
            conn.execute(
                "UPDATE esg_metrics SET co2_saved_kg=co2_saved_kg+?, water_saved_l=water_saved_l+?, energy_saved_kwh=energy_saved_kwh+?, esg_score=? WHERE date=?",
                (co2, water, energy, score, today)
            )
        else:
            conn.execute(
                "INSERT INTO esg_metrics (date, co2_saved_kg, water_saved_l, energy_saved_kwh, esg_score) VALUES (?,?,?,?,?)",
                (today, co2, water, energy, score)
            )


def get_esg_history(days: int = 30) -> pd.DataFrame:
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    with get_conn(DB_STORAGE) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM esg_metrics WHERE date >= ? ORDER BY date ASC",
            conn, params=(cutoff,)
        )
    return df
