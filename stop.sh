#!/bin/bash

echo "Stopping backend..."
pkill -f "python3 app.py"

echo "Stopping frontend..."
pkill -f "serve"

echo "Deployment stopped."
