# ZmartyChat MCP (Model Context Protocol) Setup

## Overview
ZmartyChat uses Anthropic's Model Context Protocol (MCP) to enable Claude to interact with the trading system through defined tools and resources.

## Setup Instructions

### 1. Install Claude Desktop App
Download and install the Claude desktop app from: https://claude.ai/download

### 2. Configure Claude Desktop
Copy the MCP configuration to Claude's config directory:

**On macOS:**
```bash
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**On Windows:**
```bash
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

### 3. Install Dependencies
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/ZmartyChat
npm install
```

### 4. Start the MCP Server
```bash
npm run mcp
```

### 5. Restart Claude Desktop
Quit and restart the Claude desktop app to load the new MCP configuration.

## Available MCP Tools

Once configured, Claude will have access to these trading tools:

### 📊 Market Data
- `get_market_data` - Get real-time cryptocurrency prices
- Parameters: symbol (BTC, ETH, SOL, etc.)

### 📈 Trading Analysis
- `analyze_trading_signal` - Get AI-powered trading signals
- Parameters: symbol, timeframe (1h, 4h, 1d)

### 💼 Portfolio Management
- `get_portfolio_status` - View current portfolio and positions
- No parameters required

### 💰 Trade Execution
- `execute_trade` - Execute buy/sell orders
- Parameters: symbol, side (buy/sell), amount, type (market/limit), price (optional)

### ⚠️ Risk Management
- `get_risk_analysis` - Analyze portfolio risk metrics
- No parameters required

## Using MCP in Claude Desktop

1. Open Claude Desktop
2. You'll see "zmartychat" in the available MCP servers
3. Start a conversation and Claude will automatically use the tools when relevant
4. Example prompts:
   - "What's the current price of Bitcoin?"
   - "Analyze ETH trading signals on the 4h timeframe"
   - "Show me my portfolio status"
   - "What's my current risk exposure?"

## Testing the Integration

1. In Claude Desktop, type: "Show me the current market data for BTC"
2. Claude should use the `get_market_data` tool
3. You'll see the tool usage and response in the conversation

## Troubleshooting

### MCP Server Not Showing in Claude
- Ensure the config file is in the correct location
- Restart Claude Desktop completely
- Check the server is running: `npm run mcp`

### Connection Issues
- Verify Node.js version: `node --version` (should be 18+)
- Check logs: `tail -f ~/.claude/logs/mcp.log`
- Ensure port 3000 is available

### Tool Errors
- Check the MCP server console for error messages
- Verify all dependencies are installed
- Ensure trading APIs are configured

## Advanced Configuration

### Adding Custom Tools
Edit `mcp-server.js` and add new tools to the `setupHandlers()` method:

```javascript
{
  name: 'your_tool_name',
  description: 'Tool description',
  inputSchema: {
    type: 'object',
    properties: {
      // Define parameters
    }
  }
}
```

### Connecting Real APIs
Replace mock data in `mcp-server.js` with actual API calls:

```javascript
async getMarketData(args) {
  // Replace with real API call
  const response = await fetch(`https://api.exchange.com/ticker/${args.symbol}`);
  const data = await response.json();
  // Process and return data
}
```

## Security Notes

⚠️ **Important Security Considerations:**
- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement rate limiting for API calls
- Add authentication for production use
- Validate all user inputs
- Use secure WebSocket connections (wss://)

## Support

For issues or questions:
- Check the MCP documentation: https://modelcontextprotocol.io
- Review Claude Desktop docs: https://claude.ai/docs/desktop
- ZmartBot support: support@zmartbot.com