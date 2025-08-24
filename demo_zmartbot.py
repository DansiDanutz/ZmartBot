#!/usr/bin/env python3
"""
ZmartBot Platform Demo
Interactive demonstration of the trading platform capabilities
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_health():
    """Check platform health"""
    print_header("Platform Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status'].upper()}")
            print(f"📦 Service: {data['service']}")
            print(f"🔢 Version: {data['version']}")
            print(f"⏰ Uptime: {data['timestamp']:.2f} seconds")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_endpoints():
    """List available API endpoints"""
    print_header("Available API Endpoints")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            endpoints = []
            for path, methods in data['paths'].items():
                for method in methods:
                    endpoints.append(f"{method.upper():6} {path}")
            
            # Show first 20 endpoints
            print("\nKey Trading Endpoints:")
            for endpoint in sorted(endpoints)[:20]:
                print(f"  • {endpoint}")
            
            print(f"\n📊 Total endpoints available: {len(endpoints)}")
            print(f"📚 Full documentation: {BASE_URL}/docs")
        else:
            print("❌ Failed to get endpoints")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_symbol_validation():
    """Test symbol validation"""
    print_header("Symbol Validation Test")
    
    symbols_to_test = ["BTCUSDT", "ETHUSDT", "INVALID123"]
    
    for symbol in symbols_to_test:
        try:
            response = requests.get(
                f"{BASE_URL}/api/futures-symbols/symbol/{symbol}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n📈 {symbol}:")
                print(f"  • KuCoin: {'✅' if data.get('kucoin_tradeable') else '❌'}")
                print(f"  • Binance: {'✅' if data.get('binance_tradeable') else '❌'}")
            else:
                print(f"\n❌ {symbol}: Not a valid futures symbol")
        except Exception as e:
            print(f"\n❌ {symbol}: Error - {e}")

def show_system_info():
    """Show system information"""
    print_header("System Information")
    
    print("\n🤖 Multi-Agent System:")
    print("  • Orchestration Agent: Central coordinator")
    print("  • Scoring Agent: Signal aggregation (30% KingFisher, 70% Cryptometer)")
    print("  • Risk Guard Agent: Position management & circuit breakers")
    print("  • Signal Generator: Technical analysis")
    print("  • Trading Agent: Order execution (Paper mode)")
    
    print("\n💾 Data Storage:")
    print("  • PostgreSQL: Trading data & positions")
    print("  • Redis: Caching & rate limiting")
    print("  • InfluxDB: Time-series market data")
    
    print("\n🔒 Security Features:")
    print("  • JWT authentication")
    print("  • Rate limiting (multi-tier)")
    print("  • Security headers")
    print("  • Input validation")
    
    print("\n📊 Trading Features:")
    print("  • Real-time price monitoring")
    print("  • Technical indicators")
    print("  • AI-powered analysis")
    print("  • Risk management")
    print("  • Position sizing")
    print("  • Paper trading mode")

def demo_workflow():
    """Demonstrate a typical workflow"""
    print_header("Trading Workflow Demo")
    
    print("\n📋 Typical Trading Workflow:")
    print("\n1️⃣ Market Analysis")
    print("   GET /api/real-time/market-overview")
    print("   → Fetches current market conditions")
    
    print("\n2️⃣ Signal Generation")
    print("   GET /api/signal-center/aggregation/{symbol}")
    print("   → Combines signals from multiple sources")
    
    print("\n3️⃣ Risk Assessment")
    print("   POST /api/unified-trading/position/analyze")
    print("   → Evaluates position risk")
    
    print("\n4️⃣ Trade Execution")
    print("   POST /api/unified-trading/trade/execute")
    print("   → Executes trade (paper mode)")
    
    print("\n5️⃣ Position Monitoring")
    print("   GET /api/position-management/positions")
    print("   → Tracks open positions")

def main():
    """Main demo function"""
    print("\n" + "🤖"*20)
    print("\n     ZMARTBOT TRADING PLATFORM DEMO")
    print("\n" + "🤖"*20)
    
    # Run demo sections
    check_health()
    time.sleep(1)
    
    list_endpoints()
    time.sleep(1)
    
    show_system_info()
    time.sleep(1)
    
    demo_workflow()
    
    # Final message
    print_header("Demo Complete")
    print("\n🚀 ZmartBot is running and ready for trading!")
    print(f"\n📚 Explore the API: {BASE_URL}/docs")
    print(f"📊 View metrics: Check production.log")
    print(f"🔧 Configuration: Edit .env.production")
    print(f"\n⚠️  Remember to add your API keys to .env.production")
    print("   - Cryptometer API Key")
    print("   - KuCoin API credentials")
    print("   - OpenAI API Key")
    print("\n" + "🤖"*20)

if __name__ == "__main__":
    main()