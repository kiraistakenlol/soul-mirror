import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import os

# PostgreSQL repository for responsibilities
class ResponsibilitiesRepository:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is required")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    # Create responsibility
    def create_responsibility(self, user_id: str, title: str, description: str) -> int:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO responsibilities (user_id, title, description) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, title, description)
                )
                result = cur.fetchone()
                conn.commit()
                return result['id']

    # Get all responsibilities for user
    def get_all_responsibilities(self, user_id: str) -> List[Dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, title, description, created_at, updated_at
                       FROM responsibilities
                       WHERE user_id = %s
                       ORDER BY created_at DESC""",
                    (user_id,)
                )
                rows = cur.fetchall()
                return [dict(row) for row in rows]

    # Update responsibility
    def update_responsibility(self, user_id: str, responsibility_id: int,
                            title: Optional[str] = None, description: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []

                if title is not None:
                    updates.append("title = %s")
                    params.append(title)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)

                if not updates:
                    return False

                params.extend([responsibility_id, user_id])
                query = f"UPDATE responsibilities SET {', '.join(updates)} WHERE id = %s AND user_id = %s"

                cur.execute(query, params)
                conn.commit()
                return cur.rowcount > 0

    # Delete responsibility
    def delete_responsibility(self, user_id: str, responsibility_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM responsibilities WHERE id = %s AND user_id = %s",
                    (responsibility_id, user_id)
                )
                conn.commit()
                return cur.rowcount > 0

    # Get single responsibility
    def get_responsibility(self, user_id: str, responsibility_id: int) -> Optional[Dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, title, description, created_at, updated_at
                       FROM responsibilities
                       WHERE id = %s AND user_id = %s""",
                    (responsibility_id, user_id)
                )
                result = cur.fetchone()
                return dict(result) if result else None
