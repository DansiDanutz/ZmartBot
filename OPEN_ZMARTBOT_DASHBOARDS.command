#!/bin/bash

echo "🚀 Opening ZmartBot Dashboards..."

# Open all dashboards
open "http://localhost:8090"  # MDC Dashboard
open "http://localhost:8550"  # Service Discovery
open "http://localhost:3400"  # Professional Dashboard
open "http://localhost:3000"  # Service Dashboard

echo "✅ All dashboards opened!"
echo ""
echo "📊 Dashboard URLs:"
echo "  • MDC Dashboard: http://localhost:8090"
echo "  • Service Discovery: http://localhost:8550"
echo "  • Professional Dashboard: http://localhost:3400"
echo "  • Service Dashboard: http://localhost:3000"
echo ""
echo "🔍 Health Check:"
echo "  • MDC Dashboard: http://localhost:8090/health"
echo "  • Service Discovery: http://localhost:8550/health"
echo "  • Professional Dashboard: http://localhost:3400/health"
echo "  • Service Dashboard: http://localhost:3000/health"
