#!/usr/bin/env python3
"""
Test script to verify ZmartBot server is working
"""
import requests
import time
import sys

def test_server():
    """Test if the server is running and responding"""
    print("🔍 Testing ZmartBot server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server on port 8000")
        print("💡 Make sure the server is running with:")
        print("   cd backend/zmart-api && source venv/bin/activate && PYTHONPATH=src uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_frontend():
    """Test if the frontend is accessible"""
    print("\n🔍 Testing frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
            return True
        else:
            print(f"⚠️ Frontend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Frontend not accessible on port 3000")
        print("💡 Start frontend with:")
        print("   cd frontend/zmart-dashboard && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ZmartBot Server Test")
    print("=" * 30)
    
    # Test server
    server_ok = test_server()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 30)
    print("📋 TEST RESULTS")
    print("=" * 30)
    
    if server_ok:
        print("✅ Backend Server: Working")
        print("   📍 API: http://localhost:8000")
        print("   📚 Docs: http://localhost:8000/docs")
    else:
        print("❌ Backend Server: Not working")
    
    if frontend_ok:
        print("✅ Frontend: Working")
        print("   🎨 UI: http://localhost:3000")
        print("   🔐 Login: http://localhost:3000/login")
    else:
        print("❌ Frontend: Not working")
    
    if server_ok and frontend_ok:
        print("\n🎯 ZmartBot Trading Platform is ready!")
        print("\n🔗 Access Points:")
        print("   📊 API: http://localhost:8000")
        print("   🎨 Frontend: http://localhost:3000")
        print("   📚 Documentation: http://localhost:8000/docs")
        print("   🔐 Login: http://localhost:3000/login")
    else:
        print("\n⚠️ Some components need attention")
        sys.exit(1)

if __name__ == "__main__":
    main() 