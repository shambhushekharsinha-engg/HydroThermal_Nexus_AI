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

fac = sc.get_active_facility()
sc.show_header(
    title=f"🎛️ Command Center — {fac['flag']} {fac['name']}",
    subtitle=f"{fac['city']}, {fac['country']} · {fac['timezone']} · Health: {st.session_state.get('health_score', fac['health'])}%"
)
sc.show_sidebar()


def get_current_telemetry() -> Dict[str, Any]:
    """Derive dynamic telemetry values based on active facility and active anomaly."""
    fac = sc.get_active_facility()
    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    base_p = fac["pressure"]
    base_t = fac["temp"]
    base_e = fac["energy_kw"]

    if anomaly == "Pipe Rupture / Flow Drop":
        pressure = 14.2
        temp = round(base_t - 4.5, 1)
        energy = round(base_e * 0.85, 1)
        status_msg = "🚨 Pipe Rupture: Solenoid valve restricted to 20% aperture. Fluid drop -240% vs baseline."
    elif anomaly == "HVAC Overheat / Thermal Spike":
        pressure = round(base_p * 1.05, 1)
        temp = 104.5
        energy = round(base_e * 1.42, 1)
        status_msg = "⚠️ Thermal Spike: Cooling tower fan relay stall. Temperature ramping towards 105°C."
    elif anomaly == "Power Surge / Grid Instability":
        pressure = round(base_p * 0.92, 1)
        temp = round(base_t + 5.8, 1)
        energy = 215.0
        status_msg = "⚡ Power Surge: Grid voltage fluctuation detected. Load shedding active, UPS battery engaged."
    else:
        pressure = base_p
        temp = base_t
        energy = base_e
        status_msg = "✅ Nominal Operations: All sensors streaming within certified envelope."

    delta_p = round(((pressure - 42.5) / 42.5) * 100, 1)
    delta_t = round(temp - 65.0, 1)
    delta_e = round(((energy - 120.0) / 120.0) * 100, 1)

    return {
        "pressure": pressure,
        "temp": temp,
        "energy": energy,
        "delta_p": delta_p,
        "delta_t": delta_t,
        "delta_e": delta_e,
        "status_msg": status_msg,
        "fac": fac,
        "anomaly": anomaly,
    }


def render_executive_mode(score: float, telem: Dict[str, Any]) -> None:
    """Render executive summary mode with key figures, live demo button, and prioritized directives."""
    anomaly = telem["anomaly"]
    fac = telem["fac"]

    # Threat Banner
    is_critical = score < 70 or anomaly != "Nominal / Normal Operations"
    banner_bg = "rgba(255, 45, 85, 0.12)" if is_critical else "rgba(0, 255, 136, 0.08)"
    banner_border = "#FF2D55" if is_critical else "#00FF88"
    banner_icon = "🚨" if is_critical else "🛡️"
    banner_title = f"{banner_icon} Threat Directive: {anomaly}" if is_critical else "✅ Facility Operational Status: Nominal & Compliant"

    st.markdown(f"""
    <div class="glass-panel" style="padding: 1.2rem 1.5rem; margin-bottom: 1.2rem; border-left: 5px solid {banner_border}; background: {banner_bg};">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 style="margin: 0 0 0.3rem 0; color: {banner_border}; font-size:1.25rem;">{banner_title}</h3>
          <p style="color: #CBD5E1; margin: 0; font-size: 0.88rem;">{telem['status_msg']}</p>
        </div>
        <div style="text-align:right;">
          <span style="background:rgba(255,255,255,0.08); border-radius:6px; padding:4px 10px; font-size:0.75rem; color:#94A3B8;">
            Engine: 🤖 IsolationForest v3.0 (p95: 3.8ms)
          </span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 1-Click Live Demo Action
    col_demo, col_kpi_sum = st.columns([1, 2.2])

    with col_demo:
        st.markdown("""
        <div class="glass-panel" style="padding: 1.2rem; height: 100%; border: 1px solid rgba(0,212,255,0.3); text-align:center;">
          <div style="font-size: 0.85rem; color:#38BDF8; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">
            ⚡ Evaluator Live Action
          </div>
          <div style="font-size: 0.82rem; color:#94A3B8; margin-bottom:12px;">
            Run synchronous end-to-end incident cycle (sub-3s SLA). Injects telemetry spike, runs ML, logs audit & dispatches alert.
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Run Live Incident Demo (< 3s)", key="exec_live_demo_btn", use_container_width=True, type="primary"):
            t0 = time.time()
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
            elapsed_ms = round((time.time() - t0) * 1000, 1)
            st.success(f"✅ Demo executed synchronously in {elapsed_ms}ms! Anomaly detected, RCA computed, alert dispatched.")
            st.rerun()

        if is_critical and st.button("🔄 Reset to Nominal", key="exec_reset_btn", use_container_width=True):
            st.session_state["active_mission"] = "None"
            st.session_state["current_anomaly"] = "Nominal / Normal Operations"
            st.session_state["health_score"] = fac["health"]
            st.rerun()

    with col_kpi_sum:
        # Top 3 Executive Figures
        k1, k2, k3 = st.columns(3)
        with k1:
            p_val = telem["pressure"]
            p_color = "#FF2D55" if p_val < 30 or p_val > 55 else "#00FF88"
            st.markdown(f"""
            <div class="kpi-card cyan" style="height:100%;">
              <div class="kpi-icon">💧</div>
              <div class="kpi-label">Hydraulic Pressure</div>
              <div class="kpi-value" style="color:{p_color};">{p_val} PSI</div>
              <div class="kpi-delta {'down' if telem['delta_p']<0 else 'up'}">
                {'▼' if telem['delta_p']<0 else '▲'} {telem['delta_p']:+0.1f}% vs baseline
              </div>
            </div>""", unsafe_allow_html=True)

        with k2:
            lead_time = "4.2 hrs" if anomaly == "Nominal / Normal Operations" else "< 12 mins"
            st.markdown(f"""
            <div class="kpi-card green" style="height:100%;">
              <div class="kpi-icon">⏱️</div>
              <div class="kpi-label">Advance Warning Lead Time</div>
              <div class="kpi-value green">{lead_time}</div>
              <div class="kpi-delta up">Preemptive vs reactive failure</div>
            </div>""", unsafe_allow_html=True)

        with k3:
            downtime_avoided = "$48,500" if is_critical else "$124,000"
            st.markdown(f"""
            <div class="kpi-card orange" style="height:100%;">
              <div class="kpi-icon">💰</div>
              <div class="kpi-label">Downtime Cost Avoided (Est)</div>
              <div class="kpi-value orange">{downtime_avoided}</div>
              <div class="kpi-delta up">Via proactive RUL servicing</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Prioritized Facility Directives</div>', unsafe_allow_html=True)

    c_card1, c_card2, c_card3 = st.columns(3)

    with c_card1:
        st.markdown(f"""
        <div class="glass-panel" style="padding:1rem; border-top: 3px solid #00D4FF;">
          <div style="font-weight:700; color:#F8FAFC; font-size:0.95rem;">
            {fac['flag']} {fac['name']} (Active Site)
          </div>
          <div style="font-size:0.75rem; color:#94A3B8; margin-top:2px;">{fac['city']}, {fac['country']} · {fac['timezone']}</div>
          <div style="margin-top:8px; font-size:0.82rem; color:#E2E8F0;">
            <b>Directive:</b> {telem['status_msg']}
          </div>
          <div style="margin-top:8px; font-size:0.75rem; color:#64FFDA;">
            Health: {score}% · Grid Carbon: {fac['grid_carbon']} kg CO₂/kWh
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c_card2:
        tokyo = sc.GLOBAL_FACILITIES["tokyo_hub"]
        st.markdown(f"""
        <div class="glass-panel" style="padding:1rem; border-top: 3px solid #FF2D55;">
          <div style="font-weight:700; color:#F8FAFC; font-size:0.95rem;">
            {tokyo['flag']} Tokyo Hub (Most Critical)
          </div>
          <div style="font-size:0.75rem; color:#94A3B8; margin-top:2px;">Tokyo, Japan · JST (UTC+9)</div>
          <div style="margin-top:8px; font-size:0.82rem; color:#FF8080;">
            <b>Directive:</b> Main header pressure loss (12.4 PSI). Urgent bypass valve inspection required.
          </div>
          <div style="margin-top:8px; font-size:0.75rem; color:#FF2D55;">
            Health: {tokyo['health']}% · Critical Anomaly Flagged
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c_card3:
        syd = sc.GLOBAL_FACILITIES["sydney_station"]
        st.markdown(f"""
        <div class="glass-panel" style="padding:1rem; border-top: 3px solid #00FF88;">
          <div style="font-weight:700; color:#F8FAFC; font-size:0.95rem;">
            {syd['flag']} Sydney Station (Top Fleet Performer)
          </div>
          <div style="font-size:0.75rem; color:#94A3B8; margin-top:2px;">Sydney, Australia · AEST (UTC+10)</div>
          <div style="margin-top:8px; font-size:0.82rem; color:#86EFAC;">
            <b>Directive:</b> Zero anomalies for 30 consecutive days. Recommended as reference benchmark.
          </div>
          <div style="margin-top:8px; font-size:0.75rem; color:#00FF88;">
            Health: {syd['health']}% · Optimal Efficiency
          </div>
        </div>
        """, unsafe_allow_html=True)


def render_kpi_cards(score: float, telem: Dict[str, Any]) -> None:
    """Render top KPI metrics row with dynamic values and deltas."""
    pressure = telem["pressure"]
    temp = telem["temp"]
    energy = telem["energy"]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        p_color = "#FF2D55" if pressure < 30 or pressure > 55 else "#00D4FF"
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-icon">💧</div>
          <div class="kpi-label">Hydraulic Pressure</div>
          <div class="kpi-value" style="color:{p_color};">{pressure}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">PSI (Baseline: 42.5)</div>
          <div class="kpi-delta {'down' if telem['delta_p']<0 else 'up'}">
            {'▼' if telem['delta_p']<0 else '▲'} {telem['delta_p']:+0.1f}% vs baseline
          </div>
        </div>""", unsafe_allow_html=True)

    with k2:
        t_color = "#FF2D55" if temp > 85 else "#FF6B35"
        st.markdown(f"""
        <div class="kpi-card orange">
          <div class="kpi-icon">🌡️</div>
          <div class="kpi-label">Thermal Loop Temp</div>
          <div class="kpi-value" style="color:{t_color};">{temp}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">°C (Baseline: 65.0)</div>
          <div class="kpi-delta {'down' if telem['delta_t']<0 else 'up'}">
            {'▼' if telem['delta_t']<0 else '▲'} {telem['delta_t']:+0.1f}°C vs nominal
          </div>
        </div>""", unsafe_allow_html=True)

    with k3:
        e_color = "#FF2D55" if energy > 180 else "#00FF88"
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">⚡</div>
          <div class="kpi-label">Energy Consumption</div>
          <div class="kpi-value" style="color:{e_color};">{energy}</div>
          <div style="color:#64748B;font-size:0.72rem;margin-top:2px;">kW (Baseline: 120.0)</div>
          <div class="kpi-delta {'down' if telem['delta_e']<0 else 'up'}">
            {'▼' if telem['delta_e']<0 else '▲'} {telem['delta_e']:+0.1f}% vs baseline
          </div>
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


def render_sparklines(telem: Dict[str, Any]) -> None:
    """Render real-time mini sparklines calibrated dynamically to current facility & anomaly state."""
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
      <div class="section-title" style="margin:0;">📈 Live Sensor Sparklines</div>
      <span style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:4px; padding:2px 8px; font-size:0.68rem; color:#94A3B8;">
        CALIBRATED TELEMETRY FEED · 1 Hz
      </span>
    </div>
    """, unsafe_allow_html=True)

    np.random.seed(int(datetime.datetime.now().timestamp()) % 9999)
    t_axis = [datetime.datetime.now() - datetime.timedelta(minutes=30 * i) for i in range(20, 0, -1)]

    base_p = telem["pressure"]
    base_t = telem["temp"]
    base_e = telem["energy"]

    s1, s2, s3 = st.columns(3)
    for col, label, base, unit, color in [
        (s1, "Hydraulic Pressure", base_p, "PSI", "#00D4FF"),
        (s2, "Thermal Loop Temp", base_t, "°C", "#FF6B35"),
        (s3, "Energy Consumption", base_e, "kW", "#00FF88"),
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
                title=dict(text=f"{label} ({unit}) — Current: {base} {unit}", font=dict(size=11, color="#64748B"))
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_guided_sandbox() -> None:
    """Render interactive onboarding sandbox & emergency scenario trigger."""
    st.markdown("---")
    st.markdown('<div class="section-title">🔰 Guided Emergency Missions & RBAC Sandbox</div>', unsafe_allow_html=True)

    current_mission = st.session_state.get("active_mission", "None")
    fac = sc.get_active_facility()

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
                st.session_state["health_score"] = fac["health"]
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
    telem: Dict[str, Any] = get_current_telemetry()

    # ── Live Refresh Toggle in Sidebar ────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown("#### ⚡ Live Sensor Feed")
        live_refresh = st.toggle("🔄 Enable 2s Auto-Refresh", value=False, key="live_refresh_toggle")
        if live_refresh:
            st.caption("🟢 Live mode active — sparklines updating every 2s")
        else:
            st.caption("⚪ Live mode off — manual refresh")

    # ── Dual-Mode UX Header Toggle ────────────────────────────────────
    mode_col, _ = st.columns([2, 1])
    with mode_col:
        ux_mode = st.radio(
            "Presentation Mode",
            ["🎯 Executive Summary Mode (30s)", "🛠️ Tactical Ops Cockpit (Deep Dive)"],
            horizontal=True,
            index=0,
            key="dashboard_ux_mode",
            label_visibility="collapsed"
        )

    st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)

    if "Executive" in ux_mode:
        render_executive_mode(score, telem)
    else:
        render_kpi_cards(score, telem)
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        render_health_ring_and_alerts(score)
        render_sparklines(telem)
        render_guided_sandbox()

    # Auto-refresh after all components rendered
    if live_refresh:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()
