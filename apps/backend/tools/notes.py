# Notes management tool with groups organization
# Supports multiple users with isolated storage per user_id
from typing import Dict, Optional
from datetime import datetime
import uuid

class NotesManager:
    def __init__(self):
        # Store groups per user with nested notes: {user_id: {group_id: {name, description, notes: {...}}}}
        self.user_data: Dict[str, Dict] = {}

    def _get_user_data(self, user_id: str) -> Dict:
        """Get groups structure for specific user"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        return self.user_data[user_id]

    def list_groups(self, user_id: str) -> str:
        """List all groups with descriptions"""
        groups = self._get_user_data(user_id)

        if not groups:
            return "No groups found."

        result = []
        for group_id, group in groups.items():
            note_count = len(group.get("notes", {}))
            result.append(f"- [{group_id}] {group['name']}: {group['description']} ({note_count} notes)")

        return "\n".join(result)

    def add_group(self, user_id: str, name: str, description: str) -> str:
        """Create a new group"""
        groups = self._get_user_data(user_id)

        # Check for duplicate names
        for group in groups.values():
            if group["name"].lower() == name.lower():
                return f"Group with name '{name}' already exists."

        group_id = str(uuid.uuid4())[:8]
        groups[group_id] = {
            "id": group_id,
            "name": name,
            "description": description,
            "notes": {},
            "created": datetime.now().isoformat()
        }
        return f"Created group [{group_id}] {name}"

    def remove_group(self, user_id: str, group_id: str) -> str:
        """Remove a group and all its notes"""
        groups = self._get_user_data(user_id)

        if group_id not in groups:
            return f"Group {group_id} not found."

        group = groups[group_id]
        note_count = len(group.get("notes", {}))
        group_name = group["name"]

        del groups[group_id]
        return f"Removed group [{group_id}] {group_name} and {note_count} notes"

    def list_notes(self, user_id: str, group_id: Optional[str] = None) -> str:
        """List all notes, optionally filtered by group"""
        groups = self._get_user_data(user_id)

        if not groups:
            return "No notes found."

        result = []

        # If specific group requested
        if group_id:
            if group_id not in groups:
                return f"Group {group_id} not found."

            group = groups[group_id]
            notes = group.get("notes", {})

            if not notes:
                return f"No notes in group {group['name']}."

            for note_id, note in notes.items():
                result.append(f"- [{note_id}] {note['content']}")

            return f"Notes in {group['name']}:\n" + "\n".join(result)

        # List all notes across all groups
        for group_id, group in groups.items():
            notes = group.get("notes", {})
            if notes:
                result.append(f"\n{group['name']}:")
                for note_id, note in notes.items():
                    result.append(f"  - [{note_id}] {note['content']}")

        if not result:
            return "No notes found."

        return "\n".join(result)

    def add_note(self, user_id: str, content: str, group_id: str) -> str:
        """Add a note to a specific group"""
        groups = self._get_user_data(user_id)

        # Validate group exists
        if group_id not in groups:
            return f"Group {group_id} not found. Create it first with add_group."

        group = groups[group_id]
        notes = group.get("notes", {})

        note_id = str(uuid.uuid4())[:8]
        notes[note_id] = {
            "id": note_id,
            "content": content,
            "created": datetime.now().isoformat()
        }

        group["notes"] = notes
        return f"Added note [{note_id}] to group '{group['name']}': {content}"

    def remove_note(self, user_id: str, note_id: str) -> str:
        """Remove a note by ID"""
        groups = self._get_user_data(user_id)

        # Search for note across all groups
        for group_id, group in groups.items():
            notes = group.get("notes", {})
            if note_id in notes:
                content = notes[note_id]["content"]
                del notes[note_id]
                return f"Removed note [{note_id}]: {content}"

        return f"Note {note_id} not found."

    def reset_user(self, user_id: str) -> None:
        """Clear all data for a user"""
        if user_id in self.user_data:
            self.user_data[user_id] = {}


# Global notes manager instance
notes_manager = NotesManager()