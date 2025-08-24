# Trade Strategy Module - Position Scaling & Risk Management

## 🎯 Overview

Trade Strategy is a specialized module for advanced position scaling and risk management with corrected profit calculations. It operates on **Port 8200 (API)** and **Port 3200 (Frontend)**.

## 📊 Features

### **Position Scaling**
- **Initial Position**: 500 USDT at 20X leverage
- **First Double**: +1000 USDT at 10X leverage  
- **Second Double**: +2000 USDT at 5X leverage
- **Dynamic Liquidation Recalculation** after each doubling

### **Risk Management**
- **Take Profit Calculations**: 50% of total invested value at each stage
- **Stop Loss Management**: Dynamic stop-loss adjustment
- **Position Sizing**: Risk-based position sizing
- **Portfolio Diversification**: Multi-asset allocation

### **Profit Calculations**
- **Corrected Profit Formulas**: Accurate P&L calculations
- **Real-time Profit Tracking**: Live profit/loss monitoring
- **Historical Performance**: Performance analytics
- **Risk-Adjusted Returns**: Sharpe ratio and other metrics

## 🏗️ Architecture

```
trade-strategy-module/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── config/
│   │   │   └── settings.py      # Module configuration
│   │   ├── services/
│   │   │   ├── position_scaler.py      # Position scaling logic
│   │   │   ├── risk_manager.py         # Risk management
│   │   │   ├── profit_calculator.py    # Profit calculations
│   │   │   └── vault_manager.py        # Vault management
│   │   ├── routes/
│   │   │   ├── positions.py     # Position endpoints
│   │   │   ├── scaling.py       # Scaling endpoints
│   │   │   ├── risk.py          # Risk endpoints
│   │   │   └── profit.py        # Profit endpoints
│   │   └── utils/
│   │       ├── database.py      # Database connections
│   │       └── calculations.py  # Calculation utilities
│   ├── requirements.txt
│   └── run_dev.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PositionScaler.tsx
│   │   │   ├── RiskManager.tsx
│   │   │   ├── ProfitCalculator.tsx
│   │   │   └── VaultManager.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Scaling.tsx
│   │   │   ├── Risk.tsx
│   │   │   └── Profit.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

## 🚀 Quick Start

### **1. Start Trade Strategy Module**
```bash
cd trade-strategy-module
docker-compose up -d
```

### **2. Access Trade Strategy**
- **API**: http://localhost:8200
- **Frontend**: http://localhost:3200
- **Documentation**: http://localhost:8200/docs

## 🔗 Integration with ZmartBot

### **API Endpoints**
- `GET /api/v1/positions/active` - Get active positions
- `POST /api/v1/scaling/calculate` - Calculate scaling levels
- `POST /api/v1/risk/assess` - Risk assessment
- `GET /api/v1/profit/calculate` - Profit calculations

### **Data Flow**
```
ZmartBot ←→ Trade Strategy
├── Signal Data: Trading signals for position entry
├── Position Data: Current positions and scaling levels
├── Risk Data: Risk assessments and alerts
└── Profit Data: Real-time profit/loss calculations
```

## 📈 Scaling Strategy

### **Position Scaling Levels**
```
Level 1: Initial Position
├── Investment: 500 USDT
├── Leverage: 20X
├── Position Size: 10,000 USDT
└── Take Profit: 50% of invested (250 USDT)

Level 2: First Double
├── Investment: +1000 USDT (Total: 1500 USDT)
├── Leverage: 10X
├── Position Size: 15,000 USDT
└── Take Profit: 50% of total invested (750 USDT)

Level 3: Second Double
├── Investment: +2000 USDT (Total: 3500 USDT)
├── Leverage: 5X
├── Position Size: 17,500 USDT
└── Take Profit: 50% of total invested (1750 USDT)
```

### **Profit Calculation Examples**
```
Example 1: BTCUSDT Long Position
├── Entry Price: $50,000
├── Current Price: $52,500 (5% gain)
├── Position Size: 10,000 USDT
├── Unrealized P&L: +500 USDT
└── ROI: 10% (20X leverage)

Example 2: ETHUSDT Short Position
├── Entry Price: $3,000
├── Current Price: $2,850 (5% drop)
├── Position Size: 15,000 USDT
├── Unrealized P&L: +750 USDT
└── ROI: 10% (10X leverage)
```

## 🔧 Configuration

### **Environment Variables**
```bash
export TRADE_STRATEGY_API_PORT=8200
export TRADE_STRATEGY_FRONTEND_PORT=3200
export TRADE_STRATEGY_DB_SCHEMA=trade_strategy
export TRADE_STRATEGY_REDIS_NAMESPACE=ts
```

### **Database Schema**
```sql
CREATE SCHEMA trade_strategy;

-- Vaults (Portfolio containers)
CREATE TABLE trade_strategy.vaults (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    total_value DECIMAL,
    risk_score DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Positions
CREATE TABLE trade_strategy.positions (
    id SERIAL PRIMARY KEY,
    vault_id INTEGER REFERENCES trade_strategy.vaults(id),
    symbol VARCHAR(20),
    direction VARCHAR(10), -- LONG/SHORT
    entry_price DECIMAL,
    current_price DECIMAL,
    position_size DECIMAL,
    leverage INTEGER,
    scaling_level INTEGER,
    unrealized_pnl DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scaling events
CREATE TABLE trade_strategy.scaling_events (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES trade_strategy.positions(id),
    scaling_level INTEGER,
    investment_amount DECIMAL,
    new_leverage INTEGER,
    take_profit_target DECIMAL,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Profit calculations
CREATE TABLE trade_strategy.profit_calculations (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES trade_strategy.positions(id),
    calculation_type VARCHAR(50),
    result JSONB,
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Status: Ready for Implementation

This module provides the advanced position scaling and risk management capabilities needed for professional trading operations. 