#!/bin/bash

# Cursor-Claude Context Optimizer Startup Script
# Integrates with existing ZmartBot system

echo "🚀 Starting Cursor-Claude Context Optimizer..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "cursor_claude_context_optimizer.py" ]; then
    echo "❌ cursor_claude_context_optimizer.py not found in current directory"
    echo "Please run this script from the ZmartBot project root"
    exit 1
fi

# Install required dependencies if not present
echo "📦 Checking dependencies..."
python3 -c "import sqlite3, yaml, psutil" 2>/dev/null || {
    echo "📦 Installing required dependencies..."
    pip3 install pyyaml psutil watchdog aiofiles aiohttp
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the context optimizer in background
echo "🔧 Starting context optimizer..."
python3 cursor_claude_context_optimizer.py --start &
OPTIMIZER_PID=$!

# Save PID for later cleanup
echo $OPTIMIZER_PID > .cursor_optimizer.pid

echo "✅ Cursor-Claude Context Optimizer started successfully!"
echo "📊 PID: $OPTIMIZER_PID"
echo "📝 Logs: cursor_claude_optimizer.log"
echo "⚙️  Config: .cursor_claude_optimizer.yaml"
echo ""
echo "🔍 To check status: python3 cursor_claude_context_optimizer.py --status"
echo "📋 To get context: python3 cursor_claude_context_optimizer.py --context"
echo "🛑 To stop: kill $OPTIMIZER_PID or run stop_cursor_optimizer.sh"
echo ""
echo "🎯 The optimizer is now monitoring your project and optimizing context for Claude in Cursor!"
