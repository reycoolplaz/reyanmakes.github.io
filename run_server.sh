#!/bin/bash
# Activate virtual environment and run Flask server

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Activate and run
echo "Starting server with Flask..."
./venv/bin/python server.py
