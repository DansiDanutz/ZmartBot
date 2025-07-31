#!/bin/bash

# ZmartBot Database Setup Script
# This script automatically installs and configures PostgreSQL, Redis, and InfluxDB

set -e  # Exit on any error

echo "🚀 ZmartBot Database Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Homebrew is available
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed. Please install it first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

print_success "Homebrew found"

# Function to install and start a service
install_and_start_service() {
    local service_name=$1
    local brew_package=$2
    local service_command=$3
    
    print_status "Installing $service_name..."
    if brew list $brew_package &>/dev/null; then
        print_warning "$service_name is already installed"
    else
        brew install $brew_package
        print_success "$service_name installed"
    fi
    
    print_status "Starting $service_name service..."
    brew services start $service_command
    print_success "$service_name service started"
}

# Install and start PostgreSQL
print_status "Setting up PostgreSQL..."
install_and_start_service "PostgreSQL" "postgresql@15" "postgresql@15"

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 5

# Setup PostgreSQL database and user
print_status "Creating PostgreSQL database and user..."
createdb zmart_platform 2>/dev/null || print_warning "Database zmart_platform already exists"
psql postgres -c "CREATE USER zmart_user WITH PASSWORD 'zmart_password_dev';" 2>/dev/null || print_warning "User zmart_user already exists"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;" 2>/dev/null || print_warning "Privileges already granted"
print_success "PostgreSQL setup complete"

# Install and start Redis
print_status "Setting up Redis..."
install_and_start_service "Redis" "redis" "redis"

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
sleep 3

# Test Redis connection
if redis-cli ping &>/dev/null; then
    print_success "Redis is responding"
else
    print_error "Redis is not responding"
    exit 1
fi

# Install and start InfluxDB
print_status "Setting up InfluxDB..."
install_and_start_service "InfluxDB" "influxdb" "influxdb"

# Wait for InfluxDB to be ready
print_status "Waiting for InfluxDB to be ready..."
sleep 10

# Setup InfluxDB database and user
print_status "Creating InfluxDB database and user..."
influx -execute "CREATE DATABASE trading_data" 2>/dev/null || print_warning "Database trading_data already exists"
influx -execute "CREATE USER zmart WITH PASSWORD 'zmart-super-secret-auth-token'" 2>/dev/null || print_warning "User zmart already exists"
influx -execute "GRANT ALL ON trading_data TO zmart" 2>/dev/null || print_warning "Privileges already granted"
print_success "InfluxDB setup complete"

# Test all connections
print_status "Testing database connections..."

# Test PostgreSQL
if psql -h localhost -U zmart_user -d zmart_platform -c "SELECT version();" &>/dev/null; then
    print_success "PostgreSQL connection successful"
else
    print_error "PostgreSQL connection failed"
fi

# Test Redis
if redis-cli ping | grep -q "PONG"; then
    print_success "Redis connection successful"
else
    print_error "Redis connection failed"
fi

# Test InfluxDB
if influx -execute "SHOW DATABASES" &>/dev/null; then
    print_success "InfluxDB connection successful"
else
    print_error "InfluxDB connection failed"
fi

echo ""
echo "🎉 Database setup complete!"
echo ""
echo "📊 Service Status:"
brew services list | grep -E "(postgresql|redis|influxdb)"
echo ""
echo "🔗 Connection Details:"
echo "   PostgreSQL: localhost:5432/zmart_platform"
echo "   Redis: localhost:6379"
echo "   InfluxDB: localhost:8086"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart your ZmartBot server: ./backend/zmart-api/start_server.sh"
echo "   2. Test the health endpoint: curl http://localhost:8000/api/v1/health"
echo "   3. Check the logs for any remaining connection errors"
echo ""
echo "📚 For more information, see: DATABASE_SETUP_GUIDE.md" 