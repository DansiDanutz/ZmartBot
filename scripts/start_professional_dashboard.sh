#!/bin/bash

# Start the Professional Dashboard standalone server on port 3400
# Port policy: freeze 3400 for this module

set -euo pipefail

cd "$(dirname "$0")"

PORT=3400

echo "🚀 Starting Professional Dashboard on port $PORT..."

# Kill existing process on port
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "🔧 Freeing port $PORT"
  lsof -ti:$PORT | xargs kill -9 || true
  sleep 1
fi

export PYTHONPATH=src:${PYTHONPATH:-}

uvicorn professional_dashboard_server:app --host 0.0.0.0 --port $PORT --log-level info


