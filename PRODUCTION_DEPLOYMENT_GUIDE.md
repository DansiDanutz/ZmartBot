# ZmartBot Production Deployment Guide
**Version:** 1.0  
**Last Updated:** August 7, 2025

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **CPU:** 4+ cores recommended
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 50GB+ SSD
- **OS:** Ubuntu 22.04 LTS or similar

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- Git
- Python 3.11+ (for local development)
- kubectl (for Kubernetes deployment)

### API Keys Required
- Cryptometer API Key
- KuCoin API credentials (Key, Secret, Passphrase)
- OpenAI API Key
- Google Sheets API credentials (optional)

## Deployment Options

### 1. Docker Compose (Recommended for Small-Medium Scale)
Best for: Single server deployments, development, staging

### 2. Kubernetes (Recommended for Large Scale)
Best for: Multi-node clusters, high availability, auto-scaling

### 3. Cloud Platforms
- AWS ECS/EKS
- Google Cloud Run/GKE
- Azure Container Instances/AKS
- DigitalOcean App Platform

## Docker Deployment

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/your-org/zmartbot.git
cd zmartbot

# 2. Create production environment file
cp .env.example .env.production
# Edit .env.production with your API keys and passwords

# 3. Deploy
chmod +x deploy.sh
./deploy.sh production
```

### Step-by-Step Docker Deployment

#### 1. Prepare Environment
```bash
# Create necessary directories
mkdir -p logs data backups monitoring/grafana/dashboards

# Set up environment file
cat > .env.production << EOF
# Database
POSTGRES_USER=zmartbot
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=zmartbot_db

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# RabbitMQ
RABBITMQ_DEFAULT_USER=zmartbot
RABBITMQ_DEFAULT_PASS=$(openssl rand -base64 32)

# Application
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Your API Keys
CRYPTOMETER_API_KEY=your_key_here
KUCOIN_API_KEY=your_key_here
KUCOIN_SECRET=your_secret_here
KUCOIN_PASSPHRASE=your_passphrase_here
OPENAI_API_KEY=your_key_here
EOF
```

#### 2. Build and Deploy
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Verify health
curl http://localhost:8000/health
```

#### 3. Initialize Database
```bash
# Run migrations
docker-compose exec app alembic upgrade head

# Create admin user (optional)
docker-compose exec app python -c "from src.database import create_admin_user; create_admin_user()"
```

## Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Helm (optional but recommended)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Deployment Steps

#### 1. Build and Push Image
```bash
# Build image
docker build -t zmartbot:latest .

# Tag for registry
docker tag zmartbot:latest your-registry/zmartbot:latest

# Push to registry
docker push your-registry/zmartbot:latest
```

#### 2. Update Secrets
```bash
# Edit k8s-deployment.yaml with your actual secrets
vim k8s-deployment.yaml

# Or create secrets from command line
kubectl create secret generic zmartbot-secrets \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=REDIS_URL='redis://...' \
  --from-literal=JWT_SECRET_KEY='...' \
  -n zmartbot
```

#### 3. Deploy to Kubernetes
```bash
# Apply configuration
kubectl apply -f k8s-deployment.yaml

# Check deployment status
kubectl get pods -n zmartbot

# Check service
kubectl get svc -n zmartbot

# Get external IP
kubectl get svc zmartbot-service -n zmartbot -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Cloud Deployment

### AWS ECS Deployment
```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI
docker build -t zmartbot .
docker tag zmartbot:latest $ECR_URI/zmartbot:latest
docker push $ECR_URI/zmartbot:latest

# 2. Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# 3. Create service
aws ecs create-service \
  --cluster zmartbot-cluster \
  --service-name zmartbot \
  --task-definition zmartbot:1 \
  --desired-count 2
```

### Google Cloud Run
```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/$PROJECT_ID/zmartbot

# 2. Deploy to Cloud Run
gcloud run deploy zmartbot \
  --image gcr.io/$PROJECT_ID/zmartbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat .env.production | grep -v '^#' | xargs)"
```

### DigitalOcean App Platform
```bash
# 1. Install doctl
snap install doctl

# 2. Create app
doctl apps create --spec app.yaml

# app.yaml example:
name: zmartbot
services:
- name: api
  github:
    repo: your-org/zmartbot
    branch: main
  dockerfile_path: Dockerfile
  instance_size_slug: professional-xs
  instance_count: 2
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    value: ${db.DATABASE_URL}
databases:
- name: db
  engine: PG
  version: "14"
```

## Monitoring & Maintenance

### Access Monitoring Tools
- **Grafana:** http://your-server:3000 (admin/admin)
- **Prometheus:** http://your-server:9090
- **RabbitMQ Management:** http://your-server:15672

### Set Up Alerts
```bash
# Create alert rules in Prometheus
cat > monitoring/alerts.yml << EOF
groups:
- name: zmartbot
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    annotations:
      summary: High error rate detected
      
  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 1m
    annotations:
      summary: PostgreSQL is down
EOF
```

### Backup Strategy
```bash
# Automated daily backups
crontab -e
# Add:
0 2 * * * /opt/zmartbot/backup.sh

# Manual backup
docker exec zmartbot-postgres pg_dump -U zmartbot zmartbot_db > backup_$(date +%Y%m%d).sql
```

### Monitoring Commands
```bash
# Check service health
docker-compose ps
kubectl get pods -n zmartbot

# View logs
docker-compose logs -f app
kubectl logs -f deployment/zmartbot-app -n zmartbot

# Check resource usage
docker stats
kubectl top pods -n zmartbot

# Database queries
docker exec -it zmartbot-postgres psql -U zmartbot -d zmartbot_db
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
docker-compose logs app

# Common fixes:
# - Verify all environment variables are set
# - Check database connectivity
# - Ensure ports are not already in use
```

#### 2. Database Connection Issues
```bash
# Test connection
docker exec -it zmartbot-postgres psql -U zmartbot -d zmartbot_db

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec app alembic upgrade head
```

#### 3. High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart app

# Adjust memory limits in docker-compose.yml
```

#### 4. API Rate Limiting
```bash
# Check rate limit status
curl http://localhost:8000/api/status

# Adjust rate limits in src/security/rate_limiting.py
```

### Performance Tuning

#### Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_positions_status ON positions(status);

-- Analyze tables
ANALYZE trades;
ANALYZE positions;
```

#### Redis Optimization
```bash
# Configure max memory
docker exec zmartbot-redis redis-cli CONFIG SET maxmemory 2gb
docker exec zmartbot-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### Application Tuning
```python
# Update src/config/settings.py
WORKER_PROCESSES = 4  # Adjust based on CPU cores
WORKER_CONNECTIONS = 1000
KEEPALIVE = 5
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] API key rotation schedule
- [ ] Backup encryption
- [ ] Network isolation
- [ ] Rate limiting configured
- [ ] Input validation enabled

## Support & Resources

- **Documentation:** [docs.zmartbot.com](https://docs.zmartbot.com)
- **GitHub Issues:** [github.com/your-org/zmartbot/issues](https://github.com/your-org/zmartbot/issues)
- **Discord:** [discord.gg/zmartbot](https://discord.gg/zmartbot)
- **Email:** support@zmartbot.com

## License
Copyright © 2025 ZmartBot. All rights reserved.