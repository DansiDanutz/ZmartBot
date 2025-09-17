#!/bin/bash

# ZmartBot Mobile Service Startup Script
# Port: 7777 (RESERVED - NO EXCEPTIONS)

echo "🚀 Starting ZmartBot Mobile Service on port 7777..."
echo "📱 This service is RESERVED for mobile app integration ONLY"
echo "🔗 Port 7777 = Mobile App Service (NEVER assign to other services)"

# Check if port 7777 is already in use
if lsof -Pi :7777 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ ERROR: Port 7777 is already in use!"
    echo "🚨 This port is RESERVED for mobile app service only"
    echo "🔍 Checking what's using port 7777:"
    lsof -i :7777
    exit 1
fi

# Check if Python dependencies are installed
if ! python3 -c "import fastapi, uvicorn, requests, pydantic" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start the mobile service
echo "🚀 Launching mobile service on port 7777..."
python3 zmartbot_mobile_service.py

echo "✅ Mobile service started successfully on port 7777"
echo "📱 Service available at: http://localhost:7777"
echo "🔗 Health check: http://localhost:7777/health"
echo "📊 API docs: http://localhost:7777/docs"
