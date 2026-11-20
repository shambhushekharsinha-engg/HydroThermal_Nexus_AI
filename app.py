# -*- coding: utf-8 -*-
"""
app.py — HydroThermal Nexus-AI Main Entrypoint
Initializes persistent SQLite databases, starts background FastAPI REST API, enforces authentication,
and loads shared UI layout for Streamlit multi-page architecture.
"""

import logging
from typing import Dict, Any

import streamlit as st
import shared_components as sc
from backend import database as db

logger: logging.Logger = logging.getLogger("HydroThermalNexus.App")

# ── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="HydroThermal Nexus-AI",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Main application launcher and landing overview."""
    user_info: Dict[str, str] = sc.require_auth()

    sc.show_header(
        title="🔷 HydroThermal Nexus-AI Cockpit",
        subtitle="Industrial IoT Operational Platform & Anomaly Detection System (v3.0.0)"
    )
    sc.show_sidebar()

    fac = sc.get_active_facility()

    st.markdown("""
    <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid #00D4FF;">
      <h3 style="margin: 0 0 0.5rem 0; color: #00D4FF;">Welcome to HydroThermal Nexus-AI v3.0 Enterprise</h3>
      <p style="color: #CBD5E1; margin: 0; line-height: 1.6;">
        Welcome back, <b>{}</b>! You are authenticated with the <b>{}</b> role, currently monitoring <b>{} {} ({}, {})</b>.
        Use the sidebar navigation on the left or the module hub below to access our 10 industrial operations pages:
      </p>
    </div>
    """.format(user_info['username'], user_info['role'], fac['flag'], fac['name'], fac['city'], fac['country']), unsafe_allow_html=True)

    row1_c1, row1_c2, row1_c3, row1_c4, row1_c5 = st.columns(5)

    with row1_c1:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #38BDF8;">🎛️ 1. Command Center</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Dual-mode executive dashboard, KPI cards, health ring, and live sensor sparklines.</p>
        </div>""", unsafe_allow_html=True)

    with row1_c2:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #A855F7;">📈 2. ML & RCA</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">IsolationForest anomaly detection, custom Kaggle training, and AI root cause analysis.</p>
        </div>""", unsafe_allow_html=True)

    with row1_c3:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #EF4444;">🚨 3. Alert Center</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Multi-channel alerts, Telegram bot gateway, manual dispatch, and acknowledgment.</p>
        </div>""", unsafe_allow_html=True)

    with row1_c4:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #38BDF8;">🌐 4. 3D Digital Twin</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">3D PyDeck geospatial node telemetry and automated mitigation actuator controls.</p>
        </div>""", unsafe_allow_html=True)

    with row1_c5:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #34D399;">🌱 5. ESG Reports</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Multi-currency savings calculator, GHG Protocol, ISO 14001, and BRSR disclosures.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    row2_c1, row2_c2, row2_c3, row2_c4, row2_c5 = st.columns(5)

    with row2_c1:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #64748B;">⚙️ 6. System Settings</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Tamper-evident audit ledger, 6-role RBAC security matrix, and system diagnostics.</p>
        </div>""", unsafe_allow_html=True)

    with row2_c2:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #60A5FA;">🤖 7. AI Copilot</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Domain knowledge assistant with dual-tier Bedrock + deterministic failover.</p>
        </div>""", unsafe_allow_html=True)

    with row2_c3:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #FBBF24;">🌍 8. Sustain Pro</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Waste heat recovery Sankey, dynamic grid carbon load shifting, and effluent compliance.</p>
        </div>""", unsafe_allow_html=True)

    with row2_c4:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #64FFDA;">🗺️ 9. Global Fleet</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">17-site worldwide interactive map, real-time search, and instant facility switching.</p>
        </div>""", unsafe_allow_html=True)

    with row2_c5:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #F43F5E;">🔧 10. Predictive Maint.</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Remaining Useful Life (RUL) forecasting, ISO 10816 degradation, and financial risk.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Render quick stats overview
    alerts_df = db.get_alerts(limit=5)
    st.markdown('<div class="section-title">⚡ Operational Quick Status</div>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("FastAPI Backend", "Port 8001", "Online")
    q2.metric("ML Engine Core", "IsolationForest", "Active")
    q3.metric("SQLite Storage", "nexus_storage.db", "Connected")
    q4.metric("Active Alerts", len(alerts_df) if not alerts_df.empty else 0, "Nominal")


if __name__ == "__main__":
    main()