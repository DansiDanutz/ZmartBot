#!/bin/bash

# Wait for ZmartBot API to be ready
# This script replaces the need for "sleep 10"

set -e

API_URL="http://localhost:8000"
MAX_ATTEMPTS=30
ATTEMPT=1

echo "🚀 Waiting for ZmartBot API to be ready..."

# Function to check if API is ready
check_ready() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health/ready" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# Wait for the API to be ready
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    
    if check_ready; then
        echo "✅ ZmartBot API is ready!"
        
        # Show the full readiness status
        echo "📊 Full system status:"
        curl -s "$API_URL/health/ready" | jq '.' 2>/dev/null || curl -s "$API_URL/health/ready"
        
        # Now run your original command
        echo ""
        echo "🎯 Running enhanced alerts stats:"
        curl -s "$API_URL/api/v1/alerts/enhanced/stats" | jq '.' 2>/dev/null || curl -s "$API_URL/api/v1/alerts/enhanced/stats"
        
        exit 0
    else
        # Check basic health to see if server is at least starting
        basic_health=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" 2>/dev/null || echo "000")
        
        if [ "$basic_health" = "200" ]; then
            echo "⏳ Server is starting, but not all services are ready yet..."
        else
            echo "🔄 Server not responding yet..."
        fi
        
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo "❌ Timeout: ZmartBot API did not become ready after $((MAX_ATTEMPTS * 2)) seconds"
echo "💡 You can check the status manually with:"
echo "   curl -s $API_URL/health/ready"
exit 1