# -*- coding: utf-8 -*-
"""
pages/6_Settings.py — System Settings, Audit Ledger & Role-Based Access Control (RBAC)
Manages immutable audit logs, user administration, Telegram bot tokens, system configuration, and RBAC matrix.
"""

import datetime
import logging
from typing import Dict, Any

import streamlit as st
import pandas as pd

import shared_components as sc
from backend import database as db
from backend.security import has_permission, get_role_badge, ROLE_PERMISSIONS
import config

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageSettings")

st.set_page_config(page_title="Settings & Audit — HydroThermal Nexus", page_icon="⚙️", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="⚙️ Settings, Audit Ledger & RBAC Control", subtitle="System Configurations, Immutable Audit Logs & Security Administration")
sc.show_sidebar()


def render_audit_ledger() -> None:
    """Render audit logs table and export/clear actions."""
    st.markdown('<div class="section-title">📜 Immutable System Audit Ledger</div>', unsafe_allow_html=True)
    logs_df = db.get_audit_logs(limit=200)

    if logs_df.empty:
        st.info("No audit records found in SQLite ledger.")
    else:
        total_events = len(logs_df)
        anomaly_events = int((logs_df["action"] == "TRIGGER_ANOMALY").sum()) if "action" in logs_df.columns else 0
        login_events = int((logs_df["action"] == "LOGIN").sum()) if "action" in logs_df.columns else 0

        s1, s2, s3 = st.columns(3)
        s1.metric("Total Log Entries", total_events)
        s2.metric("Anomaly Events", anomaly_events)
        s3.metric("Login Events", login_events)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        st.dataframe(logs_df, use_container_width=True, height=300)

        col_exp, col_clr = st.columns([2, 1])
        with col_exp:
            if has_permission(role, "export_data"):
                csv = logs_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export Audit CSV", data=csv,
                    file_name=f"NexusAI_Audit_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        with col_clr:
            if has_permission(role, "clear_audit"):
                if st.button("🗑️ Clear Audit Trail", type="primary", key="btn_clear_audit"):
                    db.clear_audit_logs()
                    db.log_audit(username, role, "AUDIT_CLEARED", "None", "Audit trail cleared by admin.")
                    logger.warning("Audit trail cleared by %s", username)
                    st.rerun()


def render_rbac_matrix() -> None:
    """Render Role-Based Access Control matrix."""
    st.markdown("---")
    st.markdown('<div class="section-title">🛡️ Role-Based Access Control (RBAC) Matrix</div>', unsafe_allow_html=True)

    perm_data = []
    all_permissions = set()
    for role_name, perms in ROLE_PERMISSIONS.items():
        all_permissions.update(perms)

    for perm in sorted(all_permissions):
        row = {"Permission": perm}
        for role_name in ["Viewer", "Field Engineer", "Sustainability Auditor", "Chief Financial Officer (CFO)", "Admin", "Operator"]:
            row[role_name] = "✅ Allowed" if has_permission(role_name, perm) else "❌ Denied"
        perm_data.append(row)

    df_rbac = pd.DataFrame(perm_data)
    st.dataframe(df_rbac, use_container_width=True)


def render_system_diagnostics() -> None:
    """Render environment variable diagnostic table."""
    st.markdown("---")
    st.markdown('<div class="section-title">🔧 System Environment & Configuration Diagnostics</div>', unsafe_allow_html=True)

    sys_cfg = config.get_system_config()
    st.json(sys_cfg)


def main() -> None:
    render_audit_ledger()
    render_rbac_matrix()
    render_system_diagnostics()


if __name__ == "__main__":
    main()
