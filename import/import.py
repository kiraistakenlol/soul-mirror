#!/usr/bin/env python3
"""Import messages from messages_grouped.json to Soul Mirror backend."""

import json
import httpx
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8080"
USER_ID = "default"

def main():
    # Load messages
    messages_file = Path(__file__).parent / "messages_grouped.json"
    with open(messages_file) as f:
        messages = json.load(f)

    print(f"Found {len(messages)} messages to import")

    # Submit each message
    for i, entry in enumerate(messages, 1):
        message = entry["message"]
        date = entry["date"]

        print(f"\n[{i}/{len(messages)}] Processing message from {date}")
        print(f"Preview: {message[:100]}...")

        try:
            response = httpx.post(
                f"{BACKEND_URL}/api/process",
                json={"input": message, "user_id": USER_ID},
                timeout=30.0
            )
            response.raise_for_status()

            result = response.json()
            print(f"✓ Success: {result.get('response', '')[:100]}")

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

        # Small delay to avoid overwhelming the server
        time.sleep(0.5)

    print(f"\n✓ Import complete: {len(messages)} messages processed")

if __name__ == "__main__":
    main()
