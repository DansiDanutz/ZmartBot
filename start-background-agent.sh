#!/bin/bash

# Start API-MCP Background Agent
# This ensures the agent runs persistently

echo "🤖 Starting API-MCP Background Agent"
echo "===================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
AGENT_SCRIPT="$PROJECT_ROOT/zmart-api/api_mcp_background_agent.py"
PID_FILE="$PROJECT_ROOT/zmart-api/logs/api_mcp_agent.pid"
LOG_FILE="$PROJECT_ROOT/zmart-api/logs/api_mcp_agent.log"

# Function to check if agent is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # Also check by process name
    if pgrep -f "api_mcp_background_agent.py" > /dev/null; then
        return 0
    fi

    return 1
}

# Stop existing agent if running
if is_running; then
    echo -e "${YELLOW}Stopping existing agent...${NC}"
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") 2>/dev/null
    fi
    pkill -f "api_mcp_background_agent.py" 2>/dev/null
    sleep 2
fi

# Create logs directory
mkdir -p "$PROJECT_ROOT/zmart-api/logs"

# Start the agent
echo -e "${YELLOW}Starting background agent...${NC}"
cd "$PROJECT_ROOT/zmart-api"
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

# Wait and verify
sleep 3

if is_running; then
    echo -e "${GREEN}✅ Background agent started successfully (PID: $PID)${NC}"
    echo ""
    echo "Recent logs:"
    tail -n 5 "$LOG_FILE"
    echo ""
    echo -e "${GREEN}Agent will continue running even after terminal closes${NC}"
else
    echo -e "${RED}❌ Failed to start background agent${NC}"
    echo "Check logs at: $LOG_FILE"
    exit 1
fi