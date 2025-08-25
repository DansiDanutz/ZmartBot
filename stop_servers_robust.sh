#!/bin/bash

# ZmartBot Robust Server Stop Script
# Enhanced version with proper cleanup and monitoring shutdown

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DASHBOARD_PORT=3400
PID_DIR="server_pids"
LOG_FILE="server_shutdown.log"

echo -e "${BLUE}🛑 ZmartBot Robust Server Stop Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Function to log messages with timestamp
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    case $level in
        "INFO") color=$GREEN ;;
        "WARN") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        "DEBUG") color=$CYAN ;;
        *) color=$NC ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to get process info on a port
get_port_process_info() {
    local port=$1
    if check_port $port; then
        lsof -i :$port | grep LISTEN | awk '{print $2, $1, $9}' | head -1
    else
        echo "FREE"
    fi
}

# Function to stop process by PID file
stop_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_message "INFO" "🛑 Stopping $service_name (PID: $pid)"
            kill -TERM $pid 2>/dev/null || true
            sleep 3
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                log_message "WARN" "🔨 Force stopping $service_name (PID: $pid)"
                kill -9 $pid 2>/dev/null || true
                sleep 1
            fi
            
            rm -f "$pid_file"
            log_message "INFO" "✅ $service_name stopped"
        else
            log_message "WARN" "⚠️  $service_name PID file exists but process not running"
            rm -f "$pid_file"
        fi
    else
        log_message "DEBUG" "ℹ️  No PID file found for $service_name"
    fi
}

# Function to kill processes on a port
kill_port_processes() {
    local port=$1
    local service_name=$2
    
    log_message "INFO" "🔍 Checking for processes on port $port..."
    
    if check_port $port; then
        log_message "WARN" "⚠️  Port $port is still in use. Stopping processes..."
        
        # Get PIDs using the port
        local pids=$(lsof -ti :$port 2>/dev/null)
        
        if [ -n "$pids" ]; then
            for pid in $pids; do
                log_message "INFO" "🛑 Stopping process $pid on port $port"
                kill -TERM $pid 2>/dev/null || true
            done
            
            # Wait for graceful shutdown
            sleep 3
            
            # Force kill if still running
            pids=$(lsof -ti :$port 2>/dev/null)
            if [ -n "$pids" ]; then
                for pid in $pids; do
                    log_message "WARN" "🔨 Force stopping process $pid on port $port"
                    kill -9 $pid 2>/dev/null || true
                done
                sleep 2
            fi
        fi
        
        # Verify port is now free
        if check_port $port; then
            log_message "ERROR" "❌ Failed to free port $port"
            return 1
        else
            log_message "INFO" "✅ Port $port is now free"
        fi
    else
        log_message "INFO" "✅ Port $port is already free"
    fi
}

# Function to stop monitoring
stop_monitoring() {
    log_message "INFO" "🛑 Stopping server monitoring..."
    
    if [ -f "$PID_DIR/monitor.pid" ]; then
        local monitor_pid=$(cat "$PID_DIR/monitor.pid")
        if kill -0 $monitor_pid 2>/dev/null; then
            log_message "INFO" "🛑 Stopping monitor process (PID: $monitor_pid)"
            kill -TERM $monitor_pid 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if kill -0 $monitor_pid 2>/dev/null; then
                log_message "WARN" "🔨 Force stopping monitor process (PID: $monitor_pid)"
                kill -9 $monitor_pid 2>/dev/null || true
            fi
            
            rm -f "$PID_DIR/monitor.pid"
            log_message "INFO" "✅ Monitor stopped"
        else
            log_message "WARN" "⚠️  Monitor PID file exists but process not running"
            rm -f "$PID_DIR/monitor.pid"
        fi
    else
        log_message "DEBUG" "ℹ️  No monitor PID file found"
    fi
}

# Function to kill by process name
kill_by_process_name() {
    log_message "INFO" "🛑 Stopping servers by process name..."
    
    # Kill uvicorn processes
    local uvicorn_pids=$(pgrep -f "uvicorn.*$API_PORT" 2>/dev/null || true)
    if [ -n "$uvicorn_pids" ]; then
        for pid in $uvicorn_pids; do
            log_message "INFO" "🛑 Stopping uvicorn process (PID: $pid)"
            kill -TERM $pid 2>/dev/null || true
        done
        sleep 2
    fi
    
    # Kill dashboard server processes
    local dashboard_pids=$(pgrep -f "professional_dashboard_server.py" 2>/dev/null || true)
    if [ -n "$dashboard_pids" ]; then
        for pid in $dashboard_pids; do
            log_message "INFO" "🛑 Stopping dashboard server process (PID: $pid)"
            kill -TERM $pid 2>/dev/null || true
        done
        sleep 2
    fi
    
    # Force kill any remaining processes
    pkill -9 -f "uvicorn.*$API_PORT" 2>/dev/null || true
    pkill -9 -f "professional_dashboard_server.py" 2>/dev/null || true
}

# Function to display final status
display_final_status() {
    echo ""
    echo -e "${CYAN}📊 FINAL STATUS${NC}"
    echo -e "${CYAN}==============${NC}"
    echo ""
    
    # API Server Status
    local api_info=$(get_port_process_info $API_PORT)
    if [ "$api_info" = "FREE" ]; then
        echo -e "${GREEN}✅ API Server (Port $API_PORT): Stopped${NC}"
    else
        echo -e "${RED}❌ API Server (Port $API_PORT): Still running${NC}"
        echo -e "${YELLOW}   Process: $api_info${NC}"
    fi
    
    # Dashboard Server Status
    local dashboard_info=$(get_port_process_info $DASHBOARD_PORT)
    if [ "$dashboard_info" = "FREE" ]; then
        echo -e "${GREEN}✅ Dashboard Server (Port $DASHBOARD_PORT): Stopped${NC}"
    else
        echo -e "${RED}❌ Dashboard Server (Port $DASHBOARD_PORT): Still running${NC}"
        echo -e "${YELLOW}   Process: $dashboard_info${NC}"
    fi
    
    echo ""
}

# Function to cleanup PID directory
cleanup_pid_directory() {
    if [ -d "$PID_DIR" ]; then
        local remaining_files=$(ls "$PID_DIR" 2>/dev/null | wc -l)
        if [ $remaining_files -gt 0 ]; then
            log_message "INFO" "🧹 Cleaning up PID directory..."
            rm -f "$PID_DIR"/*.pid 2>/dev/null || true
            log_message "INFO" "✅ PID directory cleaned"
        fi
    fi
}

# Main execution
main() {
    log_message "INFO" "Starting ZmartBot robust server shutdown process..."
    
    # Stop monitoring first
    stop_monitoring
    
    # Stop servers by PID files (graceful shutdown)
    log_message "INFO" "🛑 Stopping servers by PID files..."
    stop_by_pid_file "$PID_DIR/api_server.pid" "API Server"
    stop_by_pid_file "$PID_DIR/dashboard_server.pid" "Dashboard Server"
    
    # Kill by process name
    kill_by_process_name
    
    # Clean up any remaining processes on ports
    log_message "INFO" "🧹 Cleaning up any remaining processes..."
    kill_port_processes $API_PORT "API Server"
    kill_port_processes $DASHBOARD_PORT "Dashboard Server"
    
    # Clean up PID directory
    cleanup_pid_directory
    
    # Final verification
    log_message "INFO" "✅ Server shutdown completed!"
    display_final_status
    
    echo ""
    echo -e "${GREEN}✅ ZmartBot servers have been stopped${NC}"
    echo ""
    echo -e "${YELLOW}📝 Shutdown log: $LOG_FILE${NC}"
    echo ""
    echo -e "${BLUE}🚀 To restart servers, run: ./start_servers_robust.sh${NC}"
}

# Run main function
main "$@"
