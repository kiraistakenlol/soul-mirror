# Responsibilities toolkit - agent's internal workflow management
from typing import List
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from tools.responsibilities import responsibilities_manager

@tool
def list_responsibilities(config: RunnableConfig = None) -> str:
    """List all responsibilities (workflows, tasks)"""
    user_id = config.get("configurable", {}).get("user_id", "default")
    return responsibilities_manager.list_responsibilities(user_id)

@tool
def add_responsibility(title: str, description: str, config: RunnableConfig = None) -> str:
    """Create a new responsibility (workflow, recurring task, etc)

    Args:
        title: Short title for the responsibility
        description: Detailed description of what needs to be done, when, how, etc
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return responsibilities_manager.add_responsibility(user_id, title, description)

@tool
def update_responsibility(responsibility_id: str, title: str = None,
                         description: str = None, config: RunnableConfig = None) -> str:
    """Update an existing responsibility

    Args:
        responsibility_id: The ID of the responsibility to update
        title: New title (optional)
        description: New description (optional)
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return responsibilities_manager.update_responsibility(
        user_id, int(responsibility_id), title, description
    )

@tool
def remove_responsibility(responsibility_id: str, config: RunnableConfig = None) -> str:
    """Remove a responsibility

    Args:
        responsibility_id: The ID of the responsibility to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return responsibilities_manager.remove_responsibility(user_id, int(responsibility_id))


class ResponsibilitiesToolkit(BaseToolkit):
    """Toolkit for managing agent's internal responsibilities and workflows"""

    def get_tools(self) -> List[BaseTool]:
        """Return list of all responsibilities tools"""
        return [
            list_responsibilities,
            add_responsibility,
            update_responsibility,
            remove_responsibility
        ]
