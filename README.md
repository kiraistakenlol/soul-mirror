# Soul Mirror

A personal intelligence system that learns who you are through your thoughts and helps you become who you want to be.

## MVP: Content Extractor

The Content Extractor module takes raw text input and returns structured JSON with extracted insights about:

- **Content Type**: self-reflection, idea, task, goal, todo-list, random thought
- **Personality Insights**: traits, values, interests revealed in the text
- **Actionable Items**: tasks, reminders, follow-up actions, todo items
- **Goal Tracking**: short-term goals, deadlines, progress indicators
- **Emotional State**: mood, sentiment, energy level
- **Categories**: topics, themes, areas of life discussed

### Input Format
```
Raw text from voice-to-text conversion
```

### Output Format
```json
{
  "content_type": "self-reflection|idea|task|goal|todo-list|thought",
  "personality_insights": {
    "traits": ["analytical", "creative"],
    "interests": ["technology", "reading"],
    "values": ["efficiency", "growth"],
    "location_mentions": ["Buenos Aires"],
    "self_improvement_areas": ["talk less about plans"]
  },
  "actionable_items": [
    {
      "type": "reminder",
      "content": "Talk less about plans",
      "context": "before meetings"
    },
    {
      "type": "todo",
      "content": "Finish project proposal",
      "priority": "high",
      "deadline": "2024-01-15"
    }
  ],
  "goals": [
    {
      "type": "short-term",
      "content": "Read 2 books this month",
      "deadline": "2024-01-31",
      "progress_indicator": "0/2 books completed"
    }
  ],
  "emotional_state": {
    "mood": "reflective",
    "sentiment": "positive",
    "energy": "medium"
  },
  "categories": ["self-improvement", "communication"],
  "confidence": 0.85
}
```

## Setup

1. Copy `.env.example` to `.env` and fill in your values
2. Set up PostgreSQL database
3. Run: `go run main.go`

## Deployment

Simple deployment to a private virtual machine in the cloud using Docker containerization.

## Architecture

```
/
├── main.go                 # HTTP server entry point
├── internal/
│   ├── extractor/         # Content Extractor module
│   │   ├── extractor.go   # Main extraction logic
│   │   └── openai.go      # OpenAI API integration
│   ├── database/          # Database layer
│   │   └── postgres.go    # PostgreSQL operations
│   └── handlers/          # HTTP handlers
│       └── api.go         # API endpoints
└── migrations/            # Database migrations
    └── 001_init.sql
```