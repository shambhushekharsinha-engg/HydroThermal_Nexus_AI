<div align="center">

<img src="https://img.shields.io/badge/HYDROTHERMAL%20NEXUS--AI-v2.1%20PRODUCTION-00d4ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzAwZDQxZiIgZD0iTTEyIDJMMiA3bDEwIDUgMTAtNXoiLz48cGF0aCBmaWxsPSIjMDBkNDFmIiBkPSJNMiAxN2wxMCA1IDEwLTV2LTZMMTIgMTYgMiAxMXoiLz48L3N2Zz4=&labelColor=010308" />

# 🔷 HydroThermal Nexus-AI
### **Enterprise-Grade AI Cockpit for Hydrothermal IoT Monitoring & ESG Auditing**

<br/>

> *An industrial-grade operational cockpit for real-time hydrothermal facility monitoring, AI-driven anomaly detection (using IsolationForest and adaptive Z-score), ESG impact tracking, and automated edge mitigation response — secured end-to-end with SHA-256 session vaulting, corporate RBAC, and immutable audit logging.*

<br/>

---

### 🌐 Live Deployments

| Platform | Link | Description |
|:---:|:---:|:---|
| 🖥️ **Frontend Dashboard** | [![Streamlit](https://img.shields.io/badge/STREAMLIT%20DASHBOARD-Live%20Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white&labelColor=010308)](https://hydrothermal-nexus-ai.streamlit.app/) | Full 10-tab Streamlit dashboard — including Onboarding Sandbox |
| ⚙️ **Backend API** | [![FastAPI](https://img.shields.io/badge/FASTAPI%20BACKEND-hydrothermal--nexus--ai.vercel.app-00f0ff?style=for-the-badge&logo=vercel&logoColor=white&labelColor=010308)](https://hydrothermal-nexus-ai.vercel.app) | FastAPI REST microservice — all data, audit & telemetry endpoints |
| 📖 **API Docs** | [![Swagger](https://img.shields.io/badge/SWAGGER%20UI-/docs-009688?style=for-the-badge&logo=swagger&logoColor=white&labelColor=010308)](https://hydrothermal-nexus-ai.vercel.app/docs) | Interactive Swagger / OpenAPI documentation |

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat-square&logo=scikitlearn&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-Secure%20Vault-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-Visualizations-3F4F75?style=flat-square&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/Deployed-Vercel%20%2B%20Streamlit%20Cloud-00f0ff?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-10b981?style=flat-square"/>
</p>

</div>

---

## 📋 Table of Contents

- [📋 Problem Statement](#-problem-statement)
- [🎯 Success Metrics](#-success-metrics)
- [🏗️ System Architecture](#️-system-architecture)
- [✨ Core Feature Matrix](#-core-feature-matrix)
- [🖥️ Frontend Screenshots](#️-frontend-screenshots)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [🐳 Running with Docker](#-running-with-docker)
- [🔐 Default Credentials](#-default-credentials)
- [🤖 AI / ML Stack](#-ai--ml-stack)
- [🌱 ESG Impact Model](#-esg-impact-model)
- [🔐 Security Architecture](#-security-architecture)
- [📂 Project Structure](#-project-structure)
- [📜 License](#-license)
- [👨‍💻 Developer Profile](#-developer-profile)

---

## 📋 Problem Statement

Modern hydrothermal facilities (data centres, industrial campuses, hospital complexes) waste **15–30% of their water and energy resources** due to:

| Challenge | Real-World Impact |
|:---|:---|
| **Undetected pipe ruptures** | Up to 1,450 L/hr water loss per incident |
| **HVAC thermal exceedance** | 38+ kg CO₂e excess emissions per event |
| **Manual monitoring lag** | Anomalies go undetected for 4–8 hours |
| **No ESG audit trail** | Non-compliance with ISO 14001 / GHG Protocol |
| **Siloed alert systems** | Critical incidents missed by operations teams |

**HydroThermal Nexus-AI** solves these with a fully automated, AI-powered operational cockpit that detects, diagnoses, mitigates, and reports incidents in real time — with full regulatory audit capability.

---

## 🎯 Success Metrics

| Metric | Target | Measured By |
| :--- | :--- | :--- |
| **Anomaly detection latency** | < 15 minutes | Alert timestamp − sensor timestamp |
| **Water saved per incident** | ≥ 1,000 L/hr | Valve restriction × flow rate |
| **CO₂ prevented per event** | ≥ 30 kg CO₂e | HVAC efficiency × emission factor |
| **ESG Score** | ≥ 80/100 | Composite of water, CO₂, energy, uptime |
| **System health score** | ≥ 90/100 | Multi-sensor weighted average |
| **Alert delivery latency** | < 30 seconds | Telegram API response time |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Industrial IoT Sensors                     │
│  [Pressure] [Thermometer] [Flow Meter] [Energy Meter]   │
└──────────────────────┬──────────────────────────────────┘
                       │ Telemetry Stream (6h intervals)
          ┌────────────▼────────────┐
          │   Streamlit UI          │
          │   (Port 8501)           │
          │  ┌──────────────────┐   │
          │  │ Login / RBAC Auth│   │
          │  │ 10 Dashboard Tabs│   │
          │  │ Plotly Charts    │   │
          │  │ PyDeck 3D Twin   │   │
          │  └──────────────────┘   │
          └──────────┬──────────────┘
                     │ Internal API calls
          ┌──────────▼──────────────┐    ┌─────────────────────┐
          │   FastAPI Backend       │    │   SQLite Databases   │
          │   (Port 8001)           │◄───│  nexus_auth.db       │
          │   (Vercel serverless)   │    │  nexus_audit.db      │
          │  REST Endpoints         │    │  nexus_storage.db    │
          │  API Key Auth           │    └─────────────────────┘
          └──────────┬──────────────┘
          ┌──────────▼──────────────┐    ┌─────────────────────┐
          │   AI / ML Engine        │    │   Alert Channels     │
          │  IsolationForest Model  │    │  Telegram Bot API    │
          │  Z-Score Detector       │    │  Email (SMTP/TLS)    │
          │  RCA Engine             │    │  In-App Center       │
          │  AI Chatbot (12 topics) │    └─────────────────────┘
          └─────────────────────────┘
```

---

## ✨ Core Feature Matrix

| # | Feature Tab | Key Functionality |
| :---: | :--- | :--- |
| **0** | **🔰 Onboarding Sandbox** | Concept guides, simulated interactive guided missions (rupture, heatwave), and one-click role switcher |
| **1** | **🏠 Command Center** | Health ring gauge, KPI cards, live sparklines, and recent alert feed |
| **2** | **📈 Telemetry & Analytics**| Live sensor streaming, Plotly multi-chart, and correlation heatmap |
| **3** | **🌐 Digital Twin** | PyDeck 3D geo-spatial node map and real-time status cards |
| **4** | **🤖 RCA Engine** | AI root cause analysis diagnostics, mitigation path, and branded PDF report download |
| **5** | **🌱 ESG Dashboard** | CO₂/water/energy trends, ESG score timeline, and financial savings calculator |
| **6** | **🚨 Alert Center** | Multi-channel dispatch (Telegram, Email), severity levels, and ACK system |
| **7** | **💬 AI Assistant** | Domain-aware chatbot, 12-topic knowledge base, and quick chat suggestions |
| **8** | **📊 Data Insights** | EDA stats, IsolationForest model training interface, and data dictionary |
| **9** | **📜 Audit & Compliance** | Immutable audit trail ledger, CSV export, and administrative purge controls |

---

## 🖥️ Frontend Screenshots

> All screenshots captured from the live Streamlit dashboard at `app.py`

#### 🔰 Welcome Sandbox & Command Center HUD
<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/Welcome_and_Interactive_Sandbox.png" alt="Onboarding & Sandbox" width="100%"/>
      <br/><sub><b>Onboarding & Sandbox Tab</b></sub>
      <br/><sub>Concept cards, guided missions, and one-click role switcher</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/Main_Command_Center_Dashboard.png" alt="Command Center" width="100%"/>
      <br/><sub><b>Command Center HUD</b></sub>
      <br/><sub>Real-time health score ring, active alerts, and live sensor sparklines</sub>
    </td>
  </tr>
</table>

#### 📈 Sensor Telemetry & 3D Digital Twin
<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/Telemetry_and_Analytics_Console.png" alt="Telemetry Stream" width="100%"/>
      <br/><sub><b>Live Telemetry & Anomaly Injection Console</b></sub>
      <br/><sub>Dynamic data streaming charts and anomaly injection controls</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/GeoSpatial_Digital_Twin.png" alt="Digital Twin Map" width="100%"/>
      <br/><sub><b>Geospatial 3D Digital Twin Map</b></sub>
      <br/><sub>PyDeck visualization of facility nodes with status cards</sub>
    </td>
  </tr>
</table>

#### 🤖 Diagnostics & AI Assistant Chatbot
<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/RCA_Diagnostic_Engine.png" alt="RCA Mitigation Engine" width="100%"/>
      <br/><sub><b>RCA Diagnostics & Mitigation Center</b></sub>
      <br/><sub>AI failure vector mapping, step-by-step mitigation paths, and branded PDF generation</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/AI_Assistant_Chat_Interface.png" alt="AI Assistant" width="100%"/>
      <br/><sub><b>AI Assistant Chat Interface</b></sub>
      <br/><sub>Domain-aware chatbot with state integration and fast chat suggestion chips</sub>
    </td>
  </tr>
</table>

#### 🌱 ESG Carbon Ledger & Security Audits
<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/ESG_Carbon_and_Sustainability_Dashboard.png" alt="ESG Carbon Dashboard" width="100%"/>
      <br/><sub><b>ESG Carbon & Sustainability Dashboard</b></sub>
      <br/><sub>Carbon credits, water conservation metrics, and financial calculator</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/frontend/Immutable_Audit_Ledger.png" alt="Audit Ledger" width="100%"/>
      <br/><sub><b>Immutable Audit & Compliance Ledger</b></sub>
      <br/><sub>Admin controls, CSV export, and security action logs</sub>
    </td>
  </tr>
</table>

### ⚙️ Backend Screenshots

> Screenshots captured from the live FastAPI REST microservice Swagger UI documentation at `/docs`

<table>
  <tr>
    <td align="center" width="50%">
      <img src="Project Demo/backend/FastAPI_Backend_Endpoints_Swagger.png" alt="FastAPI Endpoints Swagger" width="100%"/>
      <br/><sub><b>FastAPI REST Backend Endpoints</b></sub>
      <br/><sub>Exposes endpoints for telemetry streams, incident tracking, audit trails, and ESG updates</sub>
    </td>
    <td align="center" width="50%">
      <img src="Project Demo/backend/FastAPI_Data_Schemas_Swagger.png" alt="FastAPI Data Schemas" width="100%"/>
      <br/><sub><b>FastAPI Data Schemas (Swagger OAS 3.1)</b></sub>
      <br/><sub>Strict request/response Pydantic models mapping data transfer objects</sub>
    </td>
  </tr>
</table>

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- pip

### Local Installation
```bash
# Clone the repository
git clone https://github.com/shambhushekharsinha-engg/HydroThermal_Nexus_AI.git
cd HydroThermal_Nexus_AI

# Install Streamlit and full frontend dependencies
pip install -r requirements.txt

# Run the Streamlit cockpit locally
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## 🐳 Running with Docker

Build and run both the Streamlit app and FastAPI backend services securely containerized:
```bash
# Build & start services
docker-compose up --build
```
- **Streamlit Cockpit**: `http://localhost:8501`
- **FastAPI Backend (docs)**: `http://localhost:8001/docs`

---

## 🔐 Default Credentials

| Role | Username | Password | Permissions |
|:---|:---|:---|:---|
| **Admin** | `admin` | `Admin@Nexus2026!` | Full access — all 15 permissions |
| **Operator** | `operator1` | `Operator@2026#` | Trigger anomalies, send alerts, download reports |
| **Viewer** | `viewer1` | `Viewer@View123` | Read-only dashboard access |

> ⚠️ **Change all default passwords immediately in production.**

---

## 🤖 AI / ML Stack

### 1. IsolationForest (scikit-learn)
- **Purpose**: Unsupervised anomaly detection on 6-feature telemetry.
- **Features**: `Electricity_kWh`, `Water_Litres`, `Pressure_PSI`, `Thermal_Temp_C`, `Outdoor_Temp_C`, `Humidity_Pct`
- **Contamination**: 5% (configurable in UI)
- **Output**: `IF_Anomaly` (bool) + `IF_Score` (0–100 risk score)

### 2. Adaptive Z-Score Engine
- **Purpose**: Fast per-sensor threshold detection with environmental adjustments.
- **Humidity adjustment**: `adjusted_mean = base + (humidity × 0.15)`
- **Temperature adjustment**: `adjusted_mean = base + max(0, temp - 30) × 85`
- **Threshold**: Z > 3.5 → anomaly flag

### 3. AI Chatbot
- **Domain**: 12-topic knowledge base (anomaly detection, ESG, security, RBAC, sensors, reports...)
- **State-aware**: Reads active anomaly and health score into each response.
- **Intent detection**: Keyword + phrase fuzzy matching.

---

## 🌱 ESG Impact Model

$$ESG\ Score = (\text{water}\_score \times 0.35) + (\text{co2}\_score \times 0.35) + (\text{energy}\_score \times 0.20) + (\text{uptime}\_score \times 0.10)$$

$$\text{Financial Savings (INR)} = (\text{water}\_saved\_L \times ₹0.05) + (\text{energy}\_saved\_kWh \times ₹8) + \left(\frac{\text{co2}\_saved\_kg}{1000} \times \$15 \times 83.5\right)$$

---

## 🔐 Security Architecture

| Layer | Implementation |
| :--- | :--- |
| **Authentication** | SHA-256 + application salt; 5-attempt lockout |
| **Session Management** | UUID4 tokens, 8-hour expiry, SQLite-backed |
| **Authorization** | RBAC — 3 roles × 15 explicit permissions |
| **Input Validation** | HTML escaping + SQL keyword stripping |
| **Data Privacy** | PII fields auto-hashed (SHA-256) on ingestion |
| **API Security** | FastAPI `X-API-Key` header authentication |
| **Container Security** | Non-root Docker user (`nexususer`, UID 1000) |

---

## 📂 Project Structure

```
HydroThermal_Nexus_AI/
├── app.py                     # Main Streamlit app (10 tabs, auth, UI)
├── ml_engine.py               # IsolationForest + Z-score anomaly engine
├── ai_assistant.py            # Domain-aware AI chatbot
├── alert_manager.py           # Multi-channel alert dispatcher
├── data_processor.py          # CSV/XLSX ingestion + PII anonymization
├── actuators.py               # Hardware actuation simulation
├── rca_engine.py              # Root cause analysis engine
├── report_generator.py        # ReportLab PDF generator
├── config.py                  # Baseline constants & RBAC config
├── pyproject.toml             # Vercel deployment package dependencies
│
├── backend/
│   ├── api.py                 # FastAPI REST endpoints (port 8001)
│   ├── database.py            # Thread-safe SQLite access layer
│   └── security.py            # RBAC checks, sanitization, PII masking
│
├── assets/
│   ├── logo.png               # Custom AI-generated project logo
│   ├── architecture.png       # System architecture diagram
│   └── styles.css             # Glassmorphism dark theme CSS
│
├── .streamlit/
│   └── config.toml            # Dark navy theme configuration
│
├── requirements.txt           # Master Python dependencies (Streamlit Cloud)
├── Dockerfile                 # Production Docker image (Python 3.11)
├── docker-compose.yml         # Multi-service compose with volumes
├── SCALING_STRATEGY.md        # Cloud deployment & scaling guide
└── README.md                  # This file
```

---

## 👨‍💻 Developer Profile

<div align="center">

<table align="center">
  <tr>
    <td align="center" width="100%">
      <table>
        <tr>
          <td>👤 <b>Name</b></td>
          <td>Shambhu Shekhar Sinha</td>
        </tr>
        <tr>
          <td>🎓 <b>Degree</b></td>
          <td>B.Tech — Computer Science & Engineering (AI & ML)</td>
        </tr>
        <tr>
          <td>🏫 <b>College</b></td>
          <td>Greater Noida Institute of Technology <b>(GNIOT)</b></td>
        </tr>
        <tr>
          <td>🏛️ <b>University</b></td>
          <td>Dr. APJ Abdul Kalam Technological University, Lucknow</td>
        </tr>
        <tr>
          <td>📍 <b>Location</b></td>
          <td>Greater Noida, Uttar Pradesh, India</td>
        </tr>
        <tr>
          <td>🐙 <b>GitHub</b></td>
          <td><a href="https://github.com/shambhushekharsinha-engg">@shambhushekharsinha-engg</a></td>
        </tr>
        <tr>
          <td>🖥️ <b>Frontend</b></td>
          <td><a href="https://hydrothermal-nexus-ai.streamlit.app/">hydrothermal-nexus-ai.streamlit.app</a></td>
        </tr>
        <tr>
          <td>⚙️ <b>Backend API</b></td>
          <td><a href="https://hydrothermal-nexus-ai.vercel.app/docs">hydrothermal-nexus-ai.vercel.app/docs</a></td>
        </tr>
      </table>
    </td>
  </tr>
</table>

<br/>

<img src="https://img.shields.io/badge/B.Tech-CSE%20%7C%20AI%20%26%20ML-00d4ff?style=flat-square&labelColor=010308"/>
<img src="https://img.shields.io/badge/GNIOT-Greater%20Noida%20Institute%20of%20Technology-10b981?style=flat-square"/>
<img src="https://img.shields.io/badge/AKTU-Lucknow-FF4B4B?style=flat-square"/>
<img src="https://img.shields.io/badge/GitHub-shambhushekharsinha--engg-181717?style=flat-square&logo=github"/>

</div>

---

## 📄 License
MIT License — Free for academic, commercial, and portfolio use.

---

*Built with ❤️ for the Innovation Journey — Showcase-Ready AI for Sustainability*
