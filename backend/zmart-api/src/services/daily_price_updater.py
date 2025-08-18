#!/usr/bin/env python3
"""
Daily Price History Updater
Updates all symbol price history files with the latest daily data
Runs once per day to keep all files current
"""

import os
import asyncio
import aiohttp
import sqlite3
import json
import logging
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import time
import schedule

logger = logging.getLogger(__name__)

class DailyPriceUpdater:
    """Updates all symbol price history files with latest daily data"""
    
    def __init__(self, history_data_path: Optional[str] = None, db_path: Optional[str] = None):
        self.history_data_path = history_data_path or "/Users/dansidanutz/Desktop/ZmartBot/Symbol_Price_history_data"
        self.db_path = db_path or "/Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api/my_symbols_v2.db"
        
        # CoinGecko API mapping
        self.symbol_to_coingecko = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'SOLUSDT': 'solana',
            'AVAXUSDT': 'avalanche-2',
            'ADAUSDT': 'cardano',
            'XRPUSDT': 'ripple',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'BNBUSDT': 'binancecoin',
            'DOGEUSDT': 'dogecoin',
            'AAVEUSDT': 'aave',
            'ATOMUSDT': 'cosmos',
            'HBARUSDT': 'hedera-hashgraph',
            'MKRUSDT': 'maker',
            'TRXUSDT': 'tron',
            'XTZUSDT': 'tezos',
            'LTCUSDT': 'litecoin',
            'BCHUSDT': 'bitcoin-cash',
            'UNIUSDT': 'uniswap',
            'FILUSDT': 'filecoin',
            'NEARUSDT': 'near',
            'ALGOUSDT': 'algorand',
            'VETUSDT': 'vechain',
            'ICPUSDT': 'internet-computer',
            'FTMUSDT': 'fantom',
            'MANAUSDT': 'decentraland',
            'SANDUSDT': 'the-sandbox',
            'AXSUSDT': 'axie-infinity',
            'GALAUSDT': 'gala',
            'CHZUSDT': 'chiliz',
            'HOTUSDT': 'holochain',
            'ENJUSDT': 'enjincoin',
            'BATUSDT': 'basic-attention-token',
            'ZILUSDT': 'zilliqa',
            'ONEUSDT': 'harmony',
            'IOTAUSDT': 'iota',
            'NEOUSDT': 'neo',
            'QTUMUSDT': 'qtum',
            'WAVESUSDT': 'waves',
            'DASHUSDT': 'dash',
            'ZECUSDT': 'zcash',
            'XMRUSDT': 'monero',
            'ETCUSDT': 'ethereum-classic',
            'XLMUSDT': 'stellar',
            'EOSUSDT': 'eos'
        }
        
        # Binance API mapping (for fallback)
        self.symbol_to_binance = {
            'BTCUSDT': 'BTCUSDT',
            'ETHUSDT': 'ETHUSDT',
            'SOLUSDT': 'SOLUSDT',
            'AVAXUSDT': 'AVAXUSDT',
            'ADAUSDT': 'ADAUSDT',
            'XRPUSDT': 'XRPUSDT',
            'DOTUSDT': 'DOTUSDT',
            'LINKUSDT': 'LINKUSDT',
            'BNBUSDT': 'BNBUSDT',
            'DOGEUSDT': 'DOGEUSDT',
            'AAVEUSDT': 'AAVEUSDT',
            'ATOMUSDT': 'ATOMUSDT',
            'HBARUSDT': 'HBARUSDT',
            'MKRUSDT': 'MKRUSDT',
            'TRXUSDT': 'TRXUSDT',
            'XTZUSDT': 'XTZUSDT',
            'LTCUSDT': 'LTCUSDT',
            'BCHUSDT': 'BCHUSDT',
            'UNIUSDT': 'UNIUSDT',
            'FILUSDT': 'FILUSDT',
            'NEARUSDT': 'NEARUSDT',
            'ALGOUSDT': 'ALGOUSDT',
            'VETUSDT': 'VETUSDT',
            'ICPUSDT': 'ICPUSDT',
            'FTMUSDT': 'FTMUSDT',
            'MANAUSDT': 'MANAUSDT',
            'SANDUSDT': 'SANDUSDT',
            'AXSUSDT': 'AXSUSDT',
            'GALAUSDT': 'GALAUSDT',
            'CHZUSDT': 'CHZUSDT',
            'HOTUSDT': 'HOTUSDT',
            'ENJUSDT': 'ENJUSDT',
            'BATUSDT': 'BATUSDT',
            'ZILUSDT': 'ZILUSDT',
            'ONEUSDT': 'ONEUSDT',
            'IOTAUSDT': 'IOTAUSDT',
            'NEOUSDT': 'NEOUSDT',
            'QTUMUSDT': 'QTUMUSDT',
            'WAVESUSDT': 'WAVESUSDT',
            'DASHUSDT': 'DASHUSDT',
            'ZECUSDT': 'ZECUSDT',
            'XMRUSDT': 'XMRUSDT',
            'ETCUSDT': 'ETCUSDT',
            'XLMUSDT': 'XLMUSDT',
            'EOSUSDT': 'EOSUSDT'
        }
        
        # Ensure history data directory exists
        Path(self.history_data_path).mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        self.logs_path = Path(self.history_data_path) / "logs"
        self.logs_path.mkdir(exist_ok=True)
    
    async def get_my_symbols(self) -> List[str]:
        """Get all symbols from My Symbols database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT s.symbol FROM portfolio_composition pc JOIN symbols s ON pc.symbol_id = s.id WHERE pc.status = 'Active'"
            )
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
            return symbols
        except Exception as e:
            logger.error(f"❌ Failed to get symbols from database: {e}")
            return []
    
    def get_existing_files(self) -> Dict[str, str]:
        """Get mapping of symbols to their existing CSV files"""
        existing_files = {}
        
        for file in os.listdir(self.history_data_path):
            if file.endswith('.csv') and not file.startswith('.'):
                # Extract symbol from filename
                if 'coinmarketcap' in file:
                    # Format: Bitcoin_7_1_2008-7_1_2025_historical_data_coinmarketcap.csv
                    parts = file.replace('_historical_data_coinmarketcap.csv', '').split('_')
                    if len(parts) >= 2:
                        symbol_name = parts[0].upper()
                        if symbol_name == 'BITCOIN':
                            symbol = 'BTCUSDT'
                        elif symbol_name == 'ETHEREUM':
                            symbol = 'ETHUSDT'
                        elif symbol_name == 'SOLANA':
                            symbol = 'SOLUSDT'
                        elif symbol_name == 'AVALANCHE':
                            symbol = 'AVAXUSDT'
                        elif symbol_name == 'CARDANO':
                            symbol = 'ADAUSDT'
                        elif symbol_name == 'XRP':
                            symbol = 'XRPUSDT'
                        elif symbol_name == 'POLKADOT':
                            symbol = 'DOTUSDT'
                        elif symbol_name == 'CHAINLINK':
                            symbol = 'LINKUSDT'
                        elif symbol_name == 'BNB':
                            symbol = 'BNBUSDT'
                        elif symbol_name == 'DOGECOIN':
                            symbol = 'DOGEUSDT'
                        elif symbol_name == 'AAVE':
                            symbol = 'AAVEUSDT'
                        else:
                            symbol = f"{symbol_name}USDT"
                        existing_files[symbol] = file
                elif file.endswith('-usd-max.csv'):
                    # Format: atom-usd-max.csv
                    symbol_name = file.replace('-usd-max.csv', '').upper()
                    if symbol_name == 'ATOM':
                        symbol = 'ATOMUSDT'
                    elif symbol_name == 'HBAR':
                        symbol = 'HBARUSDT'
                    elif symbol_name == 'MKR':
                        symbol = 'MKRUSDT'
                    elif symbol_name == 'TRX':
                        symbol = 'TRXUSDT'
                    elif symbol_name == 'XTZ':
                        symbol = 'XTZUSDT'
                    else:
                        symbol = f"{symbol_name}USDT"
                    existing_files[symbol] = file
        
        return existing_files
    
    async def update_from_coingecko(self, symbol: str, days: int = 365) -> bool:
        """Update symbol data from CoinGecko API"""
        try:
            coingecko_id = self.symbol_to_coingecko.get(symbol)
            if not coingecko_id:
                logger.error(f"❌ No CoinGecko ID found for {symbol}")
                return False
            
            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Create filename
                        symbol_name = symbol.replace('USDT', '').lower()
                        filename = f"{symbol_name.capitalize()}_coingecko_{days}d_historical_data.csv"
                        file_path = os.path.join(self.history_data_path, filename)
                        
                        # Convert to CSV format
                        csv_content = self._convert_coingecko_to_csv(data, symbol)
                        
                        # Save file
                        with open(file_path, 'w') as f:
                            f.write(csv_content)
                        
                        logger.info(f"✅ Updated {symbol} from CoinGecko: {len(data['prices'])} records")
                        return True
                    else:
                        logger.error(f"❌ Failed to update {symbol} from CoinGecko: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error updating {symbol} from CoinGecko: {e}")
            return False
    
    async def update_from_binance(self, symbol: str, days: int = 365) -> bool:
        """Update symbol data from Binance API (fallback)"""
        try:
            binance_symbol = self.symbol_to_binance.get(symbol)
            if not binance_symbol:
                logger.error(f"❌ No Binance symbol found for {symbol}")
                return False
            
            # Calculate start time (days ago)
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': '1d',
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Create filename
                        symbol_name = symbol.replace('USDT', '').lower()
                        filename = f"{symbol_name.capitalize()}_binance_{days}d_historical_data.csv"
                        file_path = os.path.join(self.history_data_path, filename)
                        
                        # Convert to CSV format
                        csv_content = self._convert_binance_to_csv(data, symbol)
                        
                        # Save file
                        with open(file_path, 'w') as f:
                            f.write(csv_content)
                        
                        logger.info(f"✅ Updated {symbol} from Binance: {len(data)} records")
                        return True
                    else:
                        logger.error(f"❌ Failed to update {symbol} from Binance: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error updating {symbol} from Binance: {e}")
            return False
    
    def _convert_coingecko_to_csv(self, data: Dict, symbol: str) -> str:
        """Convert CoinGecko data to CSV format"""
        csv_lines = ['Date;Open;High;Low;Close;Volume;Market_Cap']
        
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        market_caps = data.get('market_caps', [])
        
        for i, (timestamp, price) in enumerate(prices):
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            
            # Get volume and market cap for this date
            volume = volumes[i][1] if i < len(volumes) else 0
            market_cap = market_caps[i][1] if i < len(market_caps) else 0
            
            # For daily data, use same price for OHLC
            csv_lines.append(f'{date};{price};{price};{price};{price};{volume};{market_cap}')
        
        return '\n'.join(csv_lines)
    
    def _convert_binance_to_csv(self, data: List, symbol: str) -> str:
        """Convert Binance data to CSV format"""
        csv_lines = ['Date;Open;High;Low;Close;Volume;Market_Cap']
        
        for candle in data:
            # Binance klines format: [open_time, open, high, low, close, volume, close_time, ...]
            date = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d')
            open_price = float(candle[1])
            high_price = float(candle[2])
            low_price = float(candle[3])
            close_price = float(candle[4])
            volume = float(candle[5])
            
            # Market cap not available from Binance klines, use 0
            market_cap = 0
            
            csv_lines.append(f'{date};{open_price};{high_price};{low_price};{close_price};{volume};{market_cap}')
        
        return '\n'.join(csv_lines)
    
    async def update_single_symbol(self, symbol: str) -> bool:
        """Update a single symbol with latest data"""
        try:
            logger.info(f"🔄 Updating {symbol}...")
            
            # Try CoinGecko first
            success = await self.update_from_coingecko(symbol, days=365)
            
            if not success:
                logger.warning(f"⚠️ CoinGecko failed for {symbol}, trying Binance...")
                success = await self.update_from_binance(symbol, days=365)
            
            if success:
                logger.info(f"✅ Successfully updated {symbol}")
            else:
                logger.error(f"❌ Failed to update {symbol} from both sources")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error updating {symbol}: {e}")
            return False
    
    async def update_all_symbols(self) -> Dict[str, bool]:
        """Update all symbols with latest data"""
        try:
            logger.info("🔄 Starting daily price update...")
            
            # Get symbols from database
            symbols = await self.get_my_symbols()
            if not symbols:
                logger.warning("⚠️ No symbols found in database")
                return {}
            
            logger.info(f"📊 Found {len(symbols)} symbols to update: {symbols}")
            
            results = {}
            for symbol in symbols:
                success = await self.update_single_symbol(symbol)
                results[symbol] = success
                
                # Rate limiting - CoinGecko allows 50 calls/minute
                await asyncio.sleep(1.2)
            
            # Log results
            success_count = sum(1 for success in results.values() if success)
            logger.info(f"✅ Daily update complete: {success_count}/{len(results)} symbols updated successfully")
            
            # Save update log
            self._save_update_log(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in daily update: {e}")
            return {}
    
    def _save_update_log(self, results: Dict[str, bool]):
        """Save update results to log file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file = self.logs_path / f"daily_update_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(log_file, 'a') as f:
                f.write(f"\n=== Daily Update {timestamp} ===\n")
                for symbol, success in results.items():
                    status = "✅ SUCCESS" if success else "❌ FAILED"
                    f.write(f"{symbol}: {status}\n")
                
                success_count = sum(1 for success in results.values() if success)
                f.write(f"Total: {success_count}/{len(results)} successful\n")
                f.write("=" * 50 + "\n")
                
        except Exception as e:
            logger.error(f"❌ Error saving update log: {e}")
    
    async def run_daily_update(self):
        """Run the daily update process"""
        logger.info("🌅 Starting daily price history update...")
        
        try:
            results = await self.update_all_symbols()
            
            # Send notification (you can add email/telegram notifications here)
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            logger.info(f"📊 Daily update summary: {success_count}/{total_count} symbols updated")
            
            if success_count < total_count:
                failed_symbols = [symbol for symbol, success in results.items() if not success]
                logger.warning(f"⚠️ Failed symbols: {failed_symbols}")
            
        except Exception as e:
            logger.error(f"❌ Daily update failed: {e}")

# Global instance
daily_updater = DailyPriceUpdater()

async def get_daily_updater() -> DailyPriceUpdater:
    """Get the global daily updater instance"""
    return daily_updater

def schedule_daily_update():
    """Schedule daily update to run at 00:05 every day"""
    schedule.every().day.at("00:05").do(lambda: asyncio.run(daily_updater.run_daily_update()))
    logger.info("📅 Scheduled daily update for 00:05 every day")

def run_scheduler():
    """Run the scheduler"""
    schedule_daily_update()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Run immediate update
    asyncio.run(daily_updater.run_daily_update())
