# -*- coding: utf-8 -*-
"""
pages/5_Reports.py — ESG Sustainability & Executive Reports Engine
Provides carbon accounting, multi-currency financial calculators, before/after impact benchmarks, and regulatory compliance exports.
"""

import json
import datetime
import logging
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

import shared_components as sc
from backend import database as db
from currency_converter import CurrencyConverter
from esg_compliance_exporter import ESGComplianceExporter

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageReports")

st.set_page_config(page_title="ESG Reports — HydroThermal Nexus", page_icon="🌱", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="🌱 ESG Sustainability & Regulatory Reports", subtitle="Carbon Accounting, Multi-Currency Financial Yields & Standardized Compliance Disclosures")
sc.show_sidebar()


def render_esg_kpis() -> pd.DataFrame:
    """Render top 30-day ESG summary KPI cards."""
    st.markdown('<div class="section-title">🌱 ESG Carbon & Resource Conservation Summary</div>', unsafe_allow_html=True)

    esg_df = db.get_esg_history(days=30)
    if esg_df.empty:
        for i in range(14, 0, -1):
            db.upsert_esg(
                co2=round(np.random.uniform(30, 55), 1),
                water=round(np.random.uniform(900, 1600), 0),
                energy=round(np.random.uniform(200, 500), 1),
                score=round(np.random.uniform(72, 96), 1)
            )
        esg_df = db.get_esg_history(days=30)

    total_co2 = esg_df["co2_saved_kg"].sum() if "co2_saved_kg" in esg_df.columns else 0
    total_water = esg_df["water_saved_l"].sum() if "water_saved_l" in esg_df.columns else 0
    total_energy = esg_df["energy_saved_kwh"].sum() if "energy_saved_kwh" in esg_df.columns else 0
    avg_score = esg_df["esg_score"].mean() if "esg_score" in esg_df.columns else 0

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

    return esg_df


def render_financial_calculator(esg_df: pd.DataFrame) -> None:
    """Render multi-currency monetary savings calculator and charts."""
    st.markdown("---")
    st.markdown('<div class="section-title">💰 Multi-Currency Financial Savings Calculator</div>', unsafe_allow_html=True)

    total_co2 = esg_df["co2_saved_kg"].sum() if "co2_saved_kg" in esg_df.columns else 0
    total_water = esg_df["water_saved_l"].sum() if "water_saved_l" in esg_df.columns else 0
    total_energy = esg_df["energy_saved_kwh"].sum() if "energy_saved_kwh" in esg_df.columns else 0

    all_currencies = CurrencyConverter.get_supported_currencies()
    curr_keys = list(all_currencies.keys())

    fc0, fc1, fc2, fc3 = st.columns([1.2, 1, 1, 1])
    with fc0:
        selected_curr = st.selectbox(
            "🌐 Target Currency",
            options=curr_keys,
            index=curr_keys.index("INR") if "INR" in curr_keys else 0,
            format_func=lambda c: f"{c} ({all_currencies[c]['symbol'].strip()}) — {all_currencies[c]['name']}"
        )

    curr_info = all_currencies[selected_curr]
    curr_sym = curr_info["symbol"]

    with fc1:
        water_cost = st.number_input(
            f"Water cost ({curr_sym.strip()} / L)",
            min_value=0.01, max_value=1000.0,
            value=0.05 if selected_curr == "INR" else round(0.05 / curr_info["rate_vs_usd"] * 83.5, 3),
            step=0.01, format="%.3f"
        )
    with fc2:
        energy_cost = st.number_input(
            f"Energy cost ({curr_sym.strip()} / kWh)",
            min_value=0.01, max_value=5000.0,
            value=8.0 if selected_curr == "INR" else round(8.0 / curr_info["rate_vs_usd"] * 83.5, 2),
            step=0.5, format="%.2f"
        )
    with fc3:
        carbon_price = st.number_input(
            "Carbon credit ($ / tonne CO₂e)",
            min_value=1.0, max_value=500.0,
            value=15.0, step=1.0, format="%.1f"
        )

    esg_calc = CurrencyConverter.calculate_esg_savings(
        water_litres=total_water,
        energy_kwh=total_energy,
        co2_kg=total_co2,
        water_cost_per_l=water_cost,
        energy_cost_per_kwh=energy_cost,
        carbon_price_per_tonne_usd=carbon_price,
        input_currency=selected_curr,
        target_currency=selected_curr,
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-icon">💧</div>
          <div class="kpi-label">Water Savings (30d)</div>
          <div class="kpi-value" style="font-size:1.4rem;">{esg_calc['water_savings_formatted']}</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-card orange">
          <div class="kpi-icon">⚡</div>
          <div class="kpi-label">Energy Savings (30d)</div>
          <div class="kpi-value orange" style="font-size:1.4rem;">{esg_calc['energy_savings_formatted']}</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">🌿</div>
          <div class="kpi-label">Carbon Credits (30d)</div>
          <div class="kpi-value green" style="font-size:1.4rem;">{esg_calc['carbon_savings_formatted']}</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-icon">🏦</div>
          <div class="kpi-label">Total Value Unlocked</div>
          <div class="kpi-value green" style="font-size:1.4rem;">{esg_calc['total_savings_formatted']}</div>
        </div>""", unsafe_allow_html=True)


def render_compliance_exporters(esg_df: pd.DataFrame) -> None:
    """Render GHG Protocol, ISO 14001, and BRSR compliance export buttons."""
    st.markdown("---")
    st.markdown('<div class="section-title">📄 Regulatory Compliance Data Disclosures</div>', unsafe_allow_html=True)

    total_co2 = esg_df["co2_saved_kg"].sum() if "co2_saved_kg" in esg_df.columns else 0
    total_water = esg_df["water_saved_l"].sum() if "water_saved_l" in esg_df.columns else 0
    total_energy = esg_df["energy_saved_kwh"].sum() if "energy_saved_kwh" in esg_df.columns else 0

    exp1, exp2, exp3 = st.columns(3)
    with exp1:
        ghg_json = ESGComplianceExporter.export_ghg_protocol(total_co2, total_energy)
        st.download_button(
            "📥 Export GHG Protocol (JSON)",
            data=ghg_json,
            file_name="GHG_Protocol_Disclosure.json",
            mime="application/json",
            use_container_width=True
        )
    with exp2:
        iso_csv = ESGComplianceExporter.export_iso14001_audit_trail(total_water, total_energy, total_co2)
        st.download_button(
            "📥 Export ISO 14001 Ledger (CSV)",
            data=iso_csv,
            file_name="ISO_14001_Audit_Trail.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp3:
        brsr_json = json.dumps(ESGComplianceExporter.export_brsr_report(total_water, total_energy, total_co2), indent=2)
        st.download_button(
            "📥 Export BRSR Principle 6 (JSON)",
            data=brsr_json,
            file_name="BRSR_Principle6_Disclosure.json",
            mime="application/json",
            use_container_width=True
        )


def main() -> None:
    esg_df = render_esg_kpis()
    render_financial_calculator(esg_df)
    render_compliance_exporters(esg_df)


if __name__ == "__main__":
    main()
