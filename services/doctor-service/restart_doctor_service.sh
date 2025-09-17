#!/bin/bash
# Doctor Service - AI-Powered System Diagnostics Restart Script

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

echo -e "${PURPLE}🔄 Restarting Doctor Service${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Change to doctor service directory
cd "$DOCTOR_SERVICE_DIR"

# Check if scripts exist
if [ ! -f "stop_doctor_service.sh" ]; then
    echo -e "${RED}❌ Stop script not found: stop_doctor_service.sh${NC}"
    exit 1
fi

if [ ! -f "start_doctor_service.sh" ]; then
    echo -e "${RED}❌ Start script not found: start_doctor_service.sh${NC}"
    exit 1
fi

# Make scripts executable
chmod +x stop_doctor_service.sh
chmod +x start_doctor_service.sh

echo -e "${BLUE}🛑 Stopping Doctor Service...${NC}"
./stop_doctor_service.sh

# Wait a moment for cleanup
sleep 2

echo -e "${BLUE}🚀 Starting Doctor Service...${NC}"
./start_doctor_service.sh