#!/usr/bin/env python3
"""
Test script for ZmartBot Backend API
"""
import requests
import time
import sys

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing ZmartBot Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation available")
        else:
            print(f"⚠️  API docs not available: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Cannot access API docs: {e}")
    
    # Test other endpoints
    endpoints = [
        "/api/v1/auth/login",
        "/api/v1/trading/positions",
        "/api/v1/signals",
        "/api/v1/agents"
    ]
    
    print("\n🔍 Testing API endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 404]:  # 401 is expected for auth endpoints
                print(f"✅ {endpoint} - {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Connection failed")
    
    print("\n🎉 Backend API test completed!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1) 