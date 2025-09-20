#!/bin/bash

# Background Optimization Agent Startup Script
# Starts the comprehensive optimization integration as a background service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/background_optimization_agent.log"
PID_FILE="$SCRIPT_DIR/background_optimization_agent.pid"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Function to check if the agent is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Background optimization agent is already running (PID: $PID)"
            return 0
        else
            echo "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to start the agent
start_agent() {
    echo "🚀 Starting Background Optimization Agent..."
    
    # Start the comprehensive optimization integration in daemon mode
    nohup python3 "$SCRIPT_DIR/comprehensive_optimization_integration.py" --daemon > "$LOG_FILE" 2>&1 &
    
    # Save the PID
    echo $! > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "✅ Background optimization agent started successfully (PID: $(cat "$PID_FILE"))"
        echo "📋 Log file: $LOG_FILE"
        echo "📋 PID file: $PID_FILE"
        echo ""
        echo "To monitor the agent:"
        echo "  tail -f $LOG_FILE"
        echo ""
        echo "To stop the agent:"
        echo "  ./stop_background_optimization_agent.sh"
    else
        echo "❌ Failed to start background optimization agent"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the agent
stop_agent() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "🛑 Stopping background optimization agent (PID: $PID)..."
            kill "$PID"
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo "✅ Background optimization agent stopped successfully"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            echo "⚠️  Force killing background optimization agent..."
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            echo "✅ Background optimization agent force stopped"
        else
            echo "Background optimization agent is not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "Background optimization agent is not running"
    fi
}

# Function to show status
show_status() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        echo "📊 Background Optimization Agent Status:"
        echo "  Status: RUNNING"
        echo "  PID: $PID"
        echo "  Log file: $LOG_FILE"
        echo "  PID file: $PID_FILE"
        echo ""
        echo "Recent log entries:"
        tail -5 "$LOG_FILE" 2>/dev/null || echo "  No log entries yet"
    else
        echo "📊 Background Optimization Agent Status:"
        echo "  Status: STOPPED"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        if check_running; then
            exit 0
        fi
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    restart)
        stop_agent
        sleep 2
        start_agent
        ;;
    status)
        show_status
        ;;
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "Log file not found: $LOG_FILE"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the background optimization agent (default)"
        echo "  stop    - Stop the background optimization agent"
        echo "  restart - Restart the background optimization agent"
        echo "  status  - Show the current status"
        echo "  logs    - Follow the log file in real-time"
        exit 1
        ;;
esac