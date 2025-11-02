"""Persistent channel storage"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ChannelStorage:
    """Manages persistent storage of discovered Telegram channels"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.channels = {}

    def load(self):
        """Load discovered channels from JSON file"""
        try:
            channels_path = Path(self.file_path)
            if channels_path.exists():
                with open(channels_path, 'r') as f:
                    self.channels = json.load(f)
                logger.info(f"📂 Loaded {len(self.channels)} channels from {self.file_path}")
            else:
                logger.info(f"📂 No existing channels file, starting fresh")
                self.channels = {}
        except Exception as e:
            logger.error(f"❌ Error loading channels: {e}")
            self.channels = {}

    def save(self):
        """Save discovered channels to JSON file (atomic write)"""
        try:
            # Ensure data directory exists
            channels_path = Path(self.file_path)
            channels_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write: write to temp file then rename
            temp_path = channels_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self.channels, f, indent=2)
            temp_path.rename(channels_path)

            logger.info(f"💾 Saved {len(self.channels)} channels to {self.file_path}")
        except Exception as e:
            logger.error(f"❌ Error saving channels: {e}")

    def add_channel(self, chat_id: str, title: str, channel_type: str, username: str = None):
        """Add or update a channel"""
        if chat_id not in self.channels:
            self.channels[chat_id] = {
                "title": title,
                "type": channel_type,
                "username": username
            }
            self.save()
            logger.info(f"📍 Discovered new channel: {title} (ID: {chat_id})")
            return True
        return False

    def get_all(self):
        """Get all channels as list"""
        return [
            {
                "chat_id": chat_id,
                "title": info["title"],
                "type": info["type"],
                "username": info.get("username")
            }
            for chat_id, info in self.channels.items()
        ]

    def count(self):
        """Get number of discovered channels"""
        return len(self.channels)
