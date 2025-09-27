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

## Project Rules

**IMPORTANT: These rules must be followed when working with this codebase:**

- never try to run backend server yourself, it's always running in the background in hot reaload mode
- to check backend compilation errors use `./scripts/build.sh`
- keep it as simple as you can
- follow DRY(don't repeat yourself principle) - always try to break complex compoents into smaller reusable parts with clear signatures
- avoid redundancy
- every component in the system should have a concise comment explaining what it does (not how it will be used)
- minimalism in code and docs (no redundant descriptions, no obvious comments, no unnecessary formatting) - but be expressive in logs and script output for clarity. examples: 
    - ✅ `go`
    - ❌ `**Go**: Backend development language`
    - ✅ `type: string`
    - ❌ `type: string (enum)`
    - ✅ Simple variable names when context is clear
    - ❌ Long descriptive names that repeat context
    - ✅ `echo "✓ Build successful"` in scripts (expressive for debugging)
    - ✅ `fmt.Println("Server starting on :8080")` (helpful log)
- remove dead code immediately - when changing behavior, completely remove old methods/functions rather than leaving them unused or simplified. no fallback methods that just return empty values

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
- Configurable LLM provider (Anthropic Claude Haiku or OpenAI GPT-4.1-nano)
- JSON-based tool selection with reasoning
- Text processing capabilities

**Tool Service:**
- Registry of available tools (time, random, etc.)
- Each tool has name, description, and execute method with context
- Tools receive user profile as context for personalized responses
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
       ┌─────┼─────┐
       │     │     │
       ▼     ▼     ▼
  ┌───────┐ ┌───────┐ ┌───────┐
  │  LLM  │ │ Tool  │ │Profile│
  │Service│ │Service│ │Service│
  └───────┘ └───────┘ └───────┘
```

#### Directory Structure

```
apps/backend/
├── cmd/server/
│   └── main.go
├── internal/
│   ├── api/
│   ├── config/
│   │   └── config.go
│   ├── handlers/
│   │   ├── process/
│   │   ├── profile/
│   │   ├── status/
│   │   └── tools/
│   ├── llm/
│   │   ├── llm.go
│   │   └── types.go
│   ├── logging/
│   ├── orchestrator/
│   │   ├── orchestrator.go
│   │   └── types.go
│   ├── tools/
│   │   ├── registry.go
│   │   ├── context.go
│   │   ├── time.go
│   │   └── random.go
│   ├── profile/
│   │   ├── profile.go
│   │   └── mock.go
│   └── server/
│       └── server.go
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
- Anthropic Claude Haiku API / OpenAI GPT-4.1-nano API

#### API Endpoints

All endpoints prefixed with `/api` and return JSON:

- `GET /api/status` - System status and health
- `GET /api/process?input=text` - Process input with JSON response (tool_selection_result, tool_executions, profile_update)
- `GET /api/profile` - Get current profile
- `GET /api/tools` - List available tools

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

**Tool:**
```go
Execute(input string, context Context) (string, error)
Name() string
Description() string
```

**ProfileService:**
```go
Get() (string, error)
ProcessInput(input string) error
```

**Orchestrator:**
```go
ProcessInput(input string) (*ProcessResponse, error)
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
