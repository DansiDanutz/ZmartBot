#!/bin/bash

# ZmartyChat Permanent Startup Script
echo "🚀 Starting ZmartyChat with Permanent URL..."

# Kill any existing processes
echo "🛑 Stopping existing processes..."
pkill -f "simple-server.js" 2>/dev/null
pkill -f "ngrok" 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Start ZmartyChat server in background
echo "📡 Starting ZmartyChat server..."
node src/simple-server.js &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Start ngrok with permanent configuration
echo "🌐 Starting permanent ngrok tunnel..."
ngrok start --config=ngrok-config.yml zmarty-webhook &
NGROK_PID=$!

# Wait for ngrok to establish tunnel
sleep 5

# Get the public URL
echo "🔍 Getting public URL..."
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else 'No tunnels found')")

echo ""
echo "✅ ZmartyChat System Running!"
echo "================================"
echo "🖥️  Local Server: http://localhost:3001"
echo "🌐 Public URL: $PUBLIC_URL"
echo "📞 ElevenLabs Agent: agent_0601k5cct1eyffqt3ns9c2yn6d7r"
echo "🔗 Webhook: $PUBLIC_URL/api/elevenlabs/webhook"
echo ""
echo "📋 PIDs:"
echo "   Server PID: $SERVER_PID"
echo "   Ngrok PID: $NGROK_PID"
echo ""
echo "🛑 To stop: kill $SERVER_PID $NGROK_PID"

# Keep script running
wait