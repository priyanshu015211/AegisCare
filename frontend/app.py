"""
frontend/app.py

AegisCare Streamlit application entry point.
This is the Phase 1 structural placeholder.
Full implementation happens in Phase 3.

Run with:
    streamlit run frontend/app.py
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AegisCare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AegisCare")
st.caption("AI Emergency Escalation & Healthcare Coordination System")

st.info(
    "Phase 1 complete — project structure established. "
    "Full frontend implementation begins in Phase 3.",
    icon="ℹ️",
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Backend", "Configured", delta="Phase 2 next")

with col2:
    st.metric("Database", "Pending", delta="Phase 4")

with col3:
    st.metric("AI Engine", "Pending", delta="Phase 8")

st.divider()
st.markdown(f"**Backend URL:** `{BACKEND_URL}`")
