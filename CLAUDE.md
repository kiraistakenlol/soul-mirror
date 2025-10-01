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

- never run backend server yourself, it's always running in background in hot reload mode
- keep it as simple as you can
- follow DRY(don't repeat yourself principle) - always break complex components into smaller reusable parts with clear signatures
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

**LangGraph Agent:**
- Personal assistant using LangGraph state machine pattern
- Uses notes as primary memory system
- Automatically considers context from notes before responding
- Updates understanding through natural interaction patterns

**Notes Tool:**
- Single unified notes system for all information
- Agent organizes information naturally like a human assistant
- Stores personality insights, preferences, and context together
- Supports multi-user isolation via user_id

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
    │  (LangGraph)    │
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
- langgraph (state machine framework)
- langchain (agent framework)
- langchain-anthropic / langchain-openai (LLM providers)
- fastapi (API framework)
- uvicorn (ASGI server)
- pydantic (data validation)

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - System status and health
- `GET /api/process?input=text&user_id=id` - Process input with personal assistant response
- `POST /api/process` - Process input (JSON body with input and user_id)
- `GET /api/notes?user_id=id` - Get all notes for user
- `GET /api/profile?user_id=id` - Get user profile from profile notes as concatenated string
- `GET /api/profiles` - Get all user profiles
- `GET /api/reset?user_id=id` - Reset all notes for user
- `GET /api/tools` - List available tools

#### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (with hot reload) - runs automatically in background
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8080

# Or use dev script
./scripts/dev.sh
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

### Frontend (React/Vite)

apps/frontend-new

#### Tech Stack

- react (19.x)
- vite (dev server & build)
- tailwindcss (styling)

#### Directory Structure

```
apps/frontend-new/
├── src/
│   ├── components/       # React components
│   │   ├── Header.jsx
│   │   ├── Profile.jsx
│   │   ├── NotesList.jsx
│   │   ├── ChatInput.jsx
│   │   ├── ResponseDisplay.jsx
│   │   ├── MainView.jsx
│   │   ├── Profiles.jsx
│   │   ├── ProfilesView.jsx
│   │   ├── Tabs.jsx
│   │   └── TestsView.jsx
│   ├── services/
│   │   └── api.js        # API service layer
│   ├── App.jsx           # Main app component
│   └── index.css         # Global styles (Tailwind)
├── package.json
├── vite.config.js
└── .env
```

#### Development Commands

```bash
# Install dependencies
npm install

# Start dev server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### Configuration

Environment variables:
- `VITE_API_BASE` - Backend API base URL (default: http://localhost:8080)

Setup:
```bash
cp .env.example .env
```

#### Features

- Auto-refresh notes (10s interval)
- Auto-refresh status (30s interval)
- Keyboard shortcuts (Enter = submit, Esc = clear)
- Responsive 3-column layout
- Dark theme with Tailwind

### Test Runner (Python/LangChain)

apps/test-runner

#### Purpose

Automated scenario-based testing with LLM evaluation to validate prompt effectiveness and agent behavior consistency.

#### Architecture

```
┌─────────────────────┐
│   Test Runner       │
│   (port 8081)       │
│                     │
│  - Load scenarios   │
│  - Orchestrate      │
│  - Evaluate         │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   Main Backend      │
│   (port 8080)       │
│                     │
│  /api/process       │
│  /api/profile       │
│  /api/reset         │
└─────────────────────┘
```

#### Components

- `test-scenarios.json` - Test cases with input sequences and expected outcomes
- `runner.py` - Orchestrates scenario execution against backend
- `evaluator.py` - Uses LLM to compare actual vs expected profile
- `main.py` - FastAPI service exposing `/api/run-tests`

#### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run test runner (port 8081)
python main.py

# Execute tests via HTTP
curl http://localhost:8081/api/run-tests

# Or run specific scenario
curl http://localhost:8081/api/run-tests?scenario=preference_learning
```

#### Tech Stack

- python (3.9+)
- fastapi
- langchain-anthropic (LLM evaluator)

