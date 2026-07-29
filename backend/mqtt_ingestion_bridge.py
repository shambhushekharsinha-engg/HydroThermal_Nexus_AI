"""
backend/mqtt_ingestion_bridge.py
MQTT Protocol Telemetry Ingestion Bridge for HydroThermal Nexus-AI.
Parses JSON telemetry payloads published over MQTT topics (e.g., 'nexus/telemetry/facility_01').
"""

import json
import datetime
from typing import Dict, Any


class MQTTTelemetryBridge:
    """MQTT Broker Client Simulator for industrial IoT sensor payloads."""

    def __init__(self, broker_url: str = "mqtt.hydrothermal.local", port: int = 1883):
        self.broker_url = broker_url
        self.port = port
        self.subscribed_topics = ["nexus/telemetry/+", "nexus/actuators/control"]

    def parse_mqtt_message(self, topic: str, payload_str: str) -> Dict[str, Any]:
        """Parses an incoming MQTT message payload and formats for database ingestion."""
        try:
            payload = json.loads(payload_str)
            return {
                "status": "valid",
                "topic": topic,
                "broker": self.broker_url,
                "received_at": datetime.datetime.now().isoformat(),
                "data": {
                    "electricity_kwh": float(payload.get("electricity_kwh", 2200.0)),
                    "water_litres": float(payload.get("water_litres", 3100.0)),
                    "outdoor_temp_c": float(payload.get("outdoor_temp_c", 30.0)),
                    "humidity_pct": float(payload.get("humidity_pct", 60.0)),
                    "pressure_psi": float(payload.get("pressure_psi", 42.5)),
                    "thermal_temp_c": float(payload.get("thermal_temp_c", 68.4)),
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to parse MQTT payload: {e}"}
