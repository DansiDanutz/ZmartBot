#!/bin/bash

# ZmartBot Auto-Start Sync Script
# This script ensures sync is always running

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="/Users/dansidanutz/Desktop/ZmartBot"
PLIST_FILE="$HOME/Library/LaunchAgents/com.zmartbot.sync.plist"

echo -e "${BLUE}🚀 ZmartBot Auto-Sync Startup${NC}"
echo "=================================="

# Function to check if service is running
check_service_status() {
    if launchctl list | grep -q "com.zmartbot.sync"; then
        echo -e "${GREEN}✅ Sync service is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Sync service not running${NC}"
        return 1
    fi
}

# Function to start the service
start_service() {
    echo -e "${BLUE}🔄 Starting sync service...${NC}"
    
    # Load the service if it exists
    if [ -f "$PLIST_FILE" ]; then
        launchctl load "$PLIST_FILE" 2>/dev/null || true
    else
        # Install the service if it doesn't exist
        echo -e "${YELLOW}📦 Installing sync service...${NC}"
        "$SCRIPT_DIR/sync_claude_folders.sh" install
    fi
}

# Function to ensure sync is always active
ensure_sync_active() {
    if ! check_service_status; then
        start_service
        sleep 2
        if check_service_status; then
            echo -e "${GREEN}✅ Sync service started successfully${NC}"
        else
            echo -e "${YELLOW}⚠️ Starting sync in watch mode directly...${NC}"
            # Fallback: start sync in background
            nohup "$SCRIPT_DIR/sync_claude_folders.sh" watch > /tmp/zmartbot-sync-fallback.log 2>&1 &
            echo $! > /tmp/zmartbot-sync.pid
            echo -e "${GREEN}✅ Sync started in background (PID: $(cat /tmp/zmartbot-sync.pid))${NC}"
        fi
    fi
}

# Function to do initial sync
do_initial_sync() {
    echo -e "${BLUE}🔄 Performing initial sync...${NC}"
    "$SCRIPT_DIR/sync_claude_folders.sh" sync
}

# Main execution
main() {
    # Always do an initial sync
    do_initial_sync
    
    # Ensure continuous sync is active
    ensure_sync_active
    
    # Show status
    echo ""
    echo -e "${GREEN}🎉 ZmartBot sync is now active!${NC}"
    echo "  • Logs: /tmp/zmartbot-sync.log"
    echo "  • Status: Auto-sync running in background"
    echo "  • Manual sync: ./sync.sh"
}

# Check if fswatch is available (required for watch mode)
if ! command -v fswatch &> /dev/null; then
    echo -e "${YELLOW}⚠️ Installing fswatch for file monitoring...${NC}"
    if command -v brew &> /dev/null; then
        brew install fswatch
    else
        echo -e "${YELLOW}⚠️ Homebrew not found. Please install fswatch manually: brew install fswatch${NC}"
    fi
fi

# Run main function
main "$@"