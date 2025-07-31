#!/usr/bin/env python3
"""
Advanced Charting Service with TradingView Integration
Provides comprehensive charting capabilities for the trading platform
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

@dataclass
class ChartData:
    """Standardized chart data format"""
    symbol: str
    timeframe: str
    data: List[Dict[str, Any]]
    indicators: Dict[str, Any]
    signals: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class TradingViewWidget:
    """TradingView widget configuration"""
    symbol: str
    interval: str
    theme: str = "dark"
    style: str = "1"
    locale: str = "en"
    toolbar_bg: str = "#f1f3f6"
    enable_publishing: bool = False
    hide_top_toolbar: bool = False
    hide_legend: bool = False
    save_image: bool = False
    container_id: str = "tradingview_widget"

class TradingViewService:
    """TradingView integration service"""
    
    def __init__(self):
        self.base_url = "https://www.tradingview.com"
        self.widget_url = "https://s3.tradingview.com/tv.js"
        self.supported_timeframes = {
            "1m": "1",
            "5m": "5", 
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "4h": "240",
            "1d": "1D",
            "1w": "1W",
            "1M": "1M"
        }
        
        self.supported_symbols = {
            "BTCUSDT": "BINANCE:BTCUSDT",
            "ETHUSDT": "BINANCE:ETHUSDT", 
            "ADAUSDT": "BINANCE:ADAUSDT",
            "DOTUSDT": "BINANCE:DOTUSDT",
            "LINKUSDT": "BINANCE:LINKUSDT",
            "LTCUSDT": "BINANCE:LTCUSDT",
            "XRPUSDT": "BINANCE:XRPUSDT",
            "BNBUSDT": "BINANCE:BNBUSDT",
            "SOLUSDT": "BINANCE:SOLUSDT",
            "MATICUSDT": "BINANCE:MATICUSDT"
        }
    
    def get_widget_config(self, symbol: str, interval: str = "1h", theme: str = "dark") -> Dict[str, Any]:
        """Get TradingView widget configuration"""
        try:
            # Map symbol to TradingView format
            tv_symbol = self.supported_symbols.get(symbol.upper(), f"BINANCE:{symbol.upper()}")
            
            # Map timeframe
            tv_interval = self.supported_timeframes.get(interval, "60")
            
            config = {
                "symbol": tv_symbol,
                "interval": tv_interval,
                "timezone": "Etc/UTC",
                "theme": theme,
                "style": "1",  # Candlestick
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": False,
                "hide_top_toolbar": False,
                "hide_legend": False,
                "save_image": False,
                "container_id": "tradingview_widget",
                "studies": [
                    "RSI@tv-basicstudies",
                    "MACD@tv-basicstudies",
                    "BB@tv-basicstudies"
                ],
                "show_popup_button": True,
                "popup_width": "1000",
                "popup_height": "650"
            }
            
            return config
            
        except Exception as e:
            logger.error(f"❌ Error creating widget config: {e}")
            return {}
    
    def generate_widget_html(self, symbol: str, interval: str = "1h", theme: str = "dark") -> str:
        """Generate TradingView widget HTML"""
        try:
            config = self.get_widget_config(symbol, interval, theme)
            
            html = f"""
            <div class="tradingview-widget-container">
                <div id="{config['container_id']}"></div>
                <script type="text/javascript" src="{self.widget_url}"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "width": "100%",
                    "height": "600",
                    "symbol": "{config['symbol']}",
                    "interval": "{config['interval']}",
                    "timezone": "{config['timezone']}",
                    "theme": "{config['theme']}",
                    "style": "{config['style']}",
                    "locale": "{config['locale']}",
                    "toolbar_bg": "{config['toolbar_bg']}",
                    "enable_publishing": {str(config['enable_publishing']).lower()},
                    "hide_top_toolbar": {str(config['hide_top_toolbar']).lower()},
                    "hide_legend": {str(config['hide_legend']).lower()},
                    "save_image": {str(config['save_image']).lower()},
                    "container_id": "{config['container_id']}",
                    "studies": {json.dumps(config['studies'])},
                    "show_popup_button": {str(config['show_popup_button']).lower()},
                    "popup_width": "{config['popup_width']}",
                    "popup_height": "{config['popup_height']}"
                }});
                </script>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Error generating widget HTML: {e}")
            return f"<div>Error loading chart for {symbol}</div>"
    
    def get_advanced_widget(self, symbol: str, interval: str = "1h", theme: str = "dark", 
                           indicators: Optional[List[str]] = None, studies: Optional[List[str]] = None) -> str:
        """Generate advanced TradingView widget with custom indicators"""
        try:
            config = self.get_widget_config(symbol, interval, theme)
            
            # Add custom indicators
            if indicators:
                config['studies'].extend(indicators)
            
            # Add custom studies
            if studies:
                config['studies'].extend(studies)
            
            # Generate advanced HTML with custom styling
            html = f"""
            <div class="tradingview-widget-container" style="height: 600px; width: 100%;">
                <div id="{config['container_id']}" style="height: 100%; width: 100%;"></div>
                <script type="text/javascript" src="{self.widget_url}"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "width": "100%",
                    "height": "100%",
                    "symbol": "{config['symbol']}",
                    "interval": "{config['interval']}",
                    "timezone": "{config['timezone']}",
                    "theme": "{config['theme']}",
                    "style": "{config['style']}",
                    "locale": "{config['locale']}",
                    "toolbar_bg": "{config['toolbar_bg']}",
                    "enable_publishing": {str(config['enable_publishing']).lower()},
                    "hide_top_toolbar": {str(config['hide_top_toolbar']).lower()},
                    "hide_legend": {str(config['hide_legend']).lower()},
                    "save_image": {str(config['save_image']).lower()},
                    "container_id": "{config['container_id']}",
                    "studies": {json.dumps(config['studies'])},
                    "show_popup_button": {str(config['show_popup_button']).lower()},
                    "popup_width": "{config['popup_width']}",
                    "popup_height": "{config['popup_height']}",
                    "withdateranges": true,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": true,
                    "details": true,
                    "hotlist": true,
                    "calendar": true,
                    "support_host": "https://www.tradingview.com"
                }});
                </script>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Error generating advanced widget: {e}")
            return f"<div>Error loading advanced chart for {symbol}</div>"

class ChartingService:
    """Comprehensive charting service"""
    
    def __init__(self):
        self.tradingview = TradingViewService()
        self.chart_cache: Dict[str, ChartData] = {}
        self.cache_duration = timedelta(minutes=5)
    
    def get_basic_chart(self, symbol: str, interval: str = "1h", theme: str = "dark") -> str:
        """Get basic TradingView chart"""
        try:
            return self.tradingview.generate_widget_html(symbol, interval, theme)
        except Exception as e:
            logger.error(f"❌ Error getting basic chart: {e}")
            return f"<div>Error loading chart for {symbol}</div>"
    
    def get_advanced_chart(self, symbol: str, interval: str = "1h", theme: str = "dark",
                          indicators: Optional[List[str]] = None, studies: Optional[List[str]] = None) -> str:
        """Get advanced TradingView chart with custom indicators"""
        try:
            return self.tradingview.get_advanced_widget(symbol, interval, theme, indicators, studies)
        except Exception as e:
            logger.error(f"❌ Error getting advanced chart: {e}")
            return f"<div>Error loading advanced chart for {symbol}</div>"
    
    def get_chart_data(self, symbol: str, interval: str = "1h") -> ChartData:
        """Get chart data with indicators and signals"""
        try:
            cache_key = f"{symbol}_{interval}"
            
            # Check cache
            if cache_key in self.chart_cache:
                cached_data = self.chart_cache[cache_key]
                if datetime.now() - cached_data.timestamp < self.cache_duration:
                    return cached_data
            
            # Generate new chart data
            chart_data = ChartData(
                symbol=symbol,
                timeframe=interval,
                data=[],  # Would be populated with actual market data
                indicators={
                    "rsi": 65.5,
                    "macd": {"macd": 0.5, "signal": 0.3, "histogram": 0.2},
                    "bollinger_bands": {"upper": 52000, "middle": 50000, "lower": 48000}
                },
                signals=[
                    {"type": "BUY", "confidence": 0.85, "timestamp": datetime.now()},
                    {"type": "SELL", "confidence": 0.72, "timestamp": datetime.now()}
                ],
                timestamp=datetime.now()
            )
            
            # Cache the data
            self.chart_cache[cache_key] = chart_data
            
            return chart_data
            
        except Exception as e:
            logger.error(f"❌ Error getting chart data: {e}")
            return ChartData(
                symbol=symbol,
                timeframe=interval,
                data=[],
                indicators={},
                signals=[],
                timestamp=datetime.now()
            )
    
    def get_multi_timeframe_charts(self, symbol: str, timeframes: Optional[List[str]] = None) -> Dict[str, str]:
        """Get multiple timeframe charts for a symbol"""
        try:
            if timeframes is None:
                timeframes = ["5m", "1h", "4h", "1d"]
            
            charts = {}
            for timeframe in timeframes:
                charts[timeframe] = self.get_basic_chart(symbol, timeframe)
            
            return charts
            
        except Exception as e:
            logger.error(f"❌ Error getting multi-timeframe charts: {e}")
            return {}
    
    def get_portfolio_charts(self, symbols: List[str], interval: str = "1h") -> Dict[str, str]:
        """Get charts for multiple symbols in portfolio"""
        try:
            charts = {}
            for symbol in symbols:
                charts[symbol] = self.get_basic_chart(symbol, interval)
            
            return charts
            
        except Exception as e:
            logger.error(f"❌ Error getting portfolio charts: {e}")
            return {}
    
    def get_technical_analysis_chart(self, symbol: str, indicators: Optional[List[str]] = None) -> str:
        """Get chart with technical analysis indicators"""
        try:
            if indicators is None:
                indicators = [
                    "RSI@tv-basicstudies",
                    "MACD@tv-basicstudies", 
                    "BB@tv-basicstudies",
                    "Stochastic@tv-basicstudies",
                    "ATR@tv-basicstudies"
                ]
            else:
                indicators = indicators or []
            
            return self.get_advanced_chart(symbol, "1h", "dark", indicators)
            
        except Exception as e:
            logger.error(f"❌ Error getting technical analysis chart: {e}")
            return f"<div>Error loading technical analysis chart for {symbol}</div>"
    
    def get_signal_chart(self, symbol: str, signals: Optional[List[Dict[str, Any]]] = None) -> str:
        """Get chart with trading signals overlay"""
        try:
            # Add signal studies
            signal_studies = [
                "RSI@tv-basicstudies",
                "MACD@tv-basicstudies"
            ]
            
            if signals:
                # Add custom signal indicators
                signal_studies.extend([
                    "PivotPointsHighLow@tv-basicstudies",
                    "VolumeProfile@tv-basicstudies"
                ])
            
            return self.get_advanced_chart(symbol, "1h", "dark", signal_studies)
            
        except Exception as e:
            logger.error(f"❌ Error getting signal chart: {e}")
            return f"<div>Error loading signal chart for {symbol}</div>"

# Global charting service instance
charting_service: Optional[ChartingService] = None

def get_charting_service() -> ChartingService:
    """Get or create charting service instance"""
    global charting_service
    if charting_service is None:
        charting_service = ChartingService()
    return charting_service 