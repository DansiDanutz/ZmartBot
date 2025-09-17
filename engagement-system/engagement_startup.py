#!/usr/bin/env python3
"""
Zmarty Engagement Service Startup Script
Launches the engagement service and performs system checks
"""

import asyncio
import aiohttp
import sys
import time
import subprocess
import signal
import json
from datetime import datetime
from typing import Optional

class EngagementServiceManager:
    def __init__(self):
        self.service_process: Optional[subprocess.Popen] = None
        self.service_url = "http://localhost:8350"
        self.running = False

    async def check_service_health(self, max_retries: int = 30) -> bool:
        """Check if the service is healthy"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.service_url}/health", timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Service health check passed: {data.get('status', 'unknown')}")
                            return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⏳ Health check attempt {attempt + 1}/{max_retries} failed, retrying in 2s...")
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Health check failed after {max_retries} attempts: {e}")
                    
        return False

    async def test_mcp_integration(self) -> bool:
        """Test MCP integration functionality"""
        try:
            print("🔍 Testing MCP integration...")
            
            async with aiohttp.ClientSession() as session:
                # Test MCP status
                async with session.get(f"{self.service_url}/mcp-status") as response:
                    if response.status == 200:
                        mcp_data = await response.json()
                        print(f"✅ MCP Status: {mcp_data['status']}")
                        
                        # Display data source statuses
                        for source, info in mcp_data['data_sources'].items():
                            print(f"   • {source}: {info['status']}")
                        
                        # Display sample market data
                        sample = mcp_data.get('sample_data', {})
                        if sample:
                            print(f"📊 Sample Market Data:")
                            print(f"   • Asset: {sample.get('asset', 'N/A')}")
                            print(f"   • Price: ${sample.get('price', 0):,.2f}")
                            print(f"   • Volatility: {sample.get('volatility', 0):.2f}")
                            print(f"   • Sentiment: {sample.get('sentiment', 0):.2f}")
                            print(f"   • Risk Score: {sample.get('risk_score', 0):.2f}")
                        
                        return True
                    else:
                        print(f"❌ MCP status check failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ MCP integration test failed: {e}")
            return False

    async def test_basic_interaction(self) -> bool:
        """Test basic chat interaction"""
        try:
            print("💬 Testing basic interaction...")
            
            async with aiohttp.ClientSession() as session:
                # Create demo user first
                async with session.get(f"{self.service_url}/demo/create-user/test_user") as response:
                    if response.status == 200:
                        print("✅ Demo user created")
                    else:
                        print(f"⚠️  Demo user creation failed: {response.status}")
                
                # Test chat interaction
                chat_request = {
                    "user_id": "test_user",
                    "message": "What do you think about BTC right now?",
                    "asset": "BTC"
                }
                
                async with session.post(
                    f"{self.service_url}/interact",
                    json=chat_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Chat interaction successful")
                        print(f"   • Response Type: {data['response'].get('type', 'unknown')}")
                        print(f"   • Engagement Score: {data['engagement_score']:.2f}")
                        print(f"   • MCP Data Used: {data['response'].get('mcp_data_used', False)}")
                        print(f"   • Premium Tiers: {len(data['response'].get('premium_content', []))}")
                        print(f"   • Market Context: {data['market_context']['asset']} at ${data['market_context']['price']:,.2f}")
                        return True
                    else:
                        error_data = await response.text()
                        print(f"❌ Chat interaction failed: {response.status} - {error_data}")
                        return False
                        
        except Exception as e:
            print(f"❌ Basic interaction test failed: {e}")
            return False

    async def run_comprehensive_tests(self) -> bool:
        """Run comprehensive system tests"""
        print("\n🧪 Running Comprehensive Tests...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.check_service_health),
            ("MCP Integration", self.test_mcp_integration),
            ("Basic Interaction", self.test_basic_interaction),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name}...")
            try:
                if await test_func():
                    print(f"✅ {test_name} PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
        
        print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
        return passed == len(tests)

    def start_service(self):
        """Start the engagement service"""
        try:
            print("🚀 Starting Zmarty Engagement Service...")
            
            # Start the FastAPI service
            self.service_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "engagement_service:app",
                "--host", "0.0.0.0",
                "--port", "8350",
                "--log-level", "info"
            ], cwd="/Users/dansidanutz/Desktop/ZmartBot/engagement-system")
            
            print(f"✅ Service started with PID: {self.service_process.pid}")
            self.running = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return False

    def stop_service(self):
        """Stop the engagement service"""
        if self.service_process:
            print("🛑 Stopping Zmarty Engagement Service...")
            self.service_process.terminate()
            self.service_process.wait(timeout=10)
            print("✅ Service stopped")
            self.running = False

    def signal_handler(self, sig, frame):
        """Handle interrupt signals"""
        print(f"\n📢 Received signal {sig}")
        self.stop_service()
        sys.exit(0)

async def main():
    """Main startup routine"""
    manager = EngagementServiceManager()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    print("🎯 Zmarty Interactive Engagement System")
    print("=" * 50)
    print("🔧 MCP Integration: KingFisher, Cryptometer, RiskMetric, Grok, X Sentiment, Whale Alerts")
    print("⚡ Service Port: 8350")
    print("📊 Dashboard Integration: Ready")
    print("🤖 AI Personality: Adaptive Trading Mentor")
    print()
    
    try:
        # Start the service
        if not manager.start_service():
            print("❌ Failed to start service")
            return
        
        # Wait for service to be ready
        print("⏳ Waiting for service to initialize...")
        await asyncio.sleep(5)
        
        # Run tests
        if await manager.run_comprehensive_tests():
            print("\n🎉 All tests passed! Zmarty Engagement System is ready!")
            print()
            print("📋 Available Endpoints:")
            print(f"   • Health Check: {manager.service_url}/health")
            print(f"   • Chat Interaction: POST {manager.service_url}/interact")
            print(f"   • User Profile: GET {manager.service_url}/user/{{user_id}}")
            print(f"   • MCP Status: GET {manager.service_url}/mcp-status")
            print(f"   • Analytics: GET {manager.service_url}/analytics")
            print()
            print("🔥 Integration Examples:")
            print(f"   curl -X POST {manager.service_url}/interact \\")
            print('     -H "Content-Type: application/json" \\')
            print('     -d \'{"user_id": "trader123", "message": "What do you see in BTC?", "asset": "BTC"}\'')
            print()
            print("⌨️  Press Ctrl+C to stop the service")
            
            # Keep running until interrupted
            try:
                while manager.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
                
        else:
            print("\n❌ Some tests failed. Check the logs above for details.")
            manager.stop_service()
            
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        manager.stop_service()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)