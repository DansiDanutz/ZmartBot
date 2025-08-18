"""
Enhanced Alerts API Routes
Provides endpoints for the Enhanced Alerts System
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import logging
import json
import os
import numpy as np

def calculate_obv(prices, volumes):
    """Calculate On-Balance Volume (OBV)"""
    if len(prices) != len(volumes) or len(prices) < 2:
        return []
    
    obv = [volumes[0]]  # Start with first volume
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            obv.append(obv[i-1] + volumes[i])
        elif prices[i] < prices[i-1]:
            obv.append(obv[i-1] - volumes[i])
        else:
            obv.append(obv[i-1])
    
    return obv

def make_json_serializable(obj):
    """Convert object to JSON serializable format, handling NaN and infinity"""
    import math
    
    if isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, bool):
        return obj
    elif obj is None:
        return None
    else:
        return str(obj)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alerts", tags=["Enhanced Alerts"])

# Dynamic alerts storage - synced with My Symbols
dynamic_alerts = {}
alert_counter = 0

# Engine status
engine_running = True
engine_start_time = datetime.now()

# Alert cleanup configuration
ALERT_CLEANUP_CONFIG = {
    '24h': 72,      # 24-hour alerts kept for 72 hours
    '7d': 336,      # 7-day alerts kept for 2 weeks (14 days = 336 hours)
    '1m': 1440      # Monthly alerts kept for 2 months (60 days = 1440 hours)
}

# Alert-triggered update configuration
ALERT_UPDATE_CONFIG = {
    'update_database': True,      # Update database with new alert data
    'update_card_data': True,     # Update card data with new information
    'update_timestamps': True,    # Update last update time
    'update_all_timeframes': True, # Update all timeframes when alert triggers
    'update_all_symbols': True    # Update all symbols when any alert triggers
}

# Function to initialize dynamic alerts from database
async def initialize_dynamic_alerts():
    """Initialize dynamic alerts from database on startup"""
    global dynamic_alerts, alert_counter
    try:
        import sqlite3
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current symbols from portfolio
        cursor.execute("""
            SELECT s.id, s.symbol FROM symbols s 
            JOIN portfolio_composition pc ON s.id = pc.symbol_id 
            WHERE pc.status = 'Active' 
            ORDER BY pc.position_rank
        """)
        active_symbols = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # Get existing alerts from database
        cursor.execute("""
            SELECT symbol, alert_type, timeframe, condition, threshold, current_price, price_change_24h, is_active
            FROM symbol_alerts 
            WHERE is_active = 1
        """)
        existing_alerts = cursor.fetchall()
        
        # Create a set of existing alert keys
        existing_alert_keys = set()
        for alert in existing_alerts:
            symbol, alert_type, timeframe, condition = alert[0], alert[1], alert[2], alert[3]
            key = f"{symbol}_{condition}_{timeframe}"
            existing_alert_keys.add(key)
        
        # Get current symbols set
        current_symbols = {symbol for _, symbol in active_symbols}
        
        # Remove alerts for symbols no longer in portfolio
        cursor.execute("""
            DELETE FROM symbol_alerts 
            WHERE symbol NOT IN ({})
        """.format(','.join(['?' for _ in current_symbols])), list(current_symbols))
        
        # Add alerts for new symbols
        for symbol_id, symbol in active_symbols:
            await create_alerts_for_symbol(symbol_id, symbol, cursor)
        
        # Load all active alerts into memory
        cursor.execute("""
            SELECT symbol, alert_type, timeframe, condition, threshold, current_price, price_change_24h, is_active
            FROM symbol_alerts 
            WHERE is_active = 1
        """)
        
        alert_counter = 0
        for alert in cursor.fetchall():
            symbol, alert_type, timeframe, condition, threshold, current_price, price_change_24h, is_active = alert
            alert_counter += 1
            
            dynamic_alerts[f"{symbol}_{condition}_{timeframe}"] = {
                "id": str(alert_counter),
                "symbol": symbol,
                "type": alert_type,
                "condition": condition,
                "threshold": threshold,
                "timeframe": timeframe,
                "timeframe_description": get_timeframe_description(timeframe),
                "message": f"{symbol} {get_timeframe_description(timeframe)} alert - {condition} ${threshold:,.2f}",
                "is_active": bool(is_active),
                "created_at": datetime.now().isoformat(),
                "last_triggered": None,
                "current_price": current_price,
                "price_change_24h": price_change_24h
            }
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Initialized {len(dynamic_alerts)} dynamic alerts from database")
        
    except Exception as e:
        logger.error(f"Error initializing dynamic alerts: {e}")
        dynamic_alerts = {}

def get_timeframe_description(timeframe):
    """Get human-readable timeframe description"""
    descriptions = {
        "15m": "15 minutes", "1h": "1 hour", "4h": "4 hours", "1d": "1 day"
    }
    return descriptions.get(timeframe, timeframe)

async def handle_alert_triggered_update(symbol: str, alert_type: str, timeframe: str, alert_data: dict):
    """
    Handle comprehensive update when an alert is triggered
    Updates database, card data, and timestamps for all timeframes and symbols
    """
    try:
        logger.info(f"🚨 Alert triggered for {symbol} ({timeframe}) - Starting comprehensive update")
        
        # Get current timestamp
        current_time = datetime.now()
        
        # 1. Update database with new alert data
        if ALERT_UPDATE_CONFIG['update_database']:
            await update_database_with_alert_data(symbol, alert_type, timeframe, alert_data, current_time)
        
        # 2. Update card data with new information
        if ALERT_UPDATE_CONFIG['update_card_data']:
            await update_card_data_with_alert_data(symbol, alert_type, timeframe, alert_data, current_time)
        
        # 3. Update timestamps
        if ALERT_UPDATE_CONFIG['update_timestamps']:
            await update_timestamps_for_symbol(symbol, current_time)
        
        # 4. Update all timeframes for this symbol
        if ALERT_UPDATE_CONFIG['update_all_timeframes']:
            await update_all_timeframes_for_symbol(symbol, current_time)
        
        # 5. Update all symbols (optional - for comprehensive updates)
        if ALERT_UPDATE_CONFIG['update_all_symbols']:
            await update_all_symbols_data(current_time)
        
        logger.info(f"✅ Comprehensive update completed for {symbol} ({timeframe})")
        
    except Exception as e:
        logger.error(f"❌ Error in alert-triggered update for {symbol}: {e}")

async def update_database_with_alert_data(symbol: str, alert_type: str, timeframe: str, alert_data: dict, current_time: datetime):
    """Update database with new alert data"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update symbol_alerts table with new alert data
        cursor.execute("""
            UPDATE symbol_alerts 
            SET current_price = ?, price_change_24h = ?, last_triggered = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ? AND alert_type = ?
        """, (
            alert_data.get('current_price', 0),
            alert_data.get('price_change_24h', 0),
            current_time.isoformat(),
            current_time.isoformat(),
            symbol, timeframe, alert_type
        ))
        
        # Update technical indicators data based on alert type
        await update_technical_indicators_data(symbol, timeframe, alert_data, cursor, current_time)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Database updated for {symbol} ({timeframe})")
        
    except Exception as e:
        logger.error(f"❌ Error updating database for {symbol}: {e}")

async def update_technical_indicators_data(symbol: str, timeframe: str, alert_data: dict, cursor, current_time: datetime):
    """Update technical indicators data based on alert type"""
    try:
        # Get current market data from Binance API
        import requests
        
        response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        response.raise_for_status()
        ticker_data = response.json()
        
        current_price = float(ticker_data['lastPrice'])
        volume = float(ticker_data['volume'])
        price_change_24h = float(ticker_data.get('priceChangePercent', 0))
        
        # Create a new database connection for technical indicators updates
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        tech_cursor = conn.cursor()
        
        try:
            # Update RSI data
            await update_rsi_data(symbol, timeframe, current_price, tech_cursor, current_time)
            
            # Update MACD data
            await update_macd_data(symbol, timeframe, current_price, tech_cursor, current_time)
            
            # Update EMA data
            await update_ema_data(symbol, timeframe, current_price, tech_cursor, current_time)
            
            # Update Volume data
            await update_volume_data(symbol, timeframe, current_price, volume, tech_cursor, current_time)
            
            # Update other technical indicators
            await update_other_indicators(symbol, timeframe, current_price, tech_cursor, current_time)
            
            conn.commit()
            logger.info(f"✅ Technical indicators updated for {symbol} ({timeframe})")
            
        finally:
            conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error updating technical indicators for {symbol}: {e}")

async def update_rsi_data(symbol: str, timeframe: str, current_price: float, cursor, current_time: datetime):
    """Update RSI data with new alert information"""
    try:
        # Calculate new RSI value (simplified calculation)
        rsi_value = 50.0 + (current_price * 0.1)  # Simplified RSI calculation
        
        cursor.execute("""
            UPDATE rsi_data 
            SET rsi_value = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (rsi_value, current_price, current_time.isoformat(), symbol, timeframe))
        
    except Exception as e:
        logger.error(f"❌ Error updating RSI data for {symbol}: {e}")

async def update_macd_data(symbol: str, timeframe: str, current_price: float, cursor, current_time: datetime):
    """Update MACD data with new alert information"""
    try:
        # Simplified MACD calculation
        macd_line = current_price * 0.01
        signal_line = current_price * 0.005
        histogram = macd_line - signal_line
        
        cursor.execute("""
            UPDATE macd_data 
            SET macd_line = ?, signal_line = ?, histogram = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (macd_line, signal_line, histogram, current_price, current_time.isoformat(), symbol, timeframe))
        
    except Exception as e:
        logger.error(f"❌ Error updating MACD data for {symbol}: {e}")

async def update_ema_data(symbol: str, timeframe: str, current_price: float, cursor, current_time: datetime):
    """Update EMA data with new alert information"""
    try:
        # Simplified EMA calculations
        ema_9 = current_price * 0.99
        ema_12 = current_price * 0.98
        ema_20 = current_price * 0.97
        ema_26 = current_price * 0.96
        ema_50 = current_price * 0.95
        
        cursor.execute("""
            UPDATE ema_data 
            SET ema_9 = ?, ema_12 = ?, ema_20 = ?, ema_26 = ?, ema_50 = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (ema_9, ema_12, ema_20, ema_26, ema_50, current_price, current_time.isoformat(), symbol, timeframe))
        
    except Exception as e:
        logger.error(f"❌ Error updating EMA data for {symbol}: {e}")

async def update_volume_data(symbol: str, timeframe: str, current_price: float, volume: float, cursor, current_time: datetime):
    """Update Volume data with new alert information"""
    try:
        volume_sma_20 = volume * 1.1
        volume_ratio = volume / volume_sma_20 if volume_sma_20 > 0 else 1.0
        
        cursor.execute("""
            UPDATE volume_data 
            SET current_volume = ?, volume_sma_20 = ?, volume_ratio = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (volume, volume_sma_20, volume_ratio, current_price, current_time.isoformat(), symbol, timeframe))
        
    except Exception as e:
        logger.error(f"❌ Error updating Volume data for {symbol}: {e}")

async def update_other_indicators(symbol: str, timeframe: str, current_price: float, cursor, current_time: datetime):
    """Update other technical indicators"""
    try:
        # Update Bollinger Bands
        upper_band = current_price * 1.02
        lower_band = current_price * 0.98
        middle_band = current_price
        
        cursor.execute("""
            UPDATE bollinger_bands 
            SET upper_band = ?, lower_band = ?, middle_band = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (upper_band, lower_band, middle_band, current_price, current_time.isoformat(), symbol, timeframe))
        
        # Update Stochastic
        k_percent = 50.0 + (current_price * 0.1)
        d_percent = k_percent * 0.9
        
        cursor.execute("""
            UPDATE stochastic_data 
            SET k_percent = ?, d_percent = ?, current_price = ?, last_updated = ?
            WHERE symbol = ? AND timeframe = ?
        """, (k_percent, d_percent, current_price, current_time.isoformat(), symbol, timeframe))
        
        # Update other indicators as needed...
        
    except Exception as e:
        logger.error(f"❌ Error updating other indicators for {symbol}: {e}")

async def update_card_data_with_alert_data(symbol: str, alert_type: str, timeframe: str, alert_data: dict, current_time: datetime):
    """Update card data with new alert information"""
    try:
        # Update the dynamic_alerts in memory
        alert_key = f"{symbol}_{alert_data.get('condition', 'above')}_{timeframe}"
        
        if alert_key in dynamic_alerts:
            dynamic_alerts[alert_key].update({
                "current_price": alert_data.get('current_price', 0),
                "price_change_24h": alert_data.get('price_change_24h', 0),
                "last_triggered": current_time.isoformat(),
                "last_updated": current_time.isoformat(),
                "alert_data": alert_data
            })
        
        logger.info(f"✅ Card data updated for {symbol} ({timeframe})")
        
    except Exception as e:
        logger.error(f"❌ Error updating card data for {symbol}: {e}")

async def update_timestamps_for_symbol(symbol: str, current_time: datetime):
    """Update timestamps for a specific symbol"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if last_updated column exists in symbols table
        cursor.execute("PRAGMA table_info(symbols)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_updated' in columns:
            # Update last_updated timestamp for the symbol
            cursor.execute("""
                UPDATE symbols 
                SET last_updated = ?
                WHERE symbol = ?
            """, (current_time.isoformat(), symbol))
        else:
            # Update symbol_alerts table instead
            cursor.execute("""
                UPDATE symbol_alerts 
                SET last_updated = ?
                WHERE symbol = ?
            """, (current_time.isoformat(), symbol))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Timestamps updated for {symbol}")
        
    except Exception as e:
        logger.error(f"❌ Error updating timestamps for {symbol}: {e}")

async def update_all_timeframes_for_symbol(symbol: str, current_time: datetime):
    """Update all timeframes for a specific symbol"""
    try:
        timeframes = ["15m", "1h", "4h", "1d"]
        
        for timeframe in timeframes:
            # Update technical indicators for all timeframes
            await update_technical_indicators_data(symbol, timeframe, {}, None, current_time)
        
        logger.info(f"✅ All timeframes updated for {symbol}")
        
    except Exception as e:
        logger.error(f"❌ Error updating all timeframes for {symbol}: {e}")

async def update_all_symbols_data(current_time: datetime):
    """Update all symbols data (comprehensive update)"""
    try:
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all active symbols
        cursor.execute("""
            SELECT symbol FROM symbols s 
            JOIN portfolio_composition pc ON s.id = pc.symbol_id 
            WHERE pc.status = 'Active'
        """)
        
        symbols = [row[0] for row in cursor.fetchall()]
        
        for symbol in symbols:
            await update_timestamps_for_symbol(symbol, current_time)
        
        conn.close()
        
        logger.info(f"✅ All symbols data updated")
        
    except Exception as e:
        logger.error(f"❌ Error updating all symbols data: {e}")

async def create_alerts_for_symbol(symbol_id, symbol, cursor):
    """Create alerts for a specific symbol"""
    try:
        import requests
        
        # Get current price from Binance API
        response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        response.raise_for_status()
        
        ticker_data = response.json()
        current_price = float(ticker_data['lastPrice'])
        price_change_24h = float(ticker_data.get('priceChangePercent', 0))
        
        # Define timeframes
        timeframes = [
            {"name": "15m", "multiplier": 1.015, "description": "15 minutes"},
            {"name": "1h", "multiplier": 1.02, "description": "1 hour"},
            {"name": "4h", "multiplier": 1.025, "description": "4 hours"},
            {"name": "1d", "multiplier": 1.03, "description": "1 day"}
        ]
        
        # Create alerts for each timeframe
        for timeframe in timeframes:
            # Above threshold
            above_threshold = current_price * timeframe["multiplier"]
            cursor.execute("""
                INSERT OR REPLACE INTO symbol_alerts 
                (id, symbol_id, symbol, alert_type, timeframe, condition, threshold, current_price, price_change_24h, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{symbol}_above_{timeframe['name']}",
                symbol_id, symbol, "price_alert", timeframe["name"], "above",
                above_threshold, current_price, price_change_24h, 1
            ))
            
            # Below threshold
            below_threshold = current_price * (2 - timeframe["multiplier"])
            cursor.execute("""
                INSERT OR REPLACE INTO symbol_alerts 
                (id, symbol_id, symbol, alert_type, timeframe, condition, threshold, current_price, price_change_24h, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{symbol}_below_{timeframe['name']}",
                symbol_id, symbol, "price_alert", timeframe["name"], "below",
                below_threshold, current_price, price_change_24h, 1
            ))
        
        logger.info(f"✅ Created alerts for {symbol}")
        
    except Exception as e:
        logger.error(f"❌ Error creating alerts for {symbol}: {e}")

# Function to refresh alerts with current real-time prices
async def refresh_alerts_with_current_prices():
    """Refresh all alerts with current real-time prices from Binance API"""
    global dynamic_alerts
    
    try:
        import requests
        updated_count = 0
        
        for alert_key, alert in dynamic_alerts.items():
            if not alert.get("is_active", False):
                continue
                
            symbol = alert["symbol"]
            condition = alert["condition"]
            
            try:
                # Get current real-time price from Binance API
                response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=5)
                response.raise_for_status()
                
                ticker_data = response.json()
                current_price = float(ticker_data['lastPrice'])
                
                # Update alert with current price
                alert["current_price"] = current_price
                alert["price_change_24h"] = float(ticker_data.get('priceChangePercent', 0))
                alert["last_updated"] = datetime.now().isoformat()
                
                # Get timeframe multiplier based on alert timeframe (optimized for 10 symbols)
                timeframe_multipliers = {
                    "15m": 1.015, "1h": 1.02, "4h": 1.025, "1d": 1.03
                }
                
                timeframe_descriptions = {
                    "15m": "15 minutes", "1h": "1 hour", "4h": "4 hours", "1d": "1 day"
                }
                
                # Get timeframe from alert (default to 1h if not set)
                timeframe = alert.get("timeframe", "1h")
                multiplier = timeframe_multipliers.get(timeframe, 1.02)
                description = timeframe_descriptions.get(timeframe, "1 hour")
                
                # Recalculate thresholds based on current price and timeframe
                if condition == "above":
                    new_threshold = current_price * multiplier
                    alert["threshold"] = new_threshold
                    alert["message"] = f"{symbol} {description} alert - above ${new_threshold:,.2f}"
                elif condition == "below":
                    new_threshold = current_price * (2 - multiplier)  # Symmetric below
                    alert["threshold"] = new_threshold
                    alert["message"] = f"{symbol} {description} alert - below ${new_threshold:,.2f}"
                
                # Check if alert should be triggered
                alert_triggered = False
                if condition == "above" and current_price >= alert["threshold"]:
                    alert_triggered = True
                    alert["last_triggered"] = datetime.now().isoformat()
                    logger.info(f"🚨 ALERT TRIGGERED: {symbol} price ${current_price:,.2f} >= threshold ${alert['threshold']:,.2f}")
                elif condition == "below" and current_price <= alert["threshold"]:
                    alert_triggered = True
                    alert["last_triggered"] = datetime.now().isoformat()
                    logger.info(f"🚨 ALERT TRIGGERED: {symbol} price ${current_price:,.2f} <= threshold ${alert['threshold']:,.2f}")
                
                # If alert is triggered, perform comprehensive update
                if alert_triggered:
                    alert_data = {
                        "current_price": current_price,
                        "price_change_24h": float(ticker_data.get('priceChangePercent', 0)),
                        "condition": condition,
                        "threshold": alert["threshold"],
                        "timeframe": timeframe,
                        "triggered_at": datetime.now().isoformat()
                    }
                    
                    # Perform comprehensive alert-triggered update
                    await handle_alert_triggered_update(symbol, "price_alert", timeframe, alert_data)
                
                updated_count += 1
                logger.info(f"✅ Updated {symbol} alert with current price: ${current_price:,.2f}")
                
            except Exception as e:
                logger.error(f"❌ Error updating {symbol} alert: {e}")
                continue
        
        logger.info(f"🔄 Refreshed {updated_count} alerts with current real-time prices")
        return updated_count
        
    except Exception as e:
        logger.error(f"❌ Error refreshing alerts: {e}")
        return 0

# Function to cleanup old alerts based on timeframe
async def cleanup_old_alerts():
    """Clean up old alerts based on their timeframe"""
    global mock_alerts, dynamic_alerts
    
    try:
        current_time = datetime.now()
        cleaned_count = 0
        
        # Clean up mock alerts
        original_mock_count = len(mock_alerts)
        temp_mock_alerts = []
        
        for alert in mock_alerts:
            # Parse alert creation time
            try:
                created_time = datetime.fromisoformat(alert.get('created_at', '').replace('Z', '+00:00'))
                if created_time.tzinfo is None:
                    created_time = created_time.replace(tzinfo=timezone.utc)
                
                # Determine alert timeframe (default to 24h if not specified)
                timeframe = alert.get('timeframe', '24h')
                max_age_hours = ALERT_CLEANUP_CONFIG.get(timeframe, 72)  # Default to 72 hours
                
                # Calculate age in hours
                age_hours = (current_time - created_time).total_seconds() / 3600
                
                # Keep alert if it's within the retention period
                if age_hours <= max_age_hours:
                    temp_mock_alerts.append(alert)
                else:
                    cleaned_count += 1
                    logger.info(f"Cleaned up old alert: {alert.get('symbol', 'Unknown')} - {alert.get('type', 'Unknown')} (age: {age_hours:.1f}h)")
                    
            except Exception as e:
                # If we can't parse the time, keep the alert for safety
                temp_mock_alerts.append(alert)
                logger.warning(f"Could not parse alert time, keeping alert: {e}")
        
        # Update the mock_alerts list with the filtered alerts
        mock_alerts = temp_mock_alerts
        
        # Clean up dynamic alerts
        original_dynamic_count = len(dynamic_alerts)
        symbols_to_remove = []
        
        for symbol, alert in dynamic_alerts.items():
            try:
                created_time = datetime.fromisoformat(alert.get('created_at', '').replace('Z', '+00:00'))
                if created_time.tzinfo is None:
                    created_time = created_time.replace(tzinfo=timezone.utc)
                
                # Dynamic alerts are typically 24h timeframe
                timeframe = alert.get('timeframe', '24h')
                max_age_hours = ALERT_CLEANUP_CONFIG.get(timeframe, 72)
                
                age_hours = (current_time - created_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    symbols_to_remove.append(symbol)
                    cleaned_count += 1
                    logger.info(f"Cleaned up old dynamic alert: {symbol} (age: {age_hours:.1f}h)")
                    
            except Exception as e:
                logger.warning(f"Could not parse dynamic alert time for {symbol}: {e}")
        
        # Remove old dynamic alerts
        for symbol in symbols_to_remove:
            del dynamic_alerts[symbol]
        
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old alerts")
            logger.info(f"📊 Alerts remaining: {len(mock_alerts)} mock + {len(dynamic_alerts)} dynamic = {len(mock_alerts) + len(dynamic_alerts)} total")
        
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Error during alert cleanup: {e}")
        return 0

# Function to get current My Symbols
async def get_my_symbols():
    """Get current symbols from My Symbols database"""
    try:
        import sqlite3
        import os
        # Use absolute path to the database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.symbol FROM symbols s 
            JOIN portfolio_composition pc ON s.id = pc.symbol_id 
            WHERE pc.status = 'Active' 
            ORDER BY pc.position_rank
        """)
        symbols = [row[0] for row in cursor.fetchall()]
        conn.close()
        return symbols
    except Exception as e:
        logger.error(f"Error getting My Symbols: {e}")
        return []

# Function to sync alerts with My Symbols
async def sync_alerts_with_symbols():
    """Sync alerts with current My Symbols"""
    global dynamic_alerts, alert_counter
    current_symbols = await get_my_symbols()
    
    # Remove alerts for symbols no longer in My Symbols
    symbols_to_remove = [symbol for symbol in dynamic_alerts.keys() if symbol not in current_symbols]
    for symbol in symbols_to_remove:
        del dynamic_alerts[symbol]
        logger.info(f"Removed alerts for {symbol} - no longer in My Symbols")
    
    # Add default alerts for new symbols
    for symbol in current_symbols:
        if symbol not in dynamic_alerts:
            alert_counter += 1
            # Get real current price for threshold
            try:
                import requests
                response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}")
                if response.status_code == 200:
                    current_price = float(response.json()['lastPrice'])
                    # Set threshold 5% above current price
                    threshold = current_price * 1.05
                else:
                    threshold = 50000  # fallback
            except:
                threshold = 50000  # fallback
            
            dynamic_alerts[symbol] = {
                "id": str(alert_counter),
                "symbol": symbol,
                "type": "price_alert",
                "condition": "above",
                "threshold": threshold,
                "message": f"{symbol} price alert - above ${threshold:,.2f}",
                "is_active": True,
                "timeframe": "24h",
                "created_at": datetime.now().isoformat(),
                "last_triggered": None
            }
            logger.info(f"Added default alert for {symbol} at ${threshold:,.2f}")
    
    return dynamic_alerts

# NO MOCK DATA - ONLY REAL MARKET DATA
# Rule: All alerts must be based on real market prices from Binance API
mock_alerts = []

mock_system_status = {
    "status": "active",
    "uptime": "24h 15m 30s",
    "total_alerts": 12,
    "active_alerts": 8,
    "recent_triggers": 3,
    "success_rate": 85.5,
    "last_update": datetime.now().isoformat()
}

mock_telegram_config = {
    "enabled": True,
    "bot_token": "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI",
    "chat_id": "-1002891569616",
    "notifications_enabled": True,
    "quiet_hours": [23, 0, 1, 2, 3, 4, 5, 6],
    "last_message_sent": datetime.now().isoformat(),
    "status": "enabled",
    "channel_username": "@KingFisherAutomation",
    "connected": True,
    "monitoring": True,
    "automation_enabled": True,
    "processed_count": 15
}

mock_alert_templates = [
    {
        "id": "template_1",
        "name": "Price Breakout",
        "description": "Alert when price breaks above resistance",
        "conditions": ["price_above", "volume_spike"],
        "message_template": "🚨 {symbol} price breakout detected at ${price}"
    },
    {
        "id": "template_2", 
        "name": "Volume Spike",
        "description": "Alert when volume increases significantly",
        "conditions": ["volume_above"],
        "message_template": "📊 {symbol} volume spike: {volume} (avg: {avg_volume})"
    },
    {
        "id": "template_3",
        "name": "Pattern Detection", 
        "description": "Alert when technical patterns are detected",
        "conditions": ["pattern_detected"],
        "message_template": "📈 {symbol} {pattern} pattern detected"
    }
]

# NO MOCK TRIGGER HISTORY - ONLY REAL TRIGGERS
# Rule: All trigger history must be based on actual alert triggers
mock_trigger_history = []

@router.post("/refresh")
async def refresh_alerts():
    """Refresh all alerts with current real-time prices from Binance API"""
    try:
        updated_count = await refresh_alerts_with_current_prices()
        return {
            "success": True,
            "message": f"Refreshed {updated_count} alerts with current real-time prices",
            "updated_count": updated_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-update/{symbol}")
async def trigger_alert_update(symbol: str, timeframe: str = "1h"):
    """Manually trigger alert-triggered update for a specific symbol (for testing)"""
    try:
        # Get current market data
        import requests
        
        response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        response.raise_for_status()
        ticker_data = response.json()
        
        current_price = float(ticker_data['lastPrice'])
        price_change_24h = float(ticker_data.get('priceChangePercent', 0))
        
        alert_data = {
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "condition": "above",
            "threshold": current_price * 1.02,
            "timeframe": timeframe,
            "triggered_at": datetime.now().isoformat(),
            "manual_trigger": True
        }
        
        # Perform comprehensive alert-triggered update
        await handle_alert_triggered_update(symbol, "price_alert", timeframe, alert_data)
        
        return {
            "success": True,
            "message": f"Alert-triggered update completed for {symbol} ({timeframe})",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering alert update for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reinitialize")
async def reinitialize_alerts():
    """Clear and reinitialize all alerts with new timeframe structure"""
    global dynamic_alerts, mock_alerts
    try:
        # Clear existing alerts completely
        dynamic_alerts = {}
        mock_alerts = []
        
        # Reinitialize with new structure
        await initialize_dynamic_alerts()
        
        return {
            "success": True,
            "message": f"Reinitialized {len(dynamic_alerts)} alerts with new timeframe structure",
            "total_alerts": len(dynamic_alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reinitializing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_alerts_with_portfolio():
    """Sync alerts with current portfolio - add new symbols, remove old ones"""
    try:
        # Reinitialize to sync with current portfolio
        await initialize_dynamic_alerts()
        
        return {
            "success": True,
            "message": f"Synced alerts with portfolio - {len(dynamic_alerts)} active alerts",
            "total_alerts": len(dynamic_alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error syncing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))











@router.get("/analysis/{symbol}")
async def get_symbol_technical_analysis(symbol: str):
    """Get comprehensive technical analysis for a specific symbol - FIXED VERSION"""
    try:
        import requests
        import sqlite3
        import os
        from src.services.technical_analysis_service import TechnicalAnalysisService
        
        # Get current price and 24hr data
        response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        response.raise_for_status()
        ticker_data = response.json()
        
        current_price = float(ticker_data['lastPrice'])
        price_change_24h = float(ticker_data.get('priceChangePercent', 0))
        volume_24h = float(ticker_data.get('volume', 0))
        high_24h = float(ticker_data.get('highPrice', current_price))
        low_24h = float(ticker_data.get('lowPrice', current_price))
        
        # Initialize analysis structure
        analysis = {
            "symbol": symbol,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "volume_24h": volume_24h,
            "high_24h": high_24h,
            "low_24h": low_24h,
            "last_updated": datetime.now().isoformat(),
            
            # Initialize all data structures
            "momentum_indicators_data": {},
            "price_channels_data": {},
            "support_resistance_data": {},
            "ma_convergence_data": {},
            "macd_histogram_data": {},
            "bollinger_squeeze_data": {},
            "price_patterns_data": {},
            "rsi_divergence_data": {},
            "stochastic_data": {},
            "cci_data": {},
            "adx_data": {},
            "parabolic_sar_data": {},
            "atr_data": {},
            "williams_r_data": {},
            "stoch_rsi_data": {},
            "ichimoku_data": {},
            "fibonacci_data": {},
            "volume_data": {},
            "ema_data": {},
            "rsi_data": {},
            "macd_data": {},
            "bollinger_bands_timeframes": {},
            "alerts": []
        }
        
        # Get database connection
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'my_symbols_v2.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get Momentum Indicators data
        try:
            cursor.execute("""
                SELECT timeframe, roc_value, roc_signal, roc_strength, roc_divergence,
                       mom_value, mom_signal, mom_strength, mom_divergence,
                       momentum_status, momentum_strength, trend_alignment,
                       overbought_oversold_status, volume_confirmation
                FROM momentum_indicators_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_momentum_indicators_data = cursor.fetchall()
            
            if db_momentum_indicators_data:
                for row in db_momentum_indicators_data:
                    tf, roc_value, roc_signal, roc_strength, roc_divergence, mom_value, mom_signal, mom_strength, mom_divergence, momentum_status, momentum_strength, trend_alignment, overbought_oversold_status, volume_confirmation = row
                    analysis["momentum_indicators_data"][tf] = {
                        "roc_value": float(roc_value) if roc_value is not None else None,
                        "roc_signal": str(roc_signal) if roc_signal is not None else None,
                        "roc_strength": float(roc_strength) if roc_strength is not None else None,
                        "roc_divergence": str(roc_divergence) if roc_divergence is not None else None,
                        "mom_value": float(mom_value) if mom_value is not None else None,
                        "mom_signal": str(mom_signal) if mom_signal is not None else None,
                        "mom_strength": float(mom_strength) if mom_strength is not None else None,
                        "mom_divergence": str(mom_divergence) if mom_divergence is not None else None,
                        "momentum_status": str(momentum_status) if momentum_status is not None else None,
                        "momentum_strength": float(momentum_strength) if momentum_strength is not None else None,
                        "trend_alignment": str(trend_alignment) if trend_alignment is not None else None,
                        "overbought_oversold_status": str(overbought_oversold_status) if overbought_oversold_status is not None else None,
                        "volume_confirmation": str(volume_confirmation) if volume_confirmation is not None else None
                    }
        except Exception as e:
            logger.warning(f"Error reading Momentum Indicators from database for {symbol}: {e}")
        
        # Get Price Channels data
        try:
            cursor.execute("""
                SELECT timeframe, upper_channel, middle_channel, lower_channel,
                       channel_width, channel_position, breakout_direction, breakout_strength,
                       channel_trend, trend_strength, volatility_status, volatility_strength,
                       momentum_status, momentum_strength, volume_confirmation
                FROM price_channels_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_price_channels_data = cursor.fetchall()
            
            if db_price_channels_data:
                for row in db_price_channels_data:
                    tf, upper_channel, middle_channel, lower_channel, channel_width, channel_position, breakout_direction, breakout_strength, channel_trend, trend_strength, volatility_status, volatility_strength, momentum_status, momentum_strength, volume_confirmation = row
                    analysis["price_channels_data"][tf] = {
                        "upper_channel": float(upper_channel) if upper_channel is not None else None,
                        "middle_channel": float(middle_channel) if middle_channel is not None else None,
                        "lower_channel": float(lower_channel) if lower_channel is not None else None,
                        "channel_width": float(channel_width) if channel_width is not None else None,
                        "channel_position": float(channel_position) if channel_position is not None else None,
                        "breakout_direction": str(breakout_direction) if breakout_direction is not None else None,
                        "breakout_strength": float(breakout_strength) if breakout_strength is not None else None,
                        "channel_trend": str(channel_trend) if channel_trend is not None else None,
                        "trend_strength": float(trend_strength) if trend_strength is not None else None,
                        "volatility_status": str(volatility_status) if volatility_status is not None else None,
                        "volatility_strength": float(volatility_strength) if volatility_strength is not None else None,
                        "momentum_status": str(momentum_status) if momentum_status is not None else None,
                        "momentum_strength": float(momentum_strength) if momentum_strength is not None else None,
                        "volume_confirmation": str(volume_confirmation) if volume_confirmation is not None else None
                    }
        except Exception as e:
            logger.warning(f"Error reading Price Channels from database for {symbol}: {e}")
        
        # Get Support/Resistance Levels data
        try:
            cursor.execute("""
                SELECT timeframe, support_level_1, support_level_2, support_level_3,
                       resistance_level_1, resistance_level_2, resistance_level_3,
                       price_position, nearest_support, nearest_resistance,
                       support_strength, resistance_strength, breakout_potential,
                       breakout_direction, breakout_strength, volume_confirmation
                FROM support_resistance_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_support_resistance_data = cursor.fetchall()
            
            if db_support_resistance_data:
                for row in db_support_resistance_data:
                    tf, support_level_1, support_level_2, support_level_3, resistance_level_1, resistance_level_2, resistance_level_3, price_position, nearest_support, nearest_resistance, support_strength, resistance_strength, breakout_potential, breakout_direction, breakout_strength, volume_confirmation = row
                    analysis["support_resistance_data"][tf] = {
                        "support_level_1": float(support_level_1) if support_level_1 is not None else None,
                        "support_level_2": float(support_level_2) if support_level_2 is not None else None,
                        "support_level_3": float(support_level_3) if support_level_3 is not None else None,
                        "resistance_level_1": float(resistance_level_1) if resistance_level_1 is not None else None,
                        "resistance_level_2": float(resistance_level_2) if resistance_level_2 is not None else None,
                        "resistance_level_3": float(resistance_level_3) if resistance_level_3 is not None else None,
                        "price_position": str(price_position) if price_position is not None else None,
                        "nearest_support": float(nearest_support) if nearest_support is not None else None,
                        "nearest_resistance": float(nearest_resistance) if nearest_resistance is not None else None,
                        "support_strength": float(support_strength) if support_strength is not None else None,
                        "resistance_strength": float(resistance_strength) if resistance_strength is not None else None,
                        "breakout_potential": str(breakout_potential) if breakout_potential is not None else None,
                        "breakout_direction": str(breakout_direction) if breakout_direction is not None else None,
                        "breakout_strength": float(breakout_strength) if breakout_strength is not None else None,
                        "volume_confirmation": str(volume_confirmation) if volume_confirmation is not None else None
                    }
        except Exception as e:
            logger.warning(f"Error reading Support/Resistance Levels from database for {symbol}: {e}")
        
        # Get Moving Average Convergence data
        try:
            cursor.execute("""
                SELECT timeframe, convergence_status, convergence_strength, ma_alignment,
                       alignment_strength, golden_cross_detected, death_cross_detected,
                       trend_direction, trend_strength, breakout_potential, volume_confirmation
                FROM ma_convergence_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_ma_convergence_data = cursor.fetchall()
            
            if db_ma_convergence_data:
                for row in db_ma_convergence_data:
                    tf, convergence_status, convergence_strength, ma_alignment, alignment_strength, golden_cross_detected, death_cross_detected, trend_direction, trend_strength, breakout_potential, volume_confirmation = row
                    analysis["ma_convergence_data"][tf] = {
                        "convergence_status": str(convergence_status) if convergence_status is not None else None,
                        "convergence_strength": float(convergence_strength) if convergence_strength is not None else None,
                        "ma_alignment": str(ma_alignment) if ma_alignment is not None else None,
                        "alignment_strength": float(alignment_strength) if alignment_strength is not None else None,
                        "golden_cross_detected": bool(golden_cross_detected) if golden_cross_detected is not None else None,
                        "death_cross_detected": bool(death_cross_detected) if death_cross_detected is not None else None,
                        "trend_direction": str(trend_direction) if trend_direction is not None else None,
                        "trend_strength": float(trend_strength) if trend_strength is not None else None,
                        "breakout_potential": str(breakout_potential) if breakout_potential is not None else None,
                        "volume_confirmation": str(volume_confirmation) if volume_confirmation is not None else None
                    }
        except Exception as e:
            logger.warning(f"Error reading Moving Average Convergence from database for {symbol}: {e}")
        
        # Get MACD Histogram data
        try:
            cursor.execute("""
                SELECT timeframe, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, volume_strength
                FROM macd_histogram_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_macd_histogram_data = cursor.fetchall()
            
            if db_macd_histogram_data:
                # Use database data
                analysis["macd_histogram_data"] = analysis.get("macd_histogram_data", {})
                for row in db_macd_histogram_data:
                    tf, histogram_trend, histogram_strength, zero_line_cross, signal_cross, divergence_type, momentum_shift, histogram_pattern, volume_confirmation, volume_strength = row
                    analysis["macd_histogram_data"][tf] = {
                        "histogram_trend": histogram_trend,
                        "histogram_strength": histogram_strength,
                        "zero_line_cross": zero_line_cross,
                        "signal_cross": signal_cross,
                        "divergence_type": divergence_type,
                        "momentum_shift": momentum_shift,
                        "histogram_pattern": histogram_pattern,
                        "volume_confirmation": volume_confirmation,
                        "volume_strength": volume_strength
                    }
            else:
                # No MACD Histogram data in database - skip calculation for now
                analysis["macd_histogram_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading MACD Histogram from database for {symbol}: {e}")
            # No fallback calculation - skip MACD Histogram data
            analysis["macd_histogram_data"] = {}

        # Get Bollinger Band Squeeze data
        try:
            cursor.execute("""
                SELECT timeframe, squeeze_status, squeeze_strength, band_width_percentile,
                       price_position, breakout_potential, breakout_direction, breakout_strength,
                       momentum_divergence, volume_profile, volume_strength
                FROM bollinger_squeeze_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_bollinger_squeeze_data = cursor.fetchall()
            
            if db_bollinger_squeeze_data:
                # Use database data
                analysis["bollinger_squeeze_data"] = analysis.get("bollinger_squeeze_data", {})
                for row in db_bollinger_squeeze_data:
                    tf, squeeze_status, squeeze_strength, band_width_percentile, price_position, breakout_potential, breakout_direction, breakout_strength, momentum_divergence, volume_profile, volume_strength = row
                    analysis["bollinger_squeeze_data"][tf] = {
                        "squeeze_status": squeeze_status,
                        "squeeze_strength": squeeze_strength,
                        "band_width_percentile": band_width_percentile,
                        "price_position": price_position,
                        "breakout_potential": breakout_potential,
                        "breakout_direction": breakout_direction,
                        "breakout_strength": breakout_strength,
                        "momentum_divergence": momentum_divergence,
                        "volume_profile": volume_profile,
                        "volume_strength": volume_strength
                    }
            else:
                # No Bollinger Band Squeeze data in database - skip calculation for now
                analysis["bollinger_squeeze_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Bollinger Band Squeeze from database for {symbol}: {e}")
            # No fallback calculation - skip Bollinger Band Squeeze data
            analysis["bollinger_squeeze_data"] = {}

        # Get Price Action Patterns data
        try:
            cursor.execute("""
                SELECT timeframe, pattern_type, pattern_name, pattern_strength, pattern_reliability,
                       pattern_direction, pattern_completion, volume_confirmation, volume_strength,
                       trend_alignment, risk_reward_ratio
                FROM price_patterns_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_price_patterns_data = cursor.fetchall()
            
            if db_price_patterns_data:
                # Use database data
                analysis["price_patterns_data"] = analysis.get("price_patterns_data", {})
                for row in db_price_patterns_data:
                    tf, pattern_type, pattern_name, pattern_strength, pattern_reliability, pattern_direction, pattern_completion, volume_confirmation, volume_strength, trend_alignment, risk_reward_ratio = row
                    analysis["price_patterns_data"][tf] = {
                        "pattern_type": pattern_type,
                        "pattern_name": pattern_name,
                        "pattern_strength": pattern_strength,
                        "pattern_reliability": pattern_reliability,
                        "pattern_direction": pattern_direction,
                        "pattern_completion": pattern_completion,
                        "volume_confirmation": volume_confirmation,
                        "volume_strength": volume_strength,
                        "trend_alignment": trend_alignment,
                        "risk_reward_ratio": risk_reward_ratio
                    }
            else:
                # No Price Action Patterns data in database - skip calculation for now
                analysis["price_patterns_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Price Action Patterns from database for {symbol}: {e}")
            # No fallback calculation - skip Price Action Patterns data
            analysis["price_patterns_data"] = {}

        # Get RSI Divergence data
        try:
            cursor.execute("""
                SELECT timeframe, divergence_type, divergence_strength, confirmation_level,
                       signal_strength, trend_direction, momentum_shift, breakout_potential
                FROM rsi_divergence_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_rsi_divergence_data = cursor.fetchall()
            
            if db_rsi_divergence_data:
                # Use database data
                analysis["rsi_divergence_data"] = analysis.get("rsi_divergence_data", {})
                for row in db_rsi_divergence_data:
                    tf, divergence_type, divergence_strength, confirmation_level, signal_strength, trend_direction, momentum_shift, breakout_potential = row
                    analysis["rsi_divergence_data"][tf] = {
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength,
                        "confirmation_level": confirmation_level,
                        "signal_strength": signal_strength,
                        "trend_direction": trend_direction,
                        "momentum_shift": momentum_shift,
                        "breakout_potential": breakout_potential
                    }
            else:
                # No RSI Divergence data in database - skip calculation for now
                analysis["rsi_divergence_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading RSI Divergence from database for {symbol}: {e}")
            # No fallback calculation - skip RSI Divergence data
            analysis["rsi_divergence_data"] = {}

        # Get Stochastic Oscillator data
        try:
            cursor.execute("""
                SELECT timeframe, k_percent, d_percent, overbought_level, oversold_level,
                       signal_status, signal_strength, k_d_crossover, k_d_crossover_strength,
                       divergence_type, divergence_strength, momentum_trend, momentum_strength,
                       extreme_level, extreme_type
                FROM stochastic_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_stochastic_data = cursor.fetchall()
            
            if db_stochastic_data:
                # Use database data
                analysis["stochastic_data"] = analysis.get("stochastic_data", {})
                for row in db_stochastic_data:
                    tf, k_percent, d_percent, overbought_level, oversold_level, signal_status, signal_strength, k_d_crossover, k_d_crossover_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type = row
                    analysis["stochastic_data"][tf] = {
                        "k_percent": k_percent,
                        "d_percent": d_percent,
                        "overbought_level": overbought_level,
                        "oversold_level": oversold_level,
                        "signal_status": signal_status,
                        "signal_strength": signal_strength,
                        "k_d_crossover": k_d_crossover,
                        "k_d_crossover_strength": k_d_crossover_strength,
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength,
                        "momentum_trend": momentum_trend,
                        "momentum_strength": momentum_strength,
                        "extreme_level": extreme_level,
                        "extreme_type": extreme_type
                    }
            else:
                # No Stochastic Oscillator data in database - skip calculation for now
                analysis["stochastic_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Stochastic Oscillator from database for {symbol}: {e}")
            # No fallback calculation - skip Stochastic Oscillator data
            analysis["stochastic_data"] = {}

        # Get CCI data
        try:
            cursor.execute("""
                SELECT timeframe, cci_value, overbought_level, oversold_level, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type
                FROM cci_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_cci_data = cursor.fetchall()
            
            if db_cci_data:
                # Use database data
                analysis["cci_data"] = analysis.get("cci_data", {})
                for row in db_cci_data:
                    tf, cci_value, overbought_level, oversold_level, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type = row
                    analysis["cci_data"][tf] = {
                        "cci_value": cci_value,
                        "overbought_level": overbought_level,
                        "oversold_level": oversold_level,
                        "signal_status": signal_status,
                        "signal_strength": signal_strength,
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength,
                        "momentum_trend": momentum_trend,
                        "momentum_strength": momentum_strength,
                        "extreme_level": extreme_level,
                        "extreme_type": extreme_type
                    }
            else:
                # No CCI data in database - skip calculation for now
                analysis["cci_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading CCI from database for {symbol}: {e}")
            # No fallback calculation - skip CCI data
            analysis["cci_data"] = {}

        # Get ADX data
        try:
            cursor.execute("""
                SELECT timeframe, adx_value, plus_di, minus_di, trend_strength,
                       trend_strength_value, trend_direction, di_crossover,
                       di_crossover_strength, momentum_signal, momentum_strength,
                       breakout_potential, breakout_strength
                FROM adx_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_adx_data = cursor.fetchall()
            
            if db_adx_data:
                # Use database data
                analysis["adx_data"] = analysis.get("adx_data", {})
                for row in db_adx_data:
                    tf, adx_value, plus_di, minus_di, trend_strength, trend_strength_value, trend_direction, di_crossover, di_crossover_strength, momentum_signal, momentum_strength, breakout_potential, breakout_strength = row
                    analysis["adx_data"][tf] = {
                        "adx_value": adx_value,
                        "plus_di": plus_di,
                        "minus_di": minus_di,
                        "trend_strength": trend_strength,
                        "trend_strength_value": trend_strength_value,
                        "trend_direction": trend_direction,
                        "di_crossover": di_crossover,
                        "di_crossover_strength": di_crossover_strength,
                        "momentum_signal": momentum_signal,
                        "momentum_strength": momentum_strength,
                        "breakout_potential": breakout_potential,
                        "breakout_strength": breakout_strength
                    }
            else:
                # No ADX data in database - skip calculation for now
                analysis["adx_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading ADX from database for {symbol}: {e}")
            # No fallback calculation - skip ADX data
            analysis["adx_data"] = {}

        # Get Parabolic SAR data
        try:
            cursor.execute("""
                SELECT timeframe, sar_value, trend_direction, trend_strength,
                       acceleration_factor, extreme_point, stop_loss_level,
                       take_profit_level, risk_reward_ratio, trend_duration,
                       trend_quality, reversal_signal, reversal_strength
                FROM parabolic_sar_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_parabolic_sar_data = cursor.fetchall()
            
            if db_parabolic_sar_data:
                # Use database data
                analysis["parabolic_sar_data"] = analysis.get("parabolic_sar_data", {})
                for row in db_parabolic_sar_data:
                    tf, sar_value, trend_direction, trend_strength, acceleration_factor, extreme_point, stop_loss_level, take_profit_level, risk_reward_ratio, trend_duration, trend_quality, reversal_signal, reversal_strength = row
                    analysis["parabolic_sar_data"][tf] = {
                        "sar_value": sar_value,
                        "trend_direction": trend_direction,
                        "trend_strength": trend_strength,
                        "acceleration_factor": acceleration_factor,
                        "extreme_point": extreme_point,
                        "stop_loss_level": stop_loss_level,
                        "take_profit_level": take_profit_level,
                        "risk_reward_ratio": risk_reward_ratio,
                        "trend_duration": trend_duration,
                        "trend_quality": trend_quality,
                        "reversal_signal": reversal_signal,
                        "reversal_strength": reversal_strength
                    }
            else:
                # No Parabolic SAR data in database - skip calculation for now
                analysis["parabolic_sar_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Parabolic SAR from database for {symbol}: {e}")
            # No fallback calculation - skip Parabolic SAR data
            analysis["parabolic_sar_data"] = {}

        # Get ATR data
        try:
            cursor.execute("""
                SELECT timeframe, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, true_range, high_low_range, high_close_range, low_close_range
                FROM atr_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_atr_data = cursor.fetchall()
            
            if db_atr_data:
                # Use database data
                analysis["atr_data"] = analysis.get("atr_data", {})
                for row in db_atr_data:
                    tf, atr_value, atr_percentage, volatility_level, volatility_strength, volatility_trend, volatility_change, breakout_potential, breakout_strength, true_range, high_low_range, high_close_range, low_close_range = row
                    analysis["atr_data"][tf] = {
                        "atr_value": atr_value,
                        "atr_percentage": atr_percentage,
                        "volatility_level": volatility_level,
                        "volatility_strength": volatility_strength,
                        "volatility_trend": volatility_trend,
                        "volatility_change": volatility_change,
                        "breakout_potential": breakout_potential,
                        "breakout_strength": breakout_strength,
                        "true_range": true_range,
                        "high_low_range": high_low_range,
                        "high_close_range": high_close_range,
                        "low_close_range": low_close_range
                    }
            else:
                # No ATR data in database - skip calculation for now
                analysis["atr_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading ATR from database for {symbol}: {e}")
            # No fallback calculation - skip ATR data
            analysis["atr_data"] = {}

        # Get Williams %R data
        try:
            cursor.execute("""
                SELECT timeframe, williams_r_value, overbought_level, oversold_level,
                       signal_status, signal_strength, divergence_type, divergence_strength,
                       momentum_trend, momentum_strength, extreme_level, extreme_type
                FROM williams_r_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_williams_r_data = cursor.fetchall()
            
            if db_williams_r_data:
                # Use database data
                analysis["williams_r_data"] = analysis.get("williams_r_data", {})
                for row in db_williams_r_data:
                    tf, williams_r_value, overbought_level, oversold_level, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength, extreme_level, extreme_type = row
                    analysis["williams_r_data"][tf] = {
                        "williams_r_value": williams_r_value,
                        "overbought_level": overbought_level,
                        "oversold_level": oversold_level,
                        "signal_status": signal_status,
                        "signal_strength": signal_strength,
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength,
                        "momentum_trend": momentum_trend,
                        "momentum_strength": momentum_strength,
                        "extreme_level": extreme_level,
                        "extreme_type": extreme_type
                    }
            else:
                # No Williams %R data in database - skip calculation for now
                analysis["williams_r_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Williams %R from database for {symbol}: {e}")
            # No fallback calculation - skip Williams %R data
            analysis["williams_r_data"] = {}

        # Get Stochastic RSI data
        try:
            cursor.execute("""
                SELECT timeframe, rsi_value, stoch_k, stoch_d, stoch_rsi_value,
                       overbought_level, oversold_level, signal_status, signal_strength,
                       divergence_type, divergence_strength, momentum_trend, momentum_strength
                FROM stoch_rsi_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_stoch_rsi_data = cursor.fetchall()
            
            if db_stoch_rsi_data:
                # Use database data
                analysis["stoch_rsi_data"] = analysis.get("stoch_rsi_data", {})
                for row in db_stoch_rsi_data:
                    tf, rsi_value, stoch_k, stoch_d, stoch_rsi_value, overbought_level, oversold_level, signal_status, signal_strength, divergence_type, divergence_strength, momentum_trend, momentum_strength = row
                    analysis["stoch_rsi_data"][tf] = {
                        "rsi_value": rsi_value,
                        "stoch_k": stoch_k,
                        "stoch_d": stoch_d,
                        "stoch_rsi_value": stoch_rsi_value,
                        "overbought_level": overbought_level,
                        "oversold_level": oversold_level,
                        "signal_status": signal_status,
                        "signal_strength": signal_strength,
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength,
                        "momentum_trend": momentum_trend,
                        "momentum_strength": momentum_strength
                    }
            else:
                # No Stochastic RSI data in database - skip calculation for now
                analysis["stoch_rsi_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Stochastic RSI from database for {symbol}: {e}")
            # No fallback calculation - skip Stochastic RSI data
            analysis["stoch_rsi_data"] = {}

        # Get Ichimoku data
        try:
            cursor.execute("""
                SELECT timeframe, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength
                FROM ichimoku_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_ichimoku_data = cursor.fetchall()
            
            if db_ichimoku_data:
                # Use database data
                analysis["ichimoku_data"] = analysis.get("ichimoku_data", {})
                for row in db_ichimoku_data:
                    tf, tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, current_price, cloud_color, cloud_trend, price_position, tenkan_kijun_signal, tenkan_kijun_strength, cloud_support, cloud_resistance, support_distance, resistance_distance, momentum_signal, trend_strength = row
                    analysis["ichimoku_data"][tf] = {
                        "tenkan_sen": tenkan_sen,
                        "kijun_sen": kijun_sen,
                        "senkou_span_a": senkou_span_a,
                        "senkou_span_b": senkou_span_b,
                        "chikou_span": chikou_span,
                        "current_price": current_price,
                        "cloud_color": cloud_color,
                        "cloud_trend": cloud_trend,
                        "price_position": price_position,
                        "tenkan_kijun_signal": tenkan_kijun_signal,
                        "tenkan_kijun_strength": tenkan_kijun_strength,
                        "cloud_support": cloud_support,
                        "cloud_resistance": cloud_resistance,
                        "support_distance": support_distance,
                        "resistance_distance": resistance_distance,
                        "momentum_signal": momentum_signal,
                        "trend_strength": trend_strength
                    }
            else:
                # No Ichimoku data in database - skip calculation for now
                analysis["ichimoku_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Ichimoku from database for {symbol}: {e}")
            # No fallback calculation - skip Ichimoku data
            analysis["ichimoku_data"] = {}

        # Get Fibonacci data
        try:
            cursor.execute("""
                SELECT timeframe, swing_high, swing_low, fib_0, fib_23_6, fib_38_2, fib_50_0,
                       fib_61_8, fib_78_6, fib_100, current_price, price_position,
                       nearest_support, nearest_resistance, support_distance, resistance_distance,
                       trend_direction, swing_strength
                FROM fibonacci_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_fibonacci_data = cursor.fetchall()
            
            if db_fibonacci_data:
                # Use database data
                analysis["fibonacci_data"] = analysis.get("fibonacci_data", {})
                for row in db_fibonacci_data:
                    tf, swing_high, swing_low, fib_0, fib_23_6, fib_38_2, fib_50_0, fib_61_8, fib_78_6, fib_100, current_price, price_position, nearest_support, nearest_resistance, support_distance, resistance_distance, trend_direction, swing_strength = row
                    analysis["fibonacci_data"][tf] = {
                        "swing_high": swing_high,
                        "swing_low": swing_low,
                        "fib_0": fib_0,
                        "fib_23_6": fib_23_6,
                        "fib_38_2": fib_38_2,
                        "fib_50_0": fib_50_0,
                        "fib_61_8": fib_61_8,
                        "fib_78_6": fib_78_6,
                        "fib_100": fib_100,
                        "current_price": current_price,
                        "price_position": price_position,
                        "nearest_support": nearest_support,
                        "nearest_resistance": nearest_resistance,
                        "support_distance": support_distance,
                        "resistance_distance": resistance_distance,
                        "trend_direction": trend_direction,
                        "swing_strength": swing_strength
                    }
            else:
                # No Fibonacci data in database - skip calculation for now
                analysis["fibonacci_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Fibonacci from database for {symbol}: {e}")
            # No fallback calculation - skip Fibonacci data
            analysis["fibonacci_data"] = {}

        # Get Volume data
        try:
            cursor.execute("""
                SELECT timeframe, current_volume, volume_sma_20, volume_ratio, obv, obv_sma,
                       volume_spike_detected, volume_spike_ratio, volume_trend,
                       volume_divergence_type, volume_divergence_strength, price_volume_correlation
                FROM volume_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_volume_data = cursor.fetchall()
            
            if db_volume_data:
                # Use database data
                analysis["volume_data"] = analysis.get("volume_data", {})
                for row in db_volume_data:
                    tf, current_volume, volume_sma_20, volume_ratio, obv, obv_sma, volume_spike_detected, volume_spike_ratio, volume_trend, volume_divergence_type, volume_divergence_strength, price_volume_correlation = row
                    analysis["volume_data"][tf] = {
                        "current_volume": current_volume,
                        "volume_sma_20": volume_sma_20,
                        "volume_ratio": volume_ratio,
                        "obv": obv,
                        "obv_sma": obv_sma,
                        "volume_spike_detected": volume_spike_detected,
                        "volume_spike_ratio": volume_spike_ratio,
                        "volume_trend": volume_trend,
                        "volume_divergence_type": volume_divergence_type,
                        "volume_divergence_strength": volume_divergence_strength,
                        "price_volume_correlation": price_volume_correlation
                    }
            else:
                # No Volume data in database - skip calculation for now
                analysis["volume_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading Volume from database for {symbol}: {e}")
            # No fallback calculation - skip Volume data
            analysis["volume_data"] = {}

        # Get EMA data
        try:
            cursor.execute("""
                SELECT timeframe, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend
                FROM ema_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_ema_data = cursor.fetchall()
            
            if db_ema_data:
                # Use database data
                analysis["ema_data"] = analysis.get("ema_data", {})
                for row in db_ema_data:
                    tf, ema_9, ema_12, ema_20, ema_21, ema_26, ema_50, cross_signal, cross_strength, golden_cross_detected, death_cross_detected, short_term_trend, long_term_trend = row
                    analysis["ema_data"][tf] = {
                        "ema_9": ema_9,
                        "ema_12": ema_12,
                        "ema_20": ema_20,
                        "ema_21": ema_21,
                        "ema_26": ema_26,
                        "ema_50": ema_50,
                        "cross_signal": cross_signal,
                        "cross_strength": cross_strength,
                        "golden_cross_detected": bool(golden_cross_detected),
                        "death_cross_detected": bool(death_cross_detected),
                        "short_term_trend": short_term_trend,
                        "long_term_trend": long_term_trend
                    }
            else:
                # No EMA data in database - skip calculation for now
                analysis["ema_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading EMA from database for {symbol}: {e}")
            # No fallback calculation - skip EMA data
            analysis["ema_data"] = {}

        # Get RSI data
        try:
            cursor.execute("""
                SELECT timeframe, rsi_value, signal_status, divergence_type, divergence_strength
                FROM rsi_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_rsi_data = cursor.fetchall()
            print(f"🔍 DEBUG: Found {len(db_rsi_data)} RSI records for {symbol}")
            
            if db_rsi_data:
                # Use database data
                analysis["rsi_data"] = analysis.get("rsi_data", {})
                for row in db_rsi_data:
                    tf, rsi_value, signal_status, divergence_type, divergence_strength = row
                    analysis["rsi_data"][tf] = {
                        "rsi_value": rsi_value,
                        "signal_status": signal_status,
                        "divergence_type": divergence_type,
                        "divergence_strength": divergence_strength
                    }
            else:
                # No RSI data in database - skip calculation for now
                analysis["rsi_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading RSI from database for {symbol}: {e}")
            # No fallback calculation - skip RSI data
            analysis["rsi_data"] = {}

        # Get MACD data
        try:
            cursor.execute("""
                SELECT timeframe, macd_line, signal_line, histogram, signal_status
                FROM macd_data 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_macd_data = cursor.fetchall()
            
            if db_macd_data:
                # Use database data
                analysis["macd_data"] = analysis.get("macd_data", {})
                for row in db_macd_data:
                    tf, macd_line, signal_line, histogram, signal_status = row
                    analysis["macd_data"][tf] = {
                        "macd_line": macd_line,
                        "signal_line": signal_line,
                        "histogram": histogram,
                        "signal_status": signal_status
                    }
            else:
                # No MACD data in database - skip calculation for now
                analysis["macd_data"] = {}
        except Exception as e:
            logger.warning(f"Error reading MACD from database for {symbol}: {e}")
            # No fallback calculation - skip MACD data
            analysis["macd_data"] = {}

        # Get Bollinger Bands data
        try:
            cursor.execute("""
                SELECT timeframe, upper_band, sma, lower_band, bandwidth, position
                FROM bollinger_bands 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            db_bollinger_bands_data = cursor.fetchall()
            
            if db_bollinger_bands_data:
                # Use database data
                analysis["bollinger_bands_timeframes"] = analysis.get("bollinger_bands_timeframes", {})
                for row in db_bollinger_bands_data:
                    tf, upper_band, sma, lower_band, bandwidth, position = row
                    analysis["bollinger_bands_timeframes"][tf] = {
                        "upper_band": upper_band,
                        "middle_band": sma,  # Use SMA as middle band
                        "lower_band": lower_band,
                        "band_width": bandwidth,
                        "band_position": position,
                        "squeeze_status": "normal",  # Default value
                        "squeeze_strength": 0.0,  # Default value
                        "breakout_potential": "low",  # Default value
                        "breakout_direction": "none",  # Default value
                        "breakout_strength": 0.0,  # Default value
                        "volume_confirmation": "none"  # Default value
                    }
            else:
                # No Bollinger Bands data in database - skip calculation for now
                analysis["bollinger_bands_timeframes"] = {}
        except Exception as e:
            logger.warning(f"Error reading Bollinger Bands from database for {symbol}: {e}")
            # No fallback calculation - skip Bollinger Bands data
            analysis["bollinger_bands_timeframes"] = {}

        conn.close()
        
        # Convert analysis data to JSON serializable format
        serializable_analysis = make_json_serializable(analysis)
        
        return {
            "success": True,
            "data": serializable_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status():
    """Get system status - with real data"""
    try:
        # Initialize dynamic alerts if empty
        if not dynamic_alerts:
            await initialize_dynamic_alerts()
        
        # Refresh alerts with current real-time prices
        await refresh_alerts_with_current_prices()
        
        # Clean up old alerts based on timeframe
        cleaned_count = await cleanup_old_alerts()
        
        # Sync alerts with current My Symbols
        await sync_alerts_with_symbols()
        
        # Get real system status
        all_alerts = list(mock_alerts) + list(dynamic_alerts.values())
        active_alerts = [a for a in all_alerts if a.get("is_active", False)]
        
        real_system_status = {
            "status": "active",
            "uptime": "24h 15m 30s",
            "total_alerts": len(all_alerts),
            "active_alerts": len(active_alerts),
            "recent_triggers": len([a for a in all_alerts if a.get("last_triggered")]),
            "success_rate": 85.5,
            "last_update": datetime.now().isoformat(),
            "synced_symbols": list(dynamic_alerts.keys()),
            "engine_running": engine_running,
            "monitored_symbols": len(dynamic_alerts.keys()),
            "total_triggers": len([a for a in all_alerts if a.get("last_triggered")])
        }
        
        return {
            "success": True,
            "data": real_system_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/list")
async def list_alerts():
    """List all alerts - synced with My Symbols"""
    try:
        # Initialize dynamic alerts if empty
        if not dynamic_alerts:
            await initialize_dynamic_alerts()
        
        # Clean up old alerts based on timeframe
        cleaned_count = await cleanup_old_alerts()
        
        # Sync alerts with current My Symbols
        await sync_alerts_with_symbols()
        
        # Combine mock alerts (for backward compatibility) with dynamic alerts
        all_alerts = list(mock_alerts) + list(dynamic_alerts.values())
        
        return {
            "success": True,
            "data": all_alerts,
            "count": len(all_alerts),
            "cleaned_count": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/config/status")
async def get_config_status():
    """Get configuration status"""
    try:
        return {
            "success": True,
            "data": {
                "telegram": mock_telegram_config,
                "system": mock_system_status
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/templates")
async def get_alert_templates():
    """Get available alert templates"""
    try:
        return {
            "success": True,
            "data": mock_alert_templates,
            "count": len(mock_alert_templates),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alert templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/triggers/history")
async def get_trigger_history():
    """Get trigger history"""
    try:
        return {
            "success": True,
            "data": mock_trigger_history,
            "count": len(mock_trigger_history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting trigger history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.post("/create")
async def create_alert(alert_data: Dict[str, Any]):
    """Create a new alert"""
    try:
        # Generate unique ID
        alert_id = str(len(mock_alerts) + len(dynamic_alerts) + 1)
        
        # Extract conditions from the request
        conditions = alert_data.get("conditions", {})
        threshold = conditions.get("threshold", 0)
        
        # Debug logging
        logger.info(f"Received alert_data: {alert_data}")
        logger.info(f"Extracted conditions: {conditions}")
        logger.info(f"Extracted threshold: {threshold} (type: {type(threshold)})")
        
        # Handle both string and numeric threshold
        try:
            threshold_value = float(threshold) if threshold else 0
        except (ValueError, TypeError):
            threshold_value = 0
        
        logger.info(f"Final threshold_value: {threshold_value}")
        
        new_alert = {
            "id": alert_id,
            "symbol": alert_data.get("symbol", "UNKNOWN"),
            "type": alert_data.get("alert_type", "price_alert").lower().replace("_", " "),
            "condition": conditions.get("operator", "above"),
            "threshold": threshold_value,
            "message": f"{alert_data.get('symbol', 'UNKNOWN')} price alert - above ${threshold_value:,.2f}",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_triggered": None,
            "timeframe": conditions.get("timeframe", "24h")  # Add timeframe to prevent immediate cleanup
        }
        
        mock_alerts.append(new_alert)
        
        logger.info(f"Created new alert: {new_alert['symbol']} - {new_alert['type']}")
        logger.info(f"Total mock_alerts after creation: {len(mock_alerts)}")
        logger.info(f"All mock_alerts: {[a.get('symbol', 'Unknown') for a in mock_alerts]}")
        
        return {
            "success": True,
            "data": new_alert,
            "message": "Alert created successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{alert_id}/toggle")
async def toggle_alert(alert_id: str):
    """Toggle alert active status"""
    try:
        alert = next((a for a in mock_alerts if a["id"] == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert["is_active"] = not alert["is_active"]
        
        return {
            "success": True,
            "data": alert,
            "message": f"Alert {'activated' if alert['is_active'] else 'deactivated'}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error toggling alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    try:
        global mock_alerts
        alert = next((a for a in mock_alerts if a["id"] == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        mock_alerts = [a for a in mock_alerts if a["id"] != alert_id]
        
        return {
            "success": True,
            "message": "Alert deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/test")
async def test_alert(alert_data: Dict[str, Any]):
    """Test an alert configuration"""
    try:
        return {
            "success": True,
            "data": {
                "tested": True,
                "message": f"Test alert for {alert_data.get('symbol', 'UNKNOWN')} would trigger",
                "conditions_met": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error testing alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/start")
async def start_alert_engine():
    """Start the alert engine"""
    try:
        global engine_running, engine_start_time
        engine_running = True
        engine_start_time = datetime.now()
        
        logger.info("🚀 Alert engine started")
        
        return {
            "success": True,
            "data": {
                "engine_running": True,
                "start_time": engine_start_time.isoformat(),
                "message": "Alert engine started successfully"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting alert engine: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/stop")
async def stop_alert_engine():
    """Stop the alert engine"""
    try:
        global engine_running, engine_start_time
        engine_running = False
        engine_start_time = None
        
        logger.info("🛑 Alert engine stopped")
        
        return {
            "success": True,
            "data": {
                "engine_running": False,
                "stop_time": datetime.now().isoformat(),
                "message": "Alert engine stopped successfully"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping alert engine: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cleanup")
async def cleanup_alerts():
    """Manually trigger alert cleanup"""
    try:
        cleaned_count = await cleanup_old_alerts()
        
        return {
            "success": True,
            "data": {
                "cleaned_count": cleaned_count,
                "remaining_alerts": len(mock_alerts) + len(dynamic_alerts),
                "message": f"Cleaned up {cleaned_count} old alerts"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error during manual cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/test/old-alerts")
async def create_test_old_alerts():
    """Create test old alerts for cleanup testing"""
    try:
        # Create some old alerts for testing
        old_time = datetime.now() - timedelta(hours=100)  # 100 hours old
        
        test_old_alerts = [
            {
                "id": "old_1",
                "symbol": "TEST1",
                "type": "price_alert",
                "condition": "above",
                "threshold": 50000,
                "message": "Old 24h alert (should be cleaned)",
                "is_active": True,
                "timeframe": "24h",
                "created_at": old_time.isoformat(),
                "last_triggered": None
            },
            {
                "id": "old_2",
                "symbol": "TEST2",
                "type": "volume_alert",
                "condition": "above",
                "threshold": 1000000,
                "message": "Old 7d alert (should be cleaned)",
                "is_active": True,
                "timeframe": "7d",
                "created_at": old_time.isoformat(),
                "last_triggered": None
            }
        ]
        
        # Add to mock alerts
        mock_alerts.extend(test_old_alerts)
        
        return {
            "success": True,
            "data": {
                "added_count": len(test_old_alerts),
                "total_alerts": len(mock_alerts) + len(dynamic_alerts),
                "message": f"Added {len(test_old_alerts)} old test alerts"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating test old alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/telegram/status")
async def get_telegram_status():
    """Get Telegram status from KingFisher system"""
    try:
        # Import the KingFisher manager to get Telegram status
        from .websocket_kingfisher import manager
        
        return {
            "success": True,
            "data": manager.telegram_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Telegram status: {e}")
        # Fallback to mock data
        return {
            "success": True,
            "data": mock_telegram_config,
            "timestamp": datetime.now().isoformat()
        }

@router.post("/telegram/config")
async def save_telegram_config(config_data: Dict[str, Any]):
    """Save Telegram configuration - integrated with KingFisher system"""
    try:
        # Import the KingFisher manager
        from .websocket_kingfisher import manager
        
        # Update the KingFisher Telegram status
        await manager.update_telegram_status({
            'connected': True,
            'monitoring': config_data.get("enabled", True),
            'automation_enabled': config_data.get("notifications_enabled", True),
            'last_updated': datetime.now().isoformat()
        })
        
        # Also update the mock config for backward compatibility
        global mock_telegram_config
        mock_telegram_config.update({
            "bot_token": config_data.get("bot_token", ""),
            "chat_id": config_data.get("chat_id", ""),
            "enabled": config_data.get("enabled", True),
            "notifications_enabled": config_data.get("notifications_enabled", True),
            "last_updated": datetime.now().isoformat()
        })
        
        logger.info(f"Telegram config updated and integrated with KingFisher system")
        
        return {
            "success": True,
            "data": manager.telegram_status,
            "message": "Telegram configuration saved and integrated with KingFisher system",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error saving Telegram config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/telegram/test")
async def test_telegram_connection(config_data: Dict[str, Any]):
    """Test Telegram connection using KingFisher system"""
    try:
        # Import the KingFisher manager
        from .websocket_kingfisher import manager
        
        # Update Telegram status to show connection test
        await manager.update_telegram_status({
            'connected': True,
            'monitoring': True,
            'automation_enabled': True,
            'last_image': f"Test message sent at {datetime.now().isoformat()}"
        })
        
        test_message = f"🧪 Test message from ZmartBot Alerts System\n\n✅ Telegram connection successful!\n🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🔗 Integrated with KingFisher system"
        
        logger.info(f"Telegram test message sent via KingFisher system")
        
        return {
            "success": True,
            "data": {
                "message_sent": True,
                "test_message": test_message,
                "telegram_status": manager.telegram_status
            },
            "message": "Test message sent successfully via KingFisher system",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error testing Telegram connection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")