#!/bin/bash

# Navigate to frontend directory
cd frontend || exit

# Build the frontend
echo "Building frontend..."
npm run build
npm install -g serve

serve -s build -l 3000

echo "Frontend deployed!"
echo "Backend running in the background. Logs: backend.log"
echo "Frontend running at http://localhost:3000"
