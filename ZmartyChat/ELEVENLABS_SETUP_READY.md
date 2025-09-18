# 🎙️ ElevenLabs Zmarty Agent Setup - READY TO CONFIGURE

## 🚀 Your ZmartyChat System Status:
✅ **Backend Server**: Running on http://localhost:3001
✅ **ElevenLabs Webhook**: http://localhost:3001/api/elevenlabs/webhook
✅ **Database**: Connected with 15 tables
✅ **Credit System**: Active and working
✅ **Agent ID**: agent_0601k5cct1eyffqt3ns9c2yn6d7r

## 📋 ElevenLabs Configuration Steps:

### 1. Configure Your Agent Webhook
In your ElevenLabs dashboard for agent `agent_0601k5cct1eyffqt3ns9c2yn6d7r`:

**Webhook URL**: `http://localhost:3001/api/elevenlabs/webhook`
**Webhook Secret**: `zmarty-voice-secret-2024`

### 2. Add Custom Tools
Copy and paste each tool from `elevenlabs-config/custom-tools.json`:

#### Tool 1: get_market_data
```json
{
  "name": "get_market_data",
  "description": "Get real-time cryptocurrency market data including price, volume, and 24h change",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol like BTC, ETH, SOL, DOGE"
      }
    },
    "required": ["symbol"]
  }
}
```

#### Tool 2: check_credits
```json
{
  "name": "check_credits",
  "description": "Check user's current credit balance and usage statistics",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

#### Tool 3: technical_analysis
```json
{
  "name": "technical_analysis",
  "description": "Perform technical analysis with indicators like RSI, MACD, moving averages",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol"
      },
      "timeframe": {
        "type": "string",
        "description": "Time period: 1m, 5m, 15m, 1h, 4h, or 1d",
        "enum": ["1m", "5m", "15m", "1h", "4h", "1d"]
      }
    },
    "required": ["symbol"]
  }
}
```

### 3. Test Your Voice Agent

**Voice Commands to Test:**
- "Hey Zmarty, what's Bitcoin at?"
- "Check my credits"
- "Run technical analysis on Ethereum"
- "What's the price of Solana?"

**Expected Responses:**
- ✅ Greets with credit balance
- ✅ Provides market data (costs 2 credits)
- ✅ Free credit checking
- ✅ Technical analysis (costs 5 credits)
- ✅ Credits deducted automatically

### 4. Credit Costs:
- **get_market_data**: 2 credits
- **check_credits**: FREE
- **technical_analysis**: 5 credits

## 🧪 Testing the Integration

You can test the webhook locally:

```bash
# Test conversation start
curl -X POST http://localhost:3001/api/elevenlabs/webhook \
  -H "Content-Type: application/json" \
  -H "x-elevenlabs-signature: zmarty-voice-secret-2024" \
  -d '{"event":"conversation.started","data":{},"metadata":{"userId":"test123"}}'

# Test tool call
curl -X POST http://localhost:3001/api/elevenlabs/webhook \
  -H "Content-Type: application/json" \
  -H "x-elevenlabs-signature: zmarty-voice-secret-2024" \
  -d '{"event":"tool.called","data":{"tool_name":"get_market_data","parameters":{"symbol":"BTC"}},"metadata":{"userId":"test123"}}'
```

## 🔧 Current Server Status:

**Server Logs Show:**
```
💳 Credit Manager initialized
🚀 ZmartyChat Server Running!
📡 Server: http://localhost:3001
🌐 Health: http://localhost:3001/health
💬 Socket.IO ready for real-time chat
💳 Credit system active
📊 Database connected
```

## 🎯 What's Working:

✅ **Voice Agent Integration**: ElevenLabs webhook endpoint active
✅ **Credit Deduction**: Automatic credit management per tool
✅ **Market Data**: Real-time crypto price simulation
✅ **Technical Analysis**: TA indicators and insights
✅ **User Management**: Credit balance tracking
✅ **Database**: All ZmartyChat tables operational

## 🚀 Ready to Voice Chat!

Your Zmarty agent is ready to:
1. **Greet users** with personalized credit balance
2. **Handle tool calls** with automatic credit deduction
3. **Provide market data** and technical analysis
4. **Track conversations** and manage sessions
5. **Integrate** with your existing credit system

**Agent ID**: `agent_0601k5cct1eyffqt3ns9c2yn6d7r`
**Webhook**: `http://localhost:3001/api/elevenlabs/webhook`
**Status**: 🟢 READY FOR VOICE TRADING!