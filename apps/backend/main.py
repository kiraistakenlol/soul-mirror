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
from tools.memory import memory_manager
from tools.responsibilities import responsibilities_manager
from tools.notebook_toolkit import NotebookToolkit
from tools.memory_toolkit import MemoryToolkit
from tools.general_toolkit import GeneralToolkit
from tools.responsibilities_toolkit import ResponsibilitiesToolkit
from repository.notes import NotesRepository
from repository.requests import RequestsRepository
from llm_trace_callback import LLMTraceCallback

load_dotenv()

# Verify database connection on startup
try:
    repo = NotesRepository()
    with repo._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
    raise SystemExit(1)

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
    custom_rules: Optional[str] = None
    user_id: Optional[str] = "default"

# API Endpoints
@app.get("/api/status")
def get_status():
    """System health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agent": "langgraph",
        "tools": ["list_groups", "add_group", "remove_group", "list_notes", "add_note", "update_note", "remove_note"]
    }

@app.get("/api/process")
def process_get(input: str, user_id: str = "default"):
    """Process input via GET request"""
    try:
        print(f"📥 [GET] user={user_id} input=\"{input[:80]}{'...' if len(input) > 80 else ''}\"")

        # Log request to database before processing
        requests_repo = RequestsRepository()
        request_id = requests_repo.log_request(user_id, input)
        print(f"📝 Logged request id={request_id}")

        # Create callback to capture LLM traces
        trace_callback = LLMTraceCallback()

        # Process with agent
        response = agent.process_input(input, user_id, callbacks=[trace_callback])

        # Get captured traces
        llm_traces = trace_callback.get_traces()
        print(f"📊 Captured {len(llm_traces)} LLM interactions")

        # Update request with response and traces
        requests_repo.update_request_response(request_id, response, llm_traces)

        print(f"✓ Response: \"{response[:80]}{'...' if len(response) > 80 else ''}\"")
        return ProcessResponse(
            input=input,
            response=response,
            user_id=user_id
        )
    except Exception as e:
        print(f"✗ Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
def process_post(request: ProcessRequest):
    """Process input via POST request"""
    try:
        print(f"📥 [POST] user={request.user_id} input=\"{request.input[:80]}{'...' if len(request.input) > 80 else ''}\"")

        # Log request to database before processing
        requests_repo = RequestsRepository()
        request_id = requests_repo.log_request(request.user_id, request.input)
        print(f"📝 Logged request id={request_id}")

        # Create callback to capture LLM traces
        trace_callback = LLMTraceCallback()

        # Process with agent
        response = agent.process_input(request.input, request.user_id, callbacks=[trace_callback])

        # Get captured traces
        llm_traces = trace_callback.get_traces()
        print(f"📊 Captured {len(llm_traces)} LLM interactions")

        # Update request with response and traces
        requests_repo.update_request_response(request_id, response, llm_traces)

        print(f"✓ Response: \"{response[:80]}{'...' if len(response) > 80 else ''}\"")
        return ProcessResponse(
            input=request.input,
            response=response,
            user_id=request.user_id
        )
    except Exception as e:
        print(f"✗ Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/note-groups")
def create_note_group(request: NoteGroupRequest):
    """Create a note group directly without agent processing"""
    try:
        result = notes_manager.add_group(request.user_id, request.name, request.description, request.custom_rules)
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
    """Reset conversation for a user"""
    try:
        message = agent.reset_conversation(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "message": message
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

@app.get("/api/requests")
def get_requests(user_id: str = "default", limit: int = 100):
    """Get recent requests history for a user"""
    try:
        requests_repo = RequestsRepository()
        requests = requests_repo.get_recent_requests(user_id, limit)
        return {
            "user_id": user_id,
            "count": len(requests),
            "requests": requests
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory")
def get_memory(user_id: str = "default"):
    """Get core memory"""
    try:
        memory = memory_manager.get_core_memory(user_id)
        return {
            "user_id": user_id,
            "content": memory or "",
            "exists": bool(memory)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory")
def clear_memory(user_id: str = "default"):
    """Clear all core memory"""
    try:
        result = memory_manager.clear_core_memory(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "message": f"Memory cleared for {user_id}" if result else f"No memory to clear for {user_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/responsibilities")
def get_responsibilities(user_id: str = "default"):
    """Get all responsibilities"""
    try:
        from repository.responsibilities import ResponsibilitiesRepository
        repo = ResponsibilitiesRepository()
        responsibilities = repo.get_all_responsibilities(user_id)
        return {
            "user_id": user_id,
            "count": len(responsibilities),
            "responsibilities": responsibilities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar")
def get_calendar(user_id: str = "default"):
    """Get all calendar events"""
    try:
        from repository.calendar import CalendarRepository
        repo = CalendarRepository()
        events = repo.get_all_events(user_id)
        return {
            "user_id": user_id,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools")
def get_tools():
    """List available tools organized by toolkit"""
    notebook_toolkit = NotebookToolkit()
    memory_toolkit = MemoryToolkit()
    general_toolkit = GeneralToolkit()
    responsibilities_toolkit = ResponsibilitiesToolkit()
    from tools.calendar_toolkit import CalendarToolkit
    calendar_toolkit = CalendarToolkit()
    notebook_tools = notebook_toolkit.get_tools()
    memory_tools = memory_toolkit.get_tools()
    general_tools = general_toolkit.get_tools()
    responsibilities_tools = responsibilities_toolkit.get_tools()
    calendar_tools = calendar_toolkit.get_tools()

    def tool_to_dict(tool):
        """Convert tool to dict with name, description, and parameters"""
        tool_dict = {
            "name": tool.name,
            "description": tool.description
        }

        # Extract parameters from tool schema if available
        if hasattr(tool, 'args_schema') and tool.args_schema:
            schema = tool.args_schema.model_json_schema()
            if 'properties' in schema:
                params = [name for name in schema['properties'].keys() if name != 'config']
                if params:
                    tool_dict['parameters'] = params

        return tool_dict

    return {
        "toolkits": [
            {
                "name": "Notebook",
                "tools": [tool_to_dict(tool) for tool in notebook_tools]
            },
            {
                "name": "Memory",
                "tools": [tool_to_dict(tool) for tool in memory_tools]
            },
            {
                "name": "Responsibilities",
                "tools": [tool_to_dict(tool) for tool in responsibilities_tools]
            },
            {
                "name": "Calendar",
                "tools": [tool_to_dict(tool) for tool in calendar_tools]
            },
            {
                "name": "General",
                "tools": [tool_to_dict(tool) for tool in general_tools]
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
            result = notes_manager.add_group(user_id, group["name"], group["description"], group.get("customRules"))
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

@app.get("/api/admin/database/reset")
def reset_database():
    """Reset database schema and apply baseline.sql"""
    try:
        repo = NotesRepository()
        repo.reset_database()
        return {
            "status": "success",
            "message": "Database reset successfully"
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
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False,
        log_level="warning",
        access_log=False
    )