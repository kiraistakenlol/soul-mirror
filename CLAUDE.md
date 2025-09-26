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

## Curent project stage:
MVP, see mvp.spec.md

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
- Routes user input to appropriate tools
- Uses LLM to understand intent and context

**Tool Registry:**
- Extensible collection of specialized services
- Each tool handles specific user needs

**User Profile:**
- Living JSON that grows organically
- Stores personality, context, learning, goals

##### System Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│ LLM Orchestrator│───▶│  Tool Registry  │
│  (free text)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────┬───────┘
                                ▲                       │
                                │                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  User Profile   │◄───│ Selected Tools  │
                       │   (JSON)        │    │                 │
                       └─────────────────┘    └─────────────────┘
```

#### Directory structure
// TODO
#### Tech Stack

- go
- air (hot reload)

#### Development Commands

```bash
./scripts/build.sh
./scripts/check-all.sh
./scripts/format.sh
./scripts/vet.sh
```
