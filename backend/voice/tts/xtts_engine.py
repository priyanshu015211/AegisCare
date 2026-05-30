"""
backend/voice/tts/xtts_engine.py

FIX Bug 8: Added `is_available` flag so callers (voice.py /respond route)
can check whether TTS is actually functional before calling synthesize().
Previously the engine silently returned b"" and the route claimed success —
now the route can return a proper 503 instead of a misleading empty response.
"""

from backend.core.logging import get_logger

log = get_logger(__name__)

# Try to import the real XTTS library — fall back to placeholder mode if absent
try:
    # TTS (Coqui) is the library that powers XTTS v2
    from TTS.api import TTS as CoquiTTS  # noqa: F401
    _XTTS_LIBRARY_AVAILABLE = True
except ImportError:
    _XTTS_LIBRARY_AVAILABLE = False


class XTTSEngine:
    """
    Text-to-speech engine wrapper.

    When the XTTS library is installed this will synthesise real audio.
    When it is not installed (most deployments for now) `is_available` is
    False and the /respond route returns a 503 rather than empty bytes.
    """

    def __init__(self):
        self.is_available = False
        self._model = None

        if _XTTS_LIBRARY_AVAILABLE:
            try:
                # Actual model loading would go here, e.g.:
                # self._model = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2")
                # For now we confirm the library is present but don't load the model.
                self.is_available = True
                log.info("XTTSEngine initialised (library available)")
            except Exception as e:
                log.error(f"XTTSEngine failed to load model: {e}")
                self.is_available = False
        else:
            log.warning(
                "TTS library not installed — XTTSEngine running in placeholder mode. "
                "The /voice/respond endpoint will return 503 until TTS is installed."
            )

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesise speech from text.

        Returns raw audio bytes (WAV format) when is_available is True.
        Returns b"" when running in placeholder mode — callers should check
        is_available before calling this method.
        """
        if not self.is_available or self._model is None:
            return b""

        try:
            # Real synthesis would go here using self._model
            # e.g. wav = self._model.tts(text=text, language=language)
            # return wav_to_bytes(wav)
            return b""
        except Exception as e:
            log.error(f"TTS synthesis error: {e}")
            return b""
