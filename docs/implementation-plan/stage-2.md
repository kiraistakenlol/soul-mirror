# Stage 2: Real LLM Integration

## Overview

Replace mock LLMService with real LLM integration for intelligent tool selection and text processing.

## Goals

1. **Real LLM Integration** - Connect to actual LLM API (OpenAI/Anthropic/local)
2. **Smart Tool Selection** - LLM analyzes input and selects appropriate tools with reasoning
3. **Enhanced Profile Processing** - LLM extracts insights from user input for profile updates
4. **Configuration Management** - Environment-based LLM provider switching

## Implementation Plan

### 1. LLM Provider Interface

Create abstraction for different LLM providers:

```go
type LLMProvider interface {
    Complete(prompt string) (string, error)
    SelectTools(input string, tools []ToolDescriptor) ([]ToolSelection, error)
}
```

Implementations:
- OpenAI provider
- Anthropic provider  
- Local LLM provider (ollama)
- Mock provider (for testing)

### 2. Configuration System

Environment-based configuration:
- `LLM_PROVIDER` (openai|anthropic|local|mock)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `LOCAL_LLM_URL`

### 3. Enhanced LLMService

Replace mock logic with real LLM calls:

**Tool Selection:**
- Analyze user input semantically
- Match with tool descriptions intelligently
- Provide detailed reasoning for selections
- Support multi-tool workflows

**Profile Processing:**
- Extract personality insights
- Identify goals and interests
- Categorize input types (reflection, task, idea, etc.)
- Generate structured profile updates

### 4. New Tools

Add more useful tools:
- **Note Tool** - Save important thoughts
- **Task Tool** - Create actionable items
- **Reflection Tool** - Process self-reflection
- **Search Tool** - Find previous entries

### 5. Prompt Engineering

Create effective prompts for:
- Tool selection with context
- Profile analysis and updates
- Response generation
- Multi-tool orchestration

## Directory Structure Changes

```
internal/
├── llm/
│   ├── llm.go           # Core service
│   ├── providers/       # LLM provider implementations
│   │   ├── openai.go
│   │   ├── anthropic.go
│   │   ├── local.go
│   │   └── mock.go
│   ├── prompts/         # Prompt templates
│   └── config.go        # Configuration
├── tools/
│   ├── registry.go
│   ├── echo.go
│   ├── note.go          # New tools
│   ├── task.go
│   └── reflection.go
└── config/              # App configuration
    └── config.go
```

## Success Criteria

- [ ] Real LLM provider integration working
- [ ] Intelligent tool selection based on semantic analysis
- [ ] Enhanced profile updates with LLM insights
- [ ] Multiple useful tools implemented
- [ ] Environment-based configuration
- [ ] Comprehensive prompt templates
- [ ] Graceful fallback to mock when LLM unavailable

## API Changes

No breaking changes to existing endpoints. Enhanced responses:

- `/process` returns LLM-generated insights
- `/profile` shows richer, LLM-analyzed profile content
- New `/tools` endpoint to list available tools

## Testing Strategy

- Unit tests for each LLM provider
- Integration tests with real API calls
- Mock provider for CI/CD pipeline
- Load testing with LLM rate limits

**Target: Production-ready LLM integration with intelligent tool orchestration**