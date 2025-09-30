#!/bin/bash

# ZmartBot Production Startup Script
# Complete production deployment with all integrated systems

echo "🚀 Starting ZmartBot Production Deployment"
echo "=========================================="

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export OPENAI_API_KEY="${OPENAI_API_KEY:-your_openai_key_here}"

# Check if we're in the correct directory
if [ ! -f "production_server.py" ]; then
    echo "❌ Error: production_server.py not found. Please run from backend/zmart-api directory."
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "📋 System Information:"
echo "   Working Directory: $(pwd)"
echo "   Python Version: $(python3 --version)"
echo "   Date: $(date)"
echo ""

echo "🔧 Installing/Checking Dependencies..."
# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "   Installing uvicorn..."
    pip3 install uvicorn fastapi
fi

echo "   ✅ Dependencies checked"
echo ""

echo "🌟 Starting ZmartBot Production Server..."
echo "   API Server: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo "   System Status: http://localhost:8000/status"
echo ""

echo "🎯 Integrated Systems:"
echo "   ✅ Benjamin Cowen RiskMetric (20% weight)"
echo "   ✅ Cryptometer Analysis (50% weight)"
echo "   ✅ KingFisher Liquidation Analysis (30% weight)"
echo "   ✅ Real-time Trading Signals"
echo "   ✅ Market Intelligence & Risk Assessment"
echo "   ✅ Enhanced Rate Limiting"
echo "   ✅ Multi-Exchange Data Integration"
echo ""

echo "📊 Supported Symbols (17):"
echo "   Tier 1: BTC, ETH, BNB, LINK, SOL"
echo "   Tier 2: ADA, DOT, AVAX, TON, POL"
echo "   Tier 3: DOGE, TRX, SHIB, VET, ALGO"
echo "   Tier 4: LTC, XRP"
echo ""

echo "🛡️  Production Features:"
echo "   ✅ Enhanced rate limiting with exponential backoff"
echo "   ✅ 429 response handling for all APIs"
echo "   ✅ Comprehensive health monitoring"
echo "   ✅ Real-time system status reporting"
echo "   ✅ Graceful shutdown handling"
echo ""

# Start the production server
echo "🚀 Launching Production Server..."
echo "   Press Ctrl+C to stop the server"
echo "=========================================="

# Run the production server with proper logging
python3 production_server.py 2>&1 | tee logs/production_$(date +%Y%m%d_%H%M%S).log