"""
KuCoin API Service - Updated with correct implementation from guide
"""
import asyncio
import logging
import aiohttp
from aiohttp import ClientTimeout
import time
import hmac
import hashlib
import base64
import uuid
from urllib.parse import urlencode
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class KuCoinOrder(BaseModel):
    """KuCoin order model"""
    id: str
    symbol: str
    side: str  # buy, sell
    type: str  # market, limit
    size: float
    price: Optional[float] = None
    status: str
    timestamp: datetime

class KuCoinPosition(BaseModel):
    """KuCoin position model"""
    symbol: str
    side: str  # long, short
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin_type: str
    leverage: int
    liquidation_price: float
    timestamp: datetime

class KuCoinAccount(BaseModel):
    """KuCoin account model"""
    account_id: str
    currency: str
    balance: float
    available: float
    holds: float
    timestamp: datetime

class KuCoinMarketData(BaseModel):
    """KuCoin market data model"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

class KuCoinService:
    """KuCoin API Service with correct implementation"""
    
    def __init__(self):
        # Load credentials from environment variables for security
        from src.config.settings import settings
        self.api_key = settings.KUCOIN_API_KEY
        self.api_secret = settings.KUCOIN_SECRET
        self.passphrase = settings.KUCOIN_PASSPHRASE
        self.broker_name = settings.KUCOIN_BROKER_NAME or "KRYPTOSTACKMASTER"
        self.partner = settings.KUCOIN_API_PARTNER or "KRYPTOSTACK_ND"
        self.broker_key = settings.KUCOIN_API_PARTNER_SECRET or ""
        
        # Correct URLs
        self.futures_base_url = "https://api-futures.kucoin.com"
        self.spot_base_url = "https://api.kucoin.com"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Verified symbol mappings
        self.symbols = {
            "bitcoin": "XBTUSDTM",      # ⚠️ XBT not BTC!
            "ethereum": "ETHUSDTM",
            "avalanche": "AVAXUSDTM",
            "solana": "SOLUSDTM",
            "dogecoin": "DOGEUSDTM",
            "ripple": "XRPUSDTM"
        }
        
        # Contract specifications
        self.multipliers = {
            "XBTUSDTM": 0.001,    # 1 contract = 0.001 BTC
            "ETHUSDTM": 0.01,     # 1 contract = 0.01 ETH
            "AVAXUSDTM": 0.1,     # 1 contract = 0.1 AVAX
        }
        
        self.max_leverage = {
            "XBTUSDTM": 125,      # Bitcoin: 125x max
            "ETHUSDTM": 100,      # Ethereum: 100x max
            "AVAXUSDTM": 75,      # Avalanche: 75x max
        }

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass

    def _rate_limit_check(self) -> bool:
        """Check rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval)
        self.last_request_time = current_time
        return True

    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = "") -> str:
        """Generate HMAC-SHA256 signature"""
        message = timestamp + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature

    def _generate_passphrase(self) -> str:
        """Generate encrypted passphrase"""
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

    def _generate_broker_signature(self, timestamp: str) -> str:
        """Generate broker signature"""
        message = timestamp + self.partner + self.api_key
        signature = base64.b64encode(
            hmac.new(
                self.broker_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                           data: Optional[Dict] = None, use_futures: bool = True) -> Dict[str, Any]:
        """Make authenticated API request"""
        self._rate_limit_check()
        
        timestamp = str(int(time.time() * 1000))
        base_url = self.futures_base_url if use_futures else self.spot_base_url
        
        # Prepare URL
        url = base_url + endpoint
        if params:
            url += "?" + urlencode(params)
            endpoint += "?" + urlencode(params)
        
        # Prepare body
        body = ""
        if data:
            import json
            body = json.dumps(data, separators=(',', ':'))
        
        # Generate signatures
        signature = self._generate_signature(timestamp, method, endpoint, body)
        passphrase = self._generate_passphrase()
        broker_signature = self._generate_broker_signature(timestamp)
        
        # Headers with broker authentication
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
        
        # Make request with retry logic
        max_retries = 3
        timeout = ClientTimeout(total=30, connect=10)
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    if method == "GET":
                        async with session.get(url, headers=headers) as response:
                            response_text = await response.text()
                    elif method == "POST":
                        async with session.post(url, headers=headers, data=body) as response:
                            response_text = await response.text()
                    elif method == "DELETE":
                        async with session.delete(url, headers=headers) as response:
                            response_text = await response.text()
                    
                    # Handle response
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get('code') == '200000':
                            return data.get('data', {})
                        else:
                            error_msg = data.get('msg', 'Unknown error') if data else 'No response data'
                            raise Exception(f"API Error: {error_msg}")
                    else:
                        raise Exception(f"HTTP Error {response.status}: {response_text}")
                        
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise Exception("Request timeout after retries")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)
        
        # This should never be reached, but linter requires it
        raise Exception("Request failed after all retries")

    # ========== MARKET DATA METHODS ==========
    
    async def get_server_time(self) -> int:
        """Get server timestamp"""
        response = await self._make_request("GET", "/api/v1/timestamp", use_futures=True)
        return int(response) if isinstance(response, (int, str)) else 0
    
    async def get_contracts(self) -> List[Dict[str, Any]]:
        """Get all active futures contracts"""
        response = await self._make_request("GET", "/api/v1/contracts/active", use_futures=True)
        return response if isinstance(response, list) else []
    
    async def get_contract_detail(self, symbol: str) -> Dict[str, Any]:
        """Get contract details for specific symbol"""
        return await self._make_request("GET", f"/api/v1/contracts/{symbol}", use_futures=True)
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get 24hr ticker for symbol"""
        params = {"symbol": symbol}
        return await self._make_request("GET", "/api/v1/ticker", params=params, use_futures=True)
    
    async def get_orderbook(self, symbol: str) -> Dict[str, Any]:
        """Get order book for symbol"""
        params = {"symbol": symbol}
        return await self._make_request("GET", "/api/v1/level2_market_data", params=params, use_futures=True)
    
    async def get_klines(self, symbol: str, granularity: int, 
                         from_time: Optional[int] = None, to_time: Optional[int] = None) -> List:
        """Get candlestick data"""
        params = {"symbol": symbol, "granularity": granularity}
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time
        response = await self._make_request("GET", "/api/v1/kline/query", params=params, use_futures=True)
        return response if isinstance(response, list) else []

    # ========== TRADING METHODS ==========
    
    async def place_order(self, symbol: str, side: str, order_type: str = "limit",
                         size: Optional[int] = None, price: Optional[str] = None,
                         leverage: Optional[int] = None, margin_mode: str = "ISOLATED") -> Dict[str, Any]:
        """Place futures order with correct symbol validation"""
        
        # Validate symbol format
        if not symbol.endswith('M'):
            raise ValueError(f"Invalid futures symbol: {symbol}. Must end with 'M' (e.g., XBTUSDTM)")
        
        order_data = {
            "clientOid": str(uuid.uuid4()),
            "side": side,
            "symbol": symbol,
            "type": order_type,
            "marginMode": margin_mode
        }
        
        if size:
            order_data["size"] = str(size)
        if price:
            order_data["price"] = str(price)
        if leverage:
            order_data["leverage"] = str(leverage)
            
        return await self._make_request("POST", "/api/v1/orders", data=order_data, use_futures=True)
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order by ID"""
        return await self._make_request("DELETE", f"/api/v1/orders/{order_id}", use_futures=True)
    
    async def get_orders(self, status: str = "active") -> Dict[str, Any]:
        """Get order list"""
        params = {"status": status}
        return await self._make_request("GET", "/api/v1/orders", params=params, use_futures=True)
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all positions"""
        response = await self._make_request("GET", "/api/v1/positions", use_futures=True)
        return response if isinstance(response, list) else []
    
    async def get_account_overview(self) -> Dict[str, Any]:
        """Get account overview"""
        return await self._make_request("GET", "/api/v1/account-overview", use_futures=True)
    
    async def place_futures_order(
        self,
        symbol: str,
        side: str,
        size: float,
        leverage: int = 20,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """Place futures order with proper formatting"""
        # Convert symbol format (e.g., BTC/USDT -> XBTUSDTM)
        futures_symbol = self._convert_to_futures_symbol(symbol)
        
        order_data = {
            "clientOid": uuid.uuid4().hex,
            "side": side,
            "symbol": futures_symbol,
            "type": order_type,
            "size": int(size),
            "leverage": str(leverage)
        }
        
        return await self._make_request("POST", "/api/v1/orders", data=order_data, use_futures=True)
    
    async def close_futures_position(self, symbol: str) -> Dict[str, Any]:
        """Close futures position for symbol"""
        # Get current position
        positions = await self.get_positions()
        
        for position in positions:
            if position.get("symbol") == self._convert_to_futures_symbol(symbol):
                # Close position by placing opposite order
                side = "sell" if position.get("side") == "buy" else "buy"
                size = abs(position.get("currentQty", 0))
                
                if size > 0:
                    return await self.place_futures_order(
                        symbol=symbol,
                        side=side,
                        size=size,
                        order_type="market"
                    )
        
        return {"error": "No position found to close"}
    
    def _convert_to_futures_symbol(self, symbol: str) -> str:
        """Convert spot symbol to futures symbol"""
        # Remove slash if present
        symbol = symbol.replace("/", "")
        
        # Map common symbols
        symbol_map = {
            "BTCUSDT": "XBTUSDTM",
            "ETHUSDT": "ETHUSDTM",
            "SOLUSDT": "SOLUSDTM",
            "BNBUSDT": "BNBUSDTM",
            "XRPUSDT": "XRPUSDTM",
            "AVAXUSDT": "AVAXUSDTM",
            "DOGEUSDT": "DOGEUSDTM"
        }
        
        return symbol_map.get(symbol.upper(), symbol + "M")

    # ========== CONVENIENCE METHODS WITH CORRECT SYMBOLS ==========
    
    async def buy_bitcoin(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Buy Bitcoin futures (XBTUSDTM)"""
        return await self.place_order("XBTUSDTM", "buy", "limit", size, price, leverage)
    
    async def sell_bitcoin(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Sell Bitcoin futures (XBTUSDTM)"""
        return await self.place_order("XBTUSDTM", "sell", "limit", size, price, leverage)
    
    async def buy_ethereum(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Buy Ethereum futures (ETHUSDTM)"""
        return await self.place_order("ETHUSDTM", "buy", "limit", size, price, leverage)
    
    async def sell_ethereum(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Sell Ethereum futures (ETHUSDTM)"""
        return await self.place_order("ETHUSDTM", "sell", "limit", size, price, leverage)
    
    async def buy_avalanche(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Buy Avalanche futures (AVAXUSDTM)"""
        return await self.place_order("AVAXUSDTM", "buy", "limit", size, price, leverage)
    
    async def sell_avalanche(self, price: str, size: int, leverage: int = 1) -> Dict[str, Any]:
        """Sell Avalanche futures (AVAXUSDTM)"""
        return await self.place_order("AVAXUSDTM", "sell", "limit", size, price, leverage)

    # ========== SPOT MARKET DATA (for compatibility) ==========
    
    async def get_market_data(self, symbol: str) -> Optional[KuCoinMarketData]:
        """Get real-time market data for a symbol (spot)"""
        try:
            # Use spot API for market data
            response = await self._make_request("GET", f"/api/v1/market/orderbook/level1?symbol={symbol}", use_futures=False)
            
            if response:
                return KuCoinMarketData(
                    symbol=symbol,
                    price=float(response.get("price", 0)),
                    volume_24h=float(response.get("size", 0)),
                    change_24h=0.0,  # Will be calculated separately
                    high_24h=0.0,    # Will be calculated separately
                    low_24h=0.0,     # Will be calculated separately
                    timestamp=datetime.utcnow()
                )
            else:
                logger.warning(f"Failed to get market data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None

    async def get_real_market_price(self, symbol: str) -> Optional[float]:
        """Get real market price for a symbol"""
        try:
            market_data = await self.get_market_data(symbol)
            return market_data.price if market_data else None
        except Exception as e:
            logger.error(f"Error getting real market price for {symbol}: {e}")
            return None

    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limit statistics"""
        return {
            "last_request_time": self.last_request_time,
            "min_interval": self.min_request_interval
        }

async def get_kucoin_service() -> KuCoinService:
    """Get KuCoin service instance"""
    return KuCoinService() 