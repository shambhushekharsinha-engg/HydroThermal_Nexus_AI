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

### 🔰 Welcome, Onboarding & Interactive Sandbox (Tab 0)

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/onboarding_sandbox.png" alt="Onboarding & Sandbox" width="100%"/>
      <br/><sub><b>Onboarding & Sandbox Tab</b></sub>
      <br/><sub>Concept cards, guided missions, and one-click role switcher</sub>
    </td>
    <td align="center" width="50%">
      <img src="assets/command_center.png" alt="Command Center" width="100%"/>
      <br/><sub><b>Command Center HUD</b></sub>
      <br/><sub>Real-time health score ring, active alerts, and live sensor sparklines</sub>
    </td>
  </tr>
</table>

---

### 📈 Sensor Telemetry & 3D Digital Twin

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/telemetry_stream.png" alt="Telemetry Stream" width="100%"/>
      <br/><sub><b>Live Telemetry & Anomaly Injection Console</b></sub>
      <br/><sub>Dynamic data streaming charts and anomaly injection controls</sub>
    </td>
    <td align="center" width="50%">
      <img src="assets/digital_twin.png" alt="Digital Twin Map" width="100%"/>
      <br/><sub><b>Geospatial 3D Digital Twin Map</b></sub>
      <br/><sub>PyDeck visualization of facility nodes with status cards</sub>
    </td>
  </tr>
</table>

---

### 🤖 Diagnostics & Automated Mitigation

<table>
  <tr>
    <td align="center" colspan="2">
      <img src="assets/rca_engine.png" alt="RCA Mitigation Engine" width="80%"/>
      <br/><sub><b>RCA Diagnostics & Mitigation Center</b></sub>
      <br/><sub>AI failure vector mapping, step-by-step mitigation paths, and branded PDF generation</sub>
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

<table>
  <tr>
    <td align="center" width="30%">
      <img src="https://github.com/shambhushekharsinha-engg.png" alt="Shambhu Shekhar Sinha" width="150px" style="border-radius: 50%;"/>
      <br/>
      <br/>
      <b>Shambhu Shekhar Sinha</b>
    </td>
    <td valign="top">
      <h4>B.Tech Computer Science & Engineering (AI & ML)</h4>
      <h5>Greater Noida Institute of Technology</h5>
      <p>Specializing in industrial IoT, operational AI, real-time telemetry systems, and security-centric software engineering.</p>
      <ul>
        <li><b>GitHub:</b> <a href="https://github.com/shambhushekharsinha-engg">shambhushekharsinha-engg</a></li>
        <li><b>LinkedIn:</b> <a href="https://linkedin.com/in/shambhu-shekhar-sinha-636498341">Shambhu Shekhar Sinha</a></li>
        <li><b>Email:</b> <a href="mailto:shambhushekharsinha@gmail.com">shambhushekharsinha@gmail.com</a></li>
      </ul>
    </td>
  </tr>
</table>

---

## 📄 License
MIT License — Free for academic, commercial, and portfolio use.

---

*Built with ❤️ for the Innovation Journey — Showcase-Ready AI for Sustainability*
