#!/usr/bin/env python3
"""
Test script to verify ZmartBot API server startup
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        from src.config.settings import settings
        print("✅ Settings imported successfully")
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False
    
    try:
        from src.utils.database import init_database, close_database
        print("✅ Database utils imported successfully")
    except Exception as e:
        print(f"❌ Database utils import failed: {e}")
        return False
    
    try:
        from src.utils.monitoring import init_monitoring
        print("✅ Monitoring utils imported successfully")
    except Exception as e:
        print(f"❌ Monitoring utils import failed: {e}")
        return False
    
    try:
        from src.agents.orchestration.orchestration_agent import OrchestrationAgent
        print("✅ Orchestration agent imported successfully")
    except Exception as e:
        print(f"❌ Orchestration agent import failed: {e}")
        return False
    
    try:
        from src.routes.analytics import router as analytics_router
        print("✅ Analytics router imported successfully")
    except Exception as e:
        print(f"❌ Analytics router import failed: {e}")
        return False
    
    try:
        from src.services.analytics_service import analytics_service
        print("✅ Analytics service imported successfully")
    except Exception as e:
        print(f"❌ Analytics service import failed: {e}")
        return False
    
    return True

async def test_app_creation():
    """Test FastAPI app creation"""
    print("\nTesting app creation...")
    
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        print(f"   - App title: {app.title}")
        print(f"   - App version: {app.version}")
        print(f"   - App description: {app.description}")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

async def test_routes():
    """Test route registration"""
    print("\nTesting route registration...")
    
    try:
        from main import app
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"✅ Routes registered successfully ({len(routes)} routes)")
        print("   - Available routes:")
        for route in routes[:10]:  # Show first 10 routes
            print(f"     * {route}")
        if len(routes) > 10:
            print(f"     ... and {len(routes) - 10} more")
        
        return True
    except Exception as e:
        print(f"❌ Route registration failed: {e}")
        return False

async def test_health_endpoint():
    """Test health endpoint"""
    print("\nTesting health endpoint...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   - Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

async def test_analytics_endpoints():
    """Test analytics endpoints"""
    print("\nTesting analytics endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test portfolio metrics endpoint
        response = client.get("/api/v1/analytics/portfolio/metrics")
        if response.status_code == 200:
            print("✅ Portfolio metrics endpoint working")
        else:
            print(f"❌ Portfolio metrics endpoint failed: {response.status_code}")
            return False
        
        # Test trade analysis endpoint
        response = client.get("/api/v1/analytics/trades/analysis")
        if response.status_code == 200:
            print("✅ Trade analysis endpoint working")
        else:
            print(f"❌ Trade analysis endpoint failed: {response.status_code}")
            return False
        
        # Test risk analysis endpoint
        response = client.get("/api/v1/analytics/risk/analysis")
        if response.status_code == 200:
            print("✅ Risk analysis endpoint working")
        else:
            print(f"❌ Risk analysis endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Analytics endpoints test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 ZmartBot API Startup Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_imports()
    if not imports_ok:
        print("\n❌ Import tests failed. Cannot proceed.")
        return False
    
    # Test app creation
    app_ok = await test_app_creation()
    if not app_ok:
        print("\n❌ App creation failed. Cannot proceed.")
        return False
    
    # Test routes
    routes_ok = await test_routes()
    if not routes_ok:
        print("\n❌ Route registration failed.")
        return False
    
    # Test health endpoint
    health_ok = await test_health_endpoint()
    if not health_ok:
        print("\n❌ Health endpoint failed.")
        return False
    
    # Test analytics endpoints
    analytics_ok = await test_analytics_endpoints()
    if not analytics_ok:
        print("\n❌ Analytics endpoints failed.")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Server should start successfully.")
    print("🎯 Ready to start server with:")
    print("   cd backend/zmart-api")
    print("   source venv/bin/activate")
    print("   PYTHONPATH=src uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 