# Notes management tool with three methods: list, add, remove
# Supports multiple users with isolated note storage per user_id
from typing import Dict
from datetime import datetime
import uuid

class NotesManager:
    def __init__(self):
        # Store notes per user: {user_id: {note_id: note}}
        self.user_notes: Dict[str, Dict[str, Dict]] = {}

    def _get_user_notes(self, user_id: str) -> Dict[str, Dict]:
        """Get notes for specific user"""
        if user_id not in self.user_notes:
            self.user_notes[user_id] = {}
        return self.user_notes[user_id]

    def list_notes(self, user_id: str) -> str:
        """List all notes for a user"""
        notes = self._get_user_notes(user_id)
        if not notes:
            return "No notes found."

        result = []
        for note_id, note in notes.items():
            result.append(f"- [{note_id}] {note['content']} (created: {note['created']})")

        return "\n".join(result)

    def add_note(self, user_id: str, content: str) -> str:
        """Add a new note for a user"""
        notes = self._get_user_notes(user_id)
        note_id = str(uuid.uuid4())[:8]
        notes[note_id] = {
            "id": note_id,
            "content": content,
            "created": datetime.now().isoformat()
        }
        return f"Added note [{note_id}]: {content}"

    def remove_note(self, user_id: str, note_id: str) -> str:
        """Remove a note by ID for a user"""
        notes = self._get_user_notes(user_id)
        if note_id not in notes:
            return f"Note {note_id} not found."

        content = notes[note_id]["content"]
        del notes[note_id]
        return f"Removed note [{note_id}]: {content}"

    def reset_user(self, user_id: str) -> None:
        """Clear all notes for a user"""
        if user_id in self.user_notes:
            self.user_notes[user_id] = {}


# Global notes manager instance
notes_manager = NotesManager()