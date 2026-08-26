# -*- coding: utf-8 -*-
"""
pages/1_Dashboard.py — HydroThermal Nexus-AI Command Center & Diagnostic Sandbox
Renders key performance indicators, live sensor sparklines, health gauge ring, alerts, and guided diagnostic scenarios.
"""

import datetime
import logging
import time
from typing import Dict, Any

import streamlit as st
import plotly.graph_objects as go
import numpy as np

import shared_components as sc
from backend import database as db
from backend.security import get_severity_badge, get_role_badge
from alert_manager import dispatch_alert, build_anomaly_alert

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageDashboard")

# Page configuration
st.set_page_config(page_title="Command Center — HydroThermal Nexus", page_icon="🎛️", layout="wide")

# Auth enforcement guard
user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="🎛️ Command Center & Diagnostic Cockpit", subtitle="Live Telemetry, System Health & Scenario Missions")
sc.show_sidebar()


def render_kpi_cards(score: float) -> None:
    """Render top KPI metrics row."""
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
        score_class = 'green' if score >= 90 else 'yellow' if score >= 70 else 'red'
        score_status = '✅ Excellent' if score >= 90 else '⚠️ Degraded' if score >= 70 else '🚨 Critical'
        st.markdown(f"""
        <div class="kpi-card {score_class}">
          <div class="kpi-icon">🛡️</div>
          <div class="kpi-label">System Health Score</div>
          <div class="kpi-value" style="color:{score_color};">{score}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">/ 100</div>
          <div class="kpi-delta {'up' if score>=90 else 'down'}">
            {score_status}
          </div>
        </div>""", unsafe_allow_html=True)


def render_health_ring_and_alerts(score: float) -> None:
    """Render health gauge ring and recent alerts table."""
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
                "axis": {"range": [0, 100], "tickcolor": "#374151", "tickfont": {"color": "#64748B"}},
                "bar": {"color": "#00D4FF", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,0.1)",
                "steps": [
                    {"range": [0, 60], "color": "rgba(255,45,85,0.12)"},
                    {"range": [60, 80], "color": "rgba(255,184,0,0.12)"},
                    {"range": [80, 100], "color": "rgba(0,255,136,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#FF2D55", "width": 2},
                    "thickness": 0.75, "value": 70
                }
            }
        ))
        fig_gauge.update_layout(**sc.PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

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
                sev_cls = {"CRITICAL": "critical", "WARNING": "warning", "EMERGENCY": "critical", "INFO": "info"}.get(sev, "info")
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


def render_sparklines() -> None:
    """Render real-time mini sparklines."""
    st.markdown('<div class="section-title" style="margin-top:1rem;">📈 Live Sensor Sparklines</div>', unsafe_allow_html=True)
    np.random.seed(int(datetime.datetime.now().timestamp()) % 9999)
    t_axis = [datetime.datetime.now() - datetime.timedelta(minutes=30*i) for i in range(20, 0, -1)]

    s1, s2, s3 = st.columns(3)
    for col, label, base, unit, color in [
        (s1, "Hydraulic Pressure", 42.5, "PSI", "#00D4FF"),
        (s2, "Thermal Temp", 68.4, "°C", "#FF6B35"),
        (s3, "Energy Load", 128.0, "kW", "#00FF88"),
    ]:
        with col:
            vals = base + np.cumsum(np.random.randn(20) * 0.3)
            fig = go.Figure(go.Scatter(
                x=t_axis, y=vals, mode="lines",
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=sc.hex_to_rgba(color, 0.08),
            ))
            fig.update_layout(**sc.PLOTLY_LAYOUT, height=140)
            fig.update_xaxes(showticklabels=False)
            fig.update_layout(
                margin=dict(l=0, r=0, t=24, b=0),
                title=dict(text=f"{label} ({unit})", font=dict(size=11, color="#64748B"))
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_guided_sandbox() -> None:
    """Render interactive onboarding sandbox & emergency scenario trigger."""
    st.markdown("---")
    st.markdown('<div class="section-title">🔰 Guided Emergency Missions & RBAC Sandbox</div>', unsafe_allow_html=True)

    current_mission = st.session_state.get("active_mission", "None")

    col_mission, col_roles = st.columns([1.6, 1])

    with col_mission:
        st.markdown("##### 💥 Trigger Diagnostic Missions")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            if st.button("💧 Mission: Pipe Rupture", use_container_width=True):
                st.session_state["active_mission"] = "Pipe Rupture"
                st.session_state["current_anomaly"] = "Pipe Rupture / Flow Drop"
                st.session_state["health_score"] = 42.1
                template = build_anomaly_alert("Pipe Rupture / Flow Drop", username)
                dispatch_alert(
                    severity=template["severity"],
                    title=template["title"],
                    message=template["message"],
                    anomaly_type="Pipe Rupture / Flow Drop",
                    username=username,
                    role=role,
                    telegram_token=st.session_state.get("bot_token", ""),
                    telegram_chat=st.session_state.get("chat_id", ""),
                    force=True,
                )
                logger.info("Triggered mission: Pipe Rupture by user %s", username)
                st.rerun()

        with m2:
            if st.button("🌡️ Mission: HVAC Heatwave", use_container_width=True):
                st.session_state["active_mission"] = "HVAC Heatwave"
                st.session_state["current_anomaly"] = "HVAC Overheat / Thermal Spike"
                st.session_state["health_score"] = 63.8
                template = build_anomaly_alert("HVAC Overheat / Thermal Spike", username)
                dispatch_alert(
                    severity=template["severity"],
                    title=template["title"],
                    message=template["message"],
                    anomaly_type="HVAC Overheat / Thermal Spike",
                    username=username,
                    role=role,
                    telegram_token=st.session_state.get("bot_token", ""),
                    telegram_chat=st.session_state.get("chat_id", ""),
                    force=True,
                )
                logger.info("Triggered mission: HVAC Heatwave by user %s", username)
                st.rerun()

        with m3:
            if st.button("⚡ Mission: Power Surge", use_container_width=True):
                st.session_state["active_mission"] = "Power Surge"
                st.session_state["current_anomaly"] = "Power Surge / Grid Instability"
                st.session_state["health_score"] = 55.0
                template = build_anomaly_alert("Power Surge / Grid Instability", username)
                dispatch_alert(
                    severity=template["severity"],
                    title=template["title"],
                    message=template["message"],
                    anomaly_type="Power Surge / Grid Instability",
                    username=username,
                    role=role,
                    telegram_token=st.session_state.get("bot_token", ""),
                    telegram_chat=st.session_state.get("chat_id", ""),
                    force=True,
                )
                logger.info("Triggered mission: Power Surge by user %s", username)
                st.rerun()

        with m4:
            if st.button("🔄 Mission: Reset System", use_container_width=True):
                st.session_state["active_mission"] = "None"
                st.session_state["current_anomaly"] = "Nominal / Normal Operations"
                st.session_state["health_score"] = 97.4
                logger.info("Reset system mission state to nominal by user %s", username)
                st.rerun()

        if current_mission == "Pipe Rupture":
            st.warning("🚨 MISSION ACTIVE: Pipe Rupture / Leak Response. Inspect Telemetry and RCA Engine pages for details.")
        elif current_mission == "HVAC Heatwave":
            st.warning("⚠️ MISSION ACTIVE: HVAC Thermal Spike Response. Auxiliary chillers engaged.")
        elif current_mission == "Power Surge":
            st.error("⚡ MISSION ACTIVE: Power Surge / Grid Instability. Load shedding active — UPS battery engaged.")
        else:
            st.info("💡 Nominal Operations Active. Select a mission above to run guided diagnostics.")

    with col_roles:
        st.markdown("##### 🔐 Role Switcher")
        st.markdown(f"Active Role: {get_role_badge(role)}", unsafe_allow_html=True)
        if st.button("👤 Switch to Viewer", use_container_width=True):
            st.session_state["role"] = "Viewer"
            db.log_audit(username, "Viewer", "ROLE_SWITCH", "None", "Switched to Viewer role.")
            st.rerun()
        if st.button("🔧 Switch to Operator", use_container_width=True):
            st.session_state["role"] = "Operator"
            db.log_audit(username, "Operator", "ROLE_SWITCH", "None", "Switched to Operator role.")
            st.rerun()
        if st.button("👑 Switch to Admin", use_container_width=True):
            st.session_state["role"] = "Admin"
            db.log_audit(username, "Admin", "ROLE_SWITCH", "None", "Switched to Admin role.")
            st.rerun()


def main() -> None:
    score: float = float(st.session_state.get("health_score", 97.4))

    # ── Live Refresh Toggle ───────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown("#### ⚡ Live Sensor Feed")
        live_refresh = st.toggle("🔄 Enable 2s Auto-Refresh", value=False, key="live_refresh_toggle")
        if live_refresh:
            st.caption("🟢 Live mode active — sparklines updating every 2s")
        else:
            st.caption("⚪ Live mode off — manual refresh")

    render_kpi_cards(score)
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    render_health_ring_and_alerts(score)
    render_sparklines()
    render_guided_sandbox()

    # Auto-refresh after all components rendered
    if live_refresh:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()
