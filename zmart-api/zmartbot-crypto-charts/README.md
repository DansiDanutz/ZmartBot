# ZmartBot Crypto Charts Service

Professional crypto charts with free APIs - Zero cost development

## Features

- 📊 Real-time cryptocurrency price charts
- 🔄 Multiple timeframes (1H, 4H, 1D, 1W, 1M)
- 📈 Market overview with top gainers/losers
- 🚀 Free API integration (CoinGecko, Binance, Cryptometer)
- 💾 Intelligent caching system
- 🔒 Security-first approach with Helmet.js
- 📱 Responsive design
- ⚡ High-performance with compression

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Setup environment:**
   ```bash
   node setup.js
   ```

3. **Start the service:**
   ```bash
   npm start
   ```

4. **Access the application:**
   - Web Interface: http://localhost:8901
   - Health Check: http://localhost:8901/health
   - API Documentation: http://localhost:8901/api

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Market Data
- `GET /api/symbols` - Get supported symbols
- `GET /api/prices?symbol=BTC` - Get current price
- `GET /api/history?symbol=BTC&interval=1d&limit=100` - Get historical data
- `GET /api/market-overview` - Get market overview

### WebSocket
- `WS /ws` - Real-time price updates

## Configuration

Edit `.env` file to customize:
- Port settings
- API rate limits
- Cache settings
- Database configuration
- Security settings

## Architecture

- **Frontend**: HTML5 + CSS3 + JavaScript (Chart.js)
- **Backend**: Node.js + Express.js
- **Real-time**: WebSocket
- **Caching**: Redis
- **Database**: SQLite3
- **Security**: Helmet.js + CORS
- **Performance**: Compression + Winston logging

## Integration with ZmartBot

This service integrates with the ZmartBot ecosystem:
- Port Manager integration for dynamic port assignment
- Service discovery and registration
- Health monitoring and reporting
- Master Orchestration Agent compatibility

## Development

```bash
# Development mode with auto-reload
npm run dev

# Install dependencies
npm run install-deps

# Setup environment
npm run setup
```

## License

MIT License - See LICENSE file for details

## Support

For support and questions, contact the ZmartBot development team.
