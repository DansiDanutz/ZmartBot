#!/bin/bash

# Start Service Dashboard with proper API backend
# This replaces the old simple HTTP server

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DASHBOARD_DIR="./dashboard/Service-Dashboard"
PORT=3000

echo -e "${BLUE}🚀 Starting ZmartBot Service Dashboard${NC}"

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Stop any existing dashboard processes
echo -e "${YELLOW}🛑 Stopping existing dashboard processes...${NC}"
pkill -f "server.py.*3000" 2>/dev/null || true
pkill -f "api_server.py.*3000" 2>/dev/null || true
sleep 2

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python3 -c "import fastapi, uvicorn, httpx, psutil" >/dev/null 2>&1; then
    echo -e "${YELLOW}⬇️  Installing dependencies...${NC}"
    python3 -m pip install fastapi uvicorn httpx psutil --quiet
fi

# Start the new API server
echo -e "${BLUE}🚀 Starting FastAPI service dashboard...${NC}"
cd "$DASHBOARD_DIR"

# Start in background
nohup python3 api_server.py --port $PORT > /tmp/service_dashboard.log 2>&1 &
SERVER_PID=$!

# Wait and check if it started successfully
sleep 3

if port_in_use $PORT; then
    echo -e "${GREEN}✅ Service Dashboard started successfully on port $PORT${NC}"
    echo -e "${GREEN}📊 Dashboard URL: http://localhost:$PORT${NC}"
    echo -e "${GREEN}🏥 Health API: http://localhost:$PORT/health${NC}"
    echo -e "${GREEN}📋 Services API: http://localhost:$PORT/api/services/status${NC}"
    
    # Save PID for management
    echo $SERVER_PID > /tmp/service_dashboard.pid
    
    # Quick health check
    sleep 1
    if curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}🎉 Dashboard is healthy and responding!${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard started but health check failed${NC}"
    fi
else
    echo -e "${RED}❌ Failed to start Service Dashboard${NC}"
    echo -e "${YELLOW}📝 Check logs: tail -f /tmp/service_dashboard.log${NC}"
    exit 1
fi