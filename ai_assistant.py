"""
ai_assistant.py
Context-aware AI assistant for HydroThermal Nexus-AI.
Provides domain knowledge, system-state-aware responses,
conversation history, and recommended quick actions.
"""

import re
import datetime
from typing import List, Dict, Optional, Tuple


# ── Knowledge Base ───────────────────────────────────────────────────
KNOWLEDGE_BASE: List[Dict] = [
    {
        "id": "system_overview",
        "tags": ["what is", "overview", "about", "explain", "introduction", "nexus", "system"],
        "question": "What is HydroThermal Nexus-AI?",
        "answer": (
            "**HydroThermal Nexus-AI** is an enterprise-grade industrial IoT operational cockpit "
            "designed for real-time monitoring and control of hydrothermal facility infrastructure.\n\n"
            "**Core Capabilities:**\n"
            "- 🔵 **Live Telemetry** — continuous streaming of pressure, temperature, flow, and energy sensors\n"
            "- 🤖 **AI Anomaly Detection** — Z-score + adaptive threshold engine flags deviations in real-time\n"
            "- 🌐 **3D Digital Twin** — geo-spatial PyDeck map mirrors physical node states\n"
            "- 🌱 **ESG Dashboard** — tracks CO₂, water, and energy savings for regulatory compliance\n"
            "- 🚨 **Multi-Channel Alerts** — dispatches to Telegram, Email, and in-app notification center\n"
            "- 📜 **Immutable Audit Trail** — every action is logged to a tamper-evident SQLite ledger\n\n"
            "The system runs on Python + Streamlit (UI) with a FastAPI backend on port 8001."
        )
    },
    {
        "id": "anomaly_detection",
        "tags": ["anomaly", "detection", "how does detection", "z-score", "threshold", "spike", "flag"],
        "question": "How does anomaly detection work?",
        "answer": (
            "**Anomaly Detection Engine** uses an adaptive Z-score model:\n\n"
            "```\nZ = (current_value - adjusted_baseline) / std_deviation\n```\n\n"
            "- If `Z > 3.5`, an anomaly flag is raised\n"
            "- The baseline is **dynamically adjusted** by ambient temperature and humidity\n"
            "- **Water anomaly**: baseline shifts by `humidity × 0.15`\n"
            "- **Electricity anomaly**: baseline shifts by `max(0, temp - 30°C) × 85`\n\n"
            "**Detection latency**: typically < 15 minutes on 6-hour sensor cycles.\n\n"
            "When an anomaly is detected:\n"
            "1. An alert is generated in the Alert Center\n"
            "2. A Telegram notification is dispatched (if configured)\n"
            "3. Automated mitigation actions are triggered\n"
            "4. RCA engine begins root cause analysis"
        )
    },
    {
        "id": "pipe_rupture",
        "tags": ["pipe", "rupture", "flow drop", "water leak", "pressure loss", "solenoid"],
        "question": "What happens during a Pipe Rupture / Flow Drop?",
        "answer": (
            "**Pipe Rupture / Flow Drop Scenario:**\n\n"
            "📋 **Root Cause**: Solenoid Relay Valve Cutoff Failure\n"
            "📊 **Impact**: Fluid loss rate exceeds baseline by **+240%**\n\n"
            "**Automated Response Chain:**\n"
            "1. 🔴 Solenoid valve throttled to **20% aperture** (restricts flood)\n"
            "2. 🔄 Thermal loop rerouted to **auxiliary bypass**\n"
            "3. 📱 **Telegram alert** dispatched to operator channel\n"
            "4. 💾 Anomaly logged in **SQLite audit ledger**\n"
            "5. 🌱 ESG metric updated — saves ~**1,450 L/hr** water\n\n"
            "**To simulate this**: Go to **Telemetry & Analytics** tab → Select 'Pipe Rupture / Flow Drop' → Click Trigger."
        )
    },
    {
        "id": "hvac_overheat",
        "tags": ["hvac", "overheat", "thermal spike", "cooling", "heat", "temperature", "fan motor"],
        "question": "What happens during an HVAC Overheat / Thermal Spike?",
        "answer": (
            "**HVAC Overheat / Thermal Spike Scenario:**\n\n"
            "📋 **Root Cause**: Fan Motor Relay Stall → Cooling Tower Heat Exchange Degradation\n"
            "📊 **Impact**: Temperature ramps to **105°C** (threshold: 89°C)\n\n"
            "**Automated Response Chain:**\n"
            "1. ❄️ Secondary **auxiliary chiller** units engaged\n"
            "2. ⚡ High-load compute racks **throttled** to reduce heat generation\n"
            "3. 📱 **Telegram alert** dispatched\n"
            "4. 🌱 ESG impact: Prevented **38 kg CO₂e** excess emissions\n\n"
            "**Digital Twin Effect**: Cooling-Tower-Gamma node turns red on the 3D map."
        )
    },
    {
        "id": "esg_dashboard",
        "tags": ["esg", "carbon", "co2", "sustainability", "green", "environment", "emissions", "water saved"],
        "question": "How is the ESG score calculated?",
        "answer": (
            "**ESG (Environmental, Social, Governance) Score** is computed daily:\n\n"
            "| Metric | Weight | Source |\n"
            "|--------|--------|--------|\n"
            "| Water Saved | 35% | Valve restriction × flow rate |\n"
            "| CO₂ Prevented | 35% | HVAC efficiency × grid emission factor |\n"
            "| Energy Deflected | 20% | Load shedding kWh |\n"
            "| Uptime Score | 10% | System availability % |\n\n"
            "**Formula**: `ESG = (water_score × 0.35) + (co2_score × 0.35) + (energy_score × 0.20) + (uptime × 0.10)`\n\n"
            "Scores are stored in the `esg_metrics` table and visualized in the **🌱 ESG Dashboard** tab."
        )
    },
    {
        "id": "alerts",
        "tags": ["alert", "telegram", "notification", "alarm", "configure", "bot token", "chat id"],
        "question": "How do I configure Telegram alerts?",
        "answer": (
            "**Telegram Alert Setup:**\n\n"
            "1. Open **@BotFather** on Telegram → create a new bot → copy the **Bot Token**\n"
            "2. Open **@userinfobot** → send it a message → copy your **Chat ID**\n"
            "3. In the **🚨 Alert Center** tab → expand **Alert Gateway Config**\n"
            "4. Paste your Bot Token and Chat ID → click **🧪 Send Test Alert**\n\n"
            "**Alert Severity Levels:**\n"
            "- 🔵 **INFO** — normal operations notification\n"
            "- 🟡 **WARNING** — degraded performance detected\n"
            "- 🔴 **CRITICAL** — immediate action required\n"
            "- 🚨 **EMERGENCY** — automated mitigation activated\n\n"
            "Alerts are also stored in the **alerts** SQLite table for audit purposes."
        )
    },
    {
        "id": "rbac",
        "tags": ["role", "access", "permission", "admin", "operator", "viewer", "rbac", "who can"],
        "question": "What can each role do in the system?",
        "answer": (
            "**Role-Based Access Control (RBAC):**\n\n"
            "| Feature | Admin | Operator | Viewer |\n"
            "|---------|:-----:|:--------:|:------:|\n"
            "| View all dashboards | ✅ | ✅ | ✅ |\n"
            "| Trigger anomaly scenarios | ✅ | ✅ | ❌ |\n"
            "| Configure Telegram alerts | ✅ | ✅ | ❌ |\n"
            "| Acknowledge alerts | ✅ | ✅ | ❌ |\n"
            "| Download PDF reports | ✅ | ✅ | ❌ |\n"
            "| Clear audit logs | ✅ | ❌ | ❌ |\n"
            "| Manage users | ✅ | ❌ | ❌ |\n"
            "| Export raw data | ✅ | ❌ | ❌ |\n\n"
            "**Default Credentials (change after first login!):**\n"
            "- Admin: `admin` / `Admin@Nexus2026!`\n"
            "- Operator: `operator1` / `Operator@2026#`\n"
            "- Viewer: `viewer1` / `Viewer@View123`"
        )
    },
    {
        "id": "digital_twin",
        "tags": ["digital twin", "3d", "map", "pydeck", "geo", "spatial", "node", "visualization"],
        "question": "How does the Digital Twin work?",
        "answer": (
            "**3D Geo-Spatial Digital Twin** uses PyDeck (deck.gl) to render a live 3D map:\n\n"
            "**Nodes Monitored:**\n"
            "| Node | Location | Normal Temp | Status |\n"
            "|------|----------|-------------|--------|\n"
            "| Hydro-Node-Alpha | New Delhi | 42.5°C | Green |\n"
            "| Thermal-Node-Beta | New Delhi | 68.0°C | Yellow |\n"
            "| Cooling-Tower-Gamma | New Delhi | 89.2°C | Red |\n\n"
            "**Column height** = proportional to temperature\n"
            "**Column color:**\n"
            "- 🟢 Green = Normal  |  🟡 Yellow = Warning  |  🔴 Red = Critical\n\n"
            "When an anomaly is triggered, the affected node changes color and height in real-time."
        )
    },
    {
        "id": "pdf_report",
        "tags": ["pdf", "report", "download", "export", "incident", "compliance"],
        "question": "How do I generate and download an incident report?",
        "answer": (
            "**PDF Incident Report Generation:**\n\n"
            "1. Go to the **🤖 RCA Engine** tab\n"
            "2. Trigger an anomaly scenario (requires Operator/Admin role)\n"
            "3. The RCA analysis will populate automatically\n"
            "4. Click **📄 Download Incident PDF Report** button\n\n"
            "**Report Contents:**\n"
            "- Anomaly type and timestamp\n"
            "- Primary failure vector and root cause\n"
            "- Automated mitigation actions taken\n"
            "- ESG impact metrics (CO₂, water, energy)\n"
            "- Compliance statement for regulatory audit\n\n"
            "Reports are generated using **ReportLab** and are immediately downloadable without storage on server."
        )
    },
    {
        "id": "security",
        "tags": ["security", "secure", "encryption", "password", "hash", "safe", "data protection"],
        "question": "How is user data secured?",
        "answer": (
            "**Security Architecture:**\n\n"
            "🔐 **Authentication**\n"
            "- Passwords hashed with SHA-256 + application salt\n"
            "- Account lockout after 5 failed attempts (15-min cooldown)\n"
            "- Session tokens (UUID4) with 8-hour expiry\n\n"
            "🛡️ **Data Protection**\n"
            "- All PII fields auto-anonymized via SHA-256 hashing\n"
            "- SQL injection prevention via parameterized queries\n"
            "- Input sanitization strips HTML entities + SQL keywords\n\n"
            "🔒 **Access Control**\n"
            "- Strict RBAC with 3 roles (Admin / Operator / Viewer)\n"
            "- Every action logged to tamper-evident SQLite audit trail\n"
            "- FastAPI backend secured with API key header (`X-API-Key`)\n\n"
            "📋 **Audit Trail**\n"
            "- All logins, anomaly triggers, and data exports are logged\n"
            "- Logs include timestamp, username, role, and action details"
        )
    },
    {
        "id": "sensors",
        "tags": ["sensor", "kpi", "metric", "pressure", "temperature", "energy", "flow", "reading"],
        "question": "What sensors does the system monitor?",
        "answer": (
            "**Monitored Sensors & KPIs:**\n\n"
            "| Sensor | Unit | Normal Range | Alert Threshold |\n"
            "|--------|------|-------------|----------------|\n"
            "| Hydraulic Pressure | PSI | 38–46 | < 35 or > 50 |\n"
            "| Thermal Loop Temp | °C | 60–75 | > 89 |\n"
            "| Energy Consumption | kW | 120–140 | > 160 |\n"
            "| Water Flow Rate | L/min | 100–130 | < 40 |\n"
            "| Outdoor Temp | °C | 28–38 | > 42 |\n"
            "| Humidity | % | 45–85 | > 90 |\n\n"
            "All sensors stream every **6 hours** in production mode.\n"
            "Enable **Live Sensor Streaming** toggle for real-time simulation updates."
        )
    },
    {
        "id": "help",
        "tags": ["help", "how to", "guide", "tutorial", "start", "begin", "steps", "instructions"],
        "question": "How do I get started with the system?",
        "answer": (
            "**Getting Started with HydroThermal Nexus-AI:**\n\n"
            "**Step 1** — Log in with your credentials (see RBAC for defaults)\n\n"
            "**Step 2** — Visit the **🏠 Command Center** tab for a system health overview\n\n"
            "**Step 3** — Enable **Live Sensor Streaming** in **📈 Telemetry** tab\n\n"
            "**Step 4** — Configure Telegram alerts in **🚨 Alert Center** tab\n\n"
            "**Step 5** — Try triggering an anomaly to see the full RCA workflow\n\n"
            "**Step 6** — Check the **🌐 Digital Twin** to see geo-spatial impact\n\n"
            "**Step 7** — Download a PDF report from the **🤖 RCA Engine** tab\n\n"
            "💡 **Tip**: Ask me anything! I can explain any feature, interpret alerts, or guide you through the system."
        )
    }
]


# ── Intent Detection ─────────────────────────────────────────────────
def detect_intent(user_message: str) -> Optional[Dict]:
    """Fuzzy keyword-based intent matching."""
    msg_lower = user_message.lower()
    # Remove punctuation
    msg_clean = re.sub(r"[^\w\s]", " ", msg_lower)
    words = set(msg_clean.split())

    best_match = None
    best_score = 0

    for entry in KNOWLEDGE_BASE:
        score = 0
        for tag in entry["tags"]:
            tag_words = tag.lower().split()
            # Full phrase match
            if tag.lower() in msg_lower:
                score += len(tag_words) * 3
            # Individual word matches
            for w in tag_words:
                if w in words:
                    score += 1
        if score > best_score:
            best_score = score
            best_match = entry

    return best_match if best_score > 0 else None


# ── Fallback Response Generator ──────────────────────────────────────
def _fallback_response(message: str, system_state: Dict) -> str:
    anomaly = system_state.get("current_anomaly", "Nominal / Normal Operations")
    status_line = f"Current system state: **{anomaly}**"
    return (
        f"I don't have a specific answer for that query, but I can help with:\n\n"
        f"- 🔍 Anomaly detection & RCA analysis\n"
        f"- 🌱 ESG metrics and sustainability tracking\n"
        f"- 🔐 Security, roles, and access control\n"
        f"- 📊 Sensor thresholds and alert configuration\n"
        f"- 📄 PDF report generation\n\n"
        f"{status_line}\n\n"
        f"Try asking: *'How does anomaly detection work?'* or *'What is my ESG score?'*"
    )


# ── State-Aware Context Injection ────────────────────────────────────
def _inject_state_context(base_answer: str, system_state: Dict) -> str:
    """Prepends live system state context to the answer if relevant."""
    anomaly = system_state.get("current_anomaly", "Nominal / Normal Operations")
    score = system_state.get("health_score", 97.4)
    ts = datetime.datetime.now().strftime("%H:%M:%S")

    context = (
        f"> 🕐 **System Snapshot @ {ts}** — "
        f"State: `{anomaly}` | Health: `{score}%`\n\n"
    )
    return context + base_answer


# ── Quick Action Suggestions ─────────────────────────────────────────
QUICK_ACTIONS = [
    "What is HydroThermal Nexus-AI?",
    "How does anomaly detection work?",
    "How do I configure Telegram alerts?",
    "What can each role do?",
    "How is the ESG score calculated?",
    "How do I download a report?",
    "What sensors does the system monitor?",
    "How is user data secured?",
]


# ── Main Chat Function ───────────────────────────────────────────────
def get_ai_response(user_message: str, system_state: Dict,
                    conversation_history: List[Dict]) -> str:
    """
    Returns an AI response string given user message, system state,
    and conversation history.
    """
    if not user_message.strip():
        return "Please type a question or select one of the quick actions below."

    # Greetings
    greet_words = {"hi", "hello", "hey", "good morning", "good evening", "howdy"}
    if any(g in user_message.lower() for g in greet_words):
        user = system_state.get("username", "there")
        role = system_state.get("role", "")
        return (
            f"👋 Hello **{user}** ({role})! I'm your **Nexus-AI Assistant**.\n\n"
            f"I have full knowledge of this system — anomalies, ESG metrics, alerts, security, "
            f"sensor data, and operational procedures. How can I help you today?\n\n"
            f"*Try one of the quick action chips below, or type your question!*"
        )

    # Status query
    if any(w in user_message.lower() for w in ["status", "current", "state", "running", "working"]):
        anomaly = system_state.get("current_anomaly", "Nominal / Normal Operations")
        score   = system_state.get("health_score", 97.4)
        return (
            f"**Current System Status:**\n\n"
            f"| Parameter | Value |\n"
            f"|-----------|-------|\n"
            f"| System State | `{anomaly}` |\n"
            f"| Health Score | `{score}%` |\n"
            f"| Hydraulic Pressure | `42.5 PSI` |\n"
            f"| Thermal Temp | `68.4°C` |\n"
            f"| Energy Load | `128 kW` |\n"
            f"| Last Updated | `{datetime.datetime.now().strftime('%H:%M:%S')}` |\n\n"
            f"{'⚠️ **Action Required** — Check RCA Engine for root cause analysis.' if anomaly != 'Nominal / Normal Operations' else '✅ All systems operating within normal parameters.'}"
        )

    intent = detect_intent(user_message)
    if intent:
        return _inject_state_context(intent["answer"], system_state)
    else:
        return _fallback_response(user_message, system_state)
