#!/usr/bin/env python3
"""
Populate Symbols Database Script
Loads all valid futures symbols from both KuCoin and Binance into the database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.futures_symbol_validator import get_futures_validator
from src.services.my_symbols_service_v2 import MySymbolsServiceV2
import sqlite3
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def populate_symbols_database():
    """Populate the database with all valid futures symbols"""
    
    try:
        logger.info("🚀 Starting database population...")
        
        # Get the futures validator
        validator = await get_futures_validator()
        await validator.initialize()
        
        # Get the My Symbols service
        service = MySymbolsServiceV2()
        
        # Get all common symbols (available on both exchanges)
        common_symbols = await validator.get_common_futures_symbols()
        logger.info(f"📊 Found {len(common_symbols)} common symbols")
        
        # Connect to database
        conn = sqlite3.connect(service.db_path)
        cursor = conn.cursor()
        
        # Get existing symbols to avoid duplicates
        cursor.execute("SELECT symbol FROM symbols")
        existing_symbols = {row[0] for row in cursor.fetchall()}
        logger.info(f"📊 Found {len(existing_symbols)} existing symbols in database")
        
        added_count = 0
        skipped_count = 0
        
        for symbol in common_symbols:
            if symbol in existing_symbols:
                skipped_count += 1
                continue
                
            try:
                # Get symbol info from validator
                symbol_info = await validator.get_symbol_info(symbol)
                
                if not symbol_info:
                    logger.warning(f"⚠️ No info found for {symbol}, skipping")
                    skipped_count += 1
                    continue
                
                # Check if symbol is tradeable on KuCoin
                is_kucoin_tradeable = await validator.is_tradeable_on_kucoin(symbol)
                is_binance_available = symbol in validator.binance_symbols
                
                if not is_kucoin_tradeable:
                    logger.warning(f"⚠️ {symbol} not tradeable on KuCoin, skipping")
                    skipped_count += 1
                    continue
                
                # Insert symbol into database
                symbol_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO symbols (
                        id, symbol, root_symbol, base_currency, quote_currency, settle_currency,
                        contract_type, lot_size, tick_size, max_order_qty, max_price, multiplier,
                        initial_margin, maintain_margin, max_leverage, status,
                        is_kucoin_tradeable, is_binance_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol_id,
                    symbol,
                    symbol_info.base_asset,
                    symbol_info.base_asset,
                    symbol_info.quote_asset,
                    symbol_info.quote_asset,
                    symbol_info.contract_type,
                    symbol_info.min_qty,
                    symbol_info.tick_size,
                    int(symbol_info.max_qty),
                    1000000.0,  # max_price
                    1.0,        # multiplier
                    symbol_info.maintainance_margin,
                    symbol_info.maintainance_margin,
                    symbol_info.max_leverage,
                    'Active',
                    is_kucoin_tradeable,
                    is_binance_available
                ))
                
                added_count += 1
                logger.info(f"✅ Added {symbol} - KuCoin: {'✓' if is_kucoin_tradeable else '✗'}, Binance: {'✓' if is_binance_available else '✗'}")
                
            except Exception as e:
                logger.error(f"❌ Error adding {symbol}: {e}")
                skipped_count += 1
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Database population complete!")
        logger.info(f"✅ Added: {added_count} symbols")
        logger.info(f"⏭️ Skipped: {skipped_count} symbols")
        logger.info(f"📊 Total symbols in database: {len(existing_symbols) + added_count}")
        
        # Verify some specific symbols
        verify_symbols = ['ATOMUSDT', 'WIFUSDT', 'LINKUSDT', 'UNIUSDT']
        conn = sqlite3.connect(service.db_path)
        cursor = conn.cursor()
        
        logger.info("\n🔍 Verification of specific symbols:")
        for symbol in verify_symbols:
            cursor.execute("SELECT symbol, is_kucoin_tradeable, is_binance_available FROM symbols WHERE symbol = ?", (symbol,))
            result = cursor.fetchone()
            if result:
                logger.info(f"✅ {symbol}: KuCoin={result[1]}, Binance={result[2]}")
            else:
                logger.warning(f"❌ {symbol}: Not found in database")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to populate database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_symbols_database())
