"""
Symbol Alerts System
A comprehensive real-time symbol alerts system for trading bots.
"""

__version__ = "1.0.0"
__author__ = "Trading Bot Developer"
__email__ = "developer@tradingbot.com"

from .core.engine import AlertEngine
from .core.data_manager import DataManager
from .core.alert_processor import AlertProcessor
from .core.notification_manager import NotificationManager

__all__ = [
    "AlertEngine",
    "DataManager", 
    "AlertProcessor",
    "NotificationManager"
]

