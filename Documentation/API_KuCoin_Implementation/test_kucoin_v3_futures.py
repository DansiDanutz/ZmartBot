#!/usr/bin/env python3
"""
KuCoin V3 Futures API Testing Script
Tests the provided API keys and demonstrates futures trading functionality
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import uuid
from urllib.parse import urlencode

class KuCoinFuturesAPI:
    def __init__(self, api_key, api_secret, passphrase, sandbox=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        
        if sandbox:
            self.base_url = "https://api-sandbox-futures.kucoin.com"
        else:
            self.base_url = "https://api-futures.kucoin.com"
    
    def _generate_signature(self, timestamp, method, endpoint, body=""):
        """Generate signature for KuCoin V3 API authentication"""
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
        """Generate encrypted passphrase for V3 API"""
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to KuCoin V3 Futures API"""
        timestamp = str(int(time.time() * 1000))
        
        # Prepare URL and body
        url = self.base_url + endpoint
        if params:
            url += "?" + urlencode(params)
            endpoint += "?" + urlencode(params)
        
        body = ""
        if data:
            body = json.dumps(data)
        
        # Generate signature
        signature = self._generate_signature(timestamp, method, endpoint, body)
        passphrase = self._generate_passphrase()
        
        # Prepare headers for V3 API
        headers = {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",  # V3 uses version 2
            "Content-Type": "application/json"
        }
        
        # Make request
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=body, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def test_connection(self):
        """Test API connection and authentication"""
        print("Testing Futures API connection...")
        response = self._make_request("GET", "/api/v1/timestamp")
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Connection successful! Server time: {data.get('data')}")
            return True
        else:
            print(f"❌ Connection failed! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return False
    
    def get_account_overview(self):
        """Get futures account overview"""
        print("\nGetting futures account overview...")
        response = self._make_request("GET", "/api/v1/account-overview")
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ Account overview retrieved successfully!")
            account_data = data.get('data', {})
            
            print(f"Account Equity: {account_data.get('accountEquity', 'N/A')}")
            print(f"Unrealized PNL: {account_data.get('unrealisedPNL', 'N/A')}")
            print(f"Margin Balance: {account_data.get('marginBalance', 'N/A')}")
            print(f"Position Margin: {account_data.get('positionMargin', 'N/A')}")
            print(f"Order Margin: {account_data.get('orderMargin', 'N/A')}")
            print(f"Available Balance: {account_data.get('availableBalance', 'N/A')}")
            
            return account_data
        else:
            print(f"❌ Failed to get account overview! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        print("\nGetting current positions...")
        response = self._make_request("GET", "/api/v1/positions")
        
        if response and response.status_code == 200:
            data = response.json()
            positions = data.get('data', [])
            print(f"✅ Found {len(positions)} positions")
            
            for position in positions:
                if float(position.get('currentQty', 0)) != 0:
                    print(f"  - {position.get('symbol', 'Unknown')}: {position.get('currentQty', '0')} @ {position.get('avgEntryPrice', 'N/A')}")
                    print(f"    PNL: {position.get('unrealisedPnl', 'N/A')}, ROE: {position.get('unrealisedRoePcnt', 'N/A')}")
            
            return positions
        else:
            print(f"❌ Failed to get positions! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return None
    
    def get_contracts(self):
        """Get available futures contracts"""
        print("\nGetting available futures contracts...")
        response = self._make_request("GET", "/api/v1/contracts/active")
        
        if response and response.status_code == 200:
            data = response.json()
            contracts = data.get('data', [])
            print(f"✅ Found {len(contracts)} active contracts")
            
            # Show first 10 contracts as example
            print("First 10 contracts:")
            for contract in contracts[:10]:
                print(f"  - {contract.get('symbol', 'Unknown')}: {contract.get('baseCurrency', 'Unknown')}/{contract.get('quoteCurrency', 'Unknown')}")
                print(f"    Multiplier: {contract.get('multiplier', 'N/A')}, Max Leverage: {contract.get('maxLeverage', 'N/A')}")
            
            return contracts
        else:
            print(f"❌ Failed to get contracts! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return None
    
    def place_test_order(self, symbol="XBTUSDTM", side="buy", size=1, price=None):
        """Place a test futures order (small size for testing)"""
        print(f"\nPlacing test {side} order for {symbol}...")
        
        # Generate unique client order ID
        client_oid = str(uuid.uuid4())
        
        # Prepare order data
        order_data = {
            "clientOid": client_oid,
            "side": side,
            "symbol": symbol,
            "type": "limit",
            "size": size,
            "leverage": 1,  # Low leverage for testing
            "marginMode": "ISOLATED",
            "timeInForce": "GTC"
        }
        
        # Set a conservative price if not provided
        if price:
            order_data["price"] = str(price)
        else:
            # For testing, use a very low price for buy orders to avoid execution
            if side == "buy":
                order_data["price"] = "10000"  # Very low price for BTC
            else:
                order_data["price"] = "100000"  # Very high price for sell
        
        response = self._make_request("POST", "/api/v1/orders", data=order_data)
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ Test order placed successfully!")
            print(f"Order ID: {data.get('data', {}).get('orderId', 'N/A')}")
            return data.get('data')
        else:
            print(f"❌ Failed to place test order! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return None
    
    def get_orders(self, status="active"):
        """Get order list"""
        print(f"\nGetting {status} orders...")
        params = {"status": status}
        response = self._make_request("GET", "/api/v1/orders", params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('items', [])
            print(f"✅ Found {len(orders)} {status} orders")
            
            for order in orders:
                print(f"  - {order.get('symbol', 'Unknown')}: {order.get('side', 'Unknown')} {order.get('size', 'N/A')} @ {order.get('price', 'N/A')}")
                print(f"    Status: {order.get('status', 'Unknown')}, ID: {order.get('id', 'N/A')}")
            
            return orders
        else:
            print(f"❌ Failed to get orders! Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return None

def main():
    """Main testing function"""
    print("=" * 70)
    print("KuCoin V3 Futures API Testing Script")
    print("=" * 70)
    
    # User's API credentials
    API_KEY = "68888bce1cad950001b6966d"
    API_SECRET = "ba4de6f6-2fb5-4b32-8a4c-12b1f3eb045a"
    PASSPHRASE = "Danutz1981."
    
    # Initialize API client
    api = KuCoinFuturesAPI(API_KEY, API_SECRET, PASSPHRASE, sandbox=False)
    
    # Test connection
    if not api.test_connection():
        print("❌ API connection failed. Please check your credentials.")
        return
    
    # Test account overview
    account = api.get_account_overview()
    
    # Test positions
    positions = api.get_positions()
    
    # Test contracts
    contracts = api.get_contracts()
    
    # Test orders
    orders = api.get_orders()
    
    # Test order placement (with very conservative parameters)
    print("\n" + "⚠️" * 20)
    print("WARNING: The following will place a REAL test order with very conservative parameters!")
    print("The order is designed NOT to execute (very low price), but will use real API calls.")
    print("⚠️" * 20)
    
    user_input = input("\nDo you want to test order placement? (y/N): ").strip().lower()
    if user_input == 'y':
        test_order = api.place_test_order()
        if test_order:
            # Get updated orders to show the new order
            api.get_orders()
    
    print("\n" + "=" * 70)
    print("Testing completed!")
    print("=" * 70)
    
    # Summary
    print("\nSummary:")
    print(f"✅ API Connection: {'Working' if api.test_connection() else 'Failed'}")
    print(f"✅ Account Access: {'Working' if account else 'Failed'}")
    print(f"✅ Positions Access: {'Working' if positions is not None else 'Failed'}")
    print(f"✅ Contracts Access: {'Working' if contracts else 'Failed'}")
    print(f"✅ Orders Access: {'Working' if orders is not None else 'Failed'}")

if __name__ == "__main__":
    main()

