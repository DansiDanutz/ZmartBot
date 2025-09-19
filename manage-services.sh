#!/bin/bash

# ZmartBot Service Manager - Keep Everything Organized!

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎯 ZmartBot Service Manager${NC}"
echo "================================"

case "$1" in
    status)
        echo -e "${YELLOW}📊 Checking all services...${NC}"
        echo ""
        echo "Port 3000 (ZmartyChat Main):"
        lsof -i :3000 2>/dev/null || echo "  ✅ Available"
        echo ""
        echo "Port 3001 (ZmartyChat Mobile):"
        lsof -i :3001 2>/dev/null || echo "  ✅ Available"
        echo ""
        echo "Port 3002 (ZmartBot Mobile):"
        lsof -i :3002 2>/dev/null || echo "  ✅ Available"
        echo ""
        echo "Port 8080 (Web Dashboard):"
        lsof -i :8080 2>/dev/null || echo "  ✅ Available"
        echo ""
        echo "Port 8081 (Admin Dashboard):"
        lsof -i :8081 2>/dev/null || echo "  ✅ Available"
        ;;

    stop-all)
        echo -e "${RED}🛑 Stopping all services...${NC}"
        pkill -f "node" 2>/dev/null
        pkill -f "python3 -m http.server" 2>/dev/null
        pkill -f "webpack" 2>/dev/null
        pkill -f "npm" 2>/dev/null
        echo "✅ All services stopped"
        ;;

    start-dashboard)
        echo -e "${GREEN}🚀 Starting Web Dashboard on port 8080...${NC}"
        # Kill anything on 8080 first
        kill -9 $(lsof -t -i:8080) 2>/dev/null
        cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/web-app
        python3 -m http.server 8080 &
        echo "✅ Dashboard running at http://localhost:8080/dashboard.html"
        ;;

    start-mobile)
        echo -e "${GREEN}🚀 Starting Mobile App on port 3002...${NC}"
        # Kill anything on 3002 first
        kill -9 $(lsof -t -i:3002) 2>/dev/null
        cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat/mobile-app
        npm start &
        echo "✅ Mobile app running at http://localhost:3002"
        ;;

    clean-start)
        echo -e "${YELLOW}🧹 Clean start - stopping everything first...${NC}"
        $0 stop-all
        sleep 2
        echo ""
        echo -e "${GREEN}🚀 Starting fresh services...${NC}"
        $0 start-dashboard
        sleep 2
        $0 start-mobile
        echo ""
        echo -e "${GREEN}✅ All services started cleanly!${NC}"
        $0 status
        ;;

    *)
        echo "Usage: $0 {status|stop-all|start-dashboard|start-mobile|clean-start}"
        echo ""
        echo "Commands:"
        echo "  status         - Check all service ports"
        echo "  stop-all       - Stop all running services"
        echo "  start-dashboard - Start web dashboard (port 8080)"
        echo "  start-mobile   - Start mobile app (port 3002)"
        echo "  clean-start    - Stop all, then start fresh"
        ;;
esac