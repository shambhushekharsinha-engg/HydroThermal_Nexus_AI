# Save this file as config.py
import os

# --- ENTERPRISE BASELINES & HARDWARE REGISTERS ---
WATER_BASE_MEAN = 3100.0
WATER_BASE_STD = 75.0

ELEC_BASE_MEAN = 2200.0
ELEC_BASE_STD = 120.0

# --- METEOROLOGICAL DEFAULT COEFFICIENTS ---
BASE_HUMIDITY = 65.0
BASE_OUTDOOR_TEMP = 32.0

# --- SYSTEM SECURITY & ANONYMIZATION REGISTERS ---
SALT_KEY = "NexusAI_Secure_Salt_2026"
PII_KEYWORDS = ['name', 'id', 'room', 'resident', 'ip', 'email', 'phone']

# --- REPORTING & BUFFER SYSTEM CONFIGURATION ---

# The default file name assigned to the dynamically generated, executive-ready ESG impact PDF.
# This document serves as the auditable proof of resource conservation for sustainability management.
DEFAULT_REPORT_NAME = "NexusAI_Executive_Impact_Summary.pdf"

# The maximum number of telemetric data rows held in local, high-speed volatile memory buffer cache.
# Acts as a fallback storage limit to prevent data loss and blinding during edge network or Wi-Fi dropouts.
MAX_BUFFER_SIZE = 500

# --- ENTERPRISE DATABASE & RBAC CONFIGURATION ---

# The relative path pointing to our localized, persistent SQLite storage database engine.
# Ensures structural infrastructure logs survive script reboots and dashboard refreshes.
DATABASE_PATH = "nexus_storage.db"

# Multi-Tenant Role-Based Access Control (RBAC) mapping registry.
# Limits manual hardware overrides and configuration changes to verified job profiles.
USER_ROLES = {
    "Field Engineer": "FACILITIES_MAINTENANCE_TEAM",
    "Sustainability Auditor": "ESG_COMPLIANCE_TEAM",
    "Chief Financial Officer (CFO)": "EXECUTIVE_ADMIN_TEAM"
}