#!/bin/bash

# Test various enhanced alerts endpoints to find the working ones

API_URL="http://localhost:8000"

echo "🔍 Testing Enhanced Alerts endpoints..."
echo ""

# Test possible endpoints
endpoints=(
    "/api/v1/alerts/enhanced/stats"
    "/enhanced/stats"
    "/api/enhanced-alerts/stats"
    "/api/v1/enhanced/stats"
    "/alerts/enhanced/stats"
)

for endpoint in "${endpoints[@]}"; do
    echo "Testing: $API_URL$endpoint"
    
    # Get status code and response
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL$endpoint" 2>/dev/null)
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed "s/HTTPSTATUS:[0-9]*//")
    
    if [ "$http_code" = "200" ]; then
        echo "✅ SUCCESS ($http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        echo ""
    elif [ "$http_code" = "404" ]; then
        echo "❌ Not Found (404)"
    elif [ "$http_code" = "000" ]; then
        echo "🔄 Server not responding"
    else
        echo "⚠️  HTTP $http_code"
        echo "$body"
    fi
    echo "---"
done

echo ""
echo "💡 You can also check all available routes at:"
echo "   $API_URL/docs"