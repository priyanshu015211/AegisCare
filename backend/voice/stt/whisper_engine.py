from backend.core.logging import get_logger
log = get_logger(__name__)

class WhisperEngine:
    def __init__(self, model_size="base"):
        self.model_size = model_size

    async def transcribe(self, audio_bytes: bytes) -> str:
        log.info("Transcribing audio (placeholder)")
        return "Placeholder transcription from patient voice."
