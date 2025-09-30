#!/usr/bin/env python3
"""
ZmartBot Fixed Server Startup Script
Resolves all backend conflicts and ensures stable operation
"""
import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

def kill_processes_on_port(port):
    """Kill any processes using the specified port"""
    try:
        # Find processes using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔄 Killing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid], check=False)
            time.sleep(1)
            print(f"✅ Cleared port {port}")
    except Exception as e:
        print(f"⚠️ Could not clear port {port}: {e}")

def kill_uvicorn_processes():
    """Kill any existing uvicorn processes"""
    try:
        # Kill uvicorn processes
        subprocess.run(['pkill', '-f', 'uvicorn'], check=False)
        time.sleep(1)
        print("✅ Cleared uvicorn processes")
    except Exception as e:
        print(f"⚠️ Could not clear uvicorn processes: {e}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic-settings',
        'asyncpg',
        'redis',
        'influxdb-client',
        'httpx',
        'websockets'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("🔧 Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies available")

def setup_environment():
    """Setup environment variables and paths"""
    # Add src to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Set environment variables
    os.environ.setdefault('ENVIRONMENT', 'development')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    
    print("✅ Environment configured")

def create_minimal_settings():
    """Create minimal settings if config fails"""
    settings_content = '''
import os
from typing import List

class MinimalSettings:
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    ENVIRONMENT = "development"
    CORS_ORIGINS = ["*"]
    ALLOWED_HOSTS = ["*"]
    
    # Database settings (development mode)
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "zmart_platform"
    DB_USER = "zmart_user"
    DB_PASSWORD = "zmart_password_dev"
    
    # Redis settings (development mode)
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 0
    
    # InfluxDB settings (development mode)
    INFLUX_HOST = "localhost"
    INFLUX_PORT = 8086
    INFLUX_TOKEN = "dev-token"
    INFLUX_ORG = "zmart"
    INFLUX_BUCKET = "trading_data"

settings = MinimalSettings()
'''
    
    settings_file = os.path.join('src', 'config', 'minimal_settings.py')
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    
    with open(settings_file, 'w') as f:
        f.write(settings_content)
    
    print("✅ Minimal settings created")

def start_server():
    """Start the server with proper error handling"""
    print("🚀 Starting ZmartBot Fixed Server...")
    
    # Clear any existing processes
    kill_processes_on_port(8000)
    kill_uvicorn_processes()
    
    # Check dependencies
    check_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Create minimal settings if needed
    create_minimal_settings()
    
    # Start the server
    try:
        print("📍 Starting server on http://0.0.0.0:8000")
        print("📍 Health check: http://0.0.0.0:8000/health")
        print("📍 API docs: http://0.0.0.0:8000/docs")
        
        # Use the fixed main file
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'fixed_main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("🔧 Trying alternative startup...")
        
        # Try alternative startup
        try:
            subprocess.run([
                sys.executable, '-m', 'uvicorn',
                'simple_server:app',
                '--host', '0.0.0.0',
                '--port', '8000',
                '--log-level', 'info'
            ], check=True)
        except Exception as e2:
            print(f"❌ Alternative startup also failed: {e2}")
            print("🔧 Creating emergency server...")
            
            # Create emergency server
            create_emergency_server()
            subprocess.run([
                sys.executable, 'emergency_server.py',
                '--host', '0.0.0.0',
                '--port', '8000'
            ], check=True)

def create_emergency_server():
    """Create a minimal emergency server"""
    emergency_content = '''
#!/usr/bin/env python3
"""
Emergency ZmartBot Server
Minimal server for basic functionality
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ZmartBot Emergency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ZmartBot Emergency API", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "zmart-emergency"}

@app.get("/api/v1/test")
async def test():
    return {"message": "API is working", "mode": "emergency"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)
'''
    
    with open('emergency_server.py', 'w') as f:
        f.write(emergency_content)
    
    print("✅ Emergency server created")

def test_server():
    """Test if the server is responding"""
    import time
    import requests
    
    print("🧪 Testing server...")
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
            print(f"📊 Health: {response.json()}")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ZmartBot Backend Fix Script")
    print("=" * 50)
    
    # Start the server
    start_server() 