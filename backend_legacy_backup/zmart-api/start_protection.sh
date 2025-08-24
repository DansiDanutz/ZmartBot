#!/bin/bash

# My Symbols Database Protection Startup Script
# =============================================

echo "🛡️ Starting My Symbols Database Protection System..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

# Check if the protection script exists
if [ ! -f "protect_database.py" ]; then
    echo "❌ Protection script not found!"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start the protection system
echo "🚀 Launching database protection..."
nohup python3 protect_database.py > logs/protection.log 2>&1 &

# Get the process ID
PROTECTION_PID=$!

# Save the PID to a file for later use
echo $PROTECTION_PID > protection.pid

echo "✅ Database protection started with PID: $PROTECTION_PID"
echo "📝 Logs are being written to: logs/protection.log"
echo "🛡️ Database is now protected from deletion/modification"
echo ""
echo "To check status, run: python3 protect_database.py --check"
echo "To create backup, run: python3 protect_database.py --backup"
echo "To restore from backup, run: python3 protect_database.py --restore"
