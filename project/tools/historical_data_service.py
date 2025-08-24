#!/usr/bin/env python3
"""
Historical Data Service
Stores hourly snapshots of all symbol data in HistoryMySymbols database
for pattern analysis and historical trend analysis.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class HistoricalDataService:
    def __init__(self, history_db_path: str = 'HistoryMySymbols.db', current_db_path: str = 'my_symbols_v2.db'):
        self.history_db_path = history_db_path
        self.current_db_path = current_db_path
        
    def store_historical_snapshot(self, symbol: str, timeframe: str, indicators: Dict, current_price: float):
        """Store a complete historical snapshot for a symbol and timeframe"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            snapshot_time = datetime.now()
            
            # Store RSI data
            if 'rsi' in indicators:
                cursor.execute("""
                    INSERT INTO historical_rsi_data 
                    (symbol, timeframe, rsi_value, signal_status, divergence_type, divergence_strength, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, float(indicators['rsi']), 'neutral', 'none', 0.0, current_price, snapshot_time))
            
            # Store EMA data
            if all(key in indicators for key in ['ema_9', 'ema_20', 'ema_50']):
                cursor.execute("""
                    INSERT INTO historical_ema_data 
                    (symbol, timeframe, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50, 
                     cross_signal, cross_strength, golden_cross_detected, death_cross_detected,
                     short_term_trend, long_term_trend, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(indicators['ema_9']), float(indicators['ema_12']), 
                      float(indicators['ema_20']), float(indicators['ema_21']), 
                      float(indicators['ema_26']), float(indicators['ema_50']),
                      'none', 0.0, False, False, 'neutral', 'neutral', current_price, snapshot_time))
            
            # Store MACD data
            if all(key in indicators for key in ['macd_line', 'signal_line', 'histogram']):
                cursor.execute("""
                    INSERT INTO historical_macd_data 
                    (symbol, timeframe, macd_line, signal_line, histogram, signal_status, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(indicators['macd_line']), float(indicators['signal_line']), 
                      float(indicators['histogram']), 'neutral', current_price, snapshot_time))
            
            # Store Bollinger Bands data
            if all(key in indicators for key in ['bb_upper', 'bb_middle', 'bb_lower']):
                cursor.execute("""
                    INSERT INTO historical_bollinger_bands 
                    (symbol, timeframe, sma, upper_band, lower_band, bandwidth, position, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(indicators['bb_middle']), float(indicators['bb_upper']), 
                      float(indicators['bb_lower']), float(indicators['bb_bandwidth']), 
                      float(indicators['bb_position']), current_price, snapshot_time))
            
            # Store Volume data
            if 'volume_sma' in indicators and 'current_volume' in indicators:
                volume_ratio = float(indicators['current_volume']) / float(indicators['volume_sma']) if float(indicators['volume_sma']) > 0 else 1.0
                cursor.execute("""
                    INSERT INTO historical_volume_data 
                    (symbol, timeframe, current_volume, volume_sma_20, volume_ratio, obv, obv_sma,
                     volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type,
                     volume_divergence_strength, price_volume_correlation, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(indicators['current_volume']), float(indicators['volume_sma']), volume_ratio,
                      0.0, 0.0, False, 0.0, 'neutral', 'none', 0.0, 0.0, current_price, snapshot_time))
            
            # Store Support/Resistance data
            if 'support_levels' in indicators and 'resistance_levels' in indicators:
                support_levels = indicators['support_levels'][:3]
                resistance_levels = indicators['resistance_levels'][:3]
                nearest_support = support_levels[0] if support_levels else current_price * 0.95
                nearest_resistance = resistance_levels[0] if resistance_levels else current_price * 1.05
                
                cursor.execute("""
                    INSERT INTO historical_support_resistance_data 
                    (symbol, timeframe, support_level_1, support_level_2, support_level_3,
                     resistance_level_1, resistance_level_2, resistance_level_3, current_price, price_position,
                     nearest_support, nearest_resistance, support_distance, resistance_distance,
                     support_strength, resistance_strength, breakout_potential, breakout_direction,
                     breakout_strength, volume_confirmation, volume_strength, trend_alignment, snapshot_timestamp, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      support_levels[0] if len(support_levels) > 0 else current_price * 0.95,
                      support_levels[1] if len(support_levels) > 1 else current_price * 0.90,
                      support_levels[2] if len(support_levels) > 2 else current_price * 0.85,
                      resistance_levels[0] if len(resistance_levels) > 0 else current_price * 1.05,
                      resistance_levels[1] if len(resistance_levels) > 1 else current_price * 1.10,
                      resistance_levels[2] if len(resistance_levels) > 2 else current_price * 1.15,
                      current_price, 'middle_range', nearest_support, nearest_resistance,
                      abs(current_price - nearest_support), abs(current_price - nearest_resistance),
                      0.7, 0.7, 'medium', 'neutral', 0.5, 'weak', 0.3, 'neutral', snapshot_time, snapshot_time))
            
            # Store Fibonacci data
            if 'fibonacci_levels' in indicators:
                fib_levels = indicators['fibonacci_levels']
                cursor.execute("""
                    INSERT INTO historical_fibonacci_data 
                    (symbol, timeframe, fib_0, fib_236, fib_382, fib_500, fib_618, fib_786, fib_1000, fib_1618, fib_2618, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(fib_levels.get('0.0', current_price * 1.05)),
                      float(fib_levels.get('0.236', current_price * 1.02)),
                      float(fib_levels.get('0.382', current_price * 1.01)),
                      float(fib_levels.get('0.500', current_price)),
                      float(fib_levels.get('0.618', current_price * 0.99)),
                      float(fib_levels.get('0.786', current_price * 0.98)),
                      float(fib_levels.get('1.000', current_price * 0.95)),
                      float(fib_levels.get('1.618', current_price * 0.92)),
                      float(fib_levels.get('2.618', current_price * 0.88)),
                      current_price, snapshot_time))
            
            # Store Stochastic RSI data
            if all(key in indicators for key in ['stoch_rsi_k', 'stoch_rsi_d']):
                cursor.execute("""
                    INSERT INTO historical_stoch_rsi_data 
                    (symbol, timeframe, stoch_rsi_k, stoch_rsi_d, signal_status, current_price, snapshot_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, 
                      float(indicators['stoch_rsi_k']), float(indicators['stoch_rsi_d']), 
                      'neutral', current_price, snapshot_time))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored historical snapshot for {symbol} {timeframe}")
            
        except Exception as e:
            logger.error(f"Error storing historical snapshot for {symbol} {timeframe}: {e}")
    
    def get_historical_data(self, symbol: str, timeframe: str, hours_back: int = 24) -> Dict:
        """Get historical data for a symbol and timeframe for the last N hours"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            
            # Calculate the cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Get RSI data
            rsi_data = pd.read_sql_query("""
                SELECT * FROM historical_rsi_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get EMA data
            ema_data = pd.read_sql_query("""
                SELECT * FROM historical_ema_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get MACD data
            macd_data = pd.read_sql_query("""
                SELECT * FROM historical_macd_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Bollinger Bands data
            bb_data = pd.read_sql_query("""
                SELECT * FROM historical_bollinger_bands 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Volume data
            volume_data = pd.read_sql_query("""
                SELECT * FROM historical_volume_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Support/Resistance data
            sr_data = pd.read_sql_query("""
                SELECT * FROM historical_support_resistance_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Fibonacci data
            fib_data = pd.read_sql_query("""
                SELECT * FROM historical_fibonacci_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Stochastic RSI data
            stoch_data = pd.read_sql_query("""
                SELECT * FROM historical_stoch_rsi_data 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            # Get Pattern Summary data
            pattern_data = pd.read_sql_query("""
                SELECT * FROM historical_pattern_summary 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            conn.close()
            
            return {
                'rsi_data': rsi_data,
                'ema_data': ema_data,
                'macd_data': macd_data,
                'bollinger_bands': bb_data,
                'volume_data': volume_data,
                'support_resistance': sr_data,
                'fibonacci_data': fib_data,
                'stoch_rsi_data': stoch_data,
                'pattern_data': pattern_data
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} {timeframe}: {e}")
            return {}
    
    def get_pattern_analysis_data(self, symbol: str, timeframe: str, days_back: int = 7) -> pd.DataFrame:
        """Get pattern analysis data for a symbol and timeframe"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            
            # Calculate the cutoff time
            cutoff_time = datetime.now() - timedelta(days=days_back)
            
            # Get pattern summary data
            pattern_data = pd.read_sql_query("""
                SELECT * FROM historical_pattern_summary 
                WHERE symbol = ? AND timeframe = ? AND snapshot_timestamp >= ?
                ORDER BY snapshot_timestamp DESC
            """, conn, params=(symbol, timeframe, cutoff_time))
            
            conn.close()
            return pattern_data
            
        except Exception as e:
            logger.error(f"Error getting pattern analysis data for {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up historical data older than specified days"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old data from all tables
            tables = [
                'historical_rsi_data',
                'historical_ema_data', 
                'historical_macd_data',
                'historical_bollinger_bands',
                'historical_volume_data',
                'historical_support_resistance_data',
                'historical_fibonacci_data',
                'historical_stoch_rsi_data',
                'historical_price_data',
                'historical_pattern_summary'
            ]
            
            deleted_count = 0
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE snapshot_timestamp < ?", (cutoff_time,))
                deleted_count += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ Cleaned up {deleted_count} old historical records (older than {days_to_keep} days)")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the historical database"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            tables = [
                'historical_rsi_data',
                'historical_ema_data', 
                'historical_macd_data',
                'historical_bollinger_bands',
                'historical_volume_data',
                'historical_support_resistance_data',
                'historical_fibonacci_data',
                'historical_stoch_rsi_data',
                'historical_price_data',
                'historical_pattern_summary'
            ]
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            # Get date range
            cursor.execute("SELECT MIN(snapshot_timestamp), MAX(snapshot_timestamp) FROM historical_rsi_data")
            date_range = cursor.fetchone()
            
            conn.close()
            
            return {
                'table_counts': stats,
                'date_range': date_range,
                'total_records': sum(stats.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Global instance
historical_data_service = HistoricalDataService()
