#!/bin/bash
# Run the Python backend server

# Get the backend directory (parent of scripts)
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"

# Load .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting Soul Mirror backend on port 8080..."
export PYTHONPATH="$BACKEND_DIR"
uvicorn main:app --host 0.0.0.0 --port 8080 --reload --no-access-log