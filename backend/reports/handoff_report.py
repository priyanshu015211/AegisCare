from datetime import datetime
from typing import Dict, Any

def generate_handoff_report(patient_state: Dict[str, Any]) -> str:
    return f"""
### AEGISCARE DOCTOR HANDOFF REPORT
**Generated:** {datetime.utcnow()}

**Patient ID:** {patient_state.get('patient_id')}
**Severity:** {patient_state.get('severity')}
**Risk Score:** {patient_state.get('risk_score')}

**Symptoms:** {', '.join(patient_state.get('symptoms', []))}
**Summary:** {patient_state.get('conversation_summary', 'N/A')}
"""
