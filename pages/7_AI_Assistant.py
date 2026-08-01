# -*- coding: utf-8 -*-
"""
pages/7_AI_Assistant.py — Interactive Industrial AI Copilot & Chat Assistant
Provides domain-specific AI advice, quick action chips, anomaly explanations, and operational guidelines.
"""

import datetime
import logging
from typing import Dict, Any, List

import streamlit as st
import shared_components as sc
from backend.security import sanitize_input
from ai_assistant import get_ai_response, QUICK_ACTIONS

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageAIAssistant")

st.set_page_config(page_title="AI Assistant — HydroThermal Nexus", page_icon="💬", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

sc.show_header(title="🤖 Interactive AI Copilot Assistant", subtitle="Domain Knowledge, RCA Diagnostics & Operational Guidelines")
sc.show_sidebar()


def main() -> None:
    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")
    score = st.session_state.get("health_score", 97.4)

    st.markdown('<div class="section-title">🤖 Nexus Industrial Copilot</div>', unsafe_allow_html=True)
    st.caption("Ask questions regarding live telemetry, anomaly detection, ESG compliance, or emergency mitigation procedures.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "bot",
            "content": (
                f"👋 Hello **{username}** ({role})! I'm your **Nexus-AI Assistant**.\n\n"
                "I have deep operational knowledge of this facility — anomaly detection, ESG metrics, "
                "actuators, alerts, and safety procedures.\n\nHow can I assist you today?"
            ),
            "time": datetime.datetime.now().strftime("%H:%M")
        }]

    system_state = {"username": username, "role": role, "current_anomaly": anomaly, "health_score": score}

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            is_user = msg["role"] == "user"
            with st.chat_message("user" if is_user else "assistant"):
                st.write(msg["content"])
                st.caption(f"🕐 {msg['time']}")

    st.markdown("##### ⚡ Quick Prompt Chips")
    chip_cols = st.columns(4)
    quick_actions_display = QUICK_ACTIONS[:8]
    for i, qa in enumerate(quick_actions_display):
        with chip_cols[i % 4]:
            if st.button(f"💬 {qa[:28]}…" if len(qa) > 28 else f"💬 {qa}", key=f"chip_page_{i}", use_container_width=True):
                st.session_state["pending_chat_page"] = qa

    prompt = st.chat_input("Type your question regarding plant operations…")
    pending = st.session_state.pop("pending_chat_page", None)
    user_query = prompt or pending

    if user_query and user_query.strip():
        clean_input = sanitize_input(user_query, max_len=512)
        st.session_state.chat_history.append({
            "role": "user",
            "content": clean_input,
            "time": datetime.datetime.now().strftime("%H:%M")
        })
        response = get_ai_response(clean_input, system_state, st.session_state.chat_history)
        st.session_state.chat_history.append({
            "role": "bot",
            "content": response,
            "time": datetime.datetime.now().strftime("%H:%M")
        })
        if len(st.session_state.chat_history) > 40:
            st.session_state.chat_history = st.session_state.chat_history[-40:]
        logger.info("Processed AI chat query for %s", username)
        st.rerun()

    if st.button("🗑️ Clear Conversation", use_container_width=False, key="btn_clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


if __name__ == "__main__":
    main()
