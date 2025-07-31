#!/usr/bin/env python3
"""
Comprehensive KuCoin API Access Test
Tests all major API endpoints and permissions to verify full access
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import uuid
from urllib.parse import urlencode

class KuCoinFullAccessTester:
    def __init__(self, api_key, api_secret, passphrase, broker_name, partner, broker_key):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.broker_name = broker_name
        self.partner = partner
        self.broker_key = broker_key
        
        # API endpoints
        self.spot_base_url = "https://api.kucoin.com"
        self.futures_base_url = "https://api-futures.kucoin.com"
        self.margin_base_url = "https://api.kucoin.com"
        
        self.test_results = {}
    
    def _generate_signature(self, timestamp, method, endpoint, body="", secret=None):
        """Generate signature for authentication"""
        if secret is None:
            secret = self.api_secret
        message = timestamp + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(
                secret.encode('utf-8'),
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
    
    def _make_request(self, base_url, method, endpoint, params=None, data=None, include_broker=True):
        """Make authenticated request"""
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
        
        # Prepare headers
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }
        
        # Add broker headers if requested
        if include_broker:
            broker_signature = self._generate_broker_signature(timestamp, self.api_key)
            headers.update({
                "KC-API-PARTNER": self.partner,
                "KC-API-PARTNER-SIGN": broker_signature,
                "KC-BROKER-NAME": self.broker_name,
                "KC-API-PARTNER-VERIFY": "true"
            })
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=15)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=body, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            return None
    
    def test_spot_trading_access(self):
        """Test spot trading API access"""
        print("\n🔍 Testing Spot Trading Access...")
        
        tests = [
            ("Account Info", "GET", "/api/v1/accounts"),
            ("Sub Accounts", "GET", "/api/v1/sub/user"),
            ("Deposit Addresses", "GET", "/api/v1/deposit-addresses"),
            ("Withdrawals", "GET", "/api/v1/withdrawals"),
            ("Orders", "GET", "/api/v1/orders"),
            ("Fills", "GET", "/api/v1/fills"),
            ("Stop Orders", "GET", "/api/v1/stop-order"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Spot Trading"] = results
        return results
    
    def test_futures_trading_access(self):
        """Test futures trading API access"""
        print("\n🔍 Testing Futures Trading Access...")
        
        tests = [
            ("Account Overview", "GET", "/api/v1/account-overview"),
            ("Positions", "GET", "/api/v1/positions"),
            ("Orders", "GET", "/api/v1/orders"),
            ("Fills", "GET", "/api/v1/fills"),
            ("Funding History", "GET", "/api/v1/funding-history"),
            ("Contracts", "GET", "/api/v1/contracts/active"),
            ("Risk Limit", "GET", "/api/v1/contracts/risk-limit/XBTUSDTM"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.futures_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Futures Trading"] = results
        return results
    
    def test_margin_trading_access(self):
        """Test margin trading API access"""
        print("\n🔍 Testing Margin Trading Access...")
        
        tests = [
            ("Margin Account", "GET", "/api/v1/margin/account"),
            ("Margin Config", "GET", "/api/v1/margin/config"),
            ("Isolated Margin Account", "GET", "/api/v1/isolated/accounts"),
            ("Cross Margin Account", "GET", "/api/v3/margin/accounts"),
            ("Margin Orders", "GET", "/api/v1/margin/orders"),
            ("Margin Fills", "GET", "/api/v1/margin/fills"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Margin Trading"] = results
        return results
    
    def test_earn_access(self):
        """Test KuCoin Earn API access"""
        print("\n🔍 Testing KuCoin Earn Access...")
        
        tests = [
            ("Savings Products", "GET", "/api/v1/earn/saving/products"),
            ("Fixed Income Products", "GET", "/api/v1/earn/fixed-income/products"),
            ("Promotion Products", "GET", "/api/v1/earn/promotion/products"),
            ("KCS Staking", "GET", "/api/v1/earn/kcs-staking/products"),
            ("ETH Staking", "GET", "/api/v1/earn/eth-staking/products"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["KuCoin Earn"] = results
        return results
    
    def test_vip_lending_access(self):
        """Test VIP Lending API access"""
        print("\n🔍 Testing VIP Lending Access...")
        
        tests = [
            ("Lending Markets", "GET", "/api/v1/margin/lend/assets"),
            ("Lending Orders", "GET", "/api/v1/margin/lend/orders"),
            ("Lending History", "GET", "/api/v1/margin/lend/trade/settled"),
            ("Lending Account", "GET", "/api/v1/margin/lend/accounts"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["VIP Lending"] = results
        return results
    
    def test_affiliate_access(self):
        """Test Affiliate API access"""
        print("\n🔍 Testing Affiliate Access...")
        
        tests = [
            ("Affiliate Info", "GET", "/api/v2/affiliate/inviter/statistics"),
            ("Referral Statistics", "GET", "/api/v1/affiliate/invitee/statistics"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Affiliate"] = results
        return results
    
    def test_broker_access(self):
        """Test Broker API access"""
        print("\n🔍 Testing Broker API Access...")
        
        # Test with broker-specific endpoints
        broker_base_url = "https://api-broker.kucoin.com"
        
        tests = [
            ("Broker Info", "GET", "/api/v1/broker/nd/info"),
            ("Sub Accounts", "GET", "/api/v1/broker/nd/account/list"),
            ("Transfer History", "GET", "/api/v1/broker/nd/transfer/history"),
            ("Rebate Info", "GET", "/api/v1/broker/nd/rebate"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(broker_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Broker API"] = results
        return results
    
    def test_websocket_access(self):
        """Test WebSocket API access"""
        print("\n🔍 Testing WebSocket Access...")
        
        # Test getting WebSocket tokens
        tests = [
            ("Public Token", "POST", "/api/v1/bullet-public"),
            ("Private Token", "POST", "/api/v1/bullet-private"),
        ]
        
        results = {}
        for test_name, method, endpoint in tests:
            response = self._make_request(self.spot_base_url, method, endpoint)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["WebSocket"] = results
        return results
    
    def test_order_placement_permissions(self):
        """Test order placement permissions (without actually placing orders)"""
        print("\n🔍 Testing Order Placement Permissions...")
        
        # Test order validation endpoints
        tests = [
            ("Spot Order Test", "POST", "/api/v1/orders/test", self.spot_base_url),
            ("Futures Order Test", "POST", "/api/v1/orders/test", self.futures_base_url),
        ]
        
        results = {}
        for test_name, method, endpoint, base_url in tests:
            # Create minimal test order data
            test_order = {
                "clientOid": str(uuid.uuid4()),
                "side": "buy",
                "symbol": "BTC-USDT" if "Spot" in test_name else "XBTUSDTM",
                "type": "limit",
                "price": "1",  # Very low price to avoid execution
                "size": "0.0001" if "Spot" in test_name else 1
            }
            
            response = self._make_request(base_url, method, endpoint, data=test_order)
            if response and response.status_code == 200:
                results[test_name] = "✅ PASS"
            else:
                status = response.status_code if response else "No Response"
                results[test_name] = f"❌ FAIL ({status})"
        
        self.test_results["Order Placement"] = results
        return results
    
    def run_comprehensive_test(self):
        """Run all tests and generate comprehensive report"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE KUCOIN API ACCESS TEST")
        print("=" * 80)
        print(f"API Key: {self.api_key}")
        print(f"Broker: {self.broker_name}")
        print(f"Partner: {self.partner}")
        print("=" * 80)
        
        # Run all tests
        self.test_spot_trading_access()
        self.test_futures_trading_access()
        self.test_margin_trading_access()
        self.test_earn_access()
        self.test_vip_lending_access()
        self.test_affiliate_access()
        self.test_broker_access()
        self.test_websocket_access()
        self.test_order_placement_permissions()
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ACCESS REPORT")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            print(f"\n📁 {category}:")
            for test_name, result in tests.items():
                print(f"  {result} {test_name}")
                total_tests += 1
                if "✅" in result:
                    passed_tests += 1
        
        print("\n" + "=" * 80)
        print("📈 SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Determine access level
        success_rate = (passed_tests/total_tests)*100
        if success_rate >= 90:
            access_level = "🟢 FULL ACCESS"
        elif success_rate >= 70:
            access_level = "🟡 PARTIAL ACCESS"
        else:
            access_level = "🔴 LIMITED ACCESS"
        
        print(f"Access Level: {access_level}")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        if success_rate >= 90:
            print("✅ Your API keys have excellent access to KuCoin features!")
            print("✅ You can implement comprehensive trading functionality.")
            print("✅ All major trading features are available.")
        elif success_rate >= 70:
            print("⚠️  Your API keys have good access but some features may be limited.")
            print("⚠️  Check failed endpoints for specific permission requirements.")
            print("⚠️  Consider contacting KuCoin support for full access.")
        else:
            print("❌ Your API keys have limited access.")
            print("❌ Many features are not available with current permissions.")
            print("❌ Contact KuCoin support to upgrade your API access.")
        
        return success_rate

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
    tester = KuCoinFullAccessTester(
        API_KEY, API_SECRET, PASSPHRASE, 
        BROKER_NAME, PARTNER, BROKER_KEY
    )
    
    # Run comprehensive test
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()

