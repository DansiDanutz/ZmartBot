
# Installation Guide

This guide provides step-by-step instructions for setting up the Symbol Alerts System in various environments.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Internet connection for real-time data

### Required Accounts
- Exchange API access (Binance, KuCoin, etc.)
- Optional: Redis server for scaling
- Optional: PostgreSQL for production database

## Installation Methods

### Method 1: Quick Setup with Cursor IDE (Recommended)

#### Step 1: Environment Setup
1. **Install Python 3.11+**
   ```bash
   # Windows (using chocolatey)
   choco install python

   # macOS (using homebrew)
   brew install python@3.11

   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-pip
   ```

2. **Install Cursor IDE**
   - Download from [cursor.sh](https://cursor.sh)
   - Install and launch the application

#### Step 2: Project Setup
1. **Extract the project files** to your desired directory
2. **Open in Cursor IDE**:
   - File → Open Folder
   - Select the `symbol_alerts_system` directory

3. **Open integrated terminal** in Cursor (Ctrl+` or View → Terminal)

#### Step 3: Dependencies Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install TA-Lib (for technical indicators)
# Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl

# macOS
brew install ta-lib
pip install TA-Lib

# Ubuntu/Debian
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

#### Step 4: Configuration
1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit configuration** in Cursor:
   - Open `.env` file
   - Update the following essential settings:

   ```env
   # Database (SQLite for development)
   DATABASE_URL=sqlite:///./alerts.db

   # API Server
   API_HOST=0.0.0.0
   API_PORT=8000

   # WebSocket Server
   WS_HOST=0.0.0.0
   WS_PORT=8001

   # Exchange APIs (get from your exchange)
   KUCOIN_API_KEY=your-kucoin-api-key
   KUCOIN_SECRET=your-kucoin-secret
   KUCOIN_PASSPHRASE=your-kucoin-passphrase
   EXCHANGE_SANDBOX=true

   # Security
   API_SECRET_KEY=your-unique-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

#### Step 5: Database Setup
```bash
# Initialize database (automatic on first run)
python -c "
import asyncio
from config.database import init_database
asyncio.run(init_database())
print('Database initialized successfully')
"
```

#### Step 6: First Run
```bash
# Start the system
python main.py
```

You should see output like:
```
INFO - Starting Symbol Alerts System...
INFO - Database initialized
INFO - Alert Engine initialized
INFO - API Server started on 0.0.0.0:8000
INFO - WebSocket server started on 0.0.0.0:8001
```

### Method 2: Docker Setup

#### Step 1: Docker Installation
Install Docker and Docker Compose on your system.

#### Step 2: Docker Configuration
1. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     alerts:
       build: .
       ports:
         - "8000:8000"
         - "8001:8001"
       environment:
         - DATABASE_URL=postgresql://alerts:password@db:5432/alerts
         - REDIS_URL=redis://redis:6379
       depends_on:
         - db
         - redis
       volumes:
         - ./logs:/app/logs

     db:
       image: postgres:15
       environment:
         POSTGRES_DB: alerts
         POSTGRES_USER: alerts
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data

     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data

   volumes:
     postgres_data:
     redis_data:
   ```

2. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       libta-lib-dev \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create logs directory
   RUN mkdir -p logs

   # Expose ports
   EXPOSE 8000 8001

   # Run the application
   CMD ["python", "main.py"]
   ```

#### Step 3: Run with Docker
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d
```

### Method 3: Production Setup

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-pip python3.11-venv \
    postgresql postgresql-contrib redis-server nginx \
    build-essential libta-lib-dev

# Create application user
sudo useradd -m -s /bin/bash alerts
sudo usermod -aG sudo alerts
```

#### Step 2: Database Setup
```bash
# Configure PostgreSQL
sudo -u postgres createuser alerts
sudo -u postgres createdb alerts -O alerts
sudo -u postgres psql -c "ALTER USER alerts PASSWORD 'your-secure-password';"
```

#### Step 3: Application Deployment
```bash
# Switch to alerts user
sudo su - alerts

# Clone/copy application
git clone <repository-url> symbol_alerts_system
cd symbol_alerts_system

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
# Edit .env with production settings
```

#### Step 4: Systemd Service
Create `/etc/systemd/system/symbol-alerts.service`:
```ini
[Unit]
Description=Symbol Alerts System
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=alerts
WorkingDirectory=/home/alerts/symbol_alerts_system
Environment=PATH=/home/alerts/symbol_alerts_system/venv/bin
ExecStart=/home/alerts/symbol_alerts_system/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable symbol-alerts
sudo systemctl start symbol-alerts
sudo systemctl status symbol-alerts
```

## Configuration Details

### Exchange API Setup

#### KuCoin API
1. Login to KuCoin
2. Go to API Management
3. Create new API key with trading permissions
4. Note the API Key, Secret, and Passphrase
5. Add to `.env` file

#### Binance API
1. Login to Binance
2. Go to API Management
3. Create new API key
4. Enable spot trading
5. Add to `.env` file

### Database Configuration

#### SQLite (Development)
```env
DATABASE_URL=sqlite:///./alerts.db
```

#### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/alerts
```

### Redis Configuration (Optional)
```env
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password
```

## Verification

### Health Check
```bash
# Check API server
curl http://localhost:8000/health

# Check WebSocket server
wscat -c ws://localhost:8001
```

### Test Alert Creation
```bash
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "symbol": "BTCUSDT",
    "alert_type": "price_above",
    "conditions": [{
      "field": "price",
      "operator": ">",
      "value": 50000,
      "timeframe": "5m"
    }],
    "message": "BTC above $50,000"
  }'
```

## Troubleshooting

### Common Issues

#### TA-Lib Installation Error
```bash
# Windows: Download wheel file manually
# macOS: Install with homebrew first
brew install ta-lib

# Linux: Install development headers
sudo apt-get install libta-lib-dev
```

#### Database Connection Error
- Check database URL in `.env`
- Ensure database server is running
- Verify credentials and permissions

#### WebSocket Connection Failed
- Check firewall settings
- Verify port 8001 is available
- Check WebSocket server logs

#### Exchange API Errors
- Verify API credentials
- Check API permissions
- Ensure sandbox mode setting matches

### Log Files
```bash
# View application logs
tail -f logs/alerts.log

# View systemd logs (production)
sudo journalctl -u symbol-alerts -f
```

### Performance Tuning

#### For High Volume
```env
# Increase database pool size
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Adjust notification queue
NOTIFICATION_QUEUE_LIMIT=50000

# Enable Redis for caching
REDIS_URL=redis://localhost:6379
```

#### Memory Optimization
```env
# Limit trigger history
MAX_TRIGGER_HISTORY=500

# Reduce cleanup interval
CLEANUP_INTERVAL_HOURS=6
```

## Next Steps

After successful installation:
1. Read the [API Documentation](API.md)
2. Check [Usage Examples](examples/)
3. Review [Trading Bot Integration](TRADING_INTEGRATION.md)
4. Set up [Monitoring](MONITORING.md)

