# Cursor AI Quick Start Guide
## Trade Strategy Module with Corrected Profit Calculations

**⚡ FASTEST WAY TO GET STARTED WITH CURSOR AI ⚡**

---

## 🚀 1-Minute Setup

### Step 1: Extract & Navigate
```bash
cd ~/Development/trading-platform
unzip trade-strategy-complete-package.zip
cd trade-strategy-module
```

### Step 2: Open in Cursor AI
```bash
cursor trade-strategy-workspace.code-workspace
```

### Step 3: Start Everything
**Press `Cmd+Shift+S` in Cursor AI** or run:
```bash
chmod +x scripts/start-all-trade-strategy-mac-corrected.sh
./scripts/start-all-trade-strategy-mac-corrected.sh
```

### Step 4: Verify Success
Open these URLs:
- **Trade Strategy**: http://localhost:8200/docs
- **System Status**: http://localhost:8200/api/v1/trading/status
- **Monitoring**: http://localhost:3001

**🎉 DONE! Your corrected trading system is running!**

---

## ⌨️ Cursor AI Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+S` | Start All Systems (CORRECTED) |
| `Cmd+Shift+T` | Start Trade Strategy Only |
| `Cmd+Shift+R` | Run Corrected Tests |
| `Cmd+Shift+H` | Health Check All |
| `Cmd+Shift+X` | Stop All Systems |

---

## 🎯 Cursor AI Tasks Menu

**Access via:** `Cmd+Shift+P` → "Tasks: Run Task"

1. **Start All Systems (CORRECTED)**
   - Starts ZmartBot + KingFisher + Trade Strategy
   - Zero port conflicts: 8000/3000, 8100/3100, 8200/3200

2. **Validate Corrected Calculations**
   - Tests profit calculation logic
   - Ensures 75% profit on TOTAL invested amount

3. **Database Setup & Migration**
   - Creates database schema
   - Applies corrected configuration

4. **System Health Check**
   - Verifies all services running
   - Confirms corrected calculations active

---

## 🔧 Cursor AI Features Enabled

### AI Code Completion
- **Trading Logic**: Intelligent suggestions for position scaling
- **API Endpoints**: Auto-completion for FastAPI routes
- **Database Queries**: Smart SQL query assistance
- **Configuration**: Environment variable suggestions

### Integrated Debugging
- **Breakpoints**: Set breakpoints in trading logic
- **Variable Inspection**: Inspect profit calculations in real-time
- **Step Debugging**: Step through position scaling logic
- **Call Stack**: Trace trading decision flow

### Database Integration
- **PostgreSQL Connection**: Direct database access from Cursor
- **Query Execution**: Run SQL queries in integrated terminal
- **Schema Visualization**: View database structure
- **Data Inspection**: Browse trading data

### Multi-Root Workspace
- **ZmartBot**: Your existing system (unchanged)
- **KingFisher**: Your existing system (unchanged)
- **Trade Strategy**: New module with corrected calculations

---

## 📊 Instant Validation

### Test Corrected Calculations
```bash
# In Cursor AI terminal (Cmd+`)
curl "http://localhost:8200/api/v1/trading/status" | jq '.system_health.calculation_method'

# Should return: "corrected_total_invested_based"
```

### Example Position Test
```bash
# Test position with corrected calculations
curl -X POST "http://localhost:8200/api/v1/trading/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'

# Verify response contains:
# - total_invested_if_executed: actual investment amount
# - profit_threshold_75pct: 75% of total invested
# - take_profit_trigger: total_invested + profit_threshold
```

---

## 🎯 Key Corrected Features

### ✅ Profit Calculation Fix
**OLD (Incorrect):**
```
100 USDT initial → 75 USDT profit target (always)
Even after 1500 USDT total invested → still 75 USDT target ❌
```

**NEW (Corrected):**
```
100 USDT initial → 75 USDT profit target
1500 USDT total invested → 1125 USDT profit target ✅
```

### ✅ Zero Port Conflicts
- **ZmartBot**: Ports 8000, 3000 (unchanged)
- **KingFisher**: Ports 8100, 3100 (unchanged)
- **Trade Strategy**: Ports 8200, 3200 (new, no conflicts)

### ✅ Mac Mini 2025 M2 Pro Optimized
- **Apple Silicon**: Native ARM64 performance
- **12-Core CPU**: Utilizes all M2 Pro cores
- **16GB Memory**: Optimized for unified memory architecture

---

## 🔍 Cursor AI Development Workflow

### 1. Code with AI Assistance
- Open any `.py` file in `src/`
- Start typing trading logic
- Cursor AI provides intelligent completions
- Accept suggestions with `Tab`

### 2. Debug with Integrated Tools
- Set breakpoints in trading logic
- Press `F5` to start debugging
- Step through profit calculations
- Inspect variables in real-time

### 3. Test with Integrated Terminal
- Press `Cmd+`` to open terminal
- Run tests: `python -m pytest tests/ -v`
- Check API: `curl localhost:8200/health`
- Monitor logs: `tail -f logs/*.log`

### 4. Database Operations
- Use integrated PostgreSQL connection
- Run queries directly in Cursor
- Inspect trading data
- Monitor performance

---

## 📈 Monitoring in Cursor AI

### Built-in Monitoring URLs
- **API Documentation**: http://localhost:8200/docs
- **System Health**: http://localhost:8200/health
- **Trading Status**: http://localhost:8200/api/v1/trading/status
- **Grafana Dashboard**: http://localhost:3001
- **Prometheus Metrics**: http://localhost:9090

### Log Monitoring
```bash
# In Cursor AI terminal
tail -f logs/trade-strategy-api.log | grep -i "profit\|calculation"
```

### Real-time Testing
```bash
# Test corrected calculations in real-time
watch -n 5 'curl -s "http://localhost:8200/api/v1/trading/status" | jq ".trading_status"'
```

---

## 🆘 Quick Troubleshooting

### Issue: Services Won't Start
```bash
# Check ports
lsof -i :8200 :3200

# Kill conflicting processes
kill -9 <PID>

# Restart
./scripts/start-all-trade-strategy-mac-corrected.sh
```

### Issue: Database Connection Failed
```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb trading_platform

# Apply schema
psql -d trading_platform -f database/schemas/trade_strategy_schema.sql
```

### Issue: Incorrect Calculations
```bash
# Verify corrected method is active
curl "http://localhost:8200/api/v1/trading/status" | jq '.system_health.calculation_method'

# Should return: "corrected_total_invested_based"
```

---

## 🎉 Success Indicators

### ✅ All Systems Running
```bash
curl http://localhost:8000/health  # ZmartBot
curl http://localhost:8100/health  # KingFisher  
curl http://localhost:8200/health  # Trade Strategy
```

### ✅ Corrected Calculations Active
```bash
curl "http://localhost:8200/api/v1/trading/status" | jq '.system_health.calculation_method'
# Returns: "corrected_total_invested_based"
```

### ✅ Zero Port Conflicts
```bash
netstat -an | grep LISTEN | grep -E "(8000|3000|8100|3100|8200|3200)"
# Should show all 6 ports listening
```

### ✅ Cursor AI Integration Working
- Workspace opens with all three projects
- AI completions work in trading files
- Debugging works with breakpoints
- Tasks menu shows all configured tasks

---

## 🚀 Next Steps

1. **Explore the API**: http://localhost:8200/docs
2. **Run Tests**: `python -m pytest tests/ -v`
3. **Monitor Performance**: http://localhost:3001
4. **Read Full Guide**: `COMPLETE_CORRECTED_TRADE_STRATEGY_GUIDE.md`
5. **Start Trading**: Use the corrected profit calculation system!

**🎯 Your Mac Mini 2025 M2 Pro is now running a professional algorithmic trading platform with mathematically correct profit calculations!**

