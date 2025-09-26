# Soul Mirror

Your personal AI that learns who you are through your thoughts and helps you become who you want to be.

Just voice message your random thoughts, and Soul Mirror builds a living profile of your personality, goals, and growth areas. It becomes the friend who remembers everything and nudges you at exactly the right moments.

**Example scenarios:**
- Text "feeling overwhelmed with work again" → Gets reminded of your meditation goal before your next stressful meeting
- Voice note "had this cool app idea about plant care" → Gets organized with your other creative projects and surfaced when you have free coding time  
- Random thought "want to be better at listening" → Gets gentle reminders before important conversations with friends
- Mumble "should probably eat healthier" → Gets personalized suggestions based on your taste preferences and schedule

## Backend

### Development

```bash
cd apps/backend

# Setup environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run server with hot reload
./scripts/dev.sh

# Build check
./scripts/build.sh

# Format code
./scripts/format.sh
```

### API Endpoints

- `GET /health` - Health check
- `GET /process?input=your+thought+here` - Process user input
- `GET /profile` - Get current profile (plain text)

### Architecture

Core components:
- **Orchestrator** - Main workflow coordinator
- **LLMService** - Anthropic Claude integration for intelligent tool selection
- **ToolService** - Registry of available tools
- **ProfileService** - Simple plain text user profile

### Configuration

Required environment variables:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - deployment environment (default: development)