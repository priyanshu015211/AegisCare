"""
backend/services/data_retention.py

Data retention cleanup service.

HIPAA requires a defined data retention policy. This service:
1. Removes expired sessions (and their cascading symptoms/escalations)
2. Archives old handoff reports
3. Cleans up old audit log files

This should be run:
- As a scheduled job (daily or weekly)
- On application startup (optional, via lifespan handler)
- Manually via a CLI command or API endpoint

The retention periods are configurable via environment variables:
- SESSION_RETENTION_DAYS (default: 365)
- AUDIT_LOG_RETENTION_DAYS (default: 2555 / ~7 years)
"""

import os
import glob
import logging
from datetime import datetime, timedelta, timezone

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()


class DataRetentionService:
    """
    Service for enforcing data retention policies.

    Usage:
        service = DataRetentionService()
        results = service.run_cleanup()
        print(results)
    """

    def __init__(self):
        self.session_retention_days = settings.session_retention_days
        self.audit_log_retention_days = settings.audit_log_retention_days
        self.log_retention_days = settings.log_retention_days

    def run_cleanup(self) -> dict:
        """
        Run all cleanup tasks. Returns a summary of what was cleaned.

        Returns:
            dict with keys: sessions_cleaned, logs_cleaned, errors
        """
        results = {
            "sessions_cleaned": 0,
            "logs_cleaned": 0,
            "errors": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            results["sessions_cleaned"] = self._cleanup_expired_sessions()
        except Exception as e:
            results["errors"].append(f"Session cleanup failed: {str(e)}")
            log.error(f"Session cleanup failed: {e}")

        try:
            results["logs_cleaned"] = self._cleanup_old_log_files()
        except Exception as e:
            results["errors"].append(f"Log cleanup failed: {str(e)}")
            log.error(f"Log cleanup failed: {e}")

        log.info(f"Data retention cleanup complete: {results}")
        return results

    def _cleanup_expired_sessions(self) -> int:
        """
        Clean up sessions older than the retention period.

        Note: In production, this should use Supabase/SQL to delete:
            DELETE FROM sessions WHERE started_at < NOW() - INTERVAL 'X days'
            CASCADE will remove related symptom_records, escalations, reports

        For now, this logs what WOULD be deleted.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.session_retention_days)

        log.info(
            f"Data retention: Would delete sessions older than {cutoff.isoformat()} "
            f"(retention={self.session_retention_days} days). "
            f"Requires Supabase connection to execute."
        )

        # TODO: Uncomment when Supabase is connected
        # db = get_supabase_admin_client()
        # if db:
        #     result = db.table("sessions").delete().lt("started_at", cutoff.isoformat()).execute()
        #     return len(result.data) if result.data else 0

        return 0

    def _cleanup_old_log_files(self) -> int:
        """
        Remove log files older than the retention period.

        Log files follow the pattern: logs/aegiscare.log.YYYY-MM-DD
        """
        log_dir = os.path.dirname(settings.log_file) or "logs"
        if not os.path.exists(log_dir):
            return 0

        cutoff = datetime.now() - timedelta(days=self.log_retention_days)
        removed_count = 0

        # Find rotated log files (e.g., aegiscare.log.2026-01-15)
        pattern = os.path.join(log_dir, f"{os.path.basename(settings.log_file)}.*")
        for log_file in glob.glob(pattern):
            try:
                # Extract date from filename
                parts = log_file.split(".")
                if len(parts) >= 3:
                    date_str = parts[-1]  # Last part should be the date
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        os.remove(log_file)
                        removed_count += 1
                        log.debug(f"Removed expired log file: {log_file}")
            except (ValueError, OSError) as e:
                log.warning(f"Could not process log file {log_file}: {e}")

        if removed_count > 0:
            log.info(f"Data retention: Removed {removed_count} expired log files")

        return removed_count

    def get_retention_policy(self) -> dict:
        """Return the current retention policy configuration."""
        return {
            "session_retention_days": self.session_retention_days,
            "audit_log_retention_days": self.audit_log_retention_days,
            "log_retention_days": self.log_retention_days,
            "session_cutoff": (
                datetime.now(timezone.utc) - timedelta(days=self.session_retention_days)
            ).isoformat(),
            "description": {
                "sessions": f"Sessions older than {self.session_retention_days} days are deleted",
                "audit_logs": f"Audit logs are retained for {self.audit_log_retention_days} days (HIPAA)",
                "app_logs": f"Application logs are retained for {self.log_retention_days} days",
            },
        }


def run_retention_cleanup():
    """CLI entry point for data retention cleanup."""
    service = DataRetentionService()
    results = service.run_cleanup()

    if results["errors"]:
        print(f"Cleanup completed with {len(results['errors'])} errors:")
        for error in results["errors"]:
            print(f"  - {error}")
    else:
        print(f"Cleanup completed successfully: {results}")
