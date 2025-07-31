#!/bin/bash

# ZmartBot Backend Startup Script (Fixed Version)
set -e

# Set project root
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

echo "🚀 Starting ZmartBot Backend Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, pydantic, sqlalchemy, redis, influxdb_client, prometheus_client" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

# Check if server can import
echo "🔍 Testing server imports..."
python -c "from src.main import app; print('✅ Server imports successfully')" || {
    echo "❌ Server import failed. Check configuration."
    exit 1
}

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "Note: Some monitoring warnings are expected during development."
echo "The server will work normally despite these warnings."
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload