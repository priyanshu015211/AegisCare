import streamlit as st
from frontend.utils.api_client import api_client


def show_patient_triage():
    st.header("Patient Triage")
    st.caption("AI-assisted clinical assessment")

    with st.form("triage_form"):
        st.subheader("Patient Information")

        col1, col2 = st.columns(2)
        with col1:
            patient_id = st.text_input("Patient ID", value="P-1043")
        with col2:
            duration = st.text_input("Duration", placeholder="e.g., 2 days")

        st.subheader("Symptoms")
        symptoms_input = st.text_area(
            "Enter symptoms (comma separated)", 
            value="fever, cough, fatigue",
            height=120
        )

        submitted = st.form_submit_button("Analyze Patient", use_container_width=True)

        if submitted:
            symptoms = [s.strip() for s in symptoms_input.split(",") if s.strip()]

            if not symptoms:
                st.error("Please enter at least one symptom.")
                return

            with st.spinner("Analyzing symptoms..."):
                try:
                    response = api_client.post("/api/v1/ai/analyze", json={
                        "patient_id": patient_id,
                        "symptoms": symptoms,
                        "duration": duration
                    })

                    analysis = response.get("analysis", {})

                    st.success("Analysis completed successfully.")

                    st.markdown("---")
                    st.subheader("Assessment Results")

                    # Severity and Risk Score
                    col1, col2 = st.columns(2)

                    with col1:
                        severity = analysis.get("severity", "medium").capitalize()
                        st.write(f"**Severity Level:** {severity}")

                    with col2:
                        risk_score = analysis.get("risk_score", 0)
                        st.write(f"**Risk Score:** {risk_score} / 100")

                    # Clinical Reasoning
                    st.subheader("Clinical Reasoning")
                    reasoning = analysis.get("reasoning", "No reasoning provided.")
                    st.write(reasoning)

                    # Follow-up Question
                    st.subheader("Suggested Follow-up Question")
                    follow_up = analysis.get("follow_up_question", "No follow-up question.")
                    st.write(follow_up)

                    # Escalation Status
                    if analysis.get("escalation_needed"):
                        st.warning("This case may require escalation based on current symptoms.")
                    else:
                        st.info("No immediate escalation required based on current assessment.")

                    with st.expander("View Technical Details"):
                        st.json(response.get("current_state", {}))

                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
