#!/bin/bash
# ZmartBot Service Dashboard Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

ZMARTBOT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
DASHBOARD_DIR="$ZMARTBOT_ROOT/zmart-api/dashboard/Service-Dashboard"
DASHBOARD_PORT=3401

echo -e "${PURPLE}🛠️  ZmartBot Service Dashboard${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Check if dashboard directory exists
if [ ! -d "$DASHBOARD_DIR" ]; then
    echo -e "${RED}❌ Dashboard directory not found: $DASHBOARD_DIR${NC}"
    exit 1
fi

# Check if required files exist
REQUIRED_FILES=("index.html" "styles.css" "script.js" "server.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$DASHBOARD_DIR/$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        exit 1
    fi
done

# Check if Passport Service is running
echo -e "${BLUE}🔍 Checking Passport Service...${NC}"
if curl -s "http://localhost:8620/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Passport Service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Passport Service not detected on port 8620${NC}"
    echo -e "${YELLOW}💡 Start it with: ./services/passport-service/start_passport_service.sh${NC}"
fi

# Check if port is available
if lsof -Pi :$DASHBOARD_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $DASHBOARD_PORT is already in use${NC}"
    echo -e "${YELLOW}🔍 Process using port $DASHBOARD_PORT:${NC}"
    lsof -Pi :$DASHBOARD_PORT -sTCP:LISTEN
    exit 1
fi

echo -e "${BLUE}🚀 Starting Service Dashboard...${NC}"

# Change to dashboard directory
cd "$DASHBOARD_DIR"

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Start the dashboard server
echo -e "${GREEN}🌐 Service Dashboard starting on port $DASHBOARD_PORT...${NC}"
echo -e "${BLUE}📊 Dashboard URL: http://localhost:$DASHBOARD_PORT${NC}"
echo -e "${BLUE}🛂 Passport Service: http://localhost:8620${NC}"
echo -e "${BLUE}🎛️  Master Orchestration: http://localhost:8002${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Access your Service Dashboard at: ${YELLOW}http://localhost:$DASHBOARD_PORT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🔄 Server running... (Press Ctrl+C to stop)${NC}"

# Start server with auto-browser opening
python3 server.py --port $DASHBOARD_PORT --host localhost

echo -e "${GREEN}🛑 Service Dashboard stopped${NC}"