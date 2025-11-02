# Files repository - PostgreSQL data layer for file storage
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class FilesRepository:
    """PostgreSQL repository for generic file storage with metadata"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)

    def create_file(self, user_id: str, filename: str, content_type: str,
                   data: bytes, file_type: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> int:
        """Create new file"""
        import json
        size_bytes = len(data)
        metadata_json = json.dumps(metadata or {})

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO files
                    (user_id, filename, file_type, content_type, size_bytes, data, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id
                    """,
                    (user_id, filename, file_type, content_type, size_bytes, data, metadata_json)
                )
                file_id = cur.fetchone()[0]
                conn.commit()
                return file_id

    def get_file(self, file_id: int, user_id: str) -> Optional[Dict]:
        """Get file by id (with user isolation)"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, user_id, filename, file_type, content_type,
                           size_bytes, data, metadata, created_at, updated_at
                    FROM files
                    WHERE id = %s AND user_id = %s
                    """,
                    (file_id, user_id)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def list_files(self, user_id: str, file_type: Optional[str] = None) -> List[Dict]:
        """List all files for user (optionally filtered by file_type)"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if file_type:
                    cur.execute(
                        """
                        SELECT id, user_id, filename, file_type, content_type,
                               size_bytes, metadata, created_at, updated_at
                        FROM files
                        WHERE user_id = %s AND file_type = %s
                        ORDER BY created_at DESC
                        """,
                        (user_id, file_type)
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, user_id, filename, file_type, content_type,
                               size_bytes, metadata, created_at, updated_at
                        FROM files
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        """,
                        (user_id,)
                    )
                return [dict(row) for row in cur.fetchall()]

    def delete_file(self, file_id: int, user_id: str) -> bool:
        """Delete file (with user isolation)"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM files WHERE id = %s AND user_id = %s",
                    (file_id, user_id)
                )
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    def update_metadata(self, file_id: int, user_id: str, metadata: Dict) -> bool:
        """Update file metadata (with user isolation)"""
        import json
        metadata_json = json.dumps(metadata)

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE files
                    SET metadata = %s::jsonb
                    WHERE id = %s AND user_id = %s
                    """,
                    (metadata_json, file_id, user_id)
                )
                updated = cur.rowcount > 0
                conn.commit()
                return updated
