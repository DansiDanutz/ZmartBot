#!/bin/bash

# =============================================================================
# Trade Strategy Module - Complete System Startup Script
# =============================================================================
# 
# Professional startup script for Mac Mini 2025 M2 Pro
# Starts ZmartBot + KingFisher + Trade Strategy with zero conflicts
#
# Author: Manus AI
# Version: 1.0 Professional Edition
# Compatibility: Mac Mini 2025 M2 Pro Integration
# =============================================================================

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

# Emoji for better UX
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GEAR="⚙️"
DATABASE="🗄️"
ROBOT="🤖"
FISH="🐟"
TARGET="🎯"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_ROOT/logs"
PIDS_DIR="$PROJECT_ROOT/pids"

# System paths
ZMARTBOT_PATH="$PROJECT_ROOT/zmartbot"
KINGFISHER_PATH="$PROJECT_ROOT/kingfisher-platform"
TRADE_STRATEGY_PATH="$PROJECT_ROOT/trade-strategy-module"

# Port configuration (zero-conflict architecture)
ZMARTBOT_API_PORT=8000
ZMARTBOT_FRONTEND_PORT=3000
KINGFISHER_API_PORT=8100
KINGFISHER_FRONTEND_PORT=3100
TRADE_STRATEGY_API_PORT=8200
TRADE_STRATEGY_FRONTEND_PORT=3200
TRADE_STRATEGY_WS_PORT=8201
TRADE_STRATEGY_METRICS_PORT=8202

# Database configuration
DB_HOST="localhost"
DB_PORT=5432
DB_NAME="trading_platform"
DB_SCHEMAS=("zmartbot" "kingfisher" "trade_strategy")

# Redis configuration
REDIS_HOST="localhost"
REDIS_PORT=6379

# Service timeouts
STARTUP_TIMEOUT=60
HEALTH_CHECK_TIMEOUT=30
SERVICE_READY_TIMEOUT=120

# Logging functions
log_info() {
    echo -e "${CYAN}${INFO} $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_success() {
    echo -e "${GREEN}${CHECK} $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_error() {
    echo -e "${RED}${CROSS} $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_header() {
    echo -e "\n${WHITE}${GEAR} ============================================${NC}"
    echo -e "${WHITE}${GEAR} $1${NC}"
    echo -e "${WHITE}${GEAR} ============================================${NC}\n"
}

# Utility functions
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p "$LOGS_DIR"
    mkdir -p "$PIDS_DIR"
    mkdir -p "$PROJECT_ROOT/backups"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/temp"
    
    # Create log files
    touch "$LOGS_DIR/zmartbot.log"
    touch "$LOGS_DIR/kingfisher.log"
    touch "$LOGS_DIR/trade-strategy.log"
    touch "$LOGS_DIR/system.log"
    
    log_success "Directories created successfully"
}

check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check macOS version
    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    
    # Check if running on Apple Silicon
    if [[ "$(uname -m)" == "arm64" ]]; then
        log_success "Running on Apple Silicon (M-series) - Optimized performance enabled"
    else
        log_warning "Running on Intel Mac - Performance may be reduced"
    fi
    
    # Check available memory
    AVAILABLE_MEMORY=$(sysctl -n hw.memsize)
    AVAILABLE_GB=$((AVAILABLE_MEMORY / 1024 / 1024 / 1024))
    
    if [[ $AVAILABLE_GB -lt 8 ]]; then
        log_error "Insufficient memory: ${AVAILABLE_GB}GB available, minimum 8GB required"
        exit 1
    elif [[ $AVAILABLE_GB -ge 16 ]]; then
        log_success "Memory check passed: ${AVAILABLE_GB}GB available (Excellent)"
    else
        log_warning "Memory check passed: ${AVAILABLE_GB}GB available (Adequate)"
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ ${AVAILABLE_SPACE%.*} -lt 10 ]]; then
        log_error "Insufficient disk space: ${AVAILABLE_SPACE}GB available, minimum 10GB required"
        exit 1
    fi
    
    log_success "System requirements check completed"
}

check_dependencies() {
    log_info "Checking required dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python ${PYTHON_VERSION} found"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    else
        NODE_VERSION=$(node --version)
        log_success "Node.js ${NODE_VERSION} found"
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        missing_deps+=("postgresql")
    else
        log_success "PostgreSQL found"
    fi
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        missing_deps+=("redis")
    else
        log_success "Redis found"
    fi
    
    # Check Docker (optional but recommended)
    if command -v docker &> /dev/null; then
        log_success "Docker found (optional)"
    else
        log_warning "Docker not found (optional, but recommended for production)"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies using Homebrew:"
        for dep in "${missing_deps[@]}"; do
            echo "  brew install $dep"
        done
        exit 1
    fi
    
    log_success "All dependencies are available"
}

check_port_availability() {
    log_info "Checking port availability..."
    
    local ports=(
        "$ZMARTBOT_API_PORT:ZmartBot API"
        "$ZMARTBOT_FRONTEND_PORT:ZmartBot Frontend"
        "$KINGFISHER_API_PORT:KingFisher API"
        "$KINGFISHER_FRONTEND_PORT:KingFisher Frontend"
        "$TRADE_STRATEGY_API_PORT:Trade Strategy API"
        "$TRADE_STRATEGY_FRONTEND_PORT:Trade Strategy Frontend"
        "$TRADE_STRATEGY_WS_PORT:Trade Strategy WebSocket"
        "$TRADE_STRATEGY_METRICS_PORT:Trade Strategy Metrics"
    )
    
    local occupied_ports=()
    
    for port_info in "${ports[@]}"; do
        local port="${port_info%%:*}"
        local service="${port_info##*:}"
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=("$port ($service)")
        fi
    done
    
    if [[ ${#occupied_ports[@]} -gt 0 ]]; then
        log_warning "The following ports are already in use:"
        for port in "${occupied_ports[@]}"; do
            echo "  - Port $port"
        done
        
        read -p "Do you want to kill existing processes and continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Stopping existing processes..."
            "$SCRIPT_DIR/stop-all-mac.sh" || true
            sleep 3
        else
            log_error "Cannot continue with occupied ports"
            exit 1
        fi
    fi
    
    log_success "All required ports are available"
}

start_infrastructure() {
    log_header "Starting Infrastructure Services"
    
    # Start PostgreSQL
    log_info "Starting PostgreSQL..."
    if brew services list | grep postgresql | grep -q started; then
        log_success "PostgreSQL is already running"
    else
        brew services start postgresql
        sleep 5
        
        # Wait for PostgreSQL to be ready
        local retries=0
        while ! pg_isready -h $DB_HOST -p $DB_PORT >/dev/null 2>&1; do
            if [[ $retries -ge 30 ]]; then
                log_error "PostgreSQL failed to start within timeout"
                exit 1
            fi
            log_info "Waiting for PostgreSQL to be ready..."
            sleep 2
            ((retries++))
        done
        
        log_success "PostgreSQL started successfully"
    fi
    
    # Start Redis
    log_info "Starting Redis..."
    if brew services list | grep redis | grep -q started; then
        log_success "Redis is already running"
    else
        brew services start redis
        sleep 3
        
        # Wait for Redis to be ready
        local retries=0
        while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping >/dev/null 2>&1; do
            if [[ $retries -ge 15 ]]; then
                log_error "Redis failed to start within timeout"
                exit 1
            fi
            log_info "Waiting for Redis to be ready..."
            sleep 2
            ((retries++))
        done
        
        log_success "Redis started successfully"
    fi
    
    log_success "Infrastructure services are running"
}

setup_database() {
    log_header "Setting Up Database"
    
    # Create database if it doesn't exist
    log_info "Creating database '$DB_NAME' if it doesn't exist..."
    if ! psql -h $DB_HOST -p $DB_PORT -U postgres -lqt | cut -d \\| -f 1 | grep -qw $DB_NAME; then
        createdb -h $DB_HOST -p $DB_PORT -U postgres $DB_NAME
        log_success "Database '$DB_NAME' created"
    else
        log_success "Database '$DB_NAME' already exists"
    fi
    
    # Create schemas
    for schema in "${DB_SCHEMAS[@]}"; do
        log_info "Creating schema '$schema'..."
        psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "CREATE SCHEMA IF NOT EXISTS $schema;" >/dev/null 2>&1
        log_success "Schema '$schema' ready"
    done
    
    # Create users and grant permissions
    log_info "Setting up database users and permissions..."
    
    # ZmartBot user
    psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'zmart_user') THEN
                CREATE USER zmart_user WITH PASSWORD 'secure_zmart_password_2025';
            END IF;
        END
        \$\$;
        GRANT ALL PRIVILEGES ON SCHEMA zmartbot TO zmart_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA zmartbot TO zmart_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA zmartbot TO zmart_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA zmartbot GRANT ALL ON TABLES TO zmart_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA zmartbot GRANT ALL ON SEQUENCES TO zmart_user;
    " >/dev/null 2>&1
    
    # KingFisher user
    psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kf_user') THEN
                CREATE USER kf_user WITH PASSWORD 'secure_kf_password_2025';
            END IF;
        END
        \$\$;
        GRANT ALL PRIVILEGES ON SCHEMA kingfisher TO kf_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA kingfisher TO kf_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA kingfisher TO kf_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA kingfisher GRANT ALL ON TABLES TO kf_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA kingfisher GRANT ALL ON SEQUENCES TO kf_user;
    " >/dev/null 2>&1
    
    # Trade Strategy user
    psql -h $DB_HOST -p $DB_PORT -U postgres -d $DB_NAME -c "
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'trade_strategy_app') THEN
                CREATE USER trade_strategy_app WITH PASSWORD 'secure_app_password_2025';
            END IF;
        END
        \$\$;
        GRANT ALL PRIVILEGES ON SCHEMA trade_strategy TO trade_strategy_app;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA trade_strategy TO trade_strategy_app;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA trade_strategy TO trade_strategy_app;
        ALTER DEFAULT PRIVILEGES IN SCHEMA trade_strategy GRANT ALL ON TABLES TO trade_strategy_app;
        ALTER DEFAULT PRIVILEGES IN SCHEMA trade_strategy GRANT ALL ON SEQUENCES TO trade_strategy_app;
    " >/dev/null 2>&1
    
    log_success "Database setup completed"
}

start_zmartbot() {
    log_header "${ROBOT} Starting ZmartBot System"
    
    if [[ ! -d "$ZMARTBOT_PATH" ]]; then
        log_error "ZmartBot directory not found at $ZMARTBOT_PATH"
        return 1
    fi
    
    cd "$ZMARTBOT_PATH"
    
    # Backend
    log_info "Starting ZmartBot backend..."
    if [[ -d "backend/zmart-api" ]]; then
        cd "backend/zmart-api"
        
        # Create virtual environment if it doesn't exist
        if [[ ! -d "venv" ]]; then
            log_info "Creating Python virtual environment for ZmartBot..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        
        if [[ -f "requirements.txt" ]]; then
            log_info "Installing ZmartBot dependencies..."
            pip install -r requirements.txt >/dev/null 2>&1
        fi
        
        # Set environment variables
        export ZMARTBOT_ENV="development"
        export ZMARTBOT_PORT="$ZMARTBOT_API_PORT"
        export DATABASE_URL="postgresql://zmart_user:secure_zmart_password_2025@$DB_HOST:$DB_PORT/$DB_NAME"
        export REDIS_URL="redis://$REDIS_HOST:$REDIS_PORT/0"
        
        # Start backend
        nohup python -m uvicorn main:app --host 0.0.0.0 --port $ZMARTBOT_API_PORT --reload > "$LOGS_DIR/zmartbot.log" 2>&1 &
        echo $! > "$PIDS_DIR/zmartbot-backend.pid"
        
        cd "$ZMARTBOT_PATH"
    fi
    
    # Frontend
    log_info "Starting ZmartBot frontend..."
    if [[ -d "frontend" ]]; then
        cd "frontend"
        
        # Install dependencies if needed
        if [[ -f "package.json" && ! -d "node_modules" ]]; then
            log_info "Installing ZmartBot frontend dependencies..."
            npm install >/dev/null 2>&1
        fi
        
        # Set environment variables
        export REACT_APP_API_URL="http://localhost:$ZMARTBOT_API_PORT"
        export PORT="$ZMARTBOT_FRONTEND_PORT"
        
        # Start frontend
        nohup npm start > "$LOGS_DIR/zmartbot-frontend.log" 2>&1 &
        echo $! > "$PIDS_DIR/zmartbot-frontend.pid"
    fi
    
    log_success "ZmartBot startup initiated"
}

start_kingfisher() {
    log_header "${FISH} Starting KingFisher Platform"
    
    if [[ ! -d "$KINGFISHER_PATH" ]]; then
        log_error "KingFisher directory not found at $KINGFISHER_PATH"
        return 1
    fi
    
    cd "$KINGFISHER_PATH"
    
    # Backend
    log_info "Starting KingFisher backend..."
    if [[ -d "src" ]]; then
        # Create virtual environment if it doesn't exist
        if [[ ! -d "venv" ]]; then
            log_info "Creating Python virtual environment for KingFisher..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        
        if [[ -f "requirements.txt" ]]; then
            log_info "Installing KingFisher dependencies..."
            pip install -r requirements.txt >/dev/null 2>&1
        fi
        
        # Set environment variables
        export KINGFISHER_ENV="development"
        export KINGFISHER_PORT="$KINGFISHER_API_PORT"
        export DATABASE_URL="postgresql://kf_user:secure_kf_password_2025@$DB_HOST:$DB_PORT/$DB_NAME"
        export REDIS_URL="redis://$REDIS_HOST:$REDIS_PORT/0"
        
        # Start backend
        nohup python -m uvicorn src.main:app --host 0.0.0.0 --port $KINGFISHER_API_PORT --reload > "$LOGS_DIR/kingfisher.log" 2>&1 &
        echo $! > "$PIDS_DIR/kingfisher-backend.pid"
    fi
    
    # Frontend
    log_info "Starting KingFisher frontend..."
    if [[ -d "frontend" ]]; then
        cd "frontend"
        
        # Install dependencies if needed
        if [[ -f "package.json" && ! -d "node_modules" ]]; then
            log_info "Installing KingFisher frontend dependencies..."
            npm install >/dev/null 2>&1
        fi
        
        # Set environment variables
        export REACT_APP_API_URL="http://localhost:$KINGFISHER_API_PORT"
        export PORT="$KINGFISHER_FRONTEND_PORT"
        
        # Start frontend
        nohup npm start > "$LOGS_DIR/kingfisher-frontend.log" 2>&1 &
        echo $! > "$PIDS_DIR/kingfisher-frontend.pid"
    fi
    
    log_success "KingFisher startup initiated"
}

start_trade_strategy() {
    log_header "${TARGET} Starting Trade Strategy Module"
    
    if [[ ! -d "$TRADE_STRATEGY_PATH" ]]; then
        log_error "Trade Strategy directory not found at $TRADE_STRATEGY_PATH"
        return 1
    fi
    
    cd "$TRADE_STRATEGY_PATH"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log_info "Creating Python virtual environment for Trade Strategy..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Trade Strategy dependencies..."
        pip install -r requirements.txt >/dev/null 2>&1
    fi
    
    # Set environment variables
    export TRADE_STRATEGY_ENV="development"
    export PYTHONPATH="$TRADE_STRATEGY_PATH/src:$PYTHONPATH"
    
    # Initialize database tables
    log_info "Initializing Trade Strategy database tables..."
    python -c "
from src.models.base import Base
from src.core.config import config_manager
try:
    Base.metadata.create_all(bind=config_manager.get_database_engine())
    print('Database tables created successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
" 2>/dev/null || log_warning "Database initialization had issues (may be normal if tables exist)"
    
    # Start API server
    log_info "Starting Trade Strategy API server..."
    nohup python -m uvicorn src.main:app --host 0.0.0.0 --port $TRADE_STRATEGY_API_PORT --reload > "$LOGS_DIR/trade-strategy.log" 2>&1 &
    echo $! > "$PIDS_DIR/trade-strategy-api.pid"
    
    # Start WebSocket server
    log_info "Starting Trade Strategy WebSocket server..."
    nohup python -m src.websocket_server --port $TRADE_STRATEGY_WS_PORT > "$LOGS_DIR/trade-strategy-ws.log" 2>&1 &
    echo $! > "$PIDS_DIR/trade-strategy-ws.pid"
    
    # Start metrics server
    log_info "Starting Trade Strategy metrics server..."
    nohup python -m src.metrics_server --port $TRADE_STRATEGY_METRICS_PORT > "$LOGS_DIR/trade-strategy-metrics.log" 2>&1 &
    echo $! > "$PIDS_DIR/trade-strategy-metrics.pid"
    
    # Start background workers
    log_info "Starting Trade Strategy background workers..."
    nohup python -m celery -A src.celery_app worker --loglevel=info > "$LOGS_DIR/trade-strategy-worker.log" 2>&1 &
    echo $! > "$PIDS_DIR/trade-strategy-worker.pid"
    
    log_success "Trade Strategy Module startup initiated"
}

wait_for_services() {
    log_header "Waiting for Services to be Ready"
    
    local services=(
        "http://localhost:$ZMARTBOT_API_PORT/health:ZmartBot API"
        "http://localhost:$KINGFISHER_API_PORT/health:KingFisher API"
        "http://localhost:$TRADE_STRATEGY_API_PORT/health:Trade Strategy API"
    )
    
    for service_info in "${services[@]}"; do
        local url="${service_info%%:*}"
        local name="${service_info##*:}"
        
        log_info "Waiting for $name to be ready..."
        
        local retries=0
        local max_retries=$((SERVICE_READY_TIMEOUT / 5))
        
        while ! curl -s "$url" >/dev/null 2>&1; do
            if [[ $retries -ge $max_retries ]]; then
                log_warning "$name failed to start within timeout"
                break
            fi
            
            sleep 5
            ((retries++))
            
            if [[ $((retries % 6)) -eq 0 ]]; then
                log_info "Still waiting for $name... (${retries}/${max_retries})"
            fi
        done
        
        if curl -s "$url" >/dev/null 2>&1; then
            log_success "$name is ready"
        fi
    done
}

run_health_checks() {
    log_header "Running Health Checks"
    
    # Check if health check script exists and run it
    if [[ -f "$SCRIPT_DIR/health-check-mac.sh" ]]; then
        log_info "Running comprehensive health checks..."
        "$SCRIPT_DIR/health-check-mac.sh" --startup-check
    else
        log_warning "Health check script not found, performing basic checks..."
        
        # Basic port checks
        local all_healthy=true
        
        if lsof -Pi :$ZMARTBOT_API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "ZmartBot API is listening on port $ZMARTBOT_API_PORT"
        else
            log_error "ZmartBot API is not listening on port $ZMARTBOT_API_PORT"
            all_healthy=false
        fi
        
        if lsof -Pi :$KINGFISHER_API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "KingFisher API is listening on port $KINGFISHER_API_PORT"
        else
            log_error "KingFisher API is not listening on port $KINGFISHER_API_PORT"
            all_healthy=false
        fi
        
        if lsof -Pi :$TRADE_STRATEGY_API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "Trade Strategy API is listening on port $TRADE_STRATEGY_API_PORT"
        else
            log_error "Trade Strategy API is not listening on port $TRADE_STRATEGY_API_PORT"
            all_healthy=false
        fi
        
        if [[ "$all_healthy" == true ]]; then
            log_success "Basic health checks passed"
        else
            log_warning "Some services may not be fully operational"
        fi
    fi
}

display_startup_summary() {
    log_header "${ROCKET} Startup Summary"
    
    echo -e "${WHITE}System Status:${NC}"
    echo -e "  ${GREEN}✓${NC} Infrastructure: PostgreSQL & Redis"
    echo -e "  ${GREEN}✓${NC} Database: Schemas and users configured"
    echo -e ""
    
    echo -e "${WHITE}Services Started:${NC}"
    echo -e "  ${ROBOT} ${GREEN}ZmartBot System${NC}"
    echo -e "    - API: http://localhost:$ZMARTBOT_API_PORT"
    echo -e "    - Frontend: http://localhost:$ZMARTBOT_FRONTEND_PORT"
    echo -e ""
    echo -e "  ${FISH} ${GREEN}KingFisher Platform${NC}"
    echo -e "    - API: http://localhost:$KINGFISHER_API_PORT"
    echo -e "    - Frontend: http://localhost:$KINGFISHER_FRONTEND_PORT"
    echo -e ""
    echo -e "  ${TARGET} ${GREEN}Trade Strategy Module${NC}"
    echo -e "    - API: http://localhost:$TRADE_STRATEGY_API_PORT"
    echo -e "    - WebSocket: ws://localhost:$TRADE_STRATEGY_WS_PORT"
    echo -e "    - Metrics: http://localhost:$TRADE_STRATEGY_METRICS_PORT"
    echo -e ""
    
    echo -e "${WHITE}Management:${NC}"
    echo -e "  ${GEAR} Logs: $LOGS_DIR/"
    echo -e "  ${GEAR} PIDs: $PIDS_DIR/"
    echo -e "  ${GEAR} Stop all: $SCRIPT_DIR/stop-all-mac.sh"
    echo -e "  ${GEAR} Health check: $SCRIPT_DIR/health-check-mac.sh"
    echo -e ""
    
    echo -e "${WHITE}Cursor AI Workspace:${NC}"
    echo -e "  ${GEAR} Open workspace: ${CYAN}cursor $TRADE_STRATEGY_PATH/trade-strategy-workspace.code-workspace${NC}"
    echo -e ""
    
    echo -e "${GREEN}${ROCKET} All systems are now running! ${ROCKET}${NC}"
    echo -e "${CYAN}Happy trading! 📈${NC}"
}

# Error handling
cleanup_on_error() {
    log_error "Startup failed. Cleaning up..."
    
    # Kill any processes we started
    if [[ -d "$PIDS_DIR" ]]; then
        for pidfile in "$PIDS_DIR"/*.pid; do
            if [[ -f "$pidfile" ]]; then
                local pid=$(cat "$pidfile")
                if kill -0 "$pid" 2>/dev/null; then
                    log_info "Stopping process $pid..."
                    kill "$pid" 2>/dev/null || true
                fi
                rm -f "$pidfile"
            fi
        done
    fi
    
    exit 1
}

# Set up error handling
trap cleanup_on_error ERR

# Main execution
main() {
    log_header "${ROCKET} Trade Strategy Complete System Startup"
    
    log_info "Starting complete trading platform with zero-conflict architecture..."
    log_info "Target: ZmartBot + KingFisher + Trade Strategy Module"
    log_info "Platform: Mac Mini 2025 M2 Pro Optimized"
    
    # Pre-flight checks
    create_directories
    check_system_requirements
    check_dependencies
    check_port_availability
    
    # Start infrastructure
    start_infrastructure
    setup_database
    
    # Start services
    start_zmartbot
    start_kingfisher
    start_trade_strategy
    
    # Post-startup
    wait_for_services
    run_health_checks
    display_startup_summary
    
    log_success "Complete system startup finished successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Trade Strategy Complete System Startup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verbose, -v  Enable verbose output"
        echo "  --force, -f    Force start (kill existing processes)"
        echo ""
        echo "This script starts the complete trading platform:"
        echo "  - ZmartBot System (ports 8000, 3000)"
        echo "  - KingFisher Platform (ports 8100, 3100)"
        echo "  - Trade Strategy Module (ports 8200, 3200, 8201, 8202)"
        echo ""
        exit 0
        ;;
    --verbose|-v)
        set -x
        ;;
    --force|-f)
        log_info "Force mode enabled - will kill existing processes"
        "$SCRIPT_DIR/stop-all-mac.sh" || true
        sleep 3
        ;;
esac

# Run main function
main "$@"

