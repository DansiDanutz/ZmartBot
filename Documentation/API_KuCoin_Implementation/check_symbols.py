#!/usr/bin/env python3
"""
Check KuCoin Futures Symbols
Retrieve and analyze actual symbol naming conventions
"""

import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode

class KuCoinSymbolChecker:
    def __init__(self):
        self.api_key = "68888bce1cad950001b6966d"
        self.api_secret = "ba4de6f6-2fb5-4b32-8a4c-12b1f3eb045a"
        self.passphrase = "Danutz1981"
        self.broker_name = "KRYPTOSTACKMASTER"
        self.partner = "KRYPTOSTACK_ND"
        self.broker_key = "0c8b0cb9-58f5-4d0d-9c73-b7bde5110cc1"
        
        self.futures_base_url = "https://api-futures.kucoin.com"
    
    def _generate_signature(self, timestamp, method, endpoint, body=""):
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
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    def _generate_broker_signature(self, timestamp):
        message = timestamp + self.partner + self.api_key
        signature = base64.b64encode(
            hmac.new(
                self.broker_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _make_request(self, method, endpoint, params=None):
        timestamp = str(int(time.time() * 1000))
        
        url = self.futures_base_url + endpoint
        if params:
            url += "?" + urlencode(params)
            endpoint += "?" + urlencode(params)
        
        signature = self._generate_signature(timestamp, method, endpoint)
        passphrase = self._generate_passphrase()
        broker_signature = self._generate_broker_signature(timestamp)
        
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
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200000':
                    return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_all_contracts(self):
        """Get all active futures contracts"""
        return self._make_request("GET", "/api/v1/contracts/active")
    
    def analyze_symbols(self):
        """Analyze symbol naming patterns"""
        print("🔍 Retrieving KuCoin Futures Symbols...")
        
        contracts = self.get_all_contracts()
        if not contracts:
            print("❌ Failed to retrieve contracts")
            return
        
        print(f"✅ Retrieved {len(contracts)} active contracts")
        print("\n" + "="*80)
        print("📊 SYMBOL ANALYSIS")
        print("="*80)
        
        # Group by base currency
        symbol_groups = {}
        popular_coins = ['BTC', 'ETH', 'SOL', 'DOGE', 'XRP', 'ADA', 'DOT', 'LINK', 'UNI', 'AVAX']
        
        for contract in contracts:
            symbol = contract.get('symbol', '')
            base_currency = contract.get('baseCurrency', '')
            quote_currency = contract.get('quoteCurrency', '')
            
            # Look for popular coins
            for coin in popular_coins:
                if coin in symbol or coin in base_currency:
                    if coin not in symbol_groups:
                        symbol_groups[coin] = []
                    symbol_groups[coin].append({
                        'symbol': symbol,
                        'base': base_currency,
                        'quote': quote_currency,
                        'multiplier': contract.get('multiplier'),
                        'max_leverage': contract.get('maxLeverage')
                    })
                    break
        
        # Display popular symbols
        print("\n🎯 POPULAR FUTURES SYMBOLS:")
        for coin in popular_coins:
            if coin in symbol_groups:
                print(f"\n{coin} Futures:")
                for contract in symbol_groups[coin][:3]:  # Show first 3
                    print(f"  📈 {contract['symbol']}")
                    print(f"     Base: {contract['base']} | Quote: {contract['quote']}")
                    print(f"     Multiplier: {contract['multiplier']} | Max Leverage: {contract['max_leverage']}x")
        
        # Show all USDT-margined contracts
        print(f"\n🔸 ALL USDT-MARGINED CONTRACTS (showing first 20):")
        usdt_contracts = [c for c in contracts if 'USDT' in c.get('symbol', '')][:20]
        for i, contract in enumerate(usdt_contracts, 1):
            symbol = contract.get('symbol', '')
            base = contract.get('baseCurrency', '')
            leverage = contract.get('maxLeverage', 'N/A')
            print(f"{i:2d}. {symbol:<20} | Base: {base:<8} | Max Leverage: {leverage}x")
        
        # Show symbol patterns
        print(f"\n🔍 SYMBOL PATTERNS:")
        patterns = {}
        for contract in contracts:
            symbol = contract.get('symbol', '')
            if symbol.endswith('M'):
                suffix = symbol[-6:]  # Last 6 characters
                if suffix not in patterns:
                    patterns[suffix] = []
                patterns[suffix].append(symbol)
        
        for pattern, symbols in patterns.items():
            if len(symbols) >= 5:  # Show patterns with at least 5 symbols
                print(f"  Pattern '{pattern}': {len(symbols)} contracts")
                print(f"    Examples: {', '.join(symbols[:5])}")
        
        # Bitcoin specific analysis
        print(f"\n₿ BITCOIN SYMBOL ANALYSIS:")
        btc_symbols = [c for c in contracts if 'BTC' in c.get('symbol', '') or 'XBT' in c.get('symbol', '') or c.get('baseCurrency') == 'XBT']
        for contract in btc_symbols:
            symbol = contract.get('symbol', '')
            base = contract.get('baseCurrency', '')
            quote = contract.get('quoteCurrency', '')
            print(f"  🟡 {symbol} | Base: {base} | Quote: {quote}")
        
        return contracts

def main():
    checker = KuCoinSymbolChecker()
    contracts = checker.analyze_symbols()
    
    if contracts:
        print(f"\n" + "="*80)
        print("✅ SYMBOL CHECK COMPLETE")
        print(f"Total contracts analyzed: {len(contracts)}")
        print("="*80)

if __name__ == "__main__":
    main()

