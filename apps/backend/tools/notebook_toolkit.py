# Notebook toolkit for organizing notes and groups
from typing import List
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from tools.notes import notes_manager

# Define tools that accept config parameter
@tool
def list_groups(config: RunnableConfig) -> str:
    """List all groups with their descriptions"""
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.list_groups(user_id)

@tool
def add_group(name: str, description: str, custom_rules: str = None, config: RunnableConfig = None) -> str:
    """Create a new group for organizing notes

    Args:
        name: Unique name for the group
        description: What this group is for
        custom_rules: Optional rules for how to manage notes in this group
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.add_group(user_id, name, description, custom_rules)

@tool
def remove_group(group_id: str, config: RunnableConfig) -> str:
    """Remove a group and all its notes

    Args:
        group_id: The ID of the group to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.remove_group(user_id, group_id)

@tool
def list_notes(group_id: str = None, config: RunnableConfig = None) -> str:
    """List all notes, optionally filtered by group

    Args:
        group_id: Optional group ID to filter notes
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    group_id_int = int(group_id) if group_id else None
    return notes_manager.list_notes(user_id, group_id_int)

@tool
def add_note(content: str, group_id: str, config: RunnableConfig) -> str:
    """Add a note to a specific group

    Args:
        content: The content of the note to add
        group_id: The ID of the group to add the note to
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.add_note(user_id, content, int(group_id))

@tool
def update_note(note_id: str, new_content: str, config: RunnableConfig) -> str:
    """Update an existing note's content

    Args:
        note_id: The ID of the note to update
        new_content: The new content for the note
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    if notes_manager.repo.update_note(user_id, int(note_id), new_content):
        return f"Updated note [{note_id}]"
    return f"Note {note_id} not found."

@tool
def remove_note(note_id: str, config: RunnableConfig) -> str:
    """Remove a note by its ID

    Args:
        note_id: The ID of the note to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.remove_note(user_id, int(note_id))


class NotebookToolkit(BaseToolkit):
    """Toolkit for managing notes and groups in a notebook"""

    def get_tools(self) -> List[BaseTool]:
        """Return list of all notebook tools"""
        return [
            list_groups,
            add_group,
            remove_group,
            list_notes,
            add_note,
            update_note,
            remove_note
        ]
