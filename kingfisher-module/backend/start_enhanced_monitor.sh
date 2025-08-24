#!/bin/bash

echo "============================================================"
echo "🤖 STARTING ENHANCED KINGFISHER MONITOR"
echo "============================================================"
echo ""
echo "Features:"
echo "✅ Precise liquidation clusters (not rounded)"
echo "✅ Automatic timestamp tracking (Last_update field)"
echo "✅ One row per symbol (updates replace old data)"
echo "✅ AI-powered symbol extraction from images"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "../../backend/zmart-api/venv" ]; then
    source ../../backend/zmart-api/venv/bin/activate
fi

# Run the enhanced monitor
python3 enhanced_kingfisher_monitor.py