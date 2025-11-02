# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current State (MVP)

**Soul Mirror** is currently a note-taking system with an AI agent that organizes your thoughts into categorized groups.

**What Works Now:**
- Core memory system - long-term understanding of user context
- Responsibilities system - agent's internal workflows and recurring tasks
- Calendar system - scheduled events with iCalendar integration
- Group-based notes organization with custom rules per group
- AI agent with multiple toolkits (notebook, memory, calendar, responsibilities, telegram, tts, general)
- Multi-user support with data isolation
- Conversation history per user (in-memory)
- Request logging for debugging
- Telegram bot integration for voice/text input and sending text/audio to channels
- TTS with ElevenLabs for generating speech from text
- File storage system for managing audio and other files

**What's Not Implemented Yet:**
- Emergent organization patterns
- Advanced learning from interaction patterns

## Long-term Vision

**Soul Mirror** will become a personal assistant that learns who you are through your thoughts and notes, building deep understanding over time.

**Future Core Approach:**
Like a real human assistant with a notebook - remembers everything about you and organizes information naturally through experience. Goes beyond note-taking to build understanding through interaction patterns.

**Key Capabilities:**
- **Memory Management**: Core memory for long-term context + notes for organized information (implemented)
- **Task Management**: Responsibilities and calendar for scheduling and workflows (implemented)
- **Natural Learning**: Automatically updates understanding through memory system (partially implemented)
- **Contextual Intelligence**: References core memory for personalized responses (implemented)
- **Emergent Organization**: Develops organizational systems over time (not implemented)

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
- Multiple toolkits: Notebook, Memory, Calendar, Responsibilities, Telegram, TTS, General
- Loads core memory into context for each request
- Automatically translates all content to English before storing
- Maintains conversation history per user

**Notebook Tool:**
- Group-based notes for organized information storage
- PostgreSQL storage with repository pattern
- Groups have `description` (required) and `custom_rules` (optional) fields
- Tools: list_groups, add_group, remove_group, list_notes, add_note, update_note, remove_note, search_notes, move_note, get_groups_count, get_current_datetime

**Memory Tool:**
- Core memory for long-term understanding of user
- Single text field per user storing important context, preferences, patterns
- Tools: read_core_memory, write_core_memory, clear_core_memory
- Agent updates memory with significant information

**Calendar Tool:**
- Scheduled events with iCalendar integration
- One-time events (with title/description) or recurring events (linked to responsibilities)
- Supports recurrence patterns (daily, weekly, etc.)
- Tools: add_calendar_event, list_calendar_events, remove_calendar_event, get_upcoming_events
- PostgreSQL storage with ical_data field

**Responsibilities Tool:**
- Agent's internal workflows and recurring tasks
- Plain English description of what, when, how
- Can be linked to calendar events for execution timing
- Tools: add_responsibility, list_responsibilities, update_responsibility, remove_responsibility

**Telegram Tool:**
- Send text and audio to user's Telegram channels
- Tools: list_telegram_channels, send_telegram_message, send_audio_to_telegram
- Integrates with telegram-bot service API
- Used for scheduled messages or on-demand posting
- send_audio_to_telegram accepts file_id from TTS and optional caption

**TTS Tool:**
- Text-to-speech using ElevenLabs API
- Tools: generate_speech, list_voices
- Generates audio files stored in PostgreSQL files table
- Returns file_id for use with send_audio_to_telegram
- Supports multiple voices

**General Tool:**
- Utility functions: get_current_datetime

**File Storage:**
- Generic file storage system with metadata
- PostgreSQL files table with binary data and JSONB metadata
- Repository pattern in repository/files.py
- Used for TTS audio files, can store any file type
- Supports categorization via file_type field

**Request Logging:**
- Automatic logging of all user requests and agent responses
- Stored in PostgreSQL requests table
- Browse history via Requests tab in frontend

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
    │  + Core Memory  │
    └────────┬────────┘
             │
             ▼
    ┌───────────────────────────────────────────────┐
    │  Toolkits: Notebook, Memory, Calendar,        │
    │  Responsibilities, Telegram, TTS, General     │
    └───────────────────────────────────────────────┘
```

#### Directory Structure

```
apps/backend/
├── main.py                       # FastAPI entry point
├── agent.py                      # LangChain personal assistant agent
├── baseline.sql                  # Database schema with timestamp triggers
├── default-note-groups.json      # Default note groups definitions
├── tools/
│   ├── notes.py                  # Notes management
│   ├── memory.py                 # Core memory management
│   ├── responsibilities.py       # Responsibilities management
│   ├── calendar.py               # Calendar management
│   ├── telegram.py               # Telegram integration
│   ├── tts.py                    # Text-to-speech with ElevenLabs
│   ├── notebook_toolkit.py       # Notebook toolkit wrapper
│   ├── memory_toolkit.py         # Memory toolkit wrapper
│   ├── general_toolkit.py        # General utilities toolkit
│   ├── responsibilities_toolkit.py
│   ├── calendar_toolkit.py
│   ├── telegram_toolkit.py
│   └── tts_toolkit.py
├── repository/
│   ├── notes.py                  # PostgreSQL notes data layer
│   ├── requests.py               # PostgreSQL requests logging
│   ├── memory.py                 # PostgreSQL core memory data layer
│   ├── responsibilities.py       # PostgreSQL responsibilities data layer
│   ├── calendar.py               # PostgreSQL calendar data layer
│   └── files.py                  # PostgreSQL files storage data layer
├── scripts/
│   └── dev.sh                    # Development server script
├── requirements.txt              # Python dependencies
└── .env                          # Environment configuration
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
- icalendar (calendar events)
- elevenlabs (TTS API)

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - System status and health
- `GET /api/process?input=text&user_id=id` - Process input with personal assistant response
- `POST /api/process` - Process input (JSON body with input and user_id)
- `POST /api/note-groups` - Create note group directly (name, description, custom_rules, user_id)
- `GET /api/notes?user_id=id&group_id=id` - Get all groups with nested notes for user
- `GET /api/memory?user_id=id` - Get core memory for user
- `DELETE /api/memory?user_id=id` - Clear core memory for user
- `GET /api/responsibilities?user_id=id` - Get all responsibilities for user
- `GET /api/calendar?user_id=id` - Get all calendar events for user
- `GET /api/files?user_id=id&file_type=type` - List files (optionally filtered by type)
- `GET /api/files/{file_id}?user_id=id` - Download file by ID
- `DELETE /api/files/{file_id}?user_id=id` - Delete file by ID
- `POST /api/tts/generate` - Generate speech from text (text, voice_id, user_id)
- `GET /api/tts/voices` - List available ElevenLabs voices
- `GET /api/reset?user_id=id` - Reset all notes for user
- `GET /api/reset-conversation?user_id=id` - Reset conversation history
- `GET /api/conversation-history?user_id=id` - Get current conversation history (debug)
- `GET /api/requests?limit=n` - Get recent requests with responses
- `GET /api/tools` - List available tools
- `GET /api/admin/create-default-note-groups?user_id=id` - Initialize default note groups from config
- `GET /api/admin/database/reset` - Reset database schema and apply baseline.sql

#### Development Commands

```bash
# Install dependencies (IMPORTANT: use venv)
./venv/bin/pip install -r requirements.txt

# Run server (with hot reload) - runs automatically in background
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8080

# Or use dev script
./scripts/dev.sh
```

**IMPORTANT:** Backend uses `venv` virtual environment. Always install packages with `./venv/bin/pip install <package>`, not global `pip install`. This issue comes up frequently when new dependencies are added.

#### Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string (required)
- `LLM_PROVIDER` - Choose LLM provider: "anthropic" or "openai" (default: anthropic)
- `ANTHROPIC_API_KEY` - Required when LLM_PROVIDER=anthropic
- `OPENAI_API_KEY` - Required when LLM_PROVIDER=openai
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Deployment environment (default: development)
- `TELEGRAM_BOT_URL` - Telegram bot service URL (local: http://localhost:8082, docker: http://telegram-bot:8082)
- `ELEVENLABS_API_KEY` - ElevenLabs API key for TTS

Setup:
```bash
cp .env.example .env
# Set DATABASE_URL and LLM_PROVIDER with corresponding API key
```

#### Database

PostgreSQL storage with schema management:
- `baseline.sql` - Database schema (note_groups, notes, requests, core_memory, responsibilities, calendar_events, files tables)
- Automatic timestamp tracking: `created_at` and `updated_at` fields with triggers
- Repository pattern in `repository/*.py` files
- Manual schema reset via `/api/admin/database/reset`
- files table stores binary data with JSONB metadata

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
│   │   ├── RequestsView.jsx       # Request history browser with copy JSON
│   │   ├── DevView.jsx            # Developer admin panel
│   │   ├── MemoryView.jsx         # Core memory display and editing
│   │   ├── ResponsibilitiesView.jsx # Responsibilities list
│   │   ├── CalendarView.jsx       # Calendar events with links to responsibilities
│   │   ├── FilesView.jsx          # Files browser with download/delete
│   │   ├── NotesList.jsx          # Notes with collapsible groups and relative timestamps
│   │   ├── ChatInput.jsx          # Input with process/reset and error display
│   │   ├── ConversationHistory.jsx # Full conversation display
│   │   ├── ResponseDisplay.jsx
│   │   ├── Tests.jsx
│   │   ├── TestScenario.jsx
│   │   └── Tools.jsx
│   ├── services/
│   │   └── api.js                 # API client with improved error handling
│   ├── utils/
│   │   └── time.js                # Timestamp formatting utilities
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
- Memory (core memory display)
- Responsibilities (workflows list)
- Calendar (scheduled events)
- Files (browse/download/delete files)
- Tools (available agent tools)
- Tests (test runner interface)
- Requests (browse request history)
- Dev (developer admin panel)

#### Features

- Collapsible note groups (collapsed by default)
- Collapsible custom_rules for groups (hidden by default)
- Relative timestamps ("2m ago", "3h ago") with hover tooltips showing full dates
- Full conversation history (no truncation)
- Auto-refresh: notes (10s), status (30s), conversation (5s), requests (5s)
- Keyboard shortcuts: Enter = submit, Shift+Enter = new line, Esc = clear
- Fixed-height layout with independent scrolling
- Large fonts, emojis, generous spacing
- Error display with dismissible alerts
- Concurrent input (can type while processing)
- Request history browser with auto-refresh and copy as JSON
- Dev panel for admin operations (create default note groups)

### Telegram Bot (Python)

apps/telegram-bot

#### Purpose

Telegram bot that forwards text and voice messages to Soul Mirror backend AND provides API for sending messages to channels. Enables bidirectional Telegram integration.

#### Architecture

```
Telegram Channel ←───────────────┐
    │                            │
    ▼                            │
Telegram Bot (port 8082)         │
    │                            │
    ├─→ Incoming:                │ Outgoing:
    │   Voice → Whisper          │ POST /send_message
    │   Text → Backend           │ GET /list_channels
    │                            │
    └─→ Backend /api/process ────┘
           │
           ▼
    Soul Mirror Agent
    (uses telegram toolkit)
```

#### Directory Structure

```
apps/telegram-bot/
├── main.py              # Bot logic with text/voice handlers + FastAPI service
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
- fastapi (API service for sending messages)
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

**Incoming (Bot → Backend):**
- Text message forwarding to Soul Mirror
- Voice message transcription using OpenAI Whisper
- Channel post support (bot as channel admin)
- Direct message support
- Replies include transcription for voice messages
- Single shared user (no per-chat user_id)

**Outgoing (API Service):**
- `POST /send_message` - Send text message to channel (chat_id, message)
- `POST /send-audio` - Send audio file to channel (chat_id, audio_base64, filename, caption)
- `GET /list_channels` - List available channels with chat_ids
- Port 8082

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

