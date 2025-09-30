#!/bin/bash

# KingFisher Auto-Monitoring Startup Script
# This script starts the KingFisher server and monitoring scripts

echo "🚀 Starting KingFisher Auto-Monitoring System..."
echo "=================================================="

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to kill processes on port
kill_port() {
    local port=$1
    echo "🔄 Killing processes on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check and kill processes on port 8100
if ! check_port 8100; then
    kill_port 8100
fi

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

# Start KingFisher server in background
echo "🖥️  Starting KingFisher server on port 8100..."
uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server started successfully
if curl -s http://localhost:8100/health > /dev/null; then
    echo "✅ KingFisher server started successfully"
else
    echo "❌ Failed to start KingFisher server"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Start auto-monitor in background
echo "📊 Starting auto-monitor..."
python auto_monitor.py > auto_monitor.log 2>&1 &
MONITOR_PID=$!

# Start Telegram monitor in background
echo "📱 Starting Telegram monitor..."
python telegram_monitor.py > telegram_monitor.log 2>&1 &
TELEGRAM_PID=$!

echo ""
echo "🎯 KingFisher Auto-Monitoring System Started!"
echo "=================================================="
echo "🖥️  KingFisher Server: http://localhost:8100"
echo "📊 Auto-Monitor: Running (PID: $MONITOR_PID)"
echo "📱 Telegram Monitor: Running (PID: $TELEGRAM_PID)"
echo "📝 Logs:"
echo "   - Server: server.log"
echo "   - Auto-Monitor: auto_monitor.log"
echo "   - Telegram Monitor: telegram_monitor.log"
echo ""
echo "🛑 To stop all services, run: ./stop_monitoring.sh"
echo "📊 To view logs: tail -f *.log"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping KingFisher Auto-Monitoring System..."
    kill $SERVER_PID $MONITOR_PID $TELEGRAM_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
echo "🔄 Monitoring active. Press Ctrl+C to stop all services..."
while true; do
    sleep 10
    
    # Check if processes are still running
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "❌ KingFisher server stopped unexpectedly"
        break
    fi
    
    if ! kill -0 $MONITOR_PID 2>/dev/null; then
        echo "❌ Auto-monitor stopped unexpectedly"
        break
    fi
    
    if ! kill -0 $TELEGRAM_PID 2>/dev/null; then
        echo "❌ Telegram monitor stopped unexpectedly"
        break
    fi
done

cleanup 