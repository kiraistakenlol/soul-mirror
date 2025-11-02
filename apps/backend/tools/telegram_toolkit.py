# Telegram toolkit - agent's Telegram channel integration tools
import os
import httpx
from typing import List
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

TELEGRAM_BOT_URL = os.getenv("TELEGRAM_BOT_URL", "http://localhost:8082")


@tool
def list_telegram_channels(config: RunnableConfig = None) -> str:
    """List all available Telegram channels that the bot can send messages to

    Returns a list of channels with their IDs, titles, and usernames.
    Use this to see what channels are available before sending messages.
    """
    try:
        response = httpx.get(f"{TELEGRAM_BOT_URL}/api/channels", timeout=10.0)
        response.raise_for_status()
        data = response.json()

        channels = data.get("channels", [])
        if not channels:
            return "No Telegram channels discovered yet. The bot needs to receive at least one message from each channel to discover it."

        result = ["Available Telegram channels:"]
        for ch in channels:
            username_part = f" (@{ch['username']})" if ch.get('username') else ""
            result.append(f"- {ch['title']}{username_part}")
            result.append(f"  ID: {ch['chat_id']}")
            result.append(f"  Type: {ch['type']}")

        return "\n".join(result)

    except httpx.HTTPError as e:
        return f"Error connecting to Telegram bot service: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool
def send_telegram_message(chat_id: str, message: str, config: RunnableConfig = None) -> str:
    """Send a message to a Telegram channel

    Args:
        chat_id: The Telegram chat/channel ID (get from list_telegram_channels)
        message: The message text to send

    Returns confirmation of message sent or error details.
    """
    try:
        response = httpx.post(
            f"{TELEGRAM_BOT_URL}/api/send-message",
            json={"chat_id": chat_id, "message": message},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        return f"Message sent successfully to chat {chat_id} (message_id: {data.get('message_id')})"

    except httpx.HTTPError as e:
        if e.response is not None:
            error_detail = e.response.json().get("detail", str(e))
            return f"Error sending message: {error_detail}"
        return f"Error connecting to Telegram bot service: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


class TelegramToolkit(BaseToolkit):
    """Toolkit for Telegram channel integration"""

    def get_tools(self) -> List[BaseTool]:
        return [
            list_telegram_channels,
            send_telegram_message
        ]
