#!/bin/bash

# Script to running the message app
# Usage: ./run_app.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting Message App..."
cd "$PROJECT_DIR"
source venv/bin/activate

# Check for conflicting process on port 5000
echo "Checking for existing process on port 5000..."
if sudo lsof -i :5000 > /dev/null; then
    echo "Killing process on port 5000..."
    sudo fuser -k 5000/tcp
    sleep 2
fi

# Run with Gunicorn (Production)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
