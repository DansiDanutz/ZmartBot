# Backend Domain Context

## BackendDoctorPack
**File**: .cursor/rules/BackendDoctorPack.mdc
**Relevance**: 30
**Size**: 18706 bytes

**Summary**: # BackendDoctorPack.mdc ## Overview

---

## BackendFrontendProtection
**File**: .cursor/rules/BackendFrontendProtection.mdc
**Relevance**: 30
**Size**: 8866 bytes

**Content**:
```
@agent: BackendFrontendProtectionAgent

# Backend & Frontend Protection System - CRITICAL COMPONENT

## Overview
The **Backend & Frontend Protection System** is a critical security component that prevents deletion, replacement, or unauthorized modifications of the most important ZmartBot components. This system MUST be run manually and cannot be automated or replaced.

## 🚨 CRITICAL IMPORTANCE

### **Why This Protection is Essential**
- **Backend (run_dev.py + src/main.py)**: Core API server with all trading operations
- **Frontend (professional_dashboard_server.py + components)**: User interface and trading platform
- **Prevents**: Accidental deletion, malicious replacement, unauthorized modifications
- **Ensures**: System integrity and operational continuity
- **Requires**: Manual intervention for any changes

## 🔒 Protection Components

### **Backend Protection System**
- **File**: `protect_backend.py`
- **Purpose**: Protects critical backend files from modification/deletion
- **Protected Files**:
  - `run_dev.py` - Backend startup script (CRITICAL)
  - `src/main.py` - Main FastAPI application (CRITICAL)
  - `src/routes/` - API routes directory (CRITICAL)
  - `src/services/` - Services directory (CRITICAL)
  - `src/config/` - Configuration directory (CRITICAL)

### **Frontend Protection System**
- **File**: `protect_frontend.py`
- **Purpose**: Protects critical frontend files from modification/deletion
- **Protected Files**:
  - `professional_dashboard_server.py` - Frontend server (CRITICAL)
  - `professional_dashboard/App.jsx` - Main React app (CRITICAL)
  - `professional_dashboard/api-proxy.js` - API proxy (CRITICAL)
  - `professional_dashboard/components/` - React components (CRITICAL)
  - `professional_dashboard/App.css` - Main styling (CRITICAL)
  - `professional_dashboard/index.html` - HTML entry (CRITICAL)
  - `professional_dashboard/main.jsx` - React entry (CRITICAL)

## 🛡️ Protection Features

### **File Integrity Monitoring**
- **SHA256 Hashing**: Calcu
```

---

## Backend
**File**: .cursor/rules/Backend.mdc
**Relevance**: 30
**Size**: 9272 bytes

**Content**:
```
@agent: BackendService

# Backend - FastAPI Server (Port 8000)

## Overview
The **official backend** of the ZmartBot project is the **FastAPI Server** running on **port 8000**. This is the core API server that provides all trading operations, data processing, external API integrations, and business logic for the entire ZmartBot platform.

## Backend Architecture

### **Core Framework**
- **Framework**: FastAPI (Python 3.11+)
- **Port**: 8000 (official backend port)
- **Architecture**: RESTful API with WebSocket support
- **Database**: PostgreSQL, Redis, InfluxDB, SQLite
- **Authentication**: JWT-based authentication system

### **API Structure**
- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1/`
- **Documentation**: `/docs` (Swagger UI)
- **Health Check**: `/health`

## Backend Components

### 1. **Trading API Endpoints**
- **My Symbols**: `/api/v1/trading/my-symbols` - Manage trading symbols
- **Portfolio**: `/api/v1/portfolio` - Portfolio management and tracking
- **Orders**: `/api/v1/orders` - Order placement and management
- **Positions**: `/api/v1/positions` - Position tracking and management
- **Risk Management**: `/api/v1/risk` - Risk assessment and controls

### 2. **Market Data Services**
- **Real-time Prices**: `/api/v1/market/prices` - Live price feeds
- **Historical Data**: `/api/v1/market/history` - Historical price data
- **Market Indicators**: `/api/v1/market/indicators` - Technical indicators
- **Market Sentiment**: `/api/v1/market/sentiment` - Market sentiment analysis

### 3. **Alert System**
- **Enhanced Alerts**: `/api/v1/alerts/enhanced` - Advanced trading alerts
- **Technical Alerts**: `/api/v1/alerts/technical` - Technical analysis alerts
- **Risk Alerts**: `/api/v1/alerts/risk` - Risk management alerts
- **Alert History**: `/api/v1/alerts/history` - Alert performance tracking

### 4. **External API Integrations**
- **KuCoin API**: Futures trading, account management, market data
- **Binance API**: Market data, price feeds, 
```

---

## API-Manager
**File**: .cursor/rules/API-Manager.mdc
**Relevance**: 30
**Size**: 10477 bytes

**Summary**: @agent: APIHandler # API Manager - External Service Integration System ## Overview

---

