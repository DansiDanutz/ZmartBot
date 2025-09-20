#!/bin/bash

# ZmartBot Optimization Background Agent Startup Script
# ====================================================
# This script starts the comprehensive optimization system as a background service

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$PROJECT_ROOT/optimization_agent.pid"
LOG_FILE="$LOG_DIR/optimization_agent.log"
PYTHON_SCRIPT="$SCRIPT_DIR/comprehensive_optimization_integration.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to check if the optimization agent is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running, clean up
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the optimization agent
start_agent() {
    print_status "Starting ZmartBot Optimization Background Agent..."
    
    # Check if already running
    if is_running; then
        print_warning "Optimization agent is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        return 1
    fi
    
    # Change to the script directory
    cd "$SCRIPT_DIR"
    
    # Start the optimization agent in background
    print_status "Starting optimization agent in background mode..."
    nohup python3 "$PYTHON_SCRIPT" --background > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID to file
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if process is still running
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "Optimization agent started successfully (PID: $pid)"
        print_status "Log file: $LOG_FILE"
        print_status "PID file: $PID_FILE"
        return 0
    else
        print_error "Failed to start optimization agent"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the optimization agent
stop_agent() {
    print_status "Stopping ZmartBot Optimization Background Agent..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_status "Sending SIGTERM to process $pid..."
            kill "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Process did not stop gracefully, sending SIGKILL..."
                kill -9 "$pid"
            fi
            
            print_success "Optimization agent stopped"
        else
            print_warning "Process $pid is not running"
        fi
        rm -f "$PID_FILE"
    else
        print_warning "PID file not found, agent may not be running"
    fi
}

# Function to restart the optimization agent
restart_agent() {
    print_status "Restarting ZmartBot Optimization Background Agent..."
    stop_agent
    sleep 2
    start_agent
}

# Function to show status
show_status() {
    print_status "ZmartBot Optimization Background Agent Status:"
    echo "=========================================="
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Status: RUNNING (PID: $pid)"
        echo "Log file: $LOG_FILE"
        echo "PID file: $PID_FILE"
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "Recent log entries:"
            echo "------------------"
            tail -n 10 "$LOG_FILE"
        fi
    else
        print_warning "Status: NOT RUNNING"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing optimization agent logs:"
        echo "====================================="
        tail -f "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
}

# Function to show help
show_help() {
    echo "ZmartBot Optimization Background Agent Management Script"
    echo "======================================================="
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the optimization agent in background"
    echo "  stop    - Stop the optimization agent"
    echo "  restart - Restart the optimization agent"
    echo "  status  - Show current status and recent logs"
    echo "  logs    - Show live log output"
    echo "  help    - Show this help message"
    echo ""
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
    echo "  Script:  $PYTHON_SCRIPT"
}

# Main script logic
case "${1:-}" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    restart)
        restart_agent
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac