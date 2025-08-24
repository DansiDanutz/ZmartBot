#!/bin/bash

# ZmartBot Server Stop Script
# This script properly stops API and Dashboard servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DASHBOARD_PORT=3400

echo -e "${BLUE}🛑 ZmartBot Server Stop Script${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port_processes() {
    local port=$1
    echo "🔍 Checking for processes on port $port..."
    
    if check_port $port; then
        echo "⚠️  Port $port is in use. Stopping processes..."
        
        # Get PIDs using the port
        local pids=$(lsof -ti :$port 2>/dev/null)
        
        if [ -n "$pids" ]; then
            for pid in $pids; do
                echo "🛑 Stopping process $pid on port $port"
                kill -TERM $pid 2>/dev/null || true
            done
            
            # Wait for graceful shutdown
            sleep 3
            
            # Force kill if still running
            pids=$(lsof -ti :$port 2>/dev/null)
            if [ -n "$pids" ]; then
                for pid in $pids; do
                    echo "🔨 Force stopping process $pid on port $port"
                    kill -9 $pid 2>/dev/null || true
                done
                sleep 1
            fi
        fi
        
        # Verify port is now free
        if check_port $port; then
            echo "❌ Failed to stop processes on port $port"
            return 1
        else
            echo "✅ Port $port is now free"
        fi
    else
        echo "✅ Port $port is already free"
    fi
}

# Function to stop servers by PID files
stop_by_pid_files() {
    echo "🛑 Stopping servers by PID files..."
    
    # Stop API server
    if [ -f "backend/zmart-api/api_server.pid" ]; then
        local api_pid=$(cat backend/zmart-api/api_server.pid)
        echo "🛑 Stopping API server (PID: $api_pid)"
        kill -TERM $api_pid 2>/dev/null || true
        rm -f backend/zmart-api/api_server.pid
    fi
    
    # Stop dashboard server
    if [ -f "dashboard_server.pid" ]; then
        local dashboard_pid=$(cat dashboard_server.pid)
        echo "🛑 Stopping dashboard server (PID: $dashboard_pid)"
        kill -TERM $dashboard_pid 2>/dev/null || true
        rm -f dashboard_server.pid
    fi
}

# Function to kill by process name
kill_by_process_name() {
    echo "🛑 Stopping servers by process name..."
    
    # Kill uvicorn processes
    pkill -f "uvicorn.*$API_PORT" 2>/dev/null || true
    pkill -f "professional_dashboard_server" 2>/dev/null || true
    
    # Wait for processes to stop
    sleep 2
}

# Main execution
main() {
    echo "Starting ZmartBot server shutdown process..."
    
    # Stop by PID files first (graceful shutdown)
    stop_by_pid_files
    
    # Kill by process name
    kill_by_process_name
    
    # Clean up any remaining processes on ports
    echo "🧹 Cleaning up any remaining processes..."
    kill_port_processes $API_PORT
    kill_port_processes $DASHBOARD_PORT
    
    # Final verification
    echo ""
    echo -e "${GREEN}✅ Server shutdown completed!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Final status:${NC}"
    echo -e "${YELLOW}   Port $API_PORT: $([ check_port $API_PORT ] && echo "❌ Still in use" || echo "✅ Free")${NC}"
    echo -e "${YELLOW}   Port $DASHBOARD_PORT: $([ check_port $DASHBOARD_PORT ] && echo "❌ Still in use" || echo "✅ Free")${NC}"
    echo ""
    echo -e "${BLUE}🚀 To restart servers, run: ./start_servers.sh${NC}"
}

# Run main function
main "$@"
