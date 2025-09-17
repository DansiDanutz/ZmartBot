#!/bin/bash
# Stop Enhanced MDC Monitor

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Enhanced MDC Monitor...${NC}"

# Change to project directory
cd /Users/dansidanutz/Desktop/ZmartBot

# Find and kill enhanced MDC monitor processes
echo -e "${YELLOW}🔍 Finding Enhanced MDC Monitor processes...${NC}"

# Kill processes by name
pkill -f "enhanced_mdc_monitor.py" 2>/dev/null

# Check if any processes are still running
sleep 2
if pgrep -f "enhanced_mdc_monitor.py" > /dev/null; then
    echo -e "${YELLOW}⚠️ Some processes still running, force killing...${NC}"
    pkill -9 -f "enhanced_mdc_monitor.py" 2>/dev/null
    sleep 1
fi

# Final check
if pgrep -f "enhanced_mdc_monitor.py" > /dev/null; then
    echo -e "${RED}❌ Failed to stop Enhanced MDC Monitor${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Enhanced MDC Monitor stopped successfully${NC}"
fi

# Show final status
echo -e "${BLUE}📋 Final Status:${NC}"
python3 zmart-api/enhanced_mdc_monitor.py --status 2>/dev/null || echo "Monitor not running"

echo -e "${GREEN}🎯 Enhanced MDC Monitor stopped!${NC}"
