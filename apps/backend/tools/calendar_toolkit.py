# Calendar toolkit - agent's calendar management tools
from typing import List, Optional
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from tools.calendar import calendar_manager

@tool
def add_calendar_event(
    scheduled_time: str,
    recurrence: Optional[str] = None,
    responsibility_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    config: RunnableConfig = None
) -> str:
    """Schedule a calendar event

    Args:
        scheduled_time: When to trigger (format: "YYYY-MM-DD HH:MM" or "YYYY-MM-DD HH:MM:SS")
        recurrence: Optional recurrence pattern: 'daily', 'weekly', 'monthly', 'yearly', or None for one-time
        responsibility_id: The ID of the responsibility to execute (for recurring tasks)
        title: Short event title (for one-time tasks without responsibility)
        description: Detailed description (optional, for one-time tasks)

    Note: For recurring tasks, provide responsibility_id. For one-time tasks, provide title (and optionally description)
    """
    user_id = config.get("configurable", {}).get("user_id", "default")

    # Convert responsibility_id to int if provided
    resp_id = int(responsibility_id) if responsibility_id else None

    return calendar_manager.add_event(
        user_id,
        scheduled_time,
        recurrence,
        resp_id,
        title,
        description
    )

@tool
def list_calendar_events(config: RunnableConfig = None) -> str:
    """List all scheduled calendar events with next occurrence times"""
    user_id = config.get("configurable", {}).get("user_id", "default")
    return calendar_manager.list_events(user_id)

@tool
def remove_calendar_event(event_id: str, config: RunnableConfig = None) -> str:
    """Remove a scheduled calendar event

    Args:
        event_id: The ID of the event to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return calendar_manager.remove_event(user_id, int(event_id))


class CalendarToolkit(BaseToolkit):
    """Toolkit for managing calendar events"""

    def get_tools(self) -> List[BaseTool]:
        """Return list of all calendar tools"""
        return [
            add_calendar_event,
            list_calendar_events,
            remove_calendar_event
        ]
