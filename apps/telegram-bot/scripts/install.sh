#!/bin/bash

cd "$(dirname "$0")/.."

echo "📦 Installing Telegram bot dependencies..."
echo ""

pip3 install -r requirements.txt --break-system-packages

echo ""
echo "✓ Installation complete!"
