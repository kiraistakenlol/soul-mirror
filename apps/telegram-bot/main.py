"""
Telegram bot that forwards messages to Soul Mirror backend and relays responses.
"""
import os
import logging
import io
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import httpx
from openai import OpenAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Hi! I'm your Soul Mirror bot.\n\n"
        "Send me any message and I'll process it through your personal assistant.\n\n"
        "Your chat_id is your unique user_id in the system."
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users or channels"""
    # Support both direct messages and channel posts
    message = update.message or update.channel_post
    if not message:
        return

    user_text = message.text
    chat_id = message.chat_id

    logger.info(f"Received message from {chat_id}: {user_text[:50]}...")

    try:
        # Send to Soul Mirror backend
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/api/process",
                json={"input": user_text}
            )
            response.raise_for_status()
            result = response.json()

        # Reply back to Telegram
        soul_mirror_response = result.get("response", "No response received")
        await message.reply_text(soul_mirror_response)

        logger.info(f"Sent response to {chat_id}")

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        await message.reply_text(
            "⚠️ Sorry, I couldn't connect to the backend service. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.reply_text(
            "⚠️ An error occurred while processing your message."
        )


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages from users or channels"""
    message = update.message or update.channel_post
    if not message or not message.voice:
        return

    chat_id = message.chat_id
    logger.info(f"Received voice message from {chat_id}")

    try:
        # Download voice file
        voice_file = await message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()

        # Transcribe using OpenAI Whisper
        logger.info("Transcribing voice message...")
        audio_file = io.BytesIO(voice_bytes)
        audio_file.name = "voice.ogg"

        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        transcribed_text = transcription.text
        logger.info(f"Transcription: {transcribed_text[:50]}...")

        # Send to Soul Mirror backend
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/api/process",
                json={"input": transcribed_text}
            )
            response.raise_for_status()
            result = response.json()

        # Reply back to Telegram
        soul_mirror_response = result.get("response", "No response received")
        await message.reply_text(f"🎤 \"{transcribed_text}\"\n\n{soul_mirror_response}")

        logger.info(f"Sent response to {chat_id}")

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        await message.reply_text(
            "⚠️ Sorry, I couldn't connect to the backend service. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.reply_text(
            "⚠️ An error occurred while processing your voice message."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    logger.info("Starting Telegram bot...")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    # Handle text from direct messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    # Handle text from channel posts
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, handle_text_message))
    # Handle voice messages
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_error_handler(error_handler)

    # Start polling
    logger.info("Bot is running. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
