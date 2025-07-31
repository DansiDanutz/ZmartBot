"""
Zmart Trading Bot Platform - Unified Market Data Service
Combines KuCoin and Binance for reliable price data and verification
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from .kucoin_service import get_kucoin_service, KuCoinService
from .binance_service import get_binance_service, BinanceService

logger = logging.getLogger(__name__)

class UnifiedMarketData(BaseModel):
    """Unified market data model"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    source: str  # "kucoin", "binance", or "verified"
    confidence: float  # 0.0 to 1.0
    timestamp: datetime

class PriceVerification(BaseModel):
    """Price verification result"""
    symbol: str
    kucoin_price: Optional[float] = None
    binance_price: Optional[float] = None
    price_difference: Optional[float] = None
    price_difference_percent: Optional[float] = None
    is_verified: bool = False
    recommended_price: Optional[float] = None
    timestamp: datetime

class MarketDataService:
    """
    Unified Market Data Service
    Combines KuCoin and Binance for reliable price data
    """
    
    def __init__(self):
        self.kucoin_service: Optional[KuCoinService] = None
        self.binance_service: Optional[BinanceService] = None
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 30  # 30 seconds cache
        
    async def _get_services(self):
        """Get or initialize services"""
        if self.kucoin_service is None:
            self.kucoin_service = await get_kucoin_service()
        if self.binance_service is None:
            self.binance_service = await get_binance_service()
    
    async def get_unified_market_data(self, symbol: str) -> Optional[UnifiedMarketData]:
        """Get unified market data from both sources"""
        try:
            await self._get_services()
            
            # Get data from both sources
            kucoin_data = None
            binance_data = None
            
            # Try KuCoin first (primary source)
            try:
                if self.kucoin_service:
                    kucoin_data = await self.kucoin_service.get_market_data(symbol)
            except Exception as e:
                logger.warning(f"KuCoin data unavailable for {symbol}: {e}")
            
            # Try Binance as backup
            try:
                if self.binance_service:
                    binance_data = await self.binance_service.get_market_data(symbol)
            except Exception as e:
                logger.warning(f"Binance data unavailable for {symbol}: {e}")
            
            # Determine best price and confidence
            if kucoin_data and binance_data:
                # Both sources available - verify prices
                price_diff = abs(kucoin_data.price - binance_data.price) / kucoin_data.price
                
                if price_diff <= 0.01:  # 1% tolerance
                    # Prices are close - use KuCoin as primary
                    return UnifiedMarketData(
                        symbol=symbol,
                        price=kucoin_data.price,
                        volume_24h=kucoin_data.volume_24h,
                        change_24h=kucoin_data.change_24h,
                        high_24h=kucoin_data.high_24h,
                        low_24h=kucoin_data.low_24h,
                        source="verified",
                        confidence=1.0 - price_diff,
                        timestamp=datetime.utcnow()
                    )
                else:
                    # Prices differ significantly - use KuCoin but with lower confidence
                    return UnifiedMarketData(
                        symbol=symbol,
                        price=kucoin_data.price,
                        volume_24h=kucoin_data.volume_24h,
                        change_24h=kucoin_data.change_24h,
                        high_24h=kucoin_data.high_24h,
                        low_24h=kucoin_data.low_24h,
                        source="kucoin",
                        confidence=0.7,
                        timestamp=datetime.utcnow()
                    )
            
            elif kucoin_data:
                # Only KuCoin available
                return UnifiedMarketData(
                    symbol=symbol,
                    price=kucoin_data.price,
                    volume_24h=kucoin_data.volume_24h,
                    change_24h=kucoin_data.change_24h,
                    high_24h=kucoin_data.high_24h,
                    low_24h=kucoin_data.low_24h,
                    source="kucoin",
                    confidence=0.8,
                    timestamp=datetime.utcnow()
                )
            
            elif binance_data:
                # Only Binance available
                return UnifiedMarketData(
                    symbol=symbol,
                    price=binance_data.price,
                    volume_24h=binance_data.volume_24h,
                    change_24h=binance_data.change_24h,
                    high_24h=binance_data.high_24h,
                    low_24h=binance_data.low_24h,
                    source="binance",
                    confidence=0.6,
                    timestamp=datetime.utcnow()
                )
            
            else:
                # No data available
                logger.error(f"No market data available for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting unified market data for {symbol}: {e}")
            return None
    
    async def verify_price(self, symbol: str, expected_price: float, tolerance: float = 0.01) -> PriceVerification:
        """Verify price against both sources"""
        try:
            await self._get_services()
            
            kucoin_price = None
            binance_price = None
            
            # Get prices from both sources
            try:
                if self.kucoin_service:
                    kucoin_data = await self.kucoin_service.get_market_data(symbol)
                    if kucoin_data:
                        kucoin_price = kucoin_data.price
            except Exception as e:
                logger.warning(f"KuCoin price unavailable for {symbol}: {e}")
            
            try:
                if self.binance_service:
                    binance_price = await self.binance_service.get_price(symbol)
            except Exception as e:
                logger.warning(f"Binance price unavailable for {symbol}: {e}")
            
            # Calculate price differences
            price_difference = None
            price_difference_percent = None
            is_verified = False
            recommended_price = None
            
            if kucoin_price and binance_price:
                price_difference = abs(kucoin_price - binance_price)
                price_difference_percent = price_difference / kucoin_price
                
                if price_difference_percent <= tolerance:
                    is_verified = True
                    recommended_price = kucoin_price  # Prefer KuCoin for trading
                else:
                    # Prices differ significantly - use average
                    recommended_price = (kucoin_price + binance_price) / 2
            
            elif kucoin_price:
                recommended_price = kucoin_price
                is_verified = True  # Single source but primary
            
            elif binance_price:
                recommended_price = binance_price
                is_verified = False  # Single source but backup
            
            return PriceVerification(
                symbol=symbol,
                kucoin_price=kucoin_price,
                binance_price=binance_price,
                price_difference=price_difference,
                price_difference_percent=price_difference_percent,
                is_verified=is_verified,
                recommended_price=recommended_price,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error verifying price for {symbol}: {e}")
            return PriceVerification(
                symbol=symbol,
                is_verified=False,
                timestamp=datetime.utcnow()
            )
    
    async def get_real_market_price(self, symbol: str) -> Optional[float]:
        """Get real market price with verification"""
        try:
            market_data = await self.get_unified_market_data(symbol)
            if market_data and market_data.confidence >= 0.6:
                return market_data.price
            else:
                logger.warning(f"Insufficient confidence for {symbol} price: {market_data.confidence if market_data else 'None'}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting real market price for {symbol}: {e}")
            return None
    
    async def get_bulk_market_data(self, symbols: List[str]) -> Dict[str, UnifiedMarketData]:
        """Get market data for multiple symbols"""
        try:
            results = {}
            
            # Process symbols concurrently
            tasks = [self.get_unified_market_data(symbol) for symbol in symbols]
            market_data_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, market_data in zip(symbols, market_data_list):
                if isinstance(market_data, Exception):
                    logger.error(f"Error getting data for {symbol}: {market_data}")
                elif market_data:
                    results[symbol] = market_data
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting bulk market data: {e}")
            return {}
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data from Binance (more reliable for historical data)"""
        try:
            await self._get_services()
            if self.binance_service:
                return await self.binance_service.get_historical_prices(symbol, days)
            else:
                logger.warning("Binance service not available for historical data")
                return []
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    async def get_market_summary(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market summary for multiple symbols"""
        try:
            market_data = await self.get_bulk_market_data(symbols)
            
            summary = {
                "symbols": {},
                "total_symbols": len(symbols),
                "successful_symbols": len(market_data),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for symbol, data in market_data.items():
                summary["symbols"][symbol] = {
                    "price": data.price,
                    "change_24h": data.change_24h,
                    "volume_24h": data.volume_24h,
                    "source": data.source,
                    "confidence": data.confidence
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics from both services"""
        try:
            kucoin_stats = {}
            binance_stats = {}
            
            if self.kucoin_service:
                kucoin_stats = self.kucoin_service.get_rate_limit_stats()
            
            if self.binance_service:
                binance_stats = self.binance_service.get_rate_limit_stats()
            
            return {
                "kucoin": kucoin_stats,
                "binance": binance_stats,
                "cache_size": len(self.price_cache)
            }
            
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {"error": str(e)}

# Global service instance
market_data_service: Optional[MarketDataService] = None

async def get_market_data_service() -> MarketDataService:
    """Get or create market data service instance"""
    global market_data_service
    if market_data_service is None:
        market_data_service = MarketDataService()
    return market_data_service 