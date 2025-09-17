# ZmartBot Orchestration Integration

## 🎯 Overview

This integration connects the ZmartBot Foundation API (port 8000) with the Zmarty Interactive Engagement System (port 8350), creating a unified trading platform with AI-powered mentoring capabilities.

## 🏗️ Architecture

### Service Layout
```
┌─────────────────────────────────────────────────────────────┐
│                 ZmartBot Orchestration                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ Foundation API  │◄──►│ Engagement System               │ │
│  │ :8000          │    │ :8350                          │ │
│  │ • Signals      │    │ • MCP Integration              │ │
│  │ • Pools        │    │ • AI Personality               │ │
│  │ • Credits      │    │ • Gamification                 │ │
│  │ • Alerts       │    │ • Real Market Data             │ │
│  │ • Health       │    │ • Psychological Triggers       │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                 MCP Data Sources                            │
│  KingFisher • Cryptometer • RiskMetric • Grok • X • Whale  │
└─────────────────────────────────────────────────────────────┘
```

### Integration Components

#### 1. Service Orchestration Manager (`service_orchestration.py`)
- **Purpose**: Manages service lifecycle, dependencies, and health monitoring
- **Features**:
  - Dependency-aware startup sequence
  - Automatic health monitoring with restart capabilities
  - Graceful shutdown handling
  - Service status tracking and reporting

#### 2. Engagement Proxy Router (`app/routers/engagement.py`)
- **Purpose**: Provides unified API access to engagement system through Foundation API
- **Endpoints**:
  - `GET /v1/engagement/health` - Check engagement system health
  - `POST /v1/engagement/interact` - Chat with Zmarty AI mentor
  - `POST /v1/engagement/unlock-premium` - Unlock premium content
  - `GET /v1/engagement/user/{user_id}` - Get user profile
  - `POST /v1/engagement/market-alert` - Send market alerts
  - `GET /v1/engagement/analytics` - Get engagement analytics
  - `GET /v1/engagement/mcp-status` - Check MCP integration status

#### 3. Integration Middleware (`app/middleware/engagement_integration.py`)
- **Purpose**: Automatically forwards relevant events from Foundation API to Engagement System
- **Features**:
  - Signal creation notifications
  - Pool update events
  - Market alert forwarding
  - Background sync tasks

## 🚀 Quick Start

### 1. Start Complete System
```bash
# Start orchestrated system (recommended)
python3 /Users/dansidanutz/Desktop/ZmartBot/service_orchestration.py
```

### 2. Manual Service Start
```bash
# Terminal 1: Start Foundation API
cd /Users/dansidanutz/Desktop/ZmartBot/zmart-foundation
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start Engagement System
cd /Users/dansidanutz/Desktop/ZmartBot/engagement-system
python3 engagement_startup.py
```

### 3. Test Integration
```bash
# Run comprehensive integration tests
python3 /Users/dansidanutz/Desktop/ZmartBot/test_orchestration_integration.py
```

## 🔗 Unified API Usage

### Chat with AI Mentor (via Foundation API)
```bash
curl -X POST http://localhost:8000/v1/engagement/interact \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "trader123", 
    "message": "What do you think about BTC right now?", 
    "asset": "BTC"
  }'
```

### Check MCP Data Sources
```bash
curl http://localhost:8000/v1/engagement/mcp-status
```

### Send Market Alert
```bash
curl -X POST http://localhost:8000/v1/engagement/market-alert \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "BTC",
    "alert_type": "whale_movement", 
    "urgency": 8,
    "message": "Large BTC whale transaction detected"
  }'
```

## 🔄 Event Integration

The system automatically forwards relevant events between services:

### Trading Signals → Engagement Alerts
When a trading signal is created via `/v1/signals`, it automatically triggers a personalized alert in the engagement system.

### Pool Updates → User Notifications  
Pool status changes (expired, liquidated, closed) are automatically communicated to relevant users through the engagement system.

### Market Alerts → AI Analysis
Market alerts trigger AI analysis and personalized responses based on user profiles and preferences.

## 📊 Monitoring & Health

### Service Status
```bash
# Check all service health
curl http://localhost:8000/v1/health
curl http://localhost:8000/v1/engagement/health
curl http://localhost:8350/health
```

### Background Processes
- **Pool Expiry**: Runs every 5 minutes
- **Engagement Sync**: Runs every 1 minute
- **Health Monitoring**: Runs every 30 seconds (in orchestrated mode)

## 🎮 Engagement Features

### Gamification Elements
- **Skill Levels**: Novice → Developing → Skilled → Advanced → Expert → Master
- **Credit System**: FREE (0) → BASIC (2) → PREMIUM (5) → EXCLUSIVE (10)
- **Achievements**: Unlocked based on trading activity and learning progress
- **Streaks**: Daily interaction streaks with multipliers

### AI Personality System
- **Adaptive Responses**: Tailored to user skill level and trading experience
- **Market Context**: Real-time integration with MCP data sources
- **Psychological Triggers**: Engagement patterns based on behavioral psychology
- **Ethical Safeguards**: Spending limits and responsible trading guidance

### MCP Data Integration
- **KingFisher**: Liquidation cluster analysis
- **Cryptometer**: Market indicator insights
- **RiskMetric**: Risk assessment values
- **Grok & X Sentiment**: Social media sentiment analysis
- **Whale Alerts**: Large transaction notifications

## 🔧 Configuration

### Service Ports
- **Foundation API**: 8000
- **Engagement System**: 8350
- **Health Dashboard**: 8080 (optional)

### Dependencies
- Foundation API must start first (critical service)
- Engagement System depends on Foundation API
- Health Scheduler depends on both services

### Environment Variables
```env
# Foundation API Database
DATABASE_URL=sqlite:///./zmart.db

# Engagement System
ENGAGEMENT_PORT=8350
MCP_SERVERS_CONFIG=/path/to/mcp/config

# Logging
LOG_LEVEL=INFO
```

## 🧪 Testing

### Automated Test Suite
The `test_orchestration_integration.py` script provides comprehensive testing:

1. **Service Health**: Verifies all services are running
2. **Engagement Proxy**: Tests Foundation API → Engagement System communication  
3. **MCP Integration**: Validates MCP data flow through proxy
4. **Chat Interaction**: Tests AI mentor functionality via proxy
5. **Market Alerts**: Verifies alert integration
6. **Signal Integration**: Tests trading signal → engagement system flow

### Expected Test Results
```
📊 INTEGRATION TEST RESULTS: 6/6 tests passed
🎉 ALL INTEGRATION TESTS PASSED!
🔗 Orchestration integration is working correctly!
```

## 🚨 Troubleshooting

### Common Issues

#### Service Startup Failures
```bash
# Check service logs
tail -f /Users/dansidanutz/Desktop/ZmartBot/health_scheduler.log

# Manually test service health
curl http://localhost:8000/v1/health
curl http://localhost:8350/health
```

#### MCP Integration Issues
```bash
# Check MCP server status
curl http://localhost:8350/mcp-status

# Restart engagement system
pkill -f engagement_startup.py
python3 /Users/dansidanutz/Desktop/ZmartBot/engagement-system/engagement_startup.py
```

#### Database Issues
```bash
# Check database connection
sqlite3 /Users/dansidanutz/Desktop/ZmartBot/zmart-foundation/zmart.db ".schema"

# Reset if needed
rm /Users/dansidanutz/Desktop/ZmartBot/zmart-foundation/zmart.db
# Restart foundation API to recreate
```

## 📈 Performance Optimization

### Response Times
- **Foundation API**: < 100ms for most endpoints
- **Engagement Proxy**: < 200ms (includes upstream call)
- **MCP Data Queries**: < 500ms (real market data)

### Caching Strategy
- User profiles cached for 5 minutes
- Market data cached for 30 seconds
- MCP responses cached for 1 minute

### Scaling Considerations
- Services can be horizontally scaled
- Database can be moved to PostgreSQL for production
- MCP integrations support load balancing

## 🎯 Next Steps

1. **Production Deployment**: Docker containerization and Kubernetes orchestration
2. **Advanced Analytics**: Integration with time-series databases for historical analysis  
3. **WebSocket Support**: Real-time bidirectional communication
4. **Mobile API**: Optimized endpoints for mobile applications
5. **Advanced AI**: Enhanced personality system with machine learning

---

**Status**: ✅ Integration Complete
**Last Updated**: 2025-09-09
**Version**: 1.0.0