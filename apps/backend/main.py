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
        "tools": ["list_notes", "add_note", "remove_note"]
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
def get_notes(user_id: str = "default"):
    """Get all notes for a user"""
    user_notes = notes_manager._get_user_notes(user_id)
    return {
        "notes": user_notes,
        "count": len(user_notes),
        "user_id": user_id
    }

@app.get("/api/profile")
def get_profile(user_id: str = "default"):
    """Get user profile from profile notes as concatenated string"""
    user_notes = notes_manager._get_user_notes(user_id)
    profile_items = []

    # Extract and clean profile notes
    for note_id, note in user_notes.items():
        content = note.get("content", "")
        if content.startswith("[PROFILE]"):
            # Remove [PROFILE] prefix and strip whitespace
            cleaned = content.replace("[PROFILE]", "").strip()
            profile_items.append(cleaned)

    # Concatenate into single string
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

    for user_id in notes_manager.user_notes.keys():
        user_notes = notes_manager._get_user_notes(user_id)
        profile_items = []

        # Extract and clean profile notes
        for _, note in user_notes.items():
            content = note.get("content", "")
            if content.startswith("[PROFILE]"):
                cleaned = content.replace("[PROFILE]", "").strip()
                profile_items.append(cleaned)

        profile_string = "; ".join(profile_items) if profile_items else ""

        all_profiles.append({
            "user_id": user_id,
            "profile": profile_string,
            "profile_count": len(profile_items),
            "total_notes": len(user_notes)
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
                "name": "list_notes",
                "description": "List all notes in the system"
            },
            {
                "name": "add_note",
                "description": "Add a new note to the system",
                "parameters": ["content"]
            },
            {
                "name": "remove_note",
                "description": "Remove a note from the system by its ID",
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