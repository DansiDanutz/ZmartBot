#!/bin/bash

# ZmartBot Comprehensive Symbol Data Updater - Continuous Mode
# Updates all symbols with real-time data every hour (with caching and historical storage)
# Stores historical snapshots for pattern analysis

echo "🚀 Starting ZmartBot Comprehensive Symbol Data Updater (Continuous Mode)"
echo "=========================================================="
echo "📊 Updates all 10 symbols with real-time Binance data"
echo "💾 Uses caching to reduce API calls"
echo "📈 Stores historical snapshots for pattern analysis"
echo "⏰ Runs every hour (fresh data when cache expires)"
echo "🔄 Press Ctrl+C to stop"
echo ""

# Function to run the comprehensive update
run_comprehensive_update() {
    echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') - Starting comprehensive update..."
    
    # Activate virtual environment and run update
    source venv/bin/activate
    python update_with_history.py
    
    if [ $? -eq 0 ]; then
        echo "✅ $(date '+%Y-%m-%d %H:%M:%S') - Comprehensive update completed successfully"
    else
        echo "❌ $(date '+%Y-%m-%d %H:%M:%S') - Comprehensive update failed"
    fi
    
    echo ""
}

# Run initial update
run_comprehensive_update

# Run updates every hour
while true; do
    echo "⏰ Next comprehensive update in 1 hour..."
    sleep 3600  # 1 hour = 3600 seconds
    run_comprehensive_update
done
