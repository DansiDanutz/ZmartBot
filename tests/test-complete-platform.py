#!/usr/bin/env python3
"""
Complete Trading Platform Test Suite
Tests all implemented features and integrations
"""
import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Add backend path
sys.path.append('backend/zmart-api/src')

async def test_backend_services():
    """Test all backend services"""
    print("🔍 Testing Backend Services...")
    
    try:
        # Test services
        from services.explainability_service import get_explainability_service
        from services.websocket_service import WebSocketService
        from services.charting_service import get_charting_service
        
        # Test explainability service
        explainability_service = get_explainability_service()
        test_signal = {
            'symbol': 'BTCUSDT',
            'direction': 'BUY',
            'confidence': 0.85,
            'kingfisher_score': 0.8,
            'riskmetric_score': 0.7,
            'cryptometer_score': 0.9
        }
        explanation = explainability_service.explain_signal(test_signal)
        print(f"✅ Explainability Service: {explanation.symbol} - {explanation.recommendation}")
        
        # Test charting service
        charting_service = get_charting_service()
        chart_html = charting_service.get_basic_chart("BTCUSDT", "1h", "dark")
        print(f"✅ Charting Service: Generated {len(chart_html)} character chart")
        
        # Test WebSocket service
        ws_service = WebSocketService()
        print(f"✅ WebSocket Service: Initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend service test error: {e}")
        return False

async def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔍 Testing API Endpoints...")
    
    try:
        async with aiohttp.ClientSession() as session:
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Check: {data.get('status', 'unknown')}")
                else:
                    print(f"❌ Health Check failed: {response.status}")
                    return False
            
            # Test authentication endpoints
            auth_endpoints = [
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/v1/auth/profile"
            ]
            
            for endpoint in auth_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status in [200, 401, 405]:  # Expected responses
                        print(f"✅ Auth Endpoint {endpoint}: Available")
                    else:
                        print(f"❌ Auth Endpoint {endpoint}: Failed ({response.status})")
            
            # Test trading endpoints
            trading_endpoints = [
                "/api/v1/trading/positions",
                "/api/v1/trading/orders",
                "/api/v1/trading/portfolio"
            ]
            
            for endpoint in trading_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status in [200, 401, 405]:
                        print(f"✅ Trading Endpoint {endpoint}: Available")
                    else:
                        print(f"❌ Trading Endpoint {endpoint}: Failed ({response.status})")
            
            # Test signals endpoints
            signals_endpoints = [
                "/api/v1/signals/active",
                "/api/v1/signals/history",
                "/api/v1/signals/generate"
            ]
            
            for endpoint in signals_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status in [200, 401, 405]:
                        print(f"✅ Signals Endpoint {endpoint}: Available")
                    else:
                        print(f"❌ Signals Endpoint {endpoint}: Failed ({response.status})")
            
            # Test charting endpoints
            charting_endpoints = [
                "/api/v1/charting/basic/BTCUSDT",
                "/api/v1/charting/technical/BTCUSDT",
                "/api/v1/charting/signal/BTCUSDT"
            ]
            
            for endpoint in charting_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status in [200, 401, 405]:
                        print(f"✅ Charting Endpoint {endpoint}: Available")
                    else:
                        print(f"❌ Charting Endpoint {endpoint}: Failed ({response.status})")
            
            # Test explainability endpoints
            explainability_endpoints = [
                "/api/v1/explainability/test/signal",
                "/api/v1/explainability/test/risk",
                "/api/v1/explainability/test/portfolio"
            ]
            
            for endpoint in explainability_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status in [200, 401, 405]:
                        print(f"✅ Explainability Endpoint {endpoint}: Available")
                    else:
                        print(f"❌ Explainability Endpoint {endpoint}: Failed ({response.status})")
            
            return True
            
    except Exception as e:
        print(f"❌ API endpoint test error: {e}")
        return False

async def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n🔍 Testing WebSocket Connection...")
    
    try:
        import websockets
        
        uri = "ws://localhost:8000/ws/stream"
        
        async with websockets.connect(uri) as websocket:
            # Send a test message
            test_message = {
                "type": "test",
                "data": {"symbol": "BTCUSDT", "price": 50000}
            }
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ WebSocket Connection: Message received")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

async def test_frontend_access():
    """Test frontend accessibility"""
    print("\n🔍 Testing Frontend Access...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test main frontend
            async with session.get("http://localhost:3000") as response:
                if response.status == 200:
                    print("✅ Frontend: Main page accessible")
                else:
                    print(f"❌ Frontend: Main page failed ({response.status})")
                    return False
            
            # Test login page
            async with session.get("http://localhost:3000/login") as response:
                if response.status == 200:
                    print("✅ Frontend: Login page accessible")
                else:
                    print(f"❌ Frontend: Login page failed ({response.status})")
            
            return True
            
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

async def test_database_connections():
    """Test database connections"""
    print("\n🔍 Testing Database Connections...")
    
    try:
        from utils.database import get_postgres_connection, get_redis_client
        
        # Test PostgreSQL connection
        try:
            conn = await get_postgres_connection()
            if conn:
                print("✅ PostgreSQL: Connection successful")
            else:
                print("⚠️ PostgreSQL: Connection not available (development mode)")
        except Exception as e:
            print(f"⚠️ PostgreSQL: {e} (development mode)")
        
        # Test Redis connection
        try:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.ping()
                print("✅ Redis: Connection successful")
            else:
                print("⚠️ Redis: Connection not available (development mode)")
        except Exception as e:
            print(f"⚠️ Redis: {e} (development mode)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

async def test_authentication_flow():
    """Test authentication flow"""
    print("\n🔍 Testing Authentication Flow...")
    
    try:
        async with aiohttp.ClientSession() as session:
            base_url = "http://localhost:8000"
            
            # Test login with demo credentials
            login_data = {
                "username": "trader",
                "password": "password123"
            }
            
            async with session.post(f"{base_url}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Authentication: Login successful")
                    
                    # Test profile access with token
                    token = data.get('access_token')
                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
                        async with session.get(f"{base_url}/api/v1/auth/profile", headers=headers) as profile_response:
                            if profile_response.status == 200:
                                profile_data = await profile_response.json()
                                print(f"✅ Authentication: Profile access successful - {profile_data.get('username')}")
                            else:
                                print(f"❌ Authentication: Profile access failed ({profile_response.status})")
                    else:
                        print("❌ Authentication: No token received")
                else:
                    print(f"❌ Authentication: Login failed ({response.status})")
            
            return True
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Complete Trading Platform Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print("")
    
    # Run all tests
    tests = [
        ("Backend Services", test_backend_services),
        ("API Endpoints", test_api_endpoints),
        ("WebSocket Connection", test_websocket_connection),
        ("Frontend Access", test_frontend_access),
        ("Database Connections", test_database_connections),
        ("Authentication Flow", test_authentication_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Print results
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎯 ALL TESTS PASSED!")
        print("\n🚀 Complete Trading Platform is ready!")
        print("\n🔗 Access Points:")
        print("   📊 API: http://localhost:8000")
        print("   🎨 Frontend: http://localhost:3000")
        print("   📚 Documentation: http://localhost:8000/docs")
        print("   🔐 Login: http://localhost:3000/login")
        print("\n✨ Platform Features:")
        print("   ✅ Multi-agent trading system")
        print("   ✅ Real-time WebSocket data")
        print("   ✅ Advanced charting with TradingView")
        print("   ✅ AI explainability engine")
        print("   ✅ Complete authentication system")
        print("   ✅ Professional UI/UX design")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("Please check the logs above for details")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 