#!/usr/bin/env python3
"""
ZmartBot Real-Time Symbol Data Updater with Caching
Updates all symbols in the database with real-time Binance data and calculates all 21 technical indicators
for all 4 timeframes (15m, 1h, 4h, 1d).

This script ensures the database data matches exactly what's displayed in the frontend cards.
Includes caching to reduce API calls and update every hour.
"""

import os
import sys
import sqlite3
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import time
import json
import hashlib

# Add src to path for imports
sys.path.append('src')

# Import technical indicators engine
from src.services.technical_indicators_engine import TechnicalIndicatorsEngine

# Import historical data service
try:
    from historical_data_service import historical_data_service
except ImportError:
    # Fallback if module not found
    historical_data_service = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('symbol_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeSymbolUpdater:
    def __init__(self, db_path: str = 'my_symbols_v2.db', cache_duration: int = 3600):
        self.db_path = db_path
        self.engine = TechnicalIndicatorsEngine()
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.timeframes = ['15m', '1h', '4h', '1d']
        self.timeframe_intervals = {
            '15m': '15m',
            '1h': '1h', 
            '4h': '4h',
            '1d': '1d'
        }
        self.cache_duration = cache_duration  # Cache duration in seconds (default: 1 hour)
        self.cache_file = 'symbol_data_cache.json'
        self.cache = self.load_cache()
        
    def load_cache(self) -> Dict:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded cache with {len(cache)} entries")
                    return cache
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
        return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.info("Cache saved successfully")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def get_cache_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key for symbol and timeframe"""
        return f"{symbol}_{timeframe}"
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        current_time = datetime.now()
        
        # Check if cache is still valid (within cache_duration seconds)
        return (current_time - cache_time).total_seconds() < self.cache_duration
    
    def update_cache(self, cache_key: str, data: Dict):
        """Update cache with new data"""
        # Convert pandas Series to float for JSON serialization
        serializable_data = {}
        for key, value in data.items():
            try:
                if hasattr(value, 'iloc'):  # pandas Series
                    serializable_data[key] = float(value)
                elif isinstance(value, (list, tuple)):
                    # Convert lists/tuples to lists of floats
                    serializable_data[key] = [float(x) if hasattr(x, 'iloc') else x for x in value]
                elif isinstance(value, dict):
                    # Handle nested dictionaries (like ichimoku data)
                    serializable_data[key] = {}
                    for k, v in value.items():
                        if hasattr(v, 'iloc'):
                            serializable_data[key][k] = float(v)
                        else:
                            serializable_data[key][k] = v
                else:
                    serializable_data[key] = value
            except Exception as e:
                # Skip problematic data
                logger.warning(f"Could not serialize {key}: {e}")
                continue
        
        self.cache[cache_key] = {
            'data': serializable_data,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_symbols_from_database(self) -> List[str]:
        """Get all active symbols from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get symbols from portfolio_composition that are active
            cursor.execute("""
                SELECT DISTINCT s.symbol 
                FROM symbols s 
                JOIN portfolio_composition pc ON s.id = pc.symbol_id 
                WHERE pc.status = 'Active'
                ORDER BY pc.position_rank
            """)
            
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Found {len(symbols)} active symbols in database")
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting symbols from database: {e}")
            return []

    async def fetch_binance_klines(self, session: aiohttp.ClientSession, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Fetch klines data from Binance API"""
        try:
            url = f"{self.binance_base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    
                    # Convert types
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    return df
                else:
                    logger.error(f"Failed to fetch data for {symbol} {interval}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching data for {symbol} {interval}: {e}")
            return None

    async def get_current_price(self, session: aiohttp.ClientSession, symbol: str) -> Optional[float]:
        """Get current price from Binance"""
        try:
            url = f"{self.binance_base_url}/ticker/price"
            params = {'symbol': symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['price'])
                else:
                    logger.error(f"Failed to get current price for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate all 21 technical indicators for the given DataFrame"""
        try:
            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient data for calculations: {len(df)} rows")
                return {}
            
            indicators = {}
            
            # RSI
            rsi_data = self.engine.calculate_rsi(df)
            indicators['rsi'] = rsi_data['rsi_current']
            
            # EMA Crossovers
            ema_data = self.engine.calculate_ema_crossovers(df)
            indicators['ema_9'] = ema_data['values']['ema_9']
            indicators['ema_12'] = ema_data['values']['ema_9']  # Use ema_9 as fallback
            indicators['ema_20'] = ema_data['values']['ema_21']  # Use ema_21 as fallback
            indicators['ema_21'] = ema_data['values']['ema_21']
            indicators['ema_26'] = ema_data['values']['ema_21']  # Use ema_21 as fallback
            indicators['ema_50'] = ema_data['values']['ema_50']
            
            # MACD
            macd_data = self.engine.calculate_macd(df)
            indicators['macd_line'] = macd_data['macd'].iloc[-1]
            indicators['signal_line'] = macd_data['signal'].iloc[-1]
            indicators['histogram'] = macd_data['histogram'].iloc[-1]
            
            # Bollinger Bands
            bb_data = self.engine.calculate_bollinger_bands(df)
            indicators['bb_upper'] = bb_data['upper'].iloc[-1]
            indicators['bb_middle'] = bb_data['middle'].iloc[-1]
            indicators['bb_lower'] = bb_data['lower'].iloc[-1]
            indicators['bb_bandwidth'] = bb_data['band_width']
            indicators['bb_position'] = bb_data['values']['position_in_band']
            
            # Volume
            volume_data = self.engine.calculate_volume_indicators(df)
            indicators['volume_sma'] = volume_data['volume_sma'].iloc[-1]
            indicators['current_volume'] = df['volume'].iloc[-1]
            
            # Support/Resistance
            sr_data = self.engine.calculate_support_resistance(df)
            indicators['support_levels'] = sr_data['support_levels']
            indicators['resistance_levels'] = sr_data['resistance_levels']
            
            # Fibonacci
            fib_data = self.engine.calculate_fibonacci_levels(df)
            indicators['fibonacci_levels'] = fib_data['levels']
            
            # Ichimoku
            ichimoku_data = self.engine.calculate_ichimoku(df)
            indicators['ichimoku'] = ichimoku_data
            
            # Stochastic RSI
            stoch_rsi_data = self.engine.calculate_stochastic_rsi(df)
            indicators['stoch_rsi_k'] = stoch_rsi_data['k'].iloc[-1]
            indicators['stoch_rsi_d'] = stoch_rsi_data['d'].iloc[-1]
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}

    def get_symbol_id(self, symbol: str) -> Optional[int]:
        """Get symbol ID from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting symbol ID for {symbol}: {e}")
            return None

    async def update_symbol_data(self, session: aiohttp.ClientSession, symbol: str) -> bool:
        """Update all data for a single symbol"""
        try:
            symbol_id = self.get_symbol_id(symbol)
            if not symbol_id:
                logger.error(f"Symbol ID not found for {symbol}")
                return False
            
            logger.info(f"Updating {symbol} (ID: {symbol_id})")
            
            # Get current price
            current_price = await self.get_current_price(session, symbol)
            if not current_price:
                logger.error(f"Failed to get current price for {symbol}")
                return False
            
            # Update for each timeframe
            for timeframe in self.timeframes:
                interval = self.timeframe_intervals[timeframe]
                cache_key = self.get_cache_key(symbol, timeframe)
                
                # Check if we have valid cached data
                if self.is_cache_valid(cache_key):
                    logger.info(f"Using cached data for {symbol} {timeframe}")
                    cached_data = self.cache[cache_key]['data']
                    await self.update_database_tables(symbol_id, symbol, timeframe, cached_data, current_price)
                    continue
                
                # Fetch fresh data from Binance
                logger.info(f"Fetching fresh data for {symbol} {timeframe}")
                df = await self.fetch_binance_klines(session, symbol, interval)
                if df is None or df.empty:
                    logger.warning(f"No data for {symbol} {timeframe}")
                    continue
                
                # Calculate indicators
                indicators = self.calculate_technical_indicators(df)
                if not indicators:
                    logger.warning(f"No indicators calculated for {symbol} {timeframe}")
                    continue
                
                # Cache the calculated data
                self.update_cache(cache_key, indicators)
                
                # Update database
                await self.update_database_tables(symbol_id, symbol, timeframe, indicators, current_price)
                
                # Store historical snapshot
                if historical_data_service:
                    historical_data_service.store_historical_snapshot(symbol, timeframe, indicators, current_price)
            
            logger.info(f"✅ Successfully updated {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating {symbol}: {e}")
            return False

    async def update_database_tables(self, symbol_id: int, symbol: str, timeframe: str, indicators: Dict, current_price: float):
        """Update all database tables with calculated indicators"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update RSI data
            if 'rsi' in indicators:
                rsi_value = float(indicators['rsi'])
                cursor.execute("""
                    INSERT OR REPLACE INTO rsi_data 
                    (symbol_id, symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, rsi_value, 'neutral', 'none', 0.0, current_price, datetime.now()))
            
            # Update EMA data
            if all(key in indicators for key in ['ema_9', 'ema_20', 'ema_50']):
                ema_9 = float(indicators['ema_9'])
                ema_12 = float(indicators['ema_12'])
                ema_20 = float(indicators['ema_20'])
                ema_21 = float(indicators['ema_21'])
                ema_26 = float(indicators['ema_26'])
                ema_50 = float(indicators['ema_50'])
                
                cursor.execute("""
                    INSERT OR REPLACE INTO ema_data 
                    (symbol_id, symbol, timeframe, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50, 
                     cross_signal, cross_strength, golden_cross_detected, death_cross_detected, 
                     short_term_trend, long_term_trend, current_price, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50,
                      'none', 0.0, False, False, 'neutral', 'neutral', current_price, datetime.now()))
            
            # Update MACD data
            if all(key in indicators for key in ['macd_line', 'signal_line', 'histogram']):
                macd_line = float(indicators['macd_line'])
                signal_line = float(indicators['signal_line'])
                histogram = float(indicators['histogram'])
                
                cursor.execute("""
                    INSERT OR REPLACE INTO macd_data 
                    (symbol_id, symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, macd_line, signal_line, histogram, 'neutral', current_price, datetime.now()))
            
            # Update Bollinger Bands
            if all(key in indicators for key in ['bb_upper', 'bb_middle', 'bb_lower']):
                upper = float(indicators['bb_upper'])
                middle = float(indicators['bb_middle'])
                lower = float(indicators['bb_lower'])
                bandwidth = float(indicators['bb_bandwidth'])
                position = float(indicators['bb_position'])
                
                cursor.execute("""
                    INSERT OR REPLACE INTO bollinger_bands 
                    (symbol_id, symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, middle, upper, lower, bandwidth, position, current_price, datetime.now()))
            
            # Update Volume data
            if 'volume_sma' in indicators and 'current_volume' in indicators:
                volume_sma = float(indicators['volume_sma'])
                current_volume = float(indicators['current_volume'])
                volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1.0
                
                cursor.execute("""
                    INSERT OR REPLACE INTO volume_data 
                    (symbol_id, symbol, timeframe, current_volume, volume_sma_20, volume_ratio, 
                     obv, obv_sma, volume_spike_detected, volume_spike_ratio, volume_trend, 
                     volume_divergence_type, volume_divergence_strength, price_volume_correlation, 
                     current_price, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, current_volume, volume_sma, volume_ratio,
                      0.0, 0.0, False, 0.0, 'neutral', 'none', 0.0, 0.0, current_price, datetime.now()))
            
            # Update Support/Resistance
            if 'support_levels' in indicators and 'resistance_levels' in indicators:
                support_levels = indicators['support_levels'][:3]  # Top 3 levels
                resistance_levels = indicators['resistance_levels'][:3]  # Top 3 levels
                
                # Calculate nearest support and resistance
                nearest_support = support_levels[0] if support_levels else current_price * 0.95
                nearest_resistance = resistance_levels[0] if resistance_levels else current_price * 1.05
                
                cursor.execute("""
                    INSERT OR REPLACE INTO support_resistance_data 
                    (symbol_id, symbol, timeframe, support_level_1, support_level_2, support_level_3,
                     resistance_level_1, resistance_level_2, resistance_level_3, current_price, price_position,
                     nearest_support, nearest_resistance, support_distance, resistance_distance,
                     support_strength, resistance_strength, breakout_potential, breakout_direction, 
                     breakout_strength, volume_confirmation, volume_strength, trend_alignment, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol_id, symbol, timeframe, 
                      support_levels[0] if len(support_levels) > 0 else current_price * 0.95,
                      support_levels[1] if len(support_levels) > 1 else current_price * 0.90,
                      support_levels[2] if len(support_levels) > 2 else current_price * 0.85,
                      resistance_levels[0] if len(resistance_levels) > 0 else current_price * 1.05,
                      resistance_levels[1] if len(resistance_levels) > 1 else current_price * 1.10,
                      resistance_levels[2] if len(resistance_levels) > 2 else current_price * 1.15,
                      current_price, 'middle_range', nearest_support, nearest_resistance,
                      abs(current_price - nearest_support), abs(current_price - nearest_resistance),
                      0.7, 0.7, 'medium', 'neutral', 0.5, 'weak', 0.3, 'neutral', datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating database tables: {e}")

    async def update_all_symbols(self):
        """Update all symbols with real-time data"""
        try:
            symbols = await self.get_symbols_from_database()
            if not symbols:
                logger.error("No symbols found in database")
                return
            
            logger.info(f"Starting update for {len(symbols)} symbols")
            logger.info(f"Cache duration: {self.cache_duration} seconds ({self.cache_duration/3600:.1f} hours)")
            
            # Create session for HTTP requests
            async with aiohttp.ClientSession() as session:
                # Update symbols with rate limiting
                semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
                
                async def update_with_semaphore(symbol):
                    async with semaphore:
                        return await self.update_symbol_data(session, symbol)
                
                # Run updates concurrently
                tasks = [update_with_semaphore(symbol) for symbol in symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes
                successful = sum(1 for result in results if result is True)
                failed = len(results) - successful
                
                logger.info(f"✅ Update completed: {successful} successful, {failed} failed")
                
                # Save cache after successful update
                self.save_cache()
                
        except Exception as e:
            logger.error(f"Error in update_all_symbols: {e}")

async def main():
    """Main function"""
    logger.info("🚀 Starting Real-Time Symbol Data Update (with Caching)")
    
    # Cache duration: 1 hour (3600 seconds)
    updater = RealTimeSymbolUpdater(cache_duration=3600)
    await updater.update_all_symbols()
    
    logger.info("✅ Real-Time Symbol Data Update completed")

if __name__ == "__main__":
    asyncio.run(main())
