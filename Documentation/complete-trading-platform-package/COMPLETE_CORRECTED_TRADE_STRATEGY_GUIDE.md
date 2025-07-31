# Complete Trade Strategy Module - CORRECTED PROFIT CALCULATIONS
## Professional Installation & Implementation Guide

**Version:** 1.0 Professional Edition - CORRECTED CALCULATIONS  
**Compatibility:** Mac Mini 2025 M2 Pro Integration  
**Author:** Manus AI  
**Date:** January 2025

---

## 🎯 CRITICAL CORRECTION NOTICE

**IMPORTANT:** This guide contains the **CORRECTED** profit calculation logic that fixes a fundamental error in the original implementation. 

### ❌ PREVIOUS INCORRECT METHOD:
- Profit calculations based on **initial investment only**
- Example: 100 USDT initial → 75 USDT profit target (75% of 100)

### ✅ CORRECTED METHOD:
- Profit calculations based on **TOTAL INVESTED AMOUNT** across all scaling stages
- Example: 1,500 USDT total invested → 1,125 USDT profit target (75% of 1,500)

This correction ensures that profit targets scale proportionally with position size and reflect the actual capital at risk.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Corrected Profit Calculation Logic](#corrected-profit-calculation-logic)
3. [Architecture & Integration](#architecture--integration)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [API Documentation](#api-documentation)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Maintenance & Monitoring](#maintenance--monitoring)

---

## 🎯 System Overview

The Trade Strategy Module is a sophisticated algorithmic trading system that integrates seamlessly with your existing ZmartBot and KingFisher platforms. It provides:

### Core Features
- **Signal Center**: Aggregates and processes signals from multiple sources
- **Trading Agent**: Makes intelligent trading decisions with advanced risk management
- **Position Scaler**: Manages position scaling with corrected profit calculations
- **Vault Manager**: Handles multiple trading vaults with performance tracking
- **Risk Management**: Advanced risk controls and position limits

### Key Improvements in Corrected Version
- **Accurate Profit Calculations**: Based on total invested amount across all scaling stages
- **Proportional Risk Management**: Risk scales appropriately with position size
- **Realistic Profit Targets**: Profit thresholds reflect actual capital at risk
- **Enhanced Performance Metrics**: True performance tracking based on total investments

---

## 🔧 Corrected Profit Calculation Logic

### Mathematical Foundation

The corrected system calculates profit thresholds based on the **cumulative invested amount** across all scaling stages:

```
Total Invested = Initial Investment + Scale 1 + Scale 2 + Scale 3
Profit Threshold = Total Invested × 75%
Take Profit Trigger = Total Invested + Profit Threshold
```

### Detailed Example

**Position Scaling Sequence:**
```
Stage 1: 100 USDT (1% bankroll, 20X leverage) = 2,000 USDT position
Stage 2: 200 USDT (2% bankroll, 10X leverage) = 2,000 USDT position  
Stage 3: 400 USDT (4% bankroll, 5X leverage)  = 2,000 USDT position
Stage 4: 800 USDT (8% bankroll, 2X leverage)  = 1,600 USDT position

Total Invested: 100 + 200 + 400 + 800 = 1,500 USDT
Total Position Value: 2,000 + 2,000 + 2,000 + 1,600 = 7,600 USDT
```

**CORRECTED Profit Calculation:**
```
Profit Threshold: 1,500 × 0.75 = 1,125 USDT
Take Profit Trigger: 1,500 + 1,125 = 2,625 USDT margin

✅ When margin reaches 2,625 USDT → FIRST TAKE PROFIT TRIGGERED!
```

### Profit Taking Strategy

**Stage 1 - First Take Profit (30%):**
- Trigger: 75% profit on total invested
- Close: 30% of position
- Set: 5% trailing stop on remaining 70%

**Stage 2 - Second Take Profit (25%):**
- Trigger: Trailing stop hit
- Close: 25% of original position (35.7% of remaining)
- Set: 3% trailing stop on remaining 45%

**Stage 3 - Final Take Profit (45%):**
- Trigger: Trailing stop hit or manual close
- Close: Remaining 45% of position
- Result: Complete position closure

---

## 🏗️ Architecture & Integration

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ZmartBot      │    │   KingFisher    │    │ Trade Strategy  │
│   Port: 8000    │    │   Port: 8100    │    │   Port: 8200    │
│   Port: 3000    │    │   Port: 3100    │    │   Port: 3200    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Shared Services │
                    │                 │
                    │ PostgreSQL:5432 │
                    │ Redis:6379      │
                    │ Prometheus:9090 │
                    │ Grafana:3001    │
                    └─────────────────┘
```

### Zero Port Conflicts Design

| Service | Port | System | Status |
|---------|------|--------|---------|
| ZmartBot API | 8000 | Existing | ✅ Unchanged |
| ZmartBot Frontend | 3000 | Existing | ✅ Unchanged |
| KingFisher API | 8100 | Existing | ✅ Unchanged |
| KingFisher Frontend | 3100 | Existing | ✅ Unchanged |
| **Trade Strategy API** | **8200** | **New** | ✅ **No Conflicts** |
| **Trade Strategy Frontend** | **3200** | **New** | ✅ **No Conflicts** |

### Database Schema Isolation

```sql
-- Namespace separation in shared PostgreSQL database
CREATE SCHEMA IF NOT EXISTS zmartbot;      -- ZmartBot tables
CREATE SCHEMA IF NOT EXISTS kingfisher;    -- KingFisher tables  
CREATE SCHEMA IF NOT EXISTS trade_strategy; -- Trade Strategy tables

-- Redis namespace separation
-- ZmartBot:     redis DB 0, prefix "zmart:"
-- KingFisher:   redis DB 1, prefix "kf:"
-- Trade Strategy: redis DB 2, prefix "ts:"
```

---

## 🚀 Installation Guide

### Prerequisites

**System Requirements:**
- macOS (Mac Mini 2025 M2 Pro recommended)
- 16GB RAM (minimum 8GB)
- 100GB free disk space
- Apple Silicon (ARM64) or Intel x64

**Required Software:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install docker docker-compose python@3.11 node@20 postgresql@15 redis
brew install --cask cursor  # Cursor AI IDE
```

### Step 1: Project Setup

```bash
# Navigate to your development directory
cd ~/Development

# Clone or ensure you have the project structure
mkdir -p trading-platform
cd trading-platform

# Your directory structure should look like:
# trading-platform/
# ├── zmartbot/                    # Your existing ZmartBot
# ├── kingfisher-platform/        # Your existing KingFisher  
# └── trade-strategy-module/       # New Trade Strategy module
```

### Step 2: Extract Trade Strategy Module

```bash
# Extract the provided trade-strategy-module files
# Place all files from the corrected package into:
# trading-platform/trade-strategy-module/

# Ensure proper file structure:
trade-strategy-module/
├── src/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── api/
│   └── main.py
├── database/
│   └── schemas/
├── scripts/
├── config/
├── frontend/
├── tests/
└── docker-compose.corrected.yml
```

### Step 3: Install Dependencies

```bash
# Navigate to Trade Strategy module
cd trade-strategy-module

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for frontend
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment

```bash
# Copy and customize configuration
cp config/trade_strategy_corrected.env.example config/trade_strategy_corrected.env

# Edit configuration file
cursor config/trade_strategy_corrected.env

# Key settings to verify:
# PROFIT_THRESHOLD_PERCENTAGE=75
# PROFIT_CALCULATION_METHOD=total_invested_based
# SCALING_BANKROLL_PERCENTAGES=1,2,4,8
# LEVERAGE_SEQUENCE=20,10,5,2
```

### Step 5: Database Setup

```bash
# Start PostgreSQL and Redis
brew services start postgresql@15
brew services start redis

# Create database
createdb trading_platform

# Apply database schema
psql -d trading_platform -f database/schemas/trade_strategy_schema.sql

# Verify corrected configuration is applied
psql -d trading_platform -c "SELECT * FROM system_config WHERE key LIKE 'profit%';"
```

### Step 6: Start All Systems

```bash
# Make startup script executable
chmod +x scripts/start-all-trade-strategy-mac-corrected.sh

# Start all systems with corrected calculations
./scripts/start-all-trade-strategy-mac-corrected.sh
```

### Step 7: Verify Installation

```bash
# Check all services are running
./scripts/health-check-mac.sh

# Test corrected profit calculations
curl "http://localhost:8200/api/v1/trading/status"

# Open Cursor AI workspace
cursor trade-strategy-workspace.code-workspace
```

---

## ⚙️ Configuration

### Core Configuration Files

**1. Trade Strategy Configuration (`config/trade_strategy_corrected.env`)**

```bash
# CORRECTED: Profit Calculation Settings
PROFIT_THRESHOLD_PERCENTAGE=75
PROFIT_CALCULATION_METHOD=total_invested_based
PROFIT_BASE=total_invested_amount
SCALING_BANKROLL_PERCENTAGES=1,2,4,8
LEVERAGE_SEQUENCE=20,10,5,2

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
```

**2. Docker Compose Configuration (`docker-compose.corrected.yml`)**

Key environment variables for Trade Strategy API:
```yaml
environment:
  # CORRECTED: Profit Calculation Settings
  - PROFIT_THRESHOLD_PERCENTAGE=75
  - PROFIT_CALCULATION_METHOD=total_invested_based
  - PROFIT_BASE=total_invested_amount
  - SCALING_BANKROLL_PERCENTAGES=1,2,4,8
  - LEVERAGE_SEQUENCE=20,10,5,2
```

**3. Cursor AI Workspace (`trade-strategy-workspace.code-workspace`)**

```json
{
  "folders": [
    {"name": "ZmartBot", "path": "../zmartbot"},
    {"name": "KingFisher", "path": "../kingfisher-platform"},
    {"name": "Trade Strategy", "path": "."}
  ],
  "settings": {
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.analysis.extraPaths": ["./src"],
    "typescript.preferences.includePackageJsonAutoImports": "auto"
  },
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Start All Systems (CORRECTED)",
        "type": "shell",
        "command": "./scripts/start-all-trade-strategy-mac-corrected.sh",
        "group": "build",
        "presentation": {"echo": true, "reveal": "always"},
        "problemMatcher": []
      }
    ]
  }
}
```

### Environment-Specific Settings

**Development Environment:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
TESTING=true
RATE_LIMIT_PER_MINUTE=1000
```

**Production Environment:**
```bash
DEBUG=false
LOG_LEVEL=INFO
TESTING=false
RATE_LIMIT_PER_MINUTE=100
```

---

## 📚 API Documentation

### Core Endpoints with Corrected Calculations

**1. Trading Analysis**

```http
POST /api/v1/trading/analyze
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "force_analysis": false
}
```

Response with corrected calculations:
```json
{
  "decision": "open_position",
  "symbol": "BTCUSDT",
  "direction": "long",
  "confidence": 0.85,
  "risk_level": "medium",
  "recommended_investment": 100.0,
  "leverage": 20.0,
  "position_value": 2000.0,
  "total_invested_if_executed": 100.0,
  "profit_threshold_75pct": 75.0,
  "take_profit_trigger": 175.0,
  "liquidation_price": 48500.0,
  "reasoning": "Strong bullish signals with high confidence"
}
```

**2. Position Calculations**

```http
GET /api/v1/positions/{position_id}/calculations?current_price=50000
```

Response with corrected calculations:
```json
{
  "position_id": "uuid",
  "calculation_price": 50000.0,
  "investment_breakdown": {
    "total_invested": 1500.0,
    "scaling_stages": [
      {"stage": 1, "investment_amount": 100.0, "leverage": 20.0},
      {"stage": 2, "investment_amount": 200.0, "leverage": 10.0},
      {"stage": 3, "investment_amount": 400.0, "leverage": 5.0},
      {"stage": 4, "investment_amount": 800.0, "leverage": 2.0}
    ]
  },
  "profit_calculations": {
    "profit_threshold_75pct": 1125.0,
    "take_profit_trigger": 2625.0,
    "current_margin": 2800.0,
    "profit_amount": 1300.0,
    "profit_percentage": 86.67
  },
  "calculation_metadata": {
    "method": "corrected_total_invested_based",
    "profit_threshold_method": "75_percent_of_total_invested"
  }
}
```

**3. Position Scaling**

```http
POST /api/v1/positions/{position_id}/scale?current_price=49000&signal_score=0.8
```

Response:
```json
{
  "scaled": true,
  "message": "Position scaled to stage 2",
  "new_stage": 2,
  "scaling_details": {
    "investment_amount": 200.0,
    "leverage": 10.0,
    "trigger_reason": "better_score"
  },
  "updated_calculations": {
    "total_invested": 300.0,
    "profit_threshold_75pct": 225.0,
    "take_profit_trigger": 525.0,
    "liquidation_price": 47500.0
  }
}
```

**4. Profit Taking**

```http
POST /api/v1/positions/{position_id}/take-profit?current_price=52000
```

Response:
```json
{
  "profit_taken": true,
  "message": "First take profit executed",
  "profit_stage": "first_take",
  "profit_details": {
    "amount_closed": 2280.0,
    "profit_realized": 1125.0,
    "profit_percentage": 75.0,
    "remaining_position": 5320.0
  }
}
```

### WebSocket Endpoints

**Real-time Position Updates:**
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8200/ws/positions');

// Listen for corrected calculation updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'position_update') {
    console.log('Updated calculations:', data.corrected_calculations);
  }
};
```

---

## 🧪 Testing & Validation

### Automated Testing

**Run Complete Test Suite:**
```bash
# Navigate to Trade Strategy module
cd trade-strategy-module

# Activate virtual environment
source venv/bin/activate

# Run all tests with corrected calculations
python -m pytest tests/ -v --cov=src --cov-report=html

# Run specific corrected calculation tests
python -m pytest tests/test_position_scaler_corrected.py -v
python -m pytest tests/test_profit_calculations.py -v
```

### Manual Validation

**1. Test Corrected Profit Calculations:**

```bash
# Test position scaling and profit calculations
curl -X POST "http://localhost:8200/api/v1/trading/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'

# Verify response contains corrected calculations:
# - total_invested_if_executed: based on actual investment
# - profit_threshold_75pct: 75% of total invested
# - take_profit_trigger: total_invested + profit_threshold
```

**2. Test Position Scaling:**

```python
# Python test script
import requests

# Create test position
response = requests.post("http://localhost:8200/api/v1/trading/execute", json={
    "symbol": "BTCUSDT",
    "direction": "long",
    "investment_amount": 100,
    "leverage": 20
})

position_id = response.json()["position_id"]

# Scale position multiple times
for stage in range(2, 5):
    scale_response = requests.post(
        f"http://localhost:8200/api/v1/positions/{position_id}/scale",
        params={"current_price": 49000, "signal_score": 0.8}
    )
    
    # Verify corrected calculations
    calculations = scale_response.json()["updated_calculations"]
    print(f"Stage {stage}:")
    print(f"  Total Invested: {calculations['total_invested']}")
    print(f"  Profit Threshold: {calculations['profit_threshold_75pct']}")
    print(f"  Take Profit Trigger: {calculations['take_profit_trigger']}")
```

**3. Validate Profit Taking:**

```bash
# Test profit taking with corrected thresholds
curl -X POST "http://localhost:8200/api/v1/positions/{position_id}/take-profit" \
  -G -d "current_price=52000"

# Verify profit calculations are based on total invested amount
```

### Performance Testing

**Load Testing:**
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8200
```

**Memory and CPU Testing:**
```bash
# Monitor resource usage during testing
top -pid $(pgrep -f "trade-strategy")

# Check memory usage
ps aux | grep trade-strategy

# Monitor API response times
curl -w "@curl-format.txt" -s -o /dev/null "http://localhost:8200/api/v1/trading/status"
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. Incorrect Profit Calculations**

**Problem:** Profit thresholds seem too low or high
```
Expected: 1125 USDT profit threshold for 1500 USDT invested
Actual: 75 USDT profit threshold
```

**Solution:** Verify corrected configuration is loaded
```bash
# Check environment variables
curl "http://localhost:8200/api/v1/config" | grep profit

# Verify database configuration
psql -d trading_platform -c "SELECT * FROM system_config WHERE key = 'profit_calculation_method';"

# Should return: total_invested_based
```

**2. Port Conflicts**

**Problem:** Services fail to start due to port conflicts
```
Error: Port 8200 is already in use
```

**Solution:** Check and stop conflicting services
```bash
# Find process using port
lsof -i :8200

# Stop conflicting process
kill -9 <PID>

# Or use different ports in configuration
```

**3. Database Connection Issues**

**Problem:** Cannot connect to PostgreSQL
```
Error: could not connect to server: Connection refused
```

**Solution:** Ensure PostgreSQL is running and configured
```bash
# Start PostgreSQL
brew services start postgresql@15

# Check connection
pg_isready -h localhost -p 5432

# Create database if missing
createdb trading_platform
```

**4. Redis Connection Issues**

**Problem:** Redis connection failures
```
Error: Redis connection refused
```

**Solution:** Start Redis and check configuration
```bash
# Start Redis
brew services start redis

# Test connection
redis-cli ping

# Should return: PONG
```

**5. Calculation Validation Errors**

**Problem:** Position calculations don't match expected values

**Solution:** Use the validation script
```bash
# Run calculation validation
python scripts/validate_calculations.py

# Check specific position
python scripts/validate_calculations.py --position-id <uuid>
```

### Debug Mode

**Enable Debug Logging:**
```bash
# Set debug environment
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart Trade Strategy API
./scripts/restart-trade-strategy.sh

# Monitor debug logs
tail -f logs/trade-strategy-api.log | grep -i "profit\|calculation"
```

**Debug Specific Calculations:**
```python
# Python debug script
from src.services.position_scaler import PositionScaler
from decimal import Decimal

# Test calculation manually
scaler = PositionScaler(session, redis_client)
result = scaler.calculate_position_metrics(
    position, 
    current_price=Decimal('50000'), 
    vault_bankroll=Decimal('10000')
)

print(f"Total Invested: {result.total_invested}")
print(f"Profit Threshold: {result.profit_threshold_75pct}")
print(f"Take Profit Trigger: {result.first_take_profit_trigger}")
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check-corrected.sh

echo "🔍 Trade Strategy Health Check - CORRECTED CALCULATIONS"

# Check API health
if curl -s -f "http://localhost:8200/health" > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
fi

# Check corrected calculations
response=$(curl -s "http://localhost:8200/api/v1/trading/status")
method=$(echo "$response" | jq -r '.system_health.calculation_method')

if [[ "$method" == "corrected_total_invested_based" ]]; then
    echo "✅ Corrected calculations active"
else
    echo "❌ Incorrect calculation method: $method"
fi

# Check database
if psql -d trading_platform -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Database connection OK"
else
    echo "❌ Database connection failed"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis connection OK"
else
    echo "❌ Redis connection failed"
fi

echo "🎯 Health check complete"
```

---

## ⚡ Performance Optimization

### Mac Mini 2025 M2 Pro Optimizations

**1. CPU Optimization**
```bash
# Utilize all 12 cores of M2 Pro
export WORKER_PROCESSES=8
export CPU_AFFINITY=0-11

# Enable parallel processing
export UVICORN_WORKERS=4
export GUNICORN_WORKERS=8
```

**2. Memory Optimization**
```bash
# Optimize for 16GB unified memory
export MEMORY_LIMIT=4GB
export MAX_CONNECTIONS=100
export CONNECTION_POOL_SIZE=20
```

**3. Storage Optimization**
```bash
# Optimize for SSD performance
export DB_POOL_SIZE=20
export DB_MAX_OVERFLOW=30
export REDIS_MAX_CONNECTIONS=50
```

### Database Performance

**PostgreSQL Optimization:**
```sql
-- Optimize for trading workload
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '8GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Restart PostgreSQL to apply changes
SELECT pg_reload_conf();
```

**Redis Optimization:**
```bash
# Configure Redis for trading data
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Application Performance

**1. Caching Strategy**
```python
# Implement intelligent caching for calculations
@lru_cache(maxsize=1000)
def calculate_position_metrics_cached(position_id, price, timestamp):
    # Cache calculations for 30 seconds
    return calculate_position_metrics(position_id, price)
```

**2. Async Processing**
```python
# Use async for I/O operations
async def process_signals_batch(signals):
    tasks = [process_signal(signal) for signal in signals]
    return await asyncio.gather(*tasks)
```

**3. Connection Pooling**
```python
# Optimize database connections
DATABASE_POOL_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600
}
```

### Monitoring Performance

**1. Prometheus Metrics**
```python
# Custom metrics for corrected calculations
from prometheus_client import Counter, Histogram, Gauge

calculation_time = Histogram('position_calculation_seconds', 
                            'Time spent calculating positions')
profit_calculations = Counter('profit_calculations_total',
                            'Total profit calculations performed')
active_positions = Gauge('active_positions_count',
                        'Number of active positions')
```

**2. Grafana Dashboards**

Key metrics to monitor:
- Position calculation latency
- Profit calculation accuracy
- Memory usage patterns
- CPU utilization
- Database query performance
- Redis hit rates

**3. Performance Alerts**
```yaml
# Grafana alert rules
groups:
  - name: trade_strategy_performance
    rules:
      - alert: HighCalculationLatency
        expr: position_calculation_seconds > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Position calculations taking too long"
          
      - alert: MemoryUsageHigh
        expr: process_resident_memory_bytes > 4e9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Memory usage exceeding 4GB limit"
```

---

## 📊 Maintenance & Monitoring

### Daily Maintenance Tasks

**1. System Health Check**
```bash
# Run daily health check
./scripts/health-check-mac.sh

# Check log files for errors
grep -i error logs/*.log | tail -20

# Monitor disk space
df -h | grep -E "(/$|/var)"
```

**2. Database Maintenance**
```sql
-- Daily database maintenance
VACUUM ANALYZE positions;
VACUUM ANALYZE position_scales;
VACUUM ANALYZE vaults;
VACUUM ANALYZE vault_performance;

-- Check database size
SELECT pg_size_pretty(pg_database_size('trading_platform'));

-- Monitor active connections
SELECT count(*) FROM pg_stat_activity;
```

**3. Performance Monitoring**
```bash
# Check API response times
curl -w "@curl-format.txt" -s -o /dev/null "http://localhost:8200/api/v1/trading/status"

# Monitor memory usage
ps aux | grep -E "(trade-strategy|postgres|redis)" | awk '{print $4, $11}' | sort -nr

# Check CPU usage
top -l 1 | grep -E "CPU usage|trade-strategy"
```

### Weekly Maintenance Tasks

**1. Database Backup**
```bash
# Create weekly backup
./scripts/backup-all-mac.sh

# Verify backup integrity
pg_restore --list backups/trading_platform_$(date +%Y%m%d).backup

# Clean old backups (keep 4 weeks)
find backups/ -name "*.backup" -mtime +28 -delete
```

**2. Log Rotation**
```bash
# Rotate and compress logs
logrotate config/logrotate.conf

# Clean old logs
find logs/ -name "*.log.*" -mtime +7 -delete
```

**3. Performance Analysis**
```bash
# Generate weekly performance report
python scripts/generate_performance_report.py --days 7

# Analyze slow queries
psql -d trading_platform -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Monthly Maintenance Tasks

**1. System Updates**
```bash
# Update system packages
brew update && brew upgrade

# Update Python packages
pip list --outdated
pip install --upgrade -r requirements.txt

# Update Node.js packages
npm audit
npm update
```

**2. Performance Optimization**
```bash
# Analyze and optimize database
python scripts/analyze_database_performance.py

# Review and optimize queries
python scripts/optimize_slow_queries.py

# Update database statistics
psql -d trading_platform -c "ANALYZE;"
```

**3. Security Review**
```bash
# Check for security updates
npm audit --audit-level moderate

# Review API access logs
grep -E "(401|403|429)" logs/trade-strategy-api.log | tail -50

# Update security configurations
./scripts/update_security_config.sh
```

### Monitoring Dashboards

**1. System Overview Dashboard**
- System health status
- Active positions count
- Total invested amounts
- Profit/loss metrics
- API response times

**2. Trading Performance Dashboard**
- Win rate trends
- Profit factor analysis
- Position scaling statistics
- Risk utilization metrics
- Vault performance comparison

**3. Technical Metrics Dashboard**
- CPU and memory usage
- Database performance
- Redis hit rates
- API endpoint latency
- Error rates and alerts

### Alerting Configuration

**Critical Alerts:**
- System down or unresponsive
- Database connection failures
- Memory usage > 90%
- Disk space < 10%
- Position calculation errors

**Warning Alerts:**
- High API latency (> 500ms)
- Memory usage > 75%
- Unusual error rates
- Slow database queries
- Redis connection issues

**Info Alerts:**
- Daily performance summary
- Weekly backup completion
- System update notifications
- New position openings
- Profit taking events

---

## 🎯 Conclusion

This corrected Trade Strategy Module provides a robust, accurate, and scalable algorithmic trading platform that integrates seamlessly with your existing ZmartBot and KingFisher systems. The key improvements include:

### ✅ Corrected Profit Calculations
- **Accurate**: Based on total invested amount across all scaling stages
- **Proportional**: Profit targets scale with position size
- **Realistic**: Reflects actual capital at risk

### ✅ Zero Conflicts Integration
- **Port Isolation**: No conflicts with existing systems
- **Database Separation**: Schema-based isolation
- **Resource Sharing**: Efficient use of shared services

### ✅ Mac Mini 2025 M2 Pro Optimization
- **Apple Silicon Native**: Optimized for ARM64 architecture
- **Memory Efficient**: Designed for 16GB unified memory
- **Performance Tuned**: Utilizes all 12 CPU cores

### ✅ Professional Grade Features
- **Comprehensive API**: Full REST API with WebSocket support
- **Advanced Monitoring**: Prometheus and Grafana integration
- **Robust Testing**: Automated test suite with validation
- **Production Ready**: Docker orchestration and deployment

Your Mac Mini 2025 M2 Pro is now equipped with a professional algorithmic trading platform that provides accurate profit calculations, intelligent risk management, and seamless integration with your existing trading infrastructure.

**🎉 Ready to trade with confidence using corrected calculations! 🎉**

---

**Support & Documentation:**
- API Documentation: http://localhost:8200/docs
- Monitoring: http://localhost:3001 (Grafana)
- Health Check: http://localhost:8200/health
- System Status: http://localhost:8200/api/v1/trading/status

**Contact:**
- Technical Support: [Your Support Channel]
- Documentation: [Your Documentation URL]
- Updates: [Your Update Channel]

