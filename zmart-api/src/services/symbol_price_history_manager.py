import os
import asyncio
import aiohttp
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SymbolPriceHistoryDataManager:
    """Manages historical price data for symbols in My Symbols database"""
    
    def __init__(self, history_data_path: Optional[str] = None, db_path: Optional[str] = None):
        self.history_data_path = history_data_path or "/Users/dansidanutz/Desktop/ZmartBot/Symbol_Price_history_data"
        self.db_path = db_path or "/Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api/my_symbols_v2.db"
        
        # Symbol to filename mapping
        self.symbol_to_file = {
            'BTCUSDT': 'Bitcoin_7_1_2008-7_1_2025_historical_data_coinmarketcap.csv',
            'ETHUSDT': 'Ethereum_1_1_2010-7_1_2025_historical_data_coinmarketcap.csv',
            'SOLUSDT': 'Solana_5_10_2006-7_1_2025_historical_data_coinmarketcap.csv',
            'AVAXUSDT': 'Avalanche_5_1_2017-7_1_2025_historical_data_coinmarketcap.csv',
            'ADAUSDT': 'Cardano_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
            'XRPUSDT': 'XRP_2_1_2006-7_1_2025_historical_data_coinmarketcap.csv',
            'DOTUSDT': 'Polkadot_1_1_2014-7_1_2025_historical_data_coinmarketcap.csv',
            'LINKUSDT': 'Chainlink_5_11_2011-7_1_2025_historical_data_coinmarketcap.csv',
            'BNBUSDT': 'BNB_1_1_2013-7_1_2025_historical_data_coinmarketcap.csv',
            'DOGEUSDT': 'Dogecoin_5_1_2011-7_1_2025_historical_data_coinmarketcap.csv',
            'AAVEUSDT': 'Aave_5_1_2010-7_1_2025_historical_data_coinmarketcap.csv',
            'ATOMUSDT': 'atom-usd-max.csv',
            'HBARUSDT': 'hbar-usd-max.csv',
            'MKRUSDT': 'mkr-usd-max.csv',
            'TRXUSDT': 'trx-usd-max.csv',
            'XTZUSDT': 'xtz-usd-max.csv'
        }
        
        # CoinGecko API mapping for symbols not in existing files
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
            'MATICUSDT': 'matic-network',
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
            'EOSUSDT': 'eos',
            'ADAUSDT': 'cardano',
            'TRXUSDT': 'tron',
            'LINKUSDT': 'chainlink',
            'DOTUSDT': 'polkadot',
            'LTCUSDT': 'litecoin',
            'BCHUSDT': 'bitcoin-cash',
            'XRPUSDT': 'ripple',
            'BNBUSDT': 'binancecoin',
            'ETHUSDT': 'ethereum',
            'BTCUSDT': 'bitcoin'
        }
        
        # Ensure history data directory exists
        Path(self.history_data_path).mkdir(parents=True, exist_ok=True)
    
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
    
    def check_existing_files(self) -> Dict[str, bool]:
        """Check which data files exist for symbols"""
        existing_files = {}
        
        for symbol, filename in self.symbol_to_file.items():
            file_path = os.path.join(self.history_data_path, filename)
            existing_files[symbol] = os.path.exists(file_path)
        
        return existing_files
    
    async def check_missing_data(self) -> Tuple[List[str], List[str]]:
        """Check which symbols are missing historical data"""
        my_symbols = await self.get_my_symbols()
        existing_files = self.check_existing_files()
        
        missing_symbols = []
        existing_symbols = []
        
        for symbol in my_symbols:
            if symbol in existing_files and existing_files[symbol]:
                existing_symbols.append(symbol)
            else:
                missing_symbols.append(symbol)
        
        logger.info(f"📊 Data check: {len(existing_symbols)} existing, {len(missing_symbols)} missing")
        return existing_symbols, missing_symbols
    
    async def download_from_coingecko(self, symbol: str, days: int = 365) -> bool:
        """Download historical data from CoinGecko API"""
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
                        csv_content = self._convert_to_csv(data, symbol)
                        
                        # Save file
                        with open(file_path, 'w') as f:
                            f.write(csv_content)
                        
                        # Update mapping
                        self.symbol_to_file[symbol] = filename
                        
                        logger.info(f"✅ Downloaded {symbol} data: {len(data['prices'])} records")
                        return True
                    else:
                        logger.error(f"❌ Failed to download {symbol}: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error downloading {symbol}: {e}")
            return False
    
    def _convert_to_csv(self, data: Dict, symbol: str) -> str:
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
    
    async def download_missing_data(self, symbols: Optional[List[str]] = None) -> Dict[str, bool]:
        """Download missing historical data for symbols"""
        if symbols is None:
            _, missing_symbols = await self.check_missing_data()
        else:
            missing_symbols = symbols
        
        if not missing_symbols:
            logger.info("✅ No missing data to download")
            return {}
        
        logger.info(f"📥 Downloading data for {len(missing_symbols)} symbols: {missing_symbols}")
        
        results = {}
        for symbol in missing_symbols:
            success = await self.download_from_coingecko(symbol)
            results[symbol] = success
            
            # Rate limiting - CoinGecko allows 50 calls/minute
            await asyncio.sleep(1.2)
        
        return results
    
    async def ensure_data_for_symbol(self, symbol: str) -> bool:
        """Ensure historical data exists for a specific symbol"""
        existing_files = self.check_existing_files()
        
        if symbol in existing_files and existing_files[symbol]:
            logger.info(f"✅ Data already exists for {symbol}")
            return True
        
        logger.info(f"📥 Downloading data for {symbol}")
        return await self.download_from_coingecko(symbol)
    
    async def get_data_status(self) -> Dict[str, Any]:
        """Get comprehensive status of historical data"""
        my_symbols = await self.get_my_symbols()
        existing_files = self.check_existing_files()
        
        status = {
            'total_symbols': len(my_symbols),
            'existing_data': [],
            'missing_data': [],
            'symbols': {}
        }
        
        for symbol in my_symbols:
            has_data = symbol in existing_files and existing_files[symbol]
            symbol_status = {
                'symbol': symbol,
                'has_data': has_data,
                'filename': self.symbol_to_file.get(symbol, 'Not mapped'),
                'coingecko_id': self.symbol_to_coingecko.get(symbol, 'Not mapped')
            }
            
            status['symbols'][symbol] = symbol_status
            
            if has_data:
                status['existing_data'].append(symbol)
            else:
                status['missing_data'].append(symbol)
        
        return status
    
    async def auto_sync(self) -> Dict[str, Any]:
        """Automatically sync all missing data"""
        logger.info("🔄 Starting automatic data sync...")
        
        status = await self.get_data_status()
        
        if status['missing_data']:
            logger.info(f"📥 Found {len(status['missing_data'])} symbols missing data")
            download_results = await self.download_missing_data(status['missing_data'])
            
            # Update status with download results
            for symbol, success in download_results.items():
                if success:
                    status['symbols'][symbol]['has_data'] = True
                    status['existing_data'].append(symbol)
                    if symbol in status['missing_data']:
                        status['missing_data'].remove(symbol)
        
        logger.info(f"✅ Sync complete: {len(status['existing_data'])} with data, {len(status['missing_data'])} missing")
        return status

# Global instance
historical_data_manager = SymbolPriceHistoryDataManager()

async def get_historical_data_manager() -> SymbolPriceHistoryDataManager:
    """Get the global historical data manager instance"""
    return historical_data_manager
