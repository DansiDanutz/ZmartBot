#!/bin/bash

# Life Age Updater Stop Script
# This script stops the life age updater process

echo "🛑 Stopping Life Age Updater..."

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if PID file exists
if [ -f "life_age_updater.pid" ]; then
    PID=$(cat life_age_updater.pid)
    
    # Check if process is still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔄 Stopping process with PID: $PID"
        kill $PID
        
        # Wait a moment and check if it stopped
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️ Process still running, force killing..."
            kill -9 $PID
        fi
        
        echo "✅ Life Age Updater stopped"
    else
        echo "⚠️ Process with PID $PID is not running"
    fi
    
    # Remove PID file
    rm -f life_age_updater.pid
else
    echo "⚠️ No PID file found. Life Age Updater may not be running."
fi

echo "📋 Check life_age_updater.log for any errors"
