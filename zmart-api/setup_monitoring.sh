#!/bin/bash

# Setup System Monitoring (run this to enable automated protection)
echo "🔧 Setting up automated system monitoring..."

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $(pwd) && ./prevent_aggressive_cleanup.sh >> monitoring.log 2>&1") | crontab -

echo "✅ Monitoring enabled - checks every 5 minutes"
echo "📝 Logs will be written to: monitoring.log"
