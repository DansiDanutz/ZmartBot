# Trade Strategy Module - Cursor AI Deployment Guide
## Complete Package with Corrected Profit Calculations

**🎯 CRITICAL:** This package contains the **CORRECTED** profit calculation logic that fixes the fundamental error in the original implementation.

---

## 📦 Package Contents

This ZIP package contains everything you need to add the Trade Strategy module to your existing Cursor AI project:

```
trade-strategy-complete-package/
├── README_CURSOR_AI_DEPLOYMENT.md          # This file - START HERE
├── COMPLETE_CORRECTED_TRADE_STRATEGY_GUIDE.md  # 200+ page comprehensive guide
├── CORRECTED_PROFIT_CALCULATION_EXAMPLES.md    # Detailed calculation examples
├── COMPLETE_INSTALLATION_GUIDE.md              # Original installation guide
├── 
├── src/                                     # Core application code
│   ├── core/
│   │   └── config.py                       # Configuration management
│   ├── models/
│   │   └── base.py                         # Database models
│   ├── services/
│   │   ├── signal_center.py                # Signal processing (CORRECTED)
│   │   ├── position_scaler.py              # Position scaling (CORRECTED)
│   │   ├── trading_agent.py                # Trading decisions (CORRECTED)
│   │   └── vault_manager.py                # Vault management (CORRECTED)
│   ├── api/
│   │   ├── positions.py                    # Position API (CORRECTED)
│   │   └── trading.py                      # Trading API (CORRECTED)
│   └── main.py                             # FastAPI application
├── 
├── database/
│   └── schemas/
│       └── trade_strategy_schema.sql       # Database schema
├── 
├── scripts/
│   ├── start-all-trade-strategy-mac-corrected.sh  # Mac startup script
│   ├── stop-all-mac.sh                     # Stop script
│   └── health-check-mac.sh                 # Health check script
├── 
├── config/
│   └── trade_strategy_corrected.env        # Environment configuration
├── 
├── tests/
│   └── test_position_scaler_corrected.py   # Corrected calculation tests
├── 
├── docker-compose.corrected.yml            # Docker orchestration
├── trade-strategy-workspace.code-workspace # Cursor AI workspace
├── .vscode/
│   └── settings.json                       # VS Code settings
├── 
├── requirements.txt                        # Python dependencies
└── Dockerfile                              # Docker configuration
```

---

## 🚀 Quick Start for Cursor AI

### Step 1: Extract to Your Project
```bash
# Navigate to your main project directory
cd ~/Development/trading-platform

# Extract this package
unzip trade-strategy-complete-package.zip

# Your structure should now be:
# trading-platform/
# ├── zmartbot/                    # Your existing ZmartBot
# ├── kingfisher-platform/        # Your existing KingFisher
# └── trade-strategy-module/       # New Trade Strategy module (this package)
```

### Step 2: Open in Cursor AI
```bash
# Open the complete workspace in Cursor AI
cursor trade-strategy-module/trade-strategy-workspace.code-workspace
```

### Step 3: One-Command Setup
```bash
# Make startup script executable
chmod +x trade-strategy-module/scripts/start-all-trade-strategy-mac-corrected.sh

# Start everything with corrected calculations
./trade-strategy-module/scripts/start-all-trade-strategy-mac-corrected.sh
```

---

## 🎯 Key Features of This Package

### ✅ Corrected Profit Calculations
- **Fixed Logic**: Profit calculations based on TOTAL invested amount
- **Accurate Thresholds**: 75% profit on cumulative investments
- **Proportional Scaling**: Profit targets scale with position size

### ✅ Zero Port Conflicts
- **ZmartBot**: 8000/3000 (unchanged)
- **KingFisher**: 8100/3100 (unchanged)
- **Trade Strategy**: 8200/3200 (new, no conflicts)

### ✅ Mac Mini 2025 M2 Pro Optimized
- **Apple Silicon Native**: ARM64 optimized
- **Memory Efficient**: 16GB RAM optimized
- **Performance Tuned**: 12-core CPU utilization

### ✅ Cursor AI Integration
- **Complete Workspace**: Multi-root workspace configuration
- **AI-Powered Development**: Optimized for Cursor AI features
- **Keyboard Shortcuts**: Cmd+Shift+S to start all systems
- **Integrated Debugging**: Full debugging setup for all systems

---

## 📋 Cursor AI Tasks & Shortcuts

### Pre-configured Tasks (Cmd+Shift+P → "Tasks: Run Task")

1. **Start All Systems (CORRECTED)** - `Cmd+Shift+S`
   - Starts ZmartBot + KingFisher + Trade Strategy
   - Uses corrected profit calculation settings
   - Zero port conflicts guaranteed

2. **Start Trade Strategy Only** - `Cmd+Shift+T`
   - Starts only the Trade Strategy module
   - Useful for development and testing

3. **Run Corrected Calculation Tests** - `Cmd+Shift+R`
   - Runs comprehensive test suite
   - Validates corrected profit calculations

4. **Health Check All Systems** - `Cmd+Shift+H`
   - Checks health of all services
   - Validates corrected calculations are active

5. **Stop All Systems** - `Cmd+Shift+X`
   - Gracefully stops all services
   - Saves state and logs

### Cursor AI Specific Features

**AI Code Completion:**
- Optimized for FastAPI and trading logic
- Custom snippets for position scaling
- Intelligent suggestions for profit calculations

**Integrated Debugging:**
- Breakpoints in trading logic
- Variable inspection for calculations
- Step-through debugging for position scaling

**Database Integration:**
- PostgreSQL connection configured
- Query execution and inspection
- Schema visualization

---

## 🔧 Configuration for Cursor AI

### Environment Setup
The package includes pre-configured environment files:

**`config/trade_strategy_corrected.env`:**
```bash
# CORRECTED: Profit Calculation Settings
PROFIT_THRESHOLD_PERCENTAGE=75
PROFIT_CALCULATION_METHOD=total_invested_based
SCALING_BANKROLL_PERCENTAGES=1,2,4,8
LEVERAGE_SEQUENCE=20,10,5,2
```

### Workspace Configuration
**`trade-strategy-workspace.code-workspace`:**
- Multi-root workspace for all three systems
- Integrated terminal profiles
- Custom debugging configurations
- AI-optimized settings

### VS Code Settings
**`.vscode/settings.json`:**
- Python interpreter configuration
- Code formatting and linting
- AI completion settings
- Database connection settings

---

## 🧪 Testing & Validation

### Automated Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run corrected calculation tests specifically
python -m pytest tests/test_position_scaler_corrected.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Manual Validation
```bash
# Test corrected profit calculations
curl "http://localhost:8200/api/v1/trading/status"

# Verify calculation method
curl "http://localhost:8200/api/v1/positions/summary/all" | jq '.calculation_metadata'
```

---

## 📊 Monitoring & Debugging

### Built-in Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **API Docs**: http://localhost:8200/docs

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart with debug mode
./scripts/start-all-trade-strategy-mac-corrected.sh
```

### Log Monitoring
```bash
# Monitor all logs
tail -f logs/*.log

# Monitor specific service
tail -f logs/trade-strategy-api.log

# Search for calculation logs
grep -i "profit\|calculation" logs/trade-strategy-api.log
```

---

## 🎯 Example Corrected Calculation

### Your Position Scaling Example:
```
Initial Investment: 100 USDT (20X leverage)
Scale 1: +200 USDT (10X leverage)  
Scale 2: +400 USDT (5X leverage)
Scale 3: +800 USDT (2X leverage)

Total Invested: 100 + 200 + 400 + 800 = 1,500 USDT
Profit Threshold: 1,500 × 75% = 1,125 USDT
Take Profit Trigger: 1,500 + 1,125 = 2,625 USDT margin

✅ When margin reaches 2,625 USDT → FIRST TAKE PROFIT TRIGGERED!
```

This is now correctly implemented throughout the entire system.

---

## 🆘 Troubleshooting

### Common Issues

**1. Port Conflicts**
```bash
# Check ports
lsof -i :8200
lsof -i :3200

# Kill conflicting processes if needed
kill -9 <PID>
```

**2. Database Issues**
```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb trading_platform
```

**3. Calculation Validation**
```bash
# Verify corrected calculations are active
curl "http://localhost:8200/api/v1/trading/status" | jq '.system_health.calculation_method'

# Should return: "corrected_total_invested_based"
```

### Getting Help

1. **Check the comprehensive guide**: `COMPLETE_CORRECTED_TRADE_STRATEGY_GUIDE.md`
2. **Review calculation examples**: `CORRECTED_PROFIT_CALCULATION_EXAMPLES.md`
3. **Run health check**: `./scripts/health-check-mac.sh`
4. **Check logs**: `tail -f logs/*.log`

---

## 🎉 Ready to Trade!

Your Mac Mini 2025 M2 Pro is now equipped with a professional algorithmic trading platform featuring:

- ✅ **Corrected Profit Calculations** based on total invested amounts
- ✅ **Zero Port Conflicts** with existing systems
- ✅ **Apple Silicon Optimization** for maximum performance
- ✅ **Cursor AI Integration** for seamless development
- ✅ **Professional Monitoring** with Prometheus and Grafana
- ✅ **Comprehensive Testing** to ensure accuracy

**Start trading with confidence using mathematically sound profit calculations!**

---

**Quick Commands:**
- **Start Everything**: `./scripts/start-all-trade-strategy-mac-corrected.sh`
- **Open Cursor AI**: `cursor trade-strategy-workspace.code-workspace`
- **Health Check**: `./scripts/health-check-mac.sh`
- **Stop Everything**: `./scripts/stop-all-mac.sh`

**System URLs:**
- **Trade Strategy API**: http://localhost:8200
- **Trade Strategy Frontend**: http://localhost:3200
- **API Documentation**: http://localhost:8200/docs
- **Monitoring**: http://localhost:3001

