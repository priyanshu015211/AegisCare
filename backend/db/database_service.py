async def save_handoff_report(
    self, 
    session_id: str, 
    patient_id: str, 
    report_content: str
) -> bool:
    """Save doctor handoff report to database."""
    if not self.is_connected:
        return False

    try:
        data = {
            "session_id": session_id,
            "patient_id": patient_id,
            "generated_at": datetime.utcnow().isoformat(),
            "report_markdown": report_content
        }

        self.client.table("reports").insert(data).execute()
        log.info(f"Handoff report saved for session {session_id}")
        return True

    except Exception as e:
        log.error(f"Failed to save handoff report: {e}")
        return False
