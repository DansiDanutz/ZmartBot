#!/bin/bash
# Doctor Service - AI-Powered System Diagnostics Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

ZMARTBOT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
DOCTOR_SERVICE_DIR="$ZMARTBOT_ROOT/services/doctor-service"
DOCTOR_SERVICE_PORT=8700
DOCTOR_SERVICE_HOST="0.0.0.0"

echo -e "${PURPLE}🩺 Doctor Service - AI-Powered Diagnostics${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Check if doctor service directory exists
if [ ! -d "$DOCTOR_SERVICE_DIR" ]; then
    echo -e "${RED}❌ Doctor Service directory not found: $DOCTOR_SERVICE_DIR${NC}"
    exit 1
fi

# Change to doctor service directory
cd "$DOCTOR_SERVICE_DIR"

# Check if required files exist
REQUIRED_FILES=("doctor_service.py" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        exit 1
    fi
done

# Check if port is available
if lsof -Pi :$DOCTOR_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $DOCTOR_SERVICE_PORT is already in use${NC}"
    echo -e "${YELLOW}🔍 Process using port $DOCTOR_SERVICE_PORT:${NC}"
    lsof -Pi :$DOCTOR_SERVICE_PORT -sTCP:LISTEN
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing minimal dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements-minimal.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OpenAI API key not found in environment${NC}"
    echo -e "${YELLOW}💡 Set it with: export OPENAI_API_KEY=your-api-key${NC}"
fi

# Check if Passport Service is running
echo -e "${BLUE}🔍 Checking Passport Service dependency...${NC}"
if curl -s "http://localhost:8620/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Passport Service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Passport Service not detected on port 8620${NC}"
    echo -e "${YELLOW}💡 Start it with: ./services/passport-service/start_passport_service.sh${NC}"
fi

# Check if Master Orchestration Agent is running
echo -e "${BLUE}🔍 Checking Master Orchestration dependency...${NC}"
if curl -s "http://localhost:8002/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Master Orchestration Agent is running${NC}"
else
    echo -e "${YELLOW}⚠️  Master Orchestration Agent not detected on port 8002${NC}"
    echo -e "${YELLOW}💡 Start it with: ./services/orchestration-agent/start_orchestration.sh${NC}"
fi

# Create data directory if it doesn't exist
DATA_DIR="$ZMARTBOT_ROOT/data"
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${BLUE}📁 Creating data directory...${NC}"
    mkdir -p "$DATA_DIR"
fi

# Set environment variables
export DOCTOR_SERVICE_PORT=$DOCTOR_SERVICE_PORT
export DOCTOR_SERVICE_TOKEN=${DOCTOR_SERVICE_TOKEN:-"doctor-service-token"}
export ORCHESTRATION_SERVICE_URL=${ORCHESTRATION_SERVICE_URL:-"http://localhost:8002"}
export PASSPORT_SERVICE_URL=${PASSPORT_SERVICE_URL:-"http://localhost:8620"}
export DATABASE_PATH=${DATABASE_PATH:-"$DATA_DIR/doctor_service.db"}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}
export MAX_CONCURRENT_DIAGNOSES=${MAX_CONCURRENT_DIAGNOSES:-5}
export AI_TIMEOUT_SECONDS=${AI_TIMEOUT_SECONDS:-60}
export ENABLE_AUTO_EXECUTION=${ENABLE_AUTO_EXECUTION:-false}

echo -e "${BLUE}🚀 Starting Doctor Service...${NC}"
echo -e "${GREEN}🌐 Doctor Service starting on port $DOCTOR_SERVICE_PORT...${NC}"
echo -e "${BLUE}🩺 Service URL: http://localhost:$DOCTOR_SERVICE_PORT${NC}"
echo -e "${BLUE}📋 Health Check: http://localhost:$DOCTOR_SERVICE_PORT/health${NC}"
echo -e "${BLUE}📊 API Docs: http://localhost:$DOCTOR_SERVICE_PORT/docs${NC}"
echo -e "${BLUE}🛂 Passport Service: http://localhost:8620${NC}"
echo -e "${BLUE}🎛️  Master Orchestration: http://localhost:8002${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Doctor Service ready for AI-powered diagnostics${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🔄 Server running... (Press Ctrl+C to stop)${NC}"

# Start the Doctor Service
python3 doctor_service.py --port $DOCTOR_SERVICE_PORT --host $DOCTOR_SERVICE_HOST

echo -e "${GREEN}🛑 Doctor Service stopped${NC}"