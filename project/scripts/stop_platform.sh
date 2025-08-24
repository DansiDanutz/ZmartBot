#!/bin/bash

# 🛑 ZmartBot Professional Platform Shutdown
# Professional shutdown script for new project structure

echo "🛑 ZMARTBOT PROFESSIONAL PLATFORM SHUTDOWN"
echo "=========================================="

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Stop by PID files if they exist
if [ -f "$PROJECT_ROOT/runtime/api_server.pid" ]; then
    API_PID=$(cat "$PROJECT_ROOT/runtime/api_server.pid")
    echo "🛑 Stopping API Server (PID: $API_PID)"
    kill $API_PID 2>/dev/null || echo "Process already stopped"
    rm -f "$PROJECT_ROOT/runtime/api_server.pid"
fi

if [ -f "$PROJECT_ROOT/runtime/dashboard_server.pid" ]; then
    DASHBOARD_PID=$(cat "$PROJECT_ROOT/runtime/dashboard_server.pid")
    echo "🛑 Stopping Dashboard Server (PID: $DASHBOARD_PID)"
    kill $DASHBOARD_PID 2>/dev/null || echo "Process already stopped"
    rm -f "$PROJECT_ROOT/runtime/dashboard_server.pid"
fi

# Force kill by ports as backup
echo "🛑 Force stopping processes on ports 8000 and 3400"
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3400 | xargs kill -9 2>/dev/null || true

# Clean up background processes
pkill -f "python run_dev.py" 2>/dev/null || true
pkill -f "professional_dashboard_server.py" 2>/dev/null || true

echo "✅ ZMARTBOT PROFESSIONAL PLATFORM STOPPED"