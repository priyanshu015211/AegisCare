"""
backend/voice/tts/xtts_engine.py
Placeholder version (for deployment)
"""

from backend.core.logging import get_logger

log = get_logger(__name__)

class XTTSEngine:
    def __init__(self):
        log.warning("TTS is disabled in this deployment (placeholder mode)")

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        # Return empty bytes as placeholder
        return b""
