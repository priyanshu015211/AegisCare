import streamlit as st
from frontend.utils.api_client import api_client

def show_coordination_dashboard():
    st.header("Emergency Coordination Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Active Emergencies", "7")
    with col2: st.metric("Pending Appointments", "12")
    with col3: st.metric("Doctors Available", "4/9")

    st.subheader("High Priority Queue")

    try:
        # Example: Fetch high-risk patients from backend (future)
        # data = api_client.get("/api/v1/coordination/high-risk")
        st.dataframe({
            "Patient": ["P-1201", "P-1198"],
            "Risk": [88, 79],
            "Action": ["Video Consult", "Book Appointment"]
        })
    except Exception as e:
        st.error(f"Failed to load data: {e}")
