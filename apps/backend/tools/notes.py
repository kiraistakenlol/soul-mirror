# Notes management tool with groups organization
# Supports multiple users with isolated storage per user_id
from typing import Dict, Optional
from datetime import datetime
import uuid

class NotesManager:
    def __init__(self):
        # Store data per user: {user_id: {"groups": {...}, "notes": {...}}}
        self.user_data: Dict[str, Dict] = {}

    def _get_user_data(self, user_id: str) -> Dict:
        """Get data structure for specific user"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "groups": {},
                "notes": {}
            }
        return self.user_data[user_id]

    def list_groups(self, user_id: str) -> str:
        """List all groups with descriptions"""
        data = self._get_user_data(user_id)
        groups = data["groups"]

        if not groups:
            return "No groups found."

        result = []
        for group_id, group in groups.items():
            result.append(f"- [{group_id}] {group['name']}: {group['description']}")

        return "\n".join(result)

    def add_group(self, user_id: str, name: str, description: str) -> str:
        """Create a new group"""
        data = self._get_user_data(user_id)
        groups = data["groups"]

        # Check for duplicate names
        for group in groups.values():
            if group["name"].lower() == name.lower():
                return f"Group with name '{name}' already exists."

        group_id = str(uuid.uuid4())[:8]
        groups[group_id] = {
            "id": group_id,
            "name": name,
            "description": description,
            "created": datetime.now().isoformat()
        }
        return f"Created group [{group_id}] {name}"

    def remove_group(self, user_id: str, group_id: str) -> str:
        """Remove a group and all its notes"""
        data = self._get_user_data(user_id)
        groups = data["groups"]
        notes = data["notes"]

        if group_id not in groups:
            return f"Group {group_id} not found."

        # Remove all notes in this group
        notes_to_remove = [nid for nid, note in notes.items() if note.get("group_id") == group_id]
        for note_id in notes_to_remove:
            del notes[note_id]

        group_name = groups[group_id]["name"]
        del groups[group_id]
        return f"Removed group [{group_id}] {group_name} and {len(notes_to_remove)} notes"

    def list_notes(self, user_id: str, group_id: Optional[str] = None) -> str:
        """List all notes, optionally filtered by group"""
        data = self._get_user_data(user_id)
        notes = data["notes"]
        groups = data["groups"]

        if not notes:
            return "No notes found."

        result = []
        for note_id, note in notes.items():
            # Filter by group if specified
            if group_id and note.get("group_id") != group_id:
                continue

            # Get group name for display
            note_group_id = note.get("group_id")
            group_name = groups.get(note_group_id, {}).get("name", "unknown") if note_group_id else "ungrouped"

            result.append(f"- [{note_id}] {note['content']} (group: {group_name})")

        if not result:
            return f"No notes found in group {group_id}." if group_id else "No notes found."

        return "\n".join(result)

    def add_note(self, user_id: str, content: str, group_id: str) -> str:
        """Add a note to a specific group"""
        data = self._get_user_data(user_id)
        groups = data["groups"]
        notes = data["notes"]

        # Validate group exists
        if group_id not in groups:
            return f"Group {group_id} not found. Create it first with add_group."

        note_id = str(uuid.uuid4())[:8]
        notes[note_id] = {
            "id": note_id,
            "content": content,
            "group_id": group_id,
            "created": datetime.now().isoformat()
        }

        group_name = groups[group_id]["name"]
        return f"Added note [{note_id}] to group '{group_name}': {content}"

    def remove_note(self, user_id: str, note_id: str) -> str:
        """Remove a note by ID"""
        data = self._get_user_data(user_id)
        notes = data["notes"]

        if note_id not in notes:
            return f"Note {note_id} not found."

        content = notes[note_id]["content"]
        del notes[note_id]
        return f"Removed note [{note_id}]: {content}"

    def reset_user(self, user_id: str) -> None:
        """Clear all data for a user"""
        if user_id in self.user_data:
            self.user_data[user_id] = {
                "groups": {},
                "notes": {}
            }


# Global notes manager instance
notes_manager = NotesManager()