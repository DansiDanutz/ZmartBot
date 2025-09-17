#!/bin/bash

# Zmarty Dashboard Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 Setting up Zmarty Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running from project root
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check dependencies
print_step "Checking dependencies..."

command -v docker >/dev/null 2>&1 || {
    print_error "Docker is required but not installed. Please install Docker first."
    exit 1
}

command -v docker-compose >/dev/null 2>&1 || {
    print_error "Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
}

command -v node >/dev/null 2>&1 || {
    print_warning "Node.js is not installed. Some development features may not work."
}

command -v python3 >/dev/null 2>&1 || {
    print_warning "Python 3 is not installed. Backend development may not work."
}

print_status "Dependencies check completed"

# Create environment files
print_step "Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    print_status "Creating backend .env file..."
    cp backend/.env.example backend/.env
    print_warning "Please edit backend/.env with your configuration"
fi

if [ ! -f "frontend/.env.local" ]; then
    print_status "Creating frontend .env.local file..."
    cp frontend/.env.example frontend/.env.local
    print_warning "Please edit frontend/.env.local with your configuration"
fi

if [ ! -f ".env" ]; then
    print_status "Creating root .env file for Docker Compose..."
    cat > .env << EOF
# Docker Compose Environment Variables
ZMARTY_API_KEY=your-openai-api-key-here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
FIGMA_TOKEN=your_figma_token_here
POSTGRES_PASSWORD=postgres
REDIS_PASSWORD=redis_password
EOF
    print_warning "Please edit .env with your actual API keys"
fi

print_status "Environment files created"

# Setup backend
print_step "Setting up backend..."

if [ -d "backend" ]; then
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    cd ..
fi

print_status "Backend setup completed"

# Setup frontend
print_step "Setting up frontend..."

if [ -d "frontend" ] && command -v npm >/dev/null 2>&1; then
    cd frontend
    
    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    cd ..
fi

print_status "Frontend setup completed"

# Create necessary directories
print_step "Creating necessary directories..."

mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p nginx/ssl
mkdir -p monitoring

print_status "Directories created"

# Setup database
print_step "Setting up database..."

# Start PostgreSQL container for initial setup
print_status "Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Run database migrations
if [ -f "backend/alembic.ini" ]; then
    print_status "Running database migrations..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    
    # Try to run migrations (will create if they don't exist)
    python -c "
import asyncio
from core.database import init_db
asyncio.run(init_db())
print('Database initialized successfully')
" || print_warning "Database migration failed - please run manually"
    
    cd ..
fi

print_status "Database setup completed"

# Generate SSL certificates for development
print_step "Generating SSL certificates for development..."

if [ ! -f "nginx/ssl/localhost.crt" ]; then
    print_status "Generating self-signed SSL certificate..."
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/localhost.key \
        -out nginx/ssl/localhost.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        2>/dev/null || print_warning "SSL certificate generation failed"
fi

print_status "SSL setup completed"

# Create startup script
print_step "Creating startup scripts..."

cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Zmarty Dashboard..."

# Start all services
docker-compose up -d

echo "✅ Services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🔄 Redis: localhost:6379"

# Show logs
docker-compose logs -f
EOF

chmod +x start.sh

cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Zmarty Dashboard..."

# Stop all services
docker-compose down

echo "✅ All services stopped!"
EOF

chmod +x stop.sh

cat > reset.sh << 'EOF'
#!/bin/bash

echo "🔄 Resetting Zmarty Dashboard..."

# Stop and remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove any orphaned containers
docker container prune -f

# Remove any orphaned volumes
docker volume prune -f

echo "✅ Reset completed!"
EOF

chmod +x reset.sh

print_status "Startup scripts created"

# Setup monitoring (optional)
if [ "$1" = "--with-monitoring" ]; then
    print_step "Setting up monitoring..."
    
    # Create Prometheus config
    mkdir -p monitoring
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zmarty-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 30s
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

    # Create Grafana provisioning
    mkdir -p monitoring/grafana/provisioning/datasources
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    print_status "Monitoring setup completed"
fi

# Final setup completion
print_step "Finalizing setup..."

# Create a simple health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

echo "🏥 Checking Zmarty Dashboard health..."

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers are running"
else
    echo "❌ Some containers are not running"
    docker-compose ps
    exit 1
fi

# Check backend health
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000/health >/dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

# Check database connection
if docker-compose exec -T postgres pg_isready >/dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi

echo "🏁 Health check completed"
EOF

chmod +x health-check.sh

print_status "Setup completed successfully! 🎉"

echo ""
echo "📋 Next steps:"
echo "1. Edit .env files with your API keys"
echo "2. Run './start.sh' to start all services"
echo "3. Visit http://localhost:3000 to access the dashboard"
echo ""
echo "🔧 Useful commands:"
echo "  ./start.sh     - Start all services"
echo "  ./stop.sh      - Stop all services"
echo "  ./reset.sh     - Reset everything"
echo "  ./health-check.sh - Check system health"
echo ""
echo "📚 Documentation:"
echo "  API Docs: http://localhost:8000/docs"
echo "  README: ./README.md"
echo ""

if [ "$1" = "--start" ]; then
    print_status "Auto-starting services..."
    ./start.sh
fi