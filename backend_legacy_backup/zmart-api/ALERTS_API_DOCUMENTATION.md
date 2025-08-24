# ZmartBot Professional Trading Alerts API Documentation

## Overview
The ZmartBot Professional Trading Alerts API provides comprehensive alert management, real-time monitoring, and reporting capabilities for cryptocurrency trading. This API supports both internal dashboard operations and external third-party integrations.

## Base URL
```
http://localhost:3400/api/v1
```

## Authentication
External API access requires an API key header:
```
X-API-Key: zmart_external_api_key_2024
```

---

## 📊 Report Generation Endpoints

### 1. Performance Report
Generate comprehensive performance analytics for alerts.

**Endpoint:** `POST /alerts/reports/performance`

**Request Body:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "symbol": "BTCUSDT"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "2024-01-01 to 2024-01-31",
    "total_alerts": 28,
    "total_triggers": 156,
    "success_rate": 87.3,
    "most_active_symbol": "BTCUSDT",
    "most_effective_alert_type": "PRICE",
    "average_response_time": "2.3s",
    "revenue_impact": "$12,450",
    "alerts_by_type": {
      "PRICE": 15,
      "TECHNICAL": 8,
      "VOLUME": 3,
      "PATTERN": 2
    },
    "triggers_by_hour": {
      "9": 12, "10": 18, "11": 15, "12": 8,
      "13": 10, "14": 22, "15": 19, "16": 14
    }
  }
}
```

### 2. Technical Analysis Report
Generate real-time technical analysis for any symbol.

**Endpoint:** `POST /alerts/reports/technical`

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "indicators": ["RSI", "MACD", "EMA", "Bollinger_Bands"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "analysis_date": "2024-01-15T10:30:00Z",
    "current_price": 117160.85,
    "indicators": {
      "RSI": {
        "value": 65.4,
        "signal": "neutral",
        "overbought": false,
        "oversold": false
      },
      "MACD": {
        "macd_line": 245.67,
        "signal_line": 198.34,
        "histogram": 47.33,
        "signal": "bullish"
      },
      "EMA": {
        "ema_12": 116850.23,
        "ema_26": 116200.45,
        "signal": "bullish"
      },
      "Bollinger_Bands": {
        "upper": 118500.12,
        "middle": 117160.85,
        "lower": 115821.58,
        "signal": "neutral"
      }
    },
    "signals": [
      "Golden Cross detected",
      "RSI approaching overbought",
      "Price near upper Bollinger Band"
    ],
    "recommendations": [
      "Consider taking profits",
      "Monitor for reversal signals",
      "Set stop loss at $115,000"
    ],
    "risk_level": "MEDIUM"
  }
}
```

### 3. Alert Analytics Report
Generate detailed analytics for alert performance.

**Endpoint:** `POST /alerts/reports/alert_analytics`

**Request Body:**
```json
{
  "alert_id": "optional-alert-id",
  "symbol": "BTCUSDT",  // Optional
  "alert_type": "PRICE"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_alerts": 15,
    "active_alerts": 12,
    "paused_alerts": 3,
    "alerts_by_type": {
      "PRICE": 8,
      "TECHNICAL": 5,
      "VOLUME": 2
    },
    "alerts_by_symbol": {
      "BTCUSDT": 6,
      "ETHUSDT": 4,
      "SOLUSDT": 3,
      "ADAUSDT": 2
    },
    "trigger_frequency": {
      "hourly": 12,
      "daily": 45,
      "weekly": 156
    },
    "average_accuracy": 85.7,
    "most_effective_conditions": [
      {
        "condition": "RSI > 70",
        "success_rate": 92.3
      },
      {
        "condition": "Price > $50,000",
        "success_rate": 88.1
      },
      {
        "condition": "Volume > 1M",
        "success_rate": 85.4
      }
    ]
  }
}
```

### 4. Notification Report
Generate delivery analytics for notification channels.

**Endpoint:** `POST /alerts/reports/notification`

**Request Body:**
```json
{
  "channel": "telegram",  // Optional
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "2024-01-01 to 2024-01-31",
    "total_notifications": 88,
    "delivery_by_channel": {
      "telegram": {
        "sent": 45,
        "delivered": 43,
        "failed": 2
      },
      "discord": {
        "sent": 23,
        "delivered": 22,
        "failed": 1
      },
      "email": {
        "sent": 12,
        "delivered": 11,
        "failed": 1
      },
      "webhook": {
        "sent": 8,
        "delivered": 8,
        "failed": 0
      }
    },
    "delivery_rate": 94.3,
    "average_delivery_time": "1.2s",
    "most_active_hours": {
      "9": 15, "10": 22, "11": 18, "12": 12,
      "13": 14, "14": 25, "15": 20, "16": 16
    },
    "failed_notifications": [
      {
        "channel": "telegram",
        "reason": "Invalid chat ID",
        "count": 2
      },
      {
        "channel": "discord",
        "reason": "Webhook expired",
        "count": 1
      }
    ]
  }
}
```

---

## 🔌 External API Endpoints

### 1. System Status
Get current system status for external monitoring.

**Endpoint:** `GET /alerts/external/status`

**Headers:**
```
X-API-Key: zmart_external_api_key_2024
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "operational",
    "active_alerts": 12,
    "uptime": "1h 23m 45s",
    "last_check": "2024-01-15T10:30:00Z",
    "api_version": "1.0.0"
  }
}
```

### 2. Create External Alert
Create alerts from external systems.

**Endpoint:** `POST /alerts/external/alert`

**Headers:**
```
X-API-Key: zmart_external_api_key_2024
Content-Type: application/json
```

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "alert_type": "PRICE",
  "conditions": {
    "threshold": 120000,
    "operator": "above",
    "timeframe": "1m"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alert_id": "uuid-string",
    "status": "created"
  }
}
```

### 3. Get External Alerts
Retrieve alerts for a specific symbol.

**Endpoint:** `GET /alerts/external/alerts/{symbol}`

**Headers:**
```
X-API-Key: zmart_external_api_key_2024
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "alert_id": "uuid-string",
      "type": "PRICE",
      "status": "ACTIVE",
      "conditions": {
        "threshold": 120000,
        "operator": "above"
      }
    }
  ]
}
```

### 4. Trigger External Alert
Manually trigger alerts for testing or external events.

**Endpoint:** `POST /alerts/external/trigger`

**Headers:**
```
X-API-Key: zmart_external_api_key_2024
Content-Type: application/json
```

**Request Body:**
```json
{
  "alert_id": "uuid-string",
  "trigger_data": {
    "price": 120500,
    "volume": 1500000,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alert_id": "uuid-string",
    "triggered_at": "2024-01-15T10:30:00Z",
    "trigger_data": {
      "price": 120500,
      "volume": 1500000
    }
  }
}
```

---

## 📱 Telegram Configuration

### Configure Telegram Notifications
**Endpoint:** `POST /alerts/config/telegram`

**Request Body:**
```json
{
  "bot_token": "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI",
  "chat_id": "-1002891569616",
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Telegram configuration successful! Test message sent.",
  "data": {
    "bot_token": "7995587461...",
    "chat_id": "-1002891569616",
    "enabled": true
  }
}
```

---

## 🔔 Alert Management

### Create Alert
**Endpoint:** `POST /alerts/create`

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "alert_type": "PRICE",
  "conditions": {
    "threshold": 120000,
    "operator": "above",
    "timeframe": "1m"
  },
  "notification_channels": ["telegram", "discord"]
}
```

### List Alerts
**Endpoint:** `GET /alerts/list`

### Delete Alert
**Endpoint:** `DELETE /alerts/{alert_id}`

### Pause/Resume Alert
**Endpoint:** `POST /alerts/{alert_id}/{pause|resume}`

---

## 📈 Usage Examples

### Python Example
```python
import requests

# API Configuration
API_BASE = "http://localhost:3400/api/v1"
API_KEY = "zmart_external_api_key_2024"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Generate Performance Report
response = requests.post(
    f"{API_BASE}/alerts/reports/performance",
    headers=HEADERS,
    json={
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
)
print(response.json())

# Create External Alert
response = requests.post(
    f"{API_BASE}/alerts/external/alert",
    headers=HEADERS,
    json={
        "symbol": "BTCUSDT",
        "alert_type": "PRICE",
        "conditions": {
            "threshold": 120000,
            "operator": "above"
        }
    }
)
print(response.json())
```

### JavaScript Example
```javascript
const API_BASE = "http://localhost:3400/api/v1";
const API_KEY = "zmart_external_api_key_2024";

// Generate Technical Report
async function generateTechnicalReport() {
    const response = await fetch(`${API_BASE}/alerts/reports/technical`, {
        method: 'POST',
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            symbol: 'BTCUSDT',
            timeframe: '1h',
            indicators: ['RSI', 'MACD', 'EMA']
        })
    });
    
    const data = await response.json();
    console.log(data);
}

// Get System Status
async function getSystemStatus() {
    const response = await fetch(`${API_BASE}/alerts/external/status`, {
        headers: {
            'X-API-Key': API_KEY
        }
    });
    
    const data = await response.json();
    console.log(data);
}
```

---

## 🚀 Integration Guide

### 1. Setup External Access
1. Use the provided API key: `zmart_external_api_key_2024`
2. Include the key in all external API requests
3. Monitor system status before making requests

### 2. Best Practices
- Implement rate limiting (max 100 requests/minute)
- Cache system status responses
- Handle API errors gracefully
- Use webhooks for real-time updates

### 3. Monitoring
- Check system status every 5 minutes
- Monitor delivery rates for notifications
- Track alert performance metrics
- Set up alerts for API failures

---

## 📞 Support

For API support and integration assistance:
- Email: support@zmartbot.com
- Documentation: https://docs.zmartbot.com
- Status Page: https://status.zmartbot.com

---

*Last Updated: January 15, 2024*
*API Version: 1.0.0*
