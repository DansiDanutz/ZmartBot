#!/bin/bash

# Life Age Updater Startup Script
# This script starts the life age updater in the background
# Ensures only one instance runs at a time

echo "🚀 Starting Life Age Updater..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if already running
if [ -f "life_age_updater.pid" ]; then
    PID=$(cat life_age_updater.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️ Life Age Updater is already running with PID: $PID"
        echo "🔄 To restart, first run: ./stop_life_age_updater.sh"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file..."
        rm -f life_age_updater.pid
    fi
fi

# Install dependencies if needed
if ! python3 -c "import schedule" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements_life_age.txt
fi

# Create data directory if it doesn't exist
mkdir -p data

# Start the life age updater in the background
echo "⏰ Starting life age updater (will run daily at 1 AM)..."
nohup python3 life_age_updater.py > life_age_updater.out 2>&1 &

# Save the process ID
echo $! > life_age_updater.pid

echo "✅ Life Age Updater started with PID: $(cat life_age_updater.pid)"
echo "📋 Logs will be written to: life_age_updater.log"
echo "🔄 To stop the updater, run: ./stop_life_age_updater.sh"
echo "📊 To check status, run: ps aux | grep life_age_updater"
