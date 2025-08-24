#!/usr/bin/env python3
"""
Restart Indicator Collection System
Manually triggers data collection for all symbols to ensure continuous operation
"""

import sqlite3
import requests
import json
import logging
from datetime import datetime
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualIndicatorCollector:
    """Manual indicator collection to restart the system"""
    
    def __init__(self):
        self.db_path = "/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/data/indicators_history.db"
        self.api_base = "http://localhost:8000"
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
        self.timeframes = ["15m", "1h", "4h", "1d"]
    
    def collect_current_indicators(self):
        """Collect current indicator snapshots for all symbols"""
        logger.info("🚀 Starting manual indicator collection...")
        
        collected_count = 0
        
        for symbol in self.symbols:
            logger.info(f"📊 Collecting data for {symbol}...")
            
            try:
                # Get current price data
                price_data = self._get_price_data(symbol)
                if not price_data:
                    continue
                
                # Get technical indicators for each timeframe
                for timeframe in self.timeframes:
                    try:
                        indicators = self._get_indicators(symbol, timeframe)
                        
                        # Create snapshot
                        snapshot_data = {
                            'id': str(uuid.uuid4()),
                            'symbol': symbol,
                            'timestamp': datetime.now().isoformat(),
                            'timeframe': timeframe,
                            'price': float(price_data.get('lastPrice', 0)),
                            'volume': float(price_data.get('volume', 0)),
                            'volume_24h': float(price_data.get('quoteVolume', 0)),
                            'rsi': indicators.get('rsi', 50.0),
                            'macd': indicators.get('macd', 0.0),
                            'macd_signal': indicators.get('macd_signal', 0.0),
                            'ema_21': indicators.get('ema_21', 0.0),
                            'sma_20': indicators.get('sma_20', 0.0),
                            'bollinger_upper': indicators.get('bollinger_upper', 0.0),
                            'bollinger_middle': indicators.get('bollinger_middle', 0.0),
                            'bollinger_lower': indicators.get('bollinger_lower', 0.0),
                            'trend_direction': 'neutral',
                            'signal_strength': 0.5,
                            'data_source': 'manual_restart',
                            'analysis_version': 'v1.0'
                        }
                        
                        # Save to database
                        self._save_snapshot(snapshot_data)
                        collected_count += 1
                        
                        logger.info(f"✅ Saved {symbol} {timeframe} snapshot")
                        
                    except Exception as e:
                        logger.error(f"❌ Error collecting {symbol} {timeframe}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        logger.info(f"🎯 Manual collection complete! Collected {collected_count} snapshots")
        return collected_count
    
    def _get_price_data(self, symbol):
        """Get current price data from Binance API"""
        try:
            response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Error getting price data for {symbol}: {e}")
        return None
    
    def _get_indicators(self, symbol, timeframe):
        """Get technical indicators (simplified for restart)"""
        try:
            # Try to get from our API first
            response = requests.get(f"{self.api_base}/api/v1/alerts/enhanced/state/{symbol}?timeframe={timeframe}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('data', {}).get('indicators'):
                    indicators_data = data['data']['indicators']
                    return {
                        'rsi': self._extract_indicator_value(indicators_data.get('rsi')),
                        'macd': self._extract_indicator_value(indicators_data.get('macd')),
                        'macd_signal': 0.0,
                        'ema_21': 0.0,
                        'sma_20': 0.0,
                        'bollinger_upper': 0.0,
                        'bollinger_middle': 0.0,
                        'bollinger_lower': 0.0
                    }
        except Exception as e:
            logger.warning(f"⚠️ Could not get indicators from API for {symbol}: {e}")
        
        # Return default values if API is unavailable
        return {
            'rsi': 50.0,
            'macd': 0.0,
            'macd_signal': 0.0,
            'ema_21': 0.0,
            'sma_20': 0.0,
            'bollinger_upper': 0.0,
            'bollinger_middle': 0.0,
            'bollinger_lower': 0.0
        }
    
    def _extract_indicator_value(self, indicator_data):
        """Extract numeric value from indicator data"""
        if not indicator_data:
            return 0.0
        
        if isinstance(indicator_data, dict):
            fields = indicator_data.get('fields', {})
            if 'Value' in fields:
                try:
                    return float(fields['Value'])
                except (ValueError, TypeError):
                    return 0.0
        
        return 0.0
    
    def _save_snapshot(self, snapshot_data):
        """Save snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO indicator_snapshots (
                    id, symbol, timestamp, timeframe,
                    rsi, macd, macd_signal, ema_21, sma_20,
                    bollinger_upper, bollinger_middle, bollinger_lower,
                    price, volume, volume_24h,
                    trend_direction, signal_strength,
                    data_source, analysis_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_data['id'], snapshot_data['symbol'], snapshot_data['timestamp'], snapshot_data['timeframe'],
                snapshot_data['rsi'], snapshot_data['macd'], snapshot_data['macd_signal'], 
                snapshot_data['ema_21'], snapshot_data['sma_20'],
                snapshot_data['bollinger_upper'], snapshot_data['bollinger_middle'], snapshot_data['bollinger_lower'],
                snapshot_data['price'], snapshot_data['volume'], snapshot_data['volume_24h'],
                snapshot_data['trend_direction'], snapshot_data['signal_strength'],
                snapshot_data['data_source'], snapshot_data['analysis_version'], datetime.now().isoformat()
            ))
            
            # Update tracked symbols
            cursor.execute('''
                UPDATE tracked_symbols 
                SET last_snapshot = ?, total_snapshots = total_snapshots + 1
                WHERE symbol = ?
            ''', (snapshot_data['timestamp'], snapshot_data['symbol']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error saving snapshot: {e}")
            raise
    
    def get_collection_status(self):
        """Get current collection status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM indicator_snapshots")
            total_snapshots = cursor.fetchone()[0]
            
            cursor.execute("SELECT symbol, MAX(timestamp), COUNT(*) FROM indicator_snapshots GROUP BY symbol")
            symbol_stats = cursor.fetchall()
            
            cursor.execute("SELECT MAX(timestamp) FROM indicator_snapshots")
            latest_snapshot = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_snapshots': total_snapshots,
                'symbol_stats': symbol_stats,
                'latest_snapshot': latest_snapshot,
                'check_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection status: {e}")
            return {}

def main():
    """Main function"""
    collector = ManualIndicatorCollector()
    
    print("🔄 INDICATOR COLLECTION RESTART")
    print("==============================")
    
    # Get current status
    status = collector.get_collection_status()
    print(f"📊 Current Status:")
    print(f"   Total Snapshots: {status.get('total_snapshots', 0)}")
    print(f"   Latest Snapshot: {status.get('latest_snapshot', 'None')}")
    
    # Collect new data
    collected = collector.collect_current_indicators()
    
    # Get updated status
    updated_status = collector.get_collection_status()
    print(f"\n✅ Updated Status:")
    print(f"   Total Snapshots: {updated_status.get('total_snapshots', 0)}")
    print(f"   Latest Snapshot: {updated_status.get('latest_snapshot', 'None')}")
    print(f"   New Snapshots: {collected}")
    
    print("\n🎉 Indicator collection restarted successfully!")

if __name__ == "__main__":
    main()