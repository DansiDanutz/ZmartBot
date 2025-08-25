# 🤖 Telegram Alert Setup Guide

## Quick Setup for ZmartBot Telegram Alerts

### Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Send message**: `/newbot`
3. **Choose a name** for your bot (e.g., "ZmartBot Alerts")
4. **Choose a username** (e.g., "zmartbot_alerts_bot")
5. **Save the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. **Start a chat** with your bot
2. **Send any message** to the bot
3. **Visit this URL** (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat_id** in the response (looks like: `123456789`)

### Step 3: Configure ZmartBot

**Option A: Using curl command**
```bash
curl -X POST http://localhost:3400/api/v1/alerts/config/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE",
    "enabled": true
  }'
```

**Option B: Using the dashboard**
- Go to the Alerts section in your dashboard
- Look for "Notification Settings" or "Configure Telegram"
- Enter your bot token and chat ID

### Step 4: Test the Configuration

```bash
# Check configuration status
curl http://localhost:3400/api/v1/alerts/config/status

# Create a test alert
curl -X POST http://localhost:3400/api/v1/alerts/create \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "alert_type": "PRICE",
    "conditions": {
      "threshold": 45000,
      "operator": "above",
      "timeframe": "1m"
    },
    "notification_channels": ["telegram"]
  }'
```

## Example Alert Messages

### Price Alert
```
🚨 BTCUSDT Alert

Type: PRICE
Price: $45,123.45
Priority: MEDIUM
Time: 21:15:30 UTC

Conditions Met:
{
  "current_price": 45123.45,
  "threshold": 45000,
  "operator": "above"
}
```

### Technical Alert
```
🚨 ETHUSDT Alert

Type: TECHNICAL
Price: $2,850.67
Priority: HIGH
Time: 21:15:30 UTC

Conditions Met:
{
  "current_price": 2850.67,
  "technical_conditions": {
    "rsi": 75.5,
    "threshold": 70
  }
}
```

## Advanced Configuration

### Multiple Chat IDs
You can send alerts to multiple Telegram chats by configuring multiple bot instances or using a Telegram channel.

### Custom Message Templates
The system supports Markdown formatting:
- **Bold text**: `**text**`
- *Italic text*: `*text*`
- `Code`: `` `code` ``
- [Links](url): `[text](url)`

### Priority Levels
- 🟢 **LOW**: General market updates
- 🟡 **MEDIUM**: Standard alerts
- 🟠 **HIGH**: Important signals
- 🔴 **CRITICAL**: Urgent alerts

## Troubleshooting

### Bot Not Responding
1. Check if bot token is correct
2. Ensure bot is started (`/start` command)
3. Verify chat ID is correct

### No Messages Received
1. Check alert engine status: `curl http://localhost:3400/api/v1/alerts/status`
2. Verify alert is active: `curl http://localhost:3400/api/v1/alerts/list`
3. Check server logs for errors

### Configuration Issues
1. Test bot token: `https://api.telegram.org/botYOUR_TOKEN/getMe`
2. Test chat access: `https://api.telegram.org/botYOUR_TOKEN/getChat?chat_id=YOUR_CHAT_ID`

## Security Notes

- Keep your bot token secure
- Don't share bot tokens in public repositories
- Use environment variables for production
- Regularly rotate bot tokens

## Production Setup

For production environments, consider:
- Using environment variables for credentials
- Setting up webhook endpoints for faster delivery
- Implementing rate limiting
- Adding authentication for configuration endpoints