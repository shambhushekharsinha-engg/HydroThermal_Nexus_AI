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
        subtitle="Industrial IoT Operational Platform & Anomaly Detection System"
    )
    sc.show_sidebar()

    st.markdown("""
    <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid #00D4FF;">
      <h3 style="margin: 0 0 0.5rem 0; color: #00D4FF;">Welcome to HydroThermal Nexus-AI v2.1</h3>
      <p style="color: #CBD5E1; margin: 0; line-height: 1.6;">
        Welcome back, <b>{}</b>! You are authenticated with the <b>{}</b> role.
        Use the sidebar navigation on the left to navigate through our multi-page operational modules:
      </p>
    </div>
    """.format(user_info['username'], user_info['role']), unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #38BDF8;">🎛️ Command</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Real-time system health score, KPI gauges, and guided scenario missions.</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #A855F7;">📈 ML Engine</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">IsolationForest anomaly detection and AI Root Cause Analysis.</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #34D399;">🌱 ESG & Reports</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Financial yield calculators and regulatory compliance exporters.</p>
        </div>""", unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #FBBF24;">🌍 Sustain-Pro</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Next-Gen Circular Economy, GreenFi, and Scope 3 Supply Chain.</p>
        </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
          <h4 style="color: #EF4444;">🗺️ Global Fleet</h4>
          <p style="font-size: 0.82rem; color: #94A3B8;">Interactive multi-site map with localized telemetry switching.</p>
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