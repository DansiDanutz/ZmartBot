#!/bin/bash
# Start Enhanced MDC Monitor for Optimal Context Optimization

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Enhanced MDC Monitor for Optimal Context Optimization...${NC}"

# Change to project directory
cd /Users/dansidanutz/Desktop/ZmartBot

# Check if enhanced monitor script exists
if [ ! -f "zmart-api/enhanced_mdc_monitor.py" ]; then
    echo -e "${RED}❌ Enhanced MDC Monitor script not found!${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi

# Kill any existing enhanced monitor processes
echo -e "${YELLOW}🔄 Stopping any existing enhanced monitors...${NC}"
pkill -f enhanced_mdc_monitor.py

# Wait a moment for processes to stop
sleep 2

# Start the enhanced monitor with optimal settings
echo -e "${GREEN}✅ Starting Enhanced MDC Monitor with optimal settings...${NC}"
nohup python3 zmart-api/enhanced_mdc_monitor.py --start --batch-interval 30 --update-threshold 5 > zmart-api/enhanced_mdc_monitor.log 2>&1 &

# Get the process ID
MONITOR_PID=$!

# Save PID to file for easy management
echo $MONITOR_PID > zmart-api/enhanced_mdc_monitor.pid

echo -e "${GREEN}✅ Enhanced MDC Monitor started with PID: $MONITOR_PID${NC}"
echo -e "${BLUE}📝 Log file: zmart-api/enhanced_mdc_monitor.log${NC}"
echo -e "${BLUE}🔄 Real-time monitoring with 30s batch intervals...${NC}"
echo -e "${YELLOW}💡 To stop the monitor: ./stop_enhanced_mdc_monitor.sh${NC}"

# Show initial status
echo -e "${BLUE}📋 Monitor Status:${NC}"
sleep 3
python3 zmart-api/enhanced_mdc_monitor.py --status 2>/dev/null || echo "Status check failed..."

echo -e "${GREEN}🎯 Enhanced MDC Monitor is now running optimally!${NC}"
