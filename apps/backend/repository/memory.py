import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import os

# PostgreSQL repository for core memory
class MemoryRepository:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is required")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    # Get core memory
    def get_memory(self, user_id: str) -> Optional[str]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT content FROM core_memory WHERE user_id = %s",
                    (user_id,)
                )
                result = cur.fetchone()
                return result['content'] if result else None

    # Update core memory (creates if doesn't exist)
    def update_memory(self, user_id: str, content: str) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core_memory (user_id, content)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET content = EXCLUDED.content
                    """,
                    (user_id, content)
                )
                conn.commit()

    # Clear all core memory
    def clear_memory(self, user_id: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM core_memory WHERE user_id = %s",
                    (user_id,)
                )
                conn.commit()
                return cur.rowcount > 0
