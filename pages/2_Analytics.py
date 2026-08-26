# -*- coding: utf-8 -*-
"""
pages/2_Analytics.py — Telemetry, ML Anomaly Detection & RCA Engine
Provides real-time telemetry analysis, custom Kaggle dataset IsolationForest ML training, and AI Root Cause Analysis.
"""

import os
import datetime
import logging
from io import BytesIO
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import shared_components as sc
from backend import database as db
from backend.security import has_permission, get_severity_badge
from ml_engine import HydroThermalAnalyticsCore
from rca_engine import RCAEngine
from alert_manager import dispatch_alert, build_anomaly_alert

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageAnalytics")

st.set_page_config(page_title="Analytics & ML Engine — HydroThermal Nexus", page_icon="📈", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="📈 Telemetry, ML & RCA Engine", subtitle="IsolationForest Anomaly Detection & AI Root Cause Diagnostics")
sc.show_sidebar()


def render_telemetry_section() -> None:
    """Render anomaly injection and telemetry charts."""
    st.markdown('<div class="section-title">⚙️ Telemetry & Anomaly Injection Console</div>', unsafe_allow_html=True)

    if has_permission(role, "trigger_anomaly"):
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            anomaly_sel = st.selectbox("Select Anomaly Scenario", [
                "Nominal / Normal Operations",
                "Pipe Rupture / Flow Drop",
                "HVAC Overheat / Thermal Spike",
            ], key="telemetry_anomaly_select")
        with col_btn:
            st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Trigger Scenario", key="trigger_scenario_analytics", use_container_width=True):
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
                    telegram_token=st.session_state.get("bot_token", ""),
                    telegram_chat=st.session_state.get("chat_id", ""),
                    force=True,
                )
                if anomaly_sel == "Nominal / Normal Operations":
                    st.success("✅ System reset to Nominal Operations.")
                else:
                    st.error(f"🚨 Anomaly '{anomaly_sel}' activated — Alert dispatched!")
                st.rerun()
    else:
        st.info("🔒 Viewer role cannot inject anomaly scenarios.")

    st.markdown("---")
    st.markdown('<div class="section-title">🔄 Live Sensor Stream Metrics</div>', unsafe_allow_html=True)

    live_toggle = st.toggle("Enable Live Sensor Streaming", key="analytics_live_toggle")
    np.random.seed(int(datetime.datetime.now().second) if live_toggle else 42)

    pressure = round(42.5 + np.random.uniform(-0.5, 0.5), 2) if live_toggle else 42.5
    temp = round(68.4 + np.random.uniform(-0.3, 0.3), 2) if live_toggle else 68.4
    energy = round(128.0 + np.random.uniform(-1.0, 1.0), 2) if live_toggle else 128.0
    flow = round(120.0 + np.random.uniform(-2.0, 2.0), 2) if live_toggle else 120.0
    humidity = round(65.0 + np.random.uniform(-1.0, 1.0), 2) if live_toggle else 65.0
    outdoor_t = round(32.0 + np.random.uniform(-0.5, 0.5), 2) if live_toggle else 32.0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Pressure", f"{pressure} PSI", "+1.2%")
    m2.metric("Thermal", f"{temp}°C", "-0.8°C")
    m3.metric("Energy", f"{energy} kW", "+3.1%")
    m4.metric("Flow Rate", f"{flow} L/m", "+0.4%")
    m5.metric("Humidity", f"{humidity}%", "-0.5%")
    m6.metric("Outdoor Temp", f"{outdoor_t}°C", "+0.2°C")

    st.markdown('<div class="section-title" style="margin-top:1rem;">📊 Telemetry Visualization</div>', unsafe_allow_html=True)

    analytics = HydroThermalAnalyticsCore()
    df = analytics.generate_live_production_stream()
    if live_toggle:
        db.save_telemetry(energy, flow * 25, outdoor_t, humidity, pressure, temp)

    chart_type = st.radio("Chart View", ["Multi-Sensor", "Electricity", "Water Flow"], horizontal=True, key="analytics_chart_type")

    if chart_type == "Multi-Sensor":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Electricity (kWh)", "Water (Litres)"), vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Electricity_kWh"], name="Electricity", mode="lines",
                                 line=dict(color="#00D4FF", width=2), fill="tozeroy", fillcolor="rgba(0,212,255,0.07)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Water_Litres"], name="Water", mode="lines",
                                 line=dict(color="#FF6B35", width=2), fill="tozeroy", fillcolor="rgba(255,107,53,0.07)"), row=2, col=1)
        fig.update_layout(**sc.PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Electricity":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Electricity_kWh"], name="kWh", mode="lines+markers",
                                 line=dict(color="#00D4FF", width=2), marker=dict(size=4, color="#00D4FF")))
        fig.add_hline(y=2200, line_dash="dot", line_color="#FFB800", annotation_text="Baseline", annotation_position="right")
        fig.update_layout(**sc.PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.area(df, x="Timestamp", y="Water_Litres", color_discrete_sequence=["#FF6B35"])
        fig.update_layout(**sc.PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔬 Sensor Correlation Heatmap"):
        corr = df[["Electricity_kWh", "Water_Litres", "Outdoor_Temp_C", "Humidity_Pct"]].corr()
        fig_heat = px.imshow(corr, text_auto=".2f", color_continuous_scale=[[0, "#FF2D55"], [0.5, "#111827"], [1, "#00D4FF"]], aspect="auto")
        fig_heat.update_layout(**sc.PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_heat, use_container_width=True)


def render_ml_custom_training() -> None:
    """Render Custom Dataset IsolationForest Trainer & Data Insights."""
    st.markdown("---")
    st.markdown('<div class="section-title">🧠 IsolationForest ML Engine & Dataset Analyzer</div>', unsafe_allow_html=True)
    st.caption("Upload custom Kaggle CSVs or synthetic telemetry to train isolation forest models, score anomalies, and export results.")

    engine = HydroThermalAnalyticsCore()

    data_source = st.radio("Select Data Source", ["Synthetic Industrial Stream", "Upload Custom CSV File"], horizontal=True, key="analytics_source_radio")

    if data_source == "Synthetic Industrial Stream":
        raw_df = engine.generate_sample_kaggle_dataset()
        source_name = "synthetic_industrial_telemetry.csv"
    else:
        uploaded_file = st.file_uploader("Upload Telemetry CSV", type=["csv"], key="analytics_csv_uploader")
        if uploaded_file is not None:
            raw_df = pd.read_csv(uploaded_file)
            source_name = uploaded_file.name
        else:
            st.info("ℹ️ Upload a CSV file above or switch to Synthetic Stream.")
            return

    st.markdown("##### 🔍 Dataset Inspection")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", len(raw_df))
    c2.metric("Total Columns", len(raw_df.columns))
    numeric_cols: List[str] = raw_df.select_dtypes(include=[np.number]).columns.tolist()
    c3.metric("Numeric Features", len(numeric_cols))

    st.dataframe(raw_df.head(5), use_container_width=True)

    if numeric_cols:
        col_f, col_c = st.columns([3, 1])
        with col_f:
            selected_features = st.multiselect("Select Feature Columns for Anomaly Scoring", numeric_cols, default=numeric_cols[:min(4, len(numeric_cols))])
        with col_c:
            contamination = st.slider("Contamination Rate", 0.01, 0.20, 0.05, 0.01)

        if selected_features and st.button("⚡ Run IsolationForest Scoring", key="run_if_button", use_container_width=True):
            with st.spinner("Training IsolationForest model & scoring data points..."):
                scored_df, metrics = engine.train_custom_isolation_forest(
                    df=raw_df, feature_cols=selected_features, contamination=contamination
                )

            st.success(f"✅ Scoring Complete! Detected {metrics.get('anomalies_found', 0)} anomalies ({metrics.get('anomaly_percentage', 0.0):.1f}% of total).")

            m_col1, m_col2 = st.columns(2)
            with m_col1:
                fig_scatter = px.scatter(
                    scored_df, x=selected_features[0], y=selected_features[1] if len(selected_features) > 1 else selected_features[0],
                    color=scored_df["IF_Anomaly"].map({1: "Normal", -1: "Anomaly"}),
                    color_discrete_map={"Normal": "#00D4FF", "Anomaly": "#FF2D55"},
                    title="Anomaly Distribution Scatter", hover_data=["IF_Score"]
                )
                fig_scatter.update_layout(**sc.PLOTLY_LAYOUT, height=280)
                st.plotly_chart(fig_scatter, use_container_width=True)

            with m_col2:
                fig_hist = px.histogram(scored_df, x="IF_Score", color=scored_df["IF_Anomaly"].map({1: "Normal", -1: "Anomaly"}),
                                        color_discrete_map={"Normal": "#00D4FF", "Anomaly": "#FF2D55"},
                                        title="Isolation Forest Score Distribution")
                fig_hist.update_layout(**sc.PLOTLY_LAYOUT, height=280)
                st.plotly_chart(fig_hist, use_container_width=True)

            csv_bytes = scored_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Scored CSV (with IF_Anomaly & IF_Score)",
                data=csv_bytes,
                file_name=f"scored_{source_name}",
                mime="text/csv",
                use_container_width=True
            )

            # ── Feature Importance / Explainability ────────────────────
            st.markdown("---")
            st.markdown('<div class="section-title">🔍 Anomaly Explainability — Feature Contribution Analysis</div>', unsafe_allow_html=True)
            st.caption("Which sensors contributed most to the IsolationForest anomaly score? Higher % = greater contribution to anomalous readings.")

            fi_df = engine.get_feature_importance(scored_df)
            if not fi_df.empty:
                fi_col1, fi_col2 = st.columns([2, 1])
                with fi_col1:
                    colors_fi = ["#FF2D55" if i < 2 else "#FFB800" if i < 4 else "#00D4FF"
                                 for i in range(len(fi_df))]
                    fig_fi = go.Figure(go.Bar(
                        x=fi_df["Importance"],
                        y=fi_df["Feature"],
                        orientation="h",
                        marker_color=colors_fi,
                        text=[f"{v:.1f}%" for v in fi_df["Importance"]],
                        textposition="inside",
                    ))
                    fig_fi.update_layout(
                        **sc.PLOTLY_LAYOUT,
                        height=max(250, len(fi_df) * 38),
                        title="Feature Importance (% contribution to anomaly score)",
                        xaxis_title="Importance (%)",
                        yaxis_title="",
                        showlegend=False,
                    )
                    st.plotly_chart(fig_fi, use_container_width=True)

                with fi_col2:
                    st.markdown("#### 📋 Feature Details")
                    display_df = fi_df[["Feature", "Importance", "Direction", "Category"]].copy()
                    display_df["Importance"] = display_df["Importance"].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    st.caption("**Direction**: ↑ High = anomalies show higher values · ↓ Low = anomalies show lower values")
            else:
                st.info("ℹ️ Feature importance not available — train a custom model above first.")


def render_rca_section() -> None:
    """Render Root Cause Analysis Engine diagnostics."""
    st.markdown("---")
    st.markdown('<div class="section-title">🤖 AI-Driven Root Cause Analysis (RCA)</div>', unsafe_allow_html=True)
    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    health  = float(st.session_state.get("health_score", 97.4))

    rca = RCAEngine()
    analysis = rca.analyze_anomaly(anomaly, health_score=health)

    # Status banner
    sev = analysis.get("severity", "INFO")
    if sev == "CRITICAL":
        st.error(f"🚨 {analysis['primary_vector']}")
    elif sev == "WARNING":
        st.warning(f"⚠️ {analysis['primary_vector']}")
    else:
        st.success(f"✅ {analysis['primary_vector']}")

    # Confidence + MTTR metrics row
    conf = analysis.get("confidence_pct", 0)
    mttr = analysis.get("mttr", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Diagnostic Confidence", f"{conf:.1f}%")
    m2.metric("Fault Category", analysis.get("fault_category", "—"))
    m3.metric("MTTR Estimate", f"{mttr.get('mttr_hours', 0):.1f} hrs")
    m4.metric("Est. Downtime Cost", f"${mttr.get('estimated_downtime_cost_usd', 0):,.0f} USD")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="glass-panel">
          <div class="section-title">🔍 Diagnostic Findings</div>
          <p><b>Root Cause:</b> {analysis['root_cause']}</p>
          <p><b>Impact:</b> {analysis['impact']}</p>
          <p><b>Category:</b> {analysis.get('fault_category_desc', '—')}</p>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="glass-panel">
          <div class="section-title">🛠️ Recommended Action</div>
          <p>{analysis['recommendation']}</p>
        </div>""", unsafe_allow_html=True)

    # Fault tree
    fault_tree = analysis.get("fault_tree", [])
    if fault_tree and anomaly != "Nominal / Normal Operations":
        st.markdown("#### 🌳 Fault Cascade Tree")
        for node in fault_tree:
            color = {"Primary": "#FF2D55", "Secondary": "#FFB800", "Tertiary": "#00D4FF"}.get(node["level"], "#64748B")
            st.markdown(
                f'<div style="border-left:3px solid {color};padding:6px 12px;margin:4px 0;">'
                f'<span style="color:{color};font-weight:600;">[{node["level"]}]</span> '
                f'<b>{node["node"]}</b> — <span style="color:#94A3B8;">{node["cause"]}</span></div>',
                unsafe_allow_html=True
            )

    # PDF Report
    if has_permission(role, "download_reports"):
        st.markdown("---")
        if st.button("📄 Download Full PDF Incident Report", key="btn_download_pdf", use_container_width=True, type="primary"):
            from report_generator import EnterpriseReportEngine
            from backend.database import get_esg_history
            import numpy as np
            esg_df = get_esg_history(days=30)
            co2  = float(esg_df["co2_saved_kg"].sum())    if not esg_df.empty and "co2_saved_kg" in esg_df.columns else 420.0
            water = float(esg_df["water_saved_l"].sum())   if not esg_df.empty and "water_saved_l" in esg_df.columns else 18500.0
            energy = float(esg_df["energy_saved_kwh"].sum()) if not esg_df.empty and "energy_saved_kwh" in esg_df.columns else 3200.0
            score  = float(esg_df["esg_score"].mean())     if not esg_df.empty and "esg_score" in esg_df.columns else 88.5
            pdf_bytes = EnterpriseReportEngine.compile_pdf_report(
                facility_name="HydroThermal Nexus Plant Node-01",
                water_saved=f"{water:,.0f} Litres",
                energy_saved=f"{energy:,.1f} kWh",
                network_status="ONLINE",
                anomaly_type=anomaly,
                triggered_by=username,
                role=role,
                co2_saved_kg=co2,
                water_saved_l=water,
                energy_saved_kwh=energy,
                esg_score=score,
                rca_result=analysis,
            )
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"NexusAI_Incident_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )




def render_pdm_section() -> None:
    """Render Predictive Maintenance (PdM) module."""
    st.markdown("---")
    st.markdown('<div class="section-title">🔧 AI Predictive Maintenance (PdM) & RUL Forecasting</div>', unsafe_allow_html=True)
    st.caption("Forecast Remaining Useful Life (RUL) and estimate financial risk of unscheduled downtime using non-linear degradation curves.")
    
    from predictive_maintenance import PredictiveMaintenanceEngine
    
    c1, c2, c3 = st.columns(3)
    with c1:
        vib = st.slider("Current Vibration (mm/s)", 0.0, 15.0, 3.2, 0.1)
    with c2:
        temp = st.slider("Bearing Temp (°C)", 30.0, 150.0, 65.0, 1.0)
    with c3:
        pressure = st.slider("Header Pressure (PSI)", 20.0, 80.0, 42.5, 0.5)
        
    pdm = PredictiveMaintenanceEngine.calculate_rul(vib, temp, pressure)
    risk = PredictiveMaintenanceEngine.estimate_downtime_financial_risk(pdm["rul_hours"])
    
    col_metrics, col_risk = st.columns([1.5, 1])
    
    with col_metrics:
        st.markdown(f"#### Degradation Status: **{pdm['status']}**")
        st.progress(pdm['rul_percentage'] / 100.0, text=f"Remaining Useful Life (RUL): {pdm['rul_percentage']}% ({pdm['rul_hours']} hours)")
        st.info(f"**Action Code:** `{pdm['action_code']}` — {pdm['urgency']}")
        
    with col_risk:
        st.markdown("#### Financial Risk Analysis")
        st.metric("Probability of Failure (30 days)", f"{risk['failure_probability_30d']}%")
        st.metric("Net Savings by Preventative Maintenance", f"${risk['net_savings_preventative_usd']:,.2f}", "Cost Avoided")


def main() -> None:
    render_telemetry_section()
    render_ml_custom_training()
    render_rca_section()
    render_pdm_section()


if __name__ == "__main__":
    main()
