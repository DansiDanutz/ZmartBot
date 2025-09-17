#!/bin/bash

# 🛑 ZMARTBOT STOP - Clean shutdown
# ================================
# Usage: ./STOP_ZMARTBOT.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🛑 STOPPING ZMARTBOT${NC}"
echo -e "${RED}===================${NC}"

# Stop processes
echo -e "${YELLOW}Stopping Backend API...${NC}"
pkill -f "python3 run_dev.py" 2>/dev/null && echo -e "${GREEN}✅ Backend API stopped${NC}" || echo -e "${YELLOW}⚠️ No Backend API running${NC}"

echo -e "${YELLOW}Stopping Dashboard Server...${NC}"
pkill -f "professional_dashboard_server.py" 2>/dev/null && echo -e "${GREEN}✅ Dashboard Server stopped${NC}" || echo -e "${YELLOW}⚠️ No Dashboard Server running${NC}"

echo -e "${YELLOW}Stopping Orchestration Agent...${NC}"
pkill -f "orchestration_agent" 2>/dev/null && echo -e "${GREEN}✅ Orchestration Agent stopped${NC}" || echo -e "${YELLOW}⚠️ No Orchestration Agent running${NC}"

echo -e "${YELLOW}Stopping Auto-Sync Service...${NC}"
if [ -x "./sync_always.sh" ]; then
    ./sync_always.sh stop
else
    echo -e "${YELLOW}⚠️ Auto-sync script not found${NC}"
fi

# Clean up PID files
rm -f /Users/dansidanutz/Desktop/ZmartBot/project/backend/api/api_server.pid 2>/dev/null
rm -f /Users/dansidanutz/Desktop/ZmartBot/project/backend/api/dashboard_server.pid 2>/dev/null
rm -f /Users/dansidanutz/Desktop/ZmartBot/project/backend/api/orchestration_agent.pid 2>/dev/null

echo ""
echo -e "${GREEN}✅ ZmartBot completely stopped${NC}"
echo -e "${BLUE}🚀 To restart: ./START_ZMARTBOT.sh${NC}"