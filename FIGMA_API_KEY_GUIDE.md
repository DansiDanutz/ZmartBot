# 🔑 How to Get Your Figma API Key - Step by Step

## Step 1: Open Figma in Your Browser

Go to: https://www.figma.com

## Step 2: Sign In
- Click "Log in" in the top right corner
- Enter your email and password
- Complete any 2FA if enabled

## Step 3: Access Your Account Settings

Once logged in, click on your **profile picture** in the top-right corner of the page

From the dropdown menu, click on **"Settings"**

OR directly go to: https://www.figma.com/settings

## Step 4: Navigate to Personal Access Tokens

In the Settings page, look at the left sidebar menu

Find and click on **"Personal access tokens"**

The direct URL is: https://www.figma.com/settings/account#personal-access-tokens

## Step 5: Generate a New Token

1. Click the **"Generate new token"** button (usually blue)

2. A dialog will appear asking for:
   - **Token name**: Enter something descriptive like "MCP Server" or "Claude Code"
   - **Expiration**: Choose how long the token should be valid
     - No expiration (recommended for development)
     - 30 days
     - 60 days
     - 90 days
   - **Scopes**: For MCP server, you need at least:
     - ✅ File content (read-only)
     - ✅ Read-only access

3. Click **"Generate token"**

## Step 6: Copy Your Token

⚠️ **IMPORTANT**: The token will only be shown ONCE!

1. A new screen will show your token (starts with `figd_`)
2. Click the **"Copy"** button or manually select and copy the entire token
3. It will look like: `figd_xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx`

## Step 7: Save Your Token Securely
- Store it in a password manager
- Or save it in a secure note
- **Never commit it to Git repositories**

## Step 8: Add to MCP Configuration

1. Open `.cursor/mcp.json`
2. Find the Figma section
3. Replace `YOUR-FIGMA-API-KEY` with your actual token:

```json
"figma": {
  "command": "npx",
  "args": [
    "-y",
    "figma-developer-mcp",
    "--figma-api-key=figd_xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx",
    "--stdio"
  ]
}
```

## Step 9: Test Your Token

Run this command to verify it works:

```bash
npx figma-developer-mcp --figma-api-key=YOUR_TOKEN_HERE --version
```

## Troubleshooting

### Can't find Personal Access Tokens?
- Make sure you're logged into your Figma account
- Try this direct link: https://www.figma.com/settings/account#personal-access-tokens
- It might be under "Account" → "Personal access tokens"

### Token not working?
- Check there are no extra spaces before/after the token
- Make sure it starts with `figd_`
- Verify the token hasn't expired
- Ensure you copied the entire token

### Need to regenerate?

1. Go back to Personal Access Tokens
2. Find your token in the list
3. Click "Revoke" to delete it
4. Generate a new one following steps above

## Security Notes
- Tokens are like passwords - keep them secret
- Don't share tokens in screenshots or support tickets
- Revoke tokens you're no longer using
- Use different tokens for different applications

## What Can You Do With the Token?

Once configured in MCP:

- Access Figma designs directly in Claude/Cursor
- Extract design specifications
- Get layout information
- Access component properties
- Read text content from designs
- Get color and styling information

---

**Ready to proceed?** Once you have your token, add it to `.cursor/mcp.json` and restart your IDE!
