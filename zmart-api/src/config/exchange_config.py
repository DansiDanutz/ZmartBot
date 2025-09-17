"""
Exchange Configuration - Defines which exchange to use for what purpose
BINANCE: Default for all price data, market data, and analysis
KUCOIN: Default for all trading execution
"""

from enum import Enum
from typing import Dict, Any

class ExchangePurpose(Enum):
    """Purpose of exchange usage"""
    PRICE_DATA = "price_data"
    MARKET_DATA = "market_data"
    TECHNICAL_ANALYSIS = "technical_analysis"
    HISTORICAL_DATA = "historical_data"
    TRADING_EXECUTION = "trading_execution"
    POSITION_MANAGEMENT = "position_management"
    ORDER_MANAGEMENT = "order_management"

class ExchangeConfig:
    """
    Exchange configuration defining which exchange to use for what
    
    IMPORTANT:
    - Binance is DEFAULT for everything except trading
    - KuCoin is DEFAULT for trading execution only
    """
    
    # Default exchange for each purpose
    EXCHANGE_DEFAULTS = {
        ExchangePurpose.PRICE_DATA: "binance",           # Binance for real-time prices
        ExchangePurpose.MARKET_DATA: "binance",          # Binance for market data
        ExchangePurpose.TECHNICAL_ANALYSIS: "binance",   # Binance for technical indicators
        ExchangePurpose.HISTORICAL_DATA: "binance",      # Binance for historical data
        ExchangePurpose.TRADING_EXECUTION: "kucoin",     # KuCoin for placing orders
        ExchangePurpose.POSITION_MANAGEMENT: "kucoin",   # KuCoin for managing positions
        ExchangePurpose.ORDER_MANAGEMENT: "kucoin",      # KuCoin for managing orders
    }
    
    # Priority order for fallback (if primary fails)
    EXCHANGE_PRIORITY = {
        "price_data": ["binance", "kucoin", "cryptometer"],
        "market_data": ["binance", "kucoin", "cryptometer"],
        "technical_analysis": ["binance", "cryptometer", "kucoin"],
        "historical_data": ["binance", "kucoin"],
        "trading_execution": ["kucoin"],  # No fallback for trading - KuCoin only
        "position_management": ["kucoin"],  # No fallback - KuCoin only
        "order_management": ["kucoin"],  # No fallback - KuCoin only
    }
    
    @classmethod
    def get_default_exchange(cls, purpose: ExchangePurpose) -> str:
        """Get the default exchange for a specific purpose"""
        return cls.EXCHANGE_DEFAULTS.get(purpose, "binance")
    
    @classmethod
    def get_exchange_priority(cls, purpose: str) -> list:
        """Get the priority order of exchanges for a purpose"""
        return cls.EXCHANGE_PRIORITY.get(purpose, ["binance", "kucoin"])
    
    @classmethod
    def is_trading_purpose(cls, purpose: ExchangePurpose) -> bool:
        """Check if the purpose is related to trading"""
        trading_purposes = [
            ExchangePurpose.TRADING_EXECUTION,
            ExchangePurpose.POSITION_MANAGEMENT,
            ExchangePurpose.ORDER_MANAGEMENT
        ]
        return purpose in trading_purposes
    
    @classmethod
    def get_exchange_config(cls) -> Dict[str, Any]:
        """Get complete exchange configuration"""
        return {
            "price_data": {
                "default": "binance",
                "fallback": ["kucoin", "cryptometer"],
                "description": "Real-time price data"
            },
            "market_data": {
                "default": "binance",
                "fallback": ["kucoin", "cryptometer"],
                "description": "Market statistics and volume"
            },
            "technical_analysis": {
                "default": "binance",
                "fallback": ["cryptometer"],
                "description": "Technical indicators and analysis"
            },
            "historical_data": {
                "default": "binance",
                "fallback": ["kucoin"],
                "description": "Historical price data and klines"
            },
            "trading": {
                "default": "kucoin",
                "fallback": [],
                "description": "Order execution and trading"
            },
            "positions": {
                "default": "kucoin",
                "fallback": [],
                "description": "Position management"
            }
        }

# Global instance
exchange_config = ExchangeConfig()