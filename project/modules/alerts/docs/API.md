
# API Documentation

Complete API reference for the Symbol Alerts System.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses JWT token authentication for protected endpoints.

### Get API Token
```http
POST /auth/token
Content-Type: application/json

{
  "user_id": "your_user_id",
  "api_key": "your_api_key"
}
```

### Use Token
```http
Authorization: Bearer <your_jwt_token>
```

## Alert Management

### Create Alert
```http
POST /alerts
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": "demo_user",
  "symbol": "BTCUSDT",
  "alert_type": "price_above",
  "conditions": [
    {
      "field": "price",
      "operator": ">",
      "value": 50000,
      "timeframe": "5m"
    }
  ],
  "message": "BTC above $50,000",
  "webhook_url": "https://your-webhook.com/alerts",
  "expires_at": "2024-12-31T23:59:59Z",
  "max_triggers": 5,
  "cooldown_minutes": 30
}
```

**Response:**
```json
{
  "id": "alert_1234567890",
  "user_id": "demo_user",
  "symbol": "BTCUSDT",
  "alert_type": "price_above",
  "conditions": [...],
  "message": "BTC above $50,000",
  "webhook_url": "https://your-webhook.com/alerts",
  "is_active": true,
  "created_at": "2024-08-15T16:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "max_triggers": 5,
  "cooldown_minutes": 30
}
```

### List Alerts
```http
GET /alerts?user_id=demo_user
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "alert_1234567890",
    "user_id": "demo_user",
    "symbol": "BTCUSDT",
    "alert_type": "price_above",
    "is_active": true,
    "created_at": "2024-08-15T16:30:00Z"
  }
]
```

### Get Specific Alert
```http
GET /alerts/{alert_id}
Authorization: Bearer <token>
```

### Update Alert
```http
PUT /alerts/{alert_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "is_active": false,
  "message": "Updated message",
  "cooldown_minutes": 60
}
```

### Delete Alert
```http
DELETE /alerts/{alert_id}
Authorization: Bearer <token>
```

### Pause Alert
```http
POST /alerts/{alert_id}/pause
Authorization: Bearer <token>
```

### Resume Alert
```http
POST /alerts/{alert_id}/resume
Authorization: Bearer <token>
```

### Get Alert History
```http
GET /alerts/{alert_id}/history
Authorization: Bearer <token>
```

**Response:**
```json
{
  "alert_id": "alert_1234567890",
  "triggers": [
    "2024-08-15T16:35:00Z",
    "2024-08-15T17:05:00Z"
  ]
}
```

## Market Data

### Get Market Data
```http
GET /market/{symbol}
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "price": 50000.0,
  "volume": 1000000.0,
  "timestamp": "2024-08-15T16:30:00Z",
  "bid": 49999.0,
  "ask": 50001.0,
  "high_24h": 52000.0,
  "low_24h": 48000.0,
  "change_24h": 2000.0,
  "change_percent_24h": 4.17
}
```

### Get Technical Indicators
```http
GET /technical/{symbol}/{timeframe}
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "5m",
  "timestamp": "2024-08-15T16:30:00Z",
  "rsi": 55.0,
  "macd": 100.0,
  "macd_signal": 95.0,
  "macd_histogram": 5.0,
  "bb_upper": 51000.0,
  "bb_middle": 50000.0,
  "bb_lower": 49000.0,
  "sma_20": 49800.0,
  "sma_50": 49500.0,
  "ema_12": 50100.0,
  "ema_26": 49900.0,
  "volume_sma": 800000.0
}
```

## Trading Bot Management

### Add Trading Bot
```http
POST /bots
Content-Type: application/json
Authorization: Bearer <token>

{
  "bot_id": "zmart_main",
  "bot_type": "zmart",
  "config": {
    "api_key": "your_api_key",
    "api_secret": "your_secret",
    "passphrase": "your_passphrase",
    "sandbox": true,
    "sub_account": "ZmartBot"
  }
}
```

### Remove Trading Bot
```http
DELETE /bots/{bot_id}
Authorization: Bearer <token>
```

### Get Bot Positions
```http
GET /bots/positions
Authorization: Bearer <token>
```

**Response:**
```json
{
  "zmart_main": [
    {
      "symbol": "BTC",
      "amount": 0.1,
      "free": 0.05,
      "used": 0.05
    }
  ]
}
```

### Get Bot Balances
```http
GET /bots/balances
Authorization: Bearer <token>
```

**Response:**
```json
{
  "zmart_main": {
    "USDT": 1000.0,
    "BTC": 0.1,
    "ETH": 2.5
  }
}
```

### Check Bot Health
```http
GET /bots/health
Authorization: Bearer <token>
```

**Response:**
```json
{
  "zmart_main": true,
  "webhook_bot": false
}
```

## System Monitoring

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-15T16:30:00Z",
  "components": {
    "data_manager": "healthy",
    "notification_manager": "healthy",
    "alert_processor": "healthy"
  },
  "active_alerts": 15,
  "delivery_queue_size": 2
}
```

### System Status
```http
GET /status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-15T16:30:00Z",
  "metrics": {
    "active_alerts": 15,
    "monitored_symbols": 8,
    "triggers_last_hour": 23,
    "avg_processing_time_ms": 45.2,
    "memory_usage_mb": 256.8,
    "cpu_usage_percent": 12.5,
    "uptime_seconds": 86400,
    "last_updated": "2024-08-15T16:30:00Z"
  },
  "components": {
    "data_manager": "healthy",
    "notification_manager": "healthy",
    "alert_processor": "healthy"
  }
}
```

### Delivery Statistics
```http
GET /stats/delivery
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_sent": 1250,
  "successful": 1200,
  "failed": 50,
  "retries": 25,
  "queue_size": 3,
  "failed_deliveries": 2
}
```

### Failed Deliveries
```http
GET /stats/failed-deliveries
Authorization: Bearer <token>
```

## Webhook Testing

### Test Webhook
```http
POST /webhook/test
Content-Type: application/json
Authorization: Bearer <token>

{
  "webhook_url": "https://your-webhook.com/test"
}
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "response_text": "OK"
}
```

## WebSocket API

Connect to `ws://localhost:8001` for real-time updates.

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8001');

ws.onopen = function() {
    console.log('Connected to Symbol Alerts WebSocket');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Subscribe to Alerts
```javascript
ws.send(JSON.stringify({
    type: 'subscribe_alerts',
    user_id: 'demo_user',
    alert_ids: ['alert_1234567890', 'alert_0987654321']
}));
```

### Subscribe to Market Data
```javascript
ws.send(JSON.stringify({
    type: 'subscribe_symbols',
    symbols: ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
}));
```

### Unsubscribe
```javascript
ws.send(JSON.stringify({
    type: 'unsubscribe_alerts',
    alert_ids: ['alert_1234567890']
}));
```

### Get Alerts List
```javascript
ws.send(JSON.stringify({
    type: 'get_alerts',
    user_id: 'demo_user'
}));
```

### Ping/Pong
```javascript
ws.send(JSON.stringify({
    type: 'ping'
}));
```

## WebSocket Events

### Alert Triggered
```json
{
  "type": "alert_triggered",
  "alert_trigger": {
    "alert_id": "alert_1234567890",
    "symbol": "BTCUSDT",
    "alert_type": "price_above",
    "trigger_price": 50000.0,
    "message": "BTC above $50,000",
    "timestamp": "2024-08-15T16:30:00Z",
    "market_data": {...},
    "technical_data": {...}
  },
  "timestamp": "2024-08-15T16:30:00Z"
}
```

### Market Data Update
```json
{
  "type": "market_data_update",
  "symbol": "BTCUSDT",
  "data": {
    "symbol": "BTCUSDT",
    "price": 50000.0,
    "volume": 1000000.0,
    "timestamp": "2024-08-15T16:30:00Z"
  },
  "timestamp": "2024-08-15T16:30:00Z"
}
```

### System Status Update
```json
{
  "type": "system_status",
  "status": {
    "active_alerts": 15,
    "monitored_symbols": 8,
    "memory_usage_mb": 256.8
  },
  "timestamp": "2024-08-15T16:30:00Z"
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ALERT_NOT_FOUND",
    "message": "Alert with ID 'alert_1234567890' not found",
    "details": {
      "alert_id": "alert_1234567890"
    }
  },
  "timestamp": "2024-08-15T16:30:00Z"
}
```

### Common Error Codes

- `ALERT_NOT_FOUND` - Alert does not exist
- `INVALID_SYMBOL` - Invalid trading symbol
- `INVALID_TIMEFRAME` - Invalid timeframe specified
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `AUTHENTICATION_FAILED` - Invalid or expired token
- `VALIDATION_ERROR` - Request validation failed
- `INTERNAL_ERROR` - Server internal error

## Rate Limits

- **Default**: 60 requests per minute per user
- **Burst**: Up to 100 requests in 10 seconds
- **WebSocket**: 1000 messages per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1692115800
```

## Webhook Format

When alerts trigger, webhooks receive:

```json
{
  "event_type": "alert_triggered",
  "alert_trigger": {
    "alert_id": "alert_1234567890",
    "symbol": "BTCUSDT",
    "alert_type": "price_above",
    "trigger_price": 50000.0,
    "trigger_value": null,
    "message": "BTC above $50,000",
    "timestamp": "2024-08-15T16:30:00Z",
    "market_data": {
      "symbol": "BTCUSDT",
      "price": 50000.0,
      "volume": 1000000.0,
      "timestamp": "2024-08-15T16:30:00Z",
      "bid": 49999.0,
      "ask": 50001.0,
      "high_24h": 52000.0,
      "low_24h": 48000.0,
      "change_24h": 2000.0,
      "change_percent_24h": 4.17
    },
    "technical_data": {
      "symbol": "BTCUSDT",
      "timeframe": "5m",
      "timestamp": "2024-08-15T16:30:00Z",
      "rsi": 55.0,
      "macd": 100.0,
      "macd_signal": 95.0,
      "macd_histogram": 5.0,
      "bb_upper": 51000.0,
      "bb_middle": 50000.0,
      "bb_lower": 49000.0,
      "sma_20": 49800.0,
      "sma_50": 49500.0,
      "ema_12": 50100.0,
      "ema_26": 49900.0,
      "volume_sma": 800000.0
    }
  },
  "metadata": {
    "user_id": "demo_user",
    "alert_id": "alert_1234567890",
    "timestamp": "2024-08-15T16:30:00Z"
  }
}
```

## SDKs and Examples

### Python SDK Example
```python
import asyncio
from symbol_alerts_client import AlertsClient

async def main():
    client = AlertsClient(
        base_url="http://localhost:8000",
        api_key="your_api_key"
    )
    
    # Create alert
    alert = await client.create_alert(
        symbol="BTCUSDT",
        alert_type="price_above",
        conditions=[{
            "field": "price",
            "operator": ">",
            "value": 50000,
            "timeframe": "5m"
        }]
    )
    
    print(f"Created alert: {alert.id}")

asyncio.run(main())
```

### JavaScript SDK Example
```javascript
import { AlertsClient } from 'symbol-alerts-js';

const client = new AlertsClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your_api_key'
});

// Create alert
const alert = await client.createAlert({
    symbol: 'BTCUSDT',
    alertType: 'price_above',
    conditions: [{
        field: 'price',
        operator: '>',
        value: 50000,
        timeframe: '5m'
    }]
});

console.log('Created alert:', alert.id);
```

## Advanced Features

### LLM-Gated Signals
When LLM gating is enabled, alerts include additional fields:

```json
{
  "llm_confidence": 0.85,
  "llm_reasoning": "Strong bullish alignment across multiple timeframes with volume confirmation",
  "llm_validated": true
}
```

### Multi-Timeframe Analysis
Advanced alerts can include multi-timeframe scoring:

```json
{
  "tf_scores": {
    "5m_long": 2,
    "15m_long": 3,
    "1h_long": 2,
    "4h_long": 3
  },
  "alignment_score": 10,
  "confidence": "high"
}
```

### Microstructure Data
For supported symbols, orderbook microstructure data:

```json
{
  "book_tilt": 1.85,
  "spoof_detected": false,
  "liquidity_imbalance": 0.15
}
```

