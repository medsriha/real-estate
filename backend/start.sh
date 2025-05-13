#!/bin/bash

# Change to the backend directory
cd "$(dirname "$0")"

# Create required directories
mkdir -p data logs/backend

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run ./setup_env.sh first."
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Run the API server 
echo "Starting backend server with uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload