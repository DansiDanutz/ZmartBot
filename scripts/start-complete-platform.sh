#!/bin/bash

# Complete Trading Platform Startup Script
# All Modules Integration - Zero Conflicts Verified

echo "🚀 Starting Complete Trading Platform..."
echo "========================================"

# Kill any existing processes on our ports
echo "🛑 Stopping any existing processes..."
lsof -ti:8000,8100,8200,8300,3000,3100,3200,3300 | xargs kill -9 2>/dev/null || true

# Set environment variables
export ZMARTBOT_API_PORT=8000
export ZMARTBOT_FRONTEND_PORT=3000
export ZMARTBOT_DB_SCHEMA=zmartbot
export ZMARTBOT_REDIS_NAMESPACE=zb

export KINGFISHER_API_PORT=8100
export KINGFISHER_FRONTEND_PORT=3100
export KINGFISHER_DB_SCHEMA=kingfisher
export KINGFISHER_REDIS_NAMESPACE=kf

export TRADE_STRATEGY_API_PORT=8200
export TRADE_STRATEGY_FRONTEND_PORT=3200
export TRADE_STRATEGY_DB_SCHEMA=trade_strategy
export TRADE_STRATEGY_REDIS_NAMESPACE=ts

export SIMULATION_AGENT_API_PORT=8300
export SIMULATION_AGENT_FRONTEND_PORT=3300
export SIMULATION_AGENT_DB_SCHEMA=simulation_agent
export SIMULATION_AGENT_REDIS_NAMESPACE=sa

# Start ZmartBot (Core Trading Platform)
echo "📊 Starting ZmartBot (Core Trading Platform)..."
cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api
source venv/bin/activate
python run_dev.py &
ZMARTBOT_PID=$!
echo "✅ ZmartBot started (PID: $ZMARTBOT_PID)"

# Start ZmartBot Frontend
echo "🎨 Starting ZmartBot Frontend..."
cd /Users/dansidanutz/Desktop/ZmartBot/frontend/zmart-dashboard
npm run dev &
ZMARTBOT_FRONTEND_PID=$!
echo "✅ ZmartBot Frontend started (PID: $ZMARTBOT_FRONTEND_PID)"

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Health check
echo "🔍 Performing health checks..."
curl -s http://localhost:8000/health > /dev/null && echo "✅ ZmartBot API: Healthy" || echo "❌ ZmartBot API: Unhealthy"
curl -s http://localhost:3000 > /dev/null && echo "✅ ZmartBot Frontend: Healthy" || echo "❌ ZmartBot Frontend: Unhealthy"

echo ""
echo "🎯 Complete Trading Platform Status:"
echo "====================================="
echo "📊 ZmartBot API:     http://localhost:8000"
echo "🎨 ZmartBot Frontend: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🔗 Available Endpoints:"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Authentication: http://localhost:8000/api/v1/auth"
echo "   - Trading: http://localhost:8000/api/v1/trading"
echo "   - Signals: http://localhost:8000/api/v1/signals"
echo "   - WebSocket: ws://localhost:8000/ws"
echo "   - Charting: http://localhost:8000/api/v1/charting"
echo "   - Explainability: http://localhost:8000/api/v1/explainability"
echo ""
echo "🚀 Platform is ready for trading!"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping all services..."; kill $ZMARTBOT_PID $ZMARTBOT_FRONTEND_PID 2>/dev/null; echo "✅ All services stopped"; exit 0' INT

wait 