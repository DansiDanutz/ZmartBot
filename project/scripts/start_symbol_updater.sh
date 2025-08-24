#!/bin/bash

# ZmartBot Symbol Data Updater - Continuous Mode with Caching
# Updates all symbols with real-time data every hour (with caching)

echo "🚀 Starting ZmartBot Symbol Data Updater (Continuous Mode)"
echo "=========================================================="
echo "📊 Updates all 10 symbols with real-time Binance data"
echo "💾 Uses caching to reduce API calls"
echo "⏰ Runs every hour (fresh data when cache expires)"
echo "🔄 Press Ctrl+C to stop"
echo ""

# Activate virtual environment
source venv/bin/activate

# Function to run update
run_update() {
    echo ""
    echo "🔄 Running symbol data update at $(date)"
    echo "=========================================="
    python update_all_symbols_realtime.py
    echo "✅ Update completed at $(date)"
    echo ""
}

# Run initial update
run_update

# Run updates every hour
while true; do
    echo "⏰ Next update in 1 hour..."
    sleep 3600  # 1 hour = 3600 seconds
    run_update
done
