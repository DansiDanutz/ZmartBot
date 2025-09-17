#!/bin/bash

# Start MDC Orchestration Agent
# This script starts the MDC Orchestration Agent that coordinates all MDC management aspects

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENT_DIR="$SCRIPT_DIR"
AGENT_SCRIPT="$AGENT_DIR/mdc_orchestration_agent.py"
LOG_FILE="$AGENT_DIR/mdc_orchestration_agent.log"
PID_FILE="$AGENT_DIR/mdc_orchestration_agent.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[MDC-ORCHESTRATION]${NC} $1"
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

# Function to check if agent is running
is_agent_running() {
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

# Function to start the agent
start_agent() {
    print_status "Starting MDC Orchestration Agent..."
    
    # Check if already running
    if is_agent_running; then
        print_warning "MDC Orchestration Agent is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    # Validate environment
    if [ ! -f "$AGENT_SCRIPT" ]; then
        print_error "Agent script not found: $AGENT_SCRIPT"
        exit 1
    fi
    
    # Check Python requirements
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Set environment variables
    export PROJECT_ROOT="$PROJECT_ROOT"
    export MDC_ORCHESTRATION_PORT="${MDC_ORCHESTRATION_PORT:-8615}"
    export PYTHONPATH="$AGENT_DIR:$PYTHONPATH"
    
    # Start the agent in background
    cd "$AGENT_DIR"
    nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
    local agent_pid=$!
    
    # Save PID
    echo "$agent_pid" > "$PID_FILE"
    
    # Wait a moment and check if it's running
    sleep 2
    if is_agent_running; then
        print_success "MDC Orchestration Agent started successfully"
        print_status "PID: $agent_pid"
        print_status "Port: $MDC_ORCHESTRATION_PORT"
        print_status "Log: $LOG_FILE"
        print_status "API: http://localhost:$MDC_ORCHESTRATION_PORT"
        
        # Test the health endpoint
        sleep 3
        if curl -s "http://localhost:$MDC_ORCHESTRATION_PORT/health" > /dev/null 2>&1; then
            print_success "Health check passed - Agent is responding"
        else
            print_warning "Health check failed - Agent may still be starting up"
        fi
        
        return 0
    else
        print_error "Failed to start MDC Orchestration Agent"
        if [ -f "$LOG_FILE" ]; then
            print_error "Last few lines of log:"
            tail -10 "$LOG_FILE"
        fi
        return 1
    fi
}

# Function to stop the agent
stop_agent() {
    print_status "Stopping MDC Orchestration Agent..."
    
    if is_agent_running; then
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
            print_warning "Forcing kill of agent process"
            kill -9 "$pid"
        fi
        
        rm -f "$PID_FILE"
        print_success "MDC Orchestration Agent stopped"
    else
        print_warning "MDC Orchestration Agent is not running"
    fi
}

# Function to restart the agent
restart_agent() {
    stop_agent
    sleep 2
    start_agent
}

# Function to show agent status
status_agent() {
    print_status "Checking MDC Orchestration Agent status..."
    
    if is_agent_running; then
        local pid=$(cat "$PID_FILE")
        print_success "MDC Orchestration Agent is running (PID: $pid)"
        
        # Show port info
        local port="${MDC_ORCHESTRATION_PORT:-8615}"
        print_status "Port: $port"
        print_status "API: http://localhost:$port"
        
        # Test health endpoint
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "Health check: PASSED"
            
            # Get detailed status
            local status_json=$(curl -s "http://localhost:$port/status" 2>/dev/null || echo "{}")
            if [ "$status_json" != "{}" ]; then
                print_status "System Status:"
                echo "$status_json" | python3 -m json.tool 2>/dev/null || echo "$status_json"
            fi
        else
            print_warning "Health check: FAILED"
        fi
    else
        print_warning "MDC Orchestration Agent is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "MDC Orchestration Agent logs:"
        tail -n 50 "$LOG_FILE"
    else
        print_warning "No log file found: $LOG_FILE"
    fi
}

# Function to trigger orchestration
trigger_orchestration() {
    local port="${MDC_ORCHESTRATION_PORT:-8615}"
    local type="${1:-full}"
    
    print_status "Triggering $type orchestration..."
    
    if ! is_agent_running; then
        print_error "MDC Orchestration Agent is not running"
        exit 1
    fi
    
    local endpoint="/orchestrate"
    if [ "$type" == "incremental" ]; then
        endpoint="/orchestrate/incremental"
    fi
    
    local response=$(curl -s -X POST "http://localhost:$port$endpoint" 2>/dev/null || echo "{}")
    if [ "$response" != "{}" ]; then
        print_success "Orchestration triggered successfully"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        print_error "Failed to trigger orchestration"
        exit 1
    fi
}

# Main script logic
case "${1:-start}" in
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
        status_agent
        ;;
    logs)
        show_logs
        ;;
    orchestrate)
        trigger_orchestration "${2:-full}"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|orchestrate [full|incremental]}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the MDC Orchestration Agent"
        echo "  stop      - Stop the MDC Orchestration Agent"
        echo "  restart   - Restart the MDC Orchestration Agent"
        echo "  status    - Show agent status and health"
        echo "  logs      - Show recent logs"
        echo "  orchestrate [type] - Trigger orchestration (full or incremental)"
        echo ""
        echo "Environment Variables:"
        echo "  MDC_ORCHESTRATION_PORT - Port for the agent (default: 8615)"
        echo "  OPENAI_API_KEY - OpenAI API key for AI-powered features"
        exit 1
        ;;
esac