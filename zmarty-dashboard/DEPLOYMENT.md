# Zmarty Dashboard - Complete Deployment Guide

This guide provides step-by-step instructions for deploying the Zmarty Interactive Dashboard in various environments.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (required)
- **Node.js 18+** (for development)
- **Python 3.9+** (for development)
- **PostgreSQL 14+** (or use Docker)
- **Redis** (or use Docker)

### 1-Command Setup

```bash
# Clone and setup everything
git clone <your-repo-url> zmarty-dashboard
cd zmarty-dashboard
chmod +x scripts/setup.sh
./scripts/setup.sh --start
```

This will:
- Check dependencies
- Create environment files
- Set up backend and frontend
- Initialize database
- Start all services

## 📁 Project Structure

```
zmarty-dashboard/
├── backend/                 # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── api/v1/             # API routes
│   ├── core/               # Configuration
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── schemas/            # Pydantic schemas
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   └── stores/         # State management
│   └── public/             # Static assets
├── scripts/                # Setup scripts
├── nginx/                  # Reverse proxy config
├── monitoring/             # Prometheus/Grafana
└── docker-compose.yml      # Service orchestration
```

## 🔧 Environment Configuration

### Backend Configuration (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/zmarty_dashboard

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for Zmarty AI)
ZMARTY_API_KEY=sk-your-openai-api-key-here
ZMARTY_MODEL=gpt-4-turbo-preview

# Stripe (Payment Processing)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Redis
REDIS_URL=redis://localhost:6379/0

# MCP (Optional - for Figma integration)
MCP_FIGMA_SERVER_URL=http://localhost:3001
FIGMA_TOKEN=your_figma_token_here
```

### Frontend Configuration (.env.local)

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Features
VITE_MCP_ENABLED=true
VITE_ENABLE_ANALYTICS=true
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable monitoring
docker-compose --profile monitoring up -d
```

### Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus** (optional): http://localhost:9090
- **Grafana** (optional): http://localhost:3001

## 🏗️ Manual Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb zmarty_dashboard

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS + RDS

```bash
# 1. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier zmarty-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your-password \
  --allocated-storage 20

# 2. Create ECS cluster
aws ecs create-cluster --cluster-name zmarty-cluster

# 3. Deploy using ECS Task Definitions
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs create-service --cluster zmarty-cluster --service-name zmarty-service --task-definition zmarty-task
```

#### Using AWS App Runner

```bash
# 1. Create apprunner.yaml
# 2. Deploy directly from GitHub
aws apprunner create-service \
  --service-name zmarty-dashboard \
  --source-configuration file://aws/apprunner-config.json
```

### Google Cloud Deployment

#### Using Cloud Run

```bash
# 1. Build and push container
gcloud builds submit --tag gcr.io/your-project/zmarty-backend
gcloud builds submit --tag gcr.io/your-project/zmarty-frontend

# 2. Deploy to Cloud Run
gcloud run deploy zmarty-backend \
  --image gcr.io/your-project/zmarty-backend \
  --platform managed \
  --region us-central1

gcloud run deploy zmarty-frontend \
  --image gcr.io/your-project/zmarty-frontend \
  --platform managed \
  --region us-central1
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# 1. Create resource group
az group create --name zmarty-rg --location eastus

# 2. Create PostgreSQL
az postgres server create \
  --resource-group zmarty-rg \
  --name zmarty-db \
  --admin-user postgres \
  --admin-password your-password

# 3. Deploy containers
az container create \
  --resource-group zmarty-rg \
  --name zmarty-backend \
  --image your-registry/zmarty-backend:latest \
  --environment-variables DATABASE_URL=your-connection-string
```

## 🔒 Production Security

### SSL/TLS Setup

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Environment Variables

```bash
# Use secrets management
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name zmarty-secrets \
  --description "Zmarty Dashboard secrets" \
  --secret-string file://secrets.json

# Google Secret Manager
gcloud secrets create zmarty-secrets --data-file secrets.json

# Azure Key Vault
az keyvault secret set \
  --vault-name zmarty-vault \
  --name secrets \
  --file secrets.json
```

### Database Security

```bash
# PostgreSQL security settings
# In postgresql.conf:
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

# In pg_hba.conf:
hostssl all all 0.0.0.0/0 md5
```

## 📊 Monitoring & Logging

### Application Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Log Aggregation

```bash
# Using ELK Stack
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d

# Using Loki + Grafana
docker-compose -f docker-compose.yml -f docker-compose.loki.yml up -d
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health  
curl http://localhost:3000/health

# Database health
docker-compose exec postgres pg_isready

# Full system health
./health-check.sh
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py -v

# Run integration tests
pytest -m integration
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run e2e tests
npm run test:e2e

# Generate test coverage
npm run test:coverage
```

### Load Testing

```bash
# Using Artillery
npm install -g artillery
artillery run load-test.yml

# Using k6
k6 run load-test.js
```

## 🚀 Performance Optimization

### Backend Optimization

```python
# Use connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 0,
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Enable Redis caching
CACHE_TTL = 300  # 5 minutes
```

### Frontend Optimization

```javascript
// Enable code splitting
const ZmartyChat = lazy(() => import('./components/Dashboard/ZmartyChat'))

// Optimize bundle size
import { debounce } from 'lodash/debounce'  // Import specific functions

// Enable service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}
```

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_zmarty_requests_user_id_status ON zmarty_requests(user_id, status);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

## 🔧 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check database connection
python -c "from core.database import test_connection; test_connection()"

# Check environment variables
python -c "from core.config import get_settings; print(get_settings())"
```

#### Frontend build fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Check TypeScript
npm run type-check
```

#### Database connection issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
docker-compose exec postgres pg_isready

# Check connection string
psql $DATABASE_URL -c "SELECT 1"
```

#### WebSocket connection fails
```bash
# Check Redis connection
redis-cli ping
docker-compose exec redis redis-cli ping

# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/chat/your-token
```

### Performance Issues

```bash
# Monitor resource usage
docker stats
htop

# Check database performance
docker-compose exec postgres pg_stat_activity

# Monitor API performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health
```

### Debug Mode

```bash
# Backend debug
export DEBUG=1
uvicorn main:app --reload --log-level debug

# Frontend debug
export VITE_DEBUG_MODE=true
npm run dev
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 🆘 Support

- **Documentation**: ./README.md
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: support@zmartydashboard.com

---

**🎉 You now have a complete, production-ready Zmarty Interactive Dashboard!**