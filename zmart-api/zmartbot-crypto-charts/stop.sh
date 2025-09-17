#!/bin/bash

echo "🛑 Stopping ZmartBot Crypto Charts Service..."

# Find and kill the Node.js process
PID=$(pgrep -f "node.*server.js")

if [ -n "$PID" ]; then
    echo "📋 Found process with PID: $PID"
    kill -TERM $PID
    
    # Wait for graceful shutdown
    sleep 5
    
    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️  Force killing process..."
        kill -KILL $PID
    fi
    
    echo "✅ Service stopped successfully"
else
    echo "ℹ️  No running service found"
fi
