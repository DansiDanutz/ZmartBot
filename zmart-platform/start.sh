#!/bin/bash

# Zmart Trading Bot Platform - Development Startup Script

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
mkdir -p infrastructure/docker/{postgres,redis,rabbitmq,nginx,prometheus,grafana}

# Copy configuration files if they don't exist
if [ ! -f infrastructure/docker/postgres/init.sql ]; then
    echo "📄 Creating PostgreSQL init script..."
    cat > infrastructure/docker/postgres/init.sql << 'EOF'
-- PostgreSQL initialization script
CREATE DATABASE IF NOT EXISTS zmart_platform;
EOF
fi

if [ ! -f infrastructure/docker/redis/redis.conf ]; then
    echo "📄 Creating Redis configuration..."
    cat > infrastructure/docker/redis/redis.conf << 'EOF'
# Redis configuration
requirepass zmart_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
fi

if [ ! -f infrastructure/docker/rabbitmq/rabbitmq.conf ]; then
    echo "📄 Creating RabbitMQ configuration..."
    cat > infrastructure/docker/rabbitmq/rabbitmq.conf << 'EOF'
# RabbitMQ configuration
default_vhost = zmart_vhost
default_user = zmart_user
default_pass = zmart_rabbitmq_password
EOF
fi

if [ ! -f infrastructure/docker/prometheus/prometheus.yml ]; then
    echo "📄 Creating Prometheus configuration..."
    cat > infrastructure/docker/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zmart-backend'
    static_configs:
      - targets: ['backend:5000']
EOF
fi

# Start the services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo "✅ Zmart Trading Bot Platform is starting up!"
echo ""
echo "📊 Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:5000"
echo "  - API Docs: http://localhost:5000/docs"
echo "  - Grafana: http://localhost:3001 (admin/zmart_grafana_password)"
echo "  - Kibana: http://localhost:5601"
echo "  - Prometheus: http://localhost:9090"
echo ""
echo "🔧 To stop the platform, run: ./stop.sh"
echo "📝 To view logs, run: docker-compose logs -f" 