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
- Uses notes as primary memory system organized in groups
- Automatically considers context from notes before responding
- Updates understanding through natural interaction patterns
- Maintains conversation history per user with summarization

**Notes Tool:**
- Group-based notes system for organized information
- Agent creates and manages groups to organize notes by topic
- System groups (UPPERCASE): PROFILE, CONVERSATIONS
- User groups (Capitalized): Interests, Work, Goals, Tasks, Events, People, Skills
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
- `GET /api/notes?user_id=id&group_id=id` - Get all groups with nested notes for user
- `GET /api/profile?user_id=id` - Get user profile from PROFILE group notes
- `GET /api/profiles` - Get all user profiles
- `GET /api/reset?user_id=id` - Reset all notes for user
- `GET /api/reset-conversation?user_id=id` - Summarize and archive conversation, then reset
- `GET /api/conversation-history?user_id=id` - Get current conversation history (debug)
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

apps/frontend

#### Tech Stack

- react (19.x)
- vite (dev server & build)
- tailwindcss (styling)

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
│   │   ├── ProfilesView.jsx       # Profiles page
│   │   ├── Profile.jsx            # User profile display
│   │   ├── NotesList.jsx          # Notes with collapsible groups
│   │   ├── ChatInput.jsx          # Input with process/reset
│   │   ├── ConversationHistory.jsx # Full conversation display
│   │   ├── ResponseDisplay.jsx
│   │   ├── Profiles.jsx
│   │   ├── Tests.jsx
│   │   ├── TestScenario.jsx
│   │   └── Tools.jsx
│   ├── services/
│   │   └── api.js
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
- Right (30%): Profile (15%) + Conversation History (85%)
- Input confined to notes column only

**Pages:**
- Soul Mirror (main interaction)
- Tools (available agent tools)
- Tests (test runner interface)
- Profiles (all user profiles)

#### Features

- Collapsible note groups (collapsed by default)
- Full conversation history (no truncation)
- Auto-refresh: notes (10s), status (30s), conversation (5s)
- Keyboard shortcuts: Enter = submit, Shift+Enter = new line, Esc = clear
- Fixed-height layout with independent scrolling
- Profile/conversation have fixed proportions (15%/85%)
- Large fonts, emojis, generous spacing

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
│  /api/profile       │
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

## Infrastructure & Deployment

infra/

VPS deployment using Docker Compose and nginx reverse proxy. See `infra/README.md` for:
- Architecture overview
- Initial setup steps
- Deployment scripts
- Management commands
- Troubleshooting

**Quick deploy from local:**
```bash
./scripts/deploy-remote.sh
```

