#!/bin/bash

echo "🚀 Simple ZmartBot Backend Start"
echo "================================"

cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api
source venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
export METRICS_ENABLED=false

echo "✅ Starting minimal server (no monitoring)"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload