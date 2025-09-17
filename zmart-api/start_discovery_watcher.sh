#!/bin/bash

# 🔍 Discovery Database File Watcher Startup Script
# Professional file monitoring service for ZmartBot
# Monitors .py and .mdc files automatically

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WATCHER_SCRIPT="$SCRIPT_DIR/discovery_file_watcher_professional.py"
PID_FILE="$SCRIPT_DIR/discovery_watcher.pid"
LOG_FILE="$SCRIPT_DIR/discovery_watcher.log"

echo -e "${BLUE}🔍 Discovery Database File Watcher${NC}"
echo "=================================="

# Check if script exists
if [ ! -f "$WATCHER_SCRIPT" ]; then
    echo -e "${RED}❌ Watcher script not found: $WATCHER_SCRIPT${NC}"
    exit 1
fi

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo -e "${GREEN}✅ Watcher already running (PID: $(cat "$PID_FILE"))${NC}"
    exit 0
fi

# Start the watcher
echo -e "${BLUE}🚀 Starting Discovery File Watcher...${NC}"
nohup python3 "$WATCHER_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if kill -0 $PID 2>/dev/null; then
    echo -e "${GREEN}✅ Discovery File Watcher started successfully${NC}"
    echo -e "${BLUE}📋 PID: $PID${NC}"
    echo -e "${BLUE}📝 Log: $LOG_FILE${NC}"
    echo -e "${BLUE}📊 Status: Monitoring for .py and .mdc file changes${NC}"
    echo ""
    echo -e "${GREEN}🎯 The watcher is now running in the background!${NC}"
    echo -e "${BLUE}💡 Use 'pkill -f discovery_file_watcher_professional' to stop${NC}"
else
    echo -e "${RED}❌ Failed to start Discovery File Watcher${NC}"
    rm -f "$PID_FILE"
    exit 1
fi