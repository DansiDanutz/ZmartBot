#!/bin/bash

# Zmart Trading Bot Platform - Development Stop Script

set -e

echo "🛑 Stopping Zmart Trading Bot Platform..."

# Stop all services
echo "🐳 Stopping Docker services..."
docker-compose down

echo "✅ All services stopped successfully!"
echo ""
echo "💡 To start the platform again, run: ./start.sh" 