# Soul Mirror Backend (Python/LangGraph)

Modern agent implementation using LangGraph for Soul Mirror.

## Architecture

Uses LangGraph's state machine approach:
- **Agent Node**: Calls LLM with bound tools
- **Tool Node**: Executes tool calls
- **Conditional Routing**: Routes between agent and tools
- **Memory**: Persists conversation state per thread

## Quick Start

```bash
# Copy environment file and add your API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY or OPENAI_API_KEY

# Run the server
./run.sh
```

## API Endpoints

- `GET /api/status` - Health check
- `GET/POST /api/process` - Process user input through agent
- `GET /api/notes` - Direct notes access
- `GET /api/history/{thread_id}` - Conversation history
- `GET /api/tools` - List available tools

## Tools

Single notes tool with three methods:
- `list_notes()` - List all notes
- `add_note(content)` - Add a new note
- `remove_note(note_id)` - Remove a note by ID

## Key Differences from Legacy

- **LangGraph State Machine**: Replaces AgentExecutor with explicit graph
- **Tool Binding**: Tools bound directly to LLM
- **Built-in Memory**: Thread-based conversation persistence
- **Modern Patterns**: Follows latest LangChain best practices