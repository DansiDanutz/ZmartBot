#!/bin/bash

# Background Optimization Agent Stop Script
# Stops the comprehensive optimization integration background service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/background_optimization_agent.pid"

# Function to stop the agent
stop_agent() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "🛑 Stopping background optimization agent (PID: $PID)..."
            kill "$PID"
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo "✅ Background optimization agent stopped successfully"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            echo "⚠️  Force killing background optimization agent..."
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            echo "✅ Background optimization agent force stopped"
        else
            echo "Background optimization agent is not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "Background optimization agent is not running"
    fi
}

# Stop the agent
stop_agent