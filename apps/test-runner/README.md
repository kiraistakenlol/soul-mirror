# Test Runner

## Problem

Validating prompt effectiveness is hard without systematic testing. Need to verify that:
- Agent correctly extracts profile information from user inputs
- Agent maintains consistent behavior across conversation sequences
- Profile updates work correctly (additions, contradictions, removals)
- Agent personalizes responses using profile context

Manual testing is slow, inconsistent, and doesn't scale as prompt evolves.

## Solution

Automated scenario-based testing with LLM evaluation:
1. Define test scenarios: input sequences + expected profile outcomes
2. Run scenarios against main backend via HTTP
3. Compare actual profile with expected profile using LLM
4. Generate structured test results

## Architecture

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

### Components

**test_scenarios.json**
Defines test cases with input sequences and expected outcomes

**runner.py**
Orchestrates scenario execution:
- Reset backend state
- Send input sequence to `/api/process`
- Fetch resulting profile via `/api/profile`
- Pass to evaluator

**evaluator.py**
Uses LLM to compare actual vs expected profile:
- Prompt asks LLM to evaluate match
- Returns pass/fail + reasoning
- Handles fuzzy matching (synonyms, paraphrasing)

**main.py**
FastAPI service exposing `/api/run-tests`

### Test Scenario Format

```json
{
  "name": "Basic preference learning",
  "description": "Agent should extract and store user preference",
  "inputs": [
    "I love surfing",
    "What do you know about me?"
  ],
  "profileExpectations": "Should contain information that user loves surfing"
}
```

### Evaluation Strategy

LLM evaluator receives:
- Actual profile notes (from `/api/profile`)
- Expected profile criteria
- Test scenario context

Returns structured evaluation:
```json
{
  "passed": true,
  "reasoning": "Profile contains [PROFILE] note about loving surfing",
  "missing": [],
  "unexpected": []
}
```

## Usage

```bash
# Start main backend (already running in dev)
# Main backend on :8080

# Run tests
cd apps/test-runner
python main.py  # Starts on :8081

# Execute tests via HTTP
curl http://localhost:8081/api/run-tests

# Or run specific scenario
curl http://localhost:8081/api/run-tests?scenario=preference_learning
```

## Future Extensions

- Multiple scenario categories (profile, tasks, contradictions, personalization)
- Performance benchmarks (response time, tool usage)
- Regression testing in CI/CD
- Comparative testing across different prompts
- Test coverage reporting