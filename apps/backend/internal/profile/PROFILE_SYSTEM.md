# Profile System Documentation

## Overview
The Profile Service maintains a living, evolving text-based representation of the user's personality, interests, goals, and personal information. It continuously learns from user inputs and intelligently updates the profile using LLM-powered extraction and natural language processing.

## Core Concept
The profile is stored as **plain text narrative** (not structured data) that reads naturally:
```
I'm Kira, russian, living in Buenos Aires for the last 8 months. 
I like cats. I do carnivore diet and love learning spanish.
```

When the user provides new input, the system:
1. Extracts relevant information based on predefined targets
2. Compares against existing profile
3. Updates only with new or changed information
4. Maintains natural narrative flow

## Architecture

### Component Interaction
```
User Input → ProfileService → LLMService → Updated Profile
                    ↓              ↓
              [Extraction]    [Processing]
              Targets         & Comparison
```

### Key Components

#### ProfileService (`profile.go`)
- **Purpose**: Manages the user's profile state
- **Storage**: In-memory string (MVP - single user)
- **Thread Safety**: Uses sync.RWMutex for concurrent access
- **Methods**:
  - `Get()`: Returns current profile
  - `ProcessInput()`: Updates profile based on new user input

#### LLMService Integration
The ProfileService delegates the intelligent processing to LLMService, which:
1. **Extraction**: Identifies relevant information from user input
2. **Comparison**: Determines what's new or updated
3. **Blending**: Integrates changes into natural narrative

## Extraction Targets

The system looks for specific categories of information:

| Target | Description | Example |
|--------|-------------|---------|
| `personal_info` | Name, age, location, nationality, occupation | "I'm 28, moved to Moscow" |
| `interests` | Hobbies, activities, preferences | "Started learning guitar" |
| `goals` | Aspirations, things to achieve or learn | "Want to run a marathon" |
| `personality` | Traits, values, communication style | "I'm an early bird" |

## Processing Flow

### Empty Profile Scenario
```
Input: "I'm Kira, I live in Buenos Aires"
Profile: "" (empty)
Action: Extract all relevant information
Result: "I'm Kira. I live in Buenos Aires."
```

### Existing Profile Scenario
```
Input: "Just moved to Moscow, feeling excited"
Profile: "I'm Kira, living in Buenos Aires for 8 months..."
Action: Extract only the location change
Result: "I'm Kira, living in Moscow..." (Buenos Aires replaced)
```

### Irrelevant Input Handling
```
Input: "Send email to Joe"
Profile: (unchanged)
Action: No extraction targets match
Result: Profile remains the same
```

## LLM Extraction Logic

The `extractStructuredData` method in LLMService operates in two modes:

### Mode 1: Empty Profile
- Extracts any information matching the targets
- No comparison needed
- Creates initial profile content

### Mode 2: Existing Profile
- Compares input against current profile
- Only extracts:
  - **New information**: Not present in profile
  - **Updated information**: Contradicts or updates existing facts
- Ignores already known information

## Example Workflow

1. **User says**: "I'm feeling good today. I recently moved to Moscow. Still love my cats."

2. **System analyzes**:
   - "feeling good today" → No extraction (temporary state)
   - "moved to Moscow" → Extract location update
   - "love my cats" → No extraction (already known)

3. **Profile updates**:
   - Before: "I'm Kira, living in Buenos Aires... I like cats..."
   - After: "I'm Kira, living in Moscow... I like cats..."

## Design Principles

1. **Natural Language**: Profile reads as flowing narrative, not bullet points
2. **Factual Only**: No assumptions or interpretations
3. **Incremental Learning**: Each input potentially enriches the profile
4. **Intelligent Updates**: Only meaningful changes trigger updates
5. **Thread-Safe**: Supports concurrent read/write operations