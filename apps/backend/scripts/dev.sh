#!/bin/bash
# Runs the backend server in development mode with hot reload using air

echo "🚀 Starting Soul Mirror backend in development mode..."
echo "✓ Hot reload enabled with air"
echo "✓ Server will run on :8080"
echo ""

# Set air binary path
AIR_BIN="$(go env GOPATH)/bin/air"

# Check if air is installed
if [ ! -f "$AIR_BIN" ]; then
    echo "⚠️  Air is not installed. Installing..."
    go install github.com/air-verse/air@latest
fi

# Run air for hot reload
"$AIR_BIN"