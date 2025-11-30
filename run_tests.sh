#!/bin/bash
# Test runner script for the messaging application

echo "Installing test dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Running tests..."
echo "=================="
pytest test_app.py -v --tb=short

echo ""
echo "Test run complete!"

