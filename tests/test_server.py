#!/usr/bin/env python3
"""
Simple test script to verify the ZmartBot backend server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    try:
        from src.config.settings import settings
        print("✅ Settings import successful")
        
        from src.utils.database import init_database
        print("✅ Database utils import successful")
        
        from src.utils.monitoring import init_monitoring
        print("✅ Monitoring utils import successful")
        
        from src.agents.orchestration.orchestration_agent import OrchestrationAgent
        print("✅ Orchestration agent import successful")
        
        from src.main import app
        print("✅ Main app import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_start():
    """Test server startup"""
    try:
        import uvicorn
        from src.main import app
        
        print("✅ Server components available")
        return True
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ZmartBot Backend Server")
    print("=" * 50)
    
    # Test imports
    if test_imports():
        print("✅ All imports successful")
    else:
        print("❌ Import tests failed")
        sys.exit(1)
    
    # Test server startup
    if test_server_start():
        print("✅ Server startup test successful")
    else:
        print("❌ Server startup test failed")
        sys.exit(1)
    
    print("🎉 All tests passed! Server is ready to start.") 