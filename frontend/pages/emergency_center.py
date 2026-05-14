import streamlit as st

def show_emergency_center():
    st.header("Emergency Center")
    st.caption("High-Risk Patient Monitoring")

    st.subheader("High Risk Patients")
    st.dataframe({
        "Patient ID": ["P-0987", "P-0991", "P-0994"],
        "Risk Score": [82, 79, 85],
        "Last Update": ["2 min ago", "5 min ago", "12 min ago"],
        "Status": ["Escalated", "Under Review", "Critical"]
    }, use_container_width=True)

    st.subheader("Escalation Queue (Placeholder)")
    st.info("Patients requiring immediate attention will appear here.")
