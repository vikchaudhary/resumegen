#!/bin/bash

# Set script to exit on error
set -e

# Navigate to backend directory and start the backend
echo "Starting backend..."
pip install -r ./backend/requirements.txt --break-system-packages
python3 ./backend/app.py