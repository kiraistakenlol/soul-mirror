# Memory toolkit - agent's long-term understanding of user
from typing import List
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from tools.memory import memory_manager

@tool
def update_core_memory(new_content: str, config: RunnableConfig) -> str:
    """Update core memory with new understanding or important information

    Args:
        new_content: Complete updated core memory content incorporating new information
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return memory_manager.update_core_memory(user_id, new_content)


class MemoryToolkit(BaseToolkit):
    """Toolkit for managing agent's long-term memory"""

    def get_tools(self) -> List[BaseTool]:
        """Return list of all memory tools"""
        return [
            update_core_memory
        ]
