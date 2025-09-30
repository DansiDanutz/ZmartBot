#!/usr/bin/env python3
"""
KingFisher Real Market Data Service
Connects to real APIs for live market data
"""

import asyncio
import httpx
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealMarketDataService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 30  # 30 seconds cache
        self.last_update = {}
        
        # API configurations
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.kucoin_base_url = "https://api.kucoin.com/api/v1"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # API keys (should be in environment variables)
        self.binance_api_key = os.getenv('BINANCE_API_KEY', '')
        self.kucoin_api_key = os.getenv('KUCOIN_API_KEY', '')
        
    async def get_binance_price(self, symbol: str) -> Optional[float]:
        """Get current price from Binance API"""
        try:
            cache_key = f"binance_{symbol}"
            
            # Check cache
            if cache_key in self.cache:
                last_update = self.last_update.get(cache_key, 0)
                if time.time() - last_update < self.cache_duration:
                    return self.cache[cache_key]
            
            # Fetch from API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.binance_base_url}/ticker/price", params={"symbol": symbol})
                
                if response.status_code == 200:
                    data = response.json()
                    price = float(data['price'])
                    
                    # Update cache
                    self.cache[cache_key] = price
                    self.last_update[cache_key] = time.time()
                    
                    logger.info(f"✅ Binance {symbol}: ${price:,.2f}")
                    return price
                else:
                    logger.error(f"❌ Binance API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error fetching Binance price for {symbol}: {e}")
            return None
    
    async def get_kucoin_price(self, symbol: str) -> Optional[float]:
        """Get current price from KuCoin API"""
        try:
            cache_key = f"kucoin_{symbol}"
            
            # Check cache
            if cache_key in self.cache:
                last_update = self.last_update.get(cache_key, 0)
                if time.time() - last_update < self.cache_duration:
                    return self.cache[cache_key]
            
            # Fetch from API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.kucoin_base_url}/market/orderbook/level1", params={"symbol": symbol})
                
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == '200000':
                        price = float(data['data']['price'])
                        
                        # Update cache
                        self.cache[cache_key] = price
                        self.last_update[cache_key] = time.time()
                        
                        logger.info(f"✅ KuCoin {symbol}: ${price:,.2f}")
                        return price
                    else:
                        logger.error(f"❌ KuCoin API error: {data.get('msg', 'Unknown error')}")
                        return None
                else:
                    logger.error(f"❌ KuCoin API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error fetching KuCoin price for {symbol}: {e}")
            return None
    
    async def get_coingecko_price(self, symbol: str) -> Optional[float]:
        """Get current price from CoinGecko API"""
        try:
            cache_key = f"coingecko_{symbol}"
            
            # Check cache
            if cache_key in self.cache:
                last_update = self.last_update.get(cache_key, 0)
                if time.time() - last_update < self.cache_duration:
                    return self.cache[cache_key]
            
            # Convert symbol to CoinGecko format
            coingecko_id = self.convert_to_coingecko_id(symbol)
            if not coingecko_id:
                return None
            
            # Fetch from API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.coingecko_base_url}/simple/price", params={
                    "ids": coingecko_id,
                    "vs_currencies": "usd"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if coingecko_id in data and 'usd' in data[coingecko_id]:
                        price = float(data[coingecko_id]['usd'])
                        
                        # Update cache
                        self.cache[cache_key] = price
                        self.last_update[cache_key] = time.time()
                        
                        logger.info(f"✅ CoinGecko {symbol}: ${price:,.2f}")
                        return price
                    else:
                        logger.error(f"❌ CoinGecko data not found for {symbol}")
                        return None
                else:
                    logger.error(f"❌ CoinGecko API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error fetching CoinGecko price for {symbol}: {e}")
            return None
    
    def convert_to_coingecko_id(self, symbol: str) -> Optional[str]:
        """Convert trading symbol to CoinGecko ID"""
        # Remove USDT suffix
        base_symbol = symbol.replace('USDT', '').lower()
        
        # Common mappings
        mappings = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'ada': 'cardano',
            'sol': 'solana',
            'xrp': 'ripple',
            'dot': 'polkadot',
            'link': 'chainlink',
            'uni': 'uniswap',
            'ltc': 'litecoin',
            'bch': 'bitcoin-cash',
            'xlm': 'stellar',
            'vet': 'vechain',
            'icp': 'internet-computer',
            'fil': 'filecoin',
            'trx': 'tron',
            'etc': 'ethereum-classic',
            'atom': 'cosmos',
            'neo': 'neo',
            'algo': 'algorand',
            'xmr': 'monero'
        }
        
        return mappings.get(base_symbol)
    
    async def get_best_price(self, symbol: str) -> Optional[float]:
        """Get the best available price from multiple sources"""
        prices = []
        
        # Try Binance first (usually most reliable)
        binance_price = await self.get_binance_price(symbol)
        if binance_price:
            prices.append(('binance', binance_price))
        
        # Try KuCoin
        kucoin_price = await self.get_kucoin_price(symbol)
        if kucoin_price:
            prices.append(('kucoin', kucoin_price))
        
        # Try CoinGecko
        coingecko_price = await self.get_coingecko_price(symbol)
        if coingecko_price:
            prices.append(('coingecko', coingecko_price))
        
        if not prices:
            logger.error(f"❌ No price data available for {symbol}")
            return None
        
        # Return the median price to avoid outliers
        prices.sort(key=lambda x: x[1])
        median_price = prices[len(prices)//2][1]
        
        logger.info(f"📊 Best price for {symbol}: ${median_price:,.2f} (from {len(prices)} sources)")
        return median_price
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for a symbol"""
        try:
            price = await self.get_best_price(symbol)
            if not price:
                return {
                    "symbol": symbol,
                    "price": None,
                    "timestamp": datetime.now().isoformat(),
                    "error": "No price data available"
                }
            
            # Get additional data from Binance
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 24h ticker
                ticker_response = await client.get(f"{self.binance_base_url}/ticker/24hr", params={"symbol": symbol})
                
                ticker_data = {}
                if ticker_response.status_code == 200:
                    ticker_data = ticker_response.json()
                
                # Order book (top 5 levels)
                orderbook_response = await client.get(f"{self.binance_base_url}/depth", params={"symbol": symbol, "limit": 5})
                
                orderbook_data = {}
                if orderbook_response.status_code == 200:
                    orderbook_data = orderbook_response.json()
            
            return {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "24h_change": float(ticker_data.get('priceChangePercent', 0)),
                "24h_volume": float(ticker_data.get('volume', 0)),
                "24h_high": float(ticker_data.get('highPrice', 0)),
                "24h_low": float(ticker_data.get('lowPrice', 0)),
                "bid_price": float(orderbook_data.get('bids', [[0]])[0][0]) if orderbook_data.get('bids') else price,
                "ask_price": float(orderbook_data.get('asks', [[0]])[0][0]) if orderbook_data.get('asks') else price,
                "spread": float(orderbook_data.get('asks', [[0]])[0][0]) - float(orderbook_data.get('bids', [[0]])[0][0]) if orderbook_data.get('asks') and orderbook_data.get('bids') else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting market data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "price": None,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

async def main():
    """Test the market data service"""
    service = RealMarketDataService()
    
    # Test symbols
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
    
    print("🧪 Testing Real Market Data Service...")
    print("="*50)
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}:")
        
        # Get best price
        price = await service.get_best_price(symbol)
        if price:
            print(f"   💰 Price: ${price:,.2f}")
        
        # Get comprehensive data
        market_data = await service.get_market_data(symbol)
        if market_data.get('price'):
            print(f"   📈 24h Change: {market_data['24h_change']:.2f}%")
            print(f"   📊 Volume: {market_data['24h_volume']:,.0f}")
            print(f"   🔺 High: ${market_data['24h_high']:,.2f}")
            print(f"   🔻 Low: ${market_data['24h_low']:,.2f}")
        else:
            print(f"   ❌ Error: {market_data.get('error', 'Unknown error')}")
    
    print("\n✅ Market data service test complete!")

if __name__ == "__main__":
    asyncio.run(main()) 