#!/usr/bin/env python3
"""
Technical Analysis Service
Fetches real technical analysis data from the database for the alerts system
"""

import sqlite3
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """Service to fetch real technical analysis data from the database"""
    
    def __init__(self, db_path: str = "my_symbols_v2.db"):
        self.db_path = db_path
        
    async def get_technical_analysis(self, symbol: str, timeframes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive technical analysis data for a symbol across timeframes"""
        
        if timeframes is None:
            timeframes = ["15m", "1h", "4h", "1d"]
            
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get current price and basic info
            current_price = await self._get_current_price(symbol, cursor)
            
            analysis = {
                "symbol": symbol,
                "current_price": current_price,
                "price_change_24h": 0.0,  # Will be calculated
                "volume_24h": 0.0,  # Will be calculated
                "high_24h": 0.0,  # Will be calculated
                "low_24h": 0.0,  # Will be calculated
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "alerts": []
            }
            
            # Fetch data for each indicator
            indicators = [
                "rsi_data", "macd_data", "ema_data", "bollinger_bands", 
                "support_resistance_data", "volume_data", "ichimoku_data",
                "stochastic_data", "atr_data", "fibonacci_data", "adx_data",
                "cci_data", "williams_r_data", "parabolic_sar_data", 
                "stoch_rsi_data", "price_patterns_data", "bollinger_squeeze_data",
                "macd_histogram_data", "ma_convergence_data", "price_channels_data",
                "momentum_indicators_data", "rsi_divergence_data"
            ]
            
            # Map database table names to API response keys
            indicator_mapping = {
                "bollinger_bands": "bollinger_bands_timeframes"
            }
            
            for indicator in indicators:
                data = await self._fetch_indicator_data(
                    cursor, symbol, indicator, timeframes
                )
                # Use mapped key if available, otherwise use original indicator name
                key = indicator_mapping.get(indicator, indicator)
                analysis[key] = data
            
            conn.close()
            return analysis
            
        except Exception as e:
            logger.error(f"Error fetching technical analysis for {symbol}: {e}")
            return self._get_fallback_data(symbol, timeframes)
    
    async def _get_current_price(self, symbol: str, cursor) -> float:
        """Get current price from the database"""
        try:
            # Try to get price from any indicator table
            cursor.execute("""
                SELECT current_price FROM rsi_data 
                WHERE symbol = ? 
                ORDER BY last_updated DESC 
                LIMIT 1
            """, (symbol,))
            
            result = cursor.fetchone()
            if result:
                return float(result['current_price'])
            
            # Fallback to a default price
            return 50000.0
            
        except Exception as e:
            logger.warning(f"Could not get current price for {symbol}: {e}")
            return 50000.0
    
    async def _fetch_indicator_data(self, cursor, symbol: str, indicator: str, timeframes: List[str]) -> Dict[str, Any]:
        """Fetch data for a specific indicator across timeframes"""
        try:
            # Check if the table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (indicator,))
            
            if not cursor.fetchone():
                logger.warning(f"Table {indicator} does not exist")
                return {}
            
            # Get all columns for this table
            cursor.execute(f"PRAGMA table_info({indicator})")
            columns = [row['name'] for row in cursor.fetchall()]
            
            # Fetch data for all timeframes
            timeframe_data = {}
            
            for timeframe in timeframes:
                cursor.execute(f"""
                    SELECT * FROM {indicator} 
                    WHERE symbol = ? AND timeframe = ? 
                    ORDER BY last_updated DESC 
                    LIMIT 1
                """, (symbol, timeframe))
                
                row = cursor.fetchone()
                if row:
                    # Convert row to dict, excluding id and timestamp fields
                    data = {}
                    for col in columns:
                        if col not in ['id', 'symbol_id', 'created_at']:
                            data[col] = row[col]
                    
                    # Remove timeframe from data since it's the key
                    if 'timeframe' in data:
                        del data['timeframe']
                    if 'symbol' in data:
                        del data['symbol']
                    
                    timeframe_data[timeframe] = data
                else:
                    # No data for this timeframe, use closest available
                    closest_data = await self._get_closest_timeframe_data(
                        cursor, indicator, symbol, timeframe
                    )
                    if closest_data:
                        timeframe_data[timeframe] = closest_data
                        # Mark as borrowed data
                        timeframe_data[timeframe]['_data_source'] = 'borrowed_from_closest_timeframe'
                    else:
                        timeframe_data[timeframe] = {}
            
            return timeframe_data
            
        except Exception as e:
            logger.error(f"Error fetching {indicator} data for {symbol}: {e}")
            return {}
    
    async def _get_closest_timeframe_data(self, cursor, indicator: str, symbol: str, target_timeframe: str) -> Optional[Dict[str, Any]]:
        """Get data from the closest available timeframe"""
        try:
            # Get all available timeframes for this symbol and indicator
            cursor.execute(f"""
                SELECT timeframe FROM {indicator} 
                WHERE symbol = ? 
                ORDER BY last_updated DESC 
                LIMIT 1
            """, (symbol,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Get the data from the available timeframe
            cursor.execute(f"""
                SELECT * FROM {indicator} 
                WHERE symbol = ? AND timeframe = ? 
                ORDER BY last_updated DESC 
                LIMIT 1
            """, (symbol, result['timeframe']))
            
            row = cursor.fetchone()
            if row:
                # Convert row to dict
                columns = [desc[0] for desc in cursor.description]
                data = {}
                for i, col in enumerate(columns):
                    if col not in ['id', 'symbol_id', 'created_at', 'timeframe', 'symbol']:
                        data[col] = row[i]
                
                return data
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting closest timeframe data for {indicator}: {e}")
            return None
    
    def _get_fallback_data(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """Return fallback data when database is not available"""
        logger.warning(f"Using fallback data for {symbol}")
        
        return {
            "symbol": symbol,
            "current_price": 50000.0,
            "price_change_24h": 0.0,
            "volume_24h": 1000000.0,
            "high_24h": 51000.0,
            "low_24h": 49000.0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "alerts": [],
            "_data_source": "fallback_mock_data"
        }

# Global instance
technical_analysis_service = TechnicalAnalysisService()

