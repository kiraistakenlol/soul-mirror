import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import os

# PostgreSQL repository for notes
class NotesRepository:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is required")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    # Get or create note group
    def get_or_create_group(self, user_id: str, group_name: str) -> int:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO note_groups (user_id, name) VALUES (%s, %s) ON CONFLICT (user_id, name) DO UPDATE SET name = EXCLUDED.name RETURNING id",
                    (user_id, group_name)
                )
                result = cur.fetchone()
                conn.commit()
                return result['id']

    # Add note to group
    def add_note(self, user_id: str, group_id: int, content: str) -> int:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO notes (user_id, group_id, content) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, group_id, content)
                )
                result = cur.fetchone()
                conn.commit()
                return result['id']

    # Get all groups with notes for user
    def get_all_groups_with_notes(self, user_id: str) -> List[Dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name FROM note_groups WHERE user_id = %s ORDER BY created_at",
                    (user_id,)
                )
                groups = cur.fetchall()

                result = []
                for group in groups:
                    cur.execute(
                        "SELECT id, content, created_at FROM notes WHERE group_id = %s ORDER BY created_at",
                        (group['id'],)
                    )
                    notes = cur.fetchall()
                    result.append({
                        'id': group['id'],
                        'name': group['name'],
                        'notes': [{'id': n['id'], 'content': n['content'], 'created_at': str(n['created_at'])} for n in notes]
                    })

                return result

    # Get notes by group
    def get_notes_by_group(self, user_id: str, group_id: Optional[int] = None) -> List[Dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if group_id:
                    cur.execute(
                        "SELECT content FROM notes WHERE user_id = %s AND group_id = %s ORDER BY created_at",
                        (user_id, group_id)
                    )
                else:
                    cur.execute(
                        "SELECT content FROM notes WHERE user_id = %s ORDER BY created_at",
                        (user_id,)
                    )
                return [row['content'] for row in cur.fetchall()]

    # Update note
    def update_note(self, user_id: str, note_id: int, new_content: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE notes SET content = %s WHERE id = %s AND user_id = %s",
                    (new_content, note_id, user_id)
                )
                conn.commit()
                return cur.rowcount > 0

    # Delete note
    def delete_note(self, user_id: str, note_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM notes WHERE id = %s AND user_id = %s",
                    (note_id, user_id)
                )
                conn.commit()
                return cur.rowcount > 0

    # Delete all notes for user
    def delete_all_notes(self, user_id: str):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM notes WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM note_groups WHERE user_id = %s", (user_id,))
                conn.commit()

    # Create default note groups
    def create_default_groups(self, user_id: str, group_names: List[str]):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for name in group_names:
                    cur.execute(
                        "INSERT INTO note_groups (user_id, name) VALUES (%s, %s) ON CONFLICT (user_id, name) DO NOTHING",
                        (user_id, name)
                    )
                conn.commit()

    # Reset database schema and apply baseline
    def reset_database(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA public CASCADE")
                cur.execute("CREATE SCHEMA public")

                baseline_path = os.path.join(os.path.dirname(__file__), '..', 'baseline.sql')
                with open(baseline_path, 'r') as f:
                    baseline_sql = f.read()
                cur.execute(baseline_sql)

                conn.commit()
