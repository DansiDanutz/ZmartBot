#!/bin/bash

# My Symbols Database Protection Stop Script
# ==========================================

echo "🛑 Stopping My Symbols Database Protection System..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if PID file exists
if [ ! -f "protection.pid" ]; then
    echo "❌ Protection PID file not found. Protection may not be running."
    exit 1
fi

# Read the PID
PROTECTION_PID=$(cat protection.pid)

# Check if process is running
if ! ps -p $PROTECTION_PID > /dev/null; then
    echo "❌ Protection process (PID: $PROTECTION_PID) is not running."
    rm -f protection.pid
    exit 1
fi

# Stop the protection process
echo "🔄 Stopping protection process (PID: $PROTECTION_PID)..."
kill $PROTECTION_PID

# Wait for process to stop
sleep 2

# Check if process stopped
if ps -p $PROTECTION_PID > /dev/null; then
    echo "⚠️ Process still running, forcing termination..."
    kill -9 $PROTECTION_PID
    sleep 1
fi

# Remove PID file
rm -f protection.pid

echo "✅ Database protection stopped successfully"
echo "⚠️ Database is no longer protected from deletion/modification"
