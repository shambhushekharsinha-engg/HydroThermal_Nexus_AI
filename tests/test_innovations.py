"""
tests/test_innovations.py
Automated unit test suite for HydroThermal Nexus-AI Enterprise Innovations Suite:
- Predictive Maintenance & RUL Forecasting Engine
- ESG Regulatory Compliance Exporters (GHG Protocol, ISO 14001, BRSR)
- Industrial IoT Python Client SDK (NexusEdgeClient)
- Starlette / FastAPI Token-Bucket Rate Limiter Middleware
- Production Deployment Health Check CLI
"""

import sys
import os
import pytest
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from predictive_maintenance import PredictiveMaintenanceEngine
from esg_compliance_exporter import ESGComplianceExporter
from nexus_sdk import NexusEdgeClient
from backend.rate_limiter import SimpleRateLimiter
from scripts.health_check import run_deployment_health_check


def test_predictive_maintenance_rul_healthy():
    rul = PredictiveMaintenanceEngine.calculate_rul(
        vibration_mm_s=1.2, bearing_temp_c=55.0, pressure_psi=44.0
    )
    assert rul["health_index"] > 80.0
    assert rul["status"] == "HEALTHY"
    assert rul["rul_hours"] > 20000.0


def test_predictive_maintenance_rul_critical():
    rul = PredictiveMaintenanceEngine.calculate_rul(
        vibration_mm_s=8.5, bearing_temp_c=105.0, pressure_psi=75.0
    )
    assert rul["health_index"] < 50.0
    assert rul["status"] == "CRITICAL"
    assert rul["action_code"] == "ACT_EMERGENCY_SERVICING"



def test_downtime_financial_risk_estimation():
    risk = PredictiveMaintenanceEngine.estimate_downtime_financial_risk(rul_hours=300.0)
    assert risk["failure_probability_30d"] == 85.0
    assert risk["unplanned_outage_cost_usd"] > 0.0
    assert risk["net_savings_preventative_usd"] > 0.0


def test_esg_compliance_ghg_protocol_exporter():
    json_str = ESGComplianceExporter.export_ghg_protocol(
        total_co2_saved_kg=1500.0, total_energy_saved_kwh=4000.0
    )
    data = json.loads(json_str)
    assert "GHG Protocol" in data["standard"]
    assert data["scope1_direct_emissions_mitigated_tCO2e"] == 1.5
    assert data["scope2_location_based_emissions_mitigated_tCO2e"] > 0.0


def test_esg_compliance_iso14001_exporter():
    csv_str = ESGComplianceExporter.export_iso14001_audit_trail(
        water_saved_l=25000.0, energy_saved_kwh=3200.0, co2_saved_kg=890.0
    )
    assert "IsoClause" in csv_str
    assert "Preserved Volumetric Water Asset" in csv_str
    assert "25000.0" in csv_str


def test_esg_compliance_brsr_exporter():
    brsr_data = ESGComplianceExporter.export_brsr_report(
        water_saved_l=10000.0, energy_saved_kwh=2000.0, co2_saved_kg=500.0
    )
    assert "SEBI BRSR" in brsr_data["framework"]
    assert "essential_indicator_1" in brsr_data
    assert "essential_indicator_2" in brsr_data


def test_nexus_sdk_instantiation():
    client = NexusEdgeClient(api_url="http://localhost:8001", api_key="NexusAPI_Internal_2026")
    assert client.api_url == "http://localhost:8001"
    assert client.headers["x-api-key"] == "NexusAPI_Internal_2026"


def test_simple_rate_limiter():
    limiter = SimpleRateLimiter(requests_per_minute=2)
    client_ip = "192.168.1.50"

    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is True
    assert limiter.is_allowed(client_ip) is False   # Bucket depleted


def test_production_deployment_health_check_script():
    success = run_deployment_health_check()
    assert success is True
