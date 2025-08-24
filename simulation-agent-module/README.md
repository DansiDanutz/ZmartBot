# Simulation Agent Module - Pattern Analysis & Win Ratio Simulation

## 🎯 Overview

Simulation Agent is a specialized module for advanced pattern analysis and win ratio simulation. It operates on **Port 8300 (API)** and **Port 3300 (Frontend)**.

## 📊 Features

### **Pattern Analysis**
- **Technical Pattern Recognition**: Chart patterns, candlestick patterns
- **Market Structure Analysis**: Support/resistance, trend analysis
- **Volume Pattern Analysis**: Volume profile, accumulation/distribution
- **Time-based Patterns**: Seasonal patterns, time-based correlations

### **Win Ratio Simulation**
- **Historical Backtesting**: Multi-timeframe backtesting
- **Monte Carlo Simulations**: Risk-adjusted return simulations
- **Strategy Optimization**: Parameter optimization
- **Performance Analytics**: Sharpe ratio, max drawdown, win rate

### **Machine Learning**
- **Pattern Classification**: ML-based pattern recognition
- **Signal Generation**: AI-powered signal generation
- **Risk Prediction**: ML risk assessment models
- **Market Regime Detection**: Bull/bear/sideways market detection

## 🏗️ Architecture

```
simulation-agent-module/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── config/
│   │   │   └── settings.py      # Module configuration
│   │   ├── services/
│   │   │   ├── pattern_analyzer.py     # Pattern analysis
│   │   │   ├── simulation_engine.py    # Simulation engine
│   │   │   ├── ml_models.py           # Machine learning models
│   │   │   └── backtester.py          # Backtesting engine
│   │   ├── routes/
│   │   │   ├── patterns.py      # Pattern endpoints
│   │   │   ├── simulations.py   # Simulation endpoints
│   │   │   ├── backtesting.py   # Backtesting endpoints
│   │   │   └── ml.py            # ML endpoints
│   │   └── utils/
│   │       ├── database.py      # Database connections
│   │       └── analytics.py     # Analytics utilities
│   ├── requirements.txt
│   └── run_dev.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatternAnalyzer.tsx
│   │   │   ├── SimulationEngine.tsx
│   │   │   ├── Backtester.tsx
│   │   │   └── MLModels.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Patterns.tsx
│   │   │   ├── Simulations.tsx
│   │   │   └── Backtesting.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

## 🚀 Quick Start

### **1. Start Simulation Agent Module**
```bash
cd simulation-agent-module
docker-compose up -d
```

### **2. Access Simulation Agent**
- **API**: http://localhost:8300
- **Frontend**: http://localhost:3300
- **Documentation**: http://localhost:8300/docs

## 🔗 Integration with ZmartBot

### **API Endpoints**
- `GET /api/v1/patterns/analyze` - Analyze patterns
- `POST /api/v1/simulations/run` - Run simulations
- `POST /api/v1/backtesting/execute` - Execute backtests
- `GET /api/v1/ml/predict` - ML predictions

### **Data Flow**
```
ZmartBot ←→ Simulation Agent
├── Market Data: Real-time market data for analysis
├── Pattern Data: Identified patterns and signals
├── Simulation Results: Win ratios and performance metrics
└── ML Predictions: AI-powered market predictions
```

## 📈 Simulation Capabilities

### **Pattern Recognition**
```
Technical Patterns:
├── Chart Patterns: Head & Shoulders, Double Top/Bottom
├── Candlestick Patterns: Doji, Hammer, Shooting Star
├── Harmonic Patterns: Gartley, Butterfly, Bat
└── Elliott Wave: Wave counting and analysis

Volume Patterns:
├── Volume Profile: High/low volume areas
├── Accumulation/Distribution: Smart money flow
├── Volume Divergence: Price vs volume analysis
└── Volume Breakouts: Volume-based signals
```

### **Win Ratio Analysis**
```
Simulation Types:
├── Historical Backtesting: Past performance analysis
├── Monte Carlo: Risk-adjusted return simulations
├── Walk-Forward Analysis: Out-of-sample testing
└── Stress Testing: Extreme market condition testing

Performance Metrics:
├── Win Rate: Percentage of profitable trades
├── Profit Factor: Gross profit / Gross loss
├── Sharpe Ratio: Risk-adjusted returns
├── Max Drawdown: Maximum peak-to-trough decline
└── Expected Value: Average return per trade
```

## 🔧 Configuration

### **Environment Variables**
```bash
export SIMULATION_AGENT_API_PORT=8300
export SIMULATION_AGENT_FRONTEND_PORT=3300
export SIMULATION_AGENT_DB_SCHEMA=simulation_agent
export SIMULATION_AGENT_REDIS_NAMESPACE=sa
```

### **Database Schema**
```sql
CREATE SCHEMA simulation_agent;

-- Patterns
CREATE TABLE simulation_agent.patterns (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    pattern_type VARCHAR(50),
    pattern_data JSONB,
    confidence_score DECIMAL,
    detected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Simulations
CREATE TABLE simulation_agent.simulations (
    id SERIAL PRIMARY KEY,
    simulation_type VARCHAR(50),
    parameters JSONB,
    results JSONB,
    win_rate DECIMAL,
    profit_factor DECIMAL,
    sharpe_ratio DECIMAL,
    max_drawdown DECIMAL,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Backtests
CREATE TABLE simulation_agent.backtests (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    results JSONB,
    performance_metrics JSONB,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- ML Models
CREATE TABLE simulation_agent.ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    model_type VARCHAR(50),
    parameters JSONB,
    performance_metrics JSONB,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Status: Ready for Implementation

This module provides advanced pattern analysis and simulation capabilities for optimizing trading strategies and improving win ratios. 