# HydroThermal Nexus-AI — REST API Specification & OpenAPI Reference

The **HydroThermal Nexus-AI REST API** is built with **FastAPI** (OpenAPI 3.1) and provides high-performance telemetry ingestion, anomaly detection, currency conversion, tenant aggregation, and security audit logs.

- **Base URL**: `http://localhost:8001` (Local Docker/Thread) or `https://hydrothermal-nexus-ai.vercel.app` (Cloud Production)
- **Interactive Swagger Docs**: `/docs`
- **ReDoc Schema**: `/redoc`
- **Authentication**: Header `x-api-key: <NEXUS_API_SECRET>`

---

## 🔐 Authentication & Security

All API endpoints except `/api/health` and `/api/auth/quick-login` require the `x-api-key` HTTP header.

```http
x-api-key: NexusAPI_Internal_2026
```

---

## 📡 Endpoints Specification

### 1. Health Check
Returns real-time service operational status.

- **HTTP Method**: `GET`
- **Path**: `/api/health`
- **Auth Required**: None

#### Sample Request
```bash
curl -X GET "http://localhost:8001/api/health"
```

#### Sample Response (`200 OK`)
```json
{
  "status": "operational",
  "timestamp": "2026-08-01T22:50:00.123456",
  "version": "2.1.0",
  "services": {
    "database": "connected",
    "telemetry": "streaming",
    "alerts": "active"
  }
}
```

---

### 2. Live Telemetry Stream Ingestion
Pushes a multi-sensor telemetry snapshot into persistent SQLite storage.

- **HTTP Method**: `POST`
- **Path**: `/api/telemetry/push`
- **Auth Required**: Yes (`x-api-key`)

#### Sample Request
```bash
curl -X POST "http://localhost:8001/api/telemetry/push" \
     -H "x-api-key: NexusAPI_Internal_2026" \
     -H "Content-Type: application/json" \
     -d '{
           "electricity_kwh": 2150.5,
           "water_litres": 3120.0,
           "outdoor_temp_c": 33.2,
           "humidity_pct": 62.1,
           "pressure_psi": 42.8,
           "thermal_temp_c": 66.5
         }'
```

#### Sample Response (`200 OK`)
```json
{
  "status": "saved",
  "timestamp": "2026-08-01T22:50:05.987654"
}
```

---

### 3. Anomaly Scenario Trigger
Injects an emergency industrial anomaly scenario, creates an alert record, and dispatches notifications.

- **HTTP Method**: `POST`
- **Path**: `/api/anomaly/trigger`
- **Auth Required**: Yes (`x-api-key`)

#### Sample Request Payload
```json
{
  "username": "operator1",
  "role": "Operator",
  "anomaly_type": "Pipe Rupture / Flow Drop",
  "severity": "CRITICAL"
}
```

#### Sample Response (`200 OK`)
```json
{
  "status": "logged",
  "anomaly": "Pipe Rupture / Flow Drop"
}
```

---

### 4. IsolationForest ML Engine Metrics
Retrieves active machine learning model metrics, contamination rate, feature weights, and status.

- **HTTP Method**: `GET`
- **Path**: `/api/ml/metrics`
- **Auth Required**: Yes (`x-api-key`)

#### Sample Response (`200 OK`)
```json
{
  "trained": true,
  "model_type": "IsolationForest",
  "feature_count": 6,
  "features": [
    "Electricity_kWh",
    "Water_Litres",
    "Pressure_PSI",
    "Thermal_Temp_C",
    "Outdoor_Temp_C",
    "Humidity_Pct"
  ],
  "metrics": {
    "model": "IsolationForest",
    "n_estimators": 100,
    "contamination": 0.05,
    "anomalies_found": 3,
    "precision": 1.0,
    "recall": 1.0,
    "f1_score": 1.0
  },
  "status": "ready"
}
```

---

### 5. Multi-Currency Financial Savings Calculator
Computes monetary savings across 14 supported global currencies (INR, USD, EUR, GBP, JPY, etc.).

- **HTTP Method**: `POST`
- **Path**: `/api/currency/calculate-savings`
- **Auth Required**: Yes (`x-api-key`)

#### Sample Request Payload
```json
{
  "water_litres": 45000.0,
  "energy_kwh": 12500.0,
  "co2_kg": 1200.0,
  "water_cost_per_l": 0.05,
  "energy_cost_per_kwh": 8.0,
  "carbon_price_per_tonne_usd": 15.0,
  "input_currency": "INR",
  "target_currency": "INR"
}
```

#### Sample Response (`200 OK`)
```json
{
  "input_currency": "INR",
  "target_currency": "INR",
  "water_savings": 2250.0,
  "water_savings_formatted": "₹2,250",
  "energy_savings": 100000.0,
  "energy_savings_formatted": "₹1,00,000",
  "carbon_savings_usd": 18.0,
  "carbon_savings": 1503.0,
  "carbon_savings_formatted": "₹1,503",
  "total_savings": 103753.0,
  "total_savings_formatted": "₹1,03,753"
}
```
