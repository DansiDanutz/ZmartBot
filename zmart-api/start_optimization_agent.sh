#!/bin/bash

# ZmartBot System Optimization Agent Startup Script
# This script starts the comprehensive optimization integration agent in the background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/optimization_agent.log"
PID_FILE="$SCRIPT_DIR/optimization_agent.pid"

echo "🚀 Starting ZmartBot System Optimization Agent..."
echo "📁 Script Directory: $SCRIPT_DIR"
echo "📝 Log File: $LOG_FILE"
echo "🆔 PID File: $PID_FILE"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Optimization Agent is already running (PID: $PID)"
        echo "   To stop it, run: kill $PID"
        echo "   Or use: ./stop_optimization_agent.sh"
        exit 1
    else
        echo "🧹 Removing stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Start the optimization agent in background
cd "$SCRIPT_DIR"
nohup python3 comprehensive_optimization_integration.py > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

echo "✅ Optimization Agent started successfully!"
echo "🆔 Process ID: $PID"
echo "📝 Logs: tail -f $LOG_FILE"
echo "🛑 To stop: kill $PID or ./stop_optimization_agent.sh"

# Wait a moment and check if it's still running
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Agent is running and healthy"
else
    echo "❌ Agent failed to start. Check logs: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
