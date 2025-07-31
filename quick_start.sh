#!/bin/bash

echo "🚀 Quick Start - ZmartBot Backend"
echo "=================================="

# Navigate to the correct directory
cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api

# Check if we're in the right place
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this from: /Users/dansidanutz/Desktop/ZmartBot/"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Start server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API docs will be at: http://localhost:8000/docs"
echo ""
echo "Note: Some warnings about databases are normal in development mode."
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload