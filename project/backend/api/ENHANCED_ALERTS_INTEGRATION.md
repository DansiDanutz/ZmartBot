# Enhanced Alerts System Integration Guide

## Overview

This guide explains how to integrate the new Enhanced Alerts System with your existing ZmartBot alerts infrastructure. The enhanced system adds:

- **Normalized Technical Analysis**: Consistent indicator status mapping across all 21 indicators
- **Cross-Signals Engine**: Advanced pattern detection with cooldown and hysteresis
- **Real-time Updates**: Server-Sent Events (SSE) for instant UI updates
- **Enhanced Sentiment Analysis**: Derived from normalized indicators
- **Screenshot Integration**: Automatic capture for strong alerts

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Enhanced       │    │   Existing      │
│   Components    │◄──►│   Alerts API     │◄──►│   ZmartBot      │
│                 │    │                  │    │   Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SSE Stream    │    │   Core Logic     │    │   Technical     │
│   Real-time     │    │   normalizeTa    │    │   Indicators    │
│   Updates       │    │   applyDiff      │    │   ChatGPT       │
│                 │    │   engine         │    │   Telegram      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## New Components Added

### 1. Core Logic (`src/lib/alerts/`)

- **`normalizeTa.py`**: Normalizes 21 technical indicators into consistent format
- **`applyDiff.py`**: Detects indicator status changes and generates events
- **`engine.py`**: Cross-signals evaluation with cooldown and hysteresis
- **`cooldown.py`**: Manages alert cooldowns to prevent noise

### 2. Enhanced Service (`src/lib/services/enhanced_alerts_service.py`)

- Integrates with existing ZmartBot services
- Manages symbol states and alert events
- Handles SSE client registration and updates
- Coordinates with existing alert systems

### 3. API Routes (`src/routes/enhanced_alerts.py`)

- `/api/enhanced-alerts/state/<symbol>`: Get current symbol state
- `/api/enhanced-alerts/events/<symbol>`: Get alert events
- `/api/enhanced-alerts/stream`: SSE stream for real-time updates
- `/api/enhanced-alerts/process/<symbol>`: Manual trigger processing
- `/api/enhanced-alerts/summary/<symbol>`: Comprehensive summary
- `/api/enhanced-alerts/cooldowns/<symbol>`: Cooldown management

### 4. Frontend Components

- **`EnhancedAlertsCard.jsx`**: Updated with SSE integration
- **`EnhancedAlertsSystem.css`**: New styling for enhanced features

## Integration Steps

### Step 1: Register Enhanced Routes

Add to your main Flask app:

```python
# In your main app file
from src.routes.enhanced_alerts import init_enhanced_alerts_routes

# Register the enhanced alerts routes
init_enhanced_alerts_routes(app)
```

### Step 2: Update Frontend

Replace or enhance your existing alerts components:

```jsx
// Use the enhanced alerts card
import EnhancedAlertsCard from './components/EnhancedAlertsCard';

// In your alerts page
<EnhancedAlertsCard 
  symbol="BTCUSDT" 
  timeframe="1h" 
  defaultExpanded={true} 
/>
```

### Step 3: Configure Scheduler

Set up cron jobs for automated processing:

```bash
# 15-minute alerts
*/15 * * * * cd /path/to/zmartbot && python scripts/run_enhanced_alerts.py --timeframes 15m

# 1-hour alerts  
0 * * * * cd /path/to/zmartbot && python scripts/run_enhanced_alerts.py --timeframes 1h

# 4-hour alerts
0 */4 * * * cd /path/to/zmartbot && python scripts/run_enhanced_alerts.py --timeframes 4h

# Daily alerts
5 0 * * * cd /path/to/zmartbot && python scripts/run_enhanced_alerts.py --timeframes 1d
```

### Step 4: Environment Variables

Add these to your environment:

```bash
# Enhanced Alerts Configuration
ENHANCED_ALERTS_ENABLED=true
ENHANCED_ALERTS_DEBUG=false
ENHANCED_ALERTS_SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT
ENHANCED_ALERTS_TIMEFRAMES=15m,1h,4h,1d

# Screenshot Configuration (optional)
SCREENSHOT_API_URL=https://your-screenshot-service.com
SCREENSHOT_API_KEY=your-api-key
```

## Cross-Signals Rules

The enhanced system includes these cross-signal patterns:

### 1. EMA Bullish Cross
- **Trigger**: EMA 9/21 crosses from neutral/bearish to bullish
- **Cooldown**: 30 minutes
- **Score**: 0.6
- **Severity**: Warning

### 2. MACD Bullish Flip
- **Trigger**: MACD flips from neutral/bearish to bullish
- **Cooldown**: 30 minutes
- **Score**: 0.45
- **Severity**: Info

### 3. RSI Recovery
- **Trigger**: RSI recovers from oversold (<30) to >35
- **Cooldown**: 45 minutes
- **Score**: 0.35
- **Severity**: Info

### 4. Bollinger Squeeze Breakout
- **Trigger**: BB squeeze with momentum breakout
- **Cooldown**: 60 minutes
- **Score**: 0.8
- **Severity**: Strong

### 5. Golden Cross
- **Trigger**: EMA golden cross detection
- **Cooldown**: 2 hours
- **Score**: 0.9
- **Severity**: Strong

### 6. Death Cross
- **Trigger**: EMA death cross detection
- **Cooldown**: 2 hours
- **Score**: 0.9
- **Severity**: Strong

### 7. Volume Spike
- **Trigger**: Volume >2x normal
- **Cooldown**: 15 minutes
- **Score**: 0.5
- **Severity**: Warning

## API Usage Examples

### Get Symbol State
```bash
curl "http://localhost:5000/api/enhanced-alerts/state/BTCUSDT?tf=1h"
```

### Get Alert Events
```bash
curl "http://localhost:5000/api/enhanced-alerts/events/BTCUSDT?tf=1h&limit=10"
```

### Manual Processing
```bash
curl -X POST "http://localhost:5000/api/enhanced-alerts/process/BTCUSDT" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": "1h"}'
```

### SSE Stream
```javascript
const eventSource = new EventSource('/api/enhanced-alerts/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## Monitoring and Debugging

### Logs
Enhanced alerts logs are written to `enhanced_alerts.log`:

```bash
tail -f enhanced_alerts.log
```

### Health Check
```bash
curl "http://localhost:5000/api/enhanced-alerts/stats"
```

### Cooldown Status
```bash
curl "http://localhost:5000/api/enhanced-alerts/cooldowns/BTCUSDT?tf=1h"
```

## Performance Considerations

### Memory Usage
- Symbol states are stored in memory (can be moved to Redis)
- Cooldowns are in-memory (can be moved to Redis)
- Events are limited to 500 per symbol/timeframe

### Processing Time
- Single symbol/timeframe: ~1-2 seconds
- Full batch (10 symbols × 4 timeframes): ~30-60 seconds

### SSE Connections
- Each client maintains one SSE connection
- Heartbeats every 25 seconds
- Automatic reconnection on errors

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure src directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/zmartbot/project/backend/api/src"
   ```

2. **SSE Connection Issues**
   - Check CORS settings
   - Verify proxy configuration
   - Check browser console for errors

3. **Processing Failures**
   - Check existing services are running
   - Verify API keys and endpoints
   - Check logs for specific errors

### Debug Mode
Enable debug logging:

```python
import logging
logging.getLogger('lib.alerts').setLevel(logging.DEBUG)
```

## Migration from Existing System

The enhanced system is designed to work alongside your existing alerts:

1. **Gradual Migration**: Start with a few symbols
2. **A/B Testing**: Compare results with existing system
3. **Fallback Support**: Falls back to existing APIs if enhanced fails
4. **Data Preservation**: All existing data remains intact

## Future Enhancements

### Planned Features
- Redis integration for production scaling
- Advanced pattern recognition
- Machine learning integration
- Multi-timeframe consensus
- Historical analytics

### Customization
- Add custom cross-signal rules
- Modify cooldown periods
- Custom indicator normalization
- Enhanced screenshot integration

## Support

For issues or questions:
1. Check the logs first
2. Review this integration guide
3. Test with single symbol/timeframe
4. Verify all dependencies are installed

## Conclusion

The Enhanced Alerts System provides a robust foundation for advanced trading alerts while maintaining compatibility with your existing ZmartBot infrastructure. The modular design allows for easy customization and future enhancements.
