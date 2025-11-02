# Calendar repository - PostgreSQL data layer for calendar events
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class CalendarRepository:
    """PostgreSQL repository for calendar events with icalendar data"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)

    def create_event(self, user_id: str, ical_data: str,
                    responsibility_id: Optional[int] = None,
                    title: Optional[str] = None,
                    description: Optional[str] = None) -> int:
        """Create new calendar event"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO calendar_events
                    (user_id, responsibility_id, title, description, ical_data)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, responsibility_id, title, description, ical_data)
                )
                event_id = cur.fetchone()[0]
                conn.commit()
                return event_id

    def get_all_events(self, user_id: str) -> List[Dict]:
        """Get all calendar events for a user"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        e.id,
                        e.user_id,
                        e.responsibility_id,
                        e.title,
                        e.description,
                        e.ical_data,
                        e.created_at,
                        e.updated_at,
                        r.title as responsibility_title,
                        r.description as responsibility_description
                    FROM calendar_events e
                    LEFT JOIN responsibilities r ON e.responsibility_id = r.id
                    WHERE e.user_id = %s
                    ORDER BY e.created_at DESC
                    """,
                    (user_id,)
                )
                return [dict(row) for row in cur.fetchall()]

    def get_event_by_id(self, user_id: str, event_id: int) -> Optional[Dict]:
        """Get specific calendar event"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        e.id,
                        e.user_id,
                        e.responsibility_id,
                        e.title,
                        e.description,
                        e.ical_data,
                        e.created_at,
                        e.updated_at,
                        r.title as responsibility_title,
                        r.description as responsibility_description
                    FROM calendar_events e
                    LEFT JOIN responsibilities r ON e.responsibility_id = r.id
                    WHERE e.user_id = %s AND e.id = %s
                    """,
                    (user_id, event_id)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def delete_event(self, user_id: str, event_id: int) -> bool:
        """Delete calendar event"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM calendar_events
                    WHERE user_id = %s AND id = %s
                    """,
                    (user_id, event_id)
                )
                conn.commit()
                return cur.rowcount > 0

    def delete_events_by_responsibility(self, user_id: str, responsibility_id: int) -> int:
        """Delete all events for a responsibility (cascade handled by FK)"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM calendar_events
                    WHERE user_id = %s AND responsibility_id = %s
                    """,
                    (user_id, responsibility_id)
                )
                deleted_count = cur.rowcount
                conn.commit()
                return deleted_count
