# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Long-term Vision

**Soul Mirror** is a personal intelligence system that learns who you are through your thoughts and helps you become who you want to be.

**Core Experience:**
- Capture fleeting thoughts via voice messages on your phone (WhatsApp/Telegram)
- System automatically understands what type of content it is
- Builds a living profile of your personality, interests, goals, and growth areas
- Provides contextual reminders and suggestions at the right moments
- Becomes your personal assistant that truly knows you

**Key Capabilities:**
- **Personal Profiling**: Understands your values, interests, communication style, and behavioral patterns
- **Intelligent Categorization**: Distinguishes between self-reflection, actionable ideas, tasks, and random thoughts  
- **Proactive Assistance**: Reminds you of self-improvement goals before important situations
- **Idea Management**: Captures and organizes your creative thoughts for later action
- **Contextual Intelligence**: Uses your calendar, location, and profile to provide relevant suggestions

## Current project stage:
Stage 2 complete ✅ - Real LLM integration with Anthropic Claude
Stage 3 planned 📋 - Enhanced API & Simple UI
- Simple web UI for backend interaction
- Structured logging with slog
- Enhanced API endpoints (/api/tools, /api/status)
- Comprehensive process result details

## Project Rules

**IMPORTANT: These rules must be followed when working with this codebase:**

- never try to run backend server yourself, it's always running in the background in hot reaload mode
- to check backend compilation errors use `./scripts/build.sh`
- keep it as simple as you can
- follow DRY(don't repeat yourself principle) - always try to break complex compoents into smaller reusable parts with clear signatures
- avoid redundancy
- minimalism in code and docs (no redundant descriptions, no obvious comments, no unnecessary formatting) - but be expressive in logs and script output for clarity. examples: 
    - ✅ `go`
    - ❌ `**Go**: Backend development language`
    - ✅ `type: string`
    - ❌ `type: string (enum)`
    - ✅ Simple variable names when context is clear
    - ❌ Long descriptive names that repeat context
    - ✅ `echo "✓ Build successful"` in scripts (expressive for debugging)
    - ✅ `fmt.Println("Server starting on :8080")` (helpful log)

## Modules

### Backend


apps/backend

#### System Architecture

##### High-Level Components

**LLM Orchestrator:**
- Coordinates workflow between all services
- Processes user input and returns combined responses
- Handles multiple tool execution with error handling

**LLM Service:**
- Anthropic Claude integration for intelligent tool selection
- Fallback logic when API unavailable
- JSON-based tool selection with reasoning
- Text processing capabilities

**Tool Service:**
- Registry of available tools (echo, etc.)
- Each tool has name, description, and execute method
- Extensible for adding new capabilities

**Profile Service:**
- Simple plain text profile storage
- Automatically learns from user input
- Single-user MVP design

##### System Flow

```
┌─────────────────┐
│   User Input    │
│  (free text)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Orchestrator│
└────────┬────────┘
         │
   ┌─────┼─────┬─────┐
   │     │     │     │
   ▼     ▼     ▼     ▼
┌─────┐ ┌───────┐ ┌─────┐
│ LLM │ │ Tool  │ │Profile│
│Service│ │Service│ │Service│
└─────┘ └───────┘ └─────┘
```

#### Directory Structure

```
apps/backend/
├── cmd/server/          # Application entry point
│   └── main.go
├── internal/            # Private packages
│   ├── api/            # HTTP handlers
│   ├── config/         # Configuration management
│   │   └── config.go   # Environment variables + validation
│   ├── llm/            # LLM Service
│   │   ├── llm.go      # Anthropic Claude integration
│   │   └── mock.go     # Mock implementation
│   ├── logging/        # Structured logging
│   ├── orchestrator/   # Main coordinator
│   │   ├── orchestrator.go
│   │   └── mock.go
│   ├── tools/          # Tool Service
│   │   ├── registry.go # Interface + tools
│   │   ├── time.go     # Time tool
│   │   └── mock.go
│   ├── profile/        # Profile Service
│   │   ├── profile.go  # Plain text profile
│   │   └── mock.go
│   ├── server/         # HTTP server
│   │   └── server.go
│   └── types/          # Shared types
└── scripts/
    ├── build.sh
    ├── check-all.sh
    ├── check-format.sh
    ├── dev.sh
    ├── format.sh
    └── vet.sh
```
#### Tech Stack

- go (1.23.0)
- air (hot reload)
- gin (HTTP framework)
- slog (structured logging)
- github.com/joho/godotenv (environment configuration)
- Anthropic Claude API

#### API Endpoints

- `GET /health` - Health check
- `GET /process?input=text` - Process user input
- `GET /profile` - Get current profile
- `GET /api/tools` - List available tools
- `GET /api/status` - System status

#### Key Interfaces

**LLMService:**
```go
type ToolSelection struct {
    ToolName string
    Reason   string
}

SelectTools(input string, tools []ToolDescriptor) ([]ToolSelection, error)
```

**ToolService:**
```go
ListTools() []Tool
GetTool(name string) Tool
```

**ProfileService:**
```go
Get() (string, error)
ProcessInput(input string) error
```

**Orchestrator:**
```go
ProcessInput(input string) (string, error)
ProcessInputDetailed(input string) (*types.ProcessResponse, error)
```

#### Development Commands

```bash
./scripts/build.sh
./scripts/check-all.sh
./scripts/format.sh
./scripts/vet.sh
```

#### Configuration

Environment variables:
- `ANTHROPIC_API_KEY` - Required for LLM functionality
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Deployment environment (default: development)

Setup:
```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```
