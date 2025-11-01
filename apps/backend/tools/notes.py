# Notes management tool with PostgreSQL storage
from typing import Optional
from repository.notes import NotesRepository

class NotesManager:
    def __init__(self):
        self.repo = NotesRepository()

    def list_groups(self, user_id: str) -> str:
        """List all groups with descriptions and rules"""
        print(f"    🔧 list_groups(user={user_id})")
        groups = self.repo.get_all_groups_with_notes(user_id)

        if not groups:
            print(f"    ↳ No groups found")
            return "No groups found."

        result = []
        for group in groups:
            note_count = len(group['notes'])
            group_info = f"- [{group['id']}] {group['name']}: {group['description']} ({note_count} notes, created: {group['created_at']}, updated: {group['updated_at']})"
            if group['custom_rules']:
                group_info += f"\n  Rules: {group['custom_rules']}"
            result.append(group_info)

        print(f"    ↳ Found {len(groups)} groups")
        return "\n".join(result)

    def add_group(self, user_id: str, name: str, description: str, custom_rules: Optional[str] = None) -> str:
        """Create a new group"""
        print(f"    🔧 add_group(user={user_id}, name=\"{name}\")")
        try:
            group_id = self.repo.get_or_create_group(user_id, name, description, custom_rules)
            print(f"    ↳ Created group [{group_id}]")
            return f"Created group [{group_id}] {name}"
        except Exception as e:
            if "duplicate" in str(e).lower():
                print(f"    ↳ Group already exists")
                return f"Group with name '{name}' already exists."
            raise

    def remove_group(self, user_id: str, group_id: int) -> str:
        """Remove a group and all its notes (cascade handled by DB)"""
        print(f"    🔧 remove_group(user={user_id}, group={group_id})")
        if self.repo.delete_group(user_id, group_id):
            print(f"    ↳ Deleted group [{group_id}]")
            return f"Deleted group [{group_id}]"
        print(f"    ↳ Group not found")
        return f"Group {group_id} not found."

    def list_notes(self, user_id: str, group_id: Optional[int] = None) -> str:
        """List all notes with IDs, optionally filtered by group"""
        print(f"    🔧 list_notes(user={user_id}, group={group_id or 'all'})")

        groups = self.repo.get_all_groups_with_notes(user_id)
        if not groups:
            print(f"    ↳ No notes found")
            return "No notes found."

        # Filter to specific group if requested
        if group_id:
            groups = [g for g in groups if g['id'] == group_id]
            if not groups:
                print(f"    ↳ No notes in group")
                return f"No notes in group {group_id}."

        result = []
        total_notes = 0
        for group in groups:
            if group['notes']:
                for note in group['notes']:
                    result.append(f"- [{note['id']}] {note['content']} (created: {note['created_at']}, updated: {note['updated_at']})")
                    total_notes += 1

        if not result:
            print(f"    ↳ No notes found")
            return "No notes in group." if group_id else "No notes found."

        print(f"    ↳ Found {total_notes} notes")
        return "\n".join(result)

    def add_note(self, user_id: str, content: str, group_id: int) -> str:
        """Add a note to a specific group"""
        print(f"    🔧 add_note(user={user_id}, group={group_id}, content=\"{content[:40]}...\")")
        note_id = self.repo.add_note(user_id, group_id, content)
        print(f"    ↳ Created note [{note_id}]")
        return f"Added note [{note_id}] to group {group_id}: {content}"

    def remove_note(self, user_id: str, note_id: int) -> str:
        """Remove a note by ID"""
        print(f"    🔧 remove_note(user={user_id}, note={note_id})")
        if self.repo.delete_note(user_id, note_id):
            print(f"    ↳ Removed note [{note_id}]")
            return f"Removed note [{note_id}]"
        print(f"    ↳ Note not found")
        return f"Note {note_id} not found."

    def search_notes(self, user_id: str, query: str) -> str:
        """Search notes by keyword across all groups"""
        print(f"    🔧 search_notes(user={user_id}, query=\"{query}\")")
        groups = self.repo.get_all_groups_with_notes(user_id)

        if not groups:
            print(f"    ↳ No notes to search")
            return "No notes found."

        query_lower = query.lower()
        results = []

        for group in groups:
            for note in group['notes']:
                if query_lower in note['content'].lower():
                    results.append(f"- [{note['id']}] {note['content']} (in {group['name']})")

        if not results:
            print(f"    ↳ No matches found")
            return f"No notes matching '{query}'."

        print(f"    ↳ Found {len(results)} matches")
        return "\n".join(results)

    def move_note(self, user_id: str, note_id: int, new_group_id: int) -> str:
        """Move a note to a different group"""
        print(f"    🔧 move_note(user={user_id}, note={note_id}, new_group={new_group_id})")
        if self.repo.move_note(user_id, note_id, new_group_id):
            print(f"    ↳ Moved note [{note_id}] to group [{new_group_id}]")
            return f"Moved note [{note_id}] to group {new_group_id}"
        print(f"    ↳ Note or group not found")
        return f"Could not move note {note_id} to group {new_group_id}."

    def get_groups_count(self, user_id: str) -> str:
        """Get total number of groups"""
        print(f"    🔧 get_groups_count(user={user_id})")
        groups = self.repo.get_all_groups_with_notes(user_id)
        count = len(groups)
        print(f"    ↳ {count} groups")
        return f"Total groups: {count}"

    def reset_user(self, user_id: str) -> None:
        """Clear all data for a user"""
        self.repo.delete_all_notes(user_id)

    def _get_user_data(self, user_id: str):
        """Legacy method for compatibility with main.py - returns groups dict"""
        groups = self.repo.get_all_groups_with_notes(user_id)
        # Convert to old format: {group_id: {name, description, custom_rules, notes: {note_id: {content, ...}}}}
        result = {}
        for group in groups:
            notes_dict = {}
            for note in group['notes']:
                notes_dict[str(note['id'])] = {
                    'id': note['id'],
                    'content': note['content'],
                    'created': note['created_at'],
                    'updated': note['updated_at']
                }
            result[str(group['id'])] = {
                'id': group['id'],
                'name': group['name'],
                'description': group['description'],
                'custom_rules': group['custom_rules'],
                'created': group['created_at'],
                'updated': group['updated_at'],
                'notes': notes_dict
            }
        return result


# Global notes manager instance
notes_manager = NotesManager()
