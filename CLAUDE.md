# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

ZmartBot is an enterprise-grade cryptocurrency trading platform with multi-agent architecture, combining multiple data sources for automated trading decisions.

## 🎯 **CRITICAL: OFFICIAL PROFESSIONAL DASHBOARD ARCHITECTURE**

### **THE SINGLE OFFICIAL BACKEND AND FRONTEND**

**OFFICIAL Structure (THE ONLY ONE TO USE):**
```
/Users/dansidanutz/Desktop/ZmartBot/project/
├── backend/api/                         ← 🚀 OFFICIAL BACKEND (ONLY ONE)
│   ├── src/main.py                      ← Backend API (Port 8000)
│   ├── professional_dashboard_server.py ← Dashboard Server (Port 3400)
│   ├── src/routes/                      ← All API routes
│   ├── src/services/                    ← Business logic
│   ├── src/agents/                      ← Multi-agent system
│   ├── venv/                            ← Python environment
│   └── requirements.txt                 ← Dependencies
│
├── frontend/dashboard/                  ← 🎨 OFFICIAL FRONTEND (ONLY ONE)
│   ├── App.jsx                          ← Main React app with routing
│   ├── components/
│   │   ├── RealTimeLiveAlerts.jsx       ← Live Alerts system
│   │   ├── RealTimeLiveAlerts.css       ← Live Alerts styling
│   │   ├── SymbolsManager.jsx           ← Symbol management
│   │   └── Sidebar.jsx                  ← Navigation
│   ├── dist/                            ← Compiled React app
│   ├── package.json                     ← React dependencies
│   └── vite.config.js                   ← Build configuration
│
└── modules/                             ← Specialized modules (separate)
    ├── alerts/                          ← Alerts module
    ├── kingfisher/                      ← KingFisher module
    └── cryptoverse/                     ← Cryptoverse module
```

**How The System Works:**
1. **🚀 OFFICIAL Backend API (Port 8000)**
   - File: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/main.py`
   - FastAPI server for ALL API operations
   - Handles trading logic, RiskMetric, KuCoin/Binance APIs
   - Provides `/api/v1/` endpoints

2. **🖥️ OFFICIAL Dashboard Server (Port 3400)**
   - File: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/professional_dashboard_server.py`
   - Serves compiled React from `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/dist/`
   - Acts as proxy between frontend and backend
   - Handles static files (CSS, JS, images)

3. **🎨 OFFICIAL React Frontend**
   - Location: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/`
   - Dark "Zmart Trading" dashboard UI with Live Alerts
   - Makes API calls to Python backend
   - Built with Vite into `dist/` folder

## 🚀 **ONE-COMMAND STARTUP - FOREVER SOLUTION**

**THE ONLY COMMAND YOU EVER NEED:**
```bash
/Users/dansidanutz/Desktop/ZmartBot/START_ZMARTBOT.sh
```

**🎯 This single script does EVERYTHING:**
- ✅ Navigates to correct directory
- ✅ Activates virtual environment  
- ✅ Installs/verifies ALL dependencies
- ✅ Cleans up old processes
- ✅ Starts Backend API (Port 8000)
- ✅ Starts Dashboard Server (Port 3400)  
- ✅ Waits for services to be ready
- ✅ Runs complete health checks
- ✅ Shows all access URLs
- ✅ Creates process PID files for management

**FOR CLAUDE CODE SESSIONS:**
```bash
# Just run this one command:
/Users/dansidanutz/Desktop/ZmartBot/START_ZMARTBOT.sh
```

**ALTERNATIVE METHODS (if needed):**

**Method 2: Manual Step-by-Step (For troubleshooting)**
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
source venv/bin/activate
python3 run_dev.py     # Backend API

# In NEW TERMINAL:
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api  
source venv/bin/activate
python3 professional_dashboard_server.py    # Dashboard Server
```

**🎨 Frontend Build (only when frontend changes):**
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard
npm run build  # Creates/updates dist/ folder
```

**🔧 COMPLETE DEPENDENCY SETUP (Run Once After Fresh Clone):**
```bash
# Install ALL required dependencies at once
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
source venv/bin/activate
pip install -r requirements.txt psutil PyJWT matplotlib ccxt
echo "✅ Complete dependency setup finished"
```

**🔍 SYSTEM VERIFICATION:**
```bash
# Verify both servers are running and healthy
curl -s http://localhost:8000/health | jq '.status'     # Should return: "healthy"
curl -s http://localhost:3400/health | jq '.status'     # Should return: "healthy"
lsof -i :8000 -i :3400                                  # Should show 2 Python processes
```

**Access Points:**
- **Professional Dashboard**: http://localhost:3400
- **Live Alerts System**: http://localhost:3400/enhanced-alerts
- **Backend API**: http://localhost:8000/api/
- **API Documentation**: http://localhost:8000/docs

**🚨 CRITICAL RULES - SINGLE OFFICIAL STRUCTURE**: 
- **OFFICIAL Backend**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/` (ONLY ONE)
- **OFFICIAL Frontend**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/` (ONLY ONE)
- **Dashboard Server**: `project/backend/api/professional_dashboard_server.py`
- **NEVER** work in any other backend/frontend directories
- **ALWAYS** use these exact paths for development
- **Modules** are separate and have their own backend/frontend if needed

## 🔒 **CRITICAL: VIRTUAL ENVIRONMENT PROTECTION RULES**

**⚠️ NEVER DELETE THE VIRTUAL ENVIRONMENT - IT CONTAINS MONTHS OF WORK**

### **ABSOLUTE FORBIDDEN COMMANDS:**
```bash
# 🚨 NEVER RUN THESE COMMANDS:
rm -rf venv                    # ❌ DESTROYS ALL INSTALLED PACKAGES
rm -r venv                     # ❌ DESTROYS ALL INSTALLED PACKAGES  
python3 -m venv venv --clear   # ❌ WIPES EXISTING ENVIRONMENT
```

### **SAFE VIRTUAL ENVIRONMENT FIXES:**
```bash
# ✅ IF PYTHON PATH IS BROKEN, FIX SYMLINKS ONLY:
cd venv/bin
rm python python3 python3.9           # Remove broken symlinks only
ln -s /usr/bin/python3 python3        # Create new symlinks
ln -s python3 python                  # Create python alias
ln -s python3 python3.9              # Create version alias

# ✅ IF DEPENDENCIES MISSING, ADD THEM:
source venv/bin/activate
pip install [missing-package-name]    # Add specific missing packages

# ✅ VERIFY ENVIRONMENT HEALTH:
source venv/bin/activate
pip freeze | wc -l                    # Should show 100+ packages
```

### **DEPENDENCY PROTECTION:**
```bash
# ✅ BACKUP PACKAGE LIST (run periodically):
source venv/bin/activate
pip freeze > package_backup.txt

# ✅ RESTORE FROM BACKUP (if needed):
source venv/bin/activate  
pip install -r package_backup.txt
```

## 🛠️ **TROUBLESHOOTING GUIDE**

### **Common Issues & Solutions:**

**1. My Symbols API 502 Bad Gateway Errors**
```bash
# ❌ WRONG: Dashboard was trying these endpoints (caused 502 errors)
GET /api/v1/my-symbols/portfolio
GET /api/v1/my-symbols/health

# ✅ CORRECT: Use these endpoints instead
GET /api/v1/portfolio
GET /api/v1/health

# Root cause: The My Symbols routes don't have "my-symbols" prefix!
```

**2. Virtual Environment Missing Dependencies**
```bash
# If routes are disabled due to missing modules:
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
source venv/bin/activate
pip install psutil PyJWT matplotlib ccxt
# Restart both servers
```

**2. Backend API Not Responding (Port 8000)**
```bash
# Check if running
lsof -i :8000
# If not running, restart:
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api && source venv/bin/activate && python3 run_dev.py
```

**3. Dashboard Server Routes Disabled**
```bash
# Check dashboard.log for missing modules
tail -n 20 /Users/dansidanutz/Desktop/ZmartBot/project/backend/api/dashboard.log
# Install missing dependencies and restart
```

**4. "ModuleNotFoundError" Issues**
```bash
# Complete dependency reset:
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
pip install -r requirements.txt psutil PyJWT matplotlib ccxt
```

### **Emergency System Restore:**
```bash
# Complete system restart with full dependency check:
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
pkill -f "python3 run_dev.py" 2>/dev/null || true
pkill -f "professional_dashboard_server.py" 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt psutil PyJWT matplotlib ccxt
nohup python3 run_dev.py > api_server.log 2>&1 &
nohup python3 professional_dashboard_server.py > dashboard.log 2>&1 &
sleep 5
curl -s http://localhost:8000/health && curl -s http://localhost:3400/health
echo "✅ System restored"
```

## Live Alerts System

### Live Alerts Implementation
The Live Alerts system is implemented as requested with:

**File Locations:**
- **Component**: `project/frontend/dashboard/components/RealTimeLiveAlerts.jsx`
- **Styling**: `project/frontend/dashboard/components/RealTimeLiveAlerts.css`
- **Routing**: Integrated in `project/frontend/dashboard/App.jsx`

**Features:**
- **Horizontal Symbol Cards**: Each symbol from the database displayed as a card
- **REAL-TIME PRICE DATA**: Uses `/api/v1/binance/ticker/24hr` for authentic market prices
- **4 Timeframes**: 15m, 1h, 4h, 1d as clickable chips per symbol
- **21 Technical Indicators**: RSI, MACD, EMA Cross, Bollinger Bands, Stochastic, ATR, ADX, CCI, Williams %R, Parabolic SAR, Ichimoku, Fibonacci, Support/Resistance, Volume, OBV, Momentum, ROC, MA Convergence, Price Channels, Bollinger Squeeze, MACD Histogram
- **Real-time Updates**: Every 30 seconds with live price updates and alert feed
- **Color-coded States**: Bullish (green), Bearish (red), Neutral (gray)  
- **Market Sentiment**: Live ratios (Bullish/Neutral/Bearish percentages)
- **Alert Severity**: Info, Warning, Strong alerts with animations
- **Price Display**: Shows current price, 24h change, 24h high/low from Binance

**Access:**
- URL: http://localhost:3400/enhanced-alerts
- Navigation: "Live Alerts" tab in sidebar

**⚡ RECENT UPDATES (2025-08-21):**
- ✅ **My Symbols API Issue Resolved**: Dashboard was using wrong endpoints with "/my-symbols" prefix
- ✅ **Real-Time Data Working**: Live Alerts now uses correct Binance ticker API
- ✅ **502 Bad Gateway Fixed**: All API endpoints corrected and documented

## 🤖 **ACTIVE ALERTS - CHATGPT-5 TRADING ADVICE SYSTEM**

### **Generate AI Advice Feature - FULLY IMPLEMENTED**

**🎯 Core Implementation (2025-08-21):**
- ✅ **"Generate AI Advice" Button**: Integrated into Active Alerts tab for real-time trading analysis
- ✅ **ChatGPT-5 Integration**: Uses OpenAI API with ChatGPT-5 → GPT-4 model mapping  
- ✅ **Real Technical Data**: Analyzes live RSI, MACD, EMA, Bollinger Bands, Stochastic, ADX data
- ✅ **API Keys Manager Integration**: Secure credential management through centralized API manager
- ✅ **Professional Trading Advice**: AI provides entry/exit levels, risk management, market analysis

### **File Locations:**
- **Frontend Component**: `project/frontend/dashboard/components/EnhancedAlertsSystem.jsx`
- **Component Styling**: `project/frontend/dashboard/components/EnhancedAlertsSystem.css`
- **Backend Route**: `project/backend/api/src/routes/openai_trading_advice.py`
- **API Keys Manager**: `project/backend/api/src/config/api_keys_manager.py`

### **Key Features:**
- **🎯 Real-Time Analysis**: Uses current market data (price, RSI, MACD, Bollinger Bands)
- **🔮 Professional Prompts**: Enhanced system prompts for expert-level trading analysis
- **🔄 Model Mapping**: ChatGPT-5 requests automatically map to GPT-4 (latest available)
- **🛡️ Error Handling**: Rate limit management, quota monitoring, fallback mechanisms
- **🔐 Secure Integration**: All API calls go through encrypted API keys manager

### **API Endpoints:**
```bash
# Generate trading advice
POST /api/v1/openai/trading-advice
{
  "prompt": "Technical analysis prompt with indicators",
  "symbol": "ETH", 
  "model": "gpt-5",
  "temperature": 0.7,
  "max_tokens": 500
}

# Check service status  
GET /api/v1/openai/status
# Returns: Configuration, model mapping, API availability
```

### **Usage Example:**
1. **Navigate**: Go to Active Alerts tab in dashboard
2. **Select Symbol**: Choose any trading symbol (BTC, ETH, etc.)
3. **Click Button**: "Generate AI Advice" button appears with technical data
4. **Get Analysis**: Receives professional ChatGPT-5 trading advice based on live indicators

### **Security & Configuration:**
- **🔑 API Keys Manager**: OpenAI API key stored in encrypted centralized manager
- **📊 Usage Tracking**: Monitors API calls, rate limits, token usage
- **🔒 Credential Protection**: All sensitive data encrypted at rest
- **⚡ Rate Limiting**: Handles OpenAI quota limits gracefully

### **Status Verification:**
```bash
# Check if ChatGPT-5 is properly configured
curl "http://localhost:8000/api/v1/openai/status"

# Expected response:
{
  "success": true,
  "service_available": true,
  "api_key_configured": true,
  "supported_models": ["gpt-5", "chatgpt-5", "gpt-4"],
  "configuration": {
    "default_model": "gpt-5", 
    "actual_model_used": "gpt-4",
    "model_mapping": "gpt-5 -> gpt-4 (latest available)"
  }
}
```

## 🔐 **API KEYS MANAGER - CENTRALIZED CREDENTIAL SYSTEM**

### **Secure API Key Management - CRITICAL INFRASTRUCTURE**

**🎯 Purpose**: Centralized, encrypted storage and management of ALL external API credentials (OpenAI, Binance, KuCoin, Cryptometer, etc.)

**File Location**: `project/backend/api/src/config/api_keys_manager.py`

### **Key Features:**
- **🔒 Encryption**: All API keys encrypted at rest using Fernet symmetric encryption
- **🗂️ Centralized**: Single source of truth for all external service credentials
- **📊 Usage Tracking**: Monitors API usage, rate limits, last used timestamps
- **🔧 Service Management**: Activate/deactivate services, health monitoring
- **💾 Persistent Storage**: Configuration saved to encrypted YAML files

### **Supported Services:**
```bash
# Currently configured services:
✅ openai         - OpenAI API for ChatGPT-5/GPT-4 trading analysis
✅ binance        - Binance Exchange API  
✅ kucoin         - KuCoin Exchange API
✅ cryptometer    - Cryptometer Analysis API
✅ coinmarketcap  - CoinMarketCap API
✅ coingecko      - CoinGecko API
✅ ethereum       - Ethereum blockchain data
✅ polygon        - Polygon blockchain data
✅ bscscan        - BSC blockchain data
✅ solana         - Solana blockchain data
```

### **Management Commands:**
```bash
# Setup OpenAI API key
cd /Users/dansidanutz/Desktop/ZmartBot/project/backend/api
python setup_openai_key.py

# Check all configured services
python -c "from src.config.api_keys_manager import api_keys_manager; print(api_keys_manager.list_services())"

# Add new service
python -c "from src.config.api_keys_manager import api_keys_manager; api_keys_manager.add_api_key('service_name', 'api_key', base_url='https://api.service.com', rate_limit=1000)"
```

### **Integration Points:**
- **All Routes**: Every external API call goes through API keys manager
- **OpenAI Trading Advice**: ChatGPT-5 integration uses manager for credentials
- **Exchange APIs**: KuCoin, Binance authentication via manager
- **Data Sources**: Cryptometer, CoinGecko, etc. all use centralized credentials

### **Security Features:**
- **🔐 File Encryption**: Configuration files encrypted with Fernet keys
- **🔒 Access Control**: Programmatic access only through manager interface
- **📊 Audit Trail**: Usage tracking, last used timestamps, call counts
- **🚨 Key Rotation**: Support for updating credentials without service restart

## Architecture & Key Components

### Multi-Agent System
- **Orchestration Agent**: Central coordinator (`src/agents/orchestration/`)
- **Scoring Agent**: Signal aggregation with dynamic weighting (`src/agents/scoring/`)
- **Risk Guard Agent**: Position management and circuit breakers (`src/agents/risk_guard/`)
- **Signal Generator Agent**: Technical analysis (`src/agents/signal_generator/`)
- **Database Agent**: RiskMetric calculations (`src/agents/database/`)

### Data Sources & Integrations
- **Cryptometer API**: 17 endpoints for market data (70% weight)
- **KingFisher Module**: Liquidation analysis via image processing (30% weight)
- **Google Sheets API**: Historical risk band data
- **KuCoin Futures API**: Trading execution
- **OpenAI API**: AI-powered analysis and predictions

### Technology Stack
- **Backend**: FastAPI 0.104.1, Python 3.11+, PostgreSQL, Redis, InfluxDB
- **Frontend**: React 18, Vite, Tailwind CSS
- **Processing**: Pandas, NumPy, OpenCV, Pillow
- **Monitoring**: Prometheus metrics, structured logging

## Essential Commands

### Backend Development
```bash
cd project/backend/api
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development server with hot reload
python run_dev.py

# Testing
pytest tests/                    # Run all tests
pytest tests/test_specific.py   # Run specific test file
pytest -k "test_function_name"  # Run specific test

# Code Quality
black .                          # Format code
ruff check .                     # Lint code (configured in pyproject.toml)
```

### Frontend Development
```bash
cd project/frontend/dashboard
npm install

# Development
npm run build                    # Build for production
npm run dev                      # Development server (if needed)

# Build & Lint
npm run build                    # Production build
npm run lint                     # ESLint check
```

## Project Structure

```
ZmartBot/
├── project/
│   ├── backend/api/             # Main backend API
│   │   ├── src/
│   │   │   ├── agents/          # Multi-agent trading system
│   │   │   ├── routes/          # API endpoints (20+ modules)
│   │   │   ├── services/        # Business logic and integrations
│   │   │   ├── utils/           # Shared utilities
│   │   │   └── config/          # Settings and configuration
│   │   ├── tests/               # Test suite
│   │   └── requirements.txt     # Python dependencies
│   └── frontend/dashboard/      # OFFICIAL React frontend
│       ├── components/          # React components
│       ├── dist/                # Built files
│       └── package.json         # Dependencies
├── backend/zmart-api/           # Legacy backend (deprecated)
├── kingfisher-module/           # Liquidation analysis module
└── Documentation/               # Project documentation
```

## Critical Implementation Details

### 📡 **WORKING API ENDPOINTS - TESTED AND VERIFIED**

**🎯 REAL-TIME PRICE DATA - PRIMARY ENDPOINT:**
```bash
# ✅ VERIFIED WORKING - Used by My Symbols & Live Alerts
GET /api/v1/binance/ticker/24hr?symbol={SYMBOL}

# Example:
curl "http://localhost:3400/api/v1/binance/ticker/24hr?symbol=BTCUSDT"

# Returns REAL Binance data:
{
  "symbol": "BTCUSDT",
  "lastPrice": "113369.38000000",    # Current price
  "priceChange": "-453.69000000",    # 24h change
  "priceChangePercent": "-0.399",    # 24h change %
  "highPrice": "114821.76000000",    # 24h high
  "lowPrice": "112380.00000000",     # 24h low  
  "volume": "13711.55282000",        # 24h volume
  "quoteVolume": "1559989205.06384640"
}
```

**📊 SYMBOLS DATA:**
```bash
# ✅ VERIFIED WORKING - Portfolio symbols (Legacy endpoint)
GET /api/futures-symbols/my-symbols/current
# Returns: Portfolio symbols array with validation

# ✅ MY SYMBOLS API - CORRECT ENDPOINTS (CRITICAL FIX):
GET /api/v1/portfolio              # Get current portfolio  
GET /api/v1/health                 # Health check
GET /api/v1/scores                 # Get symbol scores
GET /api/v1/status                 # Get status
GET /api/v1/symbols                # Get available symbols
POST /api/v1/portfolio/add         # Add symbol to portfolio
DELETE /api/v1/portfolio/remove/{symbol}  # Remove symbol from portfolio

# ⚠️ WRONG ENDPOINTS (DON'T USE):
# ❌ /api/v1/my-symbols/portfolio   # Missing "my-symbols" prefix
# ❌ /api/v1/my-symbols/health      # Missing "my-symbols" prefix
```

**🔧 HEALTH CHECKS:**
```bash
# ✅ Backend API Health
curl "http://localhost:8000/health"
# Returns: {"status": "healthy", "service": "zmart-api"}

# ✅ Dashboard Server Health  
curl "http://localhost:3400/health"
# Returns: {"status": "healthy", "module": "my_symbols"}
```

**⚠️ KNOWN ISSUES - ENDPOINTS TO AVOID:**
```bash
# ❌ DON'T USE - Session closed errors
GET /api/v1/binance/price/{symbol}

# ✅ USE INSTEAD
GET /api/v1/binance/ticker/24hr?symbol={symbol}
```

**🔍 TECHNICAL ANALYSIS ENDPOINTS:**
```bash
# ✅ Try first - may work with Cryptometer integration
GET /api/v1/cryptometer/analyze/{symbol}?timeframe=1h

# ✅ Enhanced Alerts API
GET /api/enhanced-alerts/events/{symbol}?tf={timeframe}&limit=50
```

### API Response Format
All API endpoints return standardized responses:
```python
{
    "success": bool,
    "data": Any,
    "error": Optional[str],
    "timestamp": str
}
```

### Scoring System (100-point scale)
- **KingFisher**: 30 points (liquidation analysis)
- **Cryptometer**: 50 points (market metrics, 3-tier system)
- **RiskMetric**: 20 points (historical patterns)

### Environment Variables
Required in `.env`:
```
CRYPTOMETER_API_KEY=
KUCOIN_API_KEY=
KUCOIN_SECRET=
KUCOIN_PASSPHRASE=
OPENAI_API_KEY=
DATABASE_URL=postgresql://user:password@localhost/zmart_bot
REDIS_URL=redis://localhost:6379
```

### Critical RiskMetric Rules
**IMPORTANT**: These rules must be followed for RiskMetric calculations:

1. **DBI Workflow Only**: When calculating coefficients for RiskMetric, ONLY use the DBI (Database Integration) workflow. Do not use alternative calculation methods.

2. **Daily Updates Only**: Update the following ONCE per day only:
   - Life age of each symbol
   - Corresponding risk bands for each symbol
   - These updates should be scheduled, not triggered on every request

### Database Schema
- **PostgreSQL**: Trading data, positions, analytics
- **Redis**: Caching, rate limiting, session management
- **InfluxDB**: Time-series market data
- **SQLite**: Local learning system

### Testing Strategy
- Unit tests for individual components
- Integration tests for agent interactions
- Mock external APIs for consistent testing
- Use pytest fixtures for database state

## Common Tasks

### Adding a New Trading Signal
1. Create service in `src/services/`
2. Add route in `src/routes/`
3. Register in scoring agent `src/agents/scoring/`
4. Update scoring weights if needed
5. Add tests in `tests/`

### Adding Frontend Features
1. Create component in `project/frontend/dashboard/components/`
2. Add routing in `project/frontend/dashboard/App.jsx`
3. Build with `npm run build`
4. Restart dashboard server

### Debugging API Issues
1. Check logs in console output
2. Use FastAPI docs at `http://localhost:8000/docs`
3. Verify environment variables are set
4. Check database connections
5. Review rate limiting (429 errors expected for external APIs)

### Modifying Scoring Weights
Edit `src/agents/scoring/scoring_agent.py`:
- Adjust `WEIGHT_DISTRIBUTION` constants
- Update `calculate_composite_score()` method
- Test with `pytest tests/test_scoring_agent.py`

## Important Notes

- **Rate Limiting**: External APIs have rate limits; fallback mechanisms are in place
- **Mock Mode**: Development can run without external APIs using mock data
- **Correlation IDs**: All events use correlation IDs for tracking
- **Circuit Breakers**: Risk management includes automatic position closure triggers
- **AI Integration**: OpenAI calls have retry logic and error handling

## File Paths Reference

### 🎨 OFFICIAL Frontend (THE ONLY ONE)
- **Main App**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/App.jsx`
- **Live Alerts**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/components/RealTimeLiveAlerts.jsx`
- **Live Alerts CSS**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/components/RealTimeLiveAlerts.css`
- **Symbols Manager**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/components/SymbolsManager.jsx`
- **Compiled Assets**: `/Users/dansidanutz/Desktop/ZmartBot/project/frontend/dashboard/dist/`

### 🚀 OFFICIAL Backend (THE ONLY ONE)
- **Dashboard Server**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/professional_dashboard_server.py`
- **API Server**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/main.py`
- **Routes**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/routes/`
- **Services**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/services/`
- **Agents**: `/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/agents/`

### URLs
- **Dashboard**: http://localhost:3400/
- **Live Alerts**: http://localhost:3400/enhanced-alerts
- **API**: http://localhost:8000/api/
- **API Docs**: http://localhost:8000/docs