"""
backend/core/config.py

Central configuration for AegisCare backend.
All settings are loaded from environment variables via pydantic-settings.
No hardcoded secrets. Fail fast if required values are missing.
"""

import os
import warnings
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    AegisCare application settings.
    Values are read from environment variables or the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----------------------------------------------------------
    # Application
    # ----------------------------------------------------------
    app_env: str = Field(default="development")
    app_name: str = Field(default="AegisCare")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ----------------------------------------------------------
    # Backend
    # ----------------------------------------------------------
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default_factory=lambda: int(os.environ.get("PORT", 8000)))
    backend_workers: int = Field(default=1)

    # "changeme" is the insecure fallback. A validator below raises an error
    # in production and emits a loud warning in development so this is never
    # silently deployed with a known-weak key.
    # Generate a safe value with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    secret_key: str = Field(default="changeme")

    # Must be set to real domain(s) in production — never "*".
    # See render.yaml for instructions.
    allowed_origins: str = Field(default="*")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        is_production = os.environ.get("APP_ENV", "development").lower() == "production"
        if v in ("changeme", "", "secret", "dev"):
            if is_production:
                raise ValueError(
                    "SECRET_KEY is set to an insecure default value. "
                    "Set a strong SECRET_KEY environment variable before deploying. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            else:
                warnings.warn(
                    "WARNING: SECRET_KEY is using the insecure default 'changeme'. "
                    "Set SECRET_KEY in your .env file for local dev to avoid this warning. "
                    "This will raise an error in production.",
                    stacklevel=2,
                )
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    # ----------------------------------------------------------
    # Frontend
    # ----------------------------------------------------------
    streamlit_port: int = Field(default=8501)
    backend_url: str = Field(default="http://localhost:8000")

    # ----------------------------------------------------------
    # Supabase
    # ----------------------------------------------------------
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_service_role_key: str = Field(default="")

    # ----------------------------------------------------------
    # AI Models
    # ----------------------------------------------------------
    gemini_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    primary_llm: str = Field(default="gemini")
    gemini_model: str = Field(default="gemini-1.5-flash")
    openai_model: str = Field(default="gpt-4o-mini")
    llm_max_tokens: int = Field(default=1024)
    llm_temperature: float = Field(default=0.3)
    llm_timeout_seconds: int = Field(default=30)

    # ----------------------------------------------------------
    # Voice
    # ----------------------------------------------------------
    whisper_model_size: str = Field(default="base")
    whisper_device: str = Field(default="cpu")
    whisper_compute_type: str = Field(default="int8")
    tts_engine: str = Field(default="xtts")
    tts_model_path: str = Field(default="./voice_pipeline/tts/models/")
    audio_sample_rate: int = Field(default=16000)
    audio_channels: int = Field(default=1)

    # ----------------------------------------------------------
    # Agora
    # ----------------------------------------------------------
    agora_app_id: str = Field(default="")
    agora_app_certificate: str = Field(default="")
    agora_token_expiry_seconds: int = Field(default=3600)

    # ----------------------------------------------------------
    # Emergency Escalation Thresholds
    # ----------------------------------------------------------
    escalation_green_threshold: int = Field(default=30)
    escalation_yellow_threshold: int = Field(default=60)
    escalation_red_threshold: int = Field(default=61)
    escalation_critical_threshold: int = Field(default=85)

    # ----------------------------------------------------------
    # Hospital Load
    # ----------------------------------------------------------
    max_hospital_capacity: int = Field(default=100)
    high_load_threshold: int = Field(default=80)
    critical_load_threshold: int = Field(default=95)

    # ----------------------------------------------------------
    # Scheduling
    # ----------------------------------------------------------
    default_appointment_duration_minutes: int = Field(default=15)
    max_advance_booking_days: int = Field(default=30)
    slot_interval_minutes: int = Field(default=15)

    # ----------------------------------------------------------
    # Session / Memory
    # ----------------------------------------------------------
    session_expiry_hours: int = Field(default=24)
    patient_memory_max_turns: int = Field(default=20)
    memory_summary_trigger: int = Field(default=15)

    # ----------------------------------------------------------
    # Rate Limiting
    # ----------------------------------------------------------
    rate_limit_requests_per_minute: int = Field(default=60)
    rate_limit_burst: int = Field(default=20)

    # ----------------------------------------------------------
    # Logging
    # ----------------------------------------------------------
    log_file: str = Field(default="logs/aegiscare.log")
    log_rotation: str = Field(default="10 MB")
    log_retention: str = Field(default="30 days")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Use this everywhere instead of instantiating Settings() directly.
    """
    return Settings()
