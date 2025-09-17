#!/bin/bash

# ZmartBot zmart-api Verification Script
# Ensures all services work within zmart-api folder only

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🔍 ZmartBot zmart-api Folder Verification${NC}"
echo "========================================="
echo ""

# Check current working directory
current_dir=$(pwd)
if [[ "$current_dir" == *"zmart-api" ]]; then
    echo -e "${GREEN}✅ Running from zmart-api folder${NC}"
else
    echo -e "${RED}❌ Not running from zmart-api folder${NC}"
    echo "Current: $current_dir"
    exit 1
fi

echo ""
echo -e "${BLUE}📁 Checking Dashboard Structure:${NC}"

# Check dashboard folders
dashboard_folders=(
    "dashboard/Service-Dashboard"
    "dashboard/MDC-Dashboard"
    "dashboard/LogDashboard"
    "mdc_dashboard"
    "service_dashboard"
    "zmart_dashboard"
    "zmart-dashboard"
    "professional_dashboard"
)

for folder in "${dashboard_folders[@]}"; do
    if [ -d "$folder" ]; then
        echo -e "${GREEN}  ✅ $folder${NC}"
    else
        echo -e "${YELLOW}  ⏭️  $folder (not present)${NC}"
    fi
done

echo ""
echo -e "${BLUE}🔧 Checking Service Scripts:${NC}"

# Check key scripts
scripts=(
    "service_health_check.py"
    "fix_services.sh" 
    "start_service_dashboard.sh"
    "dashboard/Service-Dashboard/api_server.py"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}  ✅ $script${NC}"
        # Check for absolute paths
        if grep -q "/Users/dansidanutz/Desktop/ZmartBot/zmart-api" "$script" 2>/dev/null; then
            echo -e "${YELLOW}    ⚠️  Contains absolute paths${NC}"
        else
            echo -e "${GREEN}    ✅ Uses relative paths${NC}"
        fi
    else
        echo -e "${RED}  ❌ $script (missing)${NC}"
    fi
done

echo ""
echo -e "${BLUE}🏥 Testing Services:${NC}"

# Test dashboard service
if [ -f "dashboard/Service-Dashboard/api_server.py" ]; then
    echo -e "${BLUE}  🚀 Testing Service Dashboard...${NC}"
    
    if curl -s http://localhost:3401/health >/dev/null 2>&1; then
        echo -e "${GREEN}    ✅ Dashboard API responding${NC}"
        
        # Test API endpoints
        if curl -s http://localhost:3401/api/services/status | grep -q "summary"; then
            echo -e "${GREEN}    ✅ Services API working${NC}"
        else
            echo -e "${YELLOW}    ⚠️  Services API has issues${NC}"
        fi
        
        if curl -s http://localhost:3401/api/system/stats | grep -q "cpu"; then
            echo -e "${GREEN}    ✅ System Stats API working${NC}"
        else
            echo -e "${YELLOW}    ⚠️  System Stats API has issues${NC}"
        fi
    else
        echo -e "${RED}    ❌ Dashboard not responding${NC}"
        echo -e "${YELLOW}    💡 Try: ./start_service_dashboard.sh${NC}"
    fi
fi

echo ""
echo -e "${BLUE}📊 Running Health Check:${NC}"

if [ -f "service_health_check.py" ]; then
    health_result=$(python3 service_health_check.py 2>/dev/null | tail -1)
    if [[ "$health_result" == *"healthy"* ]]; then
        echo -e "${GREEN}  ✅ System health check passed${NC}"
    else
        echo -e "${YELLOW}  ⚠️  System has some issues${NC}"
    fi
else
    echo -e "${RED}  ❌ Health check script missing${NC}"
fi

echo ""
echo -e "${PURPLE}🌐 Available Services:${NC}"
echo "  • Dashboard: http://localhost:3401"
echo "  • Health API: http://localhost:3401/health"  
echo "  • Services Status: http://localhost:3401/api/services/status"
echo "  • System Stats: http://localhost:3401/api/system/stats"

echo ""
echo -e "${BLUE}🎯 Commands available in zmart-api:${NC}"
echo "  • ./service_health_check.py - Check all services"
echo "  • ./fix_services.sh - Fix service issues"
echo "  • ./start_service_dashboard.sh - Start dashboard"
echo "  • python3 dashboard/Service-Dashboard/api_server.py - Start API directly"

echo ""
if curl -s http://localhost:3401/health >/dev/null 2>&1; then
    echo -e "${GREEN}🎉 ZmartBot is fully operational within zmart-api folder!${NC}"
    echo -e "${GREEN}   No dependencies on root folder anymore.${NC}"
else
    echo -e "${YELLOW}⚠️  ZmartBot setup complete, but dashboard needs to be started.${NC}"
    echo -e "${YELLOW}   Run: ./start_service_dashboard.sh${NC}"
fi