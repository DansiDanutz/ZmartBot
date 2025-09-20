#!/bin/bash

# ZmartBot System Optimization Agent Stop Script
# This script stops the comprehensive optimization integration agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/optimization_agent.pid"

echo "🛑 Stopping ZmartBot System Optimization Agent..."

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found. Agent may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Process $PID is not running. Removing stale PID file..."
    rm -f "$PID_FILE"
    exit 1
fi

echo "🆔 Stopping process $PID..."

# Try graceful shutdown first
kill -TERM $PID

# Wait for graceful shutdown
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ Agent stopped gracefully"
        rm -f "$PID_FILE"
        exit 0
    fi
    echo "⏳ Waiting for graceful shutdown... ($i/10)"
    sleep 1
done

# Force kill if still running
echo "🔨 Force stopping agent..."
kill -KILL $PID

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ Agent force stopped"
    rm -f "$PID_FILE"
else
    echo "❌ Failed to stop agent"
    exit 1
fi
