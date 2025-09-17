#!/bin/bash

# ZmartBot Service Fixer
# Automatically detects and fixes service issues

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🔧 ZmartBot Service Fixer${NC}"
echo "=========================="

# Function to check if service is running
check_service_running() {
    local port=$1
    lsof -i :$port >/dev/null 2>&1
}

# Function to restart dashboard service
restart_dashboard() {
    echo -e "${YELLOW}🔄 Restarting Service Dashboard...${NC}"
    
    # Kill old server
    pkill -f "server.py"
    pkill -f "api_server.py"
    sleep 2
    
    # Start new API server
    cd dashboard/Service-Dashboard
    nohup python3 api_server.py --port 3401 > /tmp/service_dashboard.log 2>&1 &
    cd ../..
    
    sleep 3
    
    if check_service_running 3401; then
        echo -e "${GREEN}✅ Service Dashboard restarted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to restart Service Dashboard${NC}"
    fi
}

# Function to run health check
run_health_check() {
    echo -e "${BLUE}🏥 Running comprehensive health check...${NC}"
    python3 service_health_check.py
    return $?
}

# Function to fix common issues
fix_common_issues() {
    echo -e "${YELLOW}🔧 Checking for common issues...${NC}"
    
    # Check if FastAPI dependencies are installed
    if ! python3 -c "import fastapi, uvicorn, httpx, psutil" >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Installing missing dependencies...${NC}"
        python3 -m pip install fastapi uvicorn httpx psutil --quiet
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
    
    # Check port conflicts
    echo -e "${BLUE}🔍 Checking port conflicts...${NC}"
    
    # Key ports that should be running
    key_ports=(3401 8000 8002)
    for port in "${key_ports[@]}"; do
        if check_service_running $port; then
            echo -e "${GREEN}✅ Port $port is active${NC}"
        else
            echo -e "${YELLOW}⚠️  Port $port is not active${NC}"
            if [ "$port" = "3401" ]; then
                restart_dashboard
            fi
        fi
    done
}

# Function to show service URLs
show_service_urls() {
    echo -e "${PURPLE}🌐 Service URLs:${NC}"
    echo "  Dashboard: http://localhost:3401"
    echo "  Health API: http://localhost:3401/health"
    echo "  Services API: http://localhost:3401/api/services/status"
    echo "  System Stats: http://localhost:3401/api/system/stats"
    echo "  Main API: http://localhost:8000 (if running)"
    echo "  Orchestration: http://localhost:8002 (if running)"
}

# Main execution
main() {
    case "${1:-check}" in
        "check")
            run_health_check
            ;;
        "fix")
            fix_common_issues
            echo ""
            run_health_check
            ;;
        "dashboard")
            restart_dashboard
            ;;
        "urls")
            show_service_urls
            ;;
        "all")
            fix_common_issues
            restart_dashboard
            echo ""
            run_health_check
            echo ""
            show_service_urls
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  check      Run health check only (default)"
            echo "  fix        Fix common issues and run health check"
            echo "  dashboard  Restart service dashboard only"
            echo "  urls       Show service URLs"
            echo "  all        Fix everything and show status"
            echo "  help       Show this help message"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"