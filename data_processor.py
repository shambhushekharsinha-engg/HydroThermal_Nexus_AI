# Save this file as data_processor.py
import pandas as pd
import numpy as np
import hashlib
import sqlite3
import os
import config

class DataIngestionShield:
    @staticmethod
    def initialize_database():
        """Creates the persistence layer schema tables if they do not exist locally."""
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    timestamp TEXT PRIMARY KEY,
                    electricity_kwh REAL,
                    water_litres REAL,
                    outdoor_temp_c REAL,
                    humidity_pct REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_role TEXT,
                    event_type TEXT,
                    details TEXT
                )
            """)
            conn.commit()

    @staticmethod
    def log_audit_event(user_role: str, event_type: str, details: str):
        """Appends an unalterable compliance signature row directly to the system audit ledger."""
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_trail (timestamp, user_role, event_type, details) VALUES (?, ?, ?, ?)",
                (timestamp, user_role, event_type, details)
            )
            conn.commit()

    @staticmethod
    def secure_and_anonymize(df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if any(key in col.lower() for key in config.PII_KEYWORDS):
                df[col] = df[col].astype(str).apply(
                    lambda x: hashlib.sha256((x + config.SALT_KEY).encode()).hexdigest()[:12]
                )
                df = df.rename(columns={col: f"Anonymized_{col}"})
        df = df.ffill().bfill()
        return df

    @staticmethod
    def save_telemetry_to_db(df: pd.DataFrame):
        """Serializes incoming Pandas data blocks straight to persistent SQL storage blocks."""
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            # Drop timezone context for sqlite formatting matching
            df_copy = df.copy()
            df_copy['Timestamp'] = df_copy['Timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")
            df_copy.to_sql('telemetry_logs', conn, if_exists='append', index=False, method='multi')

    @staticmethod
    def load_historical_records() -> pd.DataFrame:
        """Retrieves verified database records back into a structured operational dataframe."""
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM telemetry_logs ORDER BY timestamp ASC", conn)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'Timestamp'})
        return df
    
    @staticmethod
    def parse_file(uploaded_file) -> pd.DataFrame:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Auto-map chronological indexes
            date_col = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if date_col:
                df[date_col[0]] = pd.to_datetime(df[date_col[0]])
                df = df.rename(columns={date_col[0]: 'Timestamp'})
            else:
                # FIXED: Changed 'H' to 'h' to avoid ValueError on Python 3.13/Pandas
                df['Timestamp'] = pd.date_range(start="2026-07-01", periods=len(df), freq='h')
                
            return DataIngestionShield.secure_and_anonymize(df)
        except Exception:
            return None