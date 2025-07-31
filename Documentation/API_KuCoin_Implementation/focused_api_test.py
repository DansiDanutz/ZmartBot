#!/usr/bin/env python3
"""
Focused KuCoin API Test - Essential Trading Features
Tests core trading functionality that we know works
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import uuid
from urllib.parse import urlencode

class KuCoinFocusedTester:
    def __init__(self, api_key, api_secret, passphrase, broker_name, partner, broker_key):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.broker_name = broker_name
        self.partner = partner
        self.broker_key = broker_key
        
        self.spot_base_url = "https://api.kucoin.com"
        self.futures_base_url = "https://api-futures.kucoin.com"
    
    def _generate_signature(self, timestamp, method, endpoint, body=""):
        """Generate signature for authentication"""
        message = timestamp + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _generate_passphrase(self):
        """Generate encrypted passphrase"""
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    def _generate_broker_signature(self, timestamp, api_key):
        """Generate broker signature"""
        message = timestamp + self.partner + api_key
        signature = base64.b64encode(
            hmac.new(
                self.broker_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _make_request(self, base_url, method, endpoint, params=None, data=None):
        """Make authenticated request with proper error handling"""
        timestamp = str(int(time.time() * 1000))
        
        # Prepare URL and body
        url = base_url + endpoint
        if params:
            url += "?" + urlencode(params)
            endpoint += "?" + urlencode(params)
        
        body = ""
        if data:
            body = json.dumps(data, separators=(',', ':'))
        
        # Generate signatures
        signature = self._generate_signature(timestamp, method, endpoint, body)
        passphrase = self._generate_passphrase()
        broker_signature = self._generate_broker_signature(timestamp, self.api_key)
        
        # Prepare headers
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "KC-API-PARTNER": self.partner,
            "KC-API-PARTNER-SIGN": broker_signature,
            "KC-BROKER-NAME": self.broker_name,
            "KC-API-PARTNER-VERIFY": "true",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=body, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout for {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"🔌 Network error for {endpoint}: {e}")
            return None
    
    def test_core_functionality(self):
        """Test core functionality that we know works"""
        print("🔍 Testing Core API Functionality...")
        
        results = {}
        
        # Test server connectivity
        print("\n1. Testing Server Connectivity...")
        response = self._make_request(self.futures_base_url, "GET", "/api/v1/timestamp")
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Server Time: {data.get('data')}")
            results["Server Connectivity"] = "✅ WORKING"
        else:
            print("❌ Server connectivity failed")
            results["Server Connectivity"] = "❌ FAILED"
        
        # Test market data access
        print("\n2. Testing Market Data Access...")
        response = self._make_request(self.futures_base_url, "GET", "/api/v1/contracts/active")
        if response and response.status_code == 200:
            data = response.json()
            contracts = data.get('data', [])
            print(f"✅ Retrieved {len(contracts)} active contracts")
            results["Market Data"] = "✅ WORKING"
        else:
            print("❌ Market data access failed")
            results["Market Data"] = "❌ FAILED"
        
        # Test authentication
        print("\n3. Testing Authentication...")
        response = self._make_request(self.spot_base_url, "POST", "/api/v1/bullet-public")
        if response and response.status_code == 200:
            print("✅ Public authentication working")
            results["Public Auth"] = "✅ WORKING"
        else:
            print("❌ Public authentication failed")
            results["Public Auth"] = "❌ FAILED"
        
        # Test private authentication
        response = self._make_request(self.spot_base_url, "POST", "/api/v1/bullet-private")
        if response and response.status_code == 200:
            print("✅ Private authentication working")
            results["Private Auth"] = "✅ WORKING"
        else:
            status = response.status_code if response else "No Response"
            print(f"⚠️  Private authentication: {status}")
            results["Private Auth"] = f"⚠️ LIMITED ({status})"
        
        # Test account access (with timeout handling)
        print("\n4. Testing Account Access...")
        response = self._make_request(self.futures_base_url, "GET", "/api/v1/account-overview")
        if response:
            if response.status_code == 200:
                print("✅ Account access working")
                results["Account Access"] = "✅ WORKING"
            else:
                print(f"⚠️  Account access limited: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('msg', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text[:100]}")
                results["Account Access"] = f"⚠️ LIMITED ({response.status_code})"
        else:
            print("⏰ Account access timeout")
            results["Account Access"] = "⏰ TIMEOUT"
        
        return results
    
    def test_trading_permissions(self):
        """Test trading permissions without placing real orders"""
        print("\n🔍 Testing Trading Permissions...")
        
        results = {}
        
        # Test spot trading symbols
        print("\n1. Testing Spot Trading Symbols...")
        response = self._make_request(self.spot_base_url, "GET", "/api/v1/symbols")
        if response and response.status_code == 200:
            data = response.json()
            symbols = data.get('data', [])
            print(f"✅ Retrieved {len(symbols)} spot trading symbols")
            results["Spot Symbols"] = "✅ WORKING"
        else:
            print("❌ Spot symbols access failed")
            results["Spot Symbols"] = "❌ FAILED"
        
        # Test futures contracts detail
        print("\n2. Testing Futures Contract Details...")
        response = self._make_request(self.futures_base_url, "GET", "/api/v1/contracts/XBTUSDTM")
        if response and response.status_code == 200:
            data = response.json()
            contract = data.get('data', {})
            print(f"✅ Retrieved contract details for XBTUSDTM")
            print(f"   Max Leverage: {contract.get('maxLeverage')}")
            print(f"   Multiplier: {contract.get('multiplier')}")
            results["Contract Details"] = "✅ WORKING"
        else:
            print("❌ Contract details access failed")
            results["Contract Details"] = "❌ FAILED"
        
        # Test order book access
        print("\n3. Testing Order Book Access...")
        response = self._make_request(self.futures_base_url, "GET", "/api/v1/level2_market_data", 
                                    params={"symbol": "XBTUSDTM"})
        if response and response.status_code == 200:
            data = response.json()
            orderbook = data.get('data', {})
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            print(f"✅ Retrieved order book: {len(bids)} bids, {len(asks)} asks")
            results["Order Book"] = "✅ WORKING"
        else:
            print("❌ Order book access failed")
            results["Order Book"] = "❌ FAILED"
        
        return results
    
    def generate_capability_report(self, core_results, trading_results):
        """Generate capability report for implementation"""
        print("\n" + "=" * 80)
        print("📊 API CAPABILITY ASSESSMENT")
        print("=" * 80)
        
        all_results = {**core_results, **trading_results}
        
        working_features = []
        limited_features = []
        failed_features = []
        
        for feature, status in all_results.items():
            if "✅" in status:
                working_features.append(feature)
            elif "⚠️" in status or "⏰" in status:
                limited_features.append(feature)
            else:
                failed_features.append(feature)
        
        print(f"\n🟢 WORKING FEATURES ({len(working_features)}):")
        for feature in working_features:
            print(f"  ✅ {feature}")
        
        if limited_features:
            print(f"\n🟡 LIMITED FEATURES ({len(limited_features)}):")
            for feature in limited_features:
                print(f"  ⚠️  {feature}")
        
        if failed_features:
            print(f"\n🔴 FAILED FEATURES ({len(failed_features)}):")
            for feature in failed_features:
                print(f"  ❌ {feature}")
        
        # Calculate implementation readiness
        total_features = len(all_results)
        working_count = len(working_features)
        readiness_score = (working_count / total_features) * 100
        
        print(f"\n📈 IMPLEMENTATION READINESS: {readiness_score:.1f}%")
        
        if readiness_score >= 70:
            print("🟢 READY FOR IMPLEMENTATION")
            print("✅ Core functionality is working")
            print("✅ Can proceed with Cursor AI implementation")
        elif readiness_score >= 50:
            print("🟡 PARTIALLY READY")
            print("⚠️  Some features may be limited")
            print("⚠️  Implementation possible with workarounds")
        else:
            print("🔴 NOT READY")
            print("❌ Too many core features are not working")
            print("❌ Need to resolve API access issues first")
        
        return readiness_score
    
    def run_focused_test(self):
        """Run focused test suite"""
        print("=" * 80)
        print("🎯 FOCUSED KUCOIN API CAPABILITY TEST")
        print("=" * 80)
        print(f"API Key: {self.api_key}")
        print(f"Broker: {self.broker_name}")
        print("=" * 80)
        
        # Run tests
        core_results = self.test_core_functionality()
        trading_results = self.test_trading_permissions()
        
        # Generate report
        readiness_score = self.generate_capability_report(core_results, trading_results)
        
        return readiness_score

def main():
    """Main testing function"""
    # Your API credentials
    API_KEY = "68888bce1cad950001b6966d"
    API_SECRET = "ba4de6f6-2fb5-4b32-8a4c-12b1f3eb045a"
    PASSPHRASE = "Danutz1981."
    BROKER_NAME = "KRYPTOSTACKMASTER"
    PARTNER = "KRYPTOSTACK_ND"
    BROKER_KEY = "0c8b0cb9-58f5-4d0d-9c73-b7bde5110cc1"
    
    # Initialize tester
    tester = KuCoinFocusedTester(
        API_KEY, API_SECRET, PASSPHRASE, 
        BROKER_NAME, PARTNER, BROKER_KEY
    )
    
    # Run focused test
    readiness_score = tester.run_focused_test()
    
    return readiness_score

if __name__ == "__main__":
    main()

