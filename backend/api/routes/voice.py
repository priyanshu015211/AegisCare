from fastapi import APIRouter, UploadFile, File, Form
from backend.voice.stt.whisper_engine import WhisperEngine
from backend.voice.tts.xtts_engine import XTTSEngine
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])

whisper_engine = WhisperEngine()
xtts_engine = XTTSEngine()


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    audio_bytes = await file.read()
    text = await whisper_engine.transcribe(audio_bytes, language=language)
    return {"status": "success", "transcription": text, "language": language}


@router.post("/respond")
async def generate_voice_response(text: str, language: str = "en"):
    audio_bytes = await xtts_engine.synthesize(text, language=language)
    return {
        "status": "success",
        "message": "Voice response generated",
        "audio_size": len(audio_bytes)
    }
