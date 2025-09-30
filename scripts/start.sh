#!/bin/bash

# Zmart Trading Bot Platform - Startup Script
# This script starts the entire platform including all services

set -e

echo "🚀 Starting Zmart Trading Bot Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/influxdb
mkdir -p data/rabbitmq
mkdir -p uploads

# Set environment variables
export COMPOSE_PROJECT_NAME=zmart
export ENVIRONMENT=development

# Start the services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Show service URLs
echo ""
echo "✅ Zmart Trading Bot Platform is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo "   API Documentation: http://localhost:5000/docs"
echo "   Grafana Monitoring: http://localhost:3001"
echo "   Prometheus Metrics: http://localhost:9090"
echo "   Kibana Logs: http://localhost:5601"
echo "   RabbitMQ Management: http://localhost:15672"
echo ""
echo "🔑 Default credentials:"
echo "   Grafana: admin / zmart_grafana_password"
echo "   RabbitMQ: zmart_user / zmart_rabbitmq_password"
echo ""
echo "📝 Logs are available in the 'logs' directory"
echo "🛑 To stop the platform, run: ./stop.sh"
echo "" 