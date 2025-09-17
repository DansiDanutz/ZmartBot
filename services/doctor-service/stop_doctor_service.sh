#!/bin/bash
# Doctor Service - AI-Powered System Diagnostics Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

DOCTOR_SERVICE_PORT=8700

echo -e "${PURPLE}🩺 Stopping Doctor Service${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Check if Doctor Service is running
if ! lsof -Pi :$DOCTOR_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Doctor Service is not running on port $DOCTOR_SERVICE_PORT${NC}"
    exit 0
fi

echo -e "${BLUE}🔍 Finding Doctor Service process...${NC}"

# Find the process ID
DOCTOR_PID=$(lsof -t -i:$DOCTOR_SERVICE_PORT)

if [ -z "$DOCTOR_PID" ]; then
    echo -e "${YELLOW}⚠️  No process found on port $DOCTOR_SERVICE_PORT${NC}"
    exit 0
fi

echo -e "${BLUE}📋 Doctor Service process ID: $DOCTOR_PID${NC}"

# Get process details
echo -e "${BLUE}🔍 Process details:${NC}"
ps -p $DOCTOR_PID -o pid,ppid,cmd

# Graceful shutdown first
echo -e "${BLUE}🔄 Attempting graceful shutdown...${NC}"
kill -TERM $DOCTOR_PID

# Wait for graceful shutdown
WAIT_TIME=0
MAX_WAIT=10

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if ! ps -p $DOCTOR_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Doctor Service stopped gracefully${NC}"
        break
    fi
    sleep 1
    WAIT_TIME=$((WAIT_TIME + 1))
    echo -e "${YELLOW}⏳ Waiting for graceful shutdown... ($WAIT_TIME/${MAX_WAIT})${NC}"
done

# Force kill if still running
if ps -p $DOCTOR_PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Graceful shutdown timeout, forcing termination...${NC}"
    kill -KILL $DOCTOR_PID
    sleep 2
    
    if ps -p $DOCTOR_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ Failed to stop Doctor Service${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Doctor Service terminated${NC}"
    fi
fi

# Verify port is free
if lsof -Pi :$DOCTOR_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $DOCTOR_SERVICE_PORT is still in use${NC}"
    echo -e "${YELLOW}🔍 Processes still using port:${NC}"
    lsof -Pi :$DOCTOR_SERVICE_PORT -sTCP:LISTEN
    exit 1
fi

echo -e "${GREEN}✅ Port $DOCTOR_SERVICE_PORT is now free${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🛑 Doctor Service stopped successfully${NC}"

# Cleanup any remaining background tasks
echo -e "${BLUE}🧹 Cleaning up background tasks...${NC}"
pkill -f "doctor_service.py" 2>/dev/null || true

echo -e "${GREEN}✨ Doctor Service cleanup complete${NC}"