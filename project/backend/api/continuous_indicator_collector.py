#!/usr/bin/env python3
"""
Continuous Indicator Collector
Keeps the IndicatorHistory database continuously updated with new snapshots
"""

import sqlite3
import requests
import json
import time
import logging
from datetime import datetime
import uuid
import asyncio
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContinuousIndicatorCollector:
    """Continuous collection of indicator data"""
    
    def __init__(self):
        self.db_path = "/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/data/indicators_history.db"
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
        self.timeframes = ["15m", "1h", "4h", "1d"]
        self.collection_interval = 300  # 5 minutes
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📤 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start_continuous_collection(self):
        """Start continuous data collection"""
        logger.info("🚀 Starting continuous indicator collection...")
        logger.info(f"📊 Monitoring {len(self.symbols)} symbols across {len(self.timeframes)} timeframes")
        logger.info(f"⏱️ Collection interval: {self.collection_interval} seconds")
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"🔄 Collection cycle #{cycle_count} starting...")
                
                start_time = time.time()
                collected = await self.collect_batch()
                end_time = time.time()
                
                duration = end_time - start_time
                logger.info(f"✅ Cycle #{cycle_count} complete: {collected} snapshots in {duration:.2f}s")
                
                # Update cycle statistics
                self.update_statistics(collected, duration)
                
                # Wait for next collection
                if self.running:
                    logger.info(f"⏳ Waiting {self.collection_interval} seconds until next collection...")
                    await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in collection cycle #{cycle_count}: {e}")
                # Wait before retrying on error
                if self.running:
                    await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("🛑 Continuous collection stopped")
    
    async def collect_batch(self):
        """Collect indicators for all symbols and timeframes"""
        collected_count = 0
        
        for symbol in self.symbols:
            if not self.running:
                break
                
            try:
                # Get current price data
                price_data = self.get_price_data(symbol)
                if not price_data:
                    continue
                
                # Collect for each timeframe
                for timeframe in self.timeframes:
                    if not self.running:
                        break
                    
                    try:
                        # Create snapshot with real data
                        snapshot = {
                            'id': str(uuid.uuid4()),
                            'symbol': symbol,
                            'timestamp': datetime.now().isoformat(),
                            'timeframe': timeframe,
                            'price': float(price_data.get('lastPrice', 0)),
                            'volume': float(price_data.get('volume', 0)),
                            'volume_24h': float(price_data.get('quoteVolume', 0)),
                            'rsi': self.calculate_simple_rsi(symbol, price_data),
                            'macd': 0.0,  # Simplified
                            'trend_direction': self.determine_trend(price_data),
                            'signal_strength': self.calculate_signal_strength(price_data),
                            'data_source': 'continuous_collection',
                            'analysis_version': 'v1.0'
                        }
                        
                        self.save_snapshot(snapshot)
                        collected_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error collecting {symbol} {timeframe}: {e}")
                        continue
                
                # Small delay between symbols to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        return collected_count
    
    def get_price_data(self, symbol):
        """Get price data from Binance API"""
        try:
            response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"⚠️ Price API error for {symbol}: {e}")
        return None
    
    def calculate_simple_rsi(self, symbol, price_data):
        """Calculate simplified RSI based on price change"""
        try:
            price_change_pct = float(price_data.get('priceChangePercent', 0))
            
            # Simple RSI approximation based on price change
            if price_change_pct > 5:
                return 70.0  # Overbought
            elif price_change_pct < -5:
                return 30.0  # Oversold
            else:
                return 50.0 + (price_change_pct * 2)  # Neutral with slight bias
                
        except:
            return 50.0
    
    def determine_trend(self, price_data):
        """Determine trend direction"""
        try:
            price_change = float(price_data.get('priceChangePercent', 0))
            if price_change > 2:
                return 'bullish'
            elif price_change < -2:
                return 'bearish'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def calculate_signal_strength(self, price_data):
        """Calculate signal strength"""
        try:
            price_change = abs(float(price_data.get('priceChangePercent', 0)))
            volume_change = float(price_data.get('volume', 1))
            
            # Normalize signal strength (0-1)
            strength = min(price_change / 10.0, 1.0)  # Max at 10% change
            return round(strength, 3)
        except:
            return 0.5
    
    def save_snapshot(self, snapshot):
        """Save snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO indicator_snapshots (
                    id, symbol, timestamp, timeframe,
                    rsi, macd, price, volume, volume_24h,
                    trend_direction, signal_strength,
                    data_source, analysis_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot['id'], snapshot['symbol'], snapshot['timestamp'], snapshot['timeframe'],
                snapshot['rsi'], snapshot['macd'], snapshot['price'], snapshot['volume'], snapshot['volume_24h'],
                snapshot['trend_direction'], snapshot['signal_strength'],
                snapshot['data_source'], snapshot['analysis_version'], datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error saving snapshot: {e}")
            raise
    
    def update_statistics(self, snapshots_count, duration):
        """Update collection statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT OR REPLACE INTO collection_stats 
                (date, snapshots_created, avg_processing_time) 
                VALUES (?, 
                    COALESCE((SELECT snapshots_created FROM collection_stats WHERE date = ?), 0) + ?, 
                    ?)
            ''', (today, today, snapshots_count, duration))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Error updating statistics: {e}")
    
    def get_status(self):
        """Get current collection status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM indicator_snapshots")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(timestamp) FROM indicator_snapshots")
            latest = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM indicator_snapshots WHERE date(timestamp) = date('now')")
            today = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_snapshots': total,
                'latest_snapshot': latest,
                'today_snapshots': today,
                'status_time': datetime.now().isoformat()
            }
        except:
            return {}

def main():
    """Main function"""
    collector = ContinuousIndicatorCollector()
    
    print("🔄 CONTINUOUS INDICATOR COLLECTION")
    print("=================================")
    
    status = collector.get_status()
    print(f"📊 Current Status:")
    print(f"   Total Snapshots: {status.get('total_snapshots', 0)}")
    print(f"   Today's Snapshots: {status.get('today_snapshots', 0)}")
    print(f"   Latest: {status.get('latest_snapshot', 'None')}")
    print(f"\n🚀 Starting continuous collection...")
    print(f"   Press Ctrl+C to stop gracefully")
    
    # Run the continuous collection
    try:
        asyncio.run(collector.start_continuous_collection())
    except KeyboardInterrupt:
        print("\n🛑 Collection stopped by user")
    except Exception as e:
        print(f"\n❌ Collection error: {e}")

if __name__ == "__main__":
    main()