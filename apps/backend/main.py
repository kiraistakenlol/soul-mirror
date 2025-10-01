# FastAPI server for Soul Mirror backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uvicorn
from dotenv import load_dotenv

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

@app.get("/api/profile")
def get_profile(user_id: str = "default"):
    """Get user profile from PROFILE group notes"""
    groups = notes_manager._get_user_data(user_id)

    # Find PROFILE group (system group in uppercase)
    profile_items = []
    for group in groups.values():
        if group["name"] == "PROFILE":
            notes = group.get("notes", {})
            profile_items = [note["content"] for note in notes.values()]
            break

    profile_string = "; ".join(profile_items) if profile_items else ""

    return {
        "profile": profile_string,
        "count": len(profile_items),
        "user_id": user_id
    }

@app.get("/api/profiles")
def get_all_profiles():
    """Get all user profiles"""
    all_profiles = []

    for user_id in notes_manager.user_data.keys():
        groups = notes_manager._get_user_data(user_id)

        # Find PROFILE group (system group in uppercase)
        profile_items = []
        for group in groups.values():
            if group["name"] == "PROFILE":
                notes = group.get("notes", {})
                profile_items = [note["content"] for note in notes.values()]
                break

        profile_string = "; ".join(profile_items) if profile_items else ""

        # Count total notes
        total_notes = sum(len(g.get("notes", {})) for g in groups.values())

        all_profiles.append({
            "user_id": user_id,
            "profile": profile_string,
            "profile_count": len(profile_items),
            "total_notes": total_notes,
            "total_groups": len(groups)
        })

    return {
        "profiles": all_profiles,
        "count": len(all_profiles)
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