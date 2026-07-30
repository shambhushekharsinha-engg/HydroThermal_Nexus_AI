"""
nexus_sdk.py
Official HydroThermal Nexus-AI Industrial Edge Client SDK.
Zero-dependency Python client for IoT telemetry streaming, health checks,
and multi-currency ESG analytics API access.
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional


class NexusEdgeClient:
    """
    Official Python Client SDK for HydroThermal Nexus-AI REST Microservice API.
    """

    def __init__(self, api_url: str = "http://localhost:8001", api_key: str = "NexusAPI_Internal_2026"):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    def _http_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper for HTTP requests using Python standard library urllib."""
        url = f"{self.api_url}{endpoint}"
        req_data = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(url, data=req_data, headers=self.headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_bytes = resp.read()
                return json.loads(resp_bytes.decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def get_health(self) -> Dict[str, Any]:
        """Returns REST API server health status."""
        return self._http_request("GET", "/api/health")

    def push_telemetry(
        self,
        electricity_kwh: float,
        water_litres: float,
        outdoor_temp_c: float,
        humidity_pct: float,
        pressure_psi: float,
        thermal_temp_c: float
    ) -> Dict[str, Any]:
        """Pushes an IoT telemetry snapshot to the Nexus-AI database."""
        payload = {
            "electricity_kwh": electricity_kwh,
            "water_litres": water_litres,
            "outdoor_temp_c": outdoor_temp_c,
            "humidity_pct": humidity_pct,
            "pressure_psi": pressure_psi,
            "thermal_temp_c": thermal_temp_c
        }
        return self._http_request("POST", "/api/telemetry/push", payload)

    def get_currency_rates(self) -> Dict[str, Any]:
        """Fetches active global currencies and exchange rates."""
        return self._http_request("GET", "/api/currency/rates")

    def convert_currency(self, amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
        """Converts an amount between two global currencies via API."""
        payload = {
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr
        }
        return self._http_request("POST", "/api/currency/convert", payload)

    def calculate_esg_savings(
        self,
        water_litres: float,
        energy_kwh: float,
        co2_kg: float,
        target_currency: str = "USD"
    ) -> Dict[str, Any]:
        """Calculates multi-currency ESG savings via API."""
        payload = {
            "water_litres": water_litres,
            "energy_kwh": energy_kwh,
            "co2_kg": co2_kg,
            "target_currency": target_currency
        }
        return self._http_request("POST", "/api/currency/calculate-savings", payload)
