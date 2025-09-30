#!/bin/bash

# Zmart Trading Bot Platform - Stop Script
# This script stops the entire platform and cleans up

set -e

echo "🛑 Stopping Zmart Trading Bot Platform..."

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker-compose down

# Optional: Remove volumes (uncomment to reset all data)
# echo "🗑️ Removing volumes..."
# docker-compose down -v

# Optional: Remove images (uncomment to clean up images)
# echo "🗑️ Removing images..."
# docker-compose down --rmi all

echo "✅ Zmart Trading Bot Platform has been stopped!"
echo ""
echo "📝 To start the platform again, run: ./start.sh"
echo "" 