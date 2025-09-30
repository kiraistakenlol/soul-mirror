# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Long-term Vision

**Soul Mirror** is a personal assistant that learns who you are through your thoughts and notes, building deep understanding over time.

**Core Approach:**
The agent works like a real human assistant with a notebook - it remembers everything about you and organizes information naturally through experience. Uses a single notes system where everything lives together, building understanding through interaction patterns rather than rigid categorization.

**Key Capabilities:**
- **Memory Management**: Uses notes as primary memory system, like a human assistant's notebook
- **Natural Learning**: Automatically updates understanding of your personality, interests, and preferences through interactions
- **Contextual Intelligence**: References what it knows about you to provide more personalized responses
- **Emergent Organization**: Develops its own organizational systems over time rather than using pre-defined categories

## Project Rules

**IMPORTANT: These rules must be followed when working with this codebase:**

- never try to run backend server yourself, it's always running in the background in hot reaload mode
- to check backend compilation errors use `./scripts/build.sh`
- keep it as simple as you can
- follow DRY(don't repeat yourself principle) - always try to break complex compoents into smaller reusable parts with clear signatures
- avoid redundancy
- every component in the system should have a concise comment explaining what it does (not how it will be used)
- minimalism in code and docs (no redundant descriptions, no obvious comments, no unnecessary formatting) - but be expressive in logs and script output for clarity. examples:
    - ✅ `python`
    - ❌ `**Python**: Backend development language`
    - ✅ `type: string`
    - ❌ `type: string (enum)`
    - ✅ Simple variable names when context is clear
    - ❌ Long descriptive names that repeat context
    - ✅ `echo "✓ Build successful"` in scripts (expressive for debugging)
    - ✅ `print("Server starting on :8080")` (helpful log)
- remove dead code immediately - when changing behavior, completely remove old methods/functions rather than leaving them unused or simplified. no fallback methods that just return empty values

## Modules

### Backend (Python/LangChain)

apps/backend

#### System Architecture

##### High-Level Components

**LangChain Agent:**
- Personal assistant that uses notes as primary memory system
- Automatically considers context from notes before responding
- Updates understanding through natural interaction patterns

**Notes Tool:**
- Single unified notes system for all information
- Agent organizes information naturally like a human assistant
- Stores personality insights, preferences, and context together

##### System Flow

```
    ┌─────────────────┐
    │   User Input    │
    │  (free text)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Personal Agent  │
    │  (LangChain)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   Notes Tool    │
    │ (unified memory)│
    └─────────────────┘
```

#### Directory Structure

```
apps/backend/
├── main.py              # FastAPI entry point
├── agent.py             # LangChain personal assistant agent
├── tools/
│   └── notes.py         # Notes management tool
├── scripts/
│   └── dev.sh           # Development server script
├── requirements.txt     # Python dependencies
└── .env                 # Environment configuration
```

#### Tech Stack

- python (3.9+)
- langchain (agent framework)
- langchain-anthropic / langchain-openai (LLM providers)
- fastapi (API framework)
- uvicorn (ASGI server)
- pydantic (data validation)

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - System status and health
- `GET /api/process?input=text` - Process input with personal assistant response
- `POST /api/process` - Process input (JSON body)

#### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (with hot reload)
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8080
```

#### Configuration

Environment variables:
- `LLM_PROVIDER` - Choose LLM provider: "anthropic" or "openai" (default: anthropic)
- `ANTHROPIC_API_KEY` - Required when LLM_PROVIDER=anthropic
- `OPENAI_API_KEY` - Required when LLM_PROVIDER=openai
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Deployment environment (default: development)

Setup:
```bash
cp .env.example .env
# Set LLM_PROVIDER and add corresponding API key
```

