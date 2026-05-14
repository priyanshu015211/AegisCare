"""
tests/backend/test_phase1_structure.py

Phase 1 validation tests.
Verify that all expected files, modules, and configurations exist and import correctly.

Run with:
    pytest tests/backend/test_phase1_structure.py -v
"""

import os
import pytest
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent  # aegiscare2/


class TestDirectoryStructure:
    """Verify that all required directories exist."""

    REQUIRED_DIRS = [
        "backend",
        "backend/api",
        "backend/api/routes",
        "backend/api/middleware",
        "backend/core",
        "backend/models",
        "backend/services",
        "backend/services/ai",
        "backend/services/voice",
        "backend/services/escalation",
        "backend/db",
        "frontend",
        "frontend/pages",
        "frontend/components",
        "frontend/assets",
        "frontend/utils",
        "voice_pipeline",
        "voice_pipeline/stt",
        "voice_pipeline/tts",
        "voice_pipeline/audio",
        "project_memory",
        "tests",
        "tests/backend",
        "tests/frontend",
        "docker",
        "docs",
    ]

    @pytest.mark.parametrize("directory", REQUIRED_DIRS)
    def test_directory_exists(self, directory):
        path = ROOT / directory
        assert path.exists(), f"Directory missing: {directory}"
        assert path.is_dir(), f"Not a directory: {directory}"


class TestRequiredFiles:
    """Verify that all critical files exist."""

    REQUIRED_FILES = [
        "README.md",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "docker-compose.yml",
        "backend/main.py",
        "backend/core/config.py",
        "backend/core/constants.py",
        "backend/core/logging.py",
        "backend/models/patient.py",
        "backend/models/hospital.py",
        "backend/models/api_schemas.py",
        "frontend/app.py",
        "docker/Dockerfile.backend",
        "docker/Dockerfile.frontend",
        "project_memory/architecture.md",
        "project_memory/current_progress.md",
        "project_memory/api_contracts.md",
        "project_memory/database_schema.md",
        "project_memory/ui_guidelines.md",
        "project_memory/feature_status.md",
        "project_memory/prompt_context.md",
        "project_memory/env_setup.md",
        "project_memory/future_tasks.md",
        "project_memory/known_issues.md",
        "project_memory/developer_handoff.md",
    ]

    @pytest.mark.parametrize("filepath", REQUIRED_FILES)
    def test_file_exists(self, filepath):
        path = ROOT / filepath
        assert path.exists(), f"File missing: {filepath}"
        assert path.is_file(), f"Not a file: {filepath}"
        assert path.stat().st_size > 0, f"File is empty: {filepath}"


class TestPythonModules:
    """Verify Python modules can be imported without errors."""

    def test_config_imports(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.core.config import get_settings, Settings
        assert get_settings is not None
        assert Settings is not None

    def test_constants_imports(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.core.constants import (
            SeverityLevel, EscalationAction, MemoryEventType,
            CRITICAL_SYMPTOMS, RESPIRATORY_SYMPTOMS, MAX_CONTEXT_TOKENS
        )
        assert SeverityLevel.GREEN == "green"
        assert SeverityLevel.CRITICAL == "critical"
        assert MAX_CONTEXT_TOKENS == 800

    def test_patient_models_import(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.models.patient import (
            PatientState, SessionMemory, SymptomRecord,
            EscalationRecord, Appointment, PatientProfile
        )
        assert PatientState is not None

    def test_hospital_models_import(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.models.hospital import Hospital, DoctorProfile, HospitalLoad
        assert Hospital is not None

    def test_api_schemas_import(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.models.api_schemas import (
            APIResponse, ChatMessageRequest, ChatMessageResponse,
            EscalationRequest, AppointmentRequest, ReportRequest
        )
        assert APIResponse is not None


class TestPatientStateSchema:
    """Verify PatientState schema behaves correctly."""

    def test_default_severity_is_green(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.models.patient import PatientState
        from backend.core.constants import SeverityLevel

        state = PatientState(patient_id="p1", session_id="s1")
        assert state.severity == SeverityLevel.GREEN
        assert state.risk_score == 0
        assert state.escalation_triggered is False

    def test_patient_state_serializes_to_dict(self):
        import sys
        sys.path.insert(0, str(ROOT))
        from backend.models.patient import PatientState

        state = PatientState(
            patient_id="p1",
            session_id="s1",
            symptoms=["fever", "cough"],
            risk_score=45,
        )
        data = state.model_dump()
        assert data["symptoms"] == ["fever", "cough"]
        assert data["risk_score"] == 45


class TestEnvExample:
    """Verify .env.example has required keys."""

    REQUIRED_KEYS = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "GEMINI_API_KEY",
        "SECRET_KEY",
        "BACKEND_PORT",
        "STREAMLIT_PORT",
        "PRIMARY_LLM",
        "WHISPER_MODEL_SIZE",
        "ESCALATION_GREEN_THRESHOLD",
        "ESCALATION_RED_THRESHOLD",
    ]

    def test_env_example_has_required_keys(self):
        env_path = ROOT / ".env.example"
        content = env_path.read_text()
        for key in self.REQUIRED_KEYS:
            assert key in content, f"Missing key in .env.example: {key}"
