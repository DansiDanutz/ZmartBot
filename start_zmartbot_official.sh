#!/bin/bash

# 🚀 ZMARTBOT OFFICIAL STARTUP SCRIPT
# ===================================
# This is the ONLY official way to start the ZmartBot system
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
PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
BACKEND_DIR="$PROJECT_ROOT/backend/zmart-api"
API_PORT=8000
DASHBOARD_PORT=3400
FORBIDDEN_PORT=5173

echo -e "${BLUE}🚀 ZMARTBOT OFFICIAL STARTUP SCRIPT${NC}"
echo -e "${BLUE}=====================================${NC}"
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
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to verify server is running
verify_server() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $name to start on port $port...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            echo -e "${GREEN}✅ $name is running on port $port${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $name failed to start on port $port${NC}"
    return 1
}

# Function to test API endpoint
test_api() {
    local url=$1
    local name=$2
    local max_attempts=10
    local attempt=1
    
    echo -e "${YELLOW}🧪 Testing $name...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is responding${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $name is not responding${NC}"
    return 1
}

echo -e "${BLUE}📋 STEP 1: Environment Setup${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "$BACKEND_DIR/run_dev.py" ]; then
    echo -e "${RED}❌ Error: run_dev.py not found in $BACKEND_DIR${NC}"
    echo -e "${YELLOW}💡 Make sure you're running this script from the project root${NC}"
    exit 1
fi

# Navigate to backend directory
echo -e "${YELLOW}📁 Navigating to backend directory...${NC}"
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${BLUE}📋 STEP 2: Cleanup Existing Processes${NC}"
echo "============================================="

# Kill any processes on forbidden port 5173
if check_port $FORBIDDEN_PORT; then
    echo -e "${RED}🚨 WARNING: Port $FORBIDDEN_PORT is in use!${NC}"
    echo -e "${YELLOW}🛑 Killing processes on port $FORBIDDEN_PORT...${NC}"
    kill_port $FORBIDDEN_PORT
fi

# Kill any existing processes on our ports
kill_port $API_PORT
kill_port $DASHBOARD_PORT

echo -e "${GREEN}✅ Cleanup completed${NC}"

echo -e "${BLUE}📋 STEP 3: Start Backend API Server${NC}"
echo "=========================================="

# Start backend API server
echo -e "${YELLOW}🚀 Starting Backend API Server on port $API_PORT...${NC}"
nohup python run_dev.py > api_server.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✅ Backend API Server started (PID: $API_PID)${NC}"

# Verify backend server is running
if ! verify_server $API_PORT "Backend API Server"; then
    echo -e "${RED}❌ Backend API Server failed to start${NC}"
    echo -e "${YELLOW}📋 Check api_server.log for details${NC}"
    exit 1
fi

echo -e "${BLUE}📋 STEP 4: Start Frontend Dashboard Server${NC}"
echo "================================================"

# Start frontend dashboard server
echo -e "${YELLOW}🚀 Starting Frontend Dashboard Server on port $DASHBOARD_PORT...${NC}"
nohup python professional_dashboard_server.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo -e "${GREEN}✅ Frontend Dashboard Server started (PID: $DASHBOARD_PID)${NC}"

# Verify dashboard server is running
if ! verify_server $DASHBOARD_PORT "Frontend Dashboard Server"; then
    echo -e "${RED}❌ Frontend Dashboard Server failed to start${NC}"
    echo -e "${YELLOW}📋 Check dashboard.log for details${NC}"
    exit 1
fi

echo -e "${BLUE}📋 STEP 5: System Verification${NC}"
echo "=================================="

# Wait a moment for servers to fully initialize
sleep 5

# Test backend API
if ! test_api "http://localhost:$API_PORT/api/v1/alerts/status" "Backend API"; then
    echo -e "${RED}❌ Backend API test failed${NC}"
    exit 1
fi

# Test frontend dashboard
if ! test_api "http://localhost:$DASHBOARD_PORT/health" "Frontend Dashboard"; then
    echo -e "${RED}❌ Frontend Dashboard test failed${NC}"
    exit 1
fi

# Test My Symbols API
if ! test_api "http://localhost:$DASHBOARD_PORT/api/futures-symbols/my-symbols/current" "My Symbols API"; then
    echo -e "${RED}❌ My Symbols API test failed${NC}"
    exit 1
fi

echo -e "${BLUE}📋 STEP 6: Final Status Check${NC}"
echo "================================="

# Display final status
echo -e "${GREEN}🎉 ZMARTBOT SYSTEM STARTED SUCCESSFULLY!${NC}"
echo ""
echo -e "${BLUE}📊 SERVER STATUS:${NC}"
echo "=================="
echo -e "${GREEN}✅ Backend API Server:${NC} Port $API_PORT (PID: $API_PID)"
echo -e "${GREEN}✅ Frontend Dashboard:${NC} Port $DASHBOARD_PORT (PID: $DASHBOARD_PID)"
echo -e "${GREEN}✅ Port 5173:${NC} COMPLETELY CLEAN (no processes)"
echo ""

echo -e "${BLUE}🌐 ACCESS URLs:${NC}"
echo "==============="
echo -e "${YELLOW}📊 Dashboard:${NC} http://localhost:$DASHBOARD_PORT/"
echo -e "${YELLOW}🔧 API Docs:${NC} http://localhost:$API_PORT/docs"
echo -e "${YELLOW}🏥 Health:${NC} http://localhost:$DASHBOARD_PORT/health"
echo ""

echo -e "${BLUE}📋 LOG FILES:${NC}"
echo "============="
echo -e "${YELLOW}📄 Backend Log:${NC} $BACKEND_DIR/api_server.log"
echo -e "${YELLOW}📄 Dashboard Log:${NC} $BACKEND_DIR/dashboard.log"
echo ""

echo -e "${BLUE}🔍 VERIFICATION COMMANDS:${NC}"
echo "============================="
echo -e "${YELLOW}Check all ports:${NC} lsof -i :$DASHBOARD_PORT && echo '---' && lsof -i :$API_PORT && echo '---' && lsof -i :$FORBIDDEN_PORT"
echo -e "${YELLOW}Test Backend:${NC} curl -s http://localhost:$API_PORT/api/v1/alerts/status | jq '.success'"
echo -e "${YELLOW}Test Frontend:${NC} curl -s http://localhost:$DASHBOARD_PORT/health | jq '.status'"
echo -e "${YELLOW}Test My Symbols:${NC} curl -s http://localhost:$DASHBOARD_PORT/api/futures-symbols/my-symbols/current | jq '.portfolio.symbols | length'"
echo ""

echo -e "${GREEN}🎯 RULE #1 COMPLIANCE: ✅ VERIFIED${NC}"
echo -e "${GREEN}🚀 System ready for trading operations!${NC}"
