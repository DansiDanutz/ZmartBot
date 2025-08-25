#!/bin/bash
# Start Background MDC Agent for Cursor

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Background MDC Agent...${NC}"

# Change to project directory
cd /Users/dansidanutz/Desktop/ZmartBot

# Check if agent script exists
if [ ! -f "zmart-api/background_mdc_agent.py" ]; then
    echo -e "${RED}❌ Background MDC Agent script not found!${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi

# Kill any existing background agent processes
echo -e "${YELLOW}🔄 Stopping any existing background agents...${NC}"
pkill -f background_mdc_agent.py

# Wait a moment for processes to stop
sleep 2

# Start the background agent
echo -e "${GREEN}✅ Starting Background MDC Agent...${NC}"
nohup python3 zmart-api/background_mdc_agent.py > zmart-api/background_mdc_agent.log 2>&1 &

# Get the process ID
AGENT_PID=$!

# Save PID to file for easy management
echo $AGENT_PID > zmart-api/background_mdc_agent.pid

echo -e "${GREEN}✅ Background MDC Agent started with PID: $AGENT_PID${NC}"
echo -e "${BLUE}📝 Log file: zmart-api/background_mdc_agent.log${NC}"
echo -e "${BLUE}🔄 Monitoring MDC files every 5 minutes...${NC}"
echo -e "${YELLOW}💡 To stop the agent: ./stop_background_mdc_agent.sh${NC}"

# Show initial log output
echo -e "${BLUE}📋 Recent log output:${NC}"
tail -n 5 zmart-api/background_mdc_agent.log 2>/dev/null || echo "No log output yet..."
