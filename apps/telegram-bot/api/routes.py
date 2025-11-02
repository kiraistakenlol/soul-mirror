"""FastAPI routes for Soul Mirror agent integration"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class SendMessageRequest(BaseModel):
    chat_id: str
    message: str


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

    return router
