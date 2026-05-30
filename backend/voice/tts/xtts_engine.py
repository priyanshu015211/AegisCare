"""
backend/voice/tts/xtts_engine.py

Bug 8 fix: the previous code set self.is_available = True as soon as the
TTS library was importable, even though the model loading line was commented
out and self._model was left as None. The synthesize() method then checked
`if not self.is_available or self._model is None` — the is_available branch
was always False (flag was True) and the _model branch was always True (None)
— so it returned b"" on every call. The is_available flag was therefore
meaningless: it claimed the engine was ready when it provably wasn't.

Fix: is_available is only set to True after the model is successfully loaded
into self._model. The flag now accurately reflects whether the engine can
produce audio, which is what the /voice/respond route checks (voice.py Bug 2).
"""

from backend.core.logging import get_logger

log = get_logger(__name__)

# Try to import the real XTTS library — fall back to placeholder mode if absent
try:
    from TTS.api import TTS as CoquiTTS
    _XTTS_LIBRARY_AVAILABLE = True
except ImportError:
    _XTTS_LIBRARY_AVAILABLE = False


class XTTSEngine:
    """
    Text-to-speech engine wrapper.

    is_available is True only when both the library is installed AND the
    model has been successfully loaded into self._model. Any other state
    means synthesize() will return b"" and callers should surface a 503.
    """

    def __init__(self):
        self.is_available = False
        self._model = None

        if not _XTTS_LIBRARY_AVAILABLE:
            log.warning(
                "TTS library not installed — XTTSEngine running in placeholder mode. "
                "The /voice/respond endpoint will return 503 until TTS is installed."
            )
            return

        try:
            self._model = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2")
            # Only mark available after the model is confirmed loaded
            self.is_available = True
            log.info("XTTSEngine initialised — model loaded successfully")
        except Exception as e:
            log.error(
                f"XTTSEngine failed to load model: {e}. "
                "The /voice/respond endpoint will return 503."
            )
            self._model = None
            self.is_available = False

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesise speech from text.

        Returns raw WAV bytes when is_available is True and the model is loaded.
        Returns b"" in all other cases — callers must check is_available before
        calling this method and raise a 503 on an empty result.
        """
        if not self.is_available or self._model is None:
            return b""

        try:
            import io
            import wave
            import struct
            wav_samples = self._model.tts(text=text, language=language)
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)    # 16-bit PCM
                wf.setframerate(24000)
                wf.writeframes(
                    struct.pack(f"<{len(wav_samples)}h",
                                *[int(s * 32767) for s in wav_samples])
                )
            return buf.getvalue()
        except Exception as e:
            log.error(f"TTS synthesis error: {e}")
            return b""
