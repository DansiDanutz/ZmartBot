#!/usr/bin/env python3
"""
Indicators Collector Service
Continuously collects real-time indicator data and screenshots for all symbols
Integrates with the main ZmartBot orchestration system
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import aiohttp
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from ..database.indicators_history_database import (
    IndicatorsHistoryDatabase, IndicatorSnapshot, get_indicators_database
)
from ..services.cryptometer_service import MultiTimeframeCryptometerSystem
from ..services.real_time_price_service import RealTimePriceService

logger = logging.getLogger(__name__)

class IndicatorsCollectorService:
    """Service for collecting and storing indicator snapshots"""
    
    def __init__(self):
        self.db = get_indicators_database()
        self.is_running = False
        self.collection_interval = 600  # 10 minutes (increased for stability)
        self.screenshot_interval = 1800  # 30 minutes (increased for stability)
        
        # Initialize services
        self.cryptometer_service = None
        self.price_service = None
        
        # Stability controls
        self.max_concurrent_requests = 3  # Limit concurrent API calls
        self.request_delay = 2.0  # Delay between requests
        self.max_errors_per_cycle = 5  # Stop if too many errors
        
        # Collection statistics
        self.stats = {
            'total_snapshots': 0,
            'total_screenshots': 0,
            'errors': 0,
            'last_collection': None,
            'collection_time_avg': 0.0,
            'cycle_errors': 0
        }
        
        logger.info("✅ Indicators Collector Service initialized with stability controls")
    
    async def initialize(self):
        """Initialize external services"""
        try:
            # Initialize Cryptometer service
            self.cryptometer_service = MultiTimeframeCryptometerSystem()
            
            # Initialize price service
            self.price_service = RealTimePriceService()
            
            logger.info("✅ External services initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing services: {e}")
    
    async def start(self):
        """Start continuous data collection"""
        if self.is_running:
            logger.warning("⚠️ Collector service already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting Indicators Collector Service...")
        
        # Initialize services
        await self.initialize()
        
        # Start collection tasks
        asyncio.create_task(self._collection_loop())
        asyncio.create_task(self._screenshot_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Indicators Collector Service started")
    
    async def stop(self):
        """Stop data collection"""
        self.is_running = False
        logger.info("🛑 Stopping Indicators Collector Service...")
    
    async def _collection_loop(self):
        """Main collection loop - runs every 10 minutes with improved stability"""
        while self.is_running:
            try:
                start_time = time.time()
                self.stats['cycle_errors'] = 0  # Reset cycle error count
                
                # Get current symbols from My Symbols
                symbols = await self._get_current_symbols()
                
                if symbols:
                    # Limit to first 5 symbols to prevent overload
                    symbols = symbols[:5]
                    logger.info(f"📊 Starting collection for {len(symbols)} symbols...")
                    
                    # Collect data with rate limiting (sequential, not parallel)
                    successful = 0
                    for i, symbol in enumerate(symbols):
                        if not self.is_running:  # Check if service was stopped
                            break
                            
                        if self.stats['cycle_errors'] >= self.max_errors_per_cycle:
                            logger.warning(f"⚠️ Too many errors in cycle, stopping collection")
                            break
                            
                        try:
                            result = await self._collect_symbol_data(symbol)
                            if result:
                                successful += 1
                            
                            # Add delay between requests to prevent overwhelming
                            if i < len(symbols) - 1:  # Don't delay after last symbol
                                await asyncio.sleep(self.request_delay)
                                
                        except Exception as e:
                            logger.error(f"❌ Error collecting {symbol}: {e}")
                            self.stats['cycle_errors'] += 1
                    
                    self.stats['total_snapshots'] += successful
                    
                    collection_time = time.time() - start_time
                    self.stats['collection_time_avg'] = (
                        self.stats['collection_time_avg'] * 0.9 + collection_time * 0.1
                    )
                    self.stats['last_collection'] = datetime.now()
                    
                    logger.info(f"✅ Collection complete: {successful}/{len(symbols)} symbols in {collection_time:.2f}s")
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in collection loop: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(120)  # Wait 2 minutes on error
    
    async def _screenshot_loop(self):
        """Screenshot collection loop - runs every 30 minutes with improved stability"""
        while self.is_running:
            try:
                # Get current symbols
                symbols = await self._get_current_symbols()
                
                if symbols:
                    # Limit to first 3 symbols for screenshots to prevent resource issues
                    symbols = symbols[:3]
                    logger.info(f"📸 Starting screenshot collection for {len(symbols)} symbols...")
                    
                    # Take screenshots with longer delays
                    for i, symbol in enumerate(symbols):
                        if not self.is_running:  # Check if service was stopped
                            break
                            
                        try:
                            success = await self._capture_indicator_screenshot(symbol)
                            if success:
                                self.stats['total_screenshots'] += 1
                            
                            # Longer delay between screenshots to prevent resource exhaustion
                            if i < len(symbols) - 1:
                                await asyncio.sleep(10)  # 10 second delay
                                
                        except Exception as e:
                            logger.error(f"❌ Error capturing screenshot for {symbol}: {e}")
                
                # Wait for next screenshot collection
                await asyncio.sleep(self.screenshot_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in screenshot loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _cleanup_loop(self):
        """Cleanup loop - runs daily"""
        while self.is_running:
            try:
                # Wait 24 hours
                await asyncio.sleep(24 * 60 * 60)
                
                # Cleanup old data (keep 30 days)
                self.db.cleanup_old_data(days_to_keep=30)
                
                logger.info("🧹 Daily cleanup completed")
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")
    
    async def _get_current_symbols(self) -> List[str]:
        """Get current symbols from My Symbols database"""
        try:
            # Make API call to get current symbols
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/api/futures-symbols/my-symbols/current') as response:
                    if response.status == 200:
                        data = await response.json()
                        symbols = data.get('portfolio', {}).get('symbols', [])
                        
                        # Add symbols to tracking database
                        for symbol in symbols:
                            self.db.add_symbol(symbol)
                        
                        return symbols
            
            # Fallback to database
            return self.db.get_tracked_symbols()
            
        except Exception as e:
            logger.error(f"❌ Error getting current symbols: {e}")
            # Return fallback symbols
            return ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
    
    async def _collect_symbol_data(self, symbol: str) -> bool:
        """Collect complete indicator data for a symbol"""
        try:
            timeframes = ['15m', '1h', '4h', '1d']
            
            for timeframe in timeframes:
                # Get technical indicators from Cryptometer
                technical_data = await self._get_technical_indicators(symbol, timeframe)
                
                # Get market data
                market_data = await self._get_market_data(symbol)
                
                # Create snapshot
                snapshot = IndicatorSnapshot(
                    id=None,  # Will be generated
                    symbol=symbol,
                    timestamp=datetime.now(),
                    timeframe=timeframe,
                    
                    # Technical indicators from Cryptometer
                    rsi=technical_data.get('rsi'),
                    rsi_14=technical_data.get('rsi_14'),
                    macd=technical_data.get('macd', {}).get('macd'),
                    macd_signal=technical_data.get('macd', {}).get('signal'),
                    macd_histogram=technical_data.get('macd', {}).get('histogram'),
                    ema_9=technical_data.get('ema_9'),
                    ema_21=technical_data.get('ema_21'),
                    ema_50=technical_data.get('ema_50'),
                    ema_200=technical_data.get('ema_200'),
                    sma_20=technical_data.get('sma_20'),
                    sma_50=technical_data.get('sma_50'),
                    bollinger_upper=technical_data.get('bollinger_bands', {}).get('upper'),
                    bollinger_middle=technical_data.get('bollinger_bands', {}).get('middle'),
                    bollinger_lower=technical_data.get('bollinger_bands', {}).get('lower'),
                    stochastic_k=technical_data.get('stochastic', {}).get('k'),
                    stochastic_d=technical_data.get('stochastic', {}).get('d'),
                    atr=technical_data.get('atr'),
                    adx=technical_data.get('adx'),
                    cci=technical_data.get('cci'),
                    williams_r=technical_data.get('williams_r'),
                    parabolic_sar=technical_data.get('parabolic_sar'),
                    
                    # Market data
                    price=market_data.get('price'),
                    volume=market_data.get('volume'),
                    volume_24h=market_data.get('volume_24h'),
                    market_cap=market_data.get('market_cap'),
                    
                    # Pattern analysis
                    trend_direction=technical_data.get('trend_direction'),
                    support_level=technical_data.get('support_level'),
                    resistance_level=technical_data.get('resistance_level'),
                    pattern_detected=technical_data.get('pattern_detected'),
                    signal_strength=technical_data.get('signal_strength'),
                    
                    # Metadata
                    data_source="cryptometer_real_time",
                    analysis_version="v2.0"
                )
                
                # Save snapshot to database
                success = self.db.save_snapshot(snapshot)
                
                if success:
                    logger.debug(f"✅ Saved {symbol} {timeframe} snapshot")
                else:
                    logger.warning(f"⚠️ Failed to save {symbol} {timeframe} snapshot")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error collecting data for {symbol}: {e}")
            return False
    
    async def _get_technical_indicators(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Get technical indicators from Cryptometer"""
        try:
            if self.cryptometer_service:
                # Use real Cryptometer service
                result = await self.cryptometer_service.analyze_multi_timeframe_symbol(symbol)
                if result and result.get('success'):
                    tf_data = result.get('data', {}).get('timeframes', {}).get(timeframe, {})
                    return tf_data.get('indicators', {})
            
            # Fallback to API call
            async with aiohttp.ClientSession() as session:
                url = f'http://localhost:8000/api/real-time/technical/{symbol}'
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting technical indicators for {symbol}: {e}")
            return {}
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data from price service"""
        try:
            # Use real-time price service
            if self.price_service:
                price_data = await self.price_service.get_real_time_price(symbol)
                if price_data:
                    return price_data
            
            # Fallback to API call
            async with aiohttp.ClientSession() as session:
                url = f'http://localhost:8000/api/real-time/prices?symbols={symbol}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get(symbol, {})
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting market data for {symbol}: {e}")
            return {}
    
    async def _capture_indicator_screenshot(self, symbol: str) -> bool:
        """Capture indicator visualization screenshot"""
        try:
            # Get recent snapshots for visualization
            snapshots = self.db.get_snapshots(symbol=symbol, timeframe='1h', limit=50)
            
            if len(snapshots) < 10:
                logger.warning(f"⚠️ Not enough data for {symbol} screenshot")
                return False
            
            # Create indicator visualization
            screenshot_data = self._create_indicator_chart(symbol, snapshots)
            
            if screenshot_data:
                # Save screenshot
                screenshot_path, screenshot_base64 = self.db.save_screenshot(
                    symbol=symbol,
                    timeframe='1h',
                    screenshot_data=screenshot_data,
                    metadata={
                        'chart_type': 'technical_indicators',
                        'data_points': len(snapshots),
                        'timeframe': '1h',
                        'generated_at': datetime.now().isoformat()
                    }
                )
                
                # Update latest snapshot with screenshot
                if snapshots and screenshot_path:
                    latest_snapshot = snapshots[0]
                    latest_snapshot.screenshot_path = screenshot_path
                    latest_snapshot.screenshot_base64 = screenshot_base64[:1000]  # Truncate for storage
                    latest_snapshot.screenshot_metadata = {
                        'chart_type': 'technical_indicators',
                        'data_points': len(snapshots)
                    }
                    
                    self.db.save_snapshot(latest_snapshot)
                
                self.stats['total_screenshots'] += 1
                logger.info(f"📸 Captured screenshot for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error capturing screenshot for {symbol}: {e}")
            return False
    
    def _create_indicator_chart(self, symbol: str, snapshots: List[IndicatorSnapshot]) -> bytes:
        """Create technical indicators chart"""
        try:
            # Prepare data
            timestamps = [s.timestamp for s in reversed(snapshots)]
            prices = [s.price for s in reversed(snapshots) if s.price]
            rsi_values = [s.rsi for s in reversed(snapshots) if s.rsi]
            macd_values = [s.macd for s in reversed(snapshots) if s.macd]
            
            if not prices or len(prices) < 5:
                return None
            
            # Create figure with subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), 
                                                gridspec_kw={'height_ratios': [3, 1, 1]})
            
            # Plot 1: Price with moving averages
            ax1.plot(timestamps[:len(prices)], prices, label='Price', color='#00ff88', linewidth=2)
            ax1.set_title(f'{symbol} - Technical Indicators', fontsize=16, color='white')
            ax1.set_ylabel('Price (USDT)', color='white')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot 2: RSI
            if rsi_values and len(rsi_values) > 1:
                ax2.plot(timestamps[:len(rsi_values)], rsi_values, label='RSI', color='#ff6b35', linewidth=2)
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7)
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7)
                ax2.set_ylabel('RSI', color='white')
                ax2.set_ylim(0, 100)
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
            # Plot 3: MACD
            if macd_values and len(macd_values) > 1:
                ax3.plot(timestamps[:len(macd_values)], macd_values, label='MACD', color='#3498db', linewidth=2)
                ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.7)
                ax3.set_ylabel('MACD', color='white')
                ax3.grid(True, alpha=0.3)
                ax3.legend()
            
            # Style the chart
            fig.patch.set_facecolor('#1a1a1a')
            for ax in [ax1, ax2, ax3]:
                ax.set_facecolor('#2d2d2d')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
            
            # Format x-axis
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax3.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
            buffer.seek(0)
            screenshot_data = buffer.getvalue()
            buffer.close()
            
            plt.close(fig)
            
            return screenshot_data
            
        except Exception as e:
            logger.error(f"❌ Error creating chart for {symbol}: {e}")
            return None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        db_stats = self.db.get_database_stats()
        
        return {
            'is_running': self.is_running,
            'collection_interval_minutes': self.collection_interval // 60,
            'screenshot_interval_minutes': self.screenshot_interval // 60,
            'stats': self.stats,
            'database': db_stats
        }

# Global service instance
indicators_collector = IndicatorsCollectorService()

async def get_indicators_collector() -> IndicatorsCollectorService:
    """Get the global indicators collector service"""
    return indicators_collector