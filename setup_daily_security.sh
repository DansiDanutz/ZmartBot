#!/bin/bash

# Setup Daily Security Check for ZmartBot
# This script adds a daily security check to crontab

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
SECURITY_SCRIPT="$PROJECT_ROOT/simple_security_check.sh"
LOG_FILE="$PROJECT_ROOT/logs/daily_security_check.log"

echo "🔒 Setting up daily security check for ZmartBot..."

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Create the daily security check script
cat > "$PROJECT_ROOT/daily_security_check.sh" << 'EOF'
#!/bin/bash
#
# Daily Security Check for ZmartBot
# Runs comprehensive security scan and logs results
#

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
LOG_FILE="$PROJECT_ROOT/logs/daily_security_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== ZmartBot Daily Security Check - $DATE ===" >> "$LOG_FILE"

cd "$PROJECT_ROOT"

# Run comprehensive security scan
if [ -x "./security_scan.sh" ]; then
    echo "Running comprehensive security scan..." >> "$LOG_FILE"
    if ./security_scan.sh --gitleaks-only >> "$LOG_FILE" 2>&1; then
        echo "✅ Comprehensive security scan passed" >> "$LOG_FILE"
        
        # Send notification (optional)
        # osascript -e 'display notification "Daily security scan passed" with title "ZmartBot Security"'
    else
        echo "❌ Comprehensive security scan found issues!" >> "$LOG_FILE"
        
        # Send alert notification
        osascript -e 'display notification "Daily security scan found issues! Check logs." with title "ZmartBot Security Alert"' 2>/dev/null || true
    fi
else
    echo "⚠️ Comprehensive security script not found" >> "$LOG_FILE"
fi

echo "=== End Daily Security Check ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
EOF

chmod +x "$PROJECT_ROOT/daily_security_check.sh"

# Add to crontab (runs daily at 9 AM)
CRON_JOB="0 9 * * * $PROJECT_ROOT/daily_security_check.sh"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "daily_security_check.sh"; then
    # Add to existing crontab or create new one
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Daily security check added to crontab (runs at 9 AM daily)"
    echo "📋 Log file: $LOG_FILE"
else
    echo "✅ Daily security check already exists in crontab"
fi

echo ""
echo "🎯 Daily Security Check Setup Complete!"
echo "📅 Will run daily at 9:00 AM"
echo "📁 Logs saved to: $LOG_FILE"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove daily check: crontab -e (then delete the line)"