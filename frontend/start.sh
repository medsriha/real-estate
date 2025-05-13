#!/bin/bash

# Change to the frontend directory
cd "$(dirname "$0")"

# Install dependencies if node_modules doesn't exist or is empty
if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules 2>/dev/null)" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the React development server
echo "Starting frontend development server..."
npm start