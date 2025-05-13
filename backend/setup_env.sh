#!/bin/bash

# Script to set up the Python environment using uv

# Change to the backend directory
cd "$(dirname "$0")"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it using:"
    echo "pip install uv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Created virtual environment using standard venv module"
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# Install base dependencies using uv
echo "Installing dependencies using uv..."
uv uv add -r requirements.txt --python 3.11

# Check if we should install dev dependencies
if [ "$1" == "dev" ]; then
    echo "Installing development dependencies..."
    uv pip install -r requirements/dev.txt --python 3.11
fi

echo "Environment setup complete."
echo "You can activate the virtual environment with:"
echo "source .venv/bin/activate" 