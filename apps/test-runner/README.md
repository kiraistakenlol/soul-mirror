# Test Runner

## Problem

Validating prompt effectiveness is hard without systematic testing. Need to verify that:
- Agent correctly organizes notes into groups
- Agent maintains consistent behavior across conversation sequences
- Notes updates work correctly (additions, contradictions, removals)
- Agent properly categorizes information into appropriate groups

Manual testing is slow, inconsistent, and doesn't scale as prompt evolves.

## Solution

Automated scenario-based testing with LLM evaluation:
1. Define test scenarios: input sequences + expected notes outcomes
2. Run scenarios against main backend via HTTP
3. Compare actual notes with expected notes using LLM
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
│  /api/notes         │
│  /api/reset         │
└─────────────────────┘
```

### Components

**test_scenarios.json**
Defines test cases with input sequences and expected outcomes

**runner.py**
Orchestrates scenario execution:
- Create unique user_id per test (no reset needed)
- Send input sequence to `/api/process`
- Fetch resulting notes via `/api/notes`
- Pass to evaluator

**evaluator.py**
Uses LLM to compare actual vs expected notes:
- Prompt asks LLM to evaluate match
- Returns pass/fail + reasoning
- Handles fuzzy matching (synonyms, paraphrasing)

**main.py**
FastAPI service exposing `/api/run-tests`

### Test Scenario Format

```json
{
  "name": "Base extraction",
  "inputs": [
    "I love surfing"
  ],
  "notesExpectations": "Has note about loving surfing in appropriate group (Interests or similar)"
}
```

### Evaluation Strategy

LLM evaluator receives:
- Actual notes data (from `/api/notes`)
- Expected notes criteria
- Test scenario context

Returns structured evaluation:
```json
{
  "passed": true,
  "reasoning": "Notes contain entry about loving surfing in Interests group",
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

- Multiple scenario categories (groups, tasks, contradictions, organization)
- Performance benchmarks (response time, tool usage)
- Regression testing in CI/CD
- Comparative testing across different prompts
- Test coverage reporting