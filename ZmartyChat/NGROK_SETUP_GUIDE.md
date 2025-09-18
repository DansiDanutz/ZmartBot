# 🌐 Ngrok Setup Guide for ElevenLabs Integration

## ⚠️ Current Issue
Your ngrok authtoken appears to be invalid or expired. ElevenLabs requires a public URL for webhooks, so we need to resolve this.

## 🔑 Get a Valid Ngrok Token

### Option 1: Get a New Free Token
1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Sign in or create a free account
3. Copy your authtoken
4. Run: `ngrok config add-authtoken YOUR_NEW_TOKEN`

### Option 2: Use Your Current Account
1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Check if your token `32mc84eco2eEbcj3V5Xi2ramGoD_5szPxWjvWFMiZE3UgozCu` is valid
3. If not, generate a new one

## 🚀 Once You Have a Valid Token

```bash
# Add your valid token
ngrok config add-authtoken YOUR_VALID_TOKEN

# Start the tunnel
ngrok http 3001

# This will give you a URL like: https://abc123.ngrok.io
```

## 🔄 Update ElevenLabs Configuration

Once you get the ngrok URL (e.g., `https://abc123.ngrok.io`), update your ElevenLabs tools:

**Replace all instances of:**
```
http://localhost:3001/api/elevenlabs/webhook
```

**With your ngrok URL:**
```
https://YOUR_NGROK_URL.ngrok.io/api/elevenlabs/webhook
```

## 📋 Current ElevenLabs Setup Status

✅ **ZmartyChat Server**: Running on http://localhost:3001
✅ **Webhook Endpoint**: `/api/elevenlabs/webhook` ready
✅ **Database**: Connected
✅ **Credit System**: Active
⚠️ **Public URL**: Pending ngrok setup

## 🎯 What to Do Next

1. Get a valid ngrok token from dashboard
2. Start ngrok tunnel: `ngrok http 3001`
3. Update the webhook URL in ElevenLabs tools
4. Test your voice agent!

Your Zmarty agent `agent_0601k5cct1eyffqt3ns9c2yn6d7r` is ready once the public URL is configured.