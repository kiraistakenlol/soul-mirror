"""
Telegram bot service with dual functionality:
1. Telegram polling - receives messages from channels/users
2. FastAPI HTTP server - provides API for Soul Mirror agent to send messages
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from openai import OpenAI
import uvicorn

from storage import ChannelStorage
from bot_telegram import TelegramBot, TelegramHandlers
from api import create_routes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", "8082"))
CHANNELS_FILE = os.getenv("CHANNELS_FILE", "./data/channels.json")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize components
openai_client = OpenAI(api_key=OPENAI_API_KEY)
channel_storage = ChannelStorage(CHANNELS_FILE)
handlers = TelegramHandlers(BACKEND_URL, openai_client, channel_storage)
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, handlers)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting FastAPI service...")
    channel_storage.load()
    await telegram_bot.start()
    yield
    # Shutdown
    logger.info("🛑 Shutting down FastAPI service...")
    await telegram_bot.stop()


# Create FastAPI app
fastapi_app = FastAPI(title="Telegram Bot Service", lifespan=lifespan)

# Register API routes
api_router = create_routes(telegram_bot, channel_storage)
fastapi_app.include_router(api_router)


if __name__ == "__main__":
    logger.info(f"🤖 Telegram Bot Service starting on port {PORT}")
    logger.info(f"📂 Channels file: {CHANNELS_FILE}")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
