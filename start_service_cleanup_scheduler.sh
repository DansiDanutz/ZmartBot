#!/bin/bash

# Service Cleanup Scheduler
# Runs the service cleanup system every hour

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Starting Service Cleanup Scheduler...${NC}"

# Change to project directory
cd /Users/dansidanutz/Desktop/ZmartBot

# Check if Python script exists
if [ ! -f "zmart-api/service_cleanup_system.py" ]; then
    echo -e "${RED}❌ Service cleanup system not found!${NC}"
    exit 1
fi

# Check if schedule module is installed
python3 -c "import schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📦 Installing schedule module...${NC}"
    pip3 install schedule
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the cleanup scheduler
echo -e "${GREEN}✅ Starting service cleanup scheduler...${NC}"
echo -e "${BLUE}📋 Cleanup will run every hour${NC}"
echo -e "${BLUE}📋 Logs will be saved to: logs/service_cleanup.log${NC}"
echo -e "${BLUE}📋 Backups will be saved to: system_backups/cleanup_backup_*/${NC}"
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop the scheduler${NC}"

# Run the cleanup system with scheduling
python3 zmart-api/service_cleanup_system.py
