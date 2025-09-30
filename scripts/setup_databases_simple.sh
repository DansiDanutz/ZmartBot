#!/bin/bash

echo "🗄️ ZmartBot Database Setup (Simple Version)"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Homebrew is available
if command -v brew &> /dev/null; then
    print_success "Homebrew found - using Homebrew installation"
    USE_HOMEBREW=true
else
    print_warning "Homebrew not found - will provide manual instructions"
    USE_HOMEBREW=false
fi

echo ""
echo "📋 Database Setup Options:"
echo "1. Install Homebrew and use automated setup"
echo "2. Use Docker (if Docker is installed)"
echo "3. Manual installation instructions"
echo "4. Skip databases for now (server works without them)"
echo ""

read -p "Choose option (1-4): " choice

case $choice in
    1)
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [ $? -eq 0 ]; then
            print_success "Homebrew installed successfully"
            print_status "Setting up databases..."
            ./setup_databases.sh
        else
            print_warning "Homebrew installation failed"
            echo "Please try option 2 or 3"
        fi
        ;;
    2)
        print_status "Checking Docker..."
        if command -v docker &> /dev/null; then
            print_success "Docker found - setting up with Docker"
            docker_setup
        else
            print_warning "Docker not found"
            echo "Please install Docker Desktop first: https://www.docker.com/products/docker-desktop"
        fi
        ;;
    3)
        manual_instructions
        ;;
    4)
        print_success "Skipping database setup"
        echo "Your server is working fine without databases!"
        echo "You can set them up later when needed."
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

docker_setup() {
    echo "🐳 Setting up databases with Docker..."
    
    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: zmart_postgres
    environment:
      POSTGRES_DB: zmart_platform
      POSTGRES_USER: zmart_user
      POSTGRES_PASSWORD: zmart_password_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: zmart_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  influxdb:
    image: influxdb:2.7
    container_name: zmart_influxdb
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: zmart
      DOCKER_INFLUXDB_INIT_PASSWORD: zmart-super-secret-auth-token
      DOCKER_INFLUXDB_INIT_ORG: zmart
      DOCKER_INFLUXDB_INIT_BUCKET: trading_data
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: zmart-super-secret-auth-token
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2

volumes:
  postgres_data:
  redis_data:
  influxdb_data:
EOF

    print_status "Starting Docker services..."
    docker-compose up -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    print_success "Docker databases started!"
    echo "PostgreSQL: localhost:5432"
    echo "Redis: localhost:6379"
    echo "InfluxDB: localhost:8086"
}

manual_instructions() {
    echo ""
    echo "📚 Manual Database Installation Instructions:"
    echo "=========================================="
    echo ""
    echo "1. Install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "2. Install PostgreSQL:"
    echo "   brew install postgresql@15"
    echo "   brew services start postgresql@15"
    echo ""
    echo "3. Install Redis:"
    echo "   brew install redis"
    echo "   brew services start redis"
    echo ""
    echo "4. Install InfluxDB:"
    echo "   brew install influxdb"
    echo "   brew services start influxdb"
    echo ""
    echo "5. Set up databases:"
    echo "   createdb zmart_platform"
    echo "   psql postgres -c \"CREATE USER zmart_user WITH PASSWORD 'zmart_password_dev';\""
    echo "   psql postgres -c \"GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;\""
    echo ""
    echo "6. Test connections:"
    echo "   psql -h localhost -U zmart_user -d zmart_platform"
    echo "   redis-cli ping"
    echo "   influx -execute \"SHOW DATABASES\""
    echo ""
    echo "📖 For detailed instructions, see: DATABASE_SETUP_GUIDE.md"
} 