# 🚀 Cryptoverse API Enhanced Features Usage Guide

## 🎯 Overview

The Cryptoverse Data Extraction API has been enhanced with comprehensive production-ready features. This guide demonstrates how to use all implemented features.

## ✅ Implemented Features

### 1. 🔧 Flexible Configuration
- **Configurable Port**: Custom port selection via command line or API initialization
- **Host Binding**: Configurable host address (default: 0.0.0.0 for all interfaces)
- **Debug Mode**: Enable/disable debug mode for development
- **Log Levels**: DEBUG, INFO, WARNING, ERROR levels
- **Scheduler Control**: Option to disable automated scheduling

### 2. 🗄️ Database Integration
- **Comprehensive Storage**: 21 data source tables
- **Data Retrieval**: Advanced querying capabilities
- **Automatic Cleanup**: Scheduled database maintenance
- **Health Monitoring**: Database connection status tracking

### 3. ⏰ Automated Scheduling
- **Crypto Risk Extraction**: Every 15 minutes
- **Screener Data Collection**: Every 5 minutes
- **AI Insights Generation**: Every 30 minutes
- **Database Cleanup**: Daily at 2 AM
- **Background Processing**: Non-blocking daemon threads

### 4. 🛡️ Error Handling & Graceful Degradation
- **Custom Error Handlers**: 404 and 500 error responses
- **Detailed Error Messages**: JSON format with timestamps
- **Component Isolation**: Individual component failure handling
- **Graceful Fallbacks**: Service continues with reduced functionality

### 5. 🌐 CORS Support
- **Cross-Origin Requests**: Full CORS implementation
- **Web Client Compatibility**: React, Vue, Angular support
- **All HTTP Methods**: GET, POST, PUT, DELETE
- **Header Management**: Automatic header handling

### 6. 📝 Comprehensive Logging
- **Request Tracking**: Before/after request middleware
- **Response Logging**: Status codes and timing
- **Error Tracking**: Detailed exception logging
- **File & Console Output**: Dual logging destinations
- **Structured Format**: Timestamp, logger, level, message

### 7. 🏥 Health Monitoring
- **Basic Health Check**: `/health` endpoint
- **Comprehensive Status**: `/api/system-status` endpoint
- **Component Tracking**: Individual component health
- **Feature Status**: Real-time feature availability
- **System Metrics**: Performance and statistics

## 🚀 Quick Start

### Basic Usage
```bash
# Start with default settings (port 5002)
python src/api/cryptoverse_api.py

# Start with custom port
python src/api/cryptoverse_api.py --port 8080

# Start with debug mode
python src/api/cryptoverse_api.py --debug

# Start with custom host
python src/api/cryptoverse_api.py --host 127.0.0.1

# Start with custom log level
python src/api/cryptoverse_api.py --log-level DEBUG

# Start without automated scheduling
python src/api/cryptoverse_api.py --no-scheduler

# Combined options
python src/api/cryptoverse_api.py --port 8080 --debug --log-level DEBUG
```

### Programmatic Usage
```python
from src.api.cryptoverse_api import CryptoverseAPI

# Create API instance with custom port
api = CryptoverseAPI(port=8080)

# Run with custom configuration
api.run(
    debug=True,
    host='127.0.0.1',
    threaded=True
)
```

## 🔗 API Endpoints

### Health & Monitoring
- `GET /health` - Basic health check with component status
- `GET /api/system-status` - Comprehensive system monitoring

### Data Access
- `GET /api/crypto-risk-indicators` - Latest crypto risk data
- `GET /api/screener-data` - Symbol screening data
- `GET /api/ai-insights` - Generated market insights
- `GET /api/historical-data` - Time-series data access
- `GET /api/analyze-symbol` - Individual symbol analysis
- `GET /api/extraction-status` - Data pipeline status
- `GET /api/data-sources` - Available data sources

## 📊 Health Check Response Example

```json
{
  "status": "healthy",
  "service": "Cryptoverse Data Extraction API",
  "timestamp": "2025-01-04T22:35:21.179Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "crypto_risk_extractor": "healthy",
    "screener_extractor": "healthy",
    "insight_generator": "healthy",
    "scheduler": "healthy",
    "flask": "healthy"
  },
  "features": {
    "automated_scheduling": true,
    "database_integration": true,
    "error_handling": true,
    "cors_support": true,
    "logging": true,
    "health_monitoring": true,
    "flexible_configuration": true
  },
  "data_sources": 21,
  "endpoints": 12,
  "uptime": "active"
}
```

## 🎯 System Status Response Example

```json
{
  "status": "healthy",
  "service": "Cryptoverse Data Extraction API",
  "timestamp": "2025-01-04T22:35:21.179Z",
  "version": "1.0.0",
  "port": 5002,
  "database_stats": {
    "connection": "healthy",
    "data_sources": 21,
    "last_extraction": "active"
  },
  "scheduler_stats": {
    "available": true,
    "tasks_configured": 4,
    "background_thread": "active",
    "schedule_intervals": {
      "crypto_risk_extraction": "15 minutes",
      "screener_extraction": "5 minutes",
      "insights_generation": "30 minutes",
      "database_cleanup": "daily at 2 AM"
    }
  },
  "feature_status": {
    "automated_scheduling": {
      "enabled": true,
      "tasks": 4,
      "intervals": {...}
    },
    "database_integration": {
      "enabled": true,
      "data_sources": 21
    },
    "error_handling": {
      "enabled": true,
      "graceful_degradation": true,
      "detailed_responses": true
    },
    "cors_support": {
      "enabled": true,
      "cross_origin_requests": true
    },
    "logging": {
      "enabled": true,
      "level": "INFO",
      "request_tracking": true,
      "error_tracking": true
    },
    "health_monitoring": {
      "enabled": true,
      "endpoints": ["/health", "/api/system-status"],
      "component_tracking": true
    },
    "flexible_configuration": {
      "enabled": true,
      "configurable_port": true,
      "debug_mode": true,
      "command_line_args": true
    }
  }
}
```

## 📝 Logging Output Example

```
2025-01-04 22:35:21,177 - INFO - 🚀 Starting Cryptoverse API server
2025-01-04 22:35:21,177 - INFO -    📍 Host: 0.0.0.0
2025-01-04 22:35:21,177 - INFO -    🔌 Port: 5002
2025-01-04 22:35:21,177 - INFO -    🐛 Debug: False
2025-01-04 22:35:21,177 - INFO -    🧵 Threaded: True
2025-01-04 22:35:21,177 - INFO -    📊 Features enabled:
2025-01-04 22:35:21,177 - INFO -       - Automated Scheduling: ✅
2025-01-04 22:35:21,177 - INFO -       - Database Integration: ✅
2025-01-04 22:35:21,177 - INFO -       - Error Handling: ✅
2025-01-04 22:35:21,177 - INFO -       - CORS Support: ✅
2025-01-04 22:35:21,177 - INFO -       - Request Logging: ✅
2025-01-04 22:35:21,177 - INFO -       - Health Monitoring: ✅
2025-01-04 22:35:21,179 - INFO - 🌐 GET /health - Remote: 127.0.0.1
2025-01-04 22:35:21,179 - INFO - 📤 Response 200 for GET /health
```

## 🛠️ Development & Testing

### Run Demo
```bash
cd cryptoverse-module
python demo_enhanced_api.py
```

### Test Health Endpoints
```bash
# Basic health check
curl http://localhost:5002/health

# Comprehensive system status
curl http://localhost:5002/api/system-status
```

### View Help
```bash
python src/api/cryptoverse_api.py --help
```

## 🎉 Production Deployment

The API is production-ready with:
- ✅ Comprehensive error handling
- ✅ Graceful degradation
- ✅ Health monitoring
- ✅ Request/response logging
- ✅ CORS support for web clients
- ✅ Flexible configuration options
- ✅ Automated background processing
- ✅ Database integration with cleanup
- ✅ Component isolation and monitoring

## 📞 Support

All features have been implemented and tested. The API provides comprehensive functionality for:
- Real-time crypto risk monitoring
- Automated data extraction
- AI-powered market insights
- Health monitoring and system status
- Production-ready deployment

---

**🚀 The Cryptoverse API is ready for production deployment with all requested features implemented!**