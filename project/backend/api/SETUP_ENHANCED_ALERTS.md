# Enhanced Alerts System - Setup Guide

## 🚀 Quick Start

### Step 1: Start the Backend Server

```bash
# Navigate to your backend directory
cd project/backend/api

# Install dependencies (if needed)
pip install flask flask-cors requests

# Start the Flask server
python app.py
# or
flask run
```

### Step 2: Test the API

```bash
# In a new terminal, test the enhanced alerts API
python test_enhanced_alerts.py
```

You should see:
```
🧪 Testing Enhanced Alerts API...
==================================================

1. Testing GET /api/enhanced-alerts/state/BTCUSDT
✅ Success: True
   Symbol: BTCUSDT
   Timeframe: 1h
   Sentiment: {'bullish': 40, 'neutral': 40, 'bearish': 20}

2. Testing GET /api/enhanced-alerts/events/BTCUSDT
✅ Success: True
   Events count: 1

3. Testing POST /api/enhanced-alerts/process/BTCUSDT
✅ Success: True
   Status: success
   Changes detected: 1
   Cross alerts: 1

4. Testing GET /api/enhanced-alerts/summary/BTCUSDT
✅ Success: True
   Symbol: BTCUSDT
   Total events: 1
   SSE clients: 0

5. Testing GET /api/enhanced-alerts/cooldowns/BTCUSDT
✅ Success: True
   Cooldowns count: 1

6. Testing GET /api/enhanced-alerts/stats
✅ Success: True
   Active cooldowns: 0
   Symbols with cooldowns: 0

==================================================
🎉 Enhanced Alerts API Test Complete!
```

### Step 3: Start the Frontend

```bash
# In another terminal, navigate to frontend
cd project/frontend/dashboard

# Install dependencies (if needed)
npm install

# Start the frontend
npm start
```

### Step 4: View Enhanced Alerts

1. Open your browser to: `http://localhost:3400`
2. Click "Enhanced Alerts" in the sidebar
3. Or navigate directly to: `http://localhost:3400/enhanced-alerts`

## 🧪 Testing the Scheduler

```bash
# Test API connection
python scripts/run_enhanced_alerts.py --test

# Test single symbol processing
python scripts/run_enhanced_alerts.py --single

# Test all symbols
python scripts/run_enhanced_alerts.py

# Test specific symbols and timeframes
python scripts/run_enhanced_alerts.py --symbols BTCUSDT ETHUSDT --timeframes 1h 4h
```

## 📋 What You'll See

### Frontend Dashboard:
- **Enhanced Alerts Card** with real-time updates
- **Market sentiment analysis** with color-coded bars
- **Cross-signals badges** when patterns are detected
- **Expandable indicator grid** with status chips
- **Connection status** (green dot when connected)

### Demo Data Includes:
- **RSI**: Neutral (50)
- **MACD**: Bullish (0.5)
- **EMA Crossovers**: Neutral
- **Bollinger Bands**: Normal breakout
- **Momentum**: Bullish (0.7 strength)
- **Sentiment**: 40% Bullish, 40% Neutral, 20% Bearish

## 🔧 API Endpoints

All endpoints are available at `http://localhost:5000/api/enhanced-alerts/`:

- `GET /state/<symbol>` - Get symbol state
- `GET /events/<symbol>` - Get alert events
- `GET /stream` - SSE stream for real-time updates
- `POST /process/<symbol>` - Manual processing
- `GET /summary/<symbol>` - Comprehensive summary
- `GET /cooldowns/<symbol>` - Cooldown status
- `GET /stats` - System statistics

## 🎯 Cross-Signals Patterns

The system detects these patterns:
1. **EMA Bullish Cross** (30min cooldown)
2. **MACD Bullish Flip** (30min cooldown)
3. **RSI Recovery** (45min cooldown)
4. **Bollinger Squeeze Breakout** (60min cooldown)
5. **Golden Cross** (2hr cooldown)
6. **Death Cross** (2hr cooldown)
7. **Volume Spike** (15min cooldown)

## 🚨 Troubleshooting

### Backend Issues:
```bash
# Check if Flask is running
curl http://localhost:5000/api/enhanced-alerts/stats

# Check logs
tail -f enhanced_alerts.log

# Restart server
pkill -f "python.*app.py"
python app.py
```

### Frontend Issues:
```bash
# Clear cache and restart
npm run build
npm start

# Check console for errors
# Open browser dev tools (F12)
```

### Import Errors:
```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/zmartbot/project/backend/api/src"

# Or run from the correct directory
cd project/backend/api
python scripts/run_enhanced_alerts.py
```

## 📊 Monitoring

### Logs:
- **Backend**: `enhanced_alerts.log`
- **Frontend**: Browser console (F12)

### Health Checks:
```bash
# API health
curl http://localhost:5000/api/enhanced-alerts/stats

# SSE connection
curl -N http://localhost:5000/api/enhanced-alerts/stream
```

## 🔄 Next Steps

1. **Test the demo** to see everything working
2. **Integrate with real data** by connecting your existing services
3. **Set up cron jobs** for automated processing
4. **Customize patterns** and cooldown periods
5. **Add more symbols** and timeframes

## 🎉 Success Indicators

✅ **Backend**: All API tests pass  
✅ **Frontend**: Enhanced alerts card loads with demo data  
✅ **SSE**: Real-time connection established  
✅ **Scheduler**: Can process symbols successfully  

Your enhanced alerts system is now ready! 🚀
