#!/bin/bash
# Run the Python backend server

# Ensure we're in the right directory
cd "$(dirname "$0")"

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
export PYTHONPATH="$(pwd)"
uvicorn main:app --host 0.0.0.0 --port 8080 --reload