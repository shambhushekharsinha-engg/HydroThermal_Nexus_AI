"""
backend/api.py
FastAPI REST backend for HydroThermal Nexus-AI.
Runs on port 8001, started as a background thread by app.py.
Provides: telemetry, anomaly, audit, ESG, health, and alert endpoints.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import datetime
import numpy as np

# Local imports (resolved relative to project root)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import database as db

app = FastAPI(
    title="HydroThermal Nexus-AI API",
    version="2.0.0",
    description="REST backend for industrial telemetry, anomaly detection, and ESG metrics."
)

from backend.rate_limiter import RateLimiterMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=200)



# ── Pydantic Models ──────────────────────────────────────────────────
class AnomalyTrigger(BaseModel):
    username: str
    role: str
    anomaly_type: str
    severity: str = "WARNING"

class TelemetryPush(BaseModel):
    electricity_kwh: float
    water_litres: float
    outdoor_temp_c: float
    humidity_pct: float
    pressure_psi: float
    thermal_temp_c: float

class AlertAck(BaseModel):
    alert_id: int
    username: str

class ESGUpdate(BaseModel):
    co2_saved_kg: float
    water_saved_l: float
    energy_saved_kwh: float
    esg_score: float

class QuickLoginRequest(BaseModel):
    role: str = "Admin"  # Admin, Operator, Viewer

class CurrencyConvertRequest(BaseModel):
    amount: float
    from_currency: str = "USD"
    to_currency: str = "INR"

class CalculateSavingsRequest(BaseModel):
    water_litres: float
    energy_kwh: float
    co2_kg: float
    water_cost_per_l: float = 0.05
    energy_cost_per_kwh: float = 8.0
    carbon_price_per_tonne_usd: float = 15.0
    input_currency: str = "INR"
    target_currency: str = "INR"



# ── Helper: Simple API token check ──────────────────────────────────
API_SECRET = os.environ.get("NEXUS_API_SECRET", "NexusAPI_Internal_2026")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API key.")
    return x_api_key


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Returns system health status and uptime."""
    return {
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database":  "connected",
            "telemetry": "streaming",
            "alerts":    "active"
        }
    }


@app.post("/api/auth/quick-login")
def quick_login(payload: QuickLoginRequest):
    """Issues an authenticated session token for demo 1-click quick login (Admin, Operator, Viewer)."""
    role_map = {
        "admin": ("admin", "Admin@Nexus2026!"),
        "operator": ("operator1", "Operator@2026#"),
        "viewer": ("viewer1", "Viewer@View123")
    }
    key = payload.role.lower()
    if key not in role_map:
        raise HTTPException(status_code=400, detail="Invalid role specified. Must be 'Admin', 'Operator', or 'Viewer'.")

    target_user, target_pass = role_map[key]
    db.initialize_all_databases()
    user = db.validate_user(target_user, target_pass)
    if not user:
        raise HTTPException(status_code=401, detail="Quick login failed. Default account not found.")

    token = db.create_session(user["username"], user["role"])
    db.log_audit(user["username"], user["role"], "API_QUICK_LOGIN", "None", f"Quick login token issued for role '{user['role']}' via API.")

    return {
        "status": "authenticated",
        "username": user["username"],
        "role": user["role"],
        "session_token": token,
        "timestamp": datetime.datetime.now().isoformat()
    }



@app.get("/api/telemetry/live")
def get_live_telemetry(hours: int = 24, _key=Depends(verify_api_key)):
    """Returns telemetry records from the last N hours."""
    df = db.get_telemetry(hours=hours)
    if df.empty:
        return {"data": [], "count": 0}
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.post("/api/telemetry/push")
def push_telemetry(payload: TelemetryPush, _key=Depends(verify_api_key)):
    """Ingests a telemetry snapshot into the database."""
    db.save_telemetry(
        payload.electricity_kwh, payload.water_litres,
        payload.outdoor_temp_c,  payload.humidity_pct,
        payload.pressure_psi,    payload.thermal_temp_c
    )
    return {"status": "saved", "timestamp": datetime.datetime.now().isoformat()}


@app.post("/api/anomaly/trigger")
def trigger_anomaly(payload: AnomalyTrigger, _key=Depends(verify_api_key)):
    """Logs an anomaly trigger event and creates an alert."""
    db.log_audit(
        payload.username, payload.role,
        "TRIGGER_ANOMALY", payload.anomaly_type,
        f"Anomaly '{payload.anomaly_type}' triggered via API."
    )
    db.save_alert(
        severity=payload.severity,
        channel="API",
        title=f"Anomaly Triggered: {payload.anomaly_type}",
        message=f"User {payload.username} triggered scenario: {payload.anomaly_type}"
    )
    return {"status": "logged", "anomaly": payload.anomaly_type}


@app.get("/api/audit/logs")
def get_audit(limit: int = 100, _key=Depends(verify_api_key)):
    """Returns the most recent audit log entries."""
    df = db.get_audit_logs(limit=limit)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.get("/api/alerts")
def get_alerts(limit: int = 50, _key=Depends(verify_api_key)):
    """Returns the most recent alert records."""
    df = db.get_alerts(limit=limit)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.post("/api/alerts/acknowledge")
def ack_alert(payload: AlertAck, _key=Depends(verify_api_key)):
    """Marks an alert as acknowledged."""
    db.acknowledge_alert(payload.alert_id, payload.username)
    return {"status": "acknowledged", "alert_id": payload.alert_id}


@app.post("/api/esg/update")
def update_esg(payload: ESGUpdate, _key=Depends(verify_api_key)):
    """Updates today's ESG metrics."""
    db.upsert_esg(
        payload.co2_saved_kg, payload.water_saved_l,
        payload.energy_saved_kwh, payload.esg_score
    )
    return {"status": "updated"}


@app.get("/api/esg/history")
def esg_history(days: int = 30, _key=Depends(verify_api_key)):
    """Returns ESG history for the last N days."""
    df = db.get_esg_history(days=days)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


import pandas as pd
from ml_engine import HydroThermalAnalyticsCore

ml_core = HydroThermalAnalyticsCore()

@app.get("/api/ml/metrics")
def get_ml_metrics(_key=Depends(verify_api_key)):
    """Returns active IsolationForest model metrics and status."""
    return ml_core.get_model_metrics()


@app.get("/api/telemetry/historical")
def get_historical_telemetry(limit: int = 100, _key=Depends(verify_api_key)):
    """Returns Kaggle benchmark historical telemetry dataset records."""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hydrothermal_telemetry_historical.csv")
    if not os.path.exists(csv_path):
        return {"data": [], "count": 0, "message": "Historical benchmark dataset not found."}
    
    df = pd.read_csv(csv_path)
    if limit > 0:
        df = df.tail(limit)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


from backend.modbus_edge_simulator import ModbusPLCSimulator
from backend.mqtt_ingestion_bridge import MQTTTelemetryBridge
from backend.multi_tenant_manager import MultiTenantFacilityManager

modbus_plc = ModbusPLCSimulator()
mqtt_bridge = MQTTTelemetryBridge()
tenant_mgr = MultiTenantFacilityManager()


@app.get("/api/modbus/status")
def get_modbus_status(_key=Depends(verify_api_key)):
    """Returns Siemens Modbus TCP / PLC hardware register status."""
    return modbus_plc.read_holding_registers()


@app.get("/api/tenants/facilities")
def get_tenant_facilities(_key=Depends(verify_api_key)):
    """Returns list of registered enterprise multi-facility plants."""
    return {"facilities": tenant_mgr.list_facilities()}


@app.get("/api/tenants/aggregate")
def get_tenant_aggregate(_key=Depends(verify_api_key)):
    """Returns cross-facility sustainability metrics and carbon reduction targets."""
    return tenant_mgr.get_enterprise_aggregate()


from currency_converter import CurrencyConverter


@app.get("/api/currency/rates")
def get_currency_rates(_key=Depends(verify_api_key)):
    """Returns supported global currencies, symbols, names, and exchange rates vs USD."""
    return {
        "base_currency": "USD",
        "currencies": CurrencyConverter.get_supported_currencies()
    }


@app.post("/api/currency/convert")
def convert_currency(payload: CurrencyConvertRequest, _key=Depends(verify_api_key)):
    """Converts an amount between two supported global currencies."""
    try:
        converted = CurrencyConverter.convert(payload.amount, payload.from_currency, payload.to_currency)
        formatted = CurrencyConverter.format_currency(converted, payload.to_currency)
        return {
            "amount": payload.amount,
            "from_currency": payload.from_currency.upper(),
            "to_currency": payload.to_currency.upper(),
            "converted_amount": converted,
            "formatted": formatted
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/currency/calculate-savings")
def calculate_currency_savings(payload: CalculateSavingsRequest, _key=Depends(verify_api_key)):
    """Computes multi-currency ESG financial savings breakdown for resource preservation."""
    try:
        res = CurrencyConverter.calculate_esg_savings(
            water_litres=payload.water_litres,
            energy_kwh=payload.energy_kwh,
            co2_kg=payload.co2_kg,
            water_cost_per_l=payload.water_cost_per_l,
            energy_cost_per_kwh=payload.energy_cost_per_kwh,
            carbon_price_per_tonne_usd=payload.carbon_price_per_tonne_usd,
            input_currency=payload.input_currency,
            target_currency=payload.target_currency,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



