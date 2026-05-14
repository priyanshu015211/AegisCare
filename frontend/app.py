"""
frontend/app.py

AegisCare Streamlit Frontend - Main Application Entry Point
Phase 3: Complete Frontend Foundation
"""

import streamlit as st
from frontend.styles.theme import apply_custom_css
from frontend.components.sidebar import render_sidebar

st.set_page_config(
    page_title="AegisCare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()
render_sidebar()

st.title("AegisCare")
st.caption("AI Emergency Escalation & Healthcare Coordination System")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active Sessions", "47", "+5")
with col2:
    st.metric("High Risk", "8", "-2", delta_color="inverse")
with col3:
    st.metric("Avg Response Time", "4.2 min", "-0.8 min")
with col4:
    st.metric("Hospital Load", "72%", "+5%")

st.markdown("---")

st.success("Frontend foundation is ready. Use the sidebar to navigate between modules.", icon="✅")

st.markdown("""
### Available Modules
- **Dashboard** — Hospital overview and key metrics
- **Patient Triage** — Symptom input and assessment interface
- **Emergency Center** — High-risk patient monitoring
- **Analytics** — Trends and reporting
""")
