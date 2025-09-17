#!/bin/bash
# ZmartBot Passport Service Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZMARTBOT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
SERVICE_PORT=8620
SERVICE_NAME="passport-service"
PID_FILE="$ZMARTBOT_ROOT/logs/passport-service.pid"

echo -e "${BLUE}🛂 Starting ZmartBot Passport Service...${NC}"

# Create logs directory
mkdir -p "$ZMARTBOT_ROOT/logs"
mkdir -p "$ZMARTBOT_ROOT/data"

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Passport Service is already running (PID: $PID)${NC}"
        echo -e "${BLUE}🌐 Service URL: http://localhost:$SERVICE_PORT${NC}"
        echo -e "${BLUE}📚 API Docs: http://localhost:$SERVICE_PORT/docs${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️ Removing stale PID file${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Check if port is available
if lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t > /dev/null 2>&1; then
    echo -e "${RED}❌ Port $SERVICE_PORT is already in use${NC}"
    echo -e "${YELLOW}🔍 Checking what's using the port:${NC}"
    lsof -Pi :$SERVICE_PORT -sTCP:LISTEN
    exit 1
fi

# Install dependencies if needed
if [ ! -f "$SCRIPT_DIR/requirements_installed.flag" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    touch "$SCRIPT_DIR/requirements_installed.flag"
fi

# Set environment variables
export PASSPORT_SECRET_KEY="zmartbot-passport-key-$(date +%s)"
export PASSPORT_DB_URL="sqlite:///$ZMARTBOT_ROOT/data/passport_registry.db"

# Start the service
cd "$SCRIPT_DIR"
echo -e "${GREEN}🚀 Starting Passport Service on port $SERVICE_PORT...${NC}"

python3 passport_service.py \
    --host 0.0.0.0 \
    --port $SERVICE_PORT \
    > "$ZMARTBOT_ROOT/logs/passport-service.log" 2>&1 &

SERVICE_PID=$!
echo $SERVICE_PID > "$PID_FILE"

# Wait a moment for service to start
sleep 3

# Check if service started successfully
if ps -p "$SERVICE_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Passport Service started successfully!${NC}"
    echo -e "${BLUE}🔗 Service Details:${NC}"
    echo -e "   PID: $SERVICE_PID"
    echo -e "   Port: $SERVICE_PORT"
    echo -e "   URL: http://localhost:$SERVICE_PORT"
    echo -e "   Health: http://localhost:$SERVICE_PORT/health"
    echo -e "   API Docs: http://localhost:$SERVICE_PORT/docs"
    echo -e "   Logs: $ZMARTBOT_ROOT/logs/passport-service.log"
    
    # Test health endpoint
    echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
    if curl -f -s "http://localhost:$SERVICE_PORT/health" > /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️ Health check failed, but service is running${NC}"
    fi
    
else
    echo -e "${RED}❌ Failed to start Passport Service${NC}"
    echo -e "${YELLOW}📋 Check logs: $ZMARTBOT_ROOT/logs/passport-service.log${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}🛂 Passport Service is ready for service registrations!${NC}"