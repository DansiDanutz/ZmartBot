#!/bin/bash

echo "🚀 Starting ZmartBot Trading Platform..."

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
sleep 2

# Start Backend
echo "🔧 Starting Backend API..."
cd backend/zmart-api
source venv/bin/activate
PYTHONPATH=src uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
echo "🧪 Testing backend..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend is running on http://127.0.0.1:8000"
else
    echo "⚠️  Backend may not be fully started yet"
fi

# Start Frontend
echo "🎨 Starting Frontend..."
cd frontend/zmart-dashboard
npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Test frontend
echo "🧪 Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "⚠️  Frontend may not be fully started yet"
fi

echo ""
echo "🎉 ZmartBot Platform Startup Complete!"
echo ""
echo "📍 Services:"
echo "   • Backend API: http://127.0.0.1:8000"
echo "   • API Docs: http://127.0.0.1:8000/docs"
echo "   • Frontend: http://localhost:3000"
echo ""
echo "🔧 To stop the platform:"
echo "   pkill -f uvicorn && pkill -f 'npm run dev'"
echo ""
echo "📊 Health Check:"
echo "   curl http://127.0.0.1:8000/health"
echo ""

# Keep script running
wait 