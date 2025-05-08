#!/bin/bash

# Define ports
BACKEND_PORT=5001  # Changed from default 5000 to avoid conflicts

# Start the FastAPI backend
echo "Starting backend server on port $BACKEND_PORT..."
uv run api.py --port $BACKEND_PORT 2>&1 | tee -a logs/backend.log &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

# Start the React frontend
echo "Starting frontend server..."
cd .
npm start 2>&1 | tee -a logs/frontend.log &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Create logs directory if it doesn't exist
mkdir -p logs

# Show live logs
echo "Showing backend logs. Press Ctrl+C to stop servers."
tail -f logs/backend.log 