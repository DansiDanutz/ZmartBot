#!/bin/bash

# Start the Professional Dashboard Server
echo "============================================"
echo "Starting ZmartBot Professional Dashboard..."
echo "============================================"

# Navigate to the dashboard directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    echo "Activating virtual environment..."
    source ../venv/bin/activate
fi

# Start the dashboard server
echo "Starting dashboard server on port 3400..."
python start_dashboard.py