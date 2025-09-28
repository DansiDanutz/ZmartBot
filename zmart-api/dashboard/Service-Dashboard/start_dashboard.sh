#!/bin/bash

# ZmartBot Professional Service Dashboard Startup Script

echo "🚀 Starting ZmartBot Professional Service Dashboard..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, uvicorn, httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Required packages not found. Installing..."
    pip3 install fastapi uvicorn httpx
fi

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is already in use. Stopping existing process..."
    pkill -f "api_server.py"
    sleep 2
fi

# Start the dashboard
echo "🌐 Starting dashboard on http://127.0.0.1:3000"
echo "📁 Dashboard files: $(pwd)"
echo ""

python3 api_server.py --port 3000 --host 127.0.0.1
















