#!/bin/bash
# ZmartBot Passport Service Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ZMARTBOT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
SERVICE_PORT=8620
SERVICE_NAME="passport-service"
PID_FILE="$ZMARTBOT_ROOT/logs/passport-service.pid"

echo -e "${BLUE}🛂 Stopping ZmartBot Passport Service...${NC}"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️ PID file not found. Checking for running processes...${NC}"
    
    # Check if any passport service process is running
    RUNNING_PIDS=$(pgrep -f "passport_service.py" || true)
    if [ -n "$RUNNING_PIDS" ]; then
        echo -e "${YELLOW}🔍 Found running Passport Service processes: $RUNNING_PIDS${NC}"
        echo -e "${BLUE}🛑 Terminating processes...${NC}"
        pkill -f "passport_service.py"
        sleep 2
        
        # Force kill if still running
        STILL_RUNNING=$(pgrep -f "passport_service.py" || true)
        if [ -n "$STILL_RUNNING" ]; then
            echo -e "${YELLOW}💀 Force killing remaining processes...${NC}"
            pkill -9 -f "passport_service.py"
        fi
        
        echo -e "${GREEN}✅ Passport Service stopped${NC}"
    else
        echo -e "${GREEN}✅ No Passport Service processes found${NC}"
    fi
    exit 0
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Process with PID $PID is not running${NC}"
    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ Cleaned up PID file${NC}"
    exit 0
fi

echo -e "${BLUE}🛑 Stopping Passport Service (PID: $PID)...${NC}"

# Graceful shutdown
kill -TERM "$PID"

# Wait for graceful shutdown
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Passport Service stopped gracefully${NC}"
        rm -f "$PID_FILE"
        break
    fi
    echo -e "${YELLOW}⏳ Waiting for graceful shutdown... ($i/10)${NC}"
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}💀 Force killing Passport Service...${NC}"
    kill -9 "$PID"
    sleep 1
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${RED}❌ Failed to stop Passport Service${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Passport Service force stopped${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Check if port is still in use
if lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Port $SERVICE_PORT is still in use. Finding and killing processes...${NC}"
    PIDS_USING_PORT=$(lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t)
    echo -e "${BLUE}🔍 PIDs using port $SERVICE_PORT: $PIDS_USING_PORT${NC}"
    
    for pid in $PIDS_USING_PORT; do
        echo -e "${YELLOW}🛑 Killing process $pid...${NC}"
        kill -9 "$pid" 2>/dev/null || true
    done
fi

echo -e "${GREEN}🛂 Passport Service stopped successfully${NC}"