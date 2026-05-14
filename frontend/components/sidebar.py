"""
frontend/components/sidebar.py

Reusable sidebar navigation for AegisCare.
"""

import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("AegisCare")
        st.caption("Healthcare Coordination")

        st.markdown("---")

        page = st.radio(
            "Navigation",
            options=["Dashboard", "Patient Triage", "Emergency Center", "Analytics"],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.subheader("System Status")
        st.success("Backend: Connected", icon="🟢")
        st.info("Database: Ready", icon="🔵")

        st.markdown("---")
        st.caption("v0.1.0 • Phase 3 Foundation")

        st.session_state["current_page"] = page
        return page
