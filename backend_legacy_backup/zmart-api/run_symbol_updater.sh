#!/bin/bash

# ZmartBot Symbol Data Updater Script
# Updates all symbols with real-time data from Binance

echo "🚀 Starting ZmartBot Symbol Data Update"
echo "========================================"

# Activate virtual environment
source venv/bin/activate

# Run the updater
python update_all_symbols_realtime.py

echo "✅ Symbol data update completed!"
echo "Check symbol_update.log for details"
