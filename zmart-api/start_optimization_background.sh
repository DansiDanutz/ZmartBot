#!/bin/bash

# ZmartBot Optimization Background Service
# ======================================
# This script starts the comprehensive optimization system as a background service

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$PROJECT_ROOT/optimization_background.pid"
LOG_FILE="$LOG_DIR/optimization_background.log"
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

# Function to check if service is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead, clean it up
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the optimization service
start_service() {
    print_status "Starting ZmartBot Optimization Background Service..."
    
    if is_running; then
        print_warning "Optimization service is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ -d "$PROJECT_ROOT/venv" ]; then
        print_status "Activating virtual environment..."
        source "$PROJECT_ROOT/venv/bin/activate"
    fi
    
    # Start the service in background
    print_status "Starting optimization service in background mode..."
    nohup python3 "$PYTHON_SCRIPT" --background > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "Optimization service started successfully (PID: $pid)"
        print_status "Log file: $LOG_FILE"
        print_status "PID file: $PID_FILE"
        return 0
    else
        print_error "Failed to start optimization service"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the optimization service
stop_service() {
    print_status "Stopping ZmartBot Optimization Background Service..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "PID file not found. Service may not be running."
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Process with PID $pid is not running"
        rm -f "$PID_FILE"
        return 1
    fi
    
    # Try graceful shutdown first
    print_status "Sending SIGTERM to process $pid..."
    kill -TERM "$pid"
    
    # Wait for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Process did not stop gracefully, forcing shutdown..."
        kill -KILL "$pid"
        sleep 1
    fi
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        print_success "Optimization service stopped successfully"
        rm -f "$PID_FILE"
        return 0
    else
        print_error "Failed to stop optimization service"
        return 1
    fi
}

# Function to restart the optimization service
restart_service() {
    print_status "Restarting ZmartBot Optimization Background Service..."
    stop_service
    sleep 2
    start_service
}

# Function to show service status
show_status() {
    print_status "ZmartBot Optimization Background Service Status:"
    echo
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Service is RUNNING (PID: $pid)"
        
        # Show process info
        echo "Process Information:"
        ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem
        
        echo
        echo "Recent log entries (last 10 lines):"
        if [ -f "$LOG_FILE" ]; then
            tail -n 10 "$LOG_FILE"
        else
            echo "No log file found"
        fi
    else
        print_warning "Service is NOT RUNNING"
        
        if [ -f "$LOG_FILE" ]; then
            echo
            echo "Last log entries:"
            tail -n 20 "$LOG_FILE"
        fi
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing optimization service logs:"
        echo "=========================================="
        tail -f "$LOG_FILE"
    else
        print_error "Log file not found: $LOG_FILE"
    fi
}

# Function to show help
show_help() {
    echo "ZmartBot Optimization Background Service Manager"
    echo "================================================"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo
    echo "Commands:"
    echo "  start   - Start the optimization service in background"
    echo "  stop    - Stop the optimization service"
    echo "  restart - Restart the optimization service"
    echo "  status  - Show service status and recent logs"
    echo "  logs    - Show live log output"
    echo "  help    - Show this help message"
    echo
    echo "Files:"
    echo "  PID File: $PID_FILE"
    echo "  Log File: $LOG_FILE"
    echo "  Script:   $PYTHON_SCRIPT"
}

# Main script logic
case "${1:-}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
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
        echo
        show_help
        exit 1
        ;;
esac
