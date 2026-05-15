"""
backend/reports/handoff_report.py
"""

from datetime import datetime
from typing import Dict, Any


def generate_handoff_report(patient_state: Dict[str, Any]) -> str:
    symptoms = patient_state.get("symptoms", [])
    symptoms_text = ", ".join(symptoms) if symptoms else "None recorded"

    report = f"""
### AEGISCARE - DOCTOR HANDOFF REPORT

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

**Patient ID:** {patient_state.get('patient_id', 'N/A')}
**Current Severity:** {patient_state.get('severity', 'Unknown').upper()}
**Risk Score:** {patient_state.get('risk_score', 0)} / 100
**AI Confidence:** {patient_state.get('confidence', 0) * 100:.0f}%

**Reported Symptoms:**
{symptoms_text}

**Conversation Summary:**
{patient_state.get('conversation_summary', 'No summary available.')}

**Escalation History:**
{len(patient_state.get('escalation_history', []))} escalation(s) recorded.

**Recommended Next Steps:**
- Clinical review recommended
- Consider urgent evaluation if risk score ≥ 70
- Verify known conditions and allergies

---
*This is a system-generated report. Please verify clinically.*
"""
    return report.strip()
