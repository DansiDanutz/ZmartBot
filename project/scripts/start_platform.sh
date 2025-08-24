#!/bin/bash

# 🚀 ZmartBot Professional Platform Startup
# Professional orchestration script for new project structure

set -e

echo "🚀 ZMARTBOT PROFESSIONAL PLATFORM STARTUP"
echo "========================================="

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend/api"
ORIGINAL_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)"

echo "📁 Project Root: $PROJECT_ROOT"
echo "🏗️ Backend Dir: $BACKEND_DIR"

# Step 1: Navigate to original backend for virtual environment
echo -e "\n🐍 STEP 1: Setting up Python environment"
cd "$ORIGINAL_ROOT/backend/zmart-api"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found at $ORIGINAL_ROOT/backend/zmart-api/venv"
    echo "Please run setup from the original location first"
    exit 1
fi

echo "✅ Virtual environment found"

# Step 2: Clean up existing processes
echo -e "\n🛑 STEP 2: Cleanup existing processes"
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3400 | xargs kill -9 2>/dev/null || true
echo "✅ Cleanup completed"

# Step 3: Start Backend API Server using original location
echo -e "\n🚀 STEP 3: Start Backend API Server"
source venv/bin/activate
nohup python run_dev.py > "$PROJECT_ROOT/logs/api_server.log" 2>&1 &
API_PID=$!
echo "✅ Backend API Server started (PID: $API_PID)"

# Wait for backend to start
echo "⏳ Waiting for Backend API Server to start on port 8000..."
sleep 5
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend API Server is running on port 8000"
        break
    fi
    sleep 1
    echo -n "."
done

# Step 4: Start Dashboard Server using original location  
echo -e "\n🎛️ STEP 4: Start Dashboard Server"
nohup python professional_dashboard_server.py > "$PROJECT_ROOT/logs/dashboard_server.log" 2>&1 &
DASHBOARD_PID=$!
echo "✅ Dashboard Server started (PID: $DASHBOARD_PID)"

# Wait for dashboard to start
echo "⏳ Waiting for Dashboard Server to start on port 3400..."
sleep 3
for i in {1..10}; do
    if curl -s http://localhost:3400/health > /dev/null; then
        echo "✅ Dashboard Server is running on port 3400"
        break
    fi
    sleep 1
    echo -n "."
done

# Step 5: Save PIDs to project structure
mkdir -p "$PROJECT_ROOT/runtime"
echo $API_PID > "$PROJECT_ROOT/runtime/api_server.pid"
echo $DASHBOARD_PID > "$PROJECT_ROOT/runtime/dashboard_server.pid"

echo -e "\n✅ ZMARTBOT PROFESSIONAL PLATFORM STARTED"
echo "========================================="
echo "🎛️ Dashboard: http://localhost:3400"
echo "🔌 API: http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo "📊 Logs: $PROJECT_ROOT/logs/"
echo "🔢 PIDs: $PROJECT_ROOT/runtime/"