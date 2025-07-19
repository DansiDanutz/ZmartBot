#!/bin/bash

# Zmart Trading Bot Platform - Production Deployment Script

set -e

echo "🚀 Deploying Zmart Trading Bot Platform to Production..."

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

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Create production directories
echo "📁 Creating production directories..."
mkdir -p infrastructure/docker/{postgres,redis,rabbitmq,nginx,prometheus,grafana}

# Create production configuration files
echo "📄 Creating production configuration files..."

# PostgreSQL production config
cat > infrastructure/docker/postgres/init.sql << 'EOF'
-- PostgreSQL production initialization script
CREATE DATABASE IF NOT EXISTS zmart_platform;
CREATE USER IF NOT EXISTS zmart_user WITH PASSWORD 'zmart_password_prod';
GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;
EOF

# Redis production config
cat > infrastructure/docker/redis/redis.conf << 'EOF'
# Redis production configuration
requirepass zmart_redis_password_prod
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF

# RabbitMQ production config
cat > infrastructure/docker/rabbitmq/rabbitmq.conf << 'EOF'
# RabbitMQ production configuration
default_vhost = zmart_vhost
default_user = zmart_user
default_pass = zmart_rabbitmq_password_prod
log.console = true
log.console.level = info
EOF

# Prometheus production config
cat > infrastructure/docker/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'zmart-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/api/v1/monitoring/metrics'
    scrape_interval: 15s

  - job_name: 'zmart-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/health'
    scrape_interval: 30s
EOF

# Build and deploy
echo "🔨 Building production images..."
docker-compose build --no-cache

echo "🐳 Starting production services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 60

# Check service health
echo "🔍 Checking production service health..."
docker-compose ps

echo "✅ Zmart Trading Bot Platform deployed successfully!"
echo ""
echo "📊 Production Services:"
echo "  - Frontend: https://your-domain.com"
echo "  - Backend API: https://your-domain.com/api"
echo "  - API Docs: https://your-domain.com/docs"
echo "  - Grafana: https://your-domain.com/grafana"
echo "  - Prometheus: https://your-domain.com/prometheus"
echo ""
echo "🔧 To stop production: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
echo "🔄 To update: ./deploy.sh" 