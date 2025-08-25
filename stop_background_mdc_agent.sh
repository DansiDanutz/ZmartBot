#!/bin/bash
# Stop Background MDC Agent for Cursor

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Background MDC Agent...${NC}"

# Change to project directory
cd /Users/dansidanutz/Desktop/ZmartBot

# Check if PID file exists
if [ -f "zmart-api/background_mdc_agent.pid" ]; then
    AGENT_PID=$(cat zmart-api/background_mdc_agent.pid)
    echo -e "${YELLOW}🔄 Stopping agent with PID: $AGENT_PID${NC}"
    
    # Try to kill the process gracefully
    if kill -TERM $AGENT_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Background MDC Agent stopped gracefully${NC}"
    else
        echo -e "${YELLOW}⚠️ Process not found, trying force kill...${NC}"
        kill -KILL $AGENT_PID 2>/dev/null || echo -e "${YELLOW}⚠️ Process already stopped${NC}"
    fi
    
    # Remove PID file
    rm -f zmart-api/background_mdc_agent.pid
else
    echo -e "${YELLOW}⚠️ PID file not found, trying to kill by process name...${NC}"
fi

# Kill any remaining processes
pkill -f background_mdc_agent.py

echo -e "${GREEN}✅ Background MDC Agent stopped${NC}"
echo -e "${BLUE}📝 Log file: zmart-api/background_mdc_agent.log${NC}"
