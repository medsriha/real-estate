#!/bin/bash
# Script to set up a cron job for cache maintenance

# Get the absolute path to the project directory
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SCRIPT_DIR="${PROJECT_DIR}/backend"
SCRIPT_PATH="${SCRIPT_DIR}/clear_cache.py"
LOG_PATH="${PROJECT_DIR}/logs/cron.log"
VENV_PATH="${SCRIPT_DIR}/.venv"

# Ensure the script is executable
chmod +x "$SCRIPT_PATH"

# Create the logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_PATH")"

# Create temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Get existing crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || true

# Check if the job is already in crontab
if grep -q "$SCRIPT_PATH" "$TEMP_CRONTAB"; then
    echo "Cache maintenance job is already in crontab."
    rm "$TEMP_CRONTAB"
    exit 0
fi

# Add the job to run at 2:00 AM daily with the virtual environment
echo "# Real Estate App - Cache maintenance job (runs daily at 2:00 AM)" >> "$TEMP_CRONTAB"
echo "0 2 * * * cd $SCRIPT_DIR && source $VENV_PATH/bin/activate && python $SCRIPT_PATH >> $LOG_PATH 2>&1" >> "$TEMP_CRONTAB"

# Install the updated crontab
if crontab "$TEMP_CRONTAB"; then
    echo "Cache maintenance cron job has been set up successfully!"
    echo "Job will run daily at 2:00 AM and clean expired cache entries (older than 5 days)."
    echo "Logs will be written to: $LOG_PATH"
else
    echo "Failed to set up cron job."
    exit 1
fi

# Clean up
rm "$TEMP_CRONTAB"
echo "To review your crontab, run: crontab -l" 