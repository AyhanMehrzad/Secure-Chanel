#!/bin/bash
# Start the Flask development server

echo "Starting Secure Messaging App..."
echo "================================"
echo ""
echo "Server will be available at:"
echo "  - Local: http://localhost:5000"
echo "  - Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python3 app.py

