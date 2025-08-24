"""
Zmart Trading Bot Platform - Routes Module
API route definitions and handlers
"""

# Import all route modules
from . import health, auth, trading, signals, agents, monitoring, cryptometer, websocket, charting, explainability, analytics, my_symbols, binance, roadmap

__all__ = [
    'health',
    'auth', 
    'trading',
    'signals',
    'agents',
    'monitoring',
    'cryptometer',
    'websocket',
    'charting',
    'explainability',
    'analytics',
    'my_symbols',
    'binance',
    'roadmap'
] 