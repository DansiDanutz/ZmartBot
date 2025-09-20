#!/bin/bash

# ZmartBot Log Rotation Script
# Automatically rotates and compresses log files

cd "$(dirname "$0")"

echo "🔄 ZmartBot Log Rotation Manager"
echo "================================="

# Check if Python script exists
if [ ! -f "log_rotation_manager.py" ]; then
    echo "❌ Error: log_rotation_manager.py not found"
    exit 1
fi

# Show current status
echo "📊 Current log file status:"
python3 log_rotation_manager.py --status

echo ""
echo "🔄 Rotating log files..."
python3 log_rotation_manager.py --rotate

echo ""
echo "📊 Status after rotation:"
python3 log_rotation_manager.py --status

echo ""
echo "📋 Detailed report:"
python3 log_rotation_manager.py --report

echo ""
echo "✅ Log rotation completed!"
