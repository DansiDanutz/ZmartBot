#!/bin/bash

echo "🔥 FINAL WORKING BACKEND START"
echo "=============================="

# Kill everything
echo "🛑 Killing all existing processes..."
sudo pkill -9 -f "uvicorn" 2>/dev/null || true
sudo pkill -9 -f "python.*src.main" 2>/dev/null || true
sudo lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sudo lsof -ti:8001 | xargs kill -9 2>/dev/null || true

sleep 2

# Navigate to correct directory
cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api

# Activate environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"
export METRICS_ENABLED=false
export DEBUG=true

echo "✅ Environment ready"
echo "🚀 Starting clean backend on port 8001..."
echo "📍 Server: http://localhost:8001"
echo "📚 Docs: http://localhost:8001/docs"
echo ""

# Start server on different port to avoid conflicts
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload --log-level info