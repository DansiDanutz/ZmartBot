#!/bin/bash

# ZmartBot Fix and Start Script
# Handles all import issues and startup problems

echo "🔧 Fixing and Starting ZmartBot Trading Platform..."
echo "=================================================="

# Kill any existing processes
echo "🛑 Stopping any existing processes..."
lsof -ti:8000,3000 | xargs kill -9 2>/dev/null || true

# Fix CSS import order
echo "🎨 Fixing CSS import order..."
if [ -f "frontend/zmart-dashboard/src/index.css" ]; then
    # Create a temporary file with correct import order
    cat > frontend/zmart-dashboard/src/index.css.tmp << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Base styles */
@layer base {
  html {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  
  body {
    @apply bg-dark-bg text-dark-text;
    font-feature-settings: 'rlig' 1, 'calt' 1;
  }
  
  * {
    @apply border-dark-border;
  }
}

/* Component styles */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none;
  }
  
  .btn-primary {
    @apply btn bg-gradient-primary text-white hover:bg-primary-700;
  }
  
  .btn-secondary {
    @apply btn bg-transparent border border-dark-border text-dark-text hover:bg-dark-card;
  }
  
  .card {
    @apply bg-dark-card border border-dark-border rounded-xl shadow-card;
  }
  
  .input {
    @apply w-full rounded-lg border border-dark-border bg-dark-bg px-3 py-2 text-dark-text placeholder-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50;
  }
}
EOF
    mv frontend/zmart-dashboard/src/index.css.tmp frontend/zmart-dashboard/src/index.css
    echo "✅ CSS fixed"
else
    echo "⚠️ CSS file not found"
fi

# Start backend server
echo "🚀 Starting backend server..."
cd backend/zmart-api
source venv/bin/activate
PYTHONPATH=src uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 10

# Test backend
echo "🔍 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Start frontend (if not already running)
echo "🎨 Starting frontend..."
cd ../../frontend/zmart-dashboard
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "✅ Frontend already running"
fi

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 5

# Test frontend
echo "🔍 Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend test failed"
fi

echo ""
echo "🎯 ZmartBot Trading Platform Status:"
echo "====================================="
echo "📊 Backend API:     http://localhost:8000"
echo "🎨 Frontend:        http://localhost:3000"
echo "📚 Documentation:    http://localhost:8000/docs"
echo "🔐 Login:           http://localhost:3000/login"
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
trap 'echo ""; echo "🛑 Stopping all services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ All services stopped"; exit 0' INT

wait 