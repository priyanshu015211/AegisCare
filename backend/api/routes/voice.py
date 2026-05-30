"""
backend/api/routes/voice.py

FIX Bug 8: The /respond endpoint previously always called synthesize(), got
back empty bytes (b"") from the XTTSEngine placeholder, and then returned a
JSON response claiming success with audio_size=0. Any client expecting audio
would silently receive nothing with no indication the feature was unavailable.

Fixes applied:
1. XTTSEngine now exposes an `is_available` flag so the route can check
   before calling synthesize().
2. When TTS is unavailable, /respond returns HTTP 503 Service Unavailable
   with a clear message instead of a misleading success response.
3. When TTS is available and returns real audio bytes, the endpoint returns
   a proper StreamingResponse with Content-Type: audio/wav so clients can
   actually play it.
4. WhisperEngine and XTTSEngine are instantiated lazily (on first request)
   rather than at module import time, consistent with the fix for Bug 4/5.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
import io

from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])

# Lazy singletons — created on first request, not at import time
_whisper_engine = None
_xtts_engine = None


def _get_whisper():
    global _whisper_engine
    if _whisper_engine is None:
        from backend.voice.stt.whisper_engine import WhisperEngine
        _whisper_engine = WhisperEngine()
    return _whisper_engine


def _get_xtts():
    global _xtts_engine
    if _xtts_engine is None:
        from backend.voice.tts.xtts_engine import XTTSEngine
        _xtts_engine = XTTSEngine()
    return _xtts_engine


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Transcribe an uploaded audio file to text using Whisper.
    Accepts any audio/* MIME type.
    """
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only audio files are accepted (audio/* content type required)"
        )

    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty"
        )

    whisper = _get_whisper()
    text = await whisper.transcribe(audio_bytes, language=language)
    return {"status": "success", "transcription": text, "language": language}


@router.post("/respond")
async def generate_voice_response(text: str, language: str = "en"):
    """
    Synthesise speech from text and return it as a streaming audio/wav response.

    Returns HTTP 503 if the TTS engine is running in placeholder mode
    (i.e. faster-whisper / XTTS is not installed in this deployment).
    Returns a StreamingResponse with Content-Type audio/wav when available.
    """
    xtts = _get_xtts()

    # FIX Bug 8: check availability before calling synthesize so we never
    # return a misleading success response with 0 bytes of audio.
    if not xtts.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Text-to-speech is not available in this deployment. "
                "Install the XTTS dependencies and set TTS_ENGINE in your .env to enable it."
            )
        )

    audio_bytes = await xtts.synthesize(text, language=language)

    if not audio_bytes:
        # Synthesis ran but produced nothing — surface this as a server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TTS synthesis returned no audio. Check engine logs."
        )

    # Stream the raw audio bytes back with the correct content type so
    # clients (browsers, mobile apps) can play it directly.
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "inline; filename=response.wav",
            "Content-Length": str(len(audio_bytes)),
        }
    )
