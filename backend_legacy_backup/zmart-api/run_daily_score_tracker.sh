#!/bin/bash

# Daily Score Tracker Runner
# This script runs the daily score tracking system

# Set the working directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run the daily score tracker
echo "Starting daily score tracking at $(date)"
python daily_score_tracker.py

# Check exit status
if [ $? -eq 0 ]; then
    echo "Daily score tracking completed successfully at $(date)"
else
    echo "Daily score tracking failed at $(date)"
    exit 1
fi
