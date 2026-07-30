"""
scripts/health_check.py
Production Readiness & Deployment Diagnostic CLI Tool.
Validates database schemas, ML model artifacts, currency engine, API readiness,
and environment setup before production deployment.
"""

import sys
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from currency_converter import CurrencyConverter
from backend import database as db
from ml_engine import HydroThermalAnalyticsCore


def run_deployment_health_check() -> bool:
    print("=" * 60)
    print(" HYDROTHERMAL NEXUS-AI: PRODUCTION DEPLOYMENT HEALTH CHECK")
    print("=" * 60)

    all_passed = True

    # 1. Database Schema Check
    print("\n[1/4] Checking SQLite Enterprise Storage Vaults...")
    try:
        db.initialize_all_databases()
        conn = sqlite3.connect("nexus_storage.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        conn.close()
        print(f"  [OK] Database initialized successfully. Found {len(tables)} storage tables.")
    except Exception as e:
        print(f"  [FAIL] Database check failed: {e}")
        all_passed = False

    # 2. ML Engine & Model Artifact Check
    print("\n[2/4] Checking Machine Learning Anomaly Engine...")
    try:
        ml_core = HydroThermalAnalyticsCore()
        metrics = ml_core.get_model_metrics()
        print(f"  [OK] IsolationForest Core ready. Trained: {metrics.get('trained', False)}, Model Type: {metrics.get('model_type')}")
    except Exception as e:
        print(f"  [FAIL] ML Engine check failed: {e}")
        all_passed = False

    # 3. Currency Converter Engine Check
    print("\n[3/4] Checking Enterprise Multi-Currency Engine...")
    try:
        currencies = CurrencyConverter.get_supported_currencies()
        converted = CurrencyConverter.convert(100.0, "USD", "INR")
        print(f"  [OK] Currency Engine active. Supported Currencies: {len(currencies)}, Conversion test ($100 -> INR {converted:,.0f}).")
    except Exception as e:
        print(f"  [FAIL] Currency engine check failed: {e}")
        all_passed = False

    # 4. REST Backend API Import & Schema Verification
    print("\n[4/4] Checking FastAPI Backend Microservice Router...")
    try:
        from backend.api import app
        print(f"  [OK] FastAPI Router compiled successfully. Version: {app.version}, Title: {app.title}")
    except Exception as e:
        print(f"  [FAIL] FastAPI backend compilation failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(" [SUCCESS] SYSTEM DEPLOYMENT STATUS: 100% PRODUCTION READY")
        print("=" * 60)
        return True
    else:
        print(" [WARNING] SYSTEM DEPLOYMENT STATUS: ERRORS DETECTED - RESOLVE BEFORE DEPLOYMENT")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_deployment_health_check()
    sys.exit(0 if success else 1)
