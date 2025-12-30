#!/bin/bash

# Activate virtual environment
source venv/bin/activate

if [ "$1" = "prod" ]; then
    echo "Starting production server (Gunicorn)..."
    gunicorn server:app --bind 0.0.0.0:5000 --workers 2
else
    echo "Starting development server (Flask)..."
    echo "Main site: http://localhost:5000"
    echo "Admin panel: http://localhost:5000/admin"
    python server.py
fi
