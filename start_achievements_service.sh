#!/bin/bash
# ZmartBot Achievements Service Startup Script
set -euo pipefail

echo "🏆 Starting ZmartBot Achievements Service"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📂 Project Root: $PROJECT_ROOT"
echo "🕐 Current Time: $(date)"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
ACHIEVEMENTS_SERVICE="$PROJECT_ROOT/zmart-api/achievements_service.py"
ACHIEVEMENTS_SCHEDULER="$PROJECT_ROOT/zmart-api/achievements_scheduler.py"

if [[ ! -f "$ACHIEVEMENTS_SERVICE" ]]; then
    echo "❌ Error: achievements_service.py not found at $ACHIEVEMENTS_SERVICE"
    exit 1
fi

if [[ ! -f "$ACHIEVEMENTS_SCHEDULER" ]]; then
    echo "❌ Error: achievements_scheduler.py not found at $ACHIEVEMENTS_SCHEDULER"
    exit 1
fi

echo "✅ All required files found"
echo ""

# Install required Python packages
echo "📦 Checking required packages..."
python3 -m pip install --user schedule sqlite3 2>/dev/null || true
echo "✅ Packages verified"
echo ""

# Run initial scan
echo "🔍 Running initial achievements scan..."
python3 "$ACHIEVEMENTS_SERVICE" --project-root "$PROJECT_ROOT" --summary
echo ""

# Option selection
echo "🎯 Choose startup option:"
echo "1) Run immediate scan only"
echo "2) Start scheduler daemon (runs in background)"
echo "3) Run immediate scan + start daemon"
echo "4) Show service status"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Running immediate achievements scan..."
        python3 "$ACHIEVEMENTS_SERVICE" --project-root "$PROJECT_ROOT" --scan
        echo "✅ Scan completed"
        ;;
    2)
        echo "🚀 Starting achievements scheduler daemon..."
        python3 "$ACHIEVEMENTS_SCHEDULER" --project-root "$PROJECT_ROOT" --daemon &
        DAEMON_PID=$!
        echo "✅ Scheduler daemon started (PID: $DAEMON_PID)"
        echo "📝 Logs available at: $PROJECT_ROOT/zmart-api/logs/achievements_scheduler.log"
        echo ""
        echo "To stop the daemon, run: kill $DAEMON_PID"
        ;;
    3)
        echo "🚀 Running immediate scan and starting daemon..."
        python3 "$ACHIEVEMENTS_SERVICE" --project-root "$PROJECT_ROOT" --scan
        echo "🚀 Starting scheduler daemon..."
        python3 "$ACHIEVEMENTS_SCHEDULER" --project-root "$PROJECT_ROOT" --daemon &
        DAEMON_PID=$!
        echo "✅ Scan completed and daemon started (PID: $DAEMON_PID)"
        echo "📝 Logs available at: $PROJECT_ROOT/zmart-api/logs/achievements_scheduler.log"
        echo ""
        echo "To stop the daemon, run: kill $DAEMON_PID"
        ;;
    4)
        echo "📊 Service Status:"
        python3 "$ACHIEVEMENTS_SCHEDULER" --project-root "$PROJECT_ROOT" --status
        echo ""
        echo "📊 Achievement Summary:"
        python3 "$ACHIEVEMENTS_SERVICE" --project-root "$PROJECT_ROOT" --summary
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🏆 ZmartBot Achievements Service operations completed"
echo "📅 Next scheduled scan: Daily at 00:00 UTC"
echo "🔧 Manual commands:"
echo "   Scan: python3 zmart-api/achievements_service.py --scan"
echo "   Status: python3 zmart-api/achievements_scheduler.py --status"
echo "   Recent: python3 zmart-api/achievements_service.py --recent 7"