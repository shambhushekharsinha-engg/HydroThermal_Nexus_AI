"""
actuators.py - Hardware Actuation & Alert Communication System
Handles automated edge mitigation, status badges, and real-time alert dispatch.
"""

import datetime
import urllib.parse
import urllib.request
import json

class AutomatedMitigationManager:
    def __init__(self):
        self.solenoid_aperture = 100  # Percentage open (0-100%)
        self.hvac_relay_state = "OPTIMIZED AUTO-MODULATION"
        
    def trigger_mitigation(self, anomaly_type: str, severity: str) -> dict:
        """
        Executes hardware actuation based on anomaly type and severity.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if anomaly_type in ["WATER_LEAK", "SUB_SURFACE_RUPTURE"]:
            if severity == "CRITICAL":
                self.solenoid_aperture = 20  # Restrict flow to prevent flooding
                action_msg = "Solenoid Valve throttled down to 20% aperture."
            else:
                self.solenoid_aperture = 50
                action_msg = "Solenoid Valve throttled down to 50% aperture."
                
        elif anomaly_type == "ENERGY_SPIKE":
            self.hvac_relay_state = "SAFETY LOAD SHEDDING ACTIVE"
            action_msg = "HVAC Circuit Relay switched to Load Shedding mode."
            
        else:
            action_msg = "Nominal system adjustments applied."

        return {
            "timestamp": timestamp,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "solenoid_aperture": f"{self.solenoid_aperture}%",
            "hvac_status": self.hvac_relay_state,
            "action_summary": action_msg
        }

    def reset_hardware(self):
        """Restores hardware registers to baseline nominal states."""
        self.solenoid_aperture = 100
        self.hvac_relay_state = "OPTIMIZED AUTO-MODULATION"
        return "Hardware registers successfully restored to baseline."

    @staticmethod
    def calculate_water_saved(valve_capacity: int) -> str:
        """Calculates volume of water saved based on current valve restriction."""
        if valve_capacity < 100:
            saved_liters = (100 - valve_capacity) * 125
            return f"{saved_liters:,} Liters"
        return "0 Liters (Baseline)"

    @staticmethod
    def calculate_energy_deflected(hvac_mode: str) -> str:
        """Calculates energy deflected based on HVAC relay state."""
        if "EMERGENCY" in hvac_mode or "SHEDDING" in hvac_mode:
            return "1,450 kWh / Day"
        return "0 kWh (Baseline)"

    @staticmethod
    def resolve_visual_badges(valve_capacity: int, hvac_mode: str) -> tuple:
        """Returns color badges based on hardware register states."""
        valve_badge = "#27AE60" if valve_capacity == 100 else "#E74C3C"
        hvac_badge = "#27AE60" if "OPTIMIZED" in hvac_mode else "#E67E22"
        return valve_badge, hvac_badge


def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Sends a real-time alert notification to a specified Telegram Chat.
    Uses standard library urllib to avoid requiring additional heavy dependencies.
    """
    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception as e:
        print(f"Telegram Alert Delivery Failed: {e}")
        return False