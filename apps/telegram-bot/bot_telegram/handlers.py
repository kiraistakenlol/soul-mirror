"""Telegram bot message handlers"""
import io
import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI

logger = logging.getLogger(__name__)


class TelegramHandlers:
    """Telegram bot message and command handlers"""

    def __init__(self, backend_url: str, openai_client: OpenAI, channel_storage):
        self.backend_url = backend_url
        self.openai_client = openai_client
        self.channel_storage = channel_storage

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "👋 Hi! I'm your Soul Mirror bot.\\n\\n"
            "Send me any message and I'll process it through your personal assistant.\\n\\n"
            "Commands:\\n"
            "/chatid - Show current chat ID\\n"
            "/channels - List discovered channels"
        )

    async def chatid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chatid command - shows the current chat ID"""
        message = update.message or update.channel_post
        if not message:
            return

        chat = message.chat
        chat_id = chat.id
        chat_type = chat.type
        chat_title = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))

        await message.reply_text(
            f"📋 Chat Information:\\n\\n"
            f"Chat ID: `{chat_id}`\\n"
            f"Type: {chat_type}\\n"
            f"Title: {chat_title}"
        )

    async def channels_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /channels command - lists all discovered channels"""
        message = update.message or update.channel_post
        if not message:
            return

        if self.channel_storage.count() == 0:
            await message.reply_text(
                "📭 No channels discovered yet.\\n\\n"
                "Post a message in a channel where I'm admin to discover it."
            )
            return

        lines = ["📡 Discovered Channels:\\n"]
        for channel in self.channel_storage.get_all():
            username_part = f" (@{channel['username']})" if channel.get('username') else ""
            lines.append(f"• {channel['title']}{username_part}")
            lines.append(f"  ID: `{channel['chat_id']}`")
            lines.append(f"  Type: {channel['type']}\\n")

        await message.reply_text("\\n".join(lines))

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages from users or channels"""
        # Support both direct messages and channel posts
        message = update.message or update.channel_post
        if not message:
            return

        user_text = message.text
        chat_id = message.chat_id
        chat = message.chat

        # Track channels automatically
        if chat.type in ['channel', 'supergroup']:
            self.channel_storage.add_channel(
                str(chat_id),
                chat.title,
                chat.type,
                getattr(chat, 'username', None)
            )

        logger.info(f"Received message from {chat_id}: {user_text[:50]}...")

        try:
            # Send to Soul Mirror backend
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/process",
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

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

            transcription = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcribed_text = transcription.text
            logger.info(f"Transcription: {transcribed_text[:50]}...")

            # Send to Soul Mirror backend
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/process",
                    json={"input": transcribed_text}
                )
                response.raise_for_status()
                result = response.json()

            # Reply back to Telegram
            soul_mirror_response = result.get("response", "No response received")
            await message.reply_text(f"🎤 \\\"{transcribed_text}\\\"\\n\\n{soul_mirror_response}")

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

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
