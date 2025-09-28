#!/bin/bash

# Start API Keys Manager and MCP Integration
# ZmartBot Platform - Unified API Management

echo "🚀 Starting ZmartBot API Manager & MCP Integration"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
API_DIR="$PROJECT_ROOT/zmart-api"

# Check if API Keys Manager is running
check_api_manager() {
    if curl -s http://localhost:8006/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Start API Keys Manager
start_api_manager() {
    echo -e "${YELLOW}Starting API Keys Manager...${NC}"

    cd "$API_DIR"
    python3 api_keys_manager/api_keys_manager_server.py --port 8006 &
    API_PID=$!

    # Wait for service to start
    sleep 3

    if check_api_manager; then
        echo -e "${GREEN}✅ API Keys Manager started (PID: $API_PID)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to start API Keys Manager${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo "1️⃣  Checking API Keys Manager status..."

    if check_api_manager; then
        echo -e "${GREEN}✅ API Keys Manager is already running${NC}"
    else
        echo -e "${YELLOW}⚠️  API Keys Manager not running${NC}"
        start_api_manager
    fi

    echo ""
    echo "2️⃣  Starting MCP Integration Interface..."
    echo ""

    # Run the integration script
    cd "$API_DIR"
    python3 mcp_api_integration.py
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    pkill -f "api_keys_manager_server.py"
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Set trap for cleanup on exit
trap cleanup EXIT

# Run main function
main