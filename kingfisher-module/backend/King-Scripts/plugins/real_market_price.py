#!/usr/bin/env python3
"""
Real Market Price Plugin for STEP-5
Fetches real-time market prices from multiple sources
"""

import logging
import requests
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import concurrent.futures

# Import the base plugin class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from step5_runner import BasePlugin, ProcessingContext

logger = logging.getLogger(__name__)

class RealMarketPricePlugin(BasePlugin):
    """Plugin for fetching real-time market prices from multiple sources"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.price_sources = config.get("price_sources", ["binance", "kucoin"])
        self.timeout = config.get("timeout", 30)
        self.retry_count = config.get("retry_count", 3)
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required symbol"""
        if not context.symbol:
            logger.error("Symbol is required for RealMarketPricePlugin")
            return False
        return True
    
    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Execute real market price fetching logic"""
        logger.info(f"💰 Fetching real market prices for: {context.symbol}")
        
        # Fetch prices from multiple sources concurrently
        price_data = self._fetch_prices_concurrent(context.symbol)
        
        # Process and validate price data
        processed_prices = self._process_price_data(price_data, context.symbol)
        
        # Calculate aggregated price metrics
        price_summary = self._calculate_price_summary(processed_prices)
        
        # Update context with price data
        context.market_data.update({
            "real_time_prices": processed_prices,
            "price_summary": price_summary,
            "price_fetch_timestamp": datetime.now().isoformat(),
            "sources_used": list(processed_prices.keys())
        })
        
        # Add to analysis data
        context.analysis_data["real_market_price"] = {
            "symbol": context.symbol,
            "sources_successful": len(processed_prices),
            "sources_failed": len(self.price_sources) - len(processed_prices),
            "primary_price": price_summary.get("average_price", 0),
            "price_spread": price_summary.get("price_spread", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Price fetching completed: {len(processed_prices)}/{len(self.price_sources)} sources successful")
        return context
    
    def _fetch_prices_concurrent(self, symbol: str) -> Dict[str, Dict[str, Any]]:
        """Fetch prices from multiple sources concurrently"""
        price_data = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.price_sources)) as executor:
            # Submit all price fetching tasks
            future_to_source = {
                executor.submit(self._fetch_from_source, source, symbol): source
                for source in self.price_sources
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_source, timeout=self.timeout):
                source = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        price_data[source] = result
                        logger.info(f"✅ Price from {source}: ${result.get('price', 0)}")
                    else:
                        logger.warning(f"❌ No price data from {source}")
                except Exception as e:
                    logger.error(f"❌ Error fetching price from {source}: {e}")
        
        return price_data
    
    def _fetch_from_source(self, source: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price from a specific source with retries"""
        for attempt in range(self.retry_count):
            try:
                if source == "binance":
                    return self._fetch_binance_price(symbol)
                elif source == "kucoin":
                    return self._fetch_kucoin_price(symbol)
                else:
                    logger.warning(f"Unknown price source: {source}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.retry_count} failed for {source}: {e}")
                if attempt == self.retry_count - 1:
                    return None
                
        return None
    
    def _fetch_binance_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price from Binance API"""
        try:
            # Use 24hr ticker for comprehensive data
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "source": "binance",
                "price": float(data["lastPrice"]),
                "volume_24h": float(data["volume"]),
                "price_change_24h": float(data["priceChange"]),
                "price_change_percent_24h": float(data["priceChangePercent"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
                "timestamp": datetime.now().isoformat(),
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None
    
    def _fetch_kucoin_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price from KuCoin API"""
        try:
            # Convert symbol format for KuCoin (e.g., BTCUSDT -> BTC-USDT)
            kucoin_symbol = symbol.replace('USDT', '-USDT').replace('USD', '-USD')
            if not ('-' in kucoin_symbol):
                # Fallback format
                kucoin_symbol = symbol[:-4] + '-' + symbol[-4:]
            
            # Get 24hr stats
            url = f"https://api.kucoin.com/api/v1/market/stats?symbol={kucoin_symbol}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == "200000" and result.get("data"):
                data = result["data"]
                
                return {
                    "source": "kucoin",
                    "price": float(data["last"]),
                    "volume_24h": float(data["vol"]),
                    "price_change_24h": float(data["changePrice"]),
                    "price_change_percent_24h": float(data["changeRate"]) * 100,
                    "high_24h": float(data["high"]),
                    "low_24h": float(data["low"]),
                    "timestamp": datetime.now().isoformat(),
                    "raw_data": data
                }
            else:
                logger.error(f"KuCoin API returned error: {result}")
                return None
            
        except Exception as e:
            logger.error(f"KuCoin API error for {symbol}: {e}")
            return None
    
    def _process_price_data(self, price_data: Dict[str, Dict[str, Any]], symbol: str) -> Dict[str, Dict[str, Any]]:
        """Process and validate price data from all sources"""
        processed = {}
        
        for source, data in price_data.items():
            try:
                # Validate price data
                price = data.get("price", 0)
                if price <= 0:
                    logger.warning(f"Invalid price from {source}: {price}")
                    continue
                
                # Add processing metadata
                processed_data = data.copy()
                processed_data.update({
                    "processing_timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "valid": True
                })
                
                processed[source] = processed_data
                
            except Exception as e:
                logger.error(f"Error processing price data from {source}: {e}")
        
        return processed
    
    def _calculate_price_summary(self, processed_prices: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregated price metrics across sources"""
        if not processed_prices:
            return {}
        
        try:
            prices = [data["price"] for data in processed_prices.values()]
            volumes = [data.get("volume_24h", 0) for data in processed_prices.values()]
            changes_24h = [data.get("price_change_percent_24h", 0) for data in processed_prices.values()]
            
            summary = {
                "average_price": round(sum(prices) / len(prices), 6),
                "min_price": min(prices),
                "max_price": max(prices),
                "price_spread": round(max(prices) - min(prices), 6),
                "price_spread_percent": round(((max(prices) - min(prices)) / min(prices)) * 100, 4) if min(prices) > 0 else 0,
                "average_volume_24h": round(sum(volumes) / len(volumes), 2) if volumes else 0,
                "average_change_24h": round(sum(changes_24h) / len(changes_24h), 4) if changes_24h else 0,
                "sources_count": len(processed_prices),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            # Determine primary price (use Binance if available, otherwise average)
            if "binance" in processed_prices:
                summary["primary_price"] = processed_prices["binance"]["price"]
                summary["primary_source"] = "binance"
            else:
                summary["primary_price"] = summary["average_price"]
                summary["primary_source"] = "average"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating price summary: {e}")
            return {}