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
    thread_id: Optional[str] = "default"

class ProcessResponse(BaseModel):
    input: str
    response: str
    thread_id: str

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
def process_get(input: str, thread_id: str = "default"):
    """Process input via GET request"""
    try:
        response = agent.process_input(input, thread_id)
        return ProcessResponse(
            input=input,
            response=response,
            thread_id=thread_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
def process_post(request: ProcessRequest):
    """Process input via POST request"""
    try:
        response = agent.process_input(request.input, request.thread_id)
        return ProcessResponse(
            input=request.input,
            response=response,
            thread_id=request.thread_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
def get_notes():
    """Get all notes directly (bypass agent)"""
    return {
        "notes": notes_manager.notes,
        "count": len(notes_manager.notes)
    }

@app.get("/api/profile")
def get_profile():
    """Get user profile from profile notes (bypass agent)"""
    profile_notes = {}
    
    # Search for notes with [PROFILE] prefix
    for note_id, note in notes_manager.notes.items():
        content = note.get("content", "")
        if content.startswith("[PROFILE]"):
            profile_notes[note_id] = note
    
    return {
        "profile_notes": profile_notes,
        "count": len(profile_notes),
        "summary": "Profile information extracted from notes with [PROFILE] prefix"
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