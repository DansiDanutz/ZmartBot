#!/bin/bash

# Start Self-Learning King Orchestration Agent
echo "========================================="
echo "  🧠 STARTING SELF-LEARNING ORCHESTRATOR"
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

# Install ML requirements
echo "Installing ML dependencies..."
pip install -q flask flask-cors python-dotenv aiohttp watchdog
pip install -q scikit-learn pandas numpy scipy

# Create learning directories
mkdir -p learning_data/models

# Start the ML orchestrator
echo ""
echo "Starting Self-Learning Orchestration Agent..."
echo "✨ ML Features Enabled:"
echo "  • Pattern recognition"
echo "  • Adaptive scheduling"
echo "  • Performance optimization"
echo "  • Anomaly detection"
echo ""
echo "📊 Dashboard: Open ml_orchestrator_dashboard.html"
echo "🌐 API: http://localhost:5555"
echo ""
python3 KING_ORCHESTRATION_AGENT_SELF_LEARNING.py