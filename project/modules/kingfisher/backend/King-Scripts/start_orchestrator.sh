#!/bin/bash

# Start King Orchestration Agent
echo "========================================="
echo "  STARTING KING ORCHESTRATION AGENT"
echo "========================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
source ../venv/bin/activate

# Install requirements if needed
pip install -q flask flask-cors python-dotenv aiohttp watchdog

# Start the orchestrator
echo "Starting orchestration agent..."
echo "API will be available at: http://localhost:5555"
echo ""
python3 KING_ORCHESTRATION_AGENT.py