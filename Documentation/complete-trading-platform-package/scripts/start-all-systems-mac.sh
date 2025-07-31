#!/bin/bash

# Complete Trading Platform - All Systems Startup Script
# =====================================================
# 
# Professional startup script for Mac Mini 2025 M2 Pro
# Starts all four trading platform modules with zero conflicts
#
# Author: Manus AI
# Version: 1.0 Professional Edition
# Compatibility: macOS Sonoma+, Apple Silicon M2 Pro

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# System requirements check
check_system_requirements() {
    log_header "CHECKING SYSTEM REQUIREMENTS"
    
    # Check macOS version
    if [[ $(uname) != "Darwin" ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    
    # Check if running on Apple Silicon
    if [[ $(uname -m) != "arm64" ]]; then
        log_warning "This script is optimized for Apple Silicon (M2 Pro)"
    fi
    
    # Check available memory
    TOTAL_MEMORY=$(sysctl -n hw.memsize)
    TOTAL_MEMORY_GB=$((TOTAL_MEMORY / 1024 / 1024 / 1024))
    
    if [[ $TOTAL_MEMORY_GB -lt 16 ]]; then
        log_error "Minimum 16GB RAM required. Found: ${TOTAL_MEMORY_GB}GB"
        exit 1
    fi
    
    log_success "System requirements check passed"
    log_info "Total Memory: ${TOTAL_MEMORY_GB}GB"
    log_info "Architecture: $(uname -m)"
    log_info "macOS Version: $(sw_vers -productVersion)"
}

# Check required tools
check_dependencies() {
    log_header "CHECKING DEPENDENCIES"
    
    local missing_deps=()
    
    # Check for required tools
    local required_tools=("docker" "docker-compose" "node" "npm" "python3" "pip3" "psql" "redis-cli")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_deps+=("$tool")
        else
            log_success "$tool found: $(command -v "$tool")"
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies using Homebrew:"
        log_info "brew install ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Check port availability
check_ports() {
    log_header "CHECKING PORT AVAILABILITY"
    
    local required_ports=(8000 3000 8100 3100 8200 3200 8300 3300 5432 6379 9090 3001)
    local occupied_ports=()
    
    for port in "${required_ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=("$port")
            log_warning "Port $port is occupied"
        else
            log_success "Port $port is available"
        fi
    done
    
    if [[ ${#occupied_ports[@]} -gt 0 ]]; then
        log_error "The following ports are occupied: ${occupied_ports[*]}"
        log_info "Please stop services using these ports or run:"
        log_info "./scripts/kill-conflicting-processes.sh"
        
        read -p "Do you want to automatically kill conflicting processes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for port in "${occupied_ports[@]}"; do
                log_info "Killing process on port $port"
                lsof -ti:$port | xargs kill -9 2>/dev/null || true
            done
            log_success "Conflicting processes terminated"
        else
            log_error "Cannot proceed with occupied ports"
            exit 1
        fi
    fi
    
    log_success "All required ports are available"
}

# Start infrastructure services
start_infrastructure() {
    log_header "STARTING INFRASTRUCTURE SERVICES"
    
    # Start PostgreSQL
    log_info "Starting PostgreSQL..."
    if brew services list | grep postgresql | grep started >/dev/null 2>&1; then
        log_success "PostgreSQL already running"
    else
        brew services start postgresql
        sleep 3
        log_success "PostgreSQL started"
    fi
    
    # Start Redis
    log_info "Starting Redis..."
    if brew services list | grep redis | grep started >/dev/null 2>&1; then
        log_success "Redis already running"
    else
        brew services start redis
        sleep 2
        log_success "Redis started"
    fi
    
    # Verify database connectivity
    log_info "Verifying database connectivity..."
    if psql -h localhost -p 5432 -U postgres -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "PostgreSQL connection verified"
    else
        log_error "Cannot connect to PostgreSQL"
        exit 1
    fi
    
    # Verify Redis connectivity
    log_info "Verifying Redis connectivity..."
    if redis-cli ping | grep PONG >/dev/null 2>&1; then
        log_success "Redis connection verified"
    else
        log_error "Cannot connect to Redis"
        exit 1
    fi
}

# Initialize databases
initialize_databases() {
    log_header "INITIALIZING DATABASES"
    
    # Create main database if not exists
    log_info "Creating trading_platform database..."
    psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE trading_platform;" 2>/dev/null || log_info "Database already exists"
    
    # Create schemas for each module
    local schemas=("zmartbot" "kingfisher" "trade_strategy" "simulation_agent")
    
    for schema in "${schemas[@]}"; do
        log_info "Creating schema: $schema"
        psql -h localhost -p 5432 -U postgres -d trading_platform -c "CREATE SCHEMA IF NOT EXISTS $schema;" 2>/dev/null
        log_success "Schema $schema ready"
    done
    
    # Run schema initialization scripts if they exist
    for schema in "${schemas[@]}"; do
        local schema_file="$PROJECT_ROOT/$schema/database/schema.sql"
        if [[ -f "$schema_file" ]]; then
            log_info "Initializing $schema schema from file"
            psql -h localhost -p 5432 -U postgres -d trading_platform -f "$schema_file" 2>/dev/null || true
        fi
    done
    
    log_success "Database initialization completed"
}

# Start ZmartBot
start_zmartbot() {
    log_header "STARTING ZMARTBOT (Ports: 8000/3000)"
    
    cd "$PROJECT_ROOT/zmartbot" 2>/dev/null || {
        log_warning "ZmartBot directory not found, skipping..."
        return 0
    }
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing ZmartBot dependencies..."
        npm install
    fi
    
    # Set environment variables
    export ZMARTBOT_API_PORT=8000
    export ZMARTBOT_FRONTEND_PORT=3000
    export ZMARTBOT_DB_SCHEMA=zmartbot
    export ZMARTBOT_REDIS_NAMESPACE=zb
    export DATABASE_URL="postgresql://postgres@localhost:5432/trading_platform"
    export REDIS_URL="redis://localhost:6379"
    
    # Start ZmartBot API
    log_info "Starting ZmartBot API on port 8000..."
    nohup npm run start:api > "$LOG_DIR/zmartbot-api.log" 2>&1 &
    echo $! > "$PID_DIR/zmartbot-api.pid"
    
    # Start ZmartBot Frontend
    log_info "Starting ZmartBot Frontend on port 3000..."
    nohup npm run start:frontend > "$LOG_DIR/zmartbot-frontend.log" 2>&1 &
    echo $! > "$PID_DIR/zmartbot-frontend.pid"
    
    # Wait for services to start
    sleep 5
    
    # Verify ZmartBot is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log_success "ZmartBot API started successfully"
    else
        log_error "ZmartBot API failed to start"
    fi
    
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_success "ZmartBot Frontend started successfully"
    else
        log_warning "ZmartBot Frontend may still be starting..."
    fi
    
    cd "$PROJECT_ROOT"
}

# Start KingFisher
start_kingfisher() {
    log_header "STARTING KINGFISHER (Ports: 8100/3100)"
    
    cd "$PROJECT_ROOT/kingfisher" 2>/dev/null || {
        log_warning "KingFisher directory not found, skipping..."
        return 0
    }
    
    # Create virtual environment if needed
    if [[ ! -d "venv" ]]; then
        log_info "Creating KingFisher virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [[ ! -f "venv/installed" ]]; then
        log_info "Installing KingFisher dependencies..."
        pip install -r requirements.txt
        touch venv/installed
    fi
    
    # Set environment variables
    export KINGFISHER_API_PORT=8100
    export KINGFISHER_FRONTEND_PORT=3100
    export KINGFISHER_DB_SCHEMA=kingfisher
    export KINGFISHER_REDIS_NAMESPACE=kf
    export DATABASE_URL="postgresql://postgres@localhost:5432/trading_platform"
    export REDIS_URL="redis://localhost:6379"
    
    # Start KingFisher API
    log_info "Starting KingFisher API on port 8100..."
    nohup python app.py > "$LOG_DIR/kingfisher-api.log" 2>&1 &
    echo $! > "$PID_DIR/kingfisher-api.pid"
    
    # Start KingFisher Frontend (if exists)
    if [[ -f "frontend/package.json" ]]; then
        cd frontend
        if [[ ! -d "node_modules" ]]; then
            npm install
        fi
        
        log_info "Starting KingFisher Frontend on port 3100..."
        nohup npm start > "$LOG_DIR/kingfisher-frontend.log" 2>&1 &
        echo $! > "$PID_DIR/kingfisher-frontend.pid"
        cd ..
    fi
    
    deactivate
    
    # Wait for services to start
    sleep 5
    
    # Verify KingFisher is running
    if curl -s http://localhost:8100/health >/dev/null 2>&1; then
        log_success "KingFisher API started successfully"
    else
        log_error "KingFisher API failed to start"
    fi
    
    cd "$PROJECT_ROOT"
}

# Start Trade Strategy
start_trade_strategy() {
    log_header "STARTING TRADE STRATEGY (Ports: 8200/3200)"
    
    cd "$PROJECT_ROOT/trade-strategy" 2>/dev/null || {
        log_warning "Trade Strategy directory not found, skipping..."
        return 0
    }
    
    # Create virtual environment if needed
    if [[ ! -d "venv" ]]; then
        log_info "Creating Trade Strategy virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [[ ! -f "venv/installed" ]]; then
        log_info "Installing Trade Strategy dependencies..."
        pip install -r requirements.txt
        touch venv/installed
    fi
    
    # Set environment variables
    export TRADE_STRATEGY_API_PORT=8200
    export TRADE_STRATEGY_FRONTEND_PORT=3200
    export TRADE_STRATEGY_DB_SCHEMA=trade_strategy
    export TRADE_STRATEGY_REDIS_NAMESPACE=ts
    export DATABASE_URL="postgresql://postgres@localhost:5432/trading_platform"
    export REDIS_URL="redis://localhost:6379"
    
    # Start Trade Strategy API
    log_info "Starting Trade Strategy API on port 8200..."
    nohup python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8200 > "$LOG_DIR/trade-strategy-api.log" 2>&1 &
    echo $! > "$PID_DIR/trade-strategy-api.pid"
    
    # Start Trade Strategy Frontend (if exists)
    if [[ -f "frontend/package.json" ]]; then
        cd frontend
        if [[ ! -d "node_modules" ]]; then
            npm install
        fi
        
        log_info "Starting Trade Strategy Frontend on port 3200..."
        nohup npm start > "$LOG_DIR/trade-strategy-frontend.log" 2>&1 &
        echo $! > "$PID_DIR/trade-strategy-frontend.pid"
        cd ..
    fi
    
    deactivate
    
    # Wait for services to start
    sleep 5
    
    # Verify Trade Strategy is running
    if curl -s http://localhost:8200/health >/dev/null 2>&1; then
        log_success "Trade Strategy API started successfully"
    else
        log_error "Trade Strategy API failed to start"
    fi
    
    cd "$PROJECT_ROOT"
}

# Start Simulation Agent
start_simulation_agent() {
    log_header "STARTING SIMULATION AGENT (Ports: 8300/3300)"
    
    cd "$PROJECT_ROOT/simulation-agent" 2>/dev/null || {
        log_warning "Simulation Agent directory not found, skipping..."
        return 0
    }
    
    # Create virtual environment if needed
    if [[ ! -d "venv" ]]; then
        log_info "Creating Simulation Agent virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [[ ! -f "venv/installed" ]]; then
        log_info "Installing Simulation Agent dependencies..."
        pip install -r requirements.txt
        touch venv/installed
    fi
    
    # Set environment variables
    export SIMULATION_AGENT_API_PORT=8300
    export SIMULATION_AGENT_FRONTEND_PORT=3300
    export SIMULATION_AGENT_DB_SCHEMA=simulation_agent
    export SIMULATION_AGENT_REDIS_NAMESPACE=sa
    export DATABASE_URL="postgresql://postgres@localhost:5432/trading_platform"
    export REDIS_URL="redis://localhost:6379"
    
    # Start Simulation Agent API
    log_info "Starting Simulation Agent API on port 8300..."
    nohup python -m uvicorn src.api.simulation:app --host 0.0.0.0 --port 8300 > "$LOG_DIR/simulation-agent-api.log" 2>&1 &
    echo $! > "$PID_DIR/simulation-agent-api.pid"
    
    # Start Simulation Agent Frontend (if exists)
    if [[ -f "frontend/package.json" ]]; then
        cd frontend
        if [[ ! -d "node_modules" ]]; then
            npm install
        fi
        
        log_info "Starting Simulation Agent Frontend on port 3300..."
        nohup npm start > "$LOG_DIR/simulation-agent-frontend.log" 2>&1 &
        echo $! > "$PID_DIR/simulation-agent-frontend.pid"
        cd ..
    fi
    
    deactivate
    
    # Wait for services to start
    sleep 5
    
    # Verify Simulation Agent is running
    if curl -s http://localhost:8300/health >/dev/null 2>&1; then
        log_success "Simulation Agent API started successfully"
    else
        log_error "Simulation Agent API failed to start"
    fi
    
    cd "$PROJECT_ROOT"
}

# Start monitoring services
start_monitoring() {
    log_header "STARTING MONITORING SERVICES"
    
    # Start Prometheus (if configured)
    if [[ -f "$PROJECT_ROOT/monitoring/prometheus.yml" ]]; then
        log_info "Starting Prometheus on port 9090..."
        cd "$PROJECT_ROOT/monitoring"
        nohup prometheus --config.file=prometheus.yml --storage.tsdb.path=data/ > "$LOG_DIR/prometheus.log" 2>&1 &
        echo $! > "$PID_DIR/prometheus.pid"
        cd "$PROJECT_ROOT"
        
        sleep 3
        if curl -s http://localhost:9090 >/dev/null 2>&1; then
            log_success "Prometheus started successfully"
        else
            log_warning "Prometheus may still be starting..."
        fi
    fi
    
    # Start Grafana (if configured)
    if [[ -f "$PROJECT_ROOT/monitoring/grafana.ini" ]]; then
        log_info "Starting Grafana on port 3001..."
        cd "$PROJECT_ROOT/monitoring"
        nohup grafana-server --config=grafana.ini > "$LOG_DIR/grafana.log" 2>&1 &
        echo $! > "$PID_DIR/grafana.pid"
        cd "$PROJECT_ROOT"
        
        sleep 5
        if curl -s http://localhost:3001 >/dev/null 2>&1; then
            log_success "Grafana started successfully"
        else
            log_warning "Grafana may still be starting..."
        fi
    fi
}

# Verify all services
verify_services() {
    log_header "VERIFYING ALL SERVICES"
    
    local services=(
        "ZmartBot API:http://localhost:8000/health"
        "ZmartBot Frontend:http://localhost:3000"
        "KingFisher API:http://localhost:8100/health"
        "KingFisher Frontend:http://localhost:3100"
        "Trade Strategy API:http://localhost:8200/health"
        "Trade Strategy Frontend:http://localhost:3200"
        "Simulation Agent API:http://localhost:8300/health"
        "Simulation Agent Frontend:http://localhost:3300"
        "Prometheus:http://localhost:9090"
        "Grafana:http://localhost:3001"
    )
    
    local running_services=0
    local total_services=${#services[@]}
    
    for service in "${services[@]}"; do
        local name="${service%%:*}"
        local url="${service##*:}"
        
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            log_success "$name is running"
            ((running_services++))
        else
            log_warning "$name is not responding"
        fi
    done
    
    log_info "Services running: $running_services/$total_services"
    
    if [[ $running_services -ge $((total_services * 3 / 4)) ]]; then
        log_success "System startup successful!"
    else
        log_warning "Some services may not be running properly"
    fi
}

# Display system status
display_status() {
    log_header "SYSTEM STATUS DASHBOARD"
    
    echo -e "${CYAN}🎯 Complete Trading Platform - System Status${NC}"
    echo -e "${CYAN}=============================================${NC}"
    echo ""
    
    echo -e "${WHITE}📊 Core Trading Modules:${NC}"
    echo -e "  • ZmartBot:        ${GREEN}http://localhost:8000${NC} | ${BLUE}http://localhost:3000${NC}"
    echo -e "  • KingFisher:      ${GREEN}http://localhost:8100${NC} | ${BLUE}http://localhost:3100${NC}"
    echo -e "  • Trade Strategy:  ${GREEN}http://localhost:8200${NC} | ${BLUE}http://localhost:3200${NC}"
    echo -e "  • Simulation Agent:${GREEN}http://localhost:8300${NC} | ${BLUE}http://localhost:3300${NC}"
    echo ""
    
    echo -e "${WHITE}🔧 Infrastructure Services:${NC}"
    echo -e "  • PostgreSQL:      ${GREEN}localhost:5432${NC} (Database)"
    echo -e "  • Redis:           ${GREEN}localhost:6379${NC} (Cache)"
    echo -e "  • Prometheus:      ${GREEN}http://localhost:9090${NC} (Metrics)"
    echo -e "  • Grafana:         ${GREEN}http://localhost:3001${NC} (Dashboards)"
    echo ""
    
    echo -e "${WHITE}📁 Important Directories:${NC}"
    echo -e "  • Logs:            ${YELLOW}$LOG_DIR${NC}"
    echo -e "  • PIDs:            ${YELLOW}$PID_DIR${NC}"
    echo -e "  • Project Root:    ${YELLOW}$PROJECT_ROOT${NC}"
    echo ""
    
    echo -e "${WHITE}🎮 Management Commands:${NC}"
    echo -e "  • Stop All:        ${CYAN}./scripts/stop-all-systems.sh${NC}"
    echo -e "  • Health Check:    ${CYAN}./scripts/health-check-all.sh${NC}"
    echo -e "  • View Logs:       ${CYAN}./scripts/view-logs.sh${NC}"
    echo -e "  • System Status:   ${CYAN}./scripts/system-status.sh${NC}"
    echo ""
    
    echo -e "${GREEN}🚀 System startup completed successfully!${NC}"
    echo -e "${YELLOW}💡 Open Cursor AI workspace: ${CYAN}cursor complete-trading-platform.code-workspace${NC}"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    # Add any cleanup tasks here
}

# Error handling
handle_error() {
    log_error "An error occurred during startup"
    log_info "Check logs in: $LOG_DIR"
    log_info "Check PIDs in: $PID_DIR"
    cleanup
    exit 1
}

# Set error trap
trap handle_error ERR

# Main execution
main() {
    log_header "COMPLETE TRADING PLATFORM STARTUP"
    log_info "Starting all systems on Mac Mini 2025 M2 Pro..."
    log_info "Project Root: $PROJECT_ROOT"
    
    # Pre-flight checks
    check_system_requirements
    check_dependencies
    check_ports
    
    # Start infrastructure
    start_infrastructure
    initialize_databases
    
    # Start trading modules
    start_zmartbot
    start_kingfisher
    start_trade_strategy
    start_simulation_agent
    
    # Start monitoring
    start_monitoring
    
    # Verify and display status
    sleep 10  # Give services time to fully start
    verify_services
    display_status
    
    log_success "Complete Trading Platform startup finished!"
}

# Execute main function
main "$@"

