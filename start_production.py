#!/usr/bin/env python3
"""
ZmartBot Production Starter
Quick production deployment without Docker
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    # Check if venv exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Check .env.production
    if not Path(".env.production").exists():
        print("❌ .env.production file not found")
        return False
    
    print("✅ Requirements met")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Activate venv and install
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    subprocess.run([pip_path, "install", "-r", "requirements.txt", "-q"])
    print("✅ Dependencies installed")

def start_services():
    """Start the production services"""
    print("🚀 Starting ZmartBot services...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(".env.production")
    
    # Start FastAPI with uvicorn
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    # Change to the correct directory structure
    os.chdir("backend/zmart-api") if Path("backend/zmart-api").exists() else None
    
    print("\n" + "="*50)
    print("🎉 ZmartBot is starting!")
    print("="*50)
    print("\nServices will be available at:")
    print("  📊 API: http://localhost:8000")
    print("  📚 Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("="*50 + "\n")
    
    try:
        # Start the server
        subprocess.run([
            python_path, "-m", "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "2",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down ZmartBot...")

def main():
    """Main entry point"""
    print("🤖 ZmartBot Production Starter")
    print("="*50)
    
    if not check_requirements():
        print("❌ Requirements check failed")
        sys.exit(1)
    
    install_dependencies()
    start_services()

if __name__ == "__main__":
    main()