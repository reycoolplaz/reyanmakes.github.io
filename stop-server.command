#!/bin/bash
echo "Stopping Reyan Makes server..."
pkill -f "server.py" 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null
echo "Server stopped."
sleep 1
