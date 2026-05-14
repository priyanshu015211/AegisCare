import streamlit as st

def show_coordination_dashboard():
    st.header("Emergency Coordination Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Active Emergencies", "7")
    with col2: st.metric("Pending Appointments", "12")
    with col3: st.metric("Doctors Available", "4/9")

    st.subheader("High Priority Queue")
    st.dataframe({
        "Patient": ["P-1201", "P-1198"],
        "Risk": [88, 79],
        "Action": ["Video Consult", "Book Appointment"]
    })
