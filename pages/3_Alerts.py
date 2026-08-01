# -*- coding: utf-8 -*-
"""
pages/3_Alerts.py — Industrial Alert Center & Dispatch System
Provides real-time alert monitoring, severity tracking, manual dispatch, and Telegram integration.
"""

import logging
from typing import Dict, Any

import streamlit as st
import shared_components as sc
from backend import database as db
from backend.security import has_permission, get_severity_badge, sanitize_input
from alert_manager import dispatch_alert

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageAlerts")

st.set_page_config(page_title="Alert Center — HydroThermal Nexus", page_icon="🚨", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="🚨 Industrial Alert Center", subtitle="Real-Time Telemetry Dispatches & Severity Audits")
sc.show_sidebar()


def render_alert_metrics() -> None:
    """Render top alert KPI cards."""
    alerts_df = db.get_alerts(limit=100)
    total = len(alerts_df)
    unacked = int((alerts_df["acknowledged"] == 0).sum()) if not alerts_df.empty else 0
    critical = int((alerts_df["severity"] == "CRITICAL").sum()) if not alerts_df.empty else 0

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <div class="kpi-label">Total Alerts (All Time)</div>
          <div class="kpi-value">{total}</div>
        </div>""", unsafe_allow_html=True)
    with a2:
        st.markdown(f"""
        <div class="kpi-card {'red' if unacked > 0 else 'green'}">
          <div class="kpi-label">Unacknowledged</div>
          <div class="kpi-value {'red' if unacked > 0 else 'green'}">{unacked}</div>
        </div>""", unsafe_allow_html=True)
    with a3:
        st.markdown(f"""
        <div class="kpi-card {'red' if critical > 0 else 'green'}">
          <div class="kpi-label">Critical Alerts</div>
          <div class="kpi-value {'red' if critical > 0 else 'green'}">{critical}</div>
        </div>""", unsafe_allow_html=True)


def render_manual_dispatch() -> None:
    """Render manual alert dispatch form."""
    bot_token = st.session_state.get("bot_token", "")
    chat_id = st.session_state.get("chat_id", "")

    if has_permission(role, "configure_alerts"):
        with st.expander("📡 Manual Alert Dispatch Console"):
            col_t, col_s = st.columns([3, 1])
            with col_t:
                alert_title = st.text_input("Alert Title", placeholder="e.g. Scheduled Compressor Servicing", key="manual_alert_title")
                alert_msg = st.text_area("Message Detail", placeholder="Describe alert context...", height=80, key="manual_alert_msg")
            with col_s:
                alert_sev = st.selectbox("Severity", ["INFO", "WARNING", "CRITICAL", "EMERGENCY"], key="manual_alert_sev")

            if st.button("📡 Dispatch Alert", use_container_width=True, key="btn_dispatch_alert"):
                if alert_title and alert_msg:
                    result = dispatch_alert(
                        severity=alert_sev,
                        title=sanitize_input(alert_title),
                        message=sanitize_input(alert_msg),
                        username=username, role=role,
                        telegram_token=bot_token, telegram_chat=chat_id,
                        force=True
                    )
                    st.success("✅ Alert dispatched successfully!")
                    for ch, res in result.items():
                        st.caption(f"Channel **{ch.title()}**: {res}")
                    logger.info("Manual alert '%s' dispatched by %s", alert_title, username)
                    st.rerun()
                else:
                    st.warning("⚠️ Please provide both alert title and detail message.")


def render_alert_history() -> None:
    """Render alert history log with acknowledgment buttons."""
    st.markdown('<div class="section-title">📋 Alert History Log</div>', unsafe_allow_html=True)
    alerts_df = db.get_alerts(limit=50)

    if alerts_df.empty:
        st.markdown("""
        <div class="glass-panel" style="text-align:center;color:#64748B;padding:2.5rem;">
          <div style="font-size:2rem;">✅</div>
          <div>No active or historical alerts on record.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for _, row in alerts_df.iterrows():
            sev = str(row.get("severity", "INFO")).upper()
            sev_cls = {"CRITICAL": "critical", "WARNING": "warning", "EMERGENCY": "critical", "INFO": "info"}.get(sev, "info")
            acked = bool(row.get("acknowledged", 0))
            ack_icon = "✅" if acked else "🔔"

            col_l, col_r = st.columns([5, 1])
            with col_l:
                st.markdown(f"""
                <div class="alert-item {sev_cls}">
                  <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#E2E8F0;">
                      {ack_icon} {row.get('title', '—')}
                    </div>
                    <div style="font-size:0.72rem;color:#64748B;margin-top:2px;">
                      {row.get('message', '')}
                    </div>
                    <div style="font-size:0.68rem;color:#94A3B8;margin-top:4px;">
                      🕐 {row.get('timestamp', '—')} · via {row.get('channel', '—')}
                    </div>
                  </div>
                  <div style="margin-left:1rem;">{get_severity_badge(sev)}</div>
                </div>""", unsafe_allow_html=True)
            with col_r:
                if not acked and has_permission(role, "acknowledge_alert"):
                    if st.button("Ack", key=f"ack_page_{row['id']}"):
                        db.acknowledge_alert(int(row["id"]), username)
                        logger.info("Alert ID %s acknowledged by %s", row["id"], username)
                        st.rerun()


def main() -> None:
    render_alert_metrics()
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    render_manual_dispatch()
    render_alert_history()


if __name__ == "__main__":
    main()
