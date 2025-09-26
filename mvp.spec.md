# MVP Specification: Content Extractor

## Overview

The Content Extractor module is the MVP for Soul Mirror. It takes raw text input (typically from voice-to-text conversion) and returns structured JSON with extracted insights about personality, actionable items, goals, emotions, and categories.

## API Endpoint

**POST** `/api/extract`

## Input Format

```json
{
  "text": "Raw text from voice-to-text conversion"
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
- **Type**: `string` (enum)
- **Values**: `self-reflection`, `idea`, `task`, `goal`, `todo-list`, `thought`
- **Description**: Primary classification of the input content

### personality_insights
- **traits**: Character traits revealed in the text
- **interests**: Topics or activities the person shows interest in
- **values**: Core values or principles expressed
- **location_mentions**: Geographic locations mentioned
- **self_improvement_areas**: Areas where the person wants to improve

### actionable_items
Array of items that require action:
- **type**: `reminder`, `todo`, `task`
- **content**: The actual action item
- **context**: When/where this applies (optional)
- **priority**: `low`, `medium`, `high` (optional)
- **deadline**: ISO date format (optional)

### goals
Array of identified goals:
- **type**: `short-term`, `long-term`
- **content**: Description of the goal
- **deadline**: Target completion date
- **progress_indicator**: Current progress (if mentioned)

### emotional_state
- **mood**: Current emotional state (`reflective`, `excited`, `anxious`, etc.)
- **sentiment**: `positive`, `neutral`, `negative`
- **energy**: `low`, `medium`, `high`

### categories
Array of relevant topic categories the content belongs to

### confidence
Float between 0-1 indicating the extraction confidence level

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