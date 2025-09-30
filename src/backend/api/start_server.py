#!/usr/bin/env python3
"""
Simple server startup script for ZmartBot API
"""
import sys
import os
import uvicorn
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def start_server():
    """Start the ZmartBot API server"""
    try:
        print("🚀 Starting ZmartBot API Server...")
        print(f"📍 Host: 127.0.0.1")
        print(f"📍 Port: 8000")
        print(f"📍 Environment: Development")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            "src.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 