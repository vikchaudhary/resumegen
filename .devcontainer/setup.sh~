#!/bin/bash

# Set script to exit on error
set -e

# Navigate to backend directory and start the backend
echo "Starting backend..."
cd backend || exit
nohup python3 app.py > backend.log 2>&1 &

# Navigate to frontend directory
cd ../frontend || exit

# Build the frontend
echo "Building frontend..."
npm run build
npm install -g serve

# Serve the frontend
echo "Starting frontend..."
nohup serve -s build -l 3000 > frontend.log 2>&1 &

echo "Deployment successful!"
echo "Backend running in the background. Logs: backend.log"
echo "Frontend running at http://localhost:3000"
