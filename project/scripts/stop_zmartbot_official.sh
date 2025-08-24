#!/bin/bash

# 🛑 ZMARTBOT OFFICIAL STOP SCRIPT
# ================================
# This is the ONLY official way to stop the ZmartBot system
# Follows Rule #1 from PROJECT_INVENTORY.md
# Last Updated: 2025-08-18

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DASHBOARD_PORT=3400
FORBIDDEN_PORT=5173

echo -e "${BLUE}🛑 ZMARTBOT OFFICIAL STOP SCRIPT${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${YELLOW}Following Rule #1 from PROJECT_INVENTORY.md${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    if check_port $port; then
        echo -e "${YELLOW}🛑 Stopping processes on port $port...${NC}"
        local pids=$(lsof -ti :$port)
        echo -e "${YELLOW}📋 Found PIDs: $pids${NC}"
        echo $pids | xargs kill -TERM 2>/dev/null || true
        sleep 3
        # Force kill if still running
        if check_port $port; then
            echo -e "${YELLOW}⚡ Force killing remaining processes...${NC}"
            lsof -ti :$port | xargs kill -9 2>/dev/null || true
            sleep 1
        fi
        if ! check_port $port; then
            echo -e "${GREEN}✅ Port $port is now free${NC}"
        else
            echo -e "${RED}❌ Failed to free port $port${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port $port is already free${NC}"
    fi
}

echo -e "${BLUE}📋 STEP 1: Check Current Status${NC}"
echo "=================================="

# Check current status
echo -e "${YELLOW}🔍 Checking current server status...${NC}"
echo ""

if check_port $API_PORT; then
    echo -e "${YELLOW}📊 Backend API Server:${NC} Running on port $API_PORT"
    lsof -i :$API_PORT
else
    echo -e "${GREEN}📊 Backend API Server:${NC} Not running"
fi

echo ""

if check_port $DASHBOARD_PORT; then
    echo -e "${YELLOW}📊 Frontend Dashboard:${NC} Running on port $DASHBOARD_PORT"
    lsof -i :$DASHBOARD_PORT
else
    echo -e "${GREEN}📊 Frontend Dashboard:${NC} Not running"
fi

echo ""

if check_port $FORBIDDEN_PORT; then
    echo -e "${RED}🚨 WARNING: Port $FORBIDDEN_PORT is in use!${NC}"
    lsof -i :$FORBIDDEN_PORT
else
    echo -e "${GREEN}📊 Port 5173:${NC} Clean (no processes)"
fi

echo ""

echo -e "${BLUE}📋 STEP 2: Graceful Shutdown${NC}"
echo "=================================="

# Stop frontend dashboard server first
echo -e "${YELLOW}🛑 Stopping Frontend Dashboard Server...${NC}"
kill_port $DASHBOARD_PORT

# Stop backend API server
echo -e "${YELLOW}🛑 Stopping Backend API Server...${NC}"
kill_port $API_PORT

# Ensure port 5173 is clean
echo -e "${YELLOW}🧹 Ensuring port 5173 is clean...${NC}"
kill_port $FORBIDDEN_PORT

echo -e "${BLUE}📋 STEP 3: Final Verification${NC}"
echo "=================================="

# Final status check
echo -e "${YELLOW}🔍 Final status verification...${NC}"
echo ""

if ! check_port $API_PORT && ! check_port $DASHBOARD_PORT && ! check_port $FORBIDDEN_PORT; then
    echo -e "${GREEN}🎉 ZMARTBOT SYSTEM STOPPED SUCCESSFULLY!${NC}"
    echo ""
    echo -e "${BLUE}📊 FINAL STATUS:${NC}"
    echo "=================="
    echo -e "${GREEN}✅ Backend API Server:${NC} Stopped"
    echo -e "${GREEN}✅ Frontend Dashboard:${NC} Stopped"
    echo -e "${GREEN}✅ Port 5173:${NC} Clean (no processes)"
    echo ""
    echo -e "${GREEN}🎯 RULE #1 COMPLIANCE: ✅ VERIFIED${NC}"
    echo -e "${GREEN}🛑 System shutdown complete!${NC}"
else
    echo -e "${RED}❌ Some processes may still be running${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Remaining processes:${NC}"
    lsof -i :$API_PORT 2>/dev/null || echo "Port $API_PORT: Clean"
    lsof -i :$DASHBOARD_PORT 2>/dev/null || echo "Port $DASHBOARD_PORT: Clean"
    lsof -i :$FORBIDDEN_PORT 2>/dev/null || echo "Port $FORBIDDEN_PORT: Clean"
    echo ""
    echo -e "${YELLOW}💡 If processes remain, you may need to force kill them manually${NC}"
fi
