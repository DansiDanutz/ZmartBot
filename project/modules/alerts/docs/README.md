# Symbol Alerts System

A comprehensive, real-time symbol alerts system designed for seamless integration with trading bots. The system provides multiple alert types, flexible configuration, and robust monitoring capabilities.

## 🚀 Features

### Core Alert Types
- **Price Alerts**: Threshold-based price monitoring (above/below/cross)
- **Volume Alerts**: Unusual volume spike detection
- **Technical Indicator Alerts**: RSI, MACD, Bollinger Bands, Moving Averages
- **Pattern Recognition**: Support/Resistance breaks, Chart patterns
- **News Sentiment Alerts**: Market sentiment analysis integration
- **Multi-timeframe Alerts**: 1m, 5m, 15m, 1h, 4h, 1d monitoring
- **Portfolio Alerts**: Position-based alerts and risk management

### Integration Capabilities
- **Multiple Data Sources**: Binance WebSocket, Alpha Vantage, Yahoo Finance
- **Trading Bot Integration**: Webhook and direct API support
- **Real-time Communication**: WebSocket streaming for live updates
- **Flexible Notifications**: Webhooks, Email, SMS, Discord, Telegram

### Advanced Features
- **Multi-user Support**: User management and API key authentication
- **Rate Limiting**: Configurable rate limits per user
- **Cooldown Periods**: Prevent alert spam with customizable cooldowns
- **Alert History**: Complete trigger history and analytics
- **System Monitoring**: Comprehensive metrics and health checks
- **Horizontal Scaling**: Redis-based message queuing support

## 📋 Requirements

- Python 3.11+
- SQLite/PostgreSQL database
- Redis (optional, for scaling)
- Exchange API keys (Binance, KuCoin)

## 🛠 Installation

### Quick Start with Cursor IDE

1. **Clone or extract the project**
2. **Open in Cursor IDE**
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. **Run the system**:
   ```bash
   python main.py
   ```

### Detailed Setup Guide

See [INSTALLATION.md](INSTALLATION.md) for complete setup instructions.

## 🔧 Configuration

The system uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Database
DATABASE_URL=sqlite:///./alerts.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Exchange APIs
KUCOIN_API_KEY=your-api-key
KUCOIN_SECRET=your-secret
KUCOIN_PASSPHRASE=your-passphrase

# Webhooks
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3
```

## 📖 API Documentation

### REST API Endpoints

- `GET /health` - System health check
- `GET /status` - Comprehensive system status
- `POST /alerts` - Create new alert
- `GET /alerts` - List alerts
- `GET /alerts/{id}` - Get specific alert
- `PUT /alerts/{id}` - Update alert
- `DELETE /alerts/{id}` - Delete alert
- `POST /alerts/{id}/pause` - Pause alert
- `POST /alerts/{id}/resume` - Resume alert

### WebSocket API

Connect to `ws://localhost:8001` for real-time updates:

```javascript
// Subscribe to alerts
{
  "type": "subscribe_alerts",
  "user_id": "your-user-id",
  "alert_ids": ["alert1", "alert2"]
}

// Subscribe to market data
{
  "type": "subscribe_symbols",
  "symbols": ["BTCUSDT", "ETHUSDT"]
}
```

## 🤖 Trading Bot Integration

### Webhook Integration

```python
# Example webhook handler
@app.post("/webhook/alerts")
async def handle_alert(alert_data: dict):
    symbol = alert_data["alert_trigger"]["symbol"]
    action = alert_data["alert_trigger"]["action"]
    price = alert_data["alert_trigger"]["trigger_price"]
    
    # Execute trade based on alert
    if action == "BUY":
        await execute_buy_order(symbol, price)
    elif action == "SELL":
        await execute_sell_order(symbol, price)
```

### Direct Integration

```python
from src.integrations.trading_bot_connector import ZmartTradingBot

# Initialize bot
bot = ZmartTradingBot(
    api_key="your-key",
    api_secret="your-secret",
    passphrase="your-passphrase",
    sub_account="ZmartBot"
)

# Add to connector
await trading_connector.add_bot("zmart_bot", bot)
```

## 📊 Monitoring

### System Metrics

Access metrics at:
- REST API: `GET /status`
- WebSocket: Subscribe to system status updates
- Prometheus: Port 8002 (if enabled)

### Health Checks

- `GET /health` - Overall system health
- `GET /bots/health` - Trading bot connectivity
- Database connectivity check
- WebSocket server status

## 🔒 Security

- JWT token authentication
- API key management
- Rate limiting per user
- Webhook signature verification
- Input validation and sanitization

## 📁 Project Structure

```
symbol_alerts_system/
├── src/
│   ├── core/           # Core engine components
│   ├── alerts/         # Alert type implementations
│   ├── integrations/   # Trading bot and API integrations
│   └── utils/          # Utility functions
├── config/             # Configuration and database
├── docs/               # Documentation
├── tests/              # Test suites
├── examples/           # Usage examples
└── main.py            # Application entry point
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_alerts.py
```

## 📈 Performance

- **Latency**: <100ms alert processing
- **Throughput**: 10,000+ symbols simultaneously
- **Memory**: <2GB per 1000 symbols
- **Uptime**: 99.9% availability target

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs/](docs/)
- Issues: Create an issue in the repository
- Email: developer@tradingbot.com

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

