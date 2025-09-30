#!/bin/bash

# Zmart Trading Bot Platform - Development Startup Script

echo "🚀 Starting Zmart Trading Bot Platform Development Environment"
echo "=========================================================="

# Function to start frontend
start_frontend() {
    echo "📱 Starting Frontend..."
    cd /Users/dansidanutz/Desktop/ZmartBot/zmart-platform/frontend/zmart-dashboard
    npm run dev &
    echo "✅ Frontend started on http://localhost:5173"
}

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend..."
    cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api
    source venv/bin/activate
    python run_dev.py &
    echo "✅ Backend started on http://localhost:8000"
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Development Environment Status:"
    echo "=================================="
    echo "Frontend: http://localhost:5173"
    echo "Backend:  http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 Tips:"
    echo "- Use 'npm run dev' in frontend directory for hot reload"
    echo "- Use 'python run_dev.py' in backend directory for hot reload"
    echo "- Database connections are optional for development"
    echo ""
}

# Main execution
case "$1" in
    "frontend")
        start_frontend
        ;;
    "backend")
        start_backend
        ;;
    "both")
        start_frontend
        sleep 2
        start_backend
        sleep 2
        show_status
        ;;
    *)
        echo "Usage: $0 {frontend|backend|both}"
        echo ""
        echo "Commands:"
        echo "  frontend  - Start frontend only"
        echo "  backend   - Start backend only"
        echo "  both      - Start both frontend and backend"
        echo ""
        echo "Manual Commands:"
        echo "  Frontend: cd /Users/dansidanutz/Desktop/ZmartBot/zmart-platform/frontend/zmart-dashboard && npm run dev"
        echo "  Backend:  cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api && source venv/bin/activate && python run_dev.py"
        ;;
esac 