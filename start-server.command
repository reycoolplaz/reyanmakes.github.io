#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Reyan Makes server..."
echo "Admin panel: http://localhost:5000/admin"
echo ""
python3 server.py
