"""Telegram bot initialization and lifecycle"""
import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters

logger = logging.getLogger(__name__)


class TelegramBot:
    """Manages Telegram bot lifecycle"""

    def __init__(self, token: str, handlers):
        self.token = token
        self.handlers = handlers
        self.app: Optional[Application] = None

    async def start(self):
        """Initialize and start Telegram bot polling"""
        logger.info("Starting Telegram bot...")

        # Create application
        self.app = Application.builder().token(self.token).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.handlers.start_command))
        self.app.add_handler(CommandHandler("chatid", self.handlers.chatid_command))
        self.app.add_handler(CommandHandler("channels", self.handlers.channels_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text_message))
        self.app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, self.handlers.handle_text_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handlers.handle_voice_message))
        self.app.add_error_handler(self.handlers.error_handler)

        # Initialize and start polling
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        logger.info("✅ Telegram bot is running")

    async def stop(self):
        """Gracefully stop Telegram bot"""
        if self.app:
            logger.info("Stopping Telegram bot...")
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("✅ Telegram bot stopped")

    async def send_message(self, chat_id: str, text: str):
        """Send a message to a Telegram channel/chat"""
        if not self.app:
            raise RuntimeError("Telegram bot not initialized")

        return await self.app.bot.send_message(chat_id=chat_id, text=text)
