# 🎨 Figma MCP Server Setup

## Status
❌ **Not Yet Configured** - Figma MCP server has been added to configuration but needs API key

## Package Information
- **Package**: `figma-developer-mcp`
- **Version**: 0.6.0 (latest)
- **Status**: Available and working

## Configuration Added to `.cursor/mcp.json`
```json
"figma": {
  "command": "npx",
  "args": [
    "-y",
    "figma-developer-mcp",
    "--figma-api-key=YOUR-FIGMA-API-KEY",
    "--stdio"
  ]
}
```

## To Complete Setup

### Step 1: Get Your Figma API Key
1. Go to https://www.figma.com/settings
2. Navigate to the "Personal Access Tokens" section
3. Click "Create new token"
4. Give it a name (e.g., "MCP Server")
5. Copy the generated token

### Step 2: Add API Key to Configuration
Replace `YOUR-FIGMA-API-KEY` in `.cursor/mcp.json` with your actual token:
```json
"--figma-api-key=figd_xxxxxxxxxxxxxxxxxxxxx"
```

### Step 3: Restart Claude/Cursor
After adding the API key, restart your IDE to activate the Figma MCP server.

## Features
Once configured, the Figma MCP server provides:
- Access to Figma designs directly in your AI coding workflow
- Translation of Figma API responses to relevant layout/styling info
- Simplified design-to-code workflow
- Support for Dev Mode features

## Alternative: Figma Desktop App MCP Server
If you have a Professional, Organization, or Enterprise Figma plan:
1. Open Figma desktop app
2. Go to Menu > Preferences
3. Enable "Enable local MCP Server"
4. Server runs at: http://127.0.0.1:3845/mcp

## Testing
After setup, test with:
```bash
npx figma-developer-mcp --figma-api-key=YOUR-KEY --version
```

## Documentation
- NPM Package: https://www.npmjs.com/package/figma-developer-mcp
- Official Guide: https://help.figma.com/hc/en-us/articles/32132100833559