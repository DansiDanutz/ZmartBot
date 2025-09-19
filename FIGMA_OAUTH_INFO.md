# 🔐 Figma OAuth Credentials Info

## Your Figma OAuth App Details
- **Client ID**: `EErdFWTGxnA2ba1262cWUt`
- **Client Secret**: Stored securely in `.env.figma`

## Important Notes

### These are OAuth App Credentials
The Client ID and Client Secret you provided are for OAuth authentication, which is used when:
- Building a Figma app/plugin
- Creating an OAuth flow for users to authorize your app
- Building a service that needs user authorization

### For MCP Server, You Need Different Credentials
The Figma MCP server uses a **Personal Access Token**, not OAuth credentials.

## Next Steps

### Option 1: Get Personal Access Token (Recommended for MCP)
1. Go to https://www.figma.com/settings/account#personal-access-tokens
2. Click "Generate new token"
3. Name it "MCP Server"
4. Copy the token (starts with `figd_`)
5. Use that token in `.cursor/mcp.json`:
```json
"--figma-api-key=figd_YOUR_TOKEN_HERE"
```

### Option 2: Use OAuth Flow (Advanced)
If you want to build a custom OAuth integration:
1. Set up OAuth callback URL
2. Implement OAuth flow using Client ID & Secret
3. Exchange authorization code for access token
4. Use the access token for API calls

## Security Notes
- ✅ Added `.env.figma` to `.gitignore`
- ⚠️ Never commit client secret to Git
- 🔒 Credentials are stored securely in `.env.figma`

## Which One to Use?
- **For MCP Server**: Use Personal Access Token ✅
- **For custom apps**: Use OAuth credentials

The MCP server configuration expects a personal access token, not OAuth credentials.