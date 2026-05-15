"""
backend/voice/tts/xtts_engine.py

Text-to-Speech using XTTS-v2 (Coqui TTS).
"""

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    log.warning("TTS (Coqui) not installed. Using placeholder mode.")


class XTTSEngine:
    def __init__(self):
        self.tts = None

        if TTS_AVAILABLE:
            try:
                self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
                log.info("XTTS-v2 model loaded successfully")
            except Exception as e:
                log.error(f"Failed to load XTTS model: {e}")
        else:
            log.warning("Running in TTS placeholder mode")

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech audio bytes.
        """
        if not self.tts:
            return b"placeholder_audio_bytes"  # Return dummy audio in placeholder mode

        try:
            # Note: Real implementation would save to file and read bytes
            wav_path = "/tmp/output.wav"
            self.tts.tts_to_file(text=text, speaker_wav=None, language=language, file_path=wav_path)

            with open(wav_path, "rb") as f:
                return f.read()
        except Exception as e:
            log.error(f"TTS synthesis error: {e}")
            return b""
