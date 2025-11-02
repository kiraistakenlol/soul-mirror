"""FastAPI routes for Soul Mirror agent integration"""
import logging
import base64
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class SendMessageRequest(BaseModel):
    chat_id: str
    message: str


class SendAudioRequest(BaseModel):
    chat_id: str
    audio_base64: str
    filename: str = "audio.mp3"
    caption: Optional[str] = None


def create_routes(telegram_bot, channel_storage):
    """Create API routes with dependencies"""

    @router.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "telegram_bot_running": telegram_bot.app is not None,
            "discovered_channels": channel_storage.count()
        }

    @router.get("/channels")
    async def get_channels():
        """List all discovered Telegram channels"""
        return {
            "channels": channel_storage.get_all()
        }

    @router.post("/send-message")
    async def send_message(request: SendMessageRequest):
        """Send a message to a Telegram channel/chat"""
        if not telegram_bot.app:
            raise HTTPException(status_code=503, detail="Telegram bot not initialized")

        try:
            sent = await telegram_bot.send_message(
                chat_id=request.chat_id,
                text=request.message
            )

            logger.info(f"✉️  Sent message to {request.chat_id}: {request.message[:50]}...")

            return {
                "status": "success",
                "message_id": sent.message_id,
                "chat_id": request.chat_id
            }
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/send-audio")
    async def send_audio(request: SendAudioRequest):
        """Send an audio file to a Telegram channel/chat"""
        if not telegram_bot.app:
            raise HTTPException(status_code=503, detail="Telegram bot not initialized")

        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(request.audio_base64)

            # Send audio
            sent = await telegram_bot.send_audio(
                chat_id=request.chat_id,
                audio_bytes=audio_bytes,
                filename=request.filename,
                caption=request.caption
            )

            logger.info(f"🔊 Sent audio to {request.chat_id}: {request.filename}" +
                       (f" with caption: {request.caption[:50]}..." if request.caption else ""))

            return {
                "status": "success",
                "message_id": sent.message_id,
                "chat_id": request.chat_id,
                "filename": request.filename
            }
        except base64.binascii.Error as e:
            logger.error(f"❌ Invalid base64 audio data: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error sending audio: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
