#!/bin/bash
# Run the test-runner server

# Get the test-runner directory (parent of scripts)
TEST_RUNNER_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$TEST_RUNNER_DIR"

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
echo "Starting test-runner on port 8081..."
export PYTHONPATH="$TEST_RUNNER_DIR"
uvicorn main:app --host 0.0.0.0 --port 8081 --reload