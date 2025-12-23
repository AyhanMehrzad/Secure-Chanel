#!/bin/bash

# Script to running the message app
# Usage: ./run_app.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting Message App..."
cd "$PROJECT_DIR"
source venv/bin/activate

# Run with Gunicorn (Production)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
