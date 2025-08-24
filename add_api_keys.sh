#!/bin/bash

# Secure API Key Configuration Script for ZmartBot
# This script helps you safely add your API keys

echo "🔐 ZmartBot Secure API Key Configuration"
echo "========================================"
echo ""
echo "This script will help you securely add your API keys."
echo "Your keys will be added directly to .env.production"
echo ""

# Function to update or add a key in .env.production
update_env_key() {
    local key=$1
    local value=$2
    local file=".env.production"
    
    if grep -q "^${key}=" "$file"; then
        # Key exists, update it
        sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
        echo "✅ Updated: ${key}"
    else
        # Key doesn't exist, add it
        echo "${key}=${value}" >> "$file"
        echo "✅ Added: ${key}"
    fi
}

# Cryptometer API Key
echo "1. Cryptometer API Configuration"
echo "   Get your key from: https://cryptometer.io/api"
read -p "   Enter your Cryptometer API Key: " CRYPTO_KEY
if [ ! -z "$CRYPTO_KEY" ]; then
    update_env_key "CRYPTOMETER_API_KEY" "$CRYPTO_KEY"
fi

echo ""
echo "2. KuCoin API Configuration"
echo "   Get your keys from: https://www.kucoin.com/account/api"
echo "   ⚠️  Make sure to enable FUTURES trading permissions!"
read -p "   Enter your KuCoin API Key: " KUCOIN_KEY
if [ ! -z "$KUCOIN_KEY" ]; then
    update_env_key "KUCOIN_API_KEY" "$KUCOIN_KEY"
fi

read -s -p "   Enter your KuCoin Secret (hidden): " KUCOIN_SEC
echo ""
if [ ! -z "$KUCOIN_SEC" ]; then
    update_env_key "KUCOIN_SECRET" "$KUCOIN_SEC"
fi

read -s -p "   Enter your KuCoin Passphrase (hidden): " KUCOIN_PASS
echo ""
if [ ! -z "$KUCOIN_PASS" ]; then
    update_env_key "KUCOIN_PASSPHRASE" "$KUCOIN_PASS"
fi

echo ""
echo "3. OpenAI API Configuration"
echo "   Get your key from: https://platform.openai.com/api-keys"
read -p "   Enter your OpenAI API Key: " OPENAI_KEY
if [ ! -z "$OPENAI_KEY" ]; then
    update_env_key "OPENAI_API_KEY" "$OPENAI_KEY"
fi

echo ""
echo "========================================"
echo "✅ API Keys configured successfully!"
echo ""
echo "🚀 Now restart the server to use your keys:"
echo ""
echo "   cd backend/zmart-api"
echo "   pkill -f uvicorn"
echo "   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📊 Then test your configuration:"
echo "   curl http://localhost:8000/api/real-time/price/BTC"
echo ""
echo "🔒 Your keys are stored in: .env.production"
echo "   Keep this file secure and never commit it to git!"
echo ""