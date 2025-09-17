#!/bin/bash

# ZmartBot Server Status Monitor
# Real-time status checking and health monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
DASHBOARD_PORT=3400
PID_DIR="server_pids"
HEALTH_CHECK_TIMEOUT=5

echo -e "${BLUE}🔍 ZmartBot Server Status Monitor${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to get process info on a port
get_port_process_info() {
    local port=$1
    if check_port $port; then
        lsof -i :$port | grep LISTEN | awk '{print $2, $1, $9}' | head -1
    else
        echo "FREE"
    fi
}

# Function to get process uptime
get_process_uptime() {
    local pid=$1
    if kill -0 $pid 2>/dev/null; then
        local start_time=$(ps -o lstart= -p $pid 2>/dev/null | xargs -I {} date -j -f "%a %b %d %H:%M:%S %Z %Y" "{}" +%s 2>/dev/null || echo 0)
        local current_time=$(date +%s)
        local uptime_seconds=$((current_time - start_time))
        
        if [ $uptime_seconds -gt 0 ]; then
            local days=$((uptime_seconds / 86400))
            local hours=$(((uptime_seconds % 86400) / 3600))
            local minutes=$(((uptime_seconds % 3600) / 60))
            
            if [ $days -gt 0 ]; then
                echo "${days}d ${hours}h ${minutes}m"
            elif [ $hours -gt 0 ]; then
                echo "${hours}h ${minutes}m"
            else
                echo "${minutes}m"
            fi
        else
            echo "Unknown"
        fi
    else
        echo "N/A"
    fi
}

# Function to check API health
check_api_health() {
    local response=$(curl -s --max-time $HEALTH_CHECK_TIMEOUT "http://localhost:$API_PORT/api/v1/alerts/status" 2>/dev/null)
    if [ $? -eq 0 ] && echo "$response" | jq -e '.success' >/dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to check dashboard health
check_dashboard_health() {
    if curl -s --max-time $HEALTH_CHECK_TIMEOUT "http://localhost:$DASHBOARD_PORT" >/dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to get API response time
get_api_response_time() {
    local start_time=$(date +%s%N)
    curl -s --max-time $HEALTH_CHECK_TIMEOUT "http://localhost:$API_PORT/api/v1/alerts/status" >/dev/null 2>&1
    local end_time=$(date +%s%N)
    local response_time=$(((end_time - start_time) / 1000000))  # Convert to milliseconds
    echo $response_time
}

# Function to get dashboard response time
get_dashboard_response_time() {
    local start_time=$(date +%s%N)
    curl -s --max-time $HEALTH_CHECK_TIMEOUT "http://localhost:$DASHBOARD_PORT" >/dev/null 2>&1
    local end_time=$(date +%s%N)
    local response_time=$(((end_time - start_time) / 1000000))  # Convert to milliseconds
    echo $response_time
}

# Function to check monitoring status
check_monitoring_status() {
    # Check if any monitoring services are running
    if lsof -i :8615 >/dev/null 2>&1 || lsof -i :8700 >/dev/null 2>&1 || lsof -i :8999 >/dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to display detailed status
display_detailed_status() {
    echo -e "${CYAN}📊 DETAILED SERVER STATUS${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    
    # API Server Status
    local api_info=$(get_port_process_info $API_PORT)
    if [ "$api_info" = "FREE" ]; then
        echo -e "${RED}❌ API Server (Port $API_PORT): Not running${NC}"
    else
        local api_pid=$(echo $api_info | awk '{print $1}')
        local api_uptime=$(get_process_uptime $api_pid)
        local api_healthy=$(check_api_health)
        local api_response_time=$(get_api_response_time)
        
        echo -e "${GREEN}✅ API Server (Port $API_PORT): Running${NC}"
        echo -e "${YELLOW}   Process: $api_info${NC}"
        echo -e "${YELLOW}   Uptime: $api_uptime${NC}"
        echo -e "${YELLOW}   Health: $([ "$api_healthy" = "true" ] && echo "✅ Healthy" || echo "❌ Unhealthy")${NC}"
        echo -e "${YELLOW}   Response Time: ${api_response_time}ms${NC}"
    fi
    
    echo ""
    
    # Dashboard Server Status
    local dashboard_info=$(get_port_process_info $DASHBOARD_PORT)
    if [ "$dashboard_info" = "FREE" ]; then
        echo -e "${RED}❌ Dashboard Server (Port $DASHBOARD_PORT): Not running${NC}"
    else
        local dashboard_pid=$(echo $dashboard_info | awk '{print $1}')
        local dashboard_uptime=$(get_process_uptime $dashboard_pid)
        local dashboard_healthy=$(check_dashboard_health)
        local dashboard_response_time=$(get_dashboard_response_time)
        
        echo -e "${GREEN}✅ Dashboard Server (Port $DASHBOARD_PORT): Running${NC}"
        echo -e "${YELLOW}   Process: $dashboard_info${NC}"
        echo -e "${YELLOW}   Uptime: $dashboard_uptime${NC}"
        echo -e "${YELLOW}   Health: $([ "$dashboard_healthy" = "true" ] && echo "✅ Healthy" || echo "❌ Unhealthy")${NC}"
        echo -e "${YELLOW}   Response Time: ${dashboard_response_time}ms${NC}"
    fi
    
    echo ""
    
    # Monitoring Status
    local monitoring_active=$(check_monitoring_status)
    echo -e "${PURPLE}🔍 Monitoring: $([ "$monitoring_active" = "true" ] && echo "✅ Active" || echo "❌ Inactive")${NC}"
    
    echo ""
}

# Function to display quick status
display_quick_status() {
    echo -e "${CYAN}📊 QUICK STATUS${NC}"
    echo -e "${CYAN}==============${NC}"
    echo ""
    
    # API Server
    if check_port $API_PORT; then
        local api_healthy=$(check_api_health)
        if [ "$api_healthy" = "true" ]; then
            echo -e "${GREEN}✅ API Server: Running & Healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  API Server: Running but Unhealthy${NC}"
        fi
    else
        echo -e "${RED}❌ API Server: Not Running${NC}"
    fi
    
    # Dashboard Server
    if check_port $DASHBOARD_PORT; then
        local dashboard_healthy=$(check_dashboard_health)
        if [ "$dashboard_healthy" = "true" ]; then
            echo -e "${GREEN}✅ Dashboard Server: Running & Healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  Dashboard Server: Running but Unhealthy${NC}"
        fi
    else
        echo -e "${RED}❌ Dashboard Server: Not Running${NC}"
    fi
    
    # Monitoring
    local monitoring_active=$(check_monitoring_status)
    if [ "$monitoring_active" = "true" ]; then
        echo -e "${GREEN}✅ Monitoring: Active${NC}"
    else
        echo -e "${RED}❌ Monitoring: Inactive${NC}"
    fi
    
    echo ""
}

# Function to display system resources
display_system_resources() {
    echo -e "${CYAN}💻 SYSTEM RESOURCES${NC}"
    echo -e "${CYAN}==================${NC}"
    echo ""
    
    # CPU Usage
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    echo -e "${YELLOW}CPU Usage: ${cpu_usage}%${NC}"
    
    # Memory Usage
    local memory_info=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local total_memory=$(sysctl hw.memsize | awk '{print $2}')
    local free_memory=$((memory_info * 4096))
    local used_memory=$((total_memory - free_memory))
    local memory_percent=$((used_memory * 100 / total_memory))
    echo -e "${YELLOW}Memory Usage: ${memory_percent}%${NC}"
    
    # Disk Usage
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    echo -e "${YELLOW}Disk Usage: ${disk_usage}%${NC}"
    
    echo ""
}

# Function to display recent logs
display_recent_logs() {
    echo -e "${CYAN}📝 RECENT LOGS (Last 5 entries)${NC}"
    echo -e "${CYAN}==============================${NC}"
    echo ""
    
    # API Server Logs
    if [ -f "backend/zmart-api/api_server.log" ]; then
        echo -e "${YELLOW}API Server Logs:${NC}"
        tail -5 "backend/zmart-api/api_server.log" | while read line; do
            echo -e "  $line"
        done
    else
        echo -e "${YELLOW}API Server Logs: No log file found${NC}"
    fi
    
    echo ""
    
    # Dashboard Server Logs
    if [ -f "dashboard_server.log" ]; then
        echo -e "${YELLOW}Dashboard Server Logs:${NC}"
        tail -5 "dashboard_server.log" | while read line; do
            echo -e "  $line"
        done
    else
        echo -e "${YELLOW}Dashboard Server Logs: No log file found${NC}"
    fi
    
    echo ""
}

# Function to display connection info
display_connection_info() {
    echo -e "${CYAN}🔗 CONNECTION INFORMATION${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    
    echo -e "${GREEN}API Server:${NC}"
    echo -e "  URL: http://localhost:$API_PORT"
    echo -e "  Status Endpoint: http://localhost:$API_PORT/api/v1/alerts/status"
    echo -e "  Health Check: $(check_api_health)"
    echo ""
    
    echo -e "${GREEN}Dashboard Server:${NC}"
    echo -e "  URL: http://localhost:$DASHBOARD_PORT"
    echo -e "  Health Check: $(check_dashboard_health)"
    echo ""
    
    echo -e "${GREEN}External Access:${NC}"
    echo -e "  API: http://$(hostname -I | awk '{print $1}'):$API_PORT"
    echo -e "  Dashboard: http://$(hostname -I | awk '{print $1}'):$DASHBOARD_PORT"
    echo ""
}

# Main execution
main() {
    local show_detailed=false
    local show_resources=false
    local show_logs=false
    local show_connections=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed|-d)
                show_detailed=true
                shift
                ;;
            --resources|-r)
                show_resources=true
                shift
                ;;
            --logs|-l)
                show_logs=true
                shift
                ;;
            --connections|-c)
                show_connections=true
                shift
                ;;
            --all|-a)
                show_detailed=true
                show_resources=true
                show_logs=true
                show_connections=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -d, --detailed     Show detailed server status"
                echo "  -r, --resources    Show system resources"
                echo "  -l, --logs         Show recent logs"
                echo "  -c, --connections  Show connection information"
                echo "  -a, --all          Show all information"
                echo "  -h, --help         Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                 # Quick status"
                echo "  $0 -d              # Detailed status"
                echo "  $0 -a              # All information"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Display quick status by default
    display_quick_status
    
    # Display additional information based on flags
    if $show_detailed; then
        display_detailed_status
    fi
    
    if $show_resources; then
        display_system_resources
    fi
    
    if $show_logs; then
        display_recent_logs
    fi
    
    if $show_connections; then
        display_connection_info
    fi
    
    # Summary
    echo -e "${BLUE}💡 TIP: Use '$0 --help' for more options${NC}"
    echo ""
}

# Run main function
main "$@"
