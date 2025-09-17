#!/bin/bash

# 🎯 ZmartBot Orchestration Start Script
# ======================================
# Manages all registered services during system startup
# Follows StopStartCycle methodology from rules

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="../.."
PORT_REGISTRY="$PROJECT_ROOT/zmart-api/port_registry.db"
SERVICES_DIR="$PROJECT_ROOT/zmart-api"

# Service startup order (dependencies first) - using exact registry names
SERVICE_STARTUP_ORDER=(
    "system-protection-service"     # CRITICAL System Protection (Port 8999)
    "optimization-claude-service"   # HIGH Priority Optimization (Port 8080)
    "snapshot-service"              # CRITICAL Disaster Recovery (Port 8085)
    "passport-service"              # Service Registration & Identity Management (Port 8620)
    "doctor-service"                # AI-Powered System Diagnostics (Port 8700)
    "servicelog-service"            # Intelligent Log Analysis & Advice System (Port 8750)
    "zmart_api"                    # Core API (Port 8000)
    "port-manager-service"          # Port management (Port 8050)
    "api-keys-manager-service"      # API keys (Port 8006)
    "mdc-orchestration-agent"       # MDC orchestration (Port 8615)
    "zmart_dashboard"              # Frontend (Port 3400)
    "zmart_analytics"              # Analytics (Port 8007)
    "zmart_backtesting"            # Backtesting (Port 8013)
    "zmart_data_warehouse"         # Data warehouse (Port 8015)
    "zmart_machine_learning"       # ML service (Port 8014)
    "zmart_notification"           # Notifications (Port 8008)
    "zmart_risk_management"        # Risk management (Port 8010)
    "zmart_technical_analysis"     # Technical analysis (Port 8011)
    "zmart_websocket"              # WebSocket (Port 8009)
    "zmart_alert_system"           # Alert system (Port 8012)
    "my-symbols-extended-service"  # Symbols extended (Port 8005)
    "mysymbols"                    # MySymbols internal API (Port 8201)
    "test-service"                 # Test service worker (Port 8301)
    "kucoin"                       # KuCoin worker (Port 8302)
    "binance-worker-service"       # Binance worker (Port 8303)
    "discovery-database-service"   # Discovery Database Service (Port 8780)
    "service-discovery"            # Service Discovery & Port Assignment (Port 8550)
    "master-orchestration-agent"   # Master Orchestration (Port 8002)
    "service-dashboard"            # Service Dashboard (Port 3000)
)

# Service directory mapping (using functions for compatibility)
get_service_dir() {
    local service_name="$1"
    case "$service_name" in
"system-protection-service") echo "system_protection" ;;
        "optimization-claude-service") echo "optimization_claude" ;;
        "snapshot-service") echo "snapshot_service" ;;
        "passport-service") echo "../services/passport-service" ;;
        "doctor-service") echo "../services/doctor-service" ;;
        "servicelog-service") echo "../services/servicelog-service" ;;
        "zmart_api") echo "." ;;
        "port-manager-service") echo "port_manager" ;;
        "api-keys-manager-service") echo "api_keys_manager" ;;
        "mdc-orchestration-agent") echo "mdc_orchestration" ;;
        "zmart_dashboard") echo "." ;;
        "zmart_analytics") echo "analytics" ;;
        "zmart_backtesting") echo "backtesting" ;;
        "zmart_data_warehouse") echo "data_warehouse" ;;
        "zmart_machine_learning") echo "machine_learning" ;;
        "zmart_notification") echo "notification" ;;
        "zmart_risk_management") echo "risk_management" ;;
        "zmart_technical_analysis") echo "technical_analysis" ;;
        "zmart_websocket") echo "websocket" ;;
        "zmart_alert_system") echo "alert_system" ;;
            "my-symbols-extended-service") echo "symbols_extended" ;;
    "mysymbols") echo "mysymbols" ;;
    "test-service") echo "test_service" ;;
    "kucoin") echo "kucoin" ;;
    "binance-worker-service") echo "binance_worker" ;;
    "discovery-database-service") echo "../services/discovery-database-service" ;;
            "service-discovery") echo "../../dashboard/MDC-Dashboard/service-discovery" ;;
        "master-orchestration-agent") echo "orchestration" ;;
        "service-dashboard") echo "../../dashboard/Service-Dashboard" ;;
    *) echo "" ;;
    esac
}

# Service startup commands (using functions for compatibility)
get_service_command() {
    local service_name="$1"
    case "$service_name" in
"system-protection-service") echo "python3 system_protection_server.py --port 8999" ;;
        "optimization-claude-service") echo "python3 optimization_claude_server.py --port 8080" ;;
        "snapshot-service") echo "python3 snapshot_service_server.py --port 8085" ;;
        "passport-service") echo "./start_passport_service.sh" ;;
        "doctor-service") echo "./start_doctor_service.sh" ;;
        "servicelog-service") echo "python3 servicelog_service.py --port 8750" ;;
        "zmart_api") echo "python3 run_dev.py" ;;
        "port-manager-service") echo "python3 port_manager_server.py --port 8050" ;;
        "api-keys-manager-service") echo "python3 api_keys_manager_server.py --port 8006" ;;
        "mdc-orchestration-agent") echo "python3 mdc_orchestration_agent.py --port 8615" ;;
        "zmart_dashboard") echo "python3 professional_dashboard_server.py --port 3400" ;;
        "zmart_analytics") echo "python3 analytics_server.py --port 8007" ;;
        "zmart_backtesting") echo "python3 backtesting_server.py --port 8013" ;;
        "zmart_data_warehouse") echo "python3 data_warehouse_server.py --port 8015" ;;
        "zmart_machine_learning") echo "python3 machine_learning_server.py --port 8014" ;;
        "zmart_notification") echo "python3 notification_server.py --port 8008" ;;
        "zmart_risk_management") echo "python3 risk_management_server.py --port 8010" ;;
        "zmart_technical_analysis") echo "python3 technical_analysis_server.py --port 8011" ;;
        "zmart_websocket") echo "python3 websocket_server.py --port 8009" ;;
        "zmart_alert_system") echo "python3 alert_system_server.py --port 8012" ;;
            "my-symbols-extended-service") echo "python3 symbols_extended_server.py --port 8005" ;;
    "mysymbols") echo "python3 mysymbols_server.py --port 8201" ;;
    "test-service") echo "python3 test_service_server.py --port 8301" ;;
    "kucoin") echo "python3 kucoin_server.py --port 8302" ;;
    "binance-worker-service") echo "python3 binance_worker_server.py --port 8303" ;;
    "discovery-database-service") echo "python3 discovery_database_server.py --port 8780" ;;
    "service-discovery") echo "python3 service_discovery_server.py --port 8550" ;;
        "master-orchestration-agent") echo "python3 orchestration_server.py --port 8002" ;;
        "service-dashboard") echo "python3 service_dashboard_server.py --port 3000" ;;
    *) echo "" ;;
    esac
}

# Function to get service port from registry
get_service_port() {
    local service_name="$1"
    sqlite3 "$PORT_REGISTRY" "SELECT port FROM port_assignments WHERE service_name = '$service_name' LIMIT 1;" 2>/dev/null || echo ""
}

# Function to check if service is running
is_service_running() {
    local service_name="$1"
    local port="$2"
    
    if [ -z "$port" ]; then
        return 1
    fi
    
    # Check if process is running
    if pgrep -f "$service_name" >/dev/null 2>&1; then
        return 0
    fi
    
    # Check if port is in use
    if lsof -i ":$port" >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# Function to start a service
start_service() {
    local service_name="$1"
    local service_dir=$(get_service_dir "$service_name")
    local startup_cmd=$(get_service_command "$service_name")
    local port=$(get_service_port "$service_name")
    
    # Change to project root for service operations
    cd "$PROJECT_ROOT" || {
        echo -e "${RED}❌ Cannot access project root: $PROJECT_ROOT${NC}"
        return 1
    }
    
    if [ -z "$service_dir" ]; then
        echo -e "${RED}❌ Service directory not found for: $service_name${NC}"
        return 1
    fi
    
    if [ -z "$port" ]; then
        echo -e "${RED}❌ Port not found in registry for: $service_name${NC}"
        return 1
    fi
    
    if is_service_running "$service_name" "$port"; then
        echo -e "${YELLOW}⚠️  Service already running: $service_name (Port $port)${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🚀 Starting: $service_name (Port $port)${NC}"
    
    # Change to service directory and start
    cd "zmart-api/$service_dir" || {
        echo -e "${RED}❌ Service directory not found: zmart-api/$service_dir${NC}"
        return 1
    }
    
    # Start service in background
    nohup $startup_cmd > "${service_name}.log" 2>&1 &
    local pid=$!
    
    # Wait a moment for startup
    sleep 2
    
    # Check if service started successfully
    if is_service_running "$service_name" "$port"; then
        echo -e "${GREEN}✅ Started: $service_name (PID: $pid, Port: $port)${NC}"
        
        # Update port registry with PID
        sqlite3 "$PORT_REGISTRY" "UPDATE port_assignments SET status = 'active', pid = $pid, updated_at = datetime('now') WHERE service_name = '$service_name';" 2>/dev/null || true
        
        return 0
    else
        echo -e "${RED}❌ Failed to start: $service_name${NC}"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local service_name="$1"
    local port=$(get_service_port "$service_name")
    
    echo -e "${YELLOW}🛑 Stopping: $service_name${NC}"
    
    # Kill processes by name
    pkill -f "$service_name" 2>/dev/null || true
    
    # Kill processes by port
    if [ -n "$port" ]; then
        lsof -ti ":$port" | xargs kill -9 2>/dev/null || true
    fi
    
    # Update port registry
    sqlite3 "$PORT_REGISTRY" "UPDATE port_assignments SET status = 'stopped', pid = NULL, updated_at = datetime('now') WHERE service_name = '$service_name';" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Stopped: $service_name${NC}"
}

# Function to check service health
check_service_health() {
    local service_name="$1"
    local port=$(get_service_port "$service_name")
    
    if [ -z "$port" ]; then
        echo -e "${RED}❌ Port not found for: $service_name${NC}"
        return 1
    fi
    
    # Try health endpoint
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy: $service_name (Port $port)${NC}"
        return 0
    fi
    
    echo -e "${RED}❌ Unhealthy: $service_name (Port $port)${NC}"
    return 1
}

# Function to add a service to orchestration
add_service() {
    local service_name="$1"
    
    echo -e "${BLUE}➕ Adding service to orchestration: $service_name${NC}"
    
    # Check if service exists in registry
    local port=$(get_service_port "$service_name")
    if [ -z "$port" ]; then
        echo -e "${RED}❌ Service not found in registry: $service_name${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Service added to orchestration: $service_name (Port $port)${NC}"
}

# Function to start all services
start_all() {
    echo -e "${BLUE}🚀 Starting all ZmartBot services...${NC}"
    echo "=============================================="
    
    local failed_services=()
    
    for service in "${SERVICE_STARTUP_ORDER[@]}"; do
        if ! start_service "$service"; then
            failed_services+=("$service")
        fi
    done
    
    echo "=============================================="
    echo -e "${BLUE}🎯 Startup complete!${NC}"
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All services started successfully${NC}"
    else
        echo -e "${RED}❌ Failed services: ${failed_services[*]}${NC}"
        return 1
    fi
}

# Function to stop all services
stop_all() {
    echo -e "${YELLOW}🛑 Stopping all ZmartBot services...${NC}"
    echo "=============================================="
    
    # Stop in reverse order
    for ((i=${#SERVICE_STARTUP_ORDER[@]}-1; i>=0; i--)); do
        local service="${SERVICE_STARTUP_ORDER[$i]}"
        stop_service "$service"
    done
    
    echo "=============================================="
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Function to check all services health
check_all_health() {
    echo -e "${BLUE}🔍 Checking health of all services...${NC}"
    echo "=============================================="
    
    local healthy_count=0
    local total_count=0
    
    for service in "${SERVICE_STARTUP_ORDER[@]}"; do
        total_count=$((total_count + 1))
        if check_service_health "$service"; then
            healthy_count=$((healthy_count + 1))
        fi
    done
    
    echo "=============================================="
    echo -e "${BLUE}📊 Health Summary: $healthy_count/$total_count services healthy${NC}"
    
    if [ $healthy_count -eq $total_count ]; then
        echo -e "${GREEN}✅ All services are healthy!${NC}"
        return 0
    else
        echo -e "${RED}❌ Some services are unhealthy${NC}"
        return 1
    fi
}

# Function to show service status
show_status() {
    echo -e "${BLUE}📋 ZmartBot Service Status${NC}"
    echo "=============================================="
    
    printf "%-30s %-10s %-10s %-10s\n" "Service" "Port" "Status" "PID"
    echo "------------------------------------------------------------"
    
    for service in "${SERVICE_STARTUP_ORDER[@]}"; do
        local port=$(get_service_port "$service")
        local status="unknown"
        local pid=""
        
        if [ -n "$port" ]; then
            if is_service_running "$service" "$port"; then
                status="running"
                pid=$(pgrep -f "$service" | head -1)
            else
                status="stopped"
            fi
        fi
        
        printf "%-30s %-10s %-10s %-10s\n" "$service" "$port" "$status" "$pid"
    done
}

# Main script logic
case "${1:-}" in
    "start")
        if [ -n "$2" ]; then
            start_service "$2"
        else
            start_all
        fi
        ;;
    "stop")
        if [ -n "$2" ]; then
            stop_service "$2"
        else
            stop_all
        fi
        ;;
    "restart")
        if [ -n "$2" ]; then
            stop_service "$2"
            sleep 2
            start_service "$2"
        else
            stop_all
            sleep 3
            start_all
        fi
        ;;
    "health"|"check")
        if [ -n "$2" ]; then
            check_service_health "$2"
        else
            check_all_health
        fi
        ;;
    "status")
        show_status
        ;;
    "add")
        if [ -n "$2" ]; then
            add_service "$2"
        else
            echo -e "${RED}❌ Service name required for add command${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${BLUE}🎯 ZmartBot Orchestration Start Script${NC}"
        echo "=============================================="
        echo "Usage: $0 {start|stop|restart|health|status|add} [service_name]"
        echo ""
        echo "Commands:"
        echo "  start [service]    - Start all services or specific service"
        echo "  stop [service]     - Stop all services or specific service"
        echo "  restart [service]  - Restart all services or specific service"
        echo "  health [service]   - Check health of all services or specific service"
        echo "  status            - Show status of all services"
        echo "  add <service>     - Add service to orchestration"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start all services"
        echo "  $0 start zmart-api          # Start specific service"
        echo "  $0 health                   # Check all services health"
        echo "  $0 status                   # Show service status"
        echo "  $0 add my-new-service       # Add new service"
        exit 1
        ;;
esac
