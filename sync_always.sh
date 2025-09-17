#!/bin/bash

# ZmartBot Always-On Sync - Simple Background Process
# This runs continuously in the background to keep folders in sync

SYNC_SCRIPT="/Users/dansidanutz/Desktop/ZmartBot/sync_claude_folders.sh"
PID_FILE="/tmp/zmartbot-sync-always.pid"
LOG_FILE="/tmp/zmartbot-sync-always.log"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 ZmartBot Always-On Sync${NC}" | tee -a "$LOG_FILE"
echo "==============================" | tee -a "$LOG_FILE"

# Function to check if already running
is_running() {
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

# Function to start sync loop
start_sync_loop() {
    echo "$(date): Starting sync loop..." >> "$LOG_FILE"
    
    # Store PID
    echo $$ > "$PID_FILE"
    
    # Initial sync
    "$SYNC_SCRIPT" sync >> "$LOG_FILE" 2>&1
    
    # Install fswatch if needed
    if ! command -v fswatch &> /dev/null; then
        echo "$(date): Installing fswatch..." >> "$LOG_FILE"
        brew install fswatch >> "$LOG_FILE" 2>&1 || {
            echo "$(date): Failed to install fswatch, using polling method" >> "$LOG_FILE"
            # Fallback to polling
            while true; do
                sleep 30
                "$SYNC_SCRIPT" sync >> "$LOG_FILE" 2>&1
            done
            return
        }
    fi
    
    # Watch for changes and sync
    fswatch -o \
        "/Users/dansidanutz/Desktop/ZmartBot/.claude" \
        "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules" \
        2>/dev/null | while read f; do
            echo "$(date): Changes detected, syncing..." >> "$LOG_FILE"
            "$SYNC_SCRIPT" sync >> "$LOG_FILE" 2>&1
        done
}

# Function to stop sync
stop_sync() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ Sync stopped${NC}"
        fi
    fi
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ Sync is running (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}⚠️ Sync is not running${NC}"
    fi
}

# Main function
case "${1:-start}" in
    "start")
        if is_running; then
            echo -e "${YELLOW}⚠️ Sync already running${NC}"
            show_status
        else
            echo -e "${BLUE}🚀 Starting background sync...${NC}"
            # Run in background
            nohup "$0" loop > /dev/null 2>&1 &
            sleep 1
            show_status
        fi
        ;;
    "stop")
        stop_sync
        ;;
    "status")
        show_status
        ;;
    "restart")
        stop_sync
        sleep 1
        "$0" start
        ;;
    "loop")
        # This is the actual background loop - don't call directly
        start_sync_loop
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo "  start   - Start background sync"
        echo "  stop    - Stop background sync"
        echo "  status  - Show sync status"
        echo "  restart - Restart sync service"
        ;;
esac