#!/bin/bash

# Cursor-Claude Context Optimizer Stop Script

echo "🛑 Stopping Cursor-Claude Context Optimizer..."

# Check if PID file exists
if [ -f ".cursor_optimizer.pid" ]; then
    OPTIMIZER_PID=$(cat .cursor_optimizer.pid)
    
    # Check if process is still running
    if ps -p $OPTIMIZER_PID > /dev/null 2>&1; then
        echo "🔄 Stopping optimizer process (PID: $OPTIMIZER_PID)..."
        kill $OPTIMIZER_PID
        
        # Wait for graceful shutdown
        sleep 2
        
        # Check if still running and force kill if necessary
        if ps -p $OPTIMIZER_PID > /dev/null 2>&1; then
            echo "⚠️  Force stopping optimizer..."
            kill -9 $OPTIMIZER_PID
        fi
        
        echo "✅ Context optimizer stopped successfully!"
    else
        echo "ℹ️  Optimizer process was not running"
    fi
    
    # Remove PID file
    rm .cursor_optimizer.pid
else
    echo "ℹ️  No PID file found. Trying to find and stop any running optimizer processes..."
    
    # Find and stop any running optimizer processes
    PIDS=$(pgrep -f "cursor_claude_context_optimizer.py")
    if [ -n "$PIDS" ]; then
        echo "🔄 Found running optimizer processes: $PIDS"
        kill $PIDS
        echo "✅ Context optimizer processes stopped!"
    else
        echo "ℹ️  No running optimizer processes found"
    fi
fi

echo "🎯 Context optimizer shutdown complete!"
