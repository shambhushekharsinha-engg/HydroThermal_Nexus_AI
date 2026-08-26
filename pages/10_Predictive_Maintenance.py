# -*- coding: utf-8 -*-
"""
pages/10_Predictive_Maintenance.py — AI Predictive Maintenance & RUL Dashboard
Exposes the PredictiveMaintenanceEngine as a full interactive UI:
  - Remaining Useful Life (RUL) gauges for 3 components
  - Interactive sensor sliders → live RUL recalculation
  - 30-day degradation trend chart
  - Financial downtime risk panel
  - Schedule Maintenance button with audit logging
"""

import datetime
import logging
import math
from typing import Dict, Any

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

import shared_components as sc
from backend import database as db
from backend.security import has_permission
from predictive_maintenance import PredictiveMaintenanceEngine

logger = logging.getLogger("HydroThermalNexus.PagePredMaintenance")

st.set_page_config(
    page_title="Predictive Maintenance — HydroThermal Nexus",
    page_icon="🔧",
    layout="wide"
)

user_info = sc.require_auth()
username = user_info["username"]
role = user_info["role"]

sc.show_header(
    title="🔧 AI Predictive Maintenance & RUL Forecasting",
    subtitle="Remaining Useful Life Engine · Degradation Trends · Financial Risk Analysis"
)
sc.show_sidebar()

# ── Component Definitions ─────────────────────────────────────────────
COMPONENTS = {
    "Hydro Pump A": {
        "icon": "💧",
        "operating_hours": 14200.0,
        "design_lifespan": 40000.0,
        "default_vib": 2.8,
        "default_temp": 62.0,
        "default_psi": 42.0,
        "color": "#00D4FF",
    },
    "Heat Exchanger B": {
        "icon": "🌡️",
        "operating_hours": 22000.0,
        "design_lifespan": 40000.0,
        "default_vib": 1.9,
        "default_temp": 74.0,
        "default_psi": 44.0,
        "color": "#FF6B35",
    },
    "Compressor C": {
        "icon": "⚙️",
        "operating_hours": 31500.0,
        "design_lifespan": 40000.0,
        "default_vib": 3.7,
        "default_temp": 79.0,
        "default_psi": 39.0,
        "color": "#A855F7",
    },
}


def render_rul_gauge(comp_name: str, rul_result: Dict[str, Any], color: str) -> go.Figure:
    """Render a health index gauge for a component."""
    hi = rul_result["health_index"]
    gauge_color = "#00FF88" if hi > 80 else "#FFB800" if hi > 50 else "#FF2D55"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=hi,
        delta={"reference": 80, "valueformat": ".1f",
               "increasing": {"color": "#00FF88"},
               "decreasing": {"color": "#FF2D55"}},
        number={"font": {"color": gauge_color, "size": 28}, "suffix": "%"},
        title={"text": f"{comp_name}<br><span style='font-size:0.7em;color:#64748B;'>"
                       f"RUL: {rul_result['rul_hours']:,.0f} hrs</span>",
               "font": {"color": "#E2E8F0", "size": 13}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#374151", "tickfont": {"color": "#64748B"}},
            "bar": {"color": gauge_color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "steps": [
                {"range": [0, 50],  "color": "rgba(255,45,85,0.10)"},
                {"range": [50, 80], "color": "rgba(255,184,0,0.10)"},
                {"range": [80, 100],"color": "rgba(0,255,136,0.10)"},
            ],
            "threshold": {"line": {"color": "#FF2D55", "width": 2}, "thickness": 0.75, "value": 50},
        }
    ))
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=240, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def render_degradation_trend(comp_name: str, comp_cfg: Dict, rul_result: Dict) -> go.Figure:
    """Simulates a 30-day wear curve for the component."""
    days = list(range(-30, 1))
    base_hi = rul_result["health_index"]
    deg_factor = rul_result["degradation_factor"]

    # Simulate exponential degradation back in time
    health_history = [
        max(0.0, base_hi + (30 - abs(d)) * deg_factor * 0.35 + np.random.uniform(-0.8, 0.8))
        for d in days
    ]
    health_history[-1] = base_hi  # pin current day to actual value

    df = pd.DataFrame({"Day": [f"D{d}" for d in days], "Health Index": health_history})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Day"], y=df["Health Index"],
        mode="lines+markers",
        line=dict(color=comp_cfg["color"], width=2.5),
        fill="tozeroy",
        fillcolor=sc.hex_to_rgba(comp_cfg["color"], 0.07),
        marker=dict(size=4),
        name="Health Index (%)",
    ))
    # Add threshold bands
    fig.add_hline(y=80, line_dash="dot", line_color="#00FF88", annotation_text="Healthy (80%)", annotation_font_color="#00FF88")
    fig.add_hline(y=50, line_dash="dot", line_color="#FFB800", annotation_text="Critical (50%)", annotation_font_color="#FFB800")
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=220, title=f"{comp_name} — 30-Day Health Trend")
    fig.update_xaxes(showticklabels=False)
    return fig


def render_financial_risk(rul_result: Dict, financial: Dict, comp_name: str) -> None:
    """Renders the financial downtime risk panel."""
    st.markdown(f'<div class="section-title">💰 Financial Risk: {comp_name}</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    prob = financial["failure_probability_30d"]
    unplanned = financial["unplanned_outage_cost_usd"]
    planned = financial["planned_servicing_cost_usd"]
    net_save = financial["net_savings_preventative_usd"]

    prob_color = "red" if prob > 50 else "yellow" if prob > 20 else "green"
    f1.markdown(f"""
    <div class="kpi-card {prob_color}">
      <div class="kpi-icon">⚠️</div>
      <div class="kpi-label">Failure Prob (30d)</div>
      <div class="kpi-value {prob_color}">{prob:.1f}%</div>
    </div>""", unsafe_allow_html=True)

    f2.markdown(f"""
    <div class="kpi-card red">
      <div class="kpi-icon">🔥</div>
      <div class="kpi-label">Unplanned Outage Cost</div>
      <div class="kpi-value red" style="font-size:1.2rem;">${unplanned:,.0f}</div>
    </div>""", unsafe_allow_html=True)

    f3.markdown(f"""
    <div class="kpi-card green">
      <div class="kpi-icon">🔧</div>
      <div class="kpi-label">Planned Service Cost</div>
      <div class="kpi-value green" style="font-size:1.2rem;">${planned:,.0f}</div>
    </div>""", unsafe_allow_html=True)

    f4.markdown(f"""
    <div class="kpi-card green">
      <div class="kpi-icon">💡</div>
      <div class="kpi-label">Net Savings (PdM)</div>
      <div class="kpi-value green" style="font-size:1.2rem;">${net_save:,.0f}</div>
    </div>""", unsafe_allow_html=True)


def main() -> None:
    st.markdown('<div class="section-title">🤖 Live Component Health Assessment</div>', unsafe_allow_html=True)
    st.caption("Adjust sensor readings to recalculate RUL in real-time. Degradation model: ISO 10816 vibration + thermal wear + accelerated exponential aging.")

    # ── Per-component tabs ────────────────────────────────────────────
    tabs = st.tabs([f"{v['icon']} {k}" for k, v in COMPONENTS.items()])

    for tab, (comp_name, comp_cfg) in zip(tabs, COMPONENTS.items()):
        with tab:
            st.markdown(f"#### {comp_cfg['icon']} {comp_name} — Sensor Input Panel")
            c1, c2, c3 = st.columns(3)
            with c1:
                vib = st.slider(
                    "Vibration (mm/s)",
                    min_value=0.1, max_value=10.0,
                    value=comp_cfg["default_vib"],
                    step=0.1, key=f"vib_{comp_name}"
                )
            with c2:
                temp = st.slider(
                    "Bearing Temp (°C)",
                    min_value=30.0, max_value=110.0,
                    value=comp_cfg["default_temp"],
                    step=0.5, key=f"temp_{comp_name}"
                )
            with c3:
                psi = st.slider(
                    "Hydraulic Pressure (PSI)",
                    min_value=20.0, max_value=70.0,
                    value=comp_cfg["default_psi"],
                    step=0.5, key=f"psi_{comp_name}"
                )

            # Compute RUL
            rul_result = PredictiveMaintenanceEngine.calculate_rul(
                vibration_mm_s=vib,
                bearing_temp_c=temp,
                pressure_psi=psi,
                operating_hours_logged=comp_cfg["operating_hours"],
                design_lifespan_hours=comp_cfg["design_lifespan"],
            )
            financial = PredictiveMaintenanceEngine.estimate_downtime_financial_risk(
                rul_hours=rul_result["rul_hours"]
            )

            # ── Status Banner ─────────────────────────────────────────
            status = rul_result["status"]
            if status == "HEALTHY":
                st.success(f"✅ **{comp_name}** — {status} | {rul_result['urgency']}")
            elif status == "DEGRADING":
                st.warning(f"⚠️ **{comp_name}** — {status} | {rul_result['urgency']}")
            else:
                st.error(f"🚨 **{comp_name}** — {status} | {rul_result['urgency']}")

            # ── Gauges + Trend ─────────────────────────────────────────
            col_gauge, col_trend = st.columns([1, 1.8])
            with col_gauge:
                st.plotly_chart(
                    render_rul_gauge(comp_name, rul_result, comp_cfg["color"]),
                    use_container_width=True, config={"displayModeBar": False}
                )
                # RUL summary metrics
                m1, m2 = st.columns(2)
                m1.metric("RUL (hours)", f"{rul_result['rul_hours']:,.0f}")
                m2.metric("RUL (%)", f"{rul_result['rul_percentage']:.1f}%")
                st.metric("Degradation Factor", f"{rul_result['degradation_factor']:.3f}")
                st.metric("Wear Multiplier", f"{rul_result['accelerated_wear_multiplier']:.2f}×")

            with col_trend:
                st.plotly_chart(
                    render_degradation_trend(comp_name, comp_cfg, rul_result),
                    use_container_width=True, config={"displayModeBar": False}
                )

            st.markdown("---")
            render_financial_risk(rul_result, financial, comp_name)

            # ── Schedule Maintenance Button ────────────────────────────
            st.markdown("---")
            if has_permission(role, "trigger_anomaly"):
                col_btn, col_note = st.columns([1, 3])
                with col_btn:
                    if st.button(
                        f"📅 Schedule Maintenance — {comp_name}",
                        key=f"schedule_{comp_name}",
                        use_container_width=True,
                        type="primary"
                    ):
                        action_detail = (
                            f"Maintenance scheduled for {comp_name}. "
                            f"Health: {rul_result['health_index']}%, "
                            f"RUL: {rul_result['rul_hours']} hrs, "
                            f"Action Code: {rul_result['action_code']}"
                        )
                        db.log_audit(username, role, "MAINTENANCE_SCHEDULED", comp_name, action_detail)
                        st.success(f"✅ Maintenance ticket created for **{comp_name}** — logged to audit ledger.")
                        logger.info("Maintenance scheduled for %s by %s", comp_name, username)
                with col_note:
                    st.info(
                        f"**Action Code:** `{rul_result['action_code']}`  "
                        f"**Urgency:** {rul_result['urgency']}"
                    )
            else:
                st.info("🔒 Field Engineer or Admin role required to schedule maintenance.")

    # ── Fleet Overview Table ──────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Fleet Health Summary Dashboard</div>', unsafe_allow_html=True)

    fleet_rows = []
    for comp_name, comp_cfg in COMPONENTS.items():
        r = PredictiveMaintenanceEngine.calculate_rul(
            vibration_mm_s=st.session_state.get(f"vib_{comp_name}", comp_cfg["default_vib"]),
            bearing_temp_c=st.session_state.get(f"temp_{comp_name}", comp_cfg["default_temp"]),
            pressure_psi=st.session_state.get(f"psi_{comp_name}", comp_cfg["default_psi"]),
            operating_hours_logged=comp_cfg["operating_hours"],
            design_lifespan_hours=comp_cfg["design_lifespan"],
        )
        fin = PredictiveMaintenanceEngine.estimate_downtime_financial_risk(r["rul_hours"])
        fleet_rows.append({
            "Component": f"{comp_cfg['icon']} {comp_name}",
            "Health Index": f"{r['health_index']:.1f}%",
            "Status": r["status"],
            "RUL (hours)": f"{r['rul_hours']:,.0f}",
            "Urgency": r["urgency"].split(" - ")[0],
            "Failure Risk (30d)": f"{fin['failure_probability_30d']:.1f}%",
            "Net Savings (PdM)": f"${fin['net_savings_preventative_usd']:,.0f}",
        })

    df_fleet = pd.DataFrame(fleet_rows)
    st.dataframe(df_fleet, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
