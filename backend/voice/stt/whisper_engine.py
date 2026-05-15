"""
backend/voice/stt/whisper_engine.py
"""

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    log.warning("faster-whisper not installed. Using placeholder mode.")


class WhisperEngine:
    def __init__(self, model_size: str = None):
        self.model_size = model_size or settings.whisper_model_size
        self.model = None

        if WHISPER_AVAILABLE:
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device=settings.whisper_device,
                    compute_type=settings.whisper_compute_type
                )
                log.info(f"Whisper model '{self.model_size}' loaded successfully")
            except Exception as e:
                log.error(f"Failed to load Whisper model: {e}")
                self.model = None
        else:
            log.warning("Running in placeholder mode (no real transcription)")

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        if not self.model:
            return "This is a placeholder transcription. Please install faster-whisper."

        try:
            segments, info = self.model.transcribe(
                audio_bytes,
                language=language,
                beam_size=5
            )
            return " ".join([segment.text for segment in segments]).strip()
        except Exception as e:
            log.error(f"Transcription error: {e}")
            return "Error during transcription."
