#!/bin/bash

# KingFisher Auto-Monitoring Launcher
# This script ensures the monitoring system is always running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/monitoring.log"
PID_FILE="$SCRIPT_DIR/monitoring.pid"

# Function to start monitoring
start_monitoring() {
    echo "$(date): Starting KingFisher Auto-Monitoring..." >> "$LOG_FILE"
    
    # Kill any conflicting processes first
    echo "$(date): Killing conflicting processes..." >> "$LOG_FILE"
    pkill -f uvicorn 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8100 | xargs kill -9 2>/dev/null || true
    pkill -f "zmart-api" 2>/dev/null || true
    
    # Activate virtual environment
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Set Python path
    export PYTHONPATH="$SCRIPT_DIR/src"
    
    # Start KingFisher server first
    echo "$(date): Starting KingFisher server..." >> "$LOG_FILE"
    cd "$SCRIPT_DIR"
    uvicorn src.main:app --host 127.0.0.1 --port 8100 --reload > kingfisher_server.log 2>&1 &
    KINGFISHER_PID=$!
    echo "$KINGFISHER_PID" > "$SCRIPT_DIR/kingfisher.pid"
    
    # Wait for server to start
    sleep 5
    
    # Check if KingFisher server is running
    if ! curl -s http://localhost:8100/health > /dev/null; then
        echo "$(date): ERROR - KingFisher server failed to start" >> "$LOG_FILE"
        return 1
    fi
    
    echo "$(date): KingFisher server started successfully" >> "$LOG_FILE"
    
    # Start the monitoring script
    python auto_monitor.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    echo "$(date): Monitoring started with PID $(cat $PID_FILE)" >> "$LOG_FILE"
}

# Function to stop monitoring
stop_monitoring() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "$(date): Stopped monitoring (PID: $PID)" >> "$LOG_FILE"
        fi
        rm -f "$PID_FILE"
    fi
    
    # Stop KingFisher server
    if [ -f "$SCRIPT_DIR/kingfisher.pid" ]; then
        KINGFISHER_PID=$(cat "$SCRIPT_DIR/kingfisher.pid")
        if kill -0 "$KINGFISHER_PID" 2>/dev/null; then
            kill "$KINGFISHER_PID"
            echo "$(date): Stopped KingFisher server (PID: $KINGFISHER_PID)" >> "$LOG_FILE"
        fi
        rm -f "$SCRIPT_DIR/kingfisher.pid"
    fi
}

# Function to check if monitoring is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to check if KingFisher server is running
is_kingfisher_running() {
    if [ -f "$SCRIPT_DIR/kingfisher.pid" ]; then
        PID=$(cat "$SCRIPT_DIR/kingfisher.pid")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$SCRIPT_DIR/kingfisher.pid"
        fi
    fi
    return 1
}

# Main logic
case "$1" in
    start)
        if is_running; then
            echo "Monitoring is already running"
        else
            start_monitoring
            if [ $? -eq 0 ]; then
                echo "Monitoring started successfully"
            else
                echo "Failed to start monitoring"
                exit 1
            fi
        fi
        ;;
    stop)
        stop_monitoring
        echo "Monitoring stopped"
        ;;
    restart)
        stop_monitoring
        sleep 2
        start_monitoring
        if [ $? -eq 0 ]; then
            echo "Monitoring restarted successfully"
        else
            echo "Failed to restart monitoring"
            exit 1
        fi
        ;;
    status)
        if is_running; then
            echo "Monitoring is running (PID: $(cat $PID_FILE))"
        else
            echo "Monitoring is not running"
        fi
        
        if is_kingfisher_running; then
            echo "KingFisher server is running (PID: $(cat $SCRIPT_DIR/kingfisher.pid))"
        else
            echo "KingFisher server is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
