"""Trading Bot Connector for seamless integration with various trading bots."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
import aiohttp
from ..core.models import AlertTrigger, MarketData, TechnicalIndicators

logger = logging.getLogger(__name__)


class TradingBotInterface(ABC):
    """Abstract interface for trading bot integrations."""
    
    @abstractmethod
    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """Send trading signal to the bot."""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from the bot."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance from the bot."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the bot is healthy and responsive."""
        pass


class WebhookTradingBot(TradingBotInterface):
    """Generic webhook-based trading bot integration."""
    
    def __init__(self, webhook_url: str, api_key: Optional[str] = None):
        self.webhook_url = webhook_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the webhook bot connection."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        )
    
    async def close(self):
        """Close the connection."""
        if self.session:
            await self.session.close()
    
    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """Send trading signal via webhook."""
        try:
            async with self.session.post(self.webhook_url, json=signal) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to send signal to webhook bot: {e}")
            return False
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions (if supported by webhook endpoint)."""
        try:
            positions_url = f"{self.webhook_url.rstrip('/')}/positions"
            async with self.session.get(positions_url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def get_balance(self) -> Dict[str, float]:
        """Get balance (if supported by webhook endpoint)."""
        try:
            balance_url = f"{self.webhook_url.rstrip('/')}/balance"
            async with self.session.get(balance_url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check webhook bot health."""
        try:
            health_url = f"{self.webhook_url.rstrip('/')}/health"
            async with self.session.get(health_url) as response:
                return response.status == 200
        except Exception:
            return False


class ZmartTradingBot(TradingBotInterface):
    """Zmart trading bot integration with KuCoin API."""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str, 
                 sandbox: bool = False, sub_account: str = "ZmartBot"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.sandbox = sandbox
        self.sub_account = sub_account
        self.exchange = None
        
    async def initialize(self):
        """Initialize KuCoin exchange connection."""
        import ccxt.async_support as ccxt
        
        self.exchange = ccxt.kucoin({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'sandbox': self.sandbox,
            'enableRateLimit': True,
        })
        
        # Set sub-account if specified
        if self.sub_account:
            self.exchange.headers['KC-API-SUB'] = self.sub_account
    
    async def close(self):
        """Close exchange connection."""
        if self.exchange:
            await self.exchange.close()
    
    async def send_signal(self, signal: Dict[str, Any]) -> bool:
        """Process trading signal and execute trade."""
        try:
            action = signal.get('action', '').upper()
            symbol = signal.get('symbol')
            quantity = signal.get('quantity', 0)
            price = signal.get('price')
            
            if not symbol or not quantity:
                logger.error("Invalid signal: missing symbol or quantity")
                return False
            
            if action == 'BUY':
                order = await self.exchange.create_market_buy_order(symbol, quantity)
            elif action == 'SELL':
                order = await self.exchange.create_market_sell_order(symbol, quantity)
            elif action == 'BUY_LIMIT':
                if not price:
                    logger.error("Limit order requires price")
                    return False
                order = await self.exchange.create_limit_buy_order(symbol, quantity, price)
            elif action == 'SELL_LIMIT':
                if not price:
                    logger.error("Limit order requires price")
                    return False
                order = await self.exchange.create_limit_sell_order(symbol, quantity, price)
            else:
                logger.error(f"Unknown action: {action}")
                return False
            
            logger.info(f"Order executed: {order['id']} - {action} {quantity} {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute trade signal: {e}")
            return False
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        try:
            balance = await self.exchange.fetch_balance()
            positions = []
            
            for currency, amounts in balance.items():
                if amounts['total'] > 0:
                    positions.append({
                        'symbol': currency,
                        'amount': amounts['total'],
                        'free': amounts['free'],
                        'used': amounts['used']
                    })
            
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance."""
        try:
            balance = await self.exchange.fetch_balance()
            return {
                'USDT': balance.get('USDT', {}).get('total', 0),
                'BTC': balance.get('BTC', {}).get('total', 0),
                'ETH': balance.get('ETH', {}).get('total', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check KuCoin API connectivity."""
        try:
            await self.exchange.fetch_status()
            return True
        except Exception:
            return False


class TradingBotConnector:
    """Main connector that manages multiple trading bot integrations."""
    
    def __init__(self):
        self.bots: Dict[str, TradingBotInterface] = {}
        self.signal_processors: Dict[str, Callable] = {}
        
    async def add_bot(self, bot_id: str, bot: TradingBotInterface):
        """Add a trading bot to the connector."""
        await bot.initialize()
        self.bots[bot_id] = bot
        logger.info(f"Added trading bot: {bot_id}")
    
    async def remove_bot(self, bot_id: str):
        """Remove a trading bot from the connector."""
        if bot_id in self.bots:
            await self.bots[bot_id].close()
            del self.bots[bot_id]
            logger.info(f"Removed trading bot: {bot_id}")
    
    def register_signal_processor(self, alert_type: str, processor: Callable):
        """Register a custom signal processor for specific alert types."""
        self.signal_processors[alert_type] = processor
        logger.info(f"Registered signal processor for: {alert_type}")
    
    async def process_alert(self, alert_trigger: AlertTrigger, bot_ids: Optional[List[str]] = None):
        """Process an alert and send signals to specified bots."""
        if bot_ids is None:
            bot_ids = list(self.bots.keys())
        
        # Generate trading signal from alert
        signal = await self._generate_signal(alert_trigger)
        if not signal:
            logger.warning(f"No signal generated for alert: {alert_trigger.alert_id}")
            return
        
        # Send signal to specified bots
        results = {}
        for bot_id in bot_ids:
            if bot_id in self.bots:
                try:
                    success = await self.bots[bot_id].send_signal(signal)
                    results[bot_id] = success
                    logger.info(f"Signal sent to {bot_id}: {success}")
                except Exception as e:
                    logger.error(f"Error sending signal to {bot_id}: {e}")
                    results[bot_id] = False
        
        return results
    
    async def _generate_signal(self, alert_trigger: AlertTrigger) -> Optional[Dict[str, Any]]:
        """Generate trading signal from alert trigger."""
        # Check for custom processor
        if alert_trigger.alert_type in self.signal_processors:
            return await self.signal_processors[alert_trigger.alert_type](alert_trigger)
        
        # Default signal generation
        signal = {
            'timestamp': alert_trigger.timestamp.isoformat(),
            'symbol': alert_trigger.symbol,
            'alert_type': alert_trigger.alert_type,
            'trigger_price': alert_trigger.trigger_price,
            'message': alert_trigger.message
        }
        
        # Generate action based on alert type
        if alert_trigger.alert_type in ['price_above', 'resistance_break', 'rsi_overbought']:
            signal.update({
                'action': 'SELL',
                'side': 'short',
                'quantity': 10  # Default small quantity for testing
            })
        elif alert_trigger.alert_type in ['price_below', 'support_break', 'rsi_oversold']:
            signal.update({
                'action': 'BUY',
                'side': 'long',
                'quantity': 10  # Default small quantity for testing
            })
        elif alert_trigger.alert_type == 'macd_bullish':
            signal.update({
                'action': 'BUY',
                'side': 'long',
                'quantity': 10
            })
        elif alert_trigger.alert_type == 'macd_bearish':
            signal.update({
                'action': 'SELL',
                'side': 'short',
                'quantity': 10
            })
        else:
            # For other alert types, just pass the information without action
            signal['action'] = 'NOTIFY'
        
        return signal
    
    async def get_all_positions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get positions from all connected bots."""
        positions = {}
        for bot_id, bot in self.bots.items():
            try:
                positions[bot_id] = await bot.get_positions()
            except Exception as e:
                logger.error(f"Error getting positions from {bot_id}: {e}")
                positions[bot_id] = []
        return positions
    
    async def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Get balances from all connected bots."""
        balances = {}
        for bot_id, bot in self.bots.items():
            try:
                balances[bot_id] = await bot.get_balance()
            except Exception as e:
                logger.error(f"Error getting balance from {bot_id}: {e}")
                balances[bot_id] = {}
        return balances
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all connected bots."""
        health = {}
        for bot_id, bot in self.bots.items():
            try:
                health[bot_id] = await bot.health_check()
            except Exception as e:
                logger.error(f"Error checking health of {bot_id}: {e}")
                health[bot_id] = False
        return health
    
    async def shutdown(self):
        """Shutdown all bot connections."""
        for bot_id, bot in self.bots.items():
            try:
                await bot.close()
                logger.info(f"Closed connection to {bot_id}")
            except Exception as e:
                logger.error(f"Error closing {bot_id}: {e}")
        
        self.bots.clear()
        logger.info("Trading bot connector shutdown complete")

