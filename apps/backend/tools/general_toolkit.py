# General toolkit - utility tools for agent
from typing import List
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
def get_current_datetime(config: RunnableConfig) -> str:
    """Get the current date and time"""
    from datetime import datetime
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A, %B %d, %Y at %I:%M %p')})"


class GeneralToolkit(BaseToolkit):
    """Toolkit for general utility tools"""

    def get_tools(self) -> List[BaseTool]:
        """Return list of general utility tools"""
        return [
            get_current_datetime
        ]
