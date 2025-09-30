#!/bin/bash

# ZmartBot Backend Server Startup Script
# This script sets the correct environment and starts the FastAPI server

echo "🚀 Starting ZmartBot Backend Server..."

# Set the project root directory
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set Python path to include the project root
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

echo "📁 Project Root: ${PROJECT_ROOT}"
echo "🐍 Python Path: ${PYTHONPATH}"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if all dependencies are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, pydantic, sqlalchemy, redis, influxdb_client, prometheus_client; print('✅ All dependencies available')" 2>/dev/null || {
    echo "❌ Missing dependencies detected. Installing..."
    python -m pip install -r requirements.txt
}

# Start the server
echo "🌐 Starting FastAPI server on http://0.0.0.0:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 