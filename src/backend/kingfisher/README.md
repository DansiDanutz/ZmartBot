# KingFisher Module - Market Analysis & Liquidation Data

## 🎯 Overview

KingFisher is a specialized module for advanced market analysis and liquidation data processing. It operates on **Port 8100 (API)** and **Port 3100 (Frontend)**.

## 📊 Features

### **Liquidation Analysis**
- Real-time liquidation cluster detection
- Toxic order flow analysis
- Short/Long term liquidation ratios
- Market manipulation detection

### **Market Analysis**
- Price action analysis
- Volume profile analysis
- Order book depth analysis
- Market microstructure analysis

### **Data Processing**
- Screenshot analysis for KingFisher images
- Liquidation cluster mapping
- Risk assessment scoring
- Market sentiment analysis

## 🏗️ Architecture

```
kingfisher-module/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── config/
│   │   │   └── settings.py      # Module configuration
│   │   ├── services/
│   │   │   ├── liquidation_service.py    # Liquidation analysis
│   │   │   ├── market_analysis_service.py # Market analysis
│   │   │   └── image_processing_service.py # Screenshot analysis
│   │   ├── routes/
│   │   │   ├── liquidation.py   # Liquidation endpoints
│   │   │   ├── analysis.py      # Analysis endpoints
│   │   │   └── images.py        # Image processing endpoints
│   │   └── utils/
│   │       ├── database.py      # Database connections
│   │       └── monitoring.py    # Health monitoring
│   ├── requirements.txt
│   └── run_dev.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LiquidationMap.tsx
│   │   │   ├── MarketAnalysis.tsx
│   │   │   └── ImageProcessor.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Analysis.tsx
│   │   │   └── Images.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

## 🚀 Quick Start

### **1. Start KingFisher Module**
```bash
cd kingfisher-module
docker-compose up -d
```

### **2. Access KingFisher**
- **API**: http://localhost:8100
- **Frontend**: http://localhost:3100
- **Documentation**: http://localhost:8100/docs

## 🔗 Integration with ZmartBot

### **API Endpoints**
- `GET /api/v1/liquidation/clusters` - Get liquidation clusters
- `GET /api/v1/analysis/market` - Get market analysis
- `POST /api/v1/images/process` - Process KingFisher screenshots

### **Data Flow**
```
ZmartBot ←→ KingFisher
├── Signal Data: Liquidation analysis results
├── Market Data: Real-time market analysis
└── Image Data: Screenshot processing results
```

## 📈 Key Metrics

- **Liquidation Score**: 0-100 scale
- **Cluster Density**: High/Medium/Low
- **Toxic Flow**: Percentage of toxic orders
- **Market Sentiment**: Bullish/Bearish/Neutral

## 🔧 Configuration

### **Environment Variables**
```bash
export KINGFISHER_API_PORT=8100
export KINGFISHER_FRONTEND_PORT=3100
export KINGFISHER_DB_SCHEMA=kingfisher
export KINGFISHER_REDIS_NAMESPACE=kf
```

### **Database Schema**
```sql
CREATE SCHEMA kingfisher;

-- Liquidation data
CREATE TABLE kingfisher.liquidation_clusters (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    cluster_type VARCHAR(50),
    price_level DECIMAL,
    volume DECIMAL,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market analysis
CREATE TABLE kingfisher.market_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    analysis_type VARCHAR(50),
    data JSONB,
    score DECIMAL,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Screenshot processing
CREATE TABLE kingfisher.screenshots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    image_type VARCHAR(50),
    image_data BYTEA,
    analysis_result JSONB,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Status: Ready for Implementation

This module is designed to integrate seamlessly with the existing ZmartBot platform while maintaining complete operational independence. 