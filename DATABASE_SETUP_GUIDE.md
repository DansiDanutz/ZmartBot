# Database Setup Guide for ZmartBot Backend

## Overview
This guide will help you set up the local databases required for the ZmartBot backend system. The current connection errors are expected because these databases aren't running locally.

## Required Databases
1. **PostgreSQL** - Primary database for trading data
2. **Redis** - Caching and session management  
3. **InfluxDB** - Time-series data for metrics

## Option 1: Using Homebrew (Recommended)

### Prerequisites
```bash
# Check if Homebrew is installed
brew --version

# If not installed, install it:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 1. Install PostgreSQL
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database and user
createdb zmart_platform
psql postgres -c "CREATE USER zmart_user WITH PASSWORD 'zmart_password_dev';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;"
```

### 2. Install Redis
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 3. Install InfluxDB
```bash
# Install InfluxDB
brew install influxdb

# Start InfluxDB service
brew services start influxdb

# Wait a moment for InfluxDB to start, then create database
influx -execute "CREATE DATABASE trading_data"
influx -execute "CREATE USER zmart WITH PASSWORD 'zmart-super-secret-auth-token'"
influx -execute "GRANT ALL ON trading_data TO zmart"
```

## Option 2: Using Docker (Alternative)

### Prerequisites
```bash
# Check if Docker is installed
docker --version

# If not installed, download from: https://www.docker.com/products/docker-desktop
```

### Docker Compose Setup
Create a `docker-compose.yml` file in the project root:

```yaml
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
```

### Start Docker Services
```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps
```

## Option 3: Quick Setup Script

I'll create an automated setup script for you:

```bash
#!/bin/bash
# Database Setup Script for ZmartBot

echo "🚀 Setting up ZmartBot databases..."

# Check if Homebrew is available
if command -v brew &> /dev/null; then
    echo "✅ Homebrew found, using Homebrew installation"
    
    # Install PostgreSQL
    echo "📦 Installing PostgreSQL..."
    brew install postgresql@15
    brew services start postgresql@15
    
    # Install Redis
    echo "📦 Installing Redis..."
    brew install redis
    brew services start redis
    
    # Install InfluxDB
    echo "📦 Installing InfluxDB..."
    brew install influxdb
    brew services start influxdb
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Setup PostgreSQL
    echo "🔧 Setting up PostgreSQL..."
    createdb zmart_platform 2>/dev/null || echo "Database already exists"
    psql postgres -c "CREATE USER zmart_user WITH PASSWORD 'zmart_password_dev';" 2>/dev/null || echo "User already exists"
    psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;" 2>/dev/null || echo "Privileges already granted"
    
    # Setup InfluxDB
    echo "🔧 Setting up InfluxDB..."
    influx -execute "CREATE DATABASE trading_data" 2>/dev/null || echo "Database already exists"
    influx -execute "CREATE USER zmart WITH PASSWORD 'zmart-super-secret-auth-token'" 2>/dev/null || echo "User already exists"
    influx -execute "GRANT ALL ON trading_data TO zmart" 2>/dev/null || echo "Privileges already granted"
    
    echo "✅ Database setup complete!"
    
else
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
fi
```

## Verification

After setup, test the connections:

### Test PostgreSQL
```bash
psql -h localhost -U zmart_user -d zmart_platform -c "SELECT version();"
```

### Test Redis
```bash
redis-cli ping
```

### Test InfluxDB
```bash
influx -execute "SHOW DATABASES"
```

## Environment Variables

Make sure your `.env` file (or environment) has these settings:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zmart_platform
DB_USER=zmart_user
DB_PASSWORD=zmart_password_dev

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# InfluxDB Configuration
INFLUX_HOST=localhost
INFLUX_PORT=8086
INFLUX_TOKEN=zmart-super-secret-auth-token
INFLUX_ORG=zmart
INFLUX_BUCKET=trading_data
```

## Troubleshooting

### Common Issues

1. **PostgreSQL connection refused**
   ```bash
   brew services restart postgresql@15
   ```

2. **Redis connection refused**
   ```bash
   brew services restart redis
   ```

3. **InfluxDB connection refused**
   ```bash
   brew services restart influxdb
   ```

4. **Permission denied errors**
   ```bash
   # For PostgreSQL
   sudo chown -R $(whoami) /usr/local/var/postgres
   
   # For Redis
   sudo chown -R $(whoami) /usr/local/var/redis
   ```

### Service Management

```bash
# Check service status
brew services list

# Restart all services
brew services restart postgresql@15
brew services restart redis
brew services restart influxdb

# Stop services
brew services stop postgresql@15
brew services stop redis
brew services stop influxdb
```

## Next Steps

After setting up the databases:

1. **Restart the ZmartBot server** to pick up the new database connections
2. **Test the health endpoint** to verify all databases are connected
3. **Check the logs** to ensure no more connection errors
4. **Run the startup script** to use the proper environment

```bash
# Restart the server
./start_server.sh
```

## Benefits of Local Databases

✅ **No more connection errors**  
✅ **Full functionality** of all features  
✅ **Local development** with real data  
✅ **Better testing** capabilities  
✅ **Performance monitoring** with real metrics  

---

**Status**: Ready for database setup  
**Priority**: High - Required for full functionality  
**Estimated Time**: 15-30 minutes 