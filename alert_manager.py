"""
alert_manager.py
Multi-channel alert system for HydroThermal Nexus-AI.
Supports: In-app, Telegram, Email (SMTP).
Includes cooldown management and severity-based routing.
"""

import datetime
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Tuple
from backend import database as db

# Alert Severity Hierarchy
SEVERITY_LEVELS = ["INFO", "WARNING", "CRITICAL", "EMERGENCY"]

# Cooldown registry (in-memory) — prevents alert spam
_last_alert_time: Dict[str, datetime.datetime] = {}
COOLDOWN_SECONDS = {
    "INFO":      300,   # 5 minutes
    "WARNING":   120,   # 2 minutes
    "CRITICAL":  30,    # 30 seconds
    "EMERGENCY": 10,    # 10 seconds
}


def _is_in_cooldown(key: str, severity: str) -> bool:
    """Returns True if the alert key is in cooldown."""
    if key not in _last_alert_time:
        return False
    elapsed = (datetime.datetime.now() - _last_alert_time[key]).total_seconds()
    return elapsed < COOLDOWN_SECONDS.get(severity, 120)


def _mark_sent(key: str):
    _last_alert_time[key] = datetime.datetime.now()


# ── Telegram ─────────────────────────────────────────────────────────
def send_telegram(bot_token: str, chat_id: str, message: str) -> Tuple[bool, str]:
    """Dispatches a Telegram message via Bot API."""
    if not bot_token or not chat_id:
        return False, "Telegram credentials not configured."
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=6)
        if resp.status_code == 200:
            return True, "Telegram message delivered."
        return False, f"Telegram API returned {resp.status_code}: {resp.text[:120]}"
    except Exception as e:
        return False, f"Telegram connection failed: {str(e)}"


# ── Email (SMTP) ──────────────────────────────────────────────────────
def send_email(
    smtp_host: str, smtp_port: int, sender: str, password: str,
    recipient: str, subject: str, body: str
) -> Tuple[bool, str]:
    """Sends an HTML email via SMTP (TLS)."""
    if not all([smtp_host, sender, password, recipient]):
        return False, "Email credentials incomplete."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = recipient

        html_body = f"""
        <html><body style="background:#0A0F1E;color:#E2E8F0;font-family:sans-serif;padding:24px;">
        <div style="max-width:600px;margin:auto;background:#111827;border:1px solid #00D4FF;
                    border-radius:12px;padding:24px;">
          <h2 style="color:#00D4FF;">⚡ HydroThermal Nexus-AI Alert</h2>
          <p style="color:#FFB800;font-size:14px;">{subject}</p>
          <pre style="background:#0A0F1E;color:#E2E8F0;padding:16px;border-radius:8px;
                      white-space:pre-wrap;">{body}</pre>
          <hr style="border-color:#1E2A3A;"/>
          <small style="color:#64748B;">HydroThermal Nexus-AI — Automated Alert System</small>
        </div></body></html>
        """
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return True, "Email delivered successfully."
    except Exception as e:
        return False, f"Email delivery failed: {str(e)}"


# ── Centralized Alert Dispatch ────────────────────────────────────────
def dispatch_alert(
    severity: str,
    title: str,
    message: str,
    anomaly_type: str = "None",
    username: str = "System",
    role: str = "System",
    telegram_token: str = "",
    telegram_chat: str = "",
    email_config: Optional[Dict] = None,
    force: bool = False,
) -> Dict[str, str]:
    """
    Central alert dispatcher.
    Returns a dict of {channel: result_message}.
    """
    results = {}
    cooldown_key = f"{severity}:{anomaly_type}"

    if not force and _is_in_cooldown(cooldown_key, severity):
        return {"cooldown": f"Alert suppressed — cooldown active for {cooldown_key}"}

    # Format the message
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = (
        f"🚨 *NEXUS-AI ALERT*\n"
        f"*Severity*: {severity}\n"
        f"*Title*: {title}\n"
        f"*Time*: {ts}\n"
        f"*Triggered By*: {username} ({role})\n\n"
        f"{message}"
    )

    # In-app (always)
    db.save_alert(severity, "In-App", title, message)
    results["in_app"] = "✅ Saved to Alert Center"

    # Audit log
    db.log_audit(username, role, f"ALERT_{severity}", anomaly_type, title)
    results["audit"] = "✅ Logged to Audit Trail"

    # Telegram
    if telegram_token and telegram_chat:
        ok, msg = send_telegram(telegram_token, telegram_chat, formatted)
        results["telegram"] = f"{'✅' if ok else '❌'} {msg}"
    else:
        results["telegram"] = "⚠️ Not configured"

    # Email
    if email_config and email_config.get("enabled"):
        ok, msg = send_email(
            smtp_host=email_config.get("smtp_host", ""),
            smtp_port=int(email_config.get("smtp_port", 587)),
            sender=email_config.get("sender", ""),
            password=email_config.get("password", ""),
            recipient=email_config.get("recipient", ""),
            subject=f"[{severity}] {title}",
            body=message
        )
        results["email"] = f"{'✅' if ok else '❌'} {msg}"
    else:
        results["email"] = "⚠️ Not configured"

    _mark_sent(cooldown_key)
    return results


# ── Predefined Alert Templates ────────────────────────────────────────
def build_anomaly_alert(anomaly_type: str, username: str) -> Dict[str, str]:
    """Builds alert content for a given anomaly type."""
    templates = {
        "Pipe Rupture / Flow Drop": {
            "severity": "CRITICAL",
            "title":    "Pipe Rupture — Flow Drop Detected",
            "message":  (
                "Critical pressure loss detected on Hydro-Node-Alpha.\n"
                "Fluid loss rate: +240% above baseline.\n"
                "Automated action: Solenoid valve throttled to 20%.\n"
                f"Operator: {username}\n"
                "Immediate physical inspection recommended."
            )
        },
        "HVAC Overheat / Thermal Spike": {
            "severity": "WARNING",
            "title":    "HVAC Thermal Exceedance — Cooling Tower",
            "message":  (
                "Thermal threshold exceeded on Cooling-Tower-Gamma.\n"
                "Temperature: 105°C (limit: 89°C).\n"
                "Automated action: Auxiliary chiller engaged, compute throttled.\n"
                f"Operator: {username}\n"
                "Schedule preventive maintenance for fan motor relay."
            )
        },
        "Nominal / Normal Operations": {
            "severity": "INFO",
            "title":    "System Reset — Normal Operations",
            "message":  (
                "All systems reset to baseline operational parameters.\n"
                f"Confirmed by: {username}\n"
                "No anomalies currently active."
            )
        }
    }
    return templates.get(anomaly_type, {
        "severity": "INFO",
        "title": f"Unknown Anomaly: {anomaly_type}",
        "message": f"Anomaly type '{anomaly_type}' triggered by {username}."
    })
