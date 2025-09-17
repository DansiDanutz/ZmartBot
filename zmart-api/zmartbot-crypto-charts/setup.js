const fs = require('fs');
const path = require('path');

console.log('🚀 Setting up ZmartBot Crypto Charts Service...');

// Create necessary directories
const dirs = [
    'logs',
    'data',
    'cache'
];

dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`✅ Created directory: ${dir}`);
    }
});

// Create .env file if it doesn't exist
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
    const envContent = `# ZmartBot Crypto Charts Configuration
PORT=8901
WS_PORT=8902
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info

# API Rate Limits (requests per minute)
COINGECKO_RATE_LIMIT=50
BINANCE_RATE_LIMIT=1200
CRYPTOMETER_RATE_LIMIT=100

# Cache Settings
CACHE_TTL=300
HISTORY_CACHE_TTL=3600

# Database Settings
DB_PATH=./data/crypto_charts.db

# Security
CORS_ORIGIN=*
HELMET_ENABLED=true
COMPRESSION_ENABLED=true

# Logging
LOG_FILE=./logs/server.log
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5
`;
    
    fs.writeFileSync(envPath, envContent);
    console.log('✅ Created .env file with default configuration');
}

// Create .gitignore file
const gitignorePath = path.join(__dirname, '.gitignore');
if (!fs.existsSync(gitignorePath)) {
    const gitignoreContent = `# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# Database files
data/
*.db
*.sqlite

# Cache files
cache/
*.cache

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
tmp/
temp/
`;
    
    fs.writeFileSync(gitignorePath, gitignoreContent);
    console.log('✅ Created .gitignore file');
}

// Create README.md
const readmePath = path.join(__dirname, 'README.md');
if (!fs.existsSync(readmePath)) {
    const readmeContent = `# ZmartBot Crypto Charts Service

Professional crypto charts with free APIs - Zero cost development

## Features

- 📊 Real-time cryptocurrency price charts
- 🔄 Multiple timeframes (1H, 4H, 1D, 1W, 1M)
- 📈 Market overview with top gainers/losers
- 🚀 Free API integration (CoinGecko, Binance, Cryptometer)
- 💾 Intelligent caching system
- 🔒 Security-first approach with Helmet.js
- 📱 Responsive design
- ⚡ High-performance with compression

## Quick Start

1. **Install dependencies:**
   \`\`\`bash
   npm install
   \`\`\`

2. **Setup environment:**
   \`\`\`bash
   node setup.js
   \`\`\`

3. **Start the service:**
   \`\`\`bash
   npm start
   \`\`\`

4. **Access the application:**
   - Web Interface: http://localhost:8901
   - Health Check: http://localhost:8901/health
   - API Documentation: http://localhost:8901/api

## API Endpoints

### Health Check
- \`GET /health\` - Service health status

### Market Data
- \`GET /api/symbols\` - Get supported symbols
- \`GET /api/prices?symbol=BTC\` - Get current price
- \`GET /api/history?symbol=BTC&interval=1d&limit=100\` - Get historical data
- \`GET /api/market-overview\` - Get market overview

### WebSocket
- \`WS /ws\` - Real-time price updates

## Configuration

Edit \`.env\` file to customize:
- Port settings
- API rate limits
- Cache settings
- Database configuration
- Security settings

## Architecture

- **Frontend**: HTML5 + CSS3 + JavaScript (Chart.js)
- **Backend**: Node.js + Express.js
- **Real-time**: WebSocket
- **Caching**: Redis
- **Database**: SQLite3
- **Security**: Helmet.js + CORS
- **Performance**: Compression + Winston logging

## Integration with ZmartBot

This service integrates with the ZmartBot ecosystem:
- Port Manager integration for dynamic port assignment
- Service discovery and registration
- Health monitoring and reporting
- Master Orchestration Agent compatibility

## Development

\`\`\`bash
# Development mode with auto-reload
npm run dev

# Install dependencies
npm run install-deps

# Setup environment
npm run setup
\`\`\`

## License

MIT License - See LICENSE file for details

## Support

For support and questions, contact the ZmartBot development team.
`;
    
    fs.writeFileSync(readmePath, readmeContent);
    console.log('✅ Created README.md file');
}

// Create Dockerfile
const dockerfilePath = path.join(__dirname, 'Dockerfile');
if (!fs.existsSync(dockerfilePath)) {
    const dockerfileContent = `FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs data cache

# Expose ports
EXPOSE 8901 8902

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8901/health || exit 1

# Start the application
CMD ["npm", "start"]
`;
    
    fs.writeFileSync(dockerfilePath, dockerfileContent);
    console.log('✅ Created Dockerfile');
}

// Create docker-compose.yml
const composePath = path.join(__dirname, 'docker-compose.yml');
if (!fs.existsSync(composePath)) {
    const composeContent = `version: '3.8'

services:
  crypto-charts:
    build: .
    ports:
      - "8901:8901"
      - "8902:8902"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./cache:/app/cache
    restart: unless-stopped
    networks:
      - zmartbot-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - zmartbot-network

volumes:
  redis-data:

networks:
  zmartbot-network:
    driver: bridge
`;
    
    fs.writeFileSync(composePath, composeContent);
    console.log('✅ Created docker-compose.yml');
}

// Create start.sh script
const startScriptPath = path.join(__dirname, 'start.sh');
if (!fs.existsSync(startScriptPath)) {
    const startScriptContent = `#!/bin/bash

echo "🚀 Starting ZmartBot Crypto Charts Service..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Setup environment if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment..."
    node setup.js
fi

# Create necessary directories
mkdir -p logs data cache

# Start the service
echo "🎯 Starting service on port 8901..."
npm start
`;
    
    fs.writeFileSync(startScriptPath, startScriptContent);
    fs.chmodSync(startScriptPath, '755');
    console.log('✅ Created start.sh script');
}

// Create stop.sh script
const stopScriptPath = path.join(__dirname, 'stop.sh');
if (!fs.existsSync(stopScriptPath)) {
    const stopScriptContent = `#!/bin/bash

echo "🛑 Stopping ZmartBot Crypto Charts Service..."

# Find and kill the Node.js process
PID=$(pgrep -f "node.*server.js")

if [ -n "$PID" ]; then
    echo "📋 Found process with PID: $PID"
    kill -TERM $PID
    
    # Wait for graceful shutdown
    sleep 5
    
    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️  Force killing process..."
        kill -KILL $PID
    fi
    
    echo "✅ Service stopped successfully"
else
    echo "ℹ️  No running service found"
fi
`;
    
    fs.writeFileSync(stopScriptPath, stopScriptContent);
    fs.chmodSync(stopScriptPath, '755');
    console.log('✅ Created stop.sh script');
}

console.log('🎉 Setup completed successfully!');
console.log('');
console.log('Next steps:');
console.log('1. Run: npm install');
console.log('2. Run: ./start.sh');
console.log('3. Access: http://localhost:8901');
console.log('');
console.log('For development:');
console.log('- Run: npm run dev');
console.log('- Edit files in real-time');
console.log('');
console.log('For production:');
console.log('- Run: docker-compose up -d');
console.log('- Service will be available on port 8901');
