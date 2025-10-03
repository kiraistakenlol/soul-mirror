# Soul Mirror - React Frontend

Modern React frontend for Soul Mirror personal assistant.

## Tech Stack

- react (19.x)
- vite (dev server & build)
- tailwindcss (styling)

## Setup

```bash
# Install dependencies
npm install

# Copy environment config
cp .env.example .env

# Start dev server (port 3000)
npm run dev
```

## Development

```bash
# Dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Edit `.env` to configure API base URL:

```
VITE_API_BASE=http://localhost:8080
```

## Architecture

```
src/
├── components/          # React components
│   ├── Header.jsx       # Header with status
│   ├── NotesList.jsx    # Notes list with auto-refresh
│   ├── ChatInput.jsx    # Input interface
│   ├── ConversationHistory.jsx  # Conversation display
│   └── ResponseDisplay.jsx  # Latest response
├── services/
│   └── api.js           # API service layer
├── App.jsx              # Main app component
└── index.css            # Global styles (Tailwind)
```

## Features

- Auto-refresh notes (10s interval)
- Auto-refresh status (30s interval)
- Keyboard shortcuts (Enter = submit, Esc = clear)
- Responsive 3-column layout
- Dark theme with Tailwind
