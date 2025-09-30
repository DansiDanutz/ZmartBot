#!/bin/bash

echo "🚀 ZmartBot Backend - Complete Startup"
echo "======================================"

# Set project root
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Update dependencies to fix SSL warnings
echo "🔧 Updating dependencies..."
pip install urllib3==1.26.18 --quiet

# Setup database if needed
echo "🗄️  Checking database setup..."
if ! psql -h localhost -U zmart_user -d zmart_platform -c "SELECT 1;" >/dev/null 2>&1; then
    echo "⚠️  Database not properly configured. Running setup..."
    if [ -f "setup_database.sh" ]; then
        ./setup_database.sh || {
            echo "❌ Database setup failed. Please run setup_database.sh manually."
            exit 1
        }
    else
        echo "❌ Database setup script not found. Please run database setup manually."
        exit 1
    fi
fi

# Test server imports
echo "🔍 Testing server imports..."
python -c "from src.main import app; print('✅ Server imports successfully')" || {
    echo "❌ Server import failed. Check configuration."
    exit 1
}

# Start the server
echo ""
echo "🌐 Starting FastAPI server..."
echo "📍 Server URL: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📝 Expected startup messages:"
echo "   ✅ PostgreSQL connection pool initialized"
echo "   ✅ Redis connection initialized"
echo "   ✅ InfluxDB connection initialized"
echo "   ✅ Starting system monitor"
echo ""
echo "⚠️  Note: Some debug messages about metrics are normal in development."
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload