"""
backend/api/routes/voice.py

Bug 19 fix: The previous implementation only checked file.content_type,
which is a client-supplied header — trivially spoofed and not validated
by faster-whisper until deep inside the model call, producing an unhelpful
500 error.

Now we:
  1. Enforce an explicit allowlist of supported MIME types (not just startswith("audio/"))
  2. Read the first 12 bytes and check magic bytes to verify the file is
     actually the format it claims to be, independent of the Content-Type header.
  3. Enforce a max file size (25 MB) to prevent OOM on the Whisper model.
  4. Return a clear 400 with a descriptive message on every validation failure,
     so clients get actionable errors instead of a generic 500.
"""

import io
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])

# ---------------------------------------------------------------------------
# Bug 8 fix: initialise heavy ML engines ONCE at module load time, not on
# every request.  XTTSEngine loads a multi-GB model; WhisperEngine loads a
# Whisper checkpoint.  Creating a new instance per request was
# catastrophically slow (many seconds of model loading per call).
#
# Both engines gracefully degrade to placeholder/unavailable mode when their
# optional dependencies (TTS / faster-whisper) are not installed, so this is
# safe to do at import time.
# ---------------------------------------------------------------------------
from backend.voice.stt.whisper_engine import WhisperEngine
from backend.voice.tts.xtts_engine import XTTSEngine

_whisper_engine: WhisperEngine = WhisperEngine()
_xtts_engine: XTTSEngine = XTTSEngine()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Explicit allowlist — faster-whisper supports WAV, MP3, OGG, FLAC, M4A/MP4
ALLOWED_MIME_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",       # mp3
    "audio/mp3",
    "audio/ogg",
    "audio/flac",
    "audio/x-flac",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "video/mp4",        # some browsers send m4a as video/mp4
}

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB

# Magic-byte signatures for each supported format.
# Each entry is (label, list_of_accepted_prefixes).
# We only need the first 12 bytes of the file to cover all formats here.
_MAGIC: list[tuple[str, list[bytes]]] = [
    ("WAV",  [b"RIFF"]),
    ("MP3",  [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"]),
    ("OGG",  [b"OggS"]),
    ("FLAC", [b"fLaC"]),
    # MP4 / M4A: ftyp box at byte 4
    ("MP4",  [b"\x00\x00\x00\x18ftyp", b"\x00\x00\x00\x1cftyp",
              b"\x00\x00\x00\x20ftyp", b"\x00\x00\x00\x1cftyp"]),
]


def _detect_format(header: bytes) -> str | None:
    """
    Return a format label if the magic bytes match a known audio format,
    or None if the bytes don't correspond to any supported format.
    Only the first 12 bytes are needed.
    """
    for label, prefixes in _MAGIC:
        for prefix in prefixes:
            if header[:len(prefix)] == prefix:
                return label
    # M4A/MP4 ftyp box can start at different offsets; check bytes 4–8
    if header[4:8] == b"ftyp":
        return "MP4"
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
):
    """
    Transcribe an uploaded audio file using Whisper.

    Validation order:
      1. MIME type must be in the explicit allowlist.
      2. File must not exceed MAX_AUDIO_BYTES.
      3. Magic bytes must match a supported audio format.
    All failures return HTTP 400 with a clear message.
    """
    # --- 1. MIME type allowlist check ---
    content_type = (file.content_type or "").lower().split(";")[0].strip()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported content type '{content_type}'. "
                f"Accepted types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            ),
        )

    # --- 2. Read file & enforce size limit ---
    audio_bytes = await file.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Audio file too large ({len(audio_bytes) // 1024 // 1024} MB). Maximum is 25 MB.",
        )

    # --- 3. Magic-byte validation ---
    detected = _detect_format(audio_bytes[:12])
    if detected is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file does not appear to be a valid audio file. "
                "Supported formats: WAV, MP3, OGG, FLAC, M4A/MP4. "
                "Please check the file and try again."
            ),
        )

    log.info(
        f"Audio upload accepted | file={file.filename!r} "
        f"mime={content_type} detected={detected} size={len(audio_bytes)} bytes"
    )

    # --- 4. Transcribe ---
    # Use the module-level singleton (Bug 8 fix — no per-request model loading)
    try:
        text = await _whisper_engine.transcribe(audio_bytes, language=language)
    except Exception as e:
        log.error(f"Whisper transcription failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Transcription failed. The audio may be corrupted or in an unsupported encoding.",
        )

    # Bug 7 fix: WhisperEngine returns a sentinel string when faster-whisper is
    # not installed. Surfacing a fake transcription as a success response is a
    # silent functional failure — return a 503 instead so callers know the
    # engine is non-functional.
    if text.startswith("__PLACEHOLDER__"):
        raise HTTPException(
            status_code=503,
            detail=(
                "Speech-to-text engine is not available. "
                "Install faster-whisper (uncomment it in requirements.txt) "
                "to enable real transcription."
            ),
        )

    return {"status": "success", "transcription": text, "language": language}


@router.post("/respond")
async def generate_voice_response(text: str, language: str = "en"):
    """
    Synthesise a voice response from text using XTTS.

    Bug 8 fix: uses the module-level singleton _xtts_engine instead of
    creating a new XTTSEngine (and loading the multi-GB model) per request.
    """
    if not _xtts_engine.is_available:
        raise HTTPException(
            status_code=503,
            detail=(
                "Text-to-speech engine is not available. "
                "Install the TTS library and ensure the model is loaded to enable this endpoint."
            ),
        )

    audio_bytes = await _xtts_engine.synthesize(text, language=language)

    if not audio_bytes:
        raise HTTPException(
            status_code=503,
            detail="TTS synthesis returned empty audio. The model may not be loaded correctly.",
        )

    return {
        "status": "success",
        "message": "Voice response generated",
        "audio_size": len(audio_bytes),
    }
