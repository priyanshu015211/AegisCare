from fastapi import APIRouter, UploadFile, File
from backend.voice.stt.whisper_engine import WhisperEngine
from backend.voice.tts.xtts_engine import XTTSEngine

router = APIRouter(prefix="/voice", tags=["Voice"])
whisper = WhisperEngine()
xtts = XTTSEngine()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio = await file.read()
    text = await whisper.transcribe(audio)
    return {"transcription": text}

@router.post("/respond")
async def respond(text: str):
    audio = await xtts.synthesize(text)
    return {"message": "Voice response generated (placeholder)"}
