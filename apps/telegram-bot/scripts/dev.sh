#!/bin/bash

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copy .env.example and configure:"
    echo "   cp .env.example .env"
    echo "   # Edit .env and add your TELEGRAM_BOT_TOKEN"
    exit 1
fi

echo "🤖 Starting Telegram bot in dev mode..."
echo ""

source .env
export TELEGRAM_BOT_TOKEN
export BACKEND_URL
export OPENAI_API_KEY

python3 main.py
