# Zmart Trading Bot Platform

A sophisticated cryptocurrency trading bot system that uses dynamic weighting to intelligently combine KingFisher liquidation analysis, Cryptometer API data, and RiskMetric assessments into a comprehensive 100-point scoring system for automated trading decisions.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.11+
- Git

### Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd zmart-platform
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start Development Environment**
```bash
# Start all services
./start.sh

# Or start manually
docker-compose up -d
```

4. **Access Services**
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:5000
- Grafana Monitoring: http://localhost:3001
- Kibana Logs: http://localhost:5601

## 🏗️ Architecture Overview

### Core Components

**Trading Engine**
- Orchestration Agent: Central coordinator for all trading activities
- Scoring Agent: Processes multiple signal sources with ML models
- Risk Guard Agent: Monitors portfolio exposure and implements circuit breakers
- Signal Generator: Multi-source signal generation (Technical, Fundamental, Sentiment)

**Data Architecture**
- PostgreSQL: Primary database for user data and transactions
- InfluxDB: Time-series data for market prices and signals
- Redis: Caching and session management
- RabbitMQ: Inter-service communication

**Frontend**
- React 18 with TypeScript
- Tailwind CSS for styling
- Real-time WebSocket connections
- Advanced charting with D3.js

## 📊 Dynamic Scoring System

The platform uses a revolutionary **100-point dynamic scoring system** with intelligent weighting:

- **KingFisher Analysis (0-100 points)**
  - Liquidation Clusters Map
  - Toxic Order Flow
  - Short/Long Term Liquidation Ratios
  - **Dynamic Weight**: Increases during high volatility

- **RiskMetric Assessment (0-100 points)**
  - Benjamin Cowen methodology
  - Historical risk analysis
  - Volatility assessment
  - Market correlation metrics
  - **Dynamic Weight**: Favored during uncertain markets

- **Cryptometer API (0-100 points)**
  - 17 different endpoints
  - Real-time market data
  - Multi-timeframe analysis
  - **Dynamic Weight**: Favored during trending markets

### **🧠 Intelligent Weighting Features:**
- **Market Condition Awareness**: Automatically adjusts weights based on bull/bear/sideways/volatile markets
- **Data Quality Assessment**: Poor quality or stale data receives lower weight
- **Reliability Tracking**: Historical accuracy influences future weighting decisions
- **Transparent Reasoning**: Clear explanations for all weighting decisions

## 🔧 Configuration

### API Keys Required
- KuCoin API (for trading)
- Cryptometer API: `k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2`
- OpenAI API (for AI explainability)

### Environment Variables
See `.env.example` for all required environment variables.

## 🧪 Testing

```bash
# Backend tests
cd backend/zmart-api
python -m pytest

# Frontend tests
cd frontend/zmart-dashboard
npm test

# Integration tests
./test.sh
```

## 📈 Monitoring

- **Grafana**: Performance dashboards and metrics
- **Kibana**: Log analysis and debugging
- **Prometheus**: System metrics collection
- **Health Checks**: Automated service monitoring

## 🚀 Deployment

### Development
```bash
./start.sh
```

### Production
```bash
./deploy.sh
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Trading Strategy](docs/trading-strategy.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**ZmartBot** - Advanced Cryptocurrency Trading Automation 