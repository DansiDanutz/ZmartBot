#!/bin/bash

# KingFisher Only Server Startup Script
# This script ensures ONLY KingFisher runs on port 8100

echo "🚀 Starting KingFisher Server Only..."
echo "=================================================="

# Function to kill all conflicting processes
kill_conflicting_processes() {
    echo "🔄 Killing all conflicting processes..."
    
    # Kill all uvicorn processes
    pkill -f uvicorn 2>/dev/null || true
    
    # Kill processes on port 8000 (zmart-api)
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Kill processes on port 8100 (kingfisher)
    lsof -ti:8100 | xargs kill -9 2>/dev/null || true
    
    # Kill any Python processes that might be related
    pkill -f "zmart-api" 2>/dev/null || true
    pkill -f "main:app" 2>/dev/null || true
    
    sleep 3
    echo "✅ All conflicting processes killed"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is still in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Navigate to the correct directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Kill all conflicting processes
kill_conflicting_processes

# Verify ports are free
if ! check_port 8000; then
    echo "❌ Port 8000 still in use after cleanup"
    exit 1
fi

if ! check_port 8100; then
    echo "❌ Port 8100 still in use after cleanup"
    exit 1
fi

# Start KingFisher server ONLY
echo "🖥️  Starting KingFisher server on port 8100..."
echo "📊 This is the ONLY server that should be running"
echo "🚫 No other servers (zmart-api, etc.) will be started"

uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload > kingfisher_server.log 2>&1 &
KINGFISHER_PID=$!

# Wait for server to start
echo "⏳ Waiting for KingFisher server to start..."
sleep 5

# Check if server started successfully
if curl -s http://localhost:8100/health > /dev/null; then
    echo "✅ KingFisher server started successfully on port 8100"
    echo "📊 Health check: $(curl -s http://localhost:8100/health | jq -r '.status')"
    echo "🔗 Server URL: http://localhost:8100"
    echo "📚 API Docs: http://localhost:8100/docs"
else
    echo "❌ Failed to start KingFisher server"
    kill $KINGFISHER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎯 KingFisher Server Running Successfully!"
echo "=================================================="
echo "🖥️  KingFisher Server: http://localhost:8100"
echo "📊 Health: $(curl -s http://localhost:8100/health | jq -r '.status')"
echo "📝 Logs: kingfisher_server.log"
echo ""
echo "🛑 To stop: Ctrl+C or kill $KINGFISHER_PID"
echo "🔄 To restart: ./start_kingfisher_only.sh"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping KingFisher Server..."
    kill $KINGFISHER_PID 2>/dev/null
    echo "✅ KingFisher server stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running and monitor the server
echo "🔄 Monitoring KingFisher server. Press Ctrl+C to stop..."
while true; do
    sleep 10
    
    # Check if KingFisher server is still running
    if ! kill -0 $KINGFISHER_PID 2>/dev/null; then
        echo "❌ KingFisher server stopped unexpectedly"
        break
    fi
    
    # Check if any other servers are trying to start
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "⚠️  Warning: Another server detected on port 8000"
        echo "🔄 Killing conflicting server..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Health check
    if ! curl -s http://localhost:8100/health > /dev/null; then
        echo "❌ KingFisher server health check failed"
        break
    fi
done

cleanup 