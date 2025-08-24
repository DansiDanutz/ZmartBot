#!/bin/bash

# Quick health check for ZmartBot API
# Usage: ./quick_check.sh [endpoint]

API_URL="http://localhost:8000"
ENDPOINT="${1:-/api/v1/alerts/enhanced/stats}"

echo "🔍 Checking if ZmartBot API is ready..."

# Function to wait for readiness
wait_for_ready() {
    local max_attempts=15
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health/ready" 2>/dev/null || echo "000")
        
        if [ "$status_code" = "200" ]; then
            echo "✅ API is ready!"
            return 0
        fi
        
        printf "⏳ Waiting... (attempt %d/%d)\r" $attempt $max_attempts
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo "❌ API not ready after 15 seconds"
    return 1
}

# Wait for API to be ready
if wait_for_ready; then
    echo "🎯 Calling: $ENDPOINT"
    echo ""
    curl -s "$API_URL$ENDPOINT" | jq '.' 2>/dev/null || curl -s "$API_URL$ENDPOINT"
else
    echo "💡 Try checking manually: curl -s $API_URL/health/ready"
    exit 1
fi