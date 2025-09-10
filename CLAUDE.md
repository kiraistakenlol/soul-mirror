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

## System Architecture

**Multi-module System:**
- **Core Engine**: Content extraction and profile building (Go/PostgreSQL/OpenAI)
- **Admin Interface**: View insights, manage categories, adjust settings
- **Frontend**: Mobile-first interface for quick input and profile viewing
- **Integration Layer**: Connects with WhatsApp, Telegram, calendar, email

**MVP Focus**: Content Extractor module - takes text input, returns structured JSON with extracted insights

## Development Commands

```bash
go run main.go       # Start development server
go build             # Build binary
go mod tidy          # Clean up dependencies
```

## Core Components

**Content Extractor** (MVP):
- **Input**: Raw text from voice messages
- **Output**: Structured JSON with extracted insights
- **Responsibility**: Analyze and categorize content using OpenAI API

**Future Components**:
- **Personality Profile Builder**: Aggregates insights into comprehensive profile
- **Knowledge Base Manager**: Stores categorized information (ideas, goals, facts)
- **Action Engine**: Processes actionable content, creates reminders
- **Context Provider**: Delivers contextual suggestions based on profile + situation