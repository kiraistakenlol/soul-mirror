#!/usr/bin/env python3
"""
Import notes and groups into Soul Mirror backend via HTTP API
"""

import json
import sys
from pathlib import Path
import httpx

BACKEND_URL = "http://localhost:8080"

IMPORT_DIR = Path(__file__).parent
GROUPS_FILE = IMPORT_DIR / "notes-groups.json"
MESSAGES_FILE = IMPORT_DIR / "messages_grouped.json"

def import_groups():
    """Import all groups"""
    print("📦 Importing groups...")

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    groups = data["groups"]

    for group in groups:
        response = httpx.post(
            f"{BACKEND_URL}/api/note-groups",
            json={
                "name": group["name"],
                "description": group["description"]
            },
            timeout=30.0
        )

        if response.status_code == 200:
            print(f"  ✓ {group['name']}")
        else:
            print(f"  ✗ Failed to create {group['name']}: {response.text}")
            sys.exit(1)

    print(f"✓ Imported {len(groups)} groups\n")

def import_messages():
    """Import all messages as notes"""
    print("📝 Importing messages...")

    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

    # Load groups to map IDs
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        groups_data = json.load(f)

    # Create mapping from group_id to group name
    group_map = {g["id"]: g["name"] for g in groups_data["groups"]}

    for i, msg in enumerate(messages, 1):
        group_name = group_map.get(msg["group_id"], "Unknown")

        # Use /api/process to add note via agent
        input_text = f"Add this note to group '{group_name}': {msg['message']}"

        response = httpx.post(
            f"{BACKEND_URL}/api/process",
            json={"input": input_text},
            timeout=30.0
        )

        if response.status_code == 200:
            print(f"  ✓ {i}/{len(messages)} - {msg['date'][:10]} → {group_name}")
        else:
            print(f"  ✗ Failed message {i}: {response.text}")
            sys.exit(1)

    print(f"\n✓ Imported {len(messages)} messages")

def main():
    print("🚀 Soul Mirror Import\n")

    # Check backend is running
    try:
        response = httpx.get(f"{BACKEND_URL}/api/status", timeout=5.0)
        if response.status_code != 200:
            print(f"❌ Backend not responding at {BACKEND_URL}")
            sys.exit(1)
    except Exception:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print(f"   Make sure backend is running: cd apps/backend && python main.py")
        sys.exit(1)

    # Import in order
    import_groups()
    import_messages()

    print("\n✅ Import complete!")

if __name__ == "__main__":
    main()
