"""
Zmart Trading Bot Platform - Binance Service
Binance API integration for trading operations
"""
import asyncio
import logging
import hmac
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout
from pydantic import BaseModel, Field
import json

from src.config.settings import settings
from src.utils.monitoring import record_api_call, record_api_error

logger = logging.getLogger(__name__)

class BinanceMarketData(BaseModel):
    """Binance market data model"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

class BinanceKline(BaseModel):
    """Binance kline/candlestick model"""
    symbol: str
    open_time: datetime
    close_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float
    trades_count: int
    timestamp: datetime

class BinanceService:
    """
    Binance API Service
    Backup service for historical data and price verification
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_calls = []
        self.rate_limit_window = 60  # seconds
        self.max_calls_per_window = 1200  # Binance allows 1200 requests per minute
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ZmartBot/1.0.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _rate_limit_check(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        # Remove old calls outside the window
        self.rate_limit_calls = [call_time for call_time in self.rate_limit_calls 
                               if now - call_time < self.rate_limit_window]
        
        if len(self.rate_limit_calls) >= self.max_calls_per_window:
            return False
        
        self.rate_limit_calls.append(now)
        return True
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        if not self._rate_limit_check():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if not self.session:
                raise RuntimeError("BinanceService session not initialized. Use 'async with BinanceService()' context manager.")
            
            async with self.session.get(url, params=params) as response:
                response_time = time.time() - start_time
                # Ensure response.status is not None for linter
                status_code = response.status if response.status is not None else 500  # type: ignore
                await record_api_call("binance", endpoint, status_code, response_time)
                
                if response.status == 200:
                    result = await response.json()
                    if result is None:
                        raise Exception("Empty response from API")
                    return result
                else:
                    error_msg = f"API request failed: {response.status}"
                    await record_api_error("binance", endpoint, response.status, error_msg)
                    raise Exception(error_msg)
                    
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            await record_api_error("binance", endpoint, 408, error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            await record_api_error("binance", endpoint, 500, error_msg)
            raise Exception(error_msg)
    
    # Market Data
    async def get_market_data(self, symbol: str) -> Optional[BinanceMarketData]:
        """Get real-time market data for a symbol"""
        try:
            # Convert symbol format (BTC-USDT -> BTCUSDT)
            binance_symbol = symbol.replace("-", "")
            
            response = await self._make_request("/api/v3/ticker/24hr", {"symbol": binance_symbol})
            
            # Add explicit check to satisfy linter
            if response is None:
                logger.error(f"Received None response for {symbol}")
                return None
            
            # Ensure response is a dictionary
            if not isinstance(response, dict):
                logger.error(f"Received non-dict response for {symbol}: {type(response)}")
                return None
            
            # Type assertion to help linter understand response is not None
            response_dict: Dict[str, Any] = response
            
            # Ensure response_dict is not None for linter
            if response_dict is None:
                logger.error(f"Response dict is None for {symbol}")
                return None
            
            # Extract values with explicit None checks to satisfy linter
            last_price = response_dict.get("lastPrice", "0")
            volume = response_dict.get("volume", "0")
            price_change = response_dict.get("priceChangePercent", "0")
            high_price = response_dict.get("highPrice", "0")
            low_price = response_dict.get("lowPrice", "0")
            
            return BinanceMarketData(
                symbol=symbol,
                price=float(last_price),
                volume_24h=float(volume),
                change_24h=float(price_change),
                high_24h=float(high_price),
                low_24h=float(low_price),
                timestamp=datetime.utcnow()
            )
                
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            # Convert symbol format (BTC-USDT -> BTCUSDT)
            binance_symbol = symbol.replace("-", "")
            
            response = await self._make_request("/api/v3/ticker/price", {"symbol": binance_symbol})
            
            if response and "price" in response:
                return float(response["price"])
            else:
                logger.warning(f"Failed to get price for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    # Historical Data
    async def get_klines(self, symbol: str, interval: str = "1h", 
                        limit: int = 100, start_time: Optional[int] = None,
                        end_time: Optional[int] = None) -> List[BinanceKline]:
        """Get historical kline data"""
        try:
            # Convert symbol format (BTC-USDT -> BTCUSDT)
            binance_symbol = symbol.replace("-", "")
            
            params = {
                "symbol": binance_symbol,
                "interval": interval,
                "limit": limit
            }
            
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time
            
            response = await self._make_request("/api/v3/klines", params)
            
            if response:
                klines = []
                for kline_data in response:
                    kline = BinanceKline(
                        symbol=symbol,
                        open_time=datetime.fromtimestamp(float(kline_data[0]) / 1000),
                        close_time=datetime.fromtimestamp(float(kline_data[6]) / 1000),
                        open_price=float(kline_data[1]),
                        high_price=float(kline_data[2]),
                        low_price=float(kline_data[3]),
                        close_price=float(kline_data[4]),
                        volume=float(kline_data[5]),
                        quote_volume=float(kline_data[7]),
                        trades_count=int(kline_data[8]),
                        timestamp=datetime.utcnow()
                    )
                    klines.append(kline)
                return klines
            else:
                logger.warning(f"Failed to get klines for {symbol}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            return []
    
    async def get_historical_prices(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical prices for analysis"""
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            klines = await self.get_klines(
                symbol=symbol,
                interval="1d",
                start_time=start_time,
                end_time=end_time
            )
            
            historical_data = []
            for kline in klines:
                historical_data.append({
                    "date": kline.open_time.isoformat(),
                    "open": kline.open_price,
                    "high": kline.high_price,
                    "low": kline.low_price,
                    "close": kline.close_price,
                    "volume": kline.volume
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical prices for {symbol}: {e}")
            return []
    
    # Exchange Information
    async def get_exchange_info(self) -> Optional[Dict[str, Any]]:
        """Get exchange information and trading rules"""
        try:
            response = await self._make_request("/api/v3/exchangeInfo")
            
            if response:
                return response
            else:
                logger.warning("Failed to get exchange info")
                return None
                
        except Exception as e:
            logger.error(f"Error getting exchange info: {e}")
            return None
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific symbol"""
        try:
            # Convert symbol format (BTC-USDT -> BTCUSDT)
            binance_symbol = symbol.replace("-", "")
            
            exchange_info = await self.get_exchange_info()
            
            if exchange_info:
                for symbol_info in exchange_info.get("symbols", []):
                    if symbol_info["symbol"] == binance_symbol:
                        return symbol_info
                
                logger.warning(f"Symbol {symbol} not found in exchange info")
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    # Price Verification
    async def verify_price(self, symbol: str, expected_price: float, tolerance: float = 0.01) -> bool:
        """Verify if a price is within acceptable range"""
        try:
            actual_price = await self.get_price(symbol)
            
            if actual_price is None:
                logger.warning(f"Could not verify price for {symbol} - no data available")
                return False
            
            price_diff = abs(actual_price - expected_price) / expected_price
            
            if price_diff <= tolerance:
                logger.info(f"Price verification passed for {symbol}: expected={expected_price}, actual={actual_price}")
                return True
            else:
                logger.warning(f"Price verification failed for {symbol}: expected={expected_price}, actual={actual_price}, diff={price_diff:.2%}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying price for {symbol}: {e}")
            return False
    
    # Market Analysis
    async def get_market_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market analysis for multiple symbols"""
        try:
            analysis = {
                "symbols": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for symbol in symbols:
                market_data = await self.get_market_data(symbol)
                if market_data:
                    analysis["symbols"][symbol] = {
                        "price": market_data.price,
                        "change_24h": market_data.change_24h,
                        "volume_24h": market_data.volume_24h,
                        "high_24h": market_data.high_24h,
                        "low_24h": market_data.low_24h
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting market analysis: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Utility Methods
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limit statistics"""
        return {
            "calls_in_window": len(self.rate_limit_calls),
            "max_calls_per_window": self.max_calls_per_window,
            "rate_limit_window": self.rate_limit_window
        }
    
    def convert_symbol_format(self, symbol: str, to_binance: bool = True) -> str:
        """Convert symbol format between KuCoin and Binance"""
        if to_binance:
            # KuCoin format (BTC-USDT) to Binance format (BTCUSDT)
            return symbol.replace("-", "")
        else:
            # Binance format (BTCUSDT) to KuCoin format (BTC-USDT)
            # This is a simplified conversion - in practice, you'd need a mapping
            if len(symbol) >= 6 and symbol.endswith("USDT"):
                return f"{symbol[:-4]}-USDT"
            return symbol

# Global service instance
binance_service: Optional[BinanceService] = None

async def get_binance_service() -> BinanceService:
    """Get or create Binance service instance"""
    global binance_service
    if binance_service is None:
        binance_service = BinanceService()
        await binance_service.__aenter__()
    return binance_service 