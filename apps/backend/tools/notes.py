# Notes management tool with PostgreSQL storage
from typing import Optional
from repository.notes import NotesRepository

class NotesManager:
    def __init__(self):
        self.repo = NotesRepository()

    def list_groups(self, user_id: str) -> str:
        """List all groups with descriptions"""
        groups = self.repo.get_all_groups_with_notes(user_id)

        if not groups:
            return "No groups found."

        result = []
        for group in groups:
            note_count = len(group['notes'])
            result.append(f"- [{group['id']}] {group['name']} ({note_count} notes)")

        return "\n".join(result)

    def add_group(self, user_id: str, name: str, description: str = "") -> str:
        """Create a new group"""
        try:
            group_id = self.repo.get_or_create_group(user_id, name)
            return f"Created group [{group_id}] {name}"
        except Exception as e:
            if "duplicate" in str(e).lower():
                return f"Group with name '{name}' already exists."
            raise

    def remove_group(self, user_id: str, group_id: str) -> str:
        """Remove a group and all its notes (cascade handled by DB)"""
        # Note: In current implementation, we don't have a delete_group method
        # Groups are removed when all notes are deleted due to cascade
        return "Group removal not implemented yet"

    def list_notes(self, user_id: str, group_id: Optional[int] = None) -> str:
        """List all notes, optionally filtered by group"""
        if group_id:
            notes = self.repo.get_notes_by_group(user_id, group_id)
            if not notes:
                return f"No notes in group {group_id}."
            return "\n".join([f"- {note}" for note in notes])

        groups = self.repo.get_all_groups_with_notes(user_id)
        if not groups:
            return "No notes found."

        result = []
        for group in groups:
            if group['notes']:
                result.append(f"\n{group['name']}:")
                for note in group['notes']:
                    result.append(f"  - [{note['id']}] {note['content']}")

        if not result:
            return "No notes found."

        return "\n".join(result)

    def add_note(self, user_id: str, content: str, group_id: int) -> str:
        """Add a note to a specific group"""
        note_id = self.repo.add_note(user_id, group_id, content)
        return f"Added note [{note_id}] to group {group_id}: {content}"

    def remove_note(self, user_id: str, note_id: int) -> str:
        """Remove a note by ID"""
        if self.repo.delete_note(user_id, note_id):
            return f"Removed note [{note_id}]"
        return f"Note {note_id} not found."

    def reset_user(self, user_id: str) -> None:
        """Clear all data for a user"""
        self.repo.delete_all_notes(user_id)

    def _get_user_data(self, user_id: str):
        """Legacy method for compatibility with main.py - returns groups dict"""
        groups = self.repo.get_all_groups_with_notes(user_id)
        # Convert to old format: {group_id: {name, notes: {note_id: {content, ...}}}}
        result = {}
        for group in groups:
            notes_dict = {}
            for note in group['notes']:
                notes_dict[str(note['id'])] = {
                    'id': note['id'],
                    'content': note['content'],
                    'created': note['created_at']
                }
            result[str(group['id'])] = {
                'id': group['id'],
                'name': group['name'],
                'notes': notes_dict
            }
        return result


# Global notes manager instance
notes_manager = NotesManager()
