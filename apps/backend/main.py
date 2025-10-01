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
    """Get all notes and groups for a user"""
    user_data = notes_manager._get_user_data(user_id)
    notes = user_data["notes"]
    groups = user_data["groups"]

    # Filter notes by group if specified
    if group_id:
        notes = {nid: note for nid, note in notes.items() if note.get("group_id") == group_id}

    return {
        "groups": groups,
        "notes": notes,
        "notes_count": len(notes),
        "groups_count": len(groups),
        "user_id": user_id
    }

@app.get("/api/profile")
def get_profile(user_id: str = "default"):
    """Get user profile from Profile group notes"""
    user_data = notes_manager._get_user_data(user_id)
    notes = user_data["notes"]
    groups = user_data["groups"]

    # Find Profile group
    profile_group_id = None
    for gid, group in groups.items():
        if group["name"].lower() == "profile":
            profile_group_id = gid
            break

    profile_items = []
    if profile_group_id:
        # Get notes from Profile group
        for note in notes.values():
            if note.get("group_id") == profile_group_id:
                profile_items.append(note["content"])

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
        user_data = notes_manager._get_user_data(user_id)
        notes = user_data["notes"]
        groups = user_data["groups"]

        # Find Profile group
        profile_group_id = None
        for gid, group in groups.items():
            if group["name"].lower() == "profile":
                profile_group_id = gid
                break

        profile_items = []
        if profile_group_id:
            for note in notes.values():
                if note.get("group_id") == profile_group_id:
                    profile_items.append(note["content"])

        profile_string = "; ".join(profile_items) if profile_items else ""

        all_profiles.append({
            "user_id": user_id,
            "profile": profile_string,
            "profile_count": len(profile_items),
            "total_notes": len(notes),
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