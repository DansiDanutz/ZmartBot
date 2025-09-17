#!/bin/bash

# ZmartBot Database Service Startup Script
# Comprehensive database management and monitoring system

echo "🗄️  Starting ZmartBot Database Service..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required Python packages are available
python3 -c "import fastapi, uvicorn, sqlite3, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required dependencies..."
    pip3 install fastapi uvicorn psutil
fi

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export DATABASE_SERVICE_PORT="${DATABASE_SERVICE_PORT:-8900}"
export DATABASE_SERVICE_HOST="${DATABASE_SERVICE_HOST:-127.0.0.1}"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if port is already in use
if lsof -Pi :$DATABASE_SERVICE_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $DATABASE_SERVICE_PORT is already in use"
    echo "🔄 Attempting to stop existing service..."
    pkill -f "database_service.py"
    sleep 2
fi

# Display service information
echo "📊 Database Service Configuration:"
echo "   Host: $DATABASE_SERVICE_HOST"
echo "   Port: $DATABASE_SERVICE_PORT"
echo "   Working Directory: $(pwd)"
echo "   Master Database: master_database_registry.db"
echo "=================================================="

# Start the Database Service
echo "🚀 Launching Database Service..."
python3 database_service.py --host $DATABASE_SERVICE_HOST --port $DATABASE_SERVICE_PORT &

# Get the process ID
DATABASE_SERVICE_PID=$!

# Wait a moment to check if service started successfully
sleep 3

if ps -p $DATABASE_SERVICE_PID > /dev/null; then
    echo "✅ Database Service started successfully!"
    echo "   PID: $DATABASE_SERVICE_PID"
    echo "   URL: http://$DATABASE_SERVICE_HOST:$DATABASE_SERVICE_PORT"
    echo "   Health Check: http://$DATABASE_SERVICE_HOST:$DATABASE_SERVICE_PORT/health"
    echo "   API Documentation: http://$DATABASE_SERVICE_HOST:$DATABASE_SERVICE_PORT/docs"
    echo ""
    echo "🔗 Available Endpoints:"
    echo "   GET  /api/databases - List all databases"
    echo "   GET  /api/databases/{name} - Get database details"
    echo "   POST /api/databases/{name}/query - Execute queries"
    echo "   GET  /api/databases/categories/stats - Category statistics"
    echo "   GET  /api/system/overview - System overview"
    echo "=================================================="
    echo "📝 Logs available at: database_service.log"
    echo "🛑 To stop: pkill -f database_service.py"
    echo ""
    
    # Test the service
    echo "🔍 Testing Database Service..."
    sleep 2
    curl -s http://$DATABASE_SERVICE_HOST:$DATABASE_SERVICE_PORT/health | python3 -m json.tool
    
else
    echo "❌ Failed to start Database Service"
    echo "📝 Check database_service.log for details"
    exit 1
fi