"""
Futures Symbol Validator Service
Ensures symbols are available on KuCoin futures for trading
Validates against both Binance and KuCoin futures markets
"""
import asyncio
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import aiohttp

from src.services.kucoin_service import get_kucoin_service
from src.services.binance_service import get_binance_service
from src.config.settings import settings
from src.utils.symbol_converter import SymbolConverter, to_standard, to_kucoin, to_binance

logger = logging.getLogger(__name__)

@dataclass
class FuturesSymbolInfo:
    """Futures symbol information"""
    symbol: str
    exchange: str
    base_asset: str
    quote_asset: str
    contract_type: str  # perpetual, quarterly, etc.
    status: str  # trading, settling, closed
    min_qty: float
    max_qty: float
    tick_size: float
    max_leverage: int
    maintainance_margin: float
    is_tradeable: bool
    volume_24h: float = 0.0
    open_interest: float = 0.0

class FuturesSymbolValidator:
    """
    Validates futures symbols across exchanges
    Ensures trading symbols are available on KuCoin
    """
    
    def __init__(self):
        self.kucoin_symbols: Dict[str, FuturesSymbolInfo] = {}
        self.binance_symbols: Dict[str, FuturesSymbolInfo] = {}
        self.common_symbols: Set[str] = set()
        self.kucoin_only_symbols: Set[str] = set()
        self.binance_only_symbols: Set[str] = set()
        self._initialized = False
        # Blacklist symbols that must be excluded from trading and listings
        # Standardized format preferred (e.g., MATICUSDT); include common exchange-specific variants
        self._blacklist: Set[str] = {
            "MATICUSDT",  # Standard format
            "MATICUSDTM", # KuCoin perpetual suffix
        }

    def _is_blacklisted(self, symbol: str, base_asset: Optional[str] = None) -> bool:
        std = to_standard(symbol)
        if std in self._blacklist:
            return True
        if base_asset and base_asset.upper() == "MATIC":
            return True
        # Also guard original symbol variants
        return symbol.upper().startswith("MATIC")
        
    async def initialize(self):
        """Initialize and fetch symbol lists from both exchanges"""
        if self._initialized:
            return
            
        try:
            # Fetch KuCoin futures symbols
            await self._fetch_kucoin_futures_symbols()
            
            # Fetch Binance futures symbols
            await self._fetch_binance_futures_symbols()
            
            # Calculate common and unique symbols
            self._calculate_symbol_sets()
            
            self._initialized = True
            logger.info(f"✅ Symbol validator initialized: {len(self.kucoin_symbols)} KuCoin, {len(self.binance_symbols)} Binance")
            
        except Exception as e:
            logger.error(f"Failed to initialize symbol validator: {e}")
            raise
    
    async def _fetch_kucoin_futures_symbols(self):
        """Fetch all futures symbols from KuCoin using the working API manager"""
        try:
            # Import and use the working KuCoin API manager
            import sys
            import os
            sys.path.append('/Users/dansidanutz/Desktop/ZmartBot')
            
            from kucoin_api_manager import KuCoinAPIManager
            
            # Initialize the API manager
            api_manager = KuCoinAPIManager()
            
            # Get the exchange instance
            exchange = api_manager.get_exchange("monitoring")
            
            if not exchange:
                logger.error("No KuCoin exchange available")
                return
            
            # Fetch markets using CCXT
            markets = exchange.fetch_markets()
            
            for market in markets:
                # Include both 'future' (quarterly) and 'swap' (perpetual) markets
                if (market.get('type') in ['future', 'swap']) and market.get('active'):
                    symbol = market.get('symbol', '')
                    
                    # Store the original KuCoin symbol for reference
                    original_kucoin_symbol = symbol
                    
                    # Convert KuCoin format to standard format
                    standard_symbol = self._standardize_kucoin_symbol(symbol)
                    
                    # Skip blacklisted symbols
                    if self._is_blacklisted(symbol, market.get('base', '')):
                        continue

                    # Get market limits
                    limits = market.get('limits', {})
                    amount = limits.get('amount', {})
                    
                    # Determine contract type
                    contract_type = 'perpetual' if market.get('type') == 'swap' else 'quarterly'
                    
                    # Store with both standard symbol and track original
                    info = FuturesSymbolInfo(
                        symbol=standard_symbol,
                        exchange='kucoin',
                        base_asset=market.get('base', '').replace('XBT', 'BTC'),
                        quote_asset=market.get('quote', ''),
                        contract_type=contract_type,
                        status='trading',
                        min_qty=float(amount.get('min', 1)),
                        max_qty=float(amount.get('max', 1000000)),
                        tick_size=float(market.get('precision', {}).get('price', 0.1)),
                        max_leverage=int(market.get('info', {}).get('maxLeverage', 100)),
                        maintainance_margin=float(market.get('info', {}).get('maintainMargin', 0.005)),
                        is_tradeable=True
                    )
                    
                    # Store with standard symbol as key
                    self.kucoin_symbols[standard_symbol] = info
                    
                    # Also store original format for reverse lookup if needed
                    if original_kucoin_symbol != standard_symbol:
                        self.kucoin_symbols[original_kucoin_symbol] = info
                    
            logger.info(f"Fetched {len(self.kucoin_symbols)} KuCoin futures symbols using API manager")
            
        except Exception as e:
            logger.error(f"Error fetching KuCoin futures symbols: {e}")
            # Continue with empty KuCoin symbols if fetch fails
            self.kucoin_symbols = {}
    

    
    async def _fetch_binance_futures_symbols(self):
        """Fetch all futures symbols from Binance"""
        try:
            # Try using the Binance service first
            binance_service = await get_binance_service()
            
            # Get exchange info from Binance futures
            async with binance_service:
                response = await binance_service._make_request(
                    "/fapi/v1/exchangeInfo",
                    use_futures=True
                )
                
                if response and 'symbols' in response:
                    for symbol_info in response['symbols']:
                        if symbol_info.get('status') == 'TRADING':
                            symbol = symbol_info.get('symbol', '')
                            # Skip blacklisted symbols (e.g., MATIC)
                            if self._is_blacklisted(symbol, symbol_info.get('baseAsset', '')):
                                continue
                            
                            # Get filters for min/max quantities
                            min_qty = 0.001
                            max_qty = 10000
                            tick_size = 0.01
                            
                            for filter in symbol_info.get('filters', []):
                                if filter['filterType'] == 'LOT_SIZE':
                                    min_qty = float(filter.get('minQty', 0.001))
                                    max_qty = float(filter.get('maxQty', 10000))
                                elif filter['filterType'] == 'PRICE_FILTER':
                                    tick_size = float(filter.get('tickSize', 0.01))
                            
                            self.binance_symbols[symbol] = FuturesSymbolInfo(
                                symbol=symbol,
                                exchange='binance',
                                base_asset=symbol_info.get('baseAsset', ''),
                                quote_asset=symbol_info.get('quoteAsset', ''),
                                contract_type=symbol_info.get('contractType', 'PERPETUAL').lower(),
                                status='trading',
                                min_qty=min_qty,
                                max_qty=max_qty,
                                tick_size=tick_size,
                                max_leverage=125,  # Binance default max
                                maintainance_margin=0.004,  # Binance typical
                                is_tradeable=True
                            )
                            
            logger.info(f"Fetched {len(self.binance_symbols)} Binance futures symbols")
            
        except Exception as e:
            logger.error(f"Error fetching Binance futures symbols: {e}")
            
            # Fallback: Use hardcoded common Binance symbols if API fails
            logger.info("Using fallback Binance symbols due to API connection issues")
            fallback_symbols = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT", 
                "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "UNIUSDT",
                "LTCUSDT", "BCHUSDT", "ATOMUSDT", "ETCUSDT", "FILUSDT", "NEARUSDT",
                "ALGOUSDT", "ICPUSDT", "VETUSDT", "FLOWUSDT", "THETAUSDT", "XTZUSDT",
                "AAVEUSDT", "SUSHIUSDT", "SNXUSDT", "COMPUSDT", "MKRUSDT", "YFIUSDT",
                "ZECUSDT", "DASHUSDT", "XMRUSDT", "TRXUSDT", "EOSUSDT", "IOTAUSDT",
                "NEOUSDT", "QTUMUSDT", "WAVESUSDT", "ZILUSDT", "HBARUSDT", "HOTUSDT",
                "ENJUSDT", "MANAUSDT", "SANDUSDT", "AXSUSDT", "GALAUSDT", "ROSEUSDT",
                "CHZUSDT", "ANKRUSDT", "BATUSDT", "DENTUSDT", "HIVEUSDT", "STMXUSDT",
                "STORJUSDT", "VTHOUSDT", "WRXUSDT", "ZRXUSDT", "KAVAUSDT", "RENUSDT",
                "RSRUSDT", "SKLUSDT", "SXPUSDT", "TOMOUSDT", "WOOUSDT", "YGGUSDT"
            ]
            
            for symbol in fallback_symbols:
                if not self._is_blacklisted(symbol):
                    self.binance_symbols[symbol] = FuturesSymbolInfo(
                        symbol=symbol,
                        exchange='binance',
                        base_asset=symbol.replace('USDT', ''),
                        quote_asset='USDT',
                        contract_type='perpetual',
                        status='trading',
                        min_qty=0.001,
                        max_qty=10000,
                        tick_size=0.01,
                        max_leverage=125,
                        maintainance_margin=0.004,
                        is_tradeable=True
                    )
            
            logger.info(f"Loaded {len(self.binance_symbols)} fallback Binance symbols")
    
    def _standardize_kucoin_symbol(self, kucoin_symbol: str) -> str:
        """Convert KuCoin symbol format to standard format"""
        # Use the new symbol converter for accurate conversion
        # KuCoin uses formats like:
        # XBTUSDTM -> BTCUSDT
        # ETHUSDTM -> ETHUSDT
        # SOLUSDTM -> SOLUSDT
        return to_standard(kucoin_symbol)
    
    def _calculate_symbol_sets(self):
        """Calculate common and unique symbol sets"""
        # Filter out any blacklisted symbols before computing sets
        kucoin_set = {s for s in self.kucoin_symbols.keys() if not self._is_blacklisted(s)}
        binance_set = {s for s in self.binance_symbols.keys() if not self._is_blacklisted(s)}
        
        self.common_symbols = kucoin_set & binance_set
        self.kucoin_only_symbols = kucoin_set - binance_set
        self.binance_only_symbols = binance_set - kucoin_set
        
        logger.info(f"Symbol distribution: {len(self.common_symbols)} common, "
                   f"{len(self.kucoin_only_symbols)} KuCoin-only, "
                   f"{len(self.binance_only_symbols)} Binance-only")
    
    async def is_tradeable_on_kucoin(self, symbol: str) -> bool:
        """Check if a symbol is tradeable on KuCoin futures"""
        if not self._initialized:
            await self.initialize()
        
        # Convert to standard format first
        standard_symbol = to_standard(symbol)
        
        # Check if the standard format exists in our KuCoin symbols
        if standard_symbol in self.kucoin_symbols:
            return self.kucoin_symbols[standard_symbol].is_tradeable
        
        # Also check the original format in case it's already standard
        return symbol in self.kucoin_symbols and self.kucoin_symbols[symbol].is_tradeable
    
    async def get_tradeable_symbols(self) -> List[str]:
        """Get all symbols tradeable on KuCoin futures"""
        if not self._initialized:
            await self.initialize()
        
        return [symbol for symbol, info in self.kucoin_symbols.items() if info.is_tradeable and not self._is_blacklisted(symbol, info.base_asset)]
    
    async def get_common_futures_symbols(self) -> List[str]:
        """Get symbols available on both KuCoin and Binance futures"""
        if not self._initialized:
            await self.initialize()
        
        return sorted([s for s in self.common_symbols if not self._is_blacklisted(s)])
    
    async def validate_symbol_list(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Validate a list of symbols for trading on KuCoin
        Returns validation results with recommendations
        """
        if not self._initialized:
            await self.initialize()
        
        results = {
            'valid_symbols': [],
            'invalid_symbols': [],
            'recommendations': [],
            'warnings': [],
            'summary': {}
        }
        
        for symbol in symbols:
            if await self.is_tradeable_on_kucoin(symbol):
                results['valid_symbols'].append(symbol)
                
                # Add info if also available on Binance
                if symbol in self.binance_symbols:
                    results['recommendations'].append(
                        f"✅ {symbol}: Available on both exchanges (good for price data)"
                    )
            else:
                results['invalid_symbols'].append(symbol)
                
                # Check if available on Binance
                if symbol in self.binance_symbols:
                    results['warnings'].append(
                        f"⚠️ {symbol}: Available on Binance but NOT on KuCoin (cannot trade)"
                    )
                    
                    # Suggest alternatives
                    alternative = self._find_similar_kucoin_symbol(symbol)
                    if alternative:
                        results['recommendations'].append(
                            f"💡 Consider {alternative} instead of {symbol}"
                        )
                else:
                    results['warnings'].append(
                        f"❌ {symbol}: Not available on either exchange"
                    )
        
        # Summary
        results['summary'] = {
            'total_symbols': len(symbols),
            'valid_for_trading': len(results['valid_symbols']),
            'invalid_for_trading': len(results['invalid_symbols']),
            'can_trade': len(results['valid_symbols']) > 0
        }
        
        return results
    
    def _find_similar_kucoin_symbol(self, symbol: str) -> Optional[str]:
        """Find a similar symbol available on KuCoin"""
        base = symbol.replace('USDT', '').replace('BUSD', '')
        
        # Look for USDT pairs
        if f"{base}USDT" in self.kucoin_symbols:
            return f"{base}USDT"
        
        # Look for similar base assets
        for kucoin_symbol in self.kucoin_symbols:
            if base in kucoin_symbol:
                return kucoin_symbol
        
        return None
    
    async def get_symbol_info(self, symbol: str) -> Optional[FuturesSymbolInfo]:
        """Get detailed information about a futures symbol"""
        if not self._initialized:
            await self.initialize()
        
        # Prefer KuCoin info since that's where we trade
        if symbol in self.kucoin_symbols:
            return self.kucoin_symbols[symbol]
        elif symbol in self.binance_symbols:
            return self.binance_symbols[symbol]
        
        return None
    
    async def get_recommended_symbols(self) -> List[str]:
        """
        Get recommended symbols for trading
        Prioritizes symbols available on both exchanges with good liquidity
        """
        if not self._initialized:
            await self.initialize()
        
        # High-volume perpetual futures available on both exchanges
        recommended = [
            'BTCUSDT',   # Bitcoin
            'ETHUSDT',   # Ethereum
            'SOLUSDT',   # Solana
            'BNBUSDT',   # Binance Coin
            'XRPUSDT',   # Ripple
            'ADAUSDT',   # Cardano
            'AVAXUSDT',  # Avalanche
            'DOGEUSDT',  # Dogecoin
            'LINKUSDT'   # Chainlink
        ]
        
        # Filter to only include symbols available on KuCoin
        available = []
        for symbol in recommended:
            if await self.is_tradeable_on_kucoin(symbol):
                available.append(symbol)
        
        return available

# Global instance
_futures_validator = None

async def get_futures_validator() -> FuturesSymbolValidator:
    """Get or create futures symbol validator instance"""
    global _futures_validator
    if _futures_validator is None:
        _futures_validator = FuturesSymbolValidator()
        await _futures_validator.initialize()
    return _futures_validator