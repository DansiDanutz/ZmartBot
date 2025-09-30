#!/bin/bash

# KingFisher Auto-Monitoring Stop Script
# This script stops all KingFisher monitoring services

echo "🛑 Stopping KingFisher Auto-Monitoring System..."
echo "=================================================="

# Function to kill processes by name
kill_processes() {
    local name=$1
    echo "🔄 Stopping $name processes..."
    pkill -f "$name" 2>/dev/null || true
    sleep 2
}

# Function to kill processes on port
kill_port() {
    local port=$1
    echo "🔄 Stopping processes on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Stop all Python processes related to KingFisher
echo "🔄 Stopping KingFisher processes..."
pkill -f "uvicorn.*kingfisher" 2>/dev/null || true
pkill -f "auto_monitor.py" 2>/dev/null || true
pkill -f "telegram_monitor.py" 2>/dev/null || true

# Kill processes on port 8100
kill_port 8100

# Stop any remaining Python processes that might be related
echo "🔄 Cleaning up remaining processes..."
pkill -f "src.main:app" 2>/dev/null || true
pkill -f "kingfisher" 2>/dev/null || true

echo ""
echo "✅ KingFisher Auto-Monitoring System Stopped!"
echo "=================================================="
echo "📊 All services have been terminated"
echo "🔄 Port 8100 is now available"
echo ""

# Check if any processes are still running
if lsof -i :8100 >/dev/null 2>&1; then
    echo "⚠️  Warning: Some processes may still be running on port 8100"
    echo "🔄 Force killing remaining processes..."
    lsof -ti:8100 | xargs kill -9 2>/dev/null || true
else
    echo "✅ Port 8100 is now free"
fi

echo ""
echo "🎯 System cleanup complete!" 