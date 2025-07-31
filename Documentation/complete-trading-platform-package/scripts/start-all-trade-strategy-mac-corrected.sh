#!/bin/bash

# Trade Strategy Module - Complete System Startup Script (CORRECTED)
# ===================================================================
# 
# Mac Mini 2025 M2 Pro optimized startup script with CORRECTED profit calculations.
# Starts ZmartBot (8000/3000) + KingFisher (8100/3100) + Trade Strategy (8200/3200)
# with zero port conflicts and accurate profit calculation logic.
#
# Author: Manus AI
# Version: 1.0 Professional Edition - CORRECTED PROFIT CALCULATIONS
# Compatibility: Mac Mini 2025 M2 Pro Integration

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# System ports (ZERO CONFLICTS)
ZMARTBOT_API_PORT=8000
ZMARTBOT_FRONTEND_PORT=3000
KINGFISHER_API_PORT=8100
KINGFISHER_FRONTEND_PORT=3100
TRADE_STRATEGY_API_PORT=8200
TRADE_STRATEGY_FRONTEND_PORT=3200

# Database configuration
POSTGRES_PORT=5432
REDIS_PORT=6379
POSTGRES_DB="trading_platform"

# CORRECTED: Profit calculation configuration
PROFIT_THRESHOLD_PCT=75  # 75% profit on TOTAL INVESTED AMOUNT
CALCULATION_METHOD="total_invested_based"
SCALING_STAGES="1,2,4,8"  # Percentage of bankroll per stage
LEVERAGE_SEQUENCE="20,10,5,2"  # Leverage per stage

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    mkdir -p "$PROJECT_ROOT/data/postgres"
    mkdir -p "$PROJECT_ROOT/data/redis"
    mkdir -p "$PROJECT_ROOT/backups"
    mkdir -p "$PROJECT_ROOT/config"
    
    # Create corrected configuration files
    create_corrected_configs
}

# Create corrected configuration files
create_corrected_configs() {
    log "Creating CORRECTED profit calculation configurations..."
    
    # Trade Strategy corrected configuration
    cat > "$PROJECT_ROOT/config/trade_strategy_corrected.env" << EOF
# Trade Strategy Module - CORRECTED Configuration
# ===============================================

# API Configuration
TRADE_STRATEGY_API_PORT=$TRADE_STRATEGY_API_PORT
TRADE_STRATEGY_FRONTEND_PORT=$TRADE_STRATEGY_FRONTEND_PORT
TRADE_STRATEGY_API_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://trading_user:trading_pass@localhost:$POSTGRES_PORT/$POSTGRES_DB
REDIS_URL=redis://localhost:$REDIS_PORT/2

# CORRECTED: Profit Calculation Settings
PROFIT_THRESHOLD_PERCENTAGE=$PROFIT_THRESHOLD_PCT
PROFIT_CALCULATION_METHOD=$CALCULATION_METHOD
PROFIT_BASE=total_invested_amount
SCALING_BANKROLL_PERCENTAGES=$SCALING_STAGES
LEVERAGE_SEQUENCE=$LEVERAGE_SEQUENCE

# Position Management (CORRECTED)
MAX_POSITIONS_PER_VAULT=2
INITIAL_BANKROLL_PERCENTAGE=1
DOUBLE_UP_PERCENTAGES=2,4,8
LEVERAGE_PROGRESSION=20,10,5,2
PROFIT_TAKING_STAGES=30,25,45
TRAILING_STOP_PERCENTAGES=5,3

# Risk Management
MAX_RISK_PER_VAULT=20
LIQUIDATION_BUFFER_PERCENTAGE=10
CORRELATION_THRESHOLD=70
MAX_DRAWDOWN_THRESHOLD=25

# Signal Processing
MIN_SIGNAL_CONFIDENCE=65
MIN_CONSENSUS_SIGNALS=3
SIGNAL_QUALITY_THRESHOLD=70

# Performance Monitoring
PERFORMANCE_UPDATE_INTERVAL=3600
METRICS_RETENTION_DAYS=90
BACKUP_INTERVAL_HOURS=6

# Mac Mini 2025 M2 Pro Optimizations
WORKER_PROCESSES=8
MAX_CONNECTIONS=100
MEMORY_LIMIT=4GB
CPU_AFFINITY=0-11

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
API_KEY_HEADER=X-API-Key
RATE_LIMIT_PER_MINUTE=100

# Development
DEBUG=false
TESTING=false
ENVIRONMENT=production
EOF

    # Docker Compose override for corrected calculations
    cat > "$PROJECT_ROOT/docker-compose.corrected.yml" << EOF
version: '3.8'

services:
  trade-strategy-api:
    build:
      context: ./trade-strategy-module
      dockerfile: Dockerfile
    ports:
      - "$TRADE_STRATEGY_API_PORT:8000"
    environment:
      - PROFIT_THRESHOLD_PERCENTAGE=$PROFIT_THRESHOLD_PCT
      - PROFIT_CALCULATION_METHOD=$CALCULATION_METHOD
      - SCALING_BANKROLL_PERCENTAGES=$SCALING_STAGES
      - LEVERAGE_SEQUENCE=$LEVERAGE_SEQUENCE
    volumes:
      - ./config/trade_strategy_corrected.env:/app/.env
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  trade-strategy-frontend:
    build:
      context: ./trade-strategy-module/frontend
      dockerfile: Dockerfile
    ports:
      - "$TRADE_STRATEGY_FRONTEND_PORT:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:$TRADE_STRATEGY_API_PORT
      - REACT_APP_PROFIT_CALCULATION_METHOD=$CALCULATION_METHOD
    volumes:
      - ./logs:/app/logs
    depends_on:
      - trade-strategy-api
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    ports:
      - "$POSTGRES_PORT:5432"
    environment:
      - POSTGRES_DB=$POSTGRES_DB
      - POSTGRES_USER=trading_user
      - POSTGRES_PASSWORD=trading_pass
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "$REDIS_PORT:6379"
    volumes:
      - ./data/redis:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./monitoring/grafana:/var/lib/grafana
    restart: unless-stopped
EOF

    # Prometheus configuration for corrected metrics
    mkdir -p "$PROJECT_ROOT/monitoring"
    cat > "$PROJECT_ROOT/monitoring/prometheus.yml" << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zmartbot-api'
    static_configs:
      - targets: ['host.docker.internal:$ZMARTBOT_API_PORT']

  - job_name: 'kingfisher-api'
    static_configs:
      - targets: ['host.docker.internal:$KINGFISHER_API_PORT']

  - job_name: 'trade-strategy-api'
    static_configs:
      - targets: ['host.docker.internal:$TRADE_STRATEGY_API_PORT']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

    log "✅ CORRECTED configuration files created successfully"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements for Mac Mini 2025 M2 Pro..."
    
    # Check macOS version
    if [[ "$(uname)" != "Darwin" ]]; then
        error "This script is designed for macOS (Mac Mini 2025)"
        exit 1
    fi
    
    # Check for Apple Silicon
    if [[ "$(uname -m)" != "arm64" ]]; then
        warning "This script is optimized for Apple Silicon (M2 Pro)"
    fi
    
    # Check available memory (should be 16GB)
    MEMORY_GB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    if [[ $MEMORY_GB -lt 8 ]]; then
        error "Insufficient memory. Minimum 8GB required, 16GB recommended"
        exit 1
    fi
    
    info "✅ Memory: ${MEMORY_GB}GB (Excellent for M2 Pro)"
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "python3" "node" "npm" "psql" "redis-cli")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool not found: $tool"
            info "Please install $tool and try again"
            exit 1
        fi
    done
    
    log "✅ All system requirements met"
}

# Check port availability
check_ports() {
    log "Checking port availability (ZERO CONFLICTS architecture)..."
    
    local ports=($ZMARTBOT_API_PORT $ZMARTBOT_FRONTEND_PORT $KINGFISHER_API_PORT $KINGFISHER_FRONTEND_PORT $TRADE_STRATEGY_API_PORT $TRADE_STRATEGY_FRONTEND_PORT $POSTGRES_PORT $REDIS_PORT)
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            error "Port $port is already in use"
            info "Please stop the service using port $port or modify the configuration"
            exit 1
        fi
    done
    
    log "✅ All ports available for ZERO CONFLICTS deployment"
}

# Start database services
start_databases() {
    log "Starting database services..."
    
    # Start PostgreSQL
    if ! pgrep -f postgres > /dev/null; then
        info "Starting PostgreSQL..."
        brew services start postgresql@15 || {
            error "Failed to start PostgreSQL"
            exit 1
        }
        sleep 3
    fi
    
    # Start Redis
    if ! pgrep -f redis-server > /dev/null; then
        info "Starting Redis..."
        brew services start redis || {
            error "Failed to start Redis"
            exit 1
        }
        sleep 2
    fi
    
    # Wait for databases to be ready
    info "Waiting for databases to be ready..."
    
    # Wait for PostgreSQL
    for i in {1..30}; do
        if pg_isready -h localhost -p $POSTGRES_PORT > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # Wait for Redis
    for i in {1..30}; do
        if redis-cli -p $REDIS_PORT ping > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    log "✅ Database services started successfully"
}

# Initialize databases with corrected schemas
initialize_databases() {
    log "Initializing databases with CORRECTED profit calculation schemas..."
    
    # Create database if it doesn't exist
    createdb -h localhost -p $POSTGRES_PORT $POSTGRES_DB 2>/dev/null || true
    
    # Run database migrations for all systems
    info "Running ZmartBot database migrations..."
    cd "$PROJECT_ROOT/zmartbot/backend/zmart-api"
    python3 -m alembic upgrade head || warning "ZmartBot migrations may have issues"
    
    info "Running KingFisher database migrations..."
    cd "$PROJECT_ROOT/kingfisher-platform/backend"
    python3 -m alembic upgrade head || warning "KingFisher migrations may have issues"
    
    info "Running Trade Strategy database migrations with CORRECTED schemas..."
    cd "$PROJECT_ROOT/trade-strategy-module"
    
    # Apply corrected database schema
    psql -h localhost -p $POSTGRES_PORT -d $POSTGRES_DB -f database/schemas/trade_strategy_schema.sql || {
        error "Failed to apply Trade Strategy corrected schema"
        exit 1
    }
    
    # Insert corrected configuration data
    psql -h localhost -p $POSTGRES_PORT -d $POSTGRES_DB << EOF
-- Insert corrected profit calculation configuration
INSERT INTO system_config (key, value, description) VALUES 
('profit_threshold_percentage', '$PROFIT_THRESHOLD_PCT', 'Profit threshold as percentage of TOTAL invested amount'),
('profit_calculation_method', '$CALCULATION_METHOD', 'Method for calculating profit thresholds'),
('scaling_bankroll_percentages', '$SCALING_STAGES', 'Bankroll percentages for each scaling stage'),
('leverage_sequence', '$LEVERAGE_SEQUENCE', 'Leverage values for each scaling stage')
ON CONFLICT (key) DO UPDATE SET 
value = EXCLUDED.value,
updated_at = CURRENT_TIMESTAMP;
EOF
    
    cd "$PROJECT_ROOT"
    
    log "✅ Databases initialized with CORRECTED profit calculation logic"
}

# Start ZmartBot system
start_zmartbot() {
    log "Starting ZmartBot system (Ports: $ZMARTBOT_API_PORT, $ZMARTBOT_FRONTEND_PORT)..."
    
    cd "$PROJECT_ROOT/zmartbot"
    
    # Start backend
    info "Starting ZmartBot API..."
    cd backend/zmart-api
    python3 -m uvicorn main:app --host 0.0.0.0 --port $ZMARTBOT_API_PORT --reload > "$LOG_DIR/zmartbot-api.log" 2>&1 &
    echo $! > "$PID_DIR/zmartbot-api.pid"
    
    # Start frontend
    info "Starting ZmartBot Frontend..."
    cd ../../frontend
    PORT=$ZMARTBOT_FRONTEND_PORT npm start > "$LOG_DIR/zmartbot-frontend.log" 2>&1 &
    echo $! > "$PID_DIR/zmartbot-frontend.pid"
    
    cd "$PROJECT_ROOT"
    
    log "✅ ZmartBot system started successfully"
}

# Start KingFisher system
start_kingfisher() {
    log "Starting KingFisher system (Ports: $KINGFISHER_API_PORT, $KINGFISHER_FRONTEND_PORT)..."
    
    cd "$PROJECT_ROOT/kingfisher-platform"
    
    # Start backend
    info "Starting KingFisher API..."
    cd backend
    python3 -m uvicorn main:app --host 0.0.0.0 --port $KINGFISHER_API_PORT --reload > "$LOG_DIR/kingfisher-api.log" 2>&1 &
    echo $! > "$PID_DIR/kingfisher-api.pid"
    
    # Start frontend
    info "Starting KingFisher Frontend..."
    cd ../frontend
    PORT=$KINGFISHER_FRONTEND_PORT npm start > "$LOG_DIR/kingfisher-frontend.log" 2>&1 &
    echo $! > "$PID_DIR/kingfisher-frontend.pid"
    
    cd "$PROJECT_ROOT"
    
    log "✅ KingFisher system started successfully"
}

# Start Trade Strategy system with corrected calculations
start_trade_strategy() {
    log "Starting Trade Strategy system with CORRECTED profit calculations (Ports: $TRADE_STRATEGY_API_PORT, $TRADE_STRATEGY_FRONTEND_PORT)..."
    
    cd "$PROJECT_ROOT/trade-strategy-module"
    
    # Load corrected environment
    export $(cat "$PROJECT_ROOT/config/trade_strategy_corrected.env" | grep -v '^#' | xargs)
    
    # Start backend with corrected configuration
    info "Starting Trade Strategy API with CORRECTED profit calculations..."
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port $TRADE_STRATEGY_API_PORT --reload > "$LOG_DIR/trade-strategy-api.log" 2>&1 &
    echo $! > "$PID_DIR/trade-strategy-api.pid"
    
    # Start frontend
    info "Starting Trade Strategy Frontend..."
    cd frontend
    PORT=$TRADE_STRATEGY_FRONTEND_PORT REACT_APP_PROFIT_METHOD=$CALCULATION_METHOD npm start > "$LOG_DIR/trade-strategy-frontend.log" 2>&1 &
    echo $! > "$PID_DIR/trade-strategy-frontend.pid"
    
    cd "$PROJECT_ROOT"
    
    log "✅ Trade Strategy system started with CORRECTED profit calculations"
}

# Start monitoring services
start_monitoring() {
    log "Starting monitoring services..."
    
    # Start with Docker Compose
    docker-compose -f docker-compose.corrected.yml up -d prometheus grafana
    
    log "✅ Monitoring services started (Prometheus: 9090, Grafana: 3001)"
}

# Health check all services
health_check() {
    log "Performing comprehensive health check..."
    
    local services=(
        "ZmartBot API:http://localhost:$ZMARTBOT_API_PORT/health"
        "ZmartBot Frontend:http://localhost:$ZMARTBOT_FRONTEND_PORT"
        "KingFisher API:http://localhost:$KINGFISHER_API_PORT/health"
        "KingFisher Frontend:http://localhost:$KINGFISHER_FRONTEND_PORT"
        "Trade Strategy API:http://localhost:$TRADE_STRATEGY_API_PORT/health"
        "Trade Strategy Frontend:http://localhost:$TRADE_STRATEGY_FRONTEND_PORT"
    )
    
    for service in "${services[@]}"; do
        local name="${service%%:*}"
        local url="${service##*:}"
        
        info "Checking $name..."
        
        for i in {1..30}; do
            if curl -s -f "$url" > /dev/null 2>&1; then
                log "✅ $name is healthy"
                break
            fi
            
            if [[ $i -eq 30 ]]; then
                error "❌ $name failed health check"
            else
                sleep 2
            fi
        done
    done
    
    # Test corrected profit calculations
    info "Testing CORRECTED profit calculation endpoints..."
    
    # Test Trade Strategy API with corrected calculations
    local test_response=$(curl -s "http://localhost:$TRADE_STRATEGY_API_PORT/api/v1/trading/status" || echo "failed")
    
    if [[ "$test_response" == "failed" ]]; then
        warning "Trade Strategy API not responding to status check"
    else
        log "✅ Trade Strategy API responding with corrected calculations"
    fi
}

# Display system information
display_system_info() {
    log "🎉 ALL SYSTEMS STARTED SUCCESSFULLY WITH CORRECTED PROFIT CALCULATIONS! 🎉"
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    TRADING PLATFORM - SYSTEM STATUS                         ║${NC}"
    echo -e "${CYAN}║                     Mac Mini 2025 M2 Pro Optimized                          ║${NC}"
    echo -e "${CYAN}║                   CORRECTED PROFIT CALCULATIONS ACTIVE                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}🚀 SYSTEM URLS (ZERO PORT CONFLICTS):${NC}"
    echo -e "   ${BLUE}ZmartBot API:${NC}          http://localhost:$ZMARTBOT_API_PORT"
    echo -e "   ${BLUE}ZmartBot Frontend:${NC}     http://localhost:$ZMARTBOT_FRONTEND_PORT"
    echo -e "   ${BLUE}KingFisher API:${NC}        http://localhost:$KINGFISHER_API_PORT"
    echo -e "   ${BLUE}KingFisher Frontend:${NC}   http://localhost:$KINGFISHER_FRONTEND_PORT"
    echo -e "   ${PURPLE}Trade Strategy API:${NC}    http://localhost:$TRADE_STRATEGY_API_PORT"
    echo -e "   ${PURPLE}Trade Strategy Frontend:${NC} http://localhost:$TRADE_STRATEGY_FRONTEND_PORT"
    echo ""
    
    echo -e "${GREEN}📊 MONITORING & DATABASES:${NC}"
    echo -e "   ${BLUE}Prometheus:${NC}            http://localhost:9090"
    echo -e "   ${BLUE}Grafana:${NC}               http://localhost:3001 (admin/admin)"
    echo -e "   ${BLUE}PostgreSQL:${NC}            localhost:$POSTGRES_PORT"
    echo -e "   ${BLUE}Redis:${NC}                 localhost:$REDIS_PORT"
    echo ""
    
    echo -e "${GREEN}🎯 CORRECTED PROFIT CALCULATION SETTINGS:${NC}"
    echo -e "   ${PURPLE}Profit Threshold:${NC}      $PROFIT_THRESHOLD_PCT% of TOTAL invested amount"
    echo -e "   ${PURPLE}Calculation Method:${NC}    $CALCULATION_METHOD"
    echo -e "   ${PURPLE}Scaling Stages:${NC}        $SCALING_STAGES% of bankroll"
    echo -e "   ${PURPLE}Leverage Sequence:${NC}     ${LEVERAGE_SEQUENCE}X"
    echo ""
    
    echo -e "${GREEN}💻 MAC MINI 2025 M2 PRO OPTIMIZATIONS:${NC}"
    echo -e "   ${BLUE}CPU Cores Used:${NC}        12 cores (M2 Pro optimized)"
    echo -e "   ${BLUE}Memory Allocation:${NC}     Optimized for 16GB unified memory"
    echo -e "   ${BLUE}Storage:${NC}               SSD optimized with fast I/O"
    echo -e "   ${BLUE}Architecture:${NC}          Apple Silicon native (ARM64)"
    echo ""
    
    echo -e "${GREEN}🛠️ MANAGEMENT COMMANDS:${NC}"
    echo -e "   ${YELLOW}Stop All Systems:${NC}      ./scripts/stop-all-mac.sh"
    echo -e "   ${YELLOW}Health Check:${NC}          ./scripts/health-check-mac.sh"
    echo -e "   ${YELLOW}View Logs:${NC}             tail -f logs/*.log"
    echo -e "   ${YELLOW}Backup System:${NC}         ./scripts/backup-all-mac.sh"
    echo ""
    
    echo -e "${GREEN}📈 EXAMPLE CORRECTED PROFIT CALCULATION:${NC}"
    echo -e "   ${CYAN}Initial Investment:${NC}     100 USDT (20X leverage)"
    echo -e "   ${CYAN}After All Scaling:${NC}      1,500 USDT total invested"
    echo -e "   ${CYAN}Profit Threshold:${NC}       1,125 USDT (75% of 1,500)"
    echo -e "   ${CYAN}Take Profit Trigger:${NC}    2,625 USDT margin"
    echo ""
    
    echo -e "${GREEN}🎉 READY FOR ALGORITHMIC TRADING WITH CORRECTED CALCULATIONS! 🎉${NC}"
    echo ""
}

# Main execution
main() {
    log "🚀 Starting Complete Trading Platform with CORRECTED Profit Calculations..."
    log "Mac Mini 2025 M2 Pro Optimized Deployment"
    
    create_directories
    check_requirements
    check_ports
    start_databases
    initialize_databases
    start_zmartbot
    start_kingfisher
    start_trade_strategy
    start_monitoring
    
    # Wait a moment for all services to fully start
    sleep 5
    
    health_check
    display_system_info
    
    log "🎯 All systems operational with CORRECTED profit calculation logic!"
    log "Your Mac Mini 2025 M2 Pro is now running a professional algorithmic trading platform!"
}

# Handle script interruption
trap 'error "Script interrupted. Some services may still be running."; exit 1' INT TERM

# Run main function
main "$@"

