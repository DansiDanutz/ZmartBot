#!/bin/bash
# Setup bi-daily cron jobs for ZmartBot Trigger Manager
# Runs at 6:00 AM and 6:00 PM daily

SCRIPT_DIR="/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
PYTHON_PATH="/usr/bin/python3"
LOG_FILE="$SCRIPT_DIR/trigger_cron.log"

echo "🚀 Setting up ZmartBot Trigger Manager cron jobs..."

# Create cron job entries
CRON_ENTRY_MORNING="0 6 * * * cd $SCRIPT_DIR && $PYTHON_PATH trigger_manager.py --sync --type=morning >> $LOG_FILE 2>&1"
CRON_ENTRY_EVENING="0 18 * * * cd $SCRIPT_DIR && $PYTHON_PATH trigger_manager.py --sync --type=evening >> $LOG_FILE 2>&1"

# Check if cron jobs already exist
if crontab -l 2>/dev/null | grep -q "trigger_manager.py"; then
    echo "⚠️ Trigger Manager cron jobs already exist. Updating..."
    # Remove existing trigger manager cron jobs
    crontab -l 2>/dev/null | grep -v "trigger_manager.py" | crontab -
fi

# Add new cron jobs
(crontab -l 2>/dev/null; echo "$CRON_ENTRY_MORNING"; echo "$CRON_ENTRY_EVENING") | crontab -

echo "✅ Cron jobs installed successfully:"
echo "   - Morning sync: 6:00 AM daily"
echo "   - Evening sync: 6:00 PM daily"
echo "   - Logs: $LOG_FILE"

# Verify cron installation
echo ""
echo "📋 Current cron jobs:"
crontab -l | grep "trigger_manager.py"

# Create log file if it doesn't exist
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

echo ""
echo "🎯 ZmartBot Trigger Manager is configured for bi-daily updates!"
echo "   Focus: LEVEL 2 (ACTIVE) and LEVEL 3 (REGISTERED) services only"
echo "   Excluded: Discovery services without ports"