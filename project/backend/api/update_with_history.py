#!/usr/bin/env python3
"""
ZmartBot Comprehensive Symbol Data Updater with Historical Storage
Updates all symbols with real-time data, caches results, and stores historical snapshots
for pattern analysis and historical trend analysis.
"""

import asyncio
import sys
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

# Import the main updater
from update_all_symbols_realtime import RealTimeSymbolUpdater

# Import historical data service
try:
    from historical_data_service import historical_data_service
    HISTORICAL_AVAILABLE = True
except ImportError:
    historical_data_service = None
    HISTORICAL_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveSymbolUpdater:
    def __init__(self, cache_duration: int = 3600):
        self.updater = RealTimeSymbolUpdater(cache_duration=cache_duration)
        self.historical_available = HISTORICAL_AVAILABLE
        
    async def update_all_symbols_with_history(self):
        """Update all symbols with real-time data and store historical snapshots"""
        try:
            logger.info("🚀 Starting Comprehensive Symbol Data Update")
            logger.info(f"📊 Historical Storage: {'✅ Available' if self.historical_available else '❌ Not Available'}")
            
            # Get symbols from database
            symbols = await self.updater.get_symbols_from_database()
            if not symbols:
                logger.error("No symbols found in database")
                return
            
            logger.info(f"📈 Updating {len(symbols)} symbols with historical storage")
            
            # Create session for HTTP requests
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Update symbols with rate limiting
                semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
                
                async def update_with_semaphore(symbol):
                    async with semaphore:
                        return await self.update_symbol_with_history(session, symbol)
                
                # Run updates concurrently
                tasks = [update_with_semaphore(symbol) for symbol in symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes
                successful = sum(1 for result in results if result is True)
                failed = len(results) - successful
                
                logger.info(f"✅ Comprehensive update completed: {successful} successful, {failed} failed")
                
                # Save cache after successful update
                self.updater.save_cache()
                
        except Exception as e:
            logger.error(f"Error in comprehensive update: {e}")
    
    async def update_symbol_with_history(self, session, symbol: str) -> bool:
        """Update a single symbol with real-time data and store historical snapshot"""
        try:
            symbol_id = self.updater.get_symbol_id(symbol)
            if not symbol_id:
                logger.error(f"Symbol ID not found for {symbol}")
                return False
            
            logger.info(f"🔄 Updating {symbol} with historical storage")
            
            # Get current price
            current_price = await self.updater.get_current_price(session, symbol)
            if not current_price:
                logger.error(f"Failed to get current price for {symbol}")
                return False
            
            # Update for each timeframe
            for timeframe in self.updater.timeframes:
                interval = self.updater.timeframe_intervals[timeframe]
                cache_key = self.updater.get_cache_key(symbol, timeframe)
                
                # Check if we have valid cached data
                if self.updater.is_cache_valid(cache_key):
                    logger.info(f"📋 Using cached data for {symbol} {timeframe}")
                    cached_data = self.updater.cache[cache_key]['data']
                    await self.updater.update_database_tables(symbol_id, symbol, timeframe, cached_data, current_price)
                    
                    # Store historical snapshot from cache
                    if self.historical_available:
                        historical_data_service.store_historical_snapshot(symbol, timeframe, cached_data, current_price)
                    continue
                
                # Fetch fresh data from Binance
                logger.info(f"🌐 Fetching fresh data for {symbol} {timeframe}")
                df = await self.updater.fetch_binance_klines(session, symbol, interval)
                if df is None or df.empty:
                    logger.warning(f"No data for {symbol} {timeframe}")
                    continue
                
                # Calculate indicators
                indicators = self.updater.calculate_technical_indicators(df)
                if not indicators:
                    logger.warning(f"No indicators calculated for {symbol} {timeframe}")
                    continue
                
                # Cache the calculated data
                self.updater.update_cache(cache_key, indicators)
                
                # Update database
                await self.updater.update_database_tables(symbol_id, symbol, timeframe, indicators, current_price)
                
                # Store historical snapshot
                if self.historical_available:
                    historical_data_service.store_historical_snapshot(symbol, timeframe, indicators, current_price)
            
            logger.info(f"✅ Successfully updated {symbol} with historical storage")
            return True
            
        except Exception as e:
            logger.error(f"Error updating {symbol} with history: {e}")
            return False

async def main():
    """Main function"""
    logger.info("🚀 Starting Comprehensive Symbol Data Update with Historical Storage")
    
    # Cache duration: 1 hour (3600 seconds)
    comprehensive_updater = ComprehensiveSymbolUpdater(cache_duration=3600)
    await comprehensive_updater.update_all_symbols_with_history()
    
    logger.info("✅ Comprehensive Symbol Data Update completed")

if __name__ == "__main__":
    asyncio.run(main())
