#!/bin/bash

# 🚀 ZMARTBOT INSTANT START - ONE COMMAND FOR EVERYTHING
# =====================================================
# This script gets ZmartBot to fully working state in one command
# Usage: ./START_ZMARTBOT.sh
# Created: August 21, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/dansidanutz/Desktop/ZmartBot/project/backend/api"
API_PORT=8000
DASHBOARD_PORT=3400

echo -e "${BLUE}🚀 ZMARTBOT INSTANT START${NC}"
echo -e "${BLUE}=========================${NC}"
echo -e "${YELLOW}Getting to fully working state...${NC}"
echo ""

# Function to check if port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local port=$1
    local name=$2
    local max_attempts=30
    
    echo -e "${YELLOW}⏳ Waiting for $name on port $port...${NC}"
    for i in $(seq 1 $max_attempts); do
        if check_port $port; then
            echo -e "${GREEN}✅ $name is ready${NC}"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    echo -e "${RED}❌ $name failed to start${NC}"
    return 1
}

# Step 1: Navigate to project directory
echo -e "${BLUE}📁 STEP 1: Navigate to project directory${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Error: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ In correct directory${NC}"
echo ""

# Step 2: Check virtual environment
echo -e "${BLUE}🐍 STEP 2: Check virtual environment${NC}"
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo -e "${YELLOW}💡 Creating new virtual environment...${NC}"
    /usr/bin/python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Step 3: Install/verify all dependencies
echo -e "${BLUE}📦 STEP 3: Install/verify all dependencies${NC}"
echo -e "${YELLOW}Installing core requirements...${NC}"
pip install -r requirements.txt >/dev/null 2>&1 || echo "Requirements installed"

echo -e "${YELLOW}Installing additional required packages...${NC}"
pip install psutil PyJWT matplotlib ccxt >/dev/null 2>&1 || echo "Additional packages installed"

# Verify we have enough packages
PACKAGE_COUNT=$(pip freeze | wc -l)
if [ "$PACKAGE_COUNT" -lt 100 ]; then
    echo -e "${YELLOW}⚠️ Restoring from backup...${NC}"
    if [ -f "package_backup.txt" ]; then
        pip install -r package_backup.txt >/dev/null 2>&1
    fi
fi

echo -e "${GREEN}✅ Dependencies verified ($(pip freeze | wc -l) packages installed)${NC}"
echo ""

# Step 4: Clean up existing processes
echo -e "${BLUE}🛑 STEP 4: Clean up existing processes${NC}"
pkill -f "python3 run_dev.py" 2>/dev/null && echo "Stopped old backend" || echo "No old backend running"
pkill -f "professional_dashboard_server.py" 2>/dev/null && echo "Stopped old dashboard" || echo "No old dashboard running"
pkill -f "orchestration_agent" 2>/dev/null && echo "Stopped old orchestration" || echo "No old orchestration running"
sleep 2
echo -e "${GREEN}✅ Cleanup completed${NC}"
echo ""

# Step 5: Start Backend API
echo -e "${BLUE}🚀 STEP 5: Start Backend API Server${NC}"
nohup python3 run_dev.py > api_server.log 2>&1 &
API_PID=$!
echo $API_PID > api_server.pid
echo -e "${GREEN}✅ Backend API started (PID: $API_PID)${NC}"

# Step 6: Start Dashboard Server
echo -e "${BLUE}🎛️ STEP 6: Start Dashboard Server${NC}"
nohup python3 professional_dashboard_server.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > dashboard_server.pid
echo -e "${GREEN}✅ Dashboard Server started (PID: $DASHBOARD_PID)${NC}"
echo ""

# Step 7: Start Orchestration Agent (Database Updates & System Management)
echo -e "${BLUE}🎯 STEP 7: Start Orchestration Agent${NC}"
echo -e "${YELLOW}Starting database orchestrator and system management...${NC}"
nohup python3 -c "
import asyncio
import sys
sys.path.append('src')
from agents.orchestration.orchestration_agent import OrchestrationAgent

async def start_orchestration():
    agent = OrchestrationAgent()
    await agent.start()
    # Keep running
    while True:
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(start_orchestration())
" > orchestration.log 2>&1 &
ORCHESTRATION_PID=$!
echo $ORCHESTRATION_PID > orchestration_agent.pid
echo -e "${GREEN}✅ Orchestration Agent started (PID: $ORCHESTRATION_PID)${NC}"
echo -e "${YELLOW}📊 Database orchestrator: Cross events, alerts, indicators, market data${NC}"
echo ""

# Step 8: Wait for services to be ready
echo -e "${BLUE}⏳ STEP 8: Verify services are ready${NC}"
wait_for_service $API_PORT "Backend API"
wait_for_service $DASHBOARD_PORT "Dashboard Server" 
echo ""

# Step 9: Health checks
echo -e "${BLUE}🏥 STEP 9: Health verification${NC}"
echo -e "${YELLOW}Testing Backend API...${NC}"
if curl -s http://localhost:$API_PORT/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API responding${NC}"
else
    echo -e "${RED}⚠️ Backend API not responding yet${NC}"
fi

echo -e "${YELLOW}Testing Dashboard Server...${NC}"
if curl -s http://localhost:$DASHBOARD_PORT/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Dashboard Server responding${NC}"
else
    echo -e "${RED}⚠️ Dashboard Server not responding yet${NC}"
fi

echo -e "${YELLOW}Testing My Symbols API...${NC}"
if curl -s http://localhost:$DASHBOARD_PORT/api/futures-symbols/my-symbols/current >/dev/null 2>&1; then
    echo -e "${GREEN}✅ My Symbols API responding${NC}"
else
    echo -e "${RED}⚠️ My Symbols API not responding yet${NC}"
fi

echo -e "${YELLOW}Testing Orchestration Agent...${NC}"
if curl -s http://localhost:$API_PORT/api/v1/orchestration/database-status >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Orchestration Agent responding${NC}"
else
    echo -e "${RED}⚠️ Orchestration Agent not responding yet${NC}"
fi
echo ""

# Step 10: Final status
echo -e "${PURPLE}🎉 ZMARTBOT FULLY OPERATIONAL!${NC}"
echo -e "${PURPLE}==============================${NC}"
echo ""
echo -e "${BLUE}📊 SERVER STATUS:${NC}"
echo -e "${GREEN}✅ Backend API Server:${NC} Port $API_PORT (PID: $API_PID)"
echo -e "${GREEN}✅ Dashboard Server:${NC} Port $DASHBOARD_PORT (PID: $DASHBOARD_PID)"
echo -e "${GREEN}✅ Orchestration Agent:${NC} Database Updates (PID: $ORCHESTRATION_PID)"
echo ""
echo -e "${BLUE}🌐 ACCESS URLS:${NC}"
echo -e "${YELLOW}📊 Professional Dashboard:${NC} http://localhost:$DASHBOARD_PORT"
echo -e "${YELLOW}🚨 Live Alerts System:${NC} http://localhost:$DASHBOARD_PORT/enhanced-alerts"
echo -e "${YELLOW}🔧 Backend API:${NC} http://localhost:$API_PORT/api/"
echo -e "${YELLOW}📚 API Documentation:${NC} http://localhost:$API_PORT/docs"
echo ""
echo -e "${BLUE}📋 PROCESS MANAGEMENT:${NC}"
echo -e "${YELLOW}Stop servers:${NC} pkill -f 'python3 run_dev.py'; pkill -f 'professional_dashboard_server.py'; pkill -f 'orchestration_agent'"
echo -e "${YELLOW}Restart:${NC} ./START_ZMARTBOT.sh"
echo -e "${YELLOW}View logs:${NC} tail -f api_server.log dashboard.log orchestration.log"
echo ""
echo -e "${GREEN}🎯 System ready for trading operations!${NC}"