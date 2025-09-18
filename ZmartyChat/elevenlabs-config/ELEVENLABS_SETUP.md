# 🎙️ ElevenLabs Agent Setup Guide for Zmarty

## 📋 Quick Setup Steps

### 1. Webhook Configuration

In your ElevenLabs Agent settings, configure the webhook:

**Webhook URL:**
```
https://your-domain.com/api/elevenlabs/webhook
```

For local testing with ngrok:
```
https://your-ngrok-id.ngrok.io/api/elevenlabs/webhook
```

**Webhook Secret (Header):**
- Header Name: `X-ElevenLabs-Signature`
- Secret Value: `zmarty-voice-secret-2024`

**Events to Subscribe:**
- ✅ conversation.started
- ✅ conversation.ended
- ✅ tool.called
- ✅ user.spoke
- ✅ agent.spoke
- ✅ error

### 2. Custom Tools Configuration

Copy and paste each tool into the ElevenLabs Custom Tools section:

#### Tool 1: Get Market Data
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

#### Tool 2: Technical Analysis
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

#### Tool 3: Check Credits
```json
{
  "name": "check_credits",
  "description": "Check user's credit balance and usage",
  "parameters": {
    "type": "object",
    "properties": {
      "userId": {
        "type": "string",
        "description": "User identifier"
      }
    },
    "required": ["userId"]
  }
}
```

#### Tool 4: Multi-Agent Consensus
```json
{
  "name": "multi_agent_consensus",
  "description": "Get trading consensus from multiple AI agents for better decision making",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Trading question or analysis request"
      },
      "symbol": {
        "type": "string",
        "description": "Optional cryptocurrency symbol for focused analysis"
      }
    },
    "required": ["query"]
  }
}
```

#### Tool 5: Set Price Alert
```json
{
  "name": "set_price_alert",
  "description": "Set a price alert notification for when a cryptocurrency reaches a target price",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol"
      },
      "targetPrice": {
        "type": "number",
        "description": "Target price in USD"
      },
      "direction": {
        "type": "string",
        "description": "Trigger when price goes above or below target",
        "enum": ["above", "below"]
      }
    },
    "required": ["symbol", "targetPrice", "direction"]
  }
}
```

#### Tool 6: Portfolio Analysis
```json
{
  "name": "portfolio_analysis",
  "description": "Analyze portfolio performance, allocation, and get recommendations",
  "parameters": {
    "type": "object",
    "properties": {
      "userId": {
        "type": "string",
        "description": "User identifier"
      }
    },
    "required": ["userId"]
  }
}
```

#### Tool 7: Get Trading Signals
```json
{
  "name": "get_trading_signals",
  "description": "Get AI-powered buy/sell signals based on market conditions",
  "parameters": {
    "type": "object",
    "properties": {
      "symbols": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of cryptocurrency symbols to analyze"
      },
      "riskLevel": {
        "type": "string",
        "description": "Risk tolerance level",
        "enum": ["conservative", "moderate", "aggressive"]
      }
    },
    "required": ["symbols"]
  }
}
```

#### Tool 8: Execute Trade (Paper Trading)
```json
{
  "name": "execute_trade",
  "description": "Execute a simulated paper trade for practice and tracking",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol"
      },
      "action": {
        "type": "string",
        "description": "Trade action",
        "enum": ["buy", "sell"]
      },
      "amount": {
        "type": "number",
        "description": "Amount in USD or quantity"
      },
      "userId": {
        "type": "string",
        "description": "User identifier"
      }
    },
    "required": ["symbol", "action", "amount", "userId"]
  }
}
```

### 3. Voice Settings

Configure Zmarty's voice personality:

- **Voice Model:** Choose a mature, warm male voice (age 55-70 sound)
- **Stability:** 0.75 (consistent but natural)
- **Clarity:** 0.85 (clear articulation)
- **Style Exaggeration:** 0.5 (balanced)
- **Speaker Boost:** ON

### 4. Agent Behavior Settings

- **Response Time:** 500ms - 1s (thoughtful pauses)
- **Interruption Sensitivity:** Medium
- **End of Speech Detection:** 1.5 seconds
- **Background Noise Suppression:** High
- **Echo Cancellation:** Enabled

### 5. System Prompt (Already Provided)

Use the PRO SYSTEM PROMPT you've already configured.

### 6. Environment Variables

Add these to your `.env` file:

```env
# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_AGENT_ID=your_agent_id
ELEVENLABS_VOICE_ID=your_selected_voice_id
ELEVENLABS_WEBHOOK_URL=https://your-domain.com/api/elevenlabs/webhook
ELEVENLABS_WEBHOOK_SECRET=zmarty-voice-secret-2024
```

### 7. Testing the Integration

1. **Start your backend server:**
```bash
npm run dev
```

2. **Test webhook with curl:**
```bash
curl -X POST http://localhost:3001/api/elevenlabs/webhook \
  -H "Content-Type: application/json" \
  -H "X-ElevenLabs-Signature: zmarty-voice-secret-2024" \
  -d '{
    "event": "tool.called",
    "data": {
      "tool": "get_market_data",
      "parameters": {"symbol": "BTC"}
    },
    "metadata": {
      "userId": "test-user-123"
    }
  }'
```

3. **Expected Response:**
```json
{
  "success": true,
  "data": {...},
  "speech": "BTC is trading at $...",
  "metadata": {
    "creditsUsed": 2
  }
}
```

### 8. Integration with Main App

Update your `main-integration.js` to include the webhook:

```javascript
import elevenLabsWebhook from './api/elevenlabs-webhook.js';

// Add to your Express app
app.use('/api/elevenlabs', elevenLabsWebhook);
```

### 9. Testing Voice Conversation

1. Call the ElevenLabs phone number or use the widget
2. Say: "Hey Zmarty, what's the price of Bitcoin?"
3. Zmarty should respond with current price and credit usage
4. Say: "Run a technical analysis on ETH"
5. Zmarty should ask for consent (5 credits) before proceeding

### 10. Monitoring & Logs

Monitor webhook calls in your console:
- `📞 ElevenLabs Event: conversation.started`
- `🔧 Tool called: get_market_data`
- `💳 Credits deducted: 2`

## 🔧 Troubleshooting

### Webhook Not Receiving Events
- Check ngrok is running: `ngrok http 3001`
- Verify webhook URL in ElevenLabs dashboard
- Check signature header matches

### Tools Not Working
- Verify tool names match exactly
- Check parameter types (string, number, array)
- Monitor console for error logs

### Voice Quality Issues
- Adjust stability/clarity settings
- Check background noise suppression
- Verify internet connection speed

### Credit System Issues
- Ensure Supabase is connected
- Check user has sufficient credits
- Verify deduction logic in webhook

## 📊 Credit Costs Reference

| Action | Credits | Voice Command Example |
|--------|---------|----------------------|
| Market Data | 2 | "What's the price of BTC?" |
| Technical Analysis | 5 | "Analyze ETH technically" |
| Check Credits | 0 | "How many credits do I have?" |
| Price Alert | 1 | "Alert me when BTC hits 100k" |
| Portfolio Analysis | 15 | "Analyze my portfolio" |
| Trading Signals | 10 | "Give me trading signals" |
| Multi-Agent Consensus | 50 | "Get full consensus on Bitcoin" |

## 🎯 Best Practices

1. **Always estimate credits** before expensive operations
2. **Get user consent** for operations over 10 credits
3. **Provide credit receipts** after each operation
4. **Offer alternatives** when user is low on credits
5. **Log all interactions** for MD transcripts
6. **Trigger addiction hooks** appropriately
7. **Maintain conversation context** across tools

## 🚀 Advanced Features

### Custom Intents
Add these to help Zmarty understand context better:

- "quick check" → Use minimal credits
- "deep dive" → Full analysis with consensus
- "paper trade" → Simulation mode
- "real analysis" → Live market data

### Voice Shortcuts
Configure these voice commands:

- "Zmarty, quick BTC" → Fast market data (2 credits)
- "Zmarty, full analysis" → Complete multi-agent (50 credits)
- "Zmarty, my credits" → Check balance (free)
- "Zmarty, help" → List available commands

---

**Ready to Launch!** 🚀

Your Zmarty voice agent is now fully configured with:
- ✅ All trading tools
- ✅ Credit management
- ✅ Webhook integration
- ✅ Personalized responses
- ✅ Addiction mechanics

Start testing with voice commands and monitor the credit usage in real-time!