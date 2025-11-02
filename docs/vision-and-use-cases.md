# Soul Mirror: Vision and Use Cases

## Core Philosophy

Soul Mirror is designed to feel like working with a real human assistant who learns about you over time, self-regulates their work, and uses available tools autonomously to accomplish tasks.

### Human Assistant Model

Like a real assistant:
- You explain what you need in plain English
- Sometimes clarifications are needed (back-and-forth)
- They learn from mistakes and refine understanding
- Eventually errors decrease as they know you better
- They remember who you are without constant reminders
- They manage their own notebook and tools to stay organized

### Self-Regulating Agent

The agent:
- Decides when to update memory based on significance
- Chooses which tools to use for each task
- Organizes information following common sense principles
- Creates/updates/deletes workflows (responsibilities) autonomously
- Checks capabilities before accepting new responsibilities
- Asks for clarification when needed, not confirmation for every action

## Core Components

### 1. Long-term Memory (Brain)
**Current state: Implemented**

How human memory works:
- Associative and context-triggered
- Not everything active at once, but right things surface when relevant
- Gradually consolidates over time
- Some details fade but essence remains

Implementation:
- Core memory: always-loaded understanding of who you are
- Updates naturally through conversation
- Plain English, not structured data
- Agent decides when significant enough to update

### 2. Responsibilities (Workflows as Plain Text)
**Current state: Not implemented**

Instead of hardcoded features, users teach the agent new behaviors:

```
You: "I want you to handle my daily meditation texts. Each morning
     generate a stoic-inspired passage, convert to audio, and post
     to my Telegram channel"

Agent: *Creates responsibility*
       "Got it - I'll handle daily meditation texts.
        I can: generate text ✓, create audio ✓, post to Telegram ✓
        Just tell me when you want one, or should I do this automatically?"

You: "Automatically at 7am Bali time"

Agent: *Updates responsibility with schedule*
       "Starting tomorrow, I'll send meditation texts at 7am Bali time"
```

Storage: Plain English descriptions, not structured workflows
- What the assistant is responsible for
- How they should do it
- When (if scheduled)
- Any clarifications from conversations

### 3. Notes (Notebook)
**Current state: Implemented**

Specific facts, tasks, details that need precision
- Referenced when needed for exact information
- Organized in semantic groups
- Agent maintains cleanliness proactively

### 4. Available Capabilities (Tool Registry)
**Current state: Partial - only notebook tools**

Generic reusable tools that enable wide variety of tasks:
- LLM generation (custom prompts, styles, topics)
- Text-to-speech (ElevenLabs)
- File storage (local with metadata)
- Telegram posting (messages + files)
- Scheduling (time-based tasks)
- Resource linking (connect related items)

Agent checks capabilities before accepting responsibilities:
```
You: "Generate daily Spanish vocabulary flashcards with audio"
Agent: "I can generate text ✓ and audio ✓, but I don't have flashcard
        storage yet. Should I just send them to Telegram for now?"
```

## Use Cases

### 1. Daily Meditation Texts
**Priority: High - demonstrates core workflow pattern**

**Description:**
Generate daily stoic/philosophical texts for self-development, convert to audio, save locally, and post to Telegram channel.

**Workflow:**
1. User explains the routine once in natural language
2. Agent creates responsibility with these steps:
   - Generate text using LLM (stoic style, short passage)
   - Convert to audio using text-to-speech
   - Save both text + audio with metadata
   - Link text and audio together
   - Post to Telegram channel
3. Can be triggered on-demand ("generate meditation about focus") or scheduled (7am daily)

**Example interaction:**
```
You: "I read self-help books like Marcus Aurelius. Each morning I want
     a short philosophical text I can write down and memorize. Also
     create audio so I can practice English listening"

Agent: *Checks capabilities*
       *Creates responsibility for meditation text generation*
       "I'll handle your daily meditation texts. Want me to send them
        at a specific time, or just when you ask?"

You: "7am Bali time"

Agent: *Updates responsibility with schedule*
       "Starting tomorrow at 7am Bali time"

[Next day, 7am]
Agent: *Executes workflow automatically*
       *Posts to Telegram*

[Later]
You: "Generate a new text about stop pleasing people"

Agent: *Recognizes trigger phrase*
       *Executes workflow with topic: "stop pleasing people"*
```

**Tools needed:**
- `llm_generate(prompt, style, length)` - Generate custom text
- `text_to_speech(text, voice)` - Create audio file
- `store_file(content, type, metadata)` - Save to local storage
- `link_resources(resource_ids)` - Connect text + audio
- `telegram_post(content, file)` - Post to channel
- `schedule_task(time, workflow)` - Time-based execution

**Reusability:**
Same tools can handle:
- Spanish vocabulary practice
- Daily journal prompts
- Quote generation for Instagram
- Podcast script drafts

### 2. Spanish Vocabulary Tracking
**Priority: Medium - tests reusability**

**Description:**
Generate Spanish texts, track vocabulary learning, create audio for pronunciation practice.

**Workflow:**
Similar to meditation texts but:
- Different language and style
- Track learned vocabulary in notes
- Difficulty progression over time

**Example:**
```
You: "I want to learn Spanish. Generate daily texts that help expand
     my vocabulary. Track what I've learned"

Agent: *Reuses: LLM generation, TTS, file storage*
       *Creates responsibility: Spanish vocabulary practice*
       *Creates note group: Spanish Vocabulary (tracks learned words)*

       "I'll generate daily Spanish texts and track your vocabulary.
        Should I start easy or intermediate level?"
```

**Additional tools:**
- Same as meditation texts
- Uses notes to track vocabulary

### 3. Scheduled Reminders
**Priority: High - common pattern**

**Description:**
Send reminders at specific times via Telegram.

**Example:**
```
You: "Remind me daily at 7am Bali time to stop trying to please people"

Agent: *Creates scheduled responsibility*
       *Adds to scheduled tasks*
       "I'll send you that reminder every morning at 7am Bali time"
```

**Tools needed:**
- `schedule_task(time, message)` - Time-based execution
- `telegram_send(message)` - Send to Telegram

### 4. Voice Input Processing
**Priority: High - already partially working**

**Description:**
Process voice messages via Telegram, transcribe, and handle like text input.

**Current state:** Basic implementation exists in telegram-bot
**Enhancement needed:** Agent should remember it's handling transcribed voice

**Example:**
```
[Voice message in Telegram]
Agent: *Transcribes via Whisper*
       *Processes: "remind me to call mom tomorrow"*
       *Creates note + responds*
       "Added reminder to call mom tomorrow"
```

### 5. Content Generation Workflows
**Priority: Medium - demonstrates extensibility**

**Description:**
Generate content for various platforms (Instagram, blog, etc.) with consistent voice based on user personality.

**Example:**
```
You: "I want to post stoic quotes to Instagram. Generate quote +
     visual description"

Agent: *Checks memory: knows you like stoicism*
       *Creates responsibility: Instagram quote generation*
       "I can generate quotes based on your stoic interests. Want me
        to also suggest caption text?"
```

**Future tools needed:**
- `image_generate(description)` - Create visual content
- `format_for_platform(content, platform)` - Platform-specific formatting

### 6. Journaling to Instagram
**Reference:** `/docs/ideas/jourling-to-instagram.md`

**Description:**
Transform journal entries into Instagram posts while maintaining privacy and authenticity.

**Workflow:**
1. User journals naturally (voice or text)
2. Agent identifies shareable insights
3. Generates Instagram-appropriate version
4. Posts with proper formatting

### 7. Habit Tracking
**Priority: Low - simple pattern**

**Description:**
Track habits and send check-in reminders.

**Example:**
```
You: "I want to meditate daily. Check in with me each evening"

Agent: *Creates responsibility: meditation habit tracking*
       *Schedules daily check-in at evening*
       *Tracks completion in notes*
```

## Implementation Strategy

### Phase 1: Core Infrastructure ✓
- [x] Core memory (implemented)
- [x] Notes system (implemented)
- [x] Basic agent with tools (implemented)

### Phase 2: Responsibilities System
- [ ] Database table for responsibilities (plain text)
- [ ] Agent tools: manage_responsibilities
- [ ] Agent behavior: recognize when user describing new responsibility
- [ ] Agent behavior: check capabilities before accepting
- [ ] Agent behavior: execute responsibilities when triggered

### Phase 3: Essential External Tools
- [ ] LLM generation tool (call LLM with custom prompts)
- [ ] Text-to-speech tool (ElevenLabs integration)
- [ ] File storage tool (local storage with metadata)
- [ ] Resource linking tool (connect related items)
- [ ] Telegram posting tool (send messages/files)

### Phase 4: Scheduling
- [ ] Scheduling tool (time-based task execution)
- [ ] Background job runner
- [ ] Timezone handling

### Phase 5: Advanced Capabilities
- [ ] Image generation
- [ ] Platform-specific formatting
- [ ] Multi-step workflow chaining

## Design Principles

**Conversational Configuration:**
- No config files or UI forms
- Everything taught through natural language
- Back-and-forth refinement when needed

**Plain Text Everything:**
- Workflows stored as English descriptions
- Memory stored as natural language
- No rigid schemas or structured formats

**Agent Autonomy:**
- Agent decides when to update memory
- Agent creates/modifies responsibilities
- Agent chooses which tools to use
- Never asks for confirmation, only clarification

**Graceful Degradation:**
- Missing capabilities don't break system
- Agent asks user what to do instead
- Can add capabilities over time

**Reusability:**
- Generic tools, specific applications
- Same tools for meditation, Spanish, reminders, etc.
- Workflows are configuration, not code

## Success Metrics

**Feels human when:**
- You can describe complex workflows in one message
- Agent asks for clarification when ambiguous, not confirmation for actions
- Same tools work for completely different use cases
- Agent "just knows" things about you without searching
- Errors decrease over time as agent learns your patterns
- You can correct behavior conversationally ("actually, make it Spanish instead")

**Working well when:**
- Users teach agent new behaviors without code changes
- Agent proactively organizes information
- Memory updates feel natural and accurate
- Scheduled tasks execute reliably
- External tool integration is seamless
