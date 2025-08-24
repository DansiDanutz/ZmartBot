#!/bin/bash

echo "============================================================"
echo "🤖 STARTING KINGFISHER AUTO MONITOR"
echo "============================================================"
echo ""
echo "This will monitor your Telegram for KingFisher images"
echo "and automatically update Airtable - NO manual input needed!"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "../../backend/zmart-api/venv" ]; then
    source ../../backend/zmart-api/venv/bin/activate
fi

# Run the auto monitor
python3 auto_kingfisher_monitor.py