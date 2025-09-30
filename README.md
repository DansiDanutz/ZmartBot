# Zmart Bot V1 - Advanced Cryptocurrency Trading Platform

## 🚀 Overview

Zmart Bot V1 is a sophisticated cryptocurrency trading bot system that combines KingFisher liquidation analysis (30%), RiskMetric scoring (20%), and Cryptometer API data (50%) into a comprehensive 25-point scoring system for automated trading decisions.

## 🏗️ Architecture

### Project Structure (Reorganized)
```
ZmartBot/
├── src/                    # Source code
│   ├── backend/           # Backend services
│   │   ├── api/           # Main API server
│   │   └── kingfisher/    # KingFisher analysis module
│   ├── frontend/          # Frontend applications
│   │   └── dashboard/     # Trading dashboard
│   └── modules/           # Additional modules
│       ├── simulation-agent/
│       └── trade-strategy/
├── config/                # Configuration files
│   └── docker-compose.yml
├── deployments/           # Deployment assets
├── docs/                  # Documentation
├── scripts/               # Utility scripts
│   └── database/         # Database scripts
├── tests/                 # Test files
└── README.md             # This file
```

### Core Technologies
- **Backend**: FastAPI (Python 3.11+), PostgreSQL, Redis, InfluxDB, Prometheus
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **External APIs**: Cryptometer (17 endpoints), KuCoin Futures, Google Sheets
- **Data**: Real-time market data, historical risk analysis, image processing

### System Components
- **Orchestration Agent**: Central coordination and event management
- **Scoring Agent**: Multi-source signal aggregation and scoring
- **Risk Guard Agent**: Position risk management and drawdown protection
- **Signal Generator Agent**: Technical analysis and signal generation
- **Trading Agent**: Order execution and position management

## 📊 Scoring System

### 25-Point Comprehensive Scoring
- **KingFisher Analysis**: 7.5 points (30% weight)
  - Liquidation Clusters Map
  - Toxic Order Flow
  - Short/Long Term Liquidation Ratios
- **RiskMetric Scoring**: 5 points (20% weight)
  - Historical risk band analysis
  - Volatility assessment
  - Market condition evaluation
- **Cryptometer Data**: 12.5 points (50% weight, 3-tier system)
  - Real-time market metrics
  - Technical indicators
  - Sentiment analysis

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Backend Setup
```bash
cd src/backend/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd src/frontend/dashboard
npm install --legacy-peer-deps
```

### Environment Configuration
Create `.env` files with your API credentials:
```bash
# Backend .env
CRYPTOMETER_API_KEY=your_cryptometer_key
KUCOIN_API_KEY=your_kucoin_key
KUCOIN_SECRET=your_kucoin_secret
KUCOIN_PASSPHRASE=your_kucoin_passphrase
DATABASE_URL=postgresql://user:password@localhost/zmart_bot
REDIS_URL=redis://localhost:6379
```

## 🚀 Development

### Starting Development Environment
```bash
# Start all services
./scripts/start_dev.sh

# Start individual services
./scripts/start_dev.sh backend
./scripts/start_dev.sh frontend
```

### Backend Development
```bash
cd src/backend/api
source venv/bin/activate
python run_dev.py
```

### Frontend Development
```bash
cd src/frontend/dashboard
npm run dev
```

## 📈 Trading Strategy

### Position Management
- **Initial Position**: 500 USDT at 20X leverage
- **First Double**: +1000 USDT at 10X leverage
- **Second Double**: +2000 USDT at 5X leverage
- **Take Profit**: 50% of total invested value at each stage

### Risk Management
- Real-time drawdown monitoring
- Dynamic position sizing
- Multi-timeframe analysis
- Correlation-based diversification

## 🔐 Security Features

- JWT authentication with Redis token storage
- Secure API credential management
- HTTPS for all communications
- Rate limiting and DDoS protection
- Audit trails for all trading decisions

## 📊 Monitoring & Analytics

### Metrics Collection
- Prometheus metrics for system monitoring
- Custom trading metrics
- Performance analytics
- Error tracking and alerting

### Dashboard Features
- Real-time portfolio overview
- Trading performance metrics
- Risk analysis visualization
- Signal strength indicators

## 🧪 Testing

### Backend Testing
```bash
cd src/backend/api
pytest tests/
```

### Frontend Testing
```bash
cd src/frontend/dashboard
npm test
```

## 🚀 Deployment

### Production Deployment
```bash
./scripts/deploy.sh
```

### Docker Deployment
```bash
docker-compose -f config/docker-compose.yml up -d
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Technical Guide](docs/Zmart_Trading_Bot_Platform_Master_Technical_Guide.pdf)
- [API Documentation](docs/api.md)
- [Trading Strategy](docs/strategy.md)

## 🔗 External Integrations

### Data Sources
- **RiskMetric**: [Google Sheets](https://docs.google.com/spreadsheets/d/1Z9h8bBP13cdcgkcwq32N5Pcx4wiue9iH69uJ0wm9MRY/)
- **Historical Risk Bands**: [Google Sheets](https://docs.google.com/spreadsheets/d/1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg/)
- **Project Documentation**: [Google Drive](https://drive.google.com/drive/folders/1pkDzzfz5RMwydW6lzLPB0w_g7BcfUtf8)

### APIs
- **Cryptometer API**: 17 endpoints for market data
- **KuCoin Futures API**: Trading execution
- **Google Sheets API**: Risk data integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### V1.0.0 (Current)
- Initial release with complete trading system
- Multi-agent architecture
- Comprehensive scoring system
- Real-time monitoring and analytics
- Production-ready deployment

---

**⚠️ Disclaimer**: This is a sophisticated trading system. Use at your own risk. Past performance does not guarantee future results. Always test thoroughly before live trading.