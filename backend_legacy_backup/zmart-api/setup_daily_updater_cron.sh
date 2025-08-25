#!/bin/bash

# Daily Price Updater Cron Setup Script
# Sets up a cron job to run daily price updates at 00:05 every day

echo "🔧 Setting up Daily Price Updater Cron Job..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/run_daily_updater.py"

# Make the Python script executable
chmod +x "$PYTHON_SCRIPT"

# Create the cron job entry (runs at 00:05 every day)
CRON_JOB="5 0 * * * cd $SCRIPT_DIR && python3 $PYTHON_SCRIPT >> /Users/dansidanutz/Desktop/ZmartBot/Symbol_Price_history_data/logs/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_daily_updater.py"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "run_daily_updater.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Daily Price Updater cron job set up successfully!"
echo "📅 Cron job will run at 00:05 every day"
echo "📝 Logs will be saved to: /Users/dansidanutz/Desktop/ZmartBot/Symbol_Price_history_data/logs/"
echo ""
echo "🔍 To check cron jobs: crontab -l"
echo "🔍 To remove cron job: crontab -r"
echo "🔍 To edit cron jobs: crontab -e"
echo ""
echo "🧪 To test the updater manually:"
echo "   cd $SCRIPT_DIR && python3 $PYTHON_SCRIPT"
