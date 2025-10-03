# FastAPI server for Soul Mirror backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
import uvicorn
from dotenv import load_dotenv
from pathlib import Path

from agent import Agent
from tools.notes import notes_manager

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Soul Mirror Backend", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = Agent()

# Request/Response models
class ProcessRequest(BaseModel):
    input: str
    user_id: Optional[str] = "default"

class ProcessResponse(BaseModel):
    input: str
    response: str
    user_id: str

class NoteGroupRequest(BaseModel):
    name: str
    description: str
    user_id: Optional[str] = "default"

# API Endpoints
@app.get("/api/status")
def get_status():
    """System health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agent": "langgraph",
        "tools": ["list_groups", "add_group", "remove_group", "list_notes", "add_note", "remove_note"]
    }

@app.get("/api/process")
def process_get(input: str, user_id: str = "default"):
    """Process input via GET request"""
    try:
        response = agent.process_input(input, user_id)
        return ProcessResponse(
            input=input,
            response=response,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
def process_post(request: ProcessRequest):
    """Process input via POST request"""
    try:
        response = agent.process_input(request.input, request.user_id)
        return ProcessResponse(
            input=request.input,
            response=response,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/note-groups")
def create_note_group(request: NoteGroupRequest):
    """Create a note group directly without agent processing"""
    try:
        result = notes_manager.add_group(request.user_id, request.name, request.description)
        return {
            "status": "success",
            "message": result,
            "user_id": request.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
def get_notes(user_id: str = "default", group_id: Optional[str] = None):
    """Get all groups with nested notes for a user"""
    groups = notes_manager._get_user_data(user_id)

    # Filter to specific group if requested
    if group_id:
        if group_id in groups:
            groups = {group_id: groups[group_id]}
        else:
            groups = {}

    # Count total notes
    total_notes = sum(len(g.get("notes", {})) for g in groups.values())

    return {
        "groups": groups,
        "notes_count": total_notes,
        "groups_count": len(groups),
        "user_id": user_id
    }


@app.get("/api/reset")
def reset_user(user_id: str = "default"):
    """Reset all notes for a user"""
    notes_manager.reset_user(user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "message": f"All notes cleared for user {user_id}"
    }

@app.get("/api/reset-conversation")
def reset_conversation(user_id: str = "default"):
    """Summarize and reset conversation for a user"""
    try:
        summary = agent.summarize_and_reset(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation-history")
def get_conversation_history(user_id: str = "default"):
    """Get current conversation history for debugging"""
    history = agent.conversation_history.get(user_id, [])

    messages = []
    for msg in history:
        msg_type = type(msg).__name__
        content = getattr(msg, "content", str(msg))
        messages.append({
            "type": msg_type,
            "content": content
        })

    return {
        "user_id": user_id,
        "message_count": len(messages),
        "messages": messages
    }


@app.get("/api/tools")
def get_tools():
    """List available tools"""
    return {
        "tools": [
            {
                "name": "list_groups",
                "description": "List all groups with their descriptions"
            },
            {
                "name": "add_group",
                "description": "Create a new group for organizing notes",
                "parameters": ["name", "description"]
            },
            {
                "name": "remove_group",
                "description": "Remove a group and all its notes",
                "parameters": ["group_id"]
            },
            {
                "name": "list_notes",
                "description": "List all notes, optionally filtered by group",
                "parameters": ["group_id (optional)"]
            },
            {
                "name": "add_note",
                "description": "Add a note to a specific group",
                "parameters": ["content", "group_id"]
            },
            {
                "name": "remove_note",
                "description": "Remove a note by its ID",
                "parameters": ["note_id"]
            }
        ]
    }

@app.get("/api/admin/create-default-note-groups")
def create_default_note_groups(user_id: str = "default"):
    """Create default note groups from default-note-groups.json"""
    try:
        # Load default groups
        groups_file = Path(__file__).parent / "default-note-groups.json"

        if not groups_file.exists():
            raise HTTPException(status_code=404, detail="default-note-groups.json not found")

        with open(groups_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        groups = data["groups"]
        created = []
        skipped = []

        for group in groups:
            result = notes_manager.add_group(user_id, group["name"], group["description"])
            if "already exists" in result:
                skipped.append(group["name"])
            else:
                created.append(group["name"])

        return {
            "status": "success",
            "user_id": user_id,
            "created": created,
            "skipped": skipped,
            "total": len(groups)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
def root():
    return {"message": "Soul Mirror Backend API", "docs": "/docs"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False
    )