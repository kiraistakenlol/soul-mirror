# Notes management tool with three methods: list, add, remove
import json
import os
from typing import List, Dict, Any
from datetime import datetime
import uuid

class NotesManager:
    def __init__(self):
        self.notes: Dict[str, Dict] = {}
    
    def list_notes(self) -> str:
        """List all notes"""
        if not self.notes:
            return "No notes found."
        
        result = []
        for note_id, note in self.notes.items():
            result.append(f"- [{note_id}] {note['content']} (created: {note['created']})")
        
        return "\n".join(result)
    
    def add_note(self, content: str) -> str:
        """Add a new note"""
        note_id = str(uuid.uuid4())[:8]
        self.notes[note_id] = {
            "id": note_id,
            "content": content,
            "created": datetime.now().isoformat()
        }
        return f"Added note [{note_id}]: {content}"
    
    def remove_note(self, note_id: str) -> str:
        """Remove a note by ID"""
        if note_id not in self.notes:
            return f"Note {note_id} not found."
        
        content = self.notes[note_id]["content"]
        del self.notes[note_id]
        return f"Removed note [{note_id}]: {content}"


# Create the tool functions for LangGraph
notes_manager = NotesManager()

def list_all_notes() -> str:
    """List all notes in the system"""
    return notes_manager.list_notes()

def add_new_note(content: str) -> str:
    """Add a new note with the given content"""
    return notes_manager.add_note(content)

def remove_note_by_id(note_id: str) -> str:
    """Remove a note by its ID"""
    return notes_manager.remove_note(note_id)