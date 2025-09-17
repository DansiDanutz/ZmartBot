#!/bin/bash

# GptMDSagentService Startup Script
# =================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="GptMDSagentService"
SERVICE_PORT=8700
PYTHON_PATH="python3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$SCRIPT_DIR"
LOG_FILE="$SERVICE_DIR/logs/service.log"
PID_FILE="$SERVICE_DIR/logs/service.pid"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v $PYTHON_PATH &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_PATH --version 2>&1 | cut -d' ' -f2)
    log_info "Python version: $PYTHON_VERSION"
    
    # Check if requirements are installed
    if [ ! -f "$SERVICE_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Check if main script exists
    if [ ! -f "$SERVICE_DIR/src/main.py" ]; then
        log_error "main.py not found"
        exit 1
    fi
}

check_environment() {
    log_info "Checking environment..."
    
    # Check OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warning "OPENAI_API_KEY not set"
        log_info "Please set OPENAI_API_KEY environment variable"
        log_info "Example: export OPENAI_API_KEY='your-api-key'"
        exit 1
    fi
    
    # Check if port is available
    if lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "Port $SERVICE_PORT is already in use"
        log_info "Please stop the service using the port or change the port"
        exit 1
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p "$SERVICE_DIR/logs"
    mkdir -p "$SERVICE_DIR/cache"
}

install_dependencies() {
    log_info "Installing dependencies..."
    
    cd "$SERVICE_DIR"
    
    if [ -f "requirements.txt" ]; then
        $PYTHON_PATH -m pip install -r requirements.txt
        log_success "Dependencies installed"
    else
        log_warning "requirements.txt not found, skipping dependency installation"
    fi
}

start_service() {
    log_info "Starting $SERVICE_NAME..."
    
    cd "$SERVICE_DIR"
    
    # Start the service in background
    nohup $PYTHON_PATH src/main.py \
        --host 0.0.0.0 \
        --port $SERVICE_PORT \
        --log-level INFO \
        > "$LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    # Wait a moment for service to start
    sleep 3
    
    # Check if service is running
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        log_success "$SERVICE_NAME started successfully"
        log_info "PID: $(cat $PID_FILE)"
        log_info "Port: $SERVICE_PORT"
        log_info "Logs: $LOG_FILE"
        log_info "Health check: http://localhost:$SERVICE_PORT/health"
    else
        log_error "Failed to start $SERVICE_NAME"
        log_info "Check logs: $LOG_FILE"
        exit 1
    fi
}

stop_service() {
    log_info "Stopping $SERVICE_NAME..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            log_success "$SERVICE_NAME stopped"
        else
            log_warning "Service not running"
        fi
        rm -f "$PID_FILE"
    else
        log_warning "PID file not found"
    fi
}

restart_service() {
    log_info "Restarting $SERVICE_NAME..."
    stop_service
    sleep 2
    start_service
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            log_success "$SERVICE_NAME is running (PID: $PID)"
            log_info "Port: $SERVICE_PORT"
            log_info "Health: http://localhost:$SERVICE_PORT/health"
        else
            log_warning "$SERVICE_NAME is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "$SERVICE_NAME is not running"
    fi
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        log_warning "Log file not found: $LOG_FILE"
    fi
}

show_help() {
    echo "Usage: $0 {start|stop|restart|status|logs|install|check}"
    echo ""
    echo "Commands:"
    echo "  start     Start the service"
    echo "  stop      Stop the service"
    echo "  restart   Restart the service"
    echo "  status    Check service status"
    echo "  logs      Show service logs"
    echo "  install   Install dependencies"
    echo "  check     Check dependencies and environment"
    echo ""
    echo "Environment variables:"
    echo "  OPENAI_API_KEY    OpenAI API key (required)"
    echo "  REGISTRY_URL      ZmartBot registry URL (default: http://localhost:8610)"
    echo "  LOG_LEVEL         Log level (default: INFO)"
}

# Main script
case "$1" in
    start)
        check_dependencies
        check_environment
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        check_dependencies
        check_environment
        restart_service
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    install)
        install_dependencies
        ;;
    check)
        check_dependencies
        check_environment
        log_success "All checks passed"
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0
