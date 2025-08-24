#!/bin/bash

# Enhanced Alerts System - Cron Jobs Setup
# This script sets up automated processing for enhanced alerts

echo "🚀 Setting up Enhanced Alerts Cron Jobs..."
echo "=========================================="

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📍 Project root: $PROJECT_ROOT"
echo "📍 Script directory: $SCRIPT_DIR"

# Create the cron jobs
echo ""
echo "📅 Creating cron jobs for automated processing..."

# 15-minute alerts (every 15 minutes)
(crontab -l 2>/dev/null; echo "*/15 * * * * cd $SCRIPT_DIR && python scripts/run_enhanced_alerts.py --timeframes 15m >> enhanced_alerts_15m.log 2>&1") | crontab -

# 1-hour alerts (every hour)
(crontab -l 2>/dev/null; echo "0 * * * * cd $SCRIPT_DIR && python scripts/run_enhanced_alerts.py --timeframes 1h >> enhanced_alerts_1h.log 2>&1") | crontab -

# 4-hour alerts (every 4 hours)
(crontab -l 2>/dev/null; echo "0 */4 * * * cd $SCRIPT_DIR && python scripts/run_enhanced_alerts.py --timeframes 4h >> enhanced_alerts_4h.log 2>&1") | crontab -

# Daily alerts (at 00:05 UTC)
(crontab -l 2>/dev/null; echo "5 0 * * * cd $SCRIPT_DIR && python scripts/run_enhanced_alerts.py --timeframes 1d >> enhanced_alerts_1d.log 2>&1") | crontab -

# Health check (every 6 hours)
(crontab -l 2>/dev/null; echo "0 */6 * * * cd $SCRIPT_DIR && python scripts/run_enhanced_alerts.py --test >> enhanced_alerts_health.log 2>&1") | crontab -

echo "✅ Cron jobs created successfully!"
echo ""

# Show current cron jobs
echo "📋 Current cron jobs:"
crontab -l | grep enhanced_alerts || echo "No enhanced alerts cron jobs found"

echo ""
echo "📊 Cron Job Schedule:"
echo "   • 15-minute alerts: */15 * * * * (every 15 minutes)"
echo "   • 1-hour alerts: 0 * * * * (every hour)"
echo "   • 4-hour alerts: 0 */4 * * * (every 4 hours)"
echo "   • Daily alerts: 5 0 * * * (daily at 00:05 UTC)"
echo "   • Health check: 0 */6 * * * (every 6 hours)"

echo ""
echo "📁 Log files will be created in:"
echo "   • $SCRIPT_DIR/enhanced_alerts_15m.log"
echo "   • $SCRIPT_DIR/enhanced_alerts_1h.log"
echo "   • $SCRIPT_DIR/enhanced_alerts_4h.log"
echo "   • $SCRIPT_DIR/enhanced_alerts_1d.log"
echo "   • $SCRIPT_DIR/enhanced_alerts_health.log"

echo ""
echo "🔧 Management Commands:"
echo "   • View cron jobs: crontab -l"
echo "   • Edit cron jobs: crontab -e"
echo "   • Remove all cron jobs: crontab -r"
echo "   • Monitor logs: tail -f $SCRIPT_DIR/enhanced_alerts_*.log"

echo ""
echo "🎯 Next Steps:"
echo "   1. Start your Flask server: cd $SCRIPT_DIR && python app.py"
echo "   2. Test the cron jobs manually: python scripts/run_enhanced_alerts.py --test"
echo "   3. Monitor the logs to ensure everything is working"
echo "   4. Access your dashboard at: http://localhost:3400/enhanced-alerts"

echo ""
echo "🎉 Enhanced Alerts Cron Jobs Setup Complete!"
