#!/bin/bash

# KingFisher Real Telegram Bot Startup Script
# This script starts the real Telegram bot that monitors the KingFisher channel

echo "🚀 Starting KingFisher Real Telegram Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if KingFisher API is running
echo "🔍 Checking KingFisher API status..."
if curl -s http://localhost:8100/health > /dev/null; then
    echo "✅ KingFisher API is running"
else
    echo "❌ KingFisher API is not running. Please start it first."
    echo "Run: python run_dev.py"
    exit 1
fi

# Check Telegram bot token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    export TELEGRAM_BOT_TOKEN="7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"
    echo "📱 Using default Telegram bot token"
else
    echo "📱 Using custom Telegram bot token"
fi

# Check Telegram chat ID
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    export TELEGRAM_CHAT_ID="-1002891569616"
    echo "💬 Using default Telegram chat ID"
else
    echo "💬 Using custom Telegram chat ID"
fi

# Check KingFisher channel
if [ -z "$KINGFISHER_CHANNEL" ]; then
    export KINGFISHER_CHANNEL="@KingFisherAutomation"
    echo "📢 Using default KingFisher channel"
else
    echo "📢 Using custom KingFisher channel"
fi

echo ""
echo "🐟 KingFisher Real Telegram Bot Configuration:"
echo "   Bot Token: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "   Chat ID: $TELEGRAM_CHAT_ID"
echo "   Channel: $KINGFISHER_CHANNEL"
echo "   API URL: http://localhost:8100"
echo ""

# Start the bot
echo "🚀 Starting bot..."
python real_telegram_bot.py 