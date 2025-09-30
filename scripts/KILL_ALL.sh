#!/bin/bash

echo "🚨 KILLING ALL PROCESSES - This will stop everything!"

# Kill all Python processes
sudo pkill -9 python

# Kill all uvicorn processes  
sudo pkill -9 uvicorn

# Kill processes on specific ports
sudo lsof -ti:8000 | xargs kill -9 2>/dev/null
sudo lsof -ti:5432 | xargs kill -9 2>/dev/null
sudo lsof -ti:6379 | xargs kill -9 2>/dev/null
sudo lsof -ti:8086 | xargs kill -9 2>/dev/null

# Wait
sleep 3

echo "✅ All processes killed!"
echo "Now run: ./cleanup_and_health_check.sh" 