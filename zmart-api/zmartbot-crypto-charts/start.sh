#!/bin/bash

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
