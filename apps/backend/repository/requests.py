import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict
import os

# PostgreSQL repository for request logging
class RequestsRepository:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is required")

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    # Log request to database
    def log_request(self, user_id: str, input_text: str) -> int:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO requests (user_id, input) VALUES (%s, %s) RETURNING id",
                    (user_id, input_text)
                )
                result = cur.fetchone()
                conn.commit()
                return result['id']

    # Update request with response and LLM traces
    def update_request_response(self, request_id: int, response: str, llm_traces: List[Dict] = None):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if llm_traces:
                    import json
                    cur.execute(
                        "UPDATE requests SET response = %s, llm_traces = %s WHERE id = %s",
                        (response, json.dumps(llm_traces), request_id)
                    )
                else:
                    cur.execute(
                        "UPDATE requests SET response = %s WHERE id = %s",
                        (response, request_id)
                    )
                conn.commit()

    # Get recent requests for user
    def get_recent_requests(self, user_id: str, limit: int = 100) -> List[Dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, input, response, llm_traces, created_at FROM requests WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                    (user_id, limit)
                )
                return cur.fetchall()