# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current State (MVP)

**Soul Mirror** is currently a note-taking system with an AI agent that organizes your thoughts into categorized groups.

**What Works Now:**
- Group-based notes organization with custom rules per group
- AI agent that processes natural language input and creates/manages notes
- Multi-user support with data isolation
- Conversation history per user (in-memory)
- Request logging for debugging
- Telegram bot integration for voice and text input

**What's Not Implemented Yet:**
- User profile building from notes
- Learning personality, interests, preferences over time
- Personalized responses based on understanding of who you are
- Emergent organization patterns

## Long-term Vision

**Soul Mirror** will become a personal assistant that learns who you are through your thoughts and notes, building deep understanding over time.

**Future Core Approach:**
Like a real human assistant with a notebook - remembers everything about you and organizes information naturally through experience. Goes beyond note-taking to build understanding through interaction patterns.

**Future Key Capabilities:**
- **Memory Management**: Notes as primary memory system (implemented)
- **Natural Learning**: Automatically updates understanding of your personality, interests, preferences (not implemented)
- **Contextual Intelligence**: References what it knows about you to provide personalized responses (not implemented)
- **Emergent Organization**: Develops organizational systems over time rather than using pre-defined categories (not implemented)

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
- Uses notes as primary memory system organized in groups
- Automatically considers context from notes before responding
- Updates understanding through natural interaction patterns
- Maintains conversation history per user

**Notes Tool:**
- Group-based notes system for organized information
- PostgreSQL storage with repository pattern
- Agent creates and manages groups to organize notes by topic
- Groups have `description` (required) and `custom_rules` (optional) fields
- Agent sees and follows custom_rules when managing notes in each group
- Default user groups: Self-Improvement, Health & Lifestyle, Project Ideas, Work & Career, Language Learning, Relationships, Philosophy & Values, Location & Travel, Tasks & Reminders, Daily Reflections
- Supports multi-user isolation via user_id
- Initialize default groups via `/api/admin/create-default-note-groups` or Dev panel

**Request Logging:**
- Automatic logging of all user requests and agent responses
- Stored in PostgreSQL requests table
- Browse history via Requests tab in frontend
- Useful for debugging and understanding interaction patterns

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
├── main.py                    # FastAPI entry point
├── agent.py                   # LangChain personal assistant agent
├── baseline.sql               # Database schema
├── default-note-groups.json   # Default note groups definitions
├── tools/
│   └── notes.py               # Notes management tool
├── repository/
│   ├── notes.py               # PostgreSQL notes data layer
│   └── requests.py            # PostgreSQL requests logging
├── scripts/
│   └── dev.sh                 # Development server script
├── requirements.txt           # Python dependencies
└── .env                       # Environment configuration
```

#### Tech Stack

- python (3.9+)
- langgraph (state machine framework)
- langchain (agent framework)
- langchain-anthropic / langchain-openai (LLM providers)
- fastapi (API framework)
- uvicorn (ASGI server)
- pydantic (data validation)
- psycopg2 (PostgreSQL driver)
- postgresql (database)

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - System status and health
- `GET /api/process?input=text&user_id=id` - Process input with personal assistant response
- `POST /api/process` - Process input (JSON body with input and user_id)
- `POST /api/note-groups` - Create note group directly (name, description, custom_rules, user_id)
- `GET /api/notes?user_id=id&group_id=id` - Get all groups with nested notes for user
- `GET /api/reset?user_id=id` - Reset all notes for user
- `GET /api/reset-conversation?user_id=id` - Reset conversation history
- `GET /api/conversation-history?user_id=id` - Get current conversation history (debug)
- `GET /api/requests?limit=n` - Get recent requests with responses
- `GET /api/tools` - List available tools
- `GET /api/admin/create-default-note-groups?user_id=id` - Initialize default note groups from config
- `GET /api/admin/database/reset` - Reset database schema and apply baseline.sql

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
- `DATABASE_URL` - PostgreSQL connection string (required)
- `LLM_PROVIDER` - Choose LLM provider: "anthropic" or "openai" (default: anthropic)
- `ANTHROPIC_API_KEY` - Required when LLM_PROVIDER=anthropic
- `OPENAI_API_KEY` - Required when LLM_PROVIDER=openai
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Deployment environment (default: development)

Setup:
```bash
cp .env.example .env
# Set DATABASE_URL and LLM_PROVIDER with corresponding API key
```

#### Database

PostgreSQL storage with schema management:
- `baseline.sql` - Database schema (note_groups, notes, requests tables)
- Repository pattern in `repository/notes.py` and `repository/requests.py`
- Manual schema reset via `/api/admin/database/reset`

### Frontend (React/Vite)

apps/frontend

#### Tech Stack

- react (19.1+)
- vite (7.x dev server & build)
- tailwindcss (4.x styling)

#### Directory Structure

```
apps/frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── Tabs.jsx
│   │   ├── MainView.jsx           # Main page layout
│   │   ├── ToolsView.jsx          # Tools page
│   │   ├── TestsView.jsx          # Tests page
│   │   ├── RequestsView.jsx       # Request history browser
│   │   ├── DevView.jsx            # Developer admin panel
│   │   ├── NotesList.jsx          # Notes with collapsible groups
│   │   ├── ChatInput.jsx          # Input with process/reset and error display
│   │   ├── ConversationHistory.jsx # Full conversation display
│   │   ├── ResponseDisplay.jsx
│   │   ├── Tests.jsx
│   │   ├── TestScenario.jsx
│   │   └── Tools.jsx
│   ├── services/
│   │   └── api.js                 # API client with improved error handling
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
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

#### Layout

**Main View:**
- Left (70%): Notes (collapsible groups) + Input at bottom
- Right (30%): Conversation History
- Input confined to notes column only

**Pages:**
- Soul Mirror (main interaction)
- Tools (available agent tools)
- Tests (test runner interface)
- Requests (browse request history)
- Dev (developer admin panel)

#### Features

- Collapsible note groups (collapsed by default)
- Shows custom_rules for groups when expanded
- Full conversation history (no truncation)
- Auto-refresh: notes (10s), status (30s), conversation (5s), requests (5s)
- Keyboard shortcuts: Enter = submit, Shift+Enter = new line, Esc = clear
- Fixed-height layout with independent scrolling
- Large fonts, emojis, generous spacing
- Error display with dismissible alerts
- Concurrent input (can type while processing)
- Request history browser with auto-refresh
- Dev panel for admin operations (create default note groups)

### Telegram Bot (Python)

apps/telegram-bot

#### Purpose

Telegram bot that forwards text and voice messages to Soul Mirror backend, enabling note-taking through Telegram channels.

#### Architecture

```
Telegram Channel
    │
    ▼
Telegram Bot
    │
    ├─→ Voice messages → OpenAI Whisper (transcribe)
    │                          │
    │                          ▼
    └─→ Text messages ────→ Backend /api/process
                              │
                              ▼
                       Soul Mirror Agent
```

#### Directory Structure

```
apps/telegram-bot/
├── main.py              # Bot logic with text/voice handlers
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image
├── scripts/
│   ├── dev.sh           # Development server
│   └── install.sh       # Install dependencies
└── .env                 # Environment configuration
```

#### Tech Stack

- python (3.9+)
- python-telegram-bot (bot framework)
- httpx (HTTP client)
- openai (Whisper API for voice transcription)

#### Configuration

Environment variables:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key for Whisper transcription
- `BACKEND_URL` - Soul Mirror backend URL (default: http://localhost:8080)

Setup:
```bash
cp .env.example .env
# Add TELEGRAM_BOT_TOKEN and OPENAI_API_KEY
```

#### Development Commands

```bash
# Install dependencies
./scripts/install.sh

# Run bot (backend must be running)
./scripts/dev.sh
```

#### Features

- Text message forwarding to Soul Mirror
- Voice message transcription using OpenAI Whisper
- Channel post support (bot as channel admin)
- Direct message support
- Replies include transcription for voice messages
- Single shared user (no per-chat user_id)

#### Setup in Telegram

1. Create bot via @BotFather: `/newbot`
2. Get bot token and add to `.env`
3. Add bot to channel as administrator
4. Enable "Manage messages" permission
5. Bot processes all messages posted to channel

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
│  /api/reset         │
└─────────────────────┘
```

#### Directory Structure

```
apps/test-runner/
├── main.py              # FastAPI entry point
├── runner.py            # Orchestrates scenario execution
├── evaluator.py         # LLM-based evaluation
├── test-scenarios.json  # Test cases with expected outcomes
├── requirements.txt     # Python dependencies
└── scripts/
    └── dev.sh           # Development server
```

#### Components

- `test-scenarios.json` - Test cases with input sequences and expected outcomes
- `runner.py` - Orchestrates scenario execution against backend
- `evaluator.py` - Uses LLM to compare actual vs expected profile
- `main.py` - FastAPI service (port 8081)

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - Health check
- `GET /api/scenarios` - Get all test scenarios
- `GET /api/run-all` - Execute all test scenarios
- `GET /api/run-scenario?scenario_name=name` - Execute specific scenario

#### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run test runner (port 8081)
./scripts/dev.sh

# Execute tests via HTTP
curl http://localhost:8081/api/run-all

# Or run specific scenario
curl http://localhost:8081/api/run-scenario?scenario_name=preference_learning
```

#### Tech Stack

- python (3.9+)
- fastapi
- langchain-anthropic (LLM evaluator)

## Local Development

### Docker Compose

`docker-compose.yml` - Local multi-container setup:
- postgres (port 5433)
- backend (port 8080)
- frontend (port 3000)
- telegram-bot

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Scripts

- `scripts/deploy-remote.sh` - Deploy to VPS from local
- `scripts/deploy.sh` - Build and deploy containers (runs on VPS)
- `scripts/db-copy.sh` - Copy database between environments

## Deployment

**VPS:** 45.32.117.48 (kiraistaken.lol)
**Production URLs:**
- Frontend: http://soulmirror.kiraistaken.lol
- API: http://api.soulmirror.kiraistaken.lol

**Infrastructure:** Managed in separate repo `https://github.com/kiraistakenlol/infra` (nginx configs, VPS bootstrap)

**Deploy from local:**
```bash
./scripts/deploy-remote.sh
```

Runs on VPS:
- Pulls latest code
- Stops containers
- Rebuilds with production API URL
- Restarts all services

**Manual deploy on VPS:**
```bash
ssh root@45.32.117.48
cd /root/soul-mirror
./scripts/deploy.sh
```

