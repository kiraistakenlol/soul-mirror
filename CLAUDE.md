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
- minimalism(no redundant descriptions, no obvious comments, no unnecessary formatting). examples: 
    - ✅ `go`
    - ❌ `**Go**: Backend development language`
    - ✅ `./scripts/build.sh`
    - ❌ `./scripts/build.sh   # Check compilation`
    - ✅ `type: string`
    - ❌ `type: string (enum)`
    - ✅ Simple variable names when context is clear
    - ❌ Long descriptive names that repeat context

## Modules

### Backend


Monolith build with go and resides in apps/backend

#### System Architecture

##### High-Level Modules

**Core Processing Pipeline:**
- **Input Gateway**: Receives raw input from multiple sources (voice, text, integrations) → *Input: raw data from various sources* → *Output: normalized message format*
- **Content Extractor** (Current MVP): Analyzes text and extracts structured insights → *Input: normalized text* → *Output: JSON with categorized content, emotions, entities*
- **Decision Engine**: Determines appropriate actions based on extracted content and user profile → *Input: extracted content + user profile* → *Output: ordered list of actions to execute*
- **Action Orchestrator**: Coordinates and executes actions in the correct sequence → *Input: action list* → *Output: execution results and confirmations*

**Knowledge & Profile:**
- **Profile Builder**: Continuously updates user's personality profile from interactions → *Input: extracted insights* → *Output: updated user profile (traits, preferences, patterns)*
- **Knowledge Base**: Stores and retrieves user's ideas, notes, goals, and historical data → *Input: categorized content* → *Output: stored items with relationships*
- **Context Provider**: Supplies relevant context for decision-making → *Input: current situation query* → *Output: relevant profile data, history, and external context*

**Action Modules:**
- **Note Manager**: Creates and organizes notes and thoughts → *Input: note content + metadata* → *Output: stored note with categorization*
- **Task Scheduler**: Creates tasks, reminders, and calendar events → *Input: task details + timing* → *Output: scheduled item confirmation*
- **Communication Handler**: Drafts and sends emails, messages → *Input: message content + recipient* → *Output: sent confirmation*
- **Idea Collector**: Manages business ideas and creative thoughts → *Input: idea content + category* → *Output: stored idea with tags*

**Integration Layer:**
- **Channel Adapters**: Connects with WhatsApp, Telegram, email, calendar APIs → *Input: external service events* → *Output: normalized messages to Input Gateway*
- **Response Router**: Sends responses back through appropriate channels → *Input: response content + destination* → *Output: delivered message*

##### System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     External Sources                        │
│  [WhatsApp]  [Telegram]  [Email]  [Voice]  [Calendar]      │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Input Gateway                          │
│                 (Normalizes all inputs)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Content Extractor (MVP)                   │
│        (Extracts insights, emotions, categories)            │
└─────────────┬───────────────────────┬───────────────────────┘
              │                       │
              ▼                       ▼
┌──────────────────────┐    ┌────────────────────────────────┐
│   Profile Builder    │    │      Decision Engine           │
│  (Updates user       │◄───│   (Determines actions based    │
│   profile over time) │    │    on content + profile)       │
└──────────────────────┘    └────────────┬───────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────┐
              │                          ▼                  │
              │            ┌──────────────────────┐         │
              │            │  Action Orchestrator │         │
              │            │  (Executes actions)  │         │
              │            └──────────┬───────────┘         │
              │                       │                     │
              ▼                       ▼                     ▼
┌──────────────────────────────────────────────────────────────┐
│                     Action Modules                           │
│  [Note Manager] [Task Scheduler] [Communication] [Ideas]     │
└──────────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Knowledge Base                            │
│         (Central storage for all user data)                  │
└──────────────────────────────────────────────────────────────┘
```

**Multi-module System:**
- **Core Engine**: Content extraction and profile building (Go/PostgreSQL/OpenAI)
- **Admin Interface**: View insights, manage categories, adjust settings
- **Frontend**: Mobile-first interface for quick input and profile viewing
- **Integration Layer**: Connects with WhatsApp, Telegram, calendar, email

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
