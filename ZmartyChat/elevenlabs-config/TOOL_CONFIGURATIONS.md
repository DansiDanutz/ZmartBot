# 🔧 ElevenLabs Tool Configurations for Zmarty Agent

## Tool Configuration Format for ElevenLabs

### **Tool 1: Get Market Data**

**Basic Settings:**
- **Name**: `get_market_data`
- **Description**: `Get real-time cryptocurrency market data including current price, 24h change, and volume for any crypto symbol`
- **Method**: `POST`
- **URL**: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`
- **Response timeout**: `20` seconds
- **Disable interruptions**: ✅ Checked
- **Pre-tool speech**: `Auto`

**Headers:**
```
Content-Type: application/json
x-elevenlabs-signature: zmarty-voice-secret-2024
```

**Query Parameters:**
- **symbol** (required): `Cryptocurrency symbol like BTC, ETH, SOL, DOGE`

**JSON Configuration:**
```json
{
  "name": "get_market_data",
  "description": "Get real-time cryptocurrency market data including current price, 24h change, and volume for any crypto symbol",
  "method": "POST",
  "url": "https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook",
  "timeout": 20,
  "disable_interruptions": true,
  "headers": {
    "Content-Type": "application/json",
    "x-elevenlabs-signature": "zmarty-voice-secret-2024"
  },
  "parameters": {
    "symbol": {
      "type": "string",
      "description": "Cryptocurrency symbol like BTC, ETH, SOL, DOGE",
      "required": true
    }
  }
}
```

---

### **Tool 2: Check Credits**

**Basic Settings:**
- **Name**: `check_credits`
- **Description**: `Check the user's current credit balance and usage statistics for their ZmartyChat account`
- **Method**: `POST`
- **URL**: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`
- **Response timeout**: `15` seconds
- **Disable interruptions**: ⬜ Unchecked
- **Pre-tool speech**: `Auto`

**Headers:**
```
Content-Type: application/json
x-elevenlabs-signature: zmarty-voice-secret-2024
```

**Query Parameters:**
- **userId** (optional): `User identifier for credit lookup`

**JSON Configuration:**
```json
{
  "name": "check_credits",
  "description": "Check the user's current credit balance and usage statistics for their ZmartyChat account",
  "method": "POST",
  "url": "https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook",
  "timeout": 15,
  "disable_interruptions": false,
  "headers": {
    "Content-Type": "application/json",
    "x-elevenlabs-signature": "zmarty-voice-secret-2024"
  },
  "parameters": {
    "userId": {
      "type": "string",
      "description": "User identifier for credit lookup",
      "required": false
    }
  }
}
```

---

### **Tool 3: Technical Analysis**

**Basic Settings:**
- **Name**: `technical_analysis`
- **Description**: `Perform comprehensive technical analysis with indicators like RSI, MACD, moving averages, and provide trading insights`
- **Method**: `POST`
- **URL**: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`
- **Response timeout**: `30` seconds
- **Disable interruptions**: ✅ Checked
- **Pre-tool speech**: `Auto`

**Headers:**
```
Content-Type: application/json
x-elevenlabs-signature: zmarty-voice-secret-2024
```

**Query Parameters:**
- **symbol** (required): `Cryptocurrency symbol for analysis`
- **timeframe** (optional): `Time period: 1m, 5m, 15m, 1h, 4h, or 1d`

**JSON Configuration:**
```json
{
  "name": "technical_analysis",
  "description": "Perform comprehensive technical analysis with indicators like RSI, MACD, moving averages, and provide trading insights",
  "method": "POST",
  "url": "https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook",
  "timeout": 30,
  "disable_interruptions": true,
  "headers": {
    "Content-Type": "application/json",
    "x-elevenlabs-signature": "zmarty-voice-secret-2024"
  },
  "parameters": {
    "symbol": {
      "type": "string",
      "description": "Cryptocurrency symbol for analysis",
      "required": true
    },
    "timeframe": {
      "type": "string",
      "description": "Time period: 1m, 5m, 15m, 1h, 4h, or 1d",
      "required": false,
      "enum": ["1m", "5m", "15m", "1h", "4h", "1d"]
    }
  }
}
```

---

### **Tool 4: Set Price Alert**

**Basic Settings:**
- **Name**: `set_price_alert`
- **Description**: `Set up price alerts to notify when a cryptocurrency reaches your target price level`
- **Method**: `POST`
- **URL**: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`
- **Response timeout**: `20` seconds
- **Disable interruptions**: ⬜ Unchecked
- **Pre-tool speech**: `Auto`

**Headers:**
```
Content-Type: application/json
x-elevenlabs-signature: zmarty-voice-secret-2024
```

**Query Parameters:**
- **symbol** (required): `Cryptocurrency symbol`
- **targetPrice** (required): `Target price in USD`
- **direction** (required): `Trigger when price goes above or below target`

**JSON Configuration:**
```json
{
  "name": "set_price_alert",
  "description": "Set up price alerts to notify when a cryptocurrency reaches your target price level",
  "method": "POST",
  "url": "https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook",
  "timeout": 20,
  "disable_interruptions": false,
  "headers": {
    "Content-Type": "application/json",
    "x-elevenlabs-signature": "zmarty-voice-secret-2024"
  },
  "parameters": {
    "symbol": {
      "type": "string",
      "description": "Cryptocurrency symbol",
      "required": true
    },
    "targetPrice": {
      "type": "number",
      "description": "Target price in USD",
      "required": true
    },
    "direction": {
      "type": "string",
      "description": "Trigger when price goes above or below target",
      "required": true,
      "enum": ["above", "below"]
    }
  }
}
```

---

### **Tool 5: Multi-Agent Consensus**

**Basic Settings:**
- **Name**: `multi_agent_consensus`
- **Description**: `Get trading consensus from multiple AI agents for comprehensive market analysis and decision making`
- **Method**: `POST`
- **URL**: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`
- **Response timeout**: `45` seconds
- **Disable interruptions**: ✅ Checked
- **Pre-tool speech**: `Auto`

**Headers:**
```
Content-Type: application/json
x-elevenlabs-signature: zmarty-voice-secret-2024
```

**Query Parameters:**
- **query** (required): `Trading question or analysis request`
- **symbol** (optional): `Cryptocurrency symbol for focused analysis`

**JSON Configuration:**
```json
{
  "name": "multi_agent_consensus",
  "description": "Get trading consensus from multiple AI agents for comprehensive market analysis and decision making",
  "method": "POST",
  "url": "https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook",
  "timeout": 45,
  "disable_interruptions": true,
  "headers": {
    "Content-Type": "application/json",
    "x-elevenlabs-signature": "zmarty-voice-secret-2024"
  },
  "parameters": {
    "query": {
      "type": "string",
      "description": "Trading question or analysis request",
      "required": true
    },
    "symbol": {
      "type": "string",
      "description": "Cryptocurrency symbol for focused analysis",
      "required": false
    }
  }
}
```

---

## 🚀 **Quick Setup Instructions:**

1. **Go to your ElevenLabs agent**: `agent_0601k5cct1eyffqt3ns9c2yn6d7r`
2. **Click "Add Custom Tool"** for each tool above
3. **Fill in the form** using the values provided
4. **Copy the JSON** if there's an "Edit as JSON" option
5. **Test** with voice commands

## 🎯 **Test Commands:**
- "What's Bitcoin at?" → `get_market_data`
- "Check my credits" → `check_credits`
- "Analyze Ethereum" → `technical_analysis`
- "Set alert for Solana at $200" → `set_price_alert`
- "Get consensus on Bitcoin" → `multi_agent_consensus`

Your webhook endpoint is ready at: `https://06f2c0ec2996.ngrok-free.app/api/elevenlabs/webhook`