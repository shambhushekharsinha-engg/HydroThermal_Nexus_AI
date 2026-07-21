# -*- coding: utf-8 -*-
"""
app.py — HydroThermal Nexus-AI v2.1
Professional-grade operational cockpit with:
  • Secure login (SHA-256 + session tokens)
  • 9 feature-rich tabs (+ Data Insights / EDA)
  • FastAPI backend (background thread)
  • IsolationForest ML anomaly detection (sklearn)
  • Plotly charts, ESG financial calculator, AI assistant, Alert center
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import threading
import base64
import os
import sys

# ── Local imports ────────────────────────────────────────────────────
from backend import database as db
from backend.security import (
    has_permission, get_role_badge, get_severity_badge,
    sanitize_input, validate_username, validate_password_strength
)
from ml_engine import HydroThermalAnalyticsCore
from report_generator import EnterpriseReportEngine
from ai_assistant import get_ai_response, QUICK_ACTIONS
from alert_manager import dispatch_alert, build_anomaly_alert, send_telegram

# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="HydroThermal Nexus-AI",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap DB & Seed Users ────────────────────────────────────────
db.initialize_all_databases()
db.seed_default_users()

# ── Start FastAPI Backend ────────────────────────────────────────────
def _start_api():
    try:
        import uvicorn
        uvicorn.run("backend.api:app", host="0.0.0.0", port=8001,
                    log_level="error", access_log=False)
    except Exception:
        pass

if "api_thread_started" not in st.session_state:
    t = threading.Thread(target=_start_api, daemon=True)
    t.start()
    st.session_state.api_thread_started = True

# ── CSS Injection ────────────────────────────────────────────────────
def _load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

_load_css()

# ── Logo helper ──────────────────────────────────────────────────────
def _logo_b64() -> str:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = _logo_b64()

# ── Plotly Dark Layout ────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    showlegend=True,
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.08)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
)

def hex_to_rgba(hex_str: str, alpha: float = 0.08) -> str:
    h = hex_str.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

# ════════════════════════════════════════════════════════════════════
# SECTION 1 — AUTHENTICATION
# ════════════════════════════════════════════════════════════════════
def show_login():
    """Full-page login & registration screen with tabbed layout & privacy enforcement."""
    # Centre the login card via empty columns
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        logo_html = (
            f'<img src="data:image/png;base64,{LOGO_B64}" />'
            if LOGO_B64 else '<div style="font-size:3rem;text-align:center;">🔷</div>'
        )
        st.markdown(f"""
        <div class="login-container">
          <div class="login-logo">{logo_html}</div>
          <div class="login-title">HydroThermal Nexus-AI</div>
          <div class="login-subtitle">Secure Industrial Cockpit & Telemetry Platform</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register / Sign Up"])

        # ── TAB 1: SIGN IN ──────────────────────────────────────────────
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter username", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
                submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

                if submitted:
                    uname = sanitize_input(username, max_len=32)
                    user = db.validate_user(uname, password)
                    if user:
                        token = db.create_session(user["username"], user["role"])
                        st.session_state["session_token"] = token
                        st.session_state["username"]      = user["username"]
                        st.session_state["role"]          = user["role"]
                        st.session_state["authenticated"] = True
                        db.log_audit(user["username"], user["role"], "LOGIN", "None", "User signed in.")
                        st.success("✅ Credentials verified. Launching cockpit...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials or account locked. Try again.")

            with st.expander("🔑 Verified Demo Credentials", expanded=True):
                st.markdown("""
                | Role | Username | Password | Access Level |
                |------|----------|----------|--------------|
                | **Admin** | `admin` | `Admin@Nexus2026!` | Full Admin Rights |
                | **Operator** | `operator1` | `Operator@2026#` | Control & Telemetry |
                | **Viewer** | `viewer1` | `Viewer@View123` | Read-only Analytics |
                """)

        # ── TAB 2: REGISTER / SIGN UP ────────────────────────────────────
        with tab_register:
            st.caption("Create a new secure operational account.")
            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input("Choose Username", placeholder="3–32 letters, digits, _, -, .", key="reg_username")
                reg_email    = st.text_input("Corporate Email (Optional)", placeholder="user@organization.com", key="reg_email")
                reg_role     = st.selectbox("Requested Role", ["Viewer", "Operator", "Admin"], index=0,
                                             help="Viewer: Read-only analytics | Operator: Controls & Alerts | Admin: System management", key="reg_role")
                reg_password = st.text_input("Password", type="password", placeholder="Min 8 chars, 1 upper, 1 digit, 1 symbol", key="reg_password")
                reg_confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
                
                # Privacy Maintenance & Consent
                privacy_consent = st.checkbox(
                    "🔒 Privacy Agreement: I consent to salted SHA-256 password hashing and session-only tracking under Nexus-AI Privacy Standards.",
                    value=True,
                    key="privacy_consent"
                )

                reg_submitted = st.form_submit_button("📝 Register Account", use_container_width=True)

                if reg_submitted:
                    if not privacy_consent:
                        st.error("❌ You must accept the Privacy Agreement to create an account.")
                    else:
                        uname = sanitize_input(reg_username, max_len=32)
                        email = sanitize_input(reg_email, max_len=64)

                        # Security Validations
                        is_valid_u, err_u = validate_username(uname)
                        if not is_valid_u:
                            st.error(f"❌ {err_u}")
                        elif reg_password != reg_confirm:
                            st.error("❌ Passwords do not match.")
                        else:
                            is_valid_p, err_p = validate_password_strength(reg_password)
                            if not is_valid_p:
                                st.error(f"❌ {err_p}")
                            else:
                                success, msg = db.register_user(uname, reg_password, role=reg_role, email=email)
                                if success:
                                    st.success(f"✅ {msg}")
                                    st.info("👉 Switch to the **🔐 Sign In** tab to log in with your new credentials.")
                                else:
                                    st.error(f"❌ {msg}")

        st.markdown("""
        <div style="text-align:center;margin-top:1rem;font-size:0.72rem;color:#64748B;">
        🛡️ Privacy Preserving &middot; SHA-256 Hashing &middot; Salted Keys &middot; PII Masking &middot; Session Expiry
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# SECTION 2 — SIDEBAR
# ════════════════════════════════════════════════════════════════════
def show_sidebar():
    username = st.session_state.get("username", "User")
    role     = st.session_state.get("role", "Viewer")
    anomaly  = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    is_ok    = anomaly == "Nominal / Normal Operations"

    with st.sidebar:
        # Logo + brand
        logo_html = (
            f'<img src="data:image/png;base64,{LOGO_B64}" '
            f'style="width:72px;height:72px;border-radius:50%;'
            f'border:2px solid #00D4FF;box-shadow:0 0 20px rgba(0,212,255,0.4);">'
        ) if LOGO_B64 else "🔷"

        st.markdown(
            f'<div class="sidebar-logo-container">'
            f'{logo_html}'
            f'<div style="margin-top:0.6rem;font-size:1rem;font-weight:700;background:linear-gradient(135deg,#00D4FF,#FF6B35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Nexus-AI</div>'
            f'<div style="font-size:0.68rem;color:#64748B;margin-top:0.1rem;">v2.0 · Industrial IoT</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # User info
        st.markdown(
            f'<div class="glass-panel" style="padding:0.8rem 1rem;margin-bottom:0.8rem;">'
            f'<div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Signed In As</div>'
            f'<div style="font-size:0.95rem;font-weight:700;color:#E2E8F0;">👤 {username}</div>'
            f'<div style="margin-top:0.3rem;">{get_role_badge(role)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # System status
        dot_cls = "online" if is_ok else "critical"
        status_text = "All Systems Nominal" if is_ok else anomaly
        color = "#00FF88" if is_ok else "#FF2D55"
        st.markdown(
            f'<div class="glass-panel" style="padding:0.8rem 1rem;margin-bottom:0.8rem;">'
            f'<div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">System Status</div>'
            f'<div style="display:flex;align-items:center;gap:6px;">'
            f'<span class="status-dot {dot_cls}"></span>'
            f'<span style="font-size:0.8rem;color:{color};font-weight:600;">{status_text}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Quick stats
        st.markdown(
            '<div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;margin:0.5rem 0 0.4rem;">Quick Stats</div>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        c1.metric("Pressure", "42.5 PSI", "+1.2%")
        c2.metric("Thermal", "68.4°C", "-0.8°C")

        st.markdown("---")

        # Telegram config
        st.markdown("**🚨 Alert Gateway**")
        bot_token = st.text_input("Bot Token", type="password", key="bot_token",
                                  help="From @BotFather on Telegram")
        chat_id   = st.text_input("Chat ID", key="chat_id",
                                  help="From @userinfobot on Telegram")
        if st.button("🧪 Test Alert", use_container_width=True):
            if has_permission(role, "send_telegram"):
                ok, msg = send_telegram(bot_token, chat_id,
                                        "🔷 *Nexus-AI Test*\nAlert gateway is active!")
                if ok: st.success(msg)
                else:  st.error(msg)
            else:
                st.warning("🔒 Insufficient permissions.")

        st.markdown("---")

        # Logout
        if st.button("🚪 Sign Out", use_container_width=True):
            token = st.session_state.get("session_token")
            if token:
                db.revoke_session(token)
                db.log_audit(username, role, "LOGOUT", "None", "User signed out.")
            for k in ["authenticated","session_token","username","role",
                      "current_anomaly","chat_history","health_score"]:
                st.session_state.pop(k, None)
            st.rerun()


# ════════════════════════════════════════════════════════════════════
# SECTION 3 — ANIMATED HEADER
# ════════════════════════════════════════════════════════════════════
def show_header():
    username = st.session_state.get("username", "User")
    role     = st.session_state.get("role", "Viewer")
    now_str  = datetime.datetime.now().strftime("%d %b %Y  •  %H:%M")

    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" '
        f'style="width:56px;height:56px;border-radius:50%;'
        f'border:2px solid #00D4FF;box-shadow:0 0 20px rgba(0,212,255,0.4);">'
    ) if LOGO_B64 else '<div style="font-size:2.5rem;">🔷</div>'

    st.markdown(f"""
    <div class="nexus-header">
      {logo_html}
      <div>
        <div class="nexus-header-title">HydroThermal Nexus-AI</div>
        <div class="nexus-header-sub">
          Multi-Tenant Operational Cockpit &middot; Climate Action &amp; Industrial Telemetry
        </div>
      </div>
      <div style="margin-left:auto;text-align:right;">
        <div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:0.1em;">
          {now_str}
        </div>
        <div style="margin-top:0.2rem;">{get_role_badge(role)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# HELPER — Plotly chart wrapper
# ════════════════════════════════════════════════════════════════════
def _plotly(fig, height=320):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ════════════════════════════════════════════════════════════════════
# TAB 1 — COMMAND CENTER
# ════════════════════════════════════════════════════════════════════
def tab_command_center():
    role    = st.session_state.get("role", "Viewer")
    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    score   = st.session_state.get("health_score", 97.4)
    is_ok   = anomaly == "Nominal / Normal Operations"

    # KPI cards row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
        <div class="kpi-card cyan">
          <div class="kpi-icon">💧</div>
          <div class="kpi-label">Hydraulic Pressure</div>
          <div class="kpi-value">42.5</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">PSI</div>
          <div class="kpi-delta up">▲ +1.2% vs baseline</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="kpi-card orange">
          <div class="kpi-icon">🌡️</div>
          <div class="kpi-label">Thermal Loop Temp</div>
          <div class="kpi-value orange">68.4</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">°C</div>
          <div class="kpi-delta down">▼ -0.8°C from last cycle</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="kpi-card green">
          <div class="kpi-icon">⚡</div>
          <div class="kpi-label">Energy Consumption</div>
          <div class="kpi-value green">128</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">kW</div>
          <div class="kpi-delta up">▲ +3.1% load increase</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        score_color = "#00FF88" if score >= 90 else "#FFB800" if score >= 70 else "#FF2D55"
        st.markdown(f"""
        <div class="kpi-card {'green' if score>=90 else 'yellow' if score>=70 else 'red'}">
          <div class="kpi-icon">🛡️</div>
          <div class="kpi-label">System Health Score</div>
          <div class="kpi-value" style="color:{score_color};">{score}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">/ 100</div>
          <div class="kpi-delta {'up' if score>=90 else 'down'}">
            {'✅ Excellent' if score>=90 else '⚠️ Degraded' if score>=70 else '🚨 Critical'}
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Health gauge + Recent alerts
    col_g, col_a = st.columns([1, 1.6])

    with col_g:
        st.markdown('<div class="section-title">⬤ Health Score Ring</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            delta={"reference": 90, "valueformat": ".1f",
                   "increasing": {"color": "#00FF88"},
                   "decreasing": {"color": "#FF2D55"}},
            number={"font": {"color": "#00D4FF", "size": 36}, "suffix": "%"},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#374151",
                         "tickfont": {"color": "#64748B"}},
                "bar":  {"color": "#00D4FF", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,0.1)",
                "steps": [
                    {"range": [0, 60],   "color": "rgba(255,45,85,0.12)"},
                    {"range": [60, 80],  "color": "rgba(255,184,0,0.12)"},
                    {"range": [80, 100], "color": "rgba(0,255,136,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#FF2D55", "width": 2},
                    "thickness": 0.75, "value": 70
                }
            }
        ))
        _plotly(fig_gauge, height=280)

    with col_a:
        st.markdown('<div class="section-title">🔔 Recent Alerts</div>', unsafe_allow_html=True)
        alerts_df = db.get_alerts(limit=5)
        if alerts_df.empty:
            st.markdown("""
            <div class="glass-panel" style="text-align:center;color:#64748B;padding:2rem;">
              <div style="font-size:2rem;">✅</div>
              <div>No active alerts — system nominal</div>
            </div>""", unsafe_allow_html=True)
        else:
            for _, row in alerts_df.iterrows():
                sev = str(row.get("severity", "INFO")).upper()
                sev_cls = {"CRITICAL":"critical","WARNING":"warning",
                           "EMERGENCY":"critical","INFO":"info"}.get(sev, "info")
                ack = "✅" if row.get("acknowledged", 0) else "🔔"
                st.markdown(f"""
                <div class="alert-item {sev_cls}">
                  <div>
                    <div style="font-size:0.8rem;font-weight:600;color:#E2E8F0;">
                      {ack} {row.get('title','Alert')}
                    </div>
                    <div style="font-size:0.7rem;color:#64748B;margin-top:2px;">
                      {row.get('timestamp','—')}
                    </div>
                  </div>
                  {get_severity_badge(sev)}
                </div>""", unsafe_allow_html=True)

    # Live mini sparklines
    st.markdown('<div class="section-title" style="margin-top:1rem;">📈 Live Sensor Sparklines</div>',
                unsafe_allow_html=True)
    np.random.seed(int(datetime.datetime.now().timestamp()) % 9999)
    t_axis = [datetime.datetime.now() - datetime.timedelta(minutes=30*i) for i in range(20, 0, -1)]

    s1, s2, s3 = st.columns(3)
    for col, label, base, unit, color in [
        (s1, "Hydraulic Pressure", 42.5, "PSI", "#00D4FF"),
        (s2, "Thermal Temp",       68.4, "°C",  "#FF6B35"),
        (s3, "Energy Load",        128,  "kW",   "#00FF88"),
    ]:
        with col:
            vals = base + np.cumsum(np.random.randn(20) * 0.3)
            fig = go.Figure(go.Scatter(
                x=t_axis, y=vals, mode="lines",
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=hex_to_rgba(color, 0.08),
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=140)
            fig.update_xaxes(showticklabels=False)
            fig.update_layout(
                margin=dict(l=0, r=0, t=24, b=0),
                title=dict(text=f"{label} ({unit})", font=dict(size=11, color="#64748B"))
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})


# ════════════════════════════════════════════════════════════════════
# TAB 2 — TELEMETRY & ANALYTICS
# ════════════════════════════════════════════════════════════════════
def tab_telemetry():
    role     = st.session_state.get("role", "Viewer")
    username = st.session_state.get("username", "User")

    st.markdown('<div class="section-title">⚙️ Anomaly Injection Console</div>',
                unsafe_allow_html=True)

    bot_token = st.session_state.get("bot_token", "")
    chat_id   = st.session_state.get("chat_id", "")

    if has_permission(role, "trigger_anomaly"):
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            anomaly_sel = st.selectbox("Select Anomaly Scenario", [
                "Nominal / Normal Operations",
                "Pipe Rupture / Flow Drop",
                "HVAC Overheat / Thermal Spike",
            ], key="anomaly_select")
        with col_btn:
            st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Trigger Scenario", use_container_width=True):
                st.session_state["current_anomaly"] = anomaly_sel
                st.session_state["health_score"] = (
                    97.4 if anomaly_sel == "Nominal / Normal Operations"
                    else 42.1 if anomaly_sel == "Pipe Rupture / Flow Drop"
                    else 63.8
                )
                template = build_anomaly_alert(anomaly_sel, username)
                dispatch_alert(
                    severity=template["severity"],
                    title=template["title"],
                    message=template["message"],
                    anomaly_type=anomaly_sel,
                    username=username,
                    role=role,
                    telegram_token=bot_token,
                    telegram_chat=chat_id,
                    force=True,
                )
                if anomaly_sel == "Nominal / Normal Operations":
                    st.success("✅ System reset to Nominal Operations.")
                else:
                    st.error(f"🚨 Anomaly '{anomaly_sel}' activated — Alert dispatched!")
    else:
        st.info("🔒 Viewer role cannot inject anomaly scenarios.")

    st.markdown("---")
    st.markdown('<div class="section-title">🔄 Live Telemetry Stream</div>',
                unsafe_allow_html=True)

    live_toggle = st.toggle("Enable Live Sensor Streaming", key="live_toggle")
    np.random.seed(int(datetime.datetime.now().second) if live_toggle else 42)

    pressure  = round(42.5 + np.random.uniform(-0.5, 0.5), 2) if live_toggle else 42.5
    temp      = round(68.4 + np.random.uniform(-0.3, 0.3), 2) if live_toggle else 68.4
    energy    = round(128  + np.random.uniform(-1.0, 1.0),  2) if live_toggle else 128.0
    flow      = round(120  + np.random.uniform(-2.0, 2.0),  2) if live_toggle else 120.0
    humidity  = round(65   + np.random.uniform(-1.0, 1.0),  2) if live_toggle else 65.0
    outdoor_t = round(32   + np.random.uniform(-0.5, 0.5),  2) if live_toggle else 32.0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Pressure",    f"{pressure} PSI",  "+1.2%")
    m2.metric("Thermal",     f"{temp}°C",        "-0.8°C")
    m3.metric("Energy",      f"{energy} kW",     "+3.1%")
    m4.metric("Flow Rate",   f"{flow} L/m",      "+0.4%")
    m5.metric("Humidity",    f"{humidity}%",     "-0.5%")
    m6.metric("Outdoor Temp",f"{outdoor_t}°C",   "+0.2°C")

    # Historical chart
    st.markdown('<div class="section-title" style="margin-top:1rem;">📊 Historical Telemetry</div>',
                unsafe_allow_html=True)

    analytics = HydroThermalAnalyticsCore()
    df = analytics.generate_live_production_stream()
    if live_toggle:
        db.save_telemetry(energy, flow * 25, outdoor_t, humidity, pressure, temp)

    chart_type = st.radio("Chart View", ["Multi-Sensor", "Electricity", "Water Flow"],
                          horizontal=True, key="chart_type")

    if chart_type == "Multi-Sensor":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Electricity (kWh)", "Water (Litres)"),
                            vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Electricity_kWh"],
                                 name="Electricity", mode="lines",
                                 line=dict(color="#00D4FF", width=2),
                                 fill="tozeroy", fillcolor="rgba(0,212,255,0.07)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Water_Litres"],
                                 name="Water", mode="lines",
                                 line=dict(color="#FF6B35", width=2),
                                 fill="tozeroy", fillcolor="rgba(255,107,53,0.07)"), row=2, col=1)
        _plotly(fig, height=380)
    elif chart_type == "Electricity":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Electricity_kWh"],
                                 name="kWh", mode="lines+markers",
                                 line=dict(color="#00D4FF", width=2),
                                 marker=dict(size=4, color="#00D4FF")))
        fig.add_hline(y=2200, line_dash="dot", line_color="#FFB800",
                      annotation_text="Baseline", annotation_position="right")
        _plotly(fig, height=300)
    else:
        fig = px.area(df, x="Timestamp", y="Water_Litres",
                      color_discrete_sequence=["#FF6B35"])
        _plotly(fig, height=300)

    # Correlation heatmap
    with st.expander("🔬 Sensor Correlation Heatmap"):
        corr = df[["Electricity_kWh","Water_Litres","Outdoor_Temp_C","Humidity_Pct"]].corr()
        fig_heat = px.imshow(corr, text_auto=".2f",
                             color_continuous_scale=[[0,"#FF2D55"],[0.5,"#111827"],[1,"#00D4FF"]],
                             aspect="auto")
        _plotly(fig_heat, height=280)


# ════════════════════════════════════════════════════════════════════
# TAB 3 — DIGITAL TWIN
# ════════════════════════════════════════════════════════════════════
def tab_digital_twin():
    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    st.markdown('<div class="section-title">🌐 Geo-Spatial Digital Twin</div>',
                unsafe_allow_html=True)
    st.caption("3D column height = node temperature. Color = operational status.")

    nodes = [
        {"node_id":"Hydro-Node-Alpha",    "lat":28.6139,"lon":77.2090,
         "status":"Normal",   "flow_rate":120,"temp":42.5},
        {"node_id":"Thermal-Node-Beta",   "lat":28.6150,"lon":77.2110,
         "status":"Warning",  "flow_rate":85, "temp":68.0},
        {"node_id":"Cooling-Tower-Gamma", "lat":28.6120,"lon":77.2070,
         "status":"Critical", "flow_rate":30, "temp":89.2},
    ]

    if anomaly == "Pipe Rupture / Flow Drop":
        nodes[0]["status"] = "Critical"; nodes[0]["flow_rate"] = 10
    elif anomaly == "HVAC Overheat / Thermal Spike":
        nodes[1]["status"] = "Critical"; nodes[1]["temp"] = 105.0

    df_nodes = pd.DataFrame(nodes)
    color_map = {
        "Normal":   [0, 212, 100, 200],
        "Warning":  [255, 184, 0, 210],
        "Critical": [255, 45, 85, 230],
    }
    df_nodes["color"] = df_nodes["status"].map(color_map)

    layer = pdk.Layer("ColumnLayer", data=df_nodes,
                      get_position=["lon","lat"],
                      get_elevation="temp",
                      elevation_scale=22, radius=40,
                      get_fill_color="color",
                      pickable=True, auto_highlight=True)

    view = pdk.ViewState(latitude=28.6139, longitude=77.2090, zoom=15, pitch=55)
    st.pydeck_chart(pdk.Deck(
        layers=[layer], initial_view_state=view,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "📍 {node_id}\nStatus: {status}\n🌡️ {temp}°C\n💧 {flow_rate} L/m"}
    ))

    # Node status cards
    st.markdown('<div class="section-title" style="margin-top:1rem;">📋 Node Status Cards</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, node in zip([c1, c2, c3], nodes):
        s = node["status"]
        c = {"Normal":"#00FF88","Warning":"#FFB800","Critical":"#FF2D55"}.get(s,"#aaa")
        with col:
            st.markdown(f"""
            <div class="kpi-card {'green' if s=='Normal' else 'yellow' if s=='Warning' else 'red'}">
              <div class="kpi-label">{node['node_id']}</div>
              <div class="kpi-value" style="font-size:1.4rem;color:{c};">{s}</div>
              <div style="margin-top:0.4rem;font-size:0.8rem;color:#64748B;">
                🌡️ {node['temp']}°C &nbsp;·&nbsp; 💧 {node['flow_rate']} L/m
              </div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4 — RCA ENGINE
# ════════════════════════════════════════════════════════════════════
def tab_rca():
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as rl_colors

    role     = st.session_state.get("role", "Viewer")
    username = st.session_state.get("username", "User")
    anomaly  = st.session_state.get("current_anomaly", "Nominal / Normal Operations")

    st.markdown('<div class="section-title">🤖 AI-Driven Diagnostic Engine</div>',
                unsafe_allow_html=True)
    st.info(f"Active System State: **{anomaly}**")

    rca_text = ""

    if anomaly == "Pipe Rupture / Flow Drop":
        rca_text = (
            "PRIMARY DIAGNOSTIC: Main Header Pressure Drop\n"
            "Root Cause: Solenoid Relay Valve Cutoff Failure\n"
            "Impact Rate: +240% fluid loss variance\n"
            "Mitigation: Actuated secondary bypass loop; throttled inlet pump.\n"
            "ESG Impact: Saved ~1,450 L/hr water loss."
        )
        st.error("🚨 **Critical Incident — Immediate Action Required**")
        a, b = st.columns(2)
        with a:
            st.markdown("""
            <div class="glass-panel">
              <div class="section-title">🔍 Primary Failure Vector</div>
              <p><b>Solenoid Valve / Main Header Pressure Breakdown</b></p>
              <p style="color:#64748B;font-size:0.85rem;">
                Calculated fluid loss rate exceeds normal threshold by <b style="color:#FF2D55;">+240%</b>.
                Solenoid relay cutoff failure detected on Hydro-Node-Alpha.
              </p>
            </div>""", unsafe_allow_html=True)
        with b:
            st.markdown("""
            <div class="glass-panel">
              <div class="section-title">🛠️ Automated Mitigation Path</div>
              <ol style="color:#E2E8F0;font-size:0.85rem;line-height:2;">
                <li>Solenoid valve throttled to <b>20% aperture</b></li>
                <li>Thermal loop rerouted to <b>auxiliary bypass</b></li>
                <li>Telegram alert dispatched to operations team</li>
                <li>Incident logged in SQLite audit ledger</li>
              </ol>
            </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-panel">
          <div class="section-title">🌱 ESG & Sustainability Impact</div>
          <div style="display:flex;gap:2rem;">
            <div><div class="kpi-label">Water Saved</div>
              <div style="font-size:1.6rem;font-weight:800;color:#00FF88;">1,450 L/hr</div></div>
            <div><div class="kpi-label">CO₂ Prevented</div>
              <div style="font-size:1.6rem;font-weight:800;color:#00D4FF;">12 kg</div></div>
            <div><div class="kpi-label">Valve State</div>
              <div style="font-size:1.6rem;font-weight:800;color:#FFB800;">20%</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    elif anomaly == "HVAC Overheat / Thermal Spike":
        rca_text = (
            "PRIMARY DIAGNOSTIC: Cooling Tower Thermal Exceedance\n"
            "Root Cause: Fan Motor Relay Stall\n"
            "Mitigation: Secondary auxiliary chiller engaged; compute racks throttled.\n"
            "ESG Impact: Avoided 38 kg CO2e in inefficient energy spikes."
        )
        st.warning("⚠️ **Warning Incident — Elevated Priority**")
        a, b = st.columns(2)
        with a:
            st.markdown("""
            <div class="glass-panel">
              <div class="section-title">🔍 Primary Failure Vector</div>
              <p><b>Cooling Tower Heat Exchange Degradation</b></p>
              <p style="color:#64748B;font-size:0.85rem;">
                Temperature ramp-up to <b style="color:#FF2D55;">105°C</b> indicates
                potential fan motor relay stall on Cooling-Tower-Gamma.
              </p>
            </div>""", unsafe_allow_html=True)
        with b:
            st.markdown("""
            <div class="glass-panel">
              <div class="section-title">🛠️ Automated Mitigation Path</div>
              <ol style="color:#E2E8F0;font-size:0.85rem;line-height:2;">
                <li>Secondary <b>auxiliary chiller</b> units engaged</li>
                <li>High-load compute racks <b>throttled to 40%</b></li>
                <li>Telegram + Email alerts dispatched</li>
                <li>Maintenance ticket flagged in audit DB</li>
              </ol>
            </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-panel">
          <div class="section-title">🌱 ESG & Sustainability Impact</div>
          <div style="display:flex;gap:2rem;">
            <div><div class="kpi-label">CO₂ Prevented</div>
              <div style="font-size:1.6rem;font-weight:800;color:#00FF88;">38 kg CO₂e</div></div>
            <div><div class="kpi-label">Energy Saved</div>
              <div style="font-size:1.6rem;font-weight:800;color:#00D4FF;">1,450 kWh</div></div>
            <div><div class="kpi-label">Penalty Avoided</div>
              <div style="font-size:1.6rem;font-weight:800;color:#FFB800;">₹12,400</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        rca_text = "SYSTEM NOMINAL: All parameters within normal thresholds."
        st.success("✅ All systems operating within normal parameters. No active failure vectors.")

    # PDF Download
    if anomaly != "Nominal / Normal Operations" and has_permission(role, "download_reports"):
        st.markdown("---")

        def _gen_pdf():
            buf = BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter,
                                    rightMargin=54, leftMargin=54,
                                    topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()
            title_s = ParagraphStyle("T", parent=styles["Heading1"],
                                     fontName="Helvetica-Bold", fontSize=22,
                                     textColor=rl_colors.HexColor("#1B2A4A"), spaceAfter=8)
            body_s  = ParagraphStyle("B", parent=styles["Normal"],
                                     fontName="Helvetica", fontSize=11, leading=16,
                                     textColor=rl_colors.HexColor("#2C3E50"), spaceAfter=8)

            story = [
                Paragraph("HydroThermal Nexus-AI — Incident Report", title_s),
                Paragraph(f"<b>Anomaly Type:</b> {anomaly}", body_s),
                Paragraph(f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_s),
                Paragraph(f"<b>Operator:</b> {username}", body_s),
                Spacer(1, 12),
                Paragraph("<b>Root Cause Analysis:</b>", body_s),
            ]
            for line in rca_text.split("\n"):
                story.append(Paragraph(line, body_s))
            story.append(Spacer(1, 12))
            story.append(Paragraph(
                "<b>Compliance Statement:</b> This document constitutes verified automated "
                "telemetry validation for carbon accounting and municipal utility conservation audits.",
                body_s
            ))
            doc.build(story)
            buf.seek(0)
            return buf

        pdf_buf = _gen_pdf()
        st.download_button(
            label="📄 Download Incident PDF Report",
            data=pdf_buf,
            file_name=f"NexusAI_RCA_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )


# ════════════════════════════════════════════════════════════════════
# TAB 5 — ESG DASHBOARD
# ════════════════════════════════════════════════════════════════════
def tab_esg():
    st.markdown('<div class="section-title">🌱 ESG Carbon & Sustainability Dashboard</div>',
                unsafe_allow_html=True)

    # Seed sample ESG data if empty
    esg_df = db.get_esg_history(days=30)
    if esg_df.empty:
        for i in range(14, 0, -1):
            d = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            db.upsert_esg(
                co2=round(np.random.uniform(30, 55), 1),
                water=round(np.random.uniform(900, 1600), 0),
                energy=round(np.random.uniform(200, 500), 1),
                score=round(np.random.uniform(72, 96), 1)
            )
        esg_df = db.get_esg_history(days=30)

    # Summary KPIs
    total_co2   = esg_df["co2_saved_kg"].sum() if "co2_saved_kg" in esg_df.columns else 0
    total_water = esg_df["water_saved_l"].sum() if "water_saved_l" in esg_df.columns else 0
    total_energy= esg_df["energy_saved_kwh"].sum() if "energy_saved_kwh" in esg_df.columns else 0
    avg_score   = esg_df["esg_score"].mean() if "esg_score" in esg_df.columns else 0

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">🌿</div>
          <div class="kpi-label">CO₂ Saved (30d)</div>
          <div class="kpi-value green">{total_co2:,.0f}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">kg CO₂e</div>
        </div>""", unsafe_allow_html=True)
    with e2:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-icon">💧</div>
          <div class="kpi-label">Water Conserved (30d)</div>
          <div class="kpi-value">{total_water:,.0f}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">Litres</div>
        </div>""", unsafe_allow_html=True)
    with e3:
        st.markdown(f"""
        <div class="kpi-card orange">
          <div class="kpi-icon">⚡</div>
          <div class="kpi-label">Energy Deflected (30d)</div>
          <div class="kpi-value orange">{total_energy:,.0f}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">kWh</div>
        </div>""", unsafe_allow_html=True)
    with e4:
        score_color = "#00FF88" if avg_score >= 80 else "#FFB800" if avg_score >= 60 else "#FF2D55"
        st.markdown(f"""
        <div class="kpi-card {'green' if avg_score>=80 else 'yellow' if avg_score>=60 else 'red'}">
          <div class="kpi-icon">🏆</div>
          <div class="kpi-label">Avg ESG Score (30d)</div>
          <div class="kpi-value" style="color:{score_color};">{avg_score:.1f}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">/ 100</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Charts
    if not esg_df.empty and "date" in esg_df.columns:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">🌿 CO₂ Savings Trend</div>',
                        unsafe_allow_html=True)
            fig = px.bar(esg_df, x="date", y="co2_saved_kg",
                         color_discrete_sequence=["#00FF88"])
            fig.update_layout(**PLOTLY_LAYOUT, height=260)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        with c2:
            st.markdown('<div class="section-title">💧 Water Conservation</div>',
                        unsafe_allow_html=True)
            fig = px.line(esg_df, x="date", y="water_saved_l",
                          color_discrete_sequence=["#00D4FF"],
                          markers=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=260)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        st.markdown('<div class="section-title">📊 ESG Score Timeline</div>',
                    unsafe_allow_html=True)
        fig_esg = go.Figure()
        fig_esg.add_trace(go.Scatter(
            x=esg_df["date"], y=esg_df["esg_score"],
            mode="lines+markers",
            line=dict(color="#00D4FF", width=3),
            marker=dict(size=7, color="#00D4FF"),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.07)",
            name="ESG Score"
        ))
        fig_esg.add_hline(y=80, line_dash="dot", line_color="#00FF88",
                          annotation_text="Target (80)", annotation_position="right")
        fig_esg.update_layout(**PLOTLY_LAYOUT, height=260)
        st.plotly_chart(fig_esg, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No ESG data yet. Trigger anomaly events to generate impact metrics.")

    st.markdown("---")

    # ── Financial Savings Calculator ──────────────────────────────────
    st.markdown('<div class="section-title">💰 Financial Savings Calculator</div>',
                unsafe_allow_html=True)
    st.caption("Adjust unit costs below to compute the real monetary value of each ESG intervention.")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        water_cost   = st.number_input("Water cost (₹ per Litre)",
                                       min_value=0.01, max_value=10.0,
                                       value=0.05, step=0.01, format="%.2f")
    with fc2:
        energy_cost  = st.number_input("Energy cost (₹ per kWh)",
                                       min_value=1.0, max_value=20.0,
                                       value=8.0, step=0.5, format="%.1f")
    with fc3:
        carbon_price = st.number_input("Carbon credit ($ per tonne CO₂e)",
                                       min_value=1.0, max_value=200.0,
                                       value=15.0, step=1.0, format="%.1f")

    # Compute savings
    water_savings_inr  = total_water  * water_cost
    energy_savings_inr = total_energy * energy_cost
    carbon_savings_usd = (total_co2 / 1000.0) * carbon_price   # kg → tonne
    usd_to_inr         = 83.5                                    # approx rate
    carbon_savings_inr = carbon_savings_usd * usd_to_inr
    total_savings_inr  = water_savings_inr + energy_savings_inr + carbon_savings_inr

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-icon">💧</div>
          <div class="kpi-label">Water Savings (30d)</div>
          <div class="kpi-value" style="font-size:1.5rem;">₹{water_savings_inr:,.0f}</div>
          <div style="color:#64748B;font-size:0.7rem;margin-top:2px;">
            {total_water:,.0f} L × ₹{water_cost}
          </div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card orange">
          <div class="kpi-icon">⚡</div>
          <div class="kpi-label">Energy Savings (30d)</div>
          <div class="kpi-value orange" style="font-size:1.5rem;">₹{energy_savings_inr:,.0f}</div>
          <div style="color:#64748B;font-size:0.7rem;margin-top:2px;">
            {total_energy:,.0f} kWh × ₹{energy_cost}
          </div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">🌿</div>
          <div class="kpi-label">Carbon Credits (30d)</div>
          <div class="kpi-value green" style="font-size:1.5rem;">₹{carbon_savings_inr:,.0f}</div>
          <div style="color:#64748B;font-size:0.7rem;margin-top:2px;">
            ${carbon_savings_usd:,.1f} @ ${carbon_price}/t
          </div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="kpi-card {'green' if total_savings_inr>0 else 'yellow'}">
          <div class="kpi-icon">🏦</div>
          <div class="kpi-label">Total Value Unlocked</div>
          <div class="kpi-value green" style="font-size:1.5rem;">₹{total_savings_inr:,.0f}</div>
          <div style="color:#64748B;font-size:0.7rem;margin-top:2px;">Combined 30-day savings</div>
        </div>""", unsafe_allow_html=True)

    # Savings breakdown donut chart
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    bc1, bc2 = st.columns([1, 1.5])
    with bc1:
        fig_pie = go.Figure(go.Pie(
            labels=["Water Savings", "Energy Savings", "Carbon Credits"],
            values=[water_savings_inr, energy_savings_inr, carbon_savings_inr],
            hole=0.55,
            marker=dict(colors=["#00D4FF", "#FF6B35", "#00FF88"],
                        line=dict(color="#0A0F1E", width=2)),
        ))
        fig_pie.update_traces(textfont_size=11,
                              hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>")
        fig_pie.update_layout(**PLOTLY_LAYOUT, height=260,
                              annotations=[dict(text=f"₹{total_savings_inr/1000:,.1f}K",
                                               x=0.5, y=0.5, font_size=16,
                                               font_color="#00D4FF", showarrow=False)])
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with bc2:
        # ── Before / After Comparison ─────────────────────────────────
        st.markdown('<div class="section-title">🔄 Before vs After Intervention</div>',
                    unsafe_allow_html=True)

        categories = ["Water Loss (L/hr)", "CO₂ Emissions (kg/event)",
                      "Energy Waste (kWh/d)", "Response Time (min)"]
        before_vals = [1450, 38, 1450, 240]
        after_vals  = [0,    0,  0,    15]

        fig_ba = go.Figure()
        fig_ba.add_trace(go.Bar(
            name="Before Nexus-AI", x=categories, y=before_vals,
            marker_color="#FF2D55", opacity=0.85,
        ))
        fig_ba.add_trace(go.Bar(
            name="After Nexus-AI", x=categories, y=after_vals,
            marker_color="#00FF88", opacity=0.85,
        ))
        fig_ba.update_layout(
            **PLOTLY_LAYOUT, height=260,
            barmode="group",
            xaxis_tickangle=-15,
        )
        st.plotly_chart(fig_ba, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="glass-panel" style="padding:0.8rem 1rem;margin-top:0.5rem;">
          <div style="font-size:0.75rem;color:#64748B;line-height:1.9;">
            💧 Water loss reduced from <b style="color:#FF2D55;">1,450 L/hr → 0</b> per incident<br>
            🌿 CO₂ emissions prevented: <b style="color:#00FF88;">38 kg/event</b><br>
            ⚡ Energy waste eliminated: <b style="color:#00FF88;">1,450 kWh/day</b><br>
            ⏱️ Incident response time: <b style="color:#FF2D55;">240 min →</b>
            <b style="color:#00FF88;"> 15 min</b> (16× faster)
          </div>
        </div>""", unsafe_allow_html=True)




# ════════════════════════════════════════════════════════════════════
# TAB 6 — ALERT CENTER
# ════════════════════════════════════════════════════════════════════
def tab_alerts():
    role     = st.session_state.get("role", "Viewer")
    username = st.session_state.get("username", "User")
    bot_token= st.session_state.get("bot_token", "")
    chat_id  = st.session_state.get("chat_id", "")

    st.markdown('<div class="section-title">🚨 Alert Management Center</div>',
                unsafe_allow_html=True)

    # Alert stats
    alerts_df = db.get_alerts(limit=100)
    total     = len(alerts_df)
    unacked   = int((alerts_df["acknowledged"] == 0).sum()) if not alerts_df.empty else 0
    critical  = int((alerts_df["severity"] == "CRITICAL").sum()) if not alerts_df.empty else 0

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-label">Total Alerts (All Time)</div>
          <div class="kpi-value">{total}</div>
        </div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""
        <div class="kpi-card {'red' if unacked>0 else 'green'}">
          <div class="kpi-label">Unacknowledged</div>
          <div class="kpi-value {'red' if unacked>0 else 'green'}">{unacked}</div>
        </div>""", unsafe_allow_html=True)
    with a3:
        st.markdown(f"""
        <div class="kpi-card {'red' if critical>0 else 'green'}">
          <div class="kpi-label">Critical Alerts</div>
          <div class="kpi-value {'red' if critical>0 else 'green'}">{critical}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Manual alert dispatch
    if has_permission(role, "configure_alerts"):
        with st.expander("📡 Manual Alert Dispatch"):
            col_t, col_s = st.columns([3, 1])
            with col_t:
                alert_title = st.text_input("Alert Title", placeholder="e.g. Scheduled Maintenance")
                alert_msg   = st.text_area("Message", placeholder="Alert details...", height=80)
            with col_s:
                alert_sev   = st.selectbox("Severity", ["INFO","WARNING","CRITICAL","EMERGENCY"])
            if st.button("📡 Dispatch Alert", use_container_width=True):
                if alert_title and alert_msg:
                    result = dispatch_alert(
                        severity=alert_sev,
                        title=sanitize_input(alert_title),
                        message=sanitize_input(alert_msg),
                        username=username, role=role,
                        telegram_token=bot_token, telegram_chat=chat_id,
                        force=True
                    )
                    for ch, res in result.items():
                        st.write(f"**{ch.title()}**: {res}")
                else:
                    st.warning("Please fill in both title and message.")

    # Alert feed
    st.markdown('<div class="section-title">📋 Alert History</div>', unsafe_allow_html=True)

    if alerts_df.empty:
        st.markdown("""
        <div class="glass-panel" style="text-align:center;color:#64748B;padding:2.5rem;">
          <div style="font-size:2rem;">✅</div>
          <div>No alerts on record.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for _, row in alerts_df.head(20).iterrows():
            sev    = str(row.get("severity","INFO")).upper()
            sev_cls= {"CRITICAL":"critical","WARNING":"warning",
                      "EMERGENCY":"critical","INFO":"info"}.get(sev,"info")
            acked  = bool(row.get("acknowledged", 0))
            ack_icon = "✅" if acked else "🔔"
            col_l, col_r = st.columns([5, 1])
            with col_l:
                st.markdown(f"""
                <div class="alert-item {sev_cls}">
                  <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#E2E8F0;">
                      {ack_icon} {row.get('title','—')}
                    </div>
                    <div style="font-size:0.72rem;color:#64748B;margin-top:2px;">
                      {row.get('message','')[:100]}...
                    </div>
                    <div style="font-size:0.68rem;color:#374151;margin-top:4px;">
                      🕐 {row.get('timestamp','—')} · via {row.get('channel','—')}
                    </div>
                  </div>
                  <div style="margin-left:1rem;">{get_severity_badge(sev)}</div>
                </div>""", unsafe_allow_html=True)
            with col_r:
                if not acked and has_permission(role, "acknowledge_alert"):
                    if st.button("Ack", key=f"ack_{row['id']}"):
                        db.acknowledge_alert(int(row["id"]), username)
                        st.rerun()


# ════════════════════════════════════════════════════════════════════
# TAB 7 — AI ASSISTANT
# ════════════════════════════════════════════════════════════════════
def tab_ai_assistant():
    username = st.session_state.get("username", "User")
    role     = st.session_state.get("role", "Viewer")
    anomaly  = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    score    = st.session_state.get("health_score", 97.4)

    st.markdown('<div class="section-title">🤖 Nexus-AI Assistant</div>',
                unsafe_allow_html=True)
    st.caption("Ask anything about the system — anomalies, ESG, alerts, security, operations.")

    # Init chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "bot",
            "content": (
                f"👋 Hello **{username}** ({role})! I'm your **Nexus-AI Assistant**.\n\n"
                "I have deep knowledge of this operational cockpit — anomaly detection, ESG metrics, "
                "security, alerts, sensor thresholds, and operational procedures.\n\n"
                "How can I help you today?"
            ),
            "time": datetime.datetime.now().strftime("%H:%M")
        }]

    system_state = {"username": username, "role": role,
                    "current_anomaly": anomaly, "health_score": score}

    # Render chat
    chat_html = '<div class="chat-container" id="chat-box">'
    for msg in st.session_state.chat_history:
        is_user = msg["role"] == "user"
        side    = "user" if is_user else "bot"
        avatar  = "👤" if is_user else "🔷"
        # Convert markdown bold to html for inline rendering
        content = msg["content"].replace("**", "<b>", 1)
        content = content.replace("**", "</b>", 1) if "<b>" in content else content

        chat_html += f"""
        <div class="chat-msg {side}">
          <div class="chat-avatar {side}">{avatar}</div>
          <div>
            <div class="chat-bubble {side}">{msg['content']}</div>
            <div class="chat-meta">{msg['time']}</div>
          </div>
        </div>"""
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Quick action chips
    st.markdown('<div class="chip-row">', unsafe_allow_html=True)
    chip_cols = st.columns(4)
    quick_actions_display = QUICK_ACTIONS[:8]
    for i, qa in enumerate(quick_actions_display):
        with chip_cols[i % 4]:
            if st.button(f"💬 {qa[:30]}…" if len(qa) > 30 else f"💬 {qa}",
                         key=f"chip_{i}", use_container_width=True):
                st.session_state["pending_chat"] = qa
    st.markdown("</div>", unsafe_allow_html=True)

    # Text input
    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            user_input = st.text_input("Type your question…",
                                       value=st.session_state.pop("pending_chat", ""),
                                       label_visibility="collapsed",
                                       placeholder="e.g. How does anomaly detection work?")
        with col_btn:
            send = st.form_submit_button("Send ➤", use_container_width=True)

        if send and user_input.strip():
            clean_input = sanitize_input(user_input, max_len=512)
            st.session_state.chat_history.append({
                "role": "user",
                "content": clean_input,
                "time": datetime.datetime.now().strftime("%H:%M")
            })
            response = get_ai_response(
                clean_input, system_state, st.session_state.chat_history
            )
            st.session_state.chat_history.append({
                "role": "bot",
                "content": response,
                "time": datetime.datetime.now().strftime("%H:%M")
            })
            # Keep last 40 messages
            if len(st.session_state.chat_history) > 40:
                st.session_state.chat_history = st.session_state.chat_history[-40:]
            st.rerun()

    if st.button("🗑️ Clear Chat History", use_container_width=False):
        st.session_state.chat_history = []
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# TAB 8 — AUDIT & COMPLIANCE
# ════════════════════════════════════════════════════════════════════
def tab_audit():
    role     = st.session_state.get("role", "Viewer")
    username = st.session_state.get("username", "User")

    st.markdown('<div class="section-title">📜 Immutable Audit Ledger</div>',
                unsafe_allow_html=True)
    logs_df = db.get_audit_logs(limit=200)

    if logs_df.empty:
        st.info("No audit records found.")
    else:
        # Summary stats
        total_events  = len(logs_df)
        anomaly_events= int((logs_df["action"] == "TRIGGER_ANOMALY").sum()) \
                        if "action" in logs_df.columns else 0
        login_events  = int((logs_df["action"] == "LOGIN").sum()) \
                        if "action" in logs_df.columns else 0

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f"""
            <div class="kpi-card cyan">
              <div class="kpi-label">Total Log Entries</div>
              <div class="kpi-value">{total_events}</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="kpi-card orange">
              <div class="kpi-label">Anomaly Events</div>
              <div class="kpi-value orange">{anomaly_events}</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="kpi-card green">
              <div class="kpi-label">Login Events</div>
              <div class="kpi-value green">{login_events}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        st.dataframe(logs_df, use_container_width=True, height=380)

        col_exp, col_clr = st.columns([2, 1])
        with col_exp:
            if has_permission(role, "export_data"):
                csv = logs_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Audit CSV", data=csv,
                                   file_name=f"NexusAI_Audit_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                                   mime="text/csv")
        with col_clr:
            if has_permission(role, "clear_audit"):
                if st.button("🗑️ Clear Audit Trail", type="primary"):
                    db.clear_audit_logs()
                    db.log_audit(username, role, "AUDIT_CLEARED", "None",
                                 "Audit trail cleared by admin.")
                    st.rerun()


# ════════════════════════════════════════════════════════════════════
# TAB 8 (new) — DATA INSIGHTS & EDA
# ════════════════════════════════════════════════════════════════════
def tab_data_insights():
    st.markdown('<div class="section-title">📊 Exploratory Data Analysis & Custom ML Model</div>',
                unsafe_allow_html=True)
    st.caption(
        "Understand raw sensor distributions, train the IsolationForest anomaly model, "
        "or upload custom Kaggle datasets / CSV files for automated anomaly auditing."
    )

    analytics = HydroThermalAnalyticsCore()

    # ── Source Selector ──
    data_source = st.radio(
        "Select Data Source",
        ["📡 Live Telemetry Stream", "📁 Upload Custom CSV / Kaggle Dataset"],
        horizontal=True,
        key="data_source_selector"
    )

    if data_source == "📡 Live Telemetry Stream":
        df = analytics.generate_live_production_stream()

        # ── EDA Summary Stats ──
        st.markdown('<div class="section-title" style="margin-top:1rem;">📈 Descriptive Statistics</div>',
                    unsafe_allow_html=True)

        stats_df = analytics.get_eda_summary()
        styled = stats_df[[
            "count", "mean", "std", "min", "25%", "50%", "75%", "max",
            "missing_pct", "completeness"
        ]].rename(columns={
            "count": "Count", "mean": "Mean", "std": "Std Dev",
            "min": "Min", "max": "Max", "missing_pct": "Missing %",
            "completeness": "Complete %"
        })
        st.dataframe(styled, use_container_width=True)

        # ── Distribution Histograms ──
        st.markdown('<div class="section-title" style="margin-top:1rem;">📊 Sensor Value Distributions</div>',
                    unsafe_allow_html=True)

        numeric_cols = ["Electricity_kWh", "Water_Litres", "Pressure_PSI",
                        "Thermal_Temp_C", "Outdoor_Temp_C", "Humidity_Pct"]
        colors_map   = ["#00D4FF", "#FF6B35", "#00FF88", "#FFB800", "#A78BFA", "#F472B6"]

        col_a, col_b = st.columns(2)
        for i, (col_name, col_color) in enumerate(zip(numeric_cols, colors_map)):
            target_col = col_a if i % 2 == 0 else col_b
            with target_col:
                fig = px.histogram(
                    df, x=col_name, nbins=20,
                    color_discrete_sequence=[col_color],
                    title=col_name.replace("_", " "),
                )
                fig.update_layout(**PLOTLY_LAYOUT, height=220)
                fig.update_layout(margin=dict(l=0, r=0, t=32, b=0))
                fig.update_traces(marker_line_color="rgba(0,0,0,0.3)",
                                  marker_line_width=0.5)
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})

        # ── IsolationForest Training Panel ──
        st.markdown('<div class="section-title" style="margin-top:1rem;">🤖 IsolationForest Anomaly Model</div>',
                    unsafe_allow_html=True)

        col_cfg, col_run = st.columns([2, 1])
        with col_cfg:
            contamination = st.slider(
                "Contamination (expected anomaly fraction)",
                min_value=0.01, max_value=0.20, value=0.05, step=0.01,
                format="%.2f",
                help="Set to the expected % of anomalous data points in your stream."
            )
            n_estimators  = st.slider(
                "Number of Trees", min_value=50, max_value=300, value=100, step=50
            )
        with col_run:
            st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
            train_btn = st.button("🚀 Train IsolationForest", use_container_width=True)

        if train_btn or st.session_state.get("if_trained"):
            if "if_metrics" not in st.session_state or train_btn:
                metrics = analytics.train_isolation_forest(
                    contamination=contamination,
                    n_estimators=n_estimators
                )
                st.session_state["if_metrics"] = metrics
                st.session_state["if_trained"] = True
                scored_df = analytics.score_with_isolation_forest(df.copy())
                st.session_state["if_scored_df"] = scored_df

            metrics   = st.session_state.get("if_metrics", {})
            scored_df = st.session_state.get("if_scored_df", df)

            if "error" in metrics:
                st.error(metrics["error"])
            else:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="kpi-card cyan">
                      <div class="kpi-label">Model</div>
                      <div style="font-size:0.9rem;font-weight:700;color:#00D4FF;margin-top:4px;">
                        IsolationForest
                      </div>
                      <div style="font-size:0.7rem;color:#64748B;margin-top:4px;">
                        {metrics.get('n_estimators',100)} trees · {int(metrics.get('contamination',0.05)*100)}% contam.
                      </div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    prec = metrics.get("precision", 0)
                    st.markdown(f"""
                    <div class="kpi-card {'green' if prec>=0.8 else 'yellow'}">
                      <div class="kpi-label">Precision</div>
                      <div class="kpi-value {'green' if prec>=0.8 else 'yellow'}">{prec:.3f}</div>
                      <div style="font-size:0.7rem;color:#64748B;margin-top:2px;">TP / (TP+FP)</div>
                    </div>""", unsafe_allow_html=True)
                with m3:
                    rec = metrics.get("recall", 0)
                    st.markdown(f"""
                    <div class="kpi-card {'green' if rec>=0.8 else 'yellow'}">
                      <div class="kpi-label">Recall</div>
                      <div class="kpi-value {'green' if rec>=0.8 else 'yellow'}">{rec:.3f}</div>
                      <div style="font-size:0.7rem;color:#64748B;margin-top:2px;">TP / (TP+FN)</div>
                    </div>""", unsafe_allow_html=True)
                with m4:
                    f1 = metrics.get("f1_score", 0)
                    st.markdown(f"""
                    <div class="kpi-card {'green' if f1>=0.8 else 'yellow'}">
                      <div class="kpi-label">F1 Score</div>
                      <div class="kpi-value {'green' if f1>=0.8 else 'yellow'}">{f1:.3f}</div>
                      <div style="font-size:0.7rem;color:#64748B;margin-top:2px;">Harmonic mean</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

                if "IF_Score" in scored_df.columns:
                    st.markdown('<div class="section-title">🔴 Anomaly Risk Score per Time Step</div>',
                                unsafe_allow_html=True)
                    fig_if = go.Figure()
                    fig_if.add_trace(go.Bar(
                        x=scored_df["Timestamp"],
                        y=scored_df["IF_Score"],
                        marker_color=[
                            "#FF2D55" if a else "#00D4FF"
                            for a in scored_df["IF_Anomaly"]
                        ],
                        name="Anomaly Risk Score",
                    ))
                    fig_if.add_hline(y=60, line_dash="dot", line_color="#FFB800",
                                     annotation_text="Warning threshold (60)",
                                     annotation_position="right")
                    fig_if.update_layout(**PLOTLY_LAYOUT, height=280)
                    st.plotly_chart(fig_if, use_container_width=True,
                                    config={"displayModeBar": False})

                    n_flagged = int(scored_df["IF_Anomaly"].sum())
                    if n_flagged > 0:
                        st.warning(
                            f"🔴 **{n_flagged} data points** flagged as anomalous by the "
                            f"IsolationForest model ({contamination*100:.0f}% contamination rate). "
                            f"Check timestamps: "
                            f"{', '.join([str(t)[:16] for t in scored_df.loc[scored_df['IF_Anomaly'],'Timestamp'].tolist()[:5]])}"
                        )

        # ── Data Dictionary ──
        st.markdown('<div class="section-title" style="margin-top:1.5rem;">📖 Data Dictionary</div>',
                    unsafe_allow_html=True)
        dict_df = analytics.get_data_dictionary()
        st.dataframe(dict_df, use_container_width=True, hide_index=True)

    else:
        # ── CUSTOM CSV / KAGGLE DATASET UPLOAD VAULT ──
        st.markdown('<div class="section-title" style="margin-top:1rem;">📂 Custom Dataset Ingestion & Testing Vault</div>',
                    unsafe_allow_html=True)
        st.info("💡 Drop any industrial sensor CSV/Excel dataset (e.g. from Kaggle) to compute EDA statistics, visualize distributions, and train the IsolationForest model on custom numeric features.")

        col_up, col_sample = st.columns([3, 1])
        with col_up:
            uploaded_file = st.file_uploader(
                "Upload Dataset (.csv, .xlsx, .xls)",
                type=["csv", "xlsx", "xls"],
                key="custom_dataset_file"
            )
        with col_sample:
            st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
            load_sample = st.button("📊 Load Sample Kaggle Dataset", use_container_width=True)

        custom_df = None
        source_name = ""

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    custom_df = pd.read_csv(uploaded_file)
                else:
                    custom_df = pd.read_excel(uploaded_file)
                source_name = uploaded_file.name
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
        elif load_sample:
            custom_df = analytics.generate_sample_kaggle_dataset()
            source_name = "Sample_Kaggle_Turbine_Sensors.csv"
            st.session_state["active_custom_df"] = custom_df
            st.session_state["active_source_name"] = source_name
        elif "active_custom_df" in st.session_state:
            custom_df = st.session_state["active_custom_df"]
            source_name = st.session_state.get("active_source_name", "Uploaded_Dataset.csv")

        if custom_df is not None:
            st.session_state["active_custom_df"] = custom_df
            st.session_state["active_source_name"] = source_name

            st.success(f"✅ Loaded dataset **{source_name}** with **{len(custom_df):,} rows** and **{len(custom_df.columns)} columns**.")

            # Summary KPI row
            c1, c2, c3, c4 = st.columns(4)
            num_cols_list = custom_df.select_dtypes(include=[np.number]).columns.tolist()
            with c1:
                st.metric("Total Rows", f"{len(custom_df):,}")
            with c2:
                st.metric("Total Features", len(custom_df.columns))
            with c3:
                st.metric("Numeric Features", len(num_cols_list))
            with c4:
                missing_total = int(custom_df.isnull().sum().sum())
                st.metric("Missing Values", f"{missing_total:,}")

            # Preview raw data
            with st.expander("👁️ Preview Raw Dataset (First 50 Rows)", expanded=False):
                st.dataframe(custom_df.head(50), use_container_width=True)

            # Feature selection for modeling
            st.markdown('<div class="section-title" style="margin-top:1rem;">⚙️ Select Feature Columns for Modeling</div>',
                        unsafe_allow_html=True)
            selected_features = st.multiselect(
                "Choose numeric sensor variables to include in IsolationForest training:",
                options=num_cols_list,
                default=num_cols_list[:6] if len(num_cols_list) >= 6 else num_cols_list
            )

            if selected_features:
                # ── Dynamic EDA ──
                st.markdown('<div class="section-title" style="margin-top:1rem;">📈 Custom Dataset Statistics</div>',
                            unsafe_allow_html=True)
                stats_custom = custom_df[selected_features].describe().T
                stats_custom["missing_pct"] = (custom_df[selected_features].isnull().sum() / len(custom_df) * 100).round(2)
                st.dataframe(stats_custom, use_container_width=True)

                # Histograms
                st.markdown('<div class="section-title" style="margin-top:1rem;">📊 Feature Distributions</div>',
                            unsafe_allow_html=True)
                colors = ["#00D4FF", "#FF6B35", "#00FF88", "#FFB800", "#A78BFA", "#F472B6"]
                col_c1, col_c2 = st.columns(2)
                for i, feat in enumerate(selected_features[:6]):
                    col_target = col_c1 if i % 2 == 0 else col_c2
                    with col_target:
                        fig_hist = px.histogram(
                            custom_df, x=feat, nbins=20,
                            color_discrete_sequence=[colors[i % len(colors)]],
                            title=f"Distribution of {feat}"
                        )
                        fig_hist.update_layout(**PLOTLY_LAYOUT, height=220)
                        fig_hist.update_layout(margin=dict(l=0, r=0, t=32, b=0))
                        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

                # ── Custom IsolationForest Training Panel ──
                st.markdown('<div class="section-title" style="margin-top:1rem;">🤖 Train IsolationForest on Custom Features</div>',
                            unsafe_allow_html=True)

                cf_c1, cf_c2, cf_c3 = st.columns([2, 2, 1])
                with cf_c1:
                    custom_contam = st.slider(
                        "Contamination Rate", min_value=0.01, max_value=0.20, value=0.05, step=0.01,
                        key="custom_contam_slider"
                    )
                with cf_c2:
                    custom_trees = st.slider(
                        "Tree Estimators", min_value=50, max_value=300, value=100, step=50,
                        key="custom_trees_slider"
                    )
                with cf_c3:
                    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
                    run_custom_if = st.button("⚡ Run IsolationForest", use_container_width=True)

                if run_custom_if or st.session_state.get("custom_if_executed"):
                    if run_custom_if or "custom_scored_df" not in st.session_state:
                        scored_custom, custom_metrics = analytics.train_custom_isolation_forest(
                            df=custom_df,
                            feature_cols=selected_features,
                            contamination=custom_contam,
                            n_estimators=custom_trees
                        )
                        st.session_state["custom_scored_df"] = scored_custom
                        st.session_state["custom_metrics"] = custom_metrics
                        st.session_state["custom_if_executed"] = True

                    scored_custom  = st.session_state.get("custom_scored_df", custom_df)
                    custom_metrics = st.session_state.get("custom_metrics", {})

                    if "error" in custom_metrics:
                        st.error(custom_metrics["error"])
                    else:
                        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.metric("Total Analyzed Rows", custom_metrics.get("training_rows", 0))
                        with m2:
                            st.metric("Anomalies Identified", custom_metrics.get("anomalies_found", 0))
                        with m3:
                            st.metric("Anomaly Ratio", f"{custom_metrics.get('anomaly_pct', 0)}%")
                        with m4:
                            st.metric("Max Risk Score", f"{custom_metrics.get('max_risk_score', 0)}%")

                        # Anomaly Risk Score chart
                        st.markdown('<div class="section-title" style="margin-top:1rem;">🔴 Anomaly Score Timeline / Sequence</div>',
                                    unsafe_allow_html=True)
                        x_axis_col = custom_df.columns[0] if "Timestamp" not in custom_df.columns else "Timestamp"
                        fig_custom_bar = go.Figure()
                        fig_custom_bar.add_trace(go.Bar(
                            x=scored_custom[x_axis_col] if x_axis_col in scored_custom.columns else list(range(len(scored_custom))),
                            y=scored_custom["IF_Score"],
                            marker_color=[
                                "#FF2D55" if flag else "#00D4FF"
                                for flag in scored_custom["IF_Anomaly"]
                            ],
                            name="Anomaly Risk Score"
                        ))
                        fig_custom_bar.update_layout(**PLOTLY_LAYOUT, height=280)
                        st.plotly_chart(fig_custom_bar, use_container_width=True, config={"displayModeBar": False})

                        # Show Scored Data Table & Download Option
                        st.markdown('<div class="section-title">📥 Download Scored Dataset</div>', unsafe_allow_html=True)
                        st.dataframe(scored_custom, use_container_width=True)

                        csv_bytes = scored_custom.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Download Scored CSV (with IF_Anomaly & IF_Score)",
                            data=csv_bytes,
                            file_name=f"scored_{source_name}",
                            mime="text/csv",
                            use_container_width=True
                        )
            else:
                st.warning("⚠️ Please select at least one numeric feature column to analyze.")


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════
def main():
    # Auth gate
    if not st.session_state.get("authenticated"):
        # Validate existing session token
        token = st.session_state.get("session_token")
        if token:
            user_info = db.validate_session(token)
            if user_info:
                st.session_state["authenticated"] = True
                st.session_state["username"]      = user_info["username"]
                st.session_state["role"]          = user_info["role"]
            else:
                show_login()
                return
        else:
            show_login()
            return

    # Session defaults
    st.session_state.setdefault("current_anomaly", "Nominal / Normal Operations")
    st.session_state.setdefault("health_score",    97.4)

    show_header()
    show_sidebar()

    # ── 9 Navigation Tabs ──────────────────────────────────────────
    TAB_LABELS = [
        "🏠 Command Center",
        "📈 Telemetry & Analytics",
        "🌐 Digital Twin",
        "🤖 RCA Engine",
        "🌱 ESG Dashboard",
        "🚨 Alert Center",
        "💬 AI Assistant",
        "📊 Data Insights",
        "📜 Audit & Compliance",
    ]

    tabs = st.tabs(TAB_LABELS)

    with tabs[0]: tab_command_center()
    with tabs[1]: tab_telemetry()
    with tabs[2]: tab_digital_twin()
    with tabs[3]: tab_rca()
    with tabs[4]: tab_esg()
    with tabs[5]: tab_alerts()
    with tabs[6]: tab_ai_assistant()
    with tabs[7]: tab_data_insights()
    with tabs[8]: tab_audit()


if __name__ == "__main__":
    main()