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
Stage 1 complete ✅ - Core architecture with mock implementations
Ready for Stage 2 - Real LLM integration

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
- Intelligent tool selection with reasoning
- Returns multiple tools with explanations
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
│   ├── llm/            # LLM Service
│   │   ├── llm.go      # Interface + implementation
│   │   └── mock.go     # Mock implementation
│   ├── orchestrator/   # Main coordinator
│   │   ├── orchestrator.go
│   │   └── mock.go
│   ├── tools/          # Tool Service
│   │   ├── registry.go # Interface + tools
│   │   └── mock.go
│   ├── profile/        # Profile Service
│   │   ├── profile.go  # Plain text profile
│   │   └── mock.go
│   └── server/         # HTTP server
│       ├── server.go
│       └── handlers.go
└── scripts/
    ├── build.sh
    ├── check-all.sh
    ├── check-format.sh
    ├── dev.sh
    ├── format.sh
    └── vet.sh
```
#### Tech Stack

- go (1.22.2)
- air (hot reload)
- standard library HTTP server

#### API Endpoints

- `GET /health` - Health check
- `GET /process?input=text` - Process user input
- `GET /profile` - Get current profile

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

#### Development Commands

```bash
./scripts/build.sh
./scripts/check-all.sh
./scripts/format.sh
./scripts/vet.sh
```
