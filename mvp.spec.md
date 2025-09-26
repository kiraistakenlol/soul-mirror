# MVP Specification: Content Extractor

## Overview

Takes text input and returns structured JSON with extracted insights.

## API Endpoint

**POST** `/api/extract`

## Input Format

```json
{
  "text": "string"
}
```

## Output Format

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

## Field Descriptions

### content_type
`self-reflection|idea|task|goal|todo-list|thought`

### personality_insights
- traits
- interests
- values
- location_mentions
- self_improvement_areas

### actionable_items
- type: `reminder|todo|task`
- content
- context (optional)
- priority: `low|medium|high` (optional)
- deadline (optional)

### goals
- type: `short-term|long-term`
- content
- deadline
- progress_indicator

### emotional_state
- mood
- sentiment: `positive|neutral|negative`
- energy: `low|medium|high`

### categories
Topic categories

### confidence
0-1

## Example Use Cases

### Example 1: Self-Reflection
**Input:**
```
"I've been thinking that I talk too much about my plans in meetings. I should listen more and execute more. Maybe I need to be more mindful about this before important conversations."
```

**Output:**
```json
{
  "content_type": "self-reflection",
  "personality_insights": {
    "traits": ["self-aware", "communicative"],
    "self_improvement_areas": ["listen more", "execute more", "talk less about plans"]
  },
  "actionable_items": [
    {
      "type": "reminder",
      "content": "Be mindful about listening more",
      "context": "before important conversations"
    }
  ],
  "emotional_state": {
    "mood": "reflective",
    "sentiment": "neutral",
    "energy": "medium"
  },
  "categories": ["self-improvement", "communication"],
  "confidence": 0.92
}
```

### Example 2: Task List
**Input:**
```
"I need to finish the project proposal by next Monday, send the invoice to the client, and also remember to buy groceries on the way home."
```

**Output:**
```json
{
  "content_type": "todo-list",
  "actionable_items": [
    {
      "type": "todo",
      "content": "Finish project proposal",
      "priority": "high",
      "deadline": "2024-01-15"
    },
    {
      "type": "todo",
      "content": "Send invoice to client",
      "priority": "medium"
    },
    {
      "type": "reminder",
      "content": "Buy groceries",
      "context": "on the way home"
    }
  ],
  "emotional_state": {
    "mood": "focused",
    "sentiment": "neutral",
    "energy": "high"
  },
  "categories": ["work", "personal"],
  "confidence": 0.88
}
```

## Implementation Notes

- The extractor uses OpenAI's GPT API for natural language understanding
- Confidence scores below 0.7 should trigger a review or clarification request
- All dates should be parsed and normalized to ISO format
- The system should handle multiple languages (initially English and Spanish)