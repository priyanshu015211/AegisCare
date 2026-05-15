import streamlit as st
from frontend.utils.api_client import api_client


def show_patient_triage():
    st.header("Patient Triage")
    st.caption("Enter symptoms to get AI-powered assessment")

    with st.form("triage_form"):
        patient_id = st.text_input("Patient ID", value="P-1043")
        symptoms_input = st.text_area("Symptoms (comma separated)", "fever, cough, fatigue")
        duration = st.text_input("Duration", placeholder="2 days")

        submitted = st.form_submit_button("Analyze Patient")

        if submitted:
            symptoms = [s.strip() for s in symptoms_input.split(",") if s.strip()]

            with st.spinner("Analyzing symptoms..."):
                try:
                    response = api_client.post("/api/v1/patient/analyze", json={
                        "patient_id": patient_id,
                        "symptoms": symptoms,
                        "duration": duration
                    })

                    st.success("Analysis Complete")
                    st.json(response)

                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")
