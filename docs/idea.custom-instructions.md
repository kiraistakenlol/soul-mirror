# Custom Instructions

Users can provide free-form custom instructions like "build a list of spanish words that i don't know".

## Implementation

Custom instructions get converted into system settings that affect behavior.

### Content Extractor Extension

Base extraction types:
- tasks
- self reflection insights  
- notes
- ... more

Custom instructions extend this list. Example:
- `unknown-spanish-word-or-phrase`

The decision engine then uses these custom types to take appropriate actions, like maintaining a personalized vocabulary list.