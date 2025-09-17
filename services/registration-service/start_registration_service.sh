#!/bin/bash

# Registration Service Startup Script
# ZmartBot Registration Service - Enterprise-grade service registration and management system

set -e

# Service configuration
SERVICE_NAME="registration-service"
SERVICE_PORT=8902
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SERVICE_DIR/registration_service.log"
PID_FILE="$SERVICE_DIR/registration_service.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check if service is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Start the service
start_service() {
    log "Starting $SERVICE_NAME..."
    
    if check_running; then
        log_warning "$SERVICE_NAME is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    # Change to service directory
    cd "$SERVICE_DIR"
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Start the service
    log "Starting $SERVICE_NAME on port $SERVICE_PORT..."
    nohup python3 registration_service.py --port "$SERVICE_PORT" > "$LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    # Wait for service to start
    log "Waiting for service to start..."
    sleep 3
    
    # Check if service started successfully
    if check_running; then
        log_success "$SERVICE_NAME started successfully (PID: $(cat $PID_FILE))"
        log "Service is running on http://localhost:$SERVICE_PORT"
        log "Dashboard available at http://localhost:$SERVICE_PORT/dashboard"
        log "Health check at http://localhost:$SERVICE_PORT/health"
        log "Logs available at $LOG_FILE"
    else
        log_error "Failed to start $SERVICE_NAME"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the service
stop_service() {
    log "Stopping $SERVICE_NAME..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            log "Sent SIGTERM to PID $PID"
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                log_warning "Force killing PID $PID"
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            log_success "$SERVICE_NAME stopped"
        else
            log_warning "$SERVICE_NAME is not running"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "PID file not found, $SERVICE_NAME may not be running"
    fi
}

# Restart the service
restart_service() {
    log "Restarting $SERVICE_NAME..."
    stop_service
    sleep 2
    start_service
}

# Check service status
status_service() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        log_success "$SERVICE_NAME is running (PID: $PID)"
        log "Service URL: http://localhost:$SERVICE_PORT"
        log "Dashboard: http://localhost:$SERVICE_PORT/dashboard"
        log "Health: http://localhost:$SERVICE_PORT/health"
        
        # Check health endpoint
        if command -v curl > /dev/null 2>&1; then
            if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
                log_success "Health check passed"
            else
                log_warning "Health check failed"
            fi
        fi
    else
        log_error "$SERVICE_NAME is not running"
        return 1
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log "Showing logs for $SERVICE_NAME..."
        tail -f "$LOG_FILE"
    else
        log_error "Log file not found: $LOG_FILE"
        return 1
    fi
}

# Show help
show_help() {
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the Registration Service"
    echo "  stop    - Stop the Registration Service"
    echo "  restart - Restart the Registration Service"
    echo "  status  - Show service status"
    echo "  logs    - Show service logs"
    echo "  help    - Show this help message"
    echo ""
    echo "Service Information:"
    echo "  Name: $SERVICE_NAME"
    echo "  Port: $SERVICE_PORT"
    echo "  Directory: $SERVICE_DIR"
    echo "  Log File: $LOG_FILE"
    echo "  PID File: $PID_FILE"
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
        status_service
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
