# 🚀 ZmartBot V1 - Complete Architecture Guide

## 📋 **PROJECT OVERVIEW**

ZmartBot V1 is a comprehensive cryptocurrency trading platform that combines real-time market data, advanced charting, symbol management, and professional alert systems. This document provides a complete architectural overview of all components, services, and scripts.

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **Core Services & Ports**

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **Professional Dashboard** | 3400 | Main user interface | ✅ Active |
| **API Server** | 8000 | Backend API services | ✅ Active |
| **Database Services** | Local | SQLite databases | ✅ Active |

---

## 📁 **PROJECT STRUCTURE**

```
ZmartBot/
├── 📊 Professional Dashboard (Port 3400)
│   ├── backend/zmart-api/professional_dashboard/
│   │   ├── components/
│   │   │   ├── SymbolsManager.jsx          # Symbol management interface
│   │   │   ├── SimpleChart.jsx             # Professional charting component
│   │   │   ├── EnhancedAlertsCard.jsx      # Alert system interface
│   │   │   ├── Sidebar.jsx                 # Navigation component
│   │   │   └── App.jsx                     # Main application
│   │   ├── App.css                         # Professional styling
│   │   ├── api-proxy.js                    # API proxy configuration
│   │   └── run_dashboard.py                # Dashboard server script
│   └── frontend/zmart-dashboard/           # Alternative frontend
│
├── 🔌 Backend API Server (Port 8000)
│   ├── backend/zmart-api/
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── futures_symbols.py      # Symbol management API
│   │   │   │   ├── my_symbols.py           # Portfolio management API
│   │   │   │   ├── alerts.py               # Alert system API
│   │   │   │   └── trading.py              # Trading operations API
│   │   │   ├── services/
│   │   │   │   ├── my_symbols_service_v2.py # Portfolio service
│   │   │   │   ├── futures_symbol_validator.py # Symbol validation
│   │   │   │   └── real_time_price_service.py # Price data service
│   │   │   └── main.py                     # Main API server
│   │   ├── run_dev.py                      # Development server script
│   │   └── professional_dashboard_server.py # Dashboard proxy server
│
├── 🗄️ Database Layer
│   ├── backend/zmart-api/my_symbols_v2.db  # Portfolio database
│   ├── backend/zmart-api/data/             # Additional databases
│   └── backend/zmart-api/cache/            # Caching layer
│
├── 🚀 Startup & Deployment
│   ├── start.sh                            # Main startup script
│   ├── deploy.sh                           # Production deployment
│   └── add_api_keys.sh                     # API key configuration
│
└── 📚 Documentation & Testing
    ├── Documentation/                      # Project documentation
    ├── tests/                              # Test scripts
    └── *.md files                          # Architecture guides
```

---

## 🔧 **CORE SERVICES DETAILED**

### **1. Professional Dashboard Service**
**Location:** `backend/zmart-api/professional_dashboard/`
**Port:** 3400
**Script:** `run_dashboard.py`

#### **Key Components:**
- **SymbolsManager.jsx**: Complete symbol management interface
  - Add/remove symbols from portfolio
  - Real-time symbol validation
  - Portfolio persistence management
  - Search and filtering capabilities

- **SimpleChart.jsx**: Professional charting component
  - Real-time price data from Binance API
  - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
  - Multiple timeframes (15m, 1h, 4h, 1D, 24H)
  - Interactive tooltips and zoom controls

- **EnhancedAlertsCard.jsx**: Professional alert system
  - Real-time market alerts
  - Custom alert configurations
  - Alert history and management

- **Sidebar.jsx**: Navigation and system status
  - Dashboard navigation
  - System status indicators
  - Quick access to key features

#### **Configuration Files:**
- **api-proxy.js**: API proxy configuration for CORS handling
- **App.css**: Professional styling with glass morphism effects
- **App.jsx**: Main application routing and state management

### **2. Backend API Server**
**Location:** `backend/zmart-api/src/`
**Port:** 8000
**Script:** `run_dev.py`

#### **Core API Routes:**

##### **Futures Symbols API** (`/api/futures-symbols/`)
- **GET** `/kucoin/available` - Get KuCoin futures symbols
- **GET** `/binance/available` - Get Binance futures symbols
- **GET** `/common` - Get symbols available on both exchanges
- **GET** `/recommended` - Get recommended symbols for portfolio
- **GET** `/my-symbols/current` - Get current portfolio
- **POST** `/my-symbols/update` - Update portfolio (add/remove symbols)
- **GET** `/symbol/{symbol}` - Get detailed symbol information

##### **My Symbols API** (`/api/v1/my-symbols/`)
- **GET** `/portfolio` - Get portfolio composition
- **GET** `/scores` - Get symbol scores
- **POST** `/add-symbol` - Add symbol to portfolio
- **POST** `/remove-symbol` - Remove symbol from portfolio
- **POST** `/replace-symbol` - Replace symbol in portfolio

##### **Alerts API** (`/api/v1/alerts/`)
- **GET** `/current` - Get current alerts
- **POST** `/create` - Create new alert
- **DELETE** `/delete/{id}` - Delete alert

##### **Trading API** (`/api/v1/trading/`)
- **GET** `/positions` - Get current positions
- **POST** `/place-order` - Place trading order
- **GET** `/history` - Get trading history

#### **Core Services:**

##### **MySymbolsServiceV2** (`my_symbols_service_v2.py`)
- Portfolio management with SQLite database
- Symbol validation and persistence
- Score calculation and ranking
- Portfolio rebalancing logic

##### **FuturesSymbolValidator** (`futures_symbol_validator.py`)
- Real-time symbol validation
- Exchange availability checking
- Symbol format conversion (KuCoin ↔ Binance ↔ Standard)

##### **RealTimePriceService** (`real_time_price_service.py`)
- Real-time price data from Binance API
- Technical indicator calculations
- Market data caching

### **3. Database Layer**

#### **Primary Database: my_symbols_v2.db**
**Location:** `backend/zmart-api/my_symbols_v2.db`

**Tables:**
- **symbols**: Symbol registry with contract specifications
- **portfolio_composition**: Current portfolio (max 10 symbols)
- **symbol_scores**: Multi-factor scoring data
- **portfolio_history**: Complete audit trail
- **signals**: Trading signal processing
- **system_configuration**: Global settings

#### **Additional Databases:**
- **riskmetric.db**: Risk analysis data
- **learning_data.db**: Machine learning models
- **cryptometer_data.db**: Cryptometer API data
- **historical_patterns.db**: Pattern recognition data

### **4. Proxy & Communication Layer**

#### **Dashboard Proxy Server** (`professional_dashboard_server.py`)
**Port:** 3400
**Purpose:** Proxy API calls to main backend server

**Key Features:**
- API request proxying
- CORS handling
- Static file serving
- Error handling and fallbacks

#### **API Proxy Configuration** (`api-proxy.js`)
**Purpose:** Frontend API communication layer

**Features:**
- Automatic request routing
- Error handling
- Request/response logging
- CORS management

---

## 🚀 **STARTUP & DEPLOYMENT SCRIPTS**

### **Main Startup Script** (`start.sh`)
**Purpose:** Complete system startup and orchestration

**Functions:**
1. **Port Cleanup**: Kill existing processes on ports 3400 and 8000
2. **Dashboard Build**: Ensure frontend is built and ready
3. **API Server Start**: Start backend API server on port 8000
4. **Dashboard Server Start**: Start dashboard proxy on port 3400
5. **Health Monitoring**: Monitor service health and provide status

**Usage:**
```bash
./start.sh
```

### **Production Deployment** (`deploy.sh`)
**Purpose:** Production deployment with Docker

**Features:**
- Docker containerization
- Environment configuration
- Service orchestration
- Health checks

### **API Key Configuration** (`add_api_keys.sh`)
**Purpose:** Secure API key management

**Features:**
- Environment variable setup
- API key validation
- Security configuration

---

## 🔄 **DATA FLOW ARCHITECTURE**

### **1. Symbol Management Flow**
```
Frontend (SymbolsManager.jsx)
    ↓
API Proxy (api-proxy.js)
    ↓
Dashboard Server (professional_dashboard_server.py)
    ↓
Backend API (futures_symbols.py)
    ↓
MySymbolsServiceV2 (my_symbols_service_v2.py)
    ↓
Database (my_symbols_v2.db)
```

### **2. Chart Data Flow**
```
Frontend (SimpleChart.jsx)
    ↓
API Proxy (api-proxy.js)
    ↓
Dashboard Server (professional_dashboard_server.py)
    ↓
Backend API (binance/klines)
    ↓
Binance API (Real-time data)
    ↓
Chart Rendering (Chart.js)
```

### **3. Alert System Flow**
```
Market Data (RealTimePriceService)
    ↓
Alert Engine (alerts.py)
    ↓
Database Storage (alerts table)
    ↓
Frontend Display (EnhancedAlertsCard.jsx)
    ↓
User Notifications
```

---

## 🛠️ **DEVELOPMENT & TESTING**

### **Test Scripts**
- **test_symbol_persistence.py**: Symbol persistence testing
- **test_enhanced_alerts.py**: Alert system testing
- **test_dashboard_fix.py**: Dashboard functionality testing
- **test_ranking_system.py**: Ranking system testing

### **Development Commands**
```bash
# Start development environment
./start.sh

# Build frontend
cd backend/zmart-api/professional_dashboard
npm run build

# Run tests
python test_*.py

# Check logs
tail -f /tmp/api_server.log
tail -f /tmp/dashboard_server.log
```

---

## 🔒 **SECURITY & CONFIGURATION**

### **Environment Variables**
- **API Keys**: Stored in environment variables
- **Database Paths**: Configurable database locations
- **Service Ports**: Configurable service ports
- **CORS Settings**: Cross-origin resource sharing

### **Security Features**
- **API Key Management**: Secure API key storage
- **Request Validation**: Input validation and sanitization
- **Error Handling**: Comprehensive error handling
- **Logging**: Detailed logging for debugging

---

## 📊 **MONITORING & LOGGING**

### **Log Files**
- **API Server**: `/tmp/api_server.log`
- **Dashboard Server**: `/tmp/dashboard_server.log`
- **Application Logs**: Database and file-based logging

### **Health Checks**
- **API Endpoints**: `/api/health`
- **Database Connectivity**: Automatic connection testing
- **Service Status**: Real-time service monitoring

---

## 🎯 **KEY FEATURES SUMMARY**

### **✅ Implemented Features**
- **Symbol Management**: Complete portfolio management (max 10 symbols)
- **Real-time Charting**: Professional charts with technical indicators
- **Alert System**: Real-time market alerts and notifications
- **Database Persistence**: Reliable symbol and data persistence
- **API Integration**: Binance and KuCoin API integration
- **Professional UI**: Modern, responsive dashboard interface
- **Error Handling**: Comprehensive error handling and recovery
- **Security**: Secure API key management and validation

### **🔧 Technical Capabilities**
- **Real-time Data**: Live market data from Binance API
- **Technical Analysis**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Portfolio Management**: Add, remove, replace symbols
- **Alert System**: Custom alerts and notifications
- **Data Persistence**: SQLite database with audit trails
- **API Proxy**: Seamless frontend-backend communication
- **Responsive Design**: Professional, mobile-friendly interface

---

## 📈 **PERFORMANCE & SCALABILITY**

### **Current Performance**
- **Response Time**: < 100ms for API calls
- **Data Throughput**: Real-time price updates
- **Concurrent Users**: Supports multiple simultaneous users
- **Database Performance**: Optimized SQLite queries

### **Scalability Considerations**
- **Database**: Can migrate to PostgreSQL for larger scale
- **Caching**: Redis integration for improved performance
- **Load Balancing**: Horizontal scaling with multiple instances
- **Microservices**: Modular architecture for easy scaling

---

## 🚀 **DEPLOYMENT STATUS**

### **Current Deployment**
- **Environment**: Development/Production ready
- **Services**: All services running and functional
- **Database**: All databases operational
- **Frontend**: Professional dashboard active
- **API**: All endpoints functional

### **Access Points**
- **Dashboard**: http://localhost:3400
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 📝 **VERSION INFORMATION**

**Version:** ZmartBot V1.0  
**Release Date:** August 16, 2025  
**Git Tag:** ZmartBot-V1.0  
**Commit Hash:** 6ea52ec  

**Key Achievements:**
- ✅ Complete symbol persistence fix
- ✅ Professional charting system
- ✅ Enhanced alerts implementation
- ✅ Comprehensive error handling
- ✅ Production-ready deployment

---

*This architecture guide documents the complete ZmartBot V1 system. For technical support or questions, refer to the individual component documentation or contact the development team.*
