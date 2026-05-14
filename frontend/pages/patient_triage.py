import streamlit as st

def show_patient_triage():
    st.header("Patient Triage")
    st.caption("Symptom Input & Initial Assessment")

    with st.form("triage_form"):
        patient_id = st.text_input("Patient ID", value="P-1043")
        symptoms = st.text_area("Reported Symptoms", placeholder="fever, cough, fatigue")
        duration = st.text_input("Duration", placeholder="2 days")

        if st.form_submit_button("Submit for Assessment"):
            st.success("Assessment submitted (placeholder).")
            st.info("This will connect to backend in future phases.")

    st.markdown("---")
    st.subheader("Symptom Timeline (Placeholder)")
    st.write("• 10:15 - Fever reported")
    st.write("• 10:22 - Cough added")

    st.subheader("Assessment Result (Placeholder)")
    col1, col2 = st.columns(2)
    with col1: st.metric("Estimated Risk Score", "58 / 100")
    with col2: st.metric("Severity Level", "Medium")
