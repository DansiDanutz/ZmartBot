#!/bin/bash

# ZmartBot System Optimization Agent Status Script
# This script provides comprehensive status information about the optimization agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/optimization_agent.pid"
LOG_FILE="$SCRIPT_DIR/optimization_agent.log"

echo "🔍 ZmartBot System Optimization Agent Status"
echo "=============================================="
echo "📁 Directory: $SCRIPT_DIR"
echo "📝 Log File: $LOG_FILE"
echo "🆔 PID File: $PID_FILE"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Status: NOT RUNNING (No PID file found)"
    echo ""
    echo "💡 To start the agent:"
    echo "   ./start_optimization_agent.sh"
    exit 1
fi

PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Status: NOT RUNNING (Stale PID file - process $PID not found)"
    echo "🧹 Cleaning up stale PID file..."
    rm -f "$PID_FILE"
    echo ""
    echo "💡 To start the agent:"
    echo "   ./start_optimization_agent.sh"
    exit 1
fi

echo "✅ Status: RUNNING"
echo "🆔 Process ID: $PID"

# Get process information
echo ""
echo "📊 Process Information:"
ps -p $PID -o pid,ppid,user,start,time,command

# Check memory and CPU usage
echo ""
echo "💾 Resource Usage:"
ps -p $PID -o pid,pcpu,pmem,rss,vsz

# Check log file
if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "📝 Recent Log Entries (last 10 lines):"
    echo "----------------------------------------"
    tail -10 "$LOG_FILE"
    
    echo ""
    echo "📈 Log File Statistics:"
    echo "   Size: $(du -h "$LOG_FILE" | cut -f1)"
    echo "   Lines: $(wc -l < "$LOG_FILE")"
    echo "   Last Modified: $(stat -f "%Sm" "$LOG_FILE")"
else
    echo ""
    echo "⚠️  No log file found at: $LOG_FILE"
fi

# Check system optimization components
echo ""
echo "🔧 System Optimization Components Status:"
echo "------------------------------------------"

# Check if Python can import the optimization manager
python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
try:
    from system_optimization_manager import SystemOptimizationManager
    manager = SystemOptimizationManager()
    status = manager.get_status()
    print('✅ SystemOptimizationManager: Initialized')
    print(f'   Components: {len(status.get(\"initialized_components\", []))}')
    print(f'   Running Threads: {sum(1 for v in status.get(\"running_threads\", {}).values() if v)}')
    for comp in status.get('initialized_components', []):
        print(f'   - {comp}')
except Exception as e:
    print(f'❌ SystemOptimizationManager: Error - {e}')
" 2>/dev/null

echo ""
echo "🛠️  Management Commands:"
echo "   Start:   ./start_optimization_agent.sh"
echo "   Stop:    ./stop_optimization_agent.sh"
echo "   Status:  ./optimization_agent_status.sh"
echo "   Logs:    tail -f $LOG_FILE"
echo "   Kill:    kill $PID"
