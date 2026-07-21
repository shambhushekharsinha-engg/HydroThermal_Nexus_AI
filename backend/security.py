"""
backend/security.py
Security layer: input sanitization, RBAC permission checks,
rate-limit guard, and data-masking utilities.
"""

import re
import html
import hashlib
import datetime
from typing import Dict, Any, Optional

# ── RBAC Permission Matrix ──────────────────────────────────────────
ROLE_PERMISSIONS: Dict[str, list] = {
    "Admin": [
        "view_dashboard", "view_telemetry", "view_digital_twin",
        "view_rca", "view_esg", "view_alerts", "view_audit",
        "trigger_anomaly", "configure_alerts", "clear_audit",
        "manage_users", "download_reports", "send_telegram",
        "acknowledge_alert", "view_ai_assistant", "export_data"
    ],
    "Operator": [
        "view_dashboard", "view_telemetry", "view_digital_twin",
        "view_rca", "view_esg", "view_alerts", "view_audit",
        "trigger_anomaly", "download_reports", "send_telegram",
        "acknowledge_alert", "view_ai_assistant"
    ],
    "Viewer": [
        "view_dashboard", "view_telemetry", "view_digital_twin",
        "view_rca", "view_esg", "view_alerts", "view_audit",
        "view_ai_assistant"
    ]
}


def has_permission(role: str, permission: str) -> bool:
    """Returns True if the role has the specified permission."""
    return permission in ROLE_PERMISSIONS.get(role, [])


# ── Input Sanitization ───────────────────────────────────────────────
_DANGEROUS_PATTERNS = re.compile(
    r"(--|;|\'|\"|\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|<script|javascript:)",
    re.IGNORECASE
)

def sanitize_input(value: str, max_len: int = 256) -> str:
    """Escapes HTML and strips SQL injection patterns from user input."""
    if not isinstance(value, str):
        return ""
    cleaned = html.escape(value.strip())
    cleaned = _DANGEROUS_PATTERNS.sub("", cleaned)
    return cleaned[:max_len]


def validate_username(username: str) -> tuple:
    """Returns (is_valid, error_message)."""
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 32:
        return False, "Username must be 3–32 characters."
    if not re.match(r"^[a-zA-Z0-9_\-\.]+$", username):
        return False, "Username may only contain letters, digits, _, -, ."
    return True, ""


def validate_password_strength(password: str) -> tuple:
    """Returns (is_valid, error_message). Checks complexity requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        return False, "Password must contain at least one special character."
    return True, ""


# ── Data Masking / Anonymization ─────────────────────────────────────
_PII_FIELDS = {"email", "phone", "ip", "name", "address", "ssn", "resident"}

def mask_pii(value: str, field_name: str) -> str:
    """Masks PII fields. Emails are partially shown; others are hashed."""
    if any(p in field_name.lower() for p in _PII_FIELDS):
        if "@" in str(value):
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        return hashlib.sha256(str(value).encode()).hexdigest()[:12] + "***"
    return value


def get_role_badge(role: str) -> str:
    """Returns an HTML badge string styled by role."""
    colors = {
        "Admin":    ("#FF6B35", "#1a0a00"),
        "Operator": ("#00D4FF", "#001a2e"),
        "Viewer":   ("#00FF88", "#001a10"),
    }
    fg, bg = colors.get(role, ("#aaa", "#222"))
    return (
        f'<span style="background:{bg};color:{fg};border:1px solid {fg};'
        f'padding:2px 10px;border-radius:12px;font-size:0.75rem;'
        f'font-weight:700;letter-spacing:1px;">{role.upper()}</span>'
    )


def get_severity_badge(severity: str) -> str:
    """Returns styled HTML badge for alert severity."""
    map_ = {
        "INFO":      ("#00D4FF", "#001420"),
        "WARNING":   ("#FFB800", "#1a1200"),
        "CRITICAL":  ("#FF2D55", "#1a0010"),
        "EMERGENCY": ("#FF2D55", "#2a0010"),
    }
    fg, bg = map_.get(severity.upper(), ("#aaa", "#222"))
    return (
        f'<span style="background:{bg};color:{fg};border:1px solid {fg};'
        f'padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">'
        f'{severity}</span>'
    )


# ── Content Security Policy headers ──────────────────────────────────
CSP_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' blob:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' http://localhost:8001 https://api.telegram.org;"
    )
}
