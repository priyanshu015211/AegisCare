"""
backend/voice/stt/whisper_engine.py

Bug 7 fix: the temp file written for faster-whisper was always given a
.wav suffix regardless of the actual audio format. faster-whisper delegates
to ffmpeg for decoding, and ffmpeg trusts the file extension as a format
hint. Uploading an MP3 that lands in a file called *.wav causes ffmpeg to
mis-parse the header and produces silence or an error.

Fix: derive the correct extension from the first four bytes of the audio
data (magic-byte detection), falling back to .wav only when the format
cannot be identified. This matches the format detection already in voice.py
so the two are consistent.
"""

import os
import tempfile

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extension_for(audio_bytes: bytes) -> str:
    """
    Return the correct file extension for the given audio data by inspecting
    the magic bytes. Falls back to '.wav' if the format is unrecognised.

    faster-whisper passes the path straight to ffmpeg, which uses the
    extension as a format hint — so the extension must match the actual
    container format or ffmpeg will mis-parse the stream.
    """
    if audio_bytes[:4] == b"RIFF":
        return ".wav"
    if audio_bytes[:3] == b"ID3" or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return ".mp3"
    if audio_bytes[:4] == b"OggS":
        return ".ogg"
    if audio_bytes[:4] == b"fLaC":
        return ".flac"
    if audio_bytes[4:8] == b"ftyp":
        return ".m4a"
    # Unknown format — .wav is the safest default and ffmpeg will attempt to
    # auto-detect anyway if the extension is wrong.
    log.warning("Could not detect audio format from magic bytes; defaulting to .wav")
    return ".wav"


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

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
            # Bug 7 fix: return a structured sentinel value rather than a string
            # that looks like real transcription output.  The route in voice.py
            # checks this prefix and surfaces it to callers as a 503 so they
            # know transcription is non-functional, instead of receiving a fake
            # result silently.
            return "__PLACEHOLDER__: faster-whisper is not installed. Install it via requirements.txt to enable real transcription."

        # faster-whisper expects a file path, not raw bytes.
        # Write to a temp file with the correct extension so ffmpeg
        # decodes the stream with the right format hint.
        ext = _extension_for(audio_bytes)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name

            segments, _ = self.model.transcribe(
                tmp_path,
                language=language,
                beam_size=5
            )
            return " ".join([segment.text for segment in segments]).strip()

        except Exception as e:
            log.error(f"Transcription error: {e}")
            return "Error during transcription."

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
