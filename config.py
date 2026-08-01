# -*- coding: utf-8 -*-
"""
config.py — HydroThermal Nexus-AI Central Configuration Engine
Centralizes environment variables, hardware registers, RBAC policies, and baseline settings.
"""

import os
import logging
from typing import Dict, List, Any

# ── LOGGING SETUP ────────────────────────────────────────────────────
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL_STR, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger: logging.Logger = logging.getLogger("HydroThermalNexus.Config")

# ── API & SECURITY CONFIGURATION ──────────────────────────────────────
NEXUS_API_SECRET: str = os.getenv("NEXUS_API_SECRET", "NexusAPI_Internal_2026")
SALT_KEY: str = os.getenv("NEXUS_SALT_KEY", "NexusAI_Secure_Salt_2026")
PII_KEYWORDS: List[str] = ['name', 'id', 'room', 'resident', 'ip', 'email', 'phone']

# ── NETWORK & HOST CONFIGURATION ──────────────────────────────────────
PORT_STREAMLIT: int = int(os.getenv("PORT_STREAMLIT", "8501"))
PORT_FASTAPI: int = int(os.getenv("PORT_FASTAPI", "8001"))
FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")

# ── DATABASE CONFIGURATION ────────────────────────────────────────────
DATABASE_PATH: str = os.getenv("DB_STORAGE_PATH", "nexus_storage.db")
AUDIT_DB_PATH: str = os.getenv("DB_AUDIT_PATH", "nexus_audit.db")
AUTH_DB_PATH: str = os.getenv("DB_AUTH_PATH", "nexus_auth.db")

# ── ENTERPRISE BASELINES & HARDWARE REGISTERS ─────────────────────────
WATER_BASE_MEAN: float = float(os.getenv("WATER_BASE_MEAN", "3100.0"))
WATER_BASE_STD: float = float(os.getenv("WATER_BASE_STD", "75.0"))

ELEC_BASE_MEAN: float = float(os.getenv("ELEC_BASE_MEAN", "2200.0"))
ELEC_BASE_STD: float = float(os.getenv("ELEC_BASE_STD", "120.0"))

BASE_HUMIDITY: float = float(os.getenv("BASE_HUMIDITY", "65.0"))
BASE_OUTDOOR_TEMP: float = float(os.getenv("BASE_OUTDOOR_TEMP", "32.0"))

# ── REPORTING & BUFFER SYSTEM CONFIGURATION ───────────────────────────
DEFAULT_REPORT_NAME: str = "NexusAI_Executive_Impact_Summary.pdf"
MAX_BUFFER_SIZE: int = int(os.getenv("MAX_BUFFER_SIZE", "500"))

# ── RBAC ROLE DEFINITIONS ─────────────────────────────────────────────
USER_ROLES: Dict[str, str] = {
    "Field Engineer": "FACILITIES_MAINTENANCE_TEAM",
    "Sustainability Auditor": "ESG_COMPLIANCE_TEAM",
    "Chief Financial Officer (CFO)": "EXECUTIVE_ADMIN_TEAM"
}


def get_system_config() -> Dict[str, Any]:
    """Return dictionary of core system configuration for diagnostic endpoints."""
    return {
        "api_secret_configured": bool(NEXUS_API_SECRET),
        "streamlit_port": PORT_STREAMLIT,
        "fastapi_port": PORT_FASTAPI,
        "storage_db": DATABASE_PATH,
        "audit_db": AUDIT_DB_PATH,
        "auth_db": AUTH_DB_PATH,
        "max_buffer_size": MAX_BUFFER_SIZE,
        "log_level": LOG_LEVEL_STR,
    }