#!/bin/bash

# Start MDC Dashboard Server
# Runs on localhost:3400/MDC-dashboard

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DASHBOARD_DIR="$PROJECT_ROOT/zmart-api/Dashboard/MDC-Dashboard"
SERVER_SCRIPT="$DASHBOARD_DIR/server.py"
LOG_FILE="$DASHBOARD_DIR/dashboard.log"
PID_FILE="$DASHBOARD_DIR/dashboard.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[MDC-DASHBOARD]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if dashboard is running
is_dashboard_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the dashboard
start_dashboard() {
    print_status "Starting MDC Dashboard Server..."
    
    # Check if already running
    if is_dashboard_running; then
        print_warning "MDC Dashboard is already running (PID: $(cat $PID_FILE))"
        local port="${MDC_DASHBOARD_PORT:-3400}"
        print_status "Dashboard URL: http://localhost:$port/MDC-dashboard"
        return 0
    fi
    
    # Validate environment
    if [ ! -f "$SERVER_SCRIPT" ]; then
        print_error "Dashboard server script not found: $SERVER_SCRIPT"
        exit 1
    fi
    
    # Check Python requirements
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check required Python packages
    print_status "Checking Python dependencies..."
    if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
        print_warning "Installing required Python packages..."
        pip3 install flask flask-cors requests || {
            print_error "Failed to install Python dependencies"
            exit 1
        }
    fi
    
    # Set environment variables
    export PROJECT_ROOT="$PROJECT_ROOT"
    export MDC_DASHBOARD_PORT="${MDC_DASHBOARD_PORT:-3400}"
    export PYTHONPATH="$DASHBOARD_DIR:$PROJECT_ROOT/zmart-api:$PYTHONPATH"
    
    # Start the dashboard in background
    cd "$DASHBOARD_DIR"
    nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
    local dashboard_pid=$!
    
    # Save PID
    echo "$dashboard_pid" > "$PID_FILE"
    
    # Wait a moment and check if it's running
    sleep 3
    if is_dashboard_running; then
        local port="${MDC_DASHBOARD_PORT:-3400}"
        print_success "MDC Dashboard Server started successfully"
        print_status "PID: $dashboard_pid"
        print_status "Port: $port"
        print_status "Log: $LOG_FILE"
        print_status "Dashboard URL: http://localhost:$port/MDC-dashboard"
        
        # Test the health endpoint
        sleep 2
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "Health check passed - Dashboard is responding"
            print_status "🎉 Ready to manage your MDC files!"
            print_status ""
            print_status "Open your browser and navigate to:"
            print_status "  http://localhost:$port/MDC-dashboard"
        else
            print_warning "Health check failed - Dashboard may still be starting up"
            print_status "Check the logs: tail -f $LOG_FILE"
        fi
        
        return 0
    else
        print_error "Failed to start MDC Dashboard Server"
        if [ -f "$LOG_FILE" ]; then
            print_error "Last few lines of log:"
            tail -10 "$LOG_FILE"
        fi
        return 1
    fi
}

# Function to stop the dashboard
stop_dashboard() {
    print_status "Stopping MDC Dashboard Server..."
    
    if is_dashboard_running; then
        local pid=$(cat "$PID_FILE")
        kill "$pid"
        
        # Wait for graceful shutdown
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            ((count++))
        done
        
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            print_warning "Forcing kill of dashboard process"
            kill -9 "$pid"
        fi
        
        rm -f "$PID_FILE"
        print_success "MDC Dashboard Server stopped"
    else
        print_warning "MDC Dashboard Server is not running"
    fi
}

# Function to restart the dashboard
restart_dashboard() {
    stop_dashboard
    sleep 2
    start_dashboard
}

# Function to show dashboard status
status_dashboard() {
    print_status "Checking MDC Dashboard status..."
    
    if is_dashboard_running; then
        local pid=$(cat "$PID_FILE")
        local port="${MDC_DASHBOARD_PORT:-3400}"
        print_success "MDC Dashboard is running (PID: $pid)"
        
        # Show connection info
        print_status "Port: $port"
        print_status "Dashboard URL: http://localhost:$port/MDC-dashboard"
        print_status "API Base URL: http://localhost:$port/api"
        
        # Test health endpoint
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "Health check: PASSED"
            
            # Get system stats
            local stats=$(curl -s "http://localhost:$port/api/mdc/files" 2>/dev/null || echo "{}")
            if [ "$stats" != "{}" ]; then
                print_status "System Stats:"
                echo "$stats" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'data' in data:
        files = data['data'].get('files', [])
        print(f'  - MDC Files: {len(files)}')
        print(f'  - Last Scan: {data[\"data\"].get(\"last_scan\", \"Unknown\")}')
except:
    pass
" 2>/dev/null || echo "  - Unable to fetch stats"
            fi
        else
            print_warning "Health check: FAILED"
        fi
    else
        print_warning "MDC Dashboard is not running"
        print_status ""
        print_status "To start the dashboard, run:"
        print_status "  $0 start"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "MDC Dashboard logs (last 50 lines):"
        tail -n 50 "$LOG_FILE"
    else
        print_warning "No log file found: $LOG_FILE"
    fi
}

# Function to follow logs
follow_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Following MDC Dashboard logs (Ctrl+C to stop):"
        tail -f "$LOG_FILE"
    else
        print_warning "No log file found: $LOG_FILE"
    fi
}

# Function to open dashboard in browser
open_dashboard() {
    local port="${MDC_DASHBOARD_PORT:-3400}"
    local url="http://localhost:$port/MDC-dashboard"
    
    print_status "Opening dashboard in browser..."
    
    if is_dashboard_running; then
        # Try to open browser on different platforms
        if command -v open &> /dev/null; then
            # macOS
            open "$url"
        elif command -v xdg-open &> /dev/null; then
            # Linux
            xdg-open "$url"
        elif command -v start &> /dev/null; then
            # Windows
            start "$url"
        else
            print_warning "Cannot automatically open browser"
            print_status "Please open this URL manually:"
            print_status "  $url"
        fi
    else
        print_error "Dashboard is not running. Start it first with: $0 start"
    fi
}

# Function to install dependencies
install_deps() {
    print_status "Installing MDC Dashboard dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Install Python packages
    print_status "Installing Python packages..."
    pip3 install flask flask-cors requests || {
        print_error "Failed to install Python dependencies"
        exit 1
    }
    
    print_success "Dependencies installed successfully"
}

# Main script logic
case "${1:-start}" in
    start)
        start_dashboard
        ;;
    stop)
        stop_dashboard
        ;;
    restart)
        restart_dashboard
        ;;
    status)
        status_dashboard
        ;;
    logs)
        show_logs
        ;;
    follow-logs)
        follow_logs
        ;;
    open)
        open_dashboard
        ;;
    install-deps)
        install_deps
        ;;
    *)
        echo "MDC Dashboard Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|follow-logs|open|install-deps}"
        echo ""
        echo "Commands:"
        echo "  start        - Start the MDC Dashboard Server"
        echo "  stop         - Stop the MDC Dashboard Server"
        echo "  restart      - Restart the MDC Dashboard Server"
        echo "  status       - Show dashboard status and health"
        echo "  logs         - Show recent logs"
        echo "  follow-logs  - Follow logs in real-time"
        echo "  open         - Open dashboard in browser"
        echo "  install-deps - Install required dependencies"
        echo ""
        echo "Environment Variables:"
        echo "  MDC_DASHBOARD_PORT - Port for the dashboard (default: 3400)"
        echo "  PROJECT_ROOT       - ZmartBot project root path"
        echo ""
        echo "Dashboard URL: http://localhost:3400/MDC-dashboard"
        exit 1
        ;;
esac