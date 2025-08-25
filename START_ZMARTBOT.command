#!/bin/bash

# ZmartBot Quick Start (Double-click to run)
cd "$(dirname "$0")"

echo "🚀 ZmartBot Quick Start"
echo "======================="
echo ""

# Function to check if port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Kill existing processes
echo "Cleaning up existing processes..."
pkill -f "python -m src.main" 2>/dev/null
pkill -f "professional_dashboard_server.py" 2>/dev/null
sleep 2

# Start Backend
echo ""
echo "Starting Backend API (Port 8000)..."
cd backend/zmart-api
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
python -m src.main &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
echo "Waiting for backend to initialize..."
for i in {1..10}; do
    if check_port 8000; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
done

# Start Dashboard
echo ""
echo "Starting Dashboard (Port 3400)..."
python professional_dashboard_server.py &
DASHBOARD_PID=$!
echo "✅ Dashboard started (PID: $DASHBOARD_PID)"

# Wait for dashboard
echo "Waiting for dashboard to initialize..."
for i in {1..10}; do
    if check_port 3400; then
        echo "✅ Dashboard is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "======================================"
echo "✅ ZmartBot is running!"
echo ""
echo "🌐 Dashboard: http://localhost:3400"
echo "🔌 API: http://localhost:8000/docs"
echo ""
echo "Professional Alerts available in My Symbols section"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Keep script running
trap "echo 'Stopping services...'; kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null; exit" INT
wait