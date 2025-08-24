#!/usr/bin/env python3
"""
Pattern Data Collector Service
Collects data from multiple sources: CoinGecko, Binance, KuCoin, Cryptometer
Imports historical data from CSV files
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
import json
from pathlib import Path
try:
    import ccxt.async_support as ccxt  # type: ignore
except ImportError:
    ccxt = None  # Handle missing ccxt library
import glob

from ..database.pattern_database import PatternDB, PriceData, TechnicalIndicators
# Import services if available
try:
    from ..services.cryptometer_service import MultiTimeframeCryptometerSystem
    cryptometer_service = MultiTimeframeCryptometerSystem()  # type: ignore
except ImportError:
    cryptometer_service = None

try:
    from ..agents.blockchain.blockchain_agent import blockchain_agent  # type: ignore
except ImportError:
    blockchain_agent = None

logger = logging.getLogger(__name__)

class PatternDataCollector:
    """
    Comprehensive data collector for pattern analysis
    Integrates multiple data sources and maintains database
    """
    
    def __init__(self):
        self.db = PatternDB()
        
        # Exchange clients
        self.binance = None
        self.kucoin = None
        self.init_exchanges()
        
        # API keys
        self.coingecko_api_key = os.getenv('COINGECKO_API_KEY', '')
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # Supported symbols
        self.symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'LINK/USDT',
            'LTC/USDT', 'ATOM/USDT', 'UNI/USDT', 'AAVE/USDT', 'MKR/USDT'
        ]
        
        # Data collection status
        self.collection_status = {}
        
        logger.info("Pattern Data Collector initialized")
    
    def init_exchanges(self):
        """Initialize exchange connections"""
        try:
            # Binance
            if ccxt:
                binance_api_key = os.getenv('BINANCE_API_KEY')
                binance_secret = os.getenv('BINANCE_SECRET')
                
                if binance_api_key and binance_secret:
                    self.binance = ccxt.binance({
                        'apiKey': str(binance_api_key),
                        'secret': str(binance_secret),
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'spot'
                        }
                    })
                else:
                    self.binance = None
                    logger.warning("Binance API credentials not configured")
            else:
                self.binance = None
                logger.warning("ccxt not available, skipping Binance initialization")
            
            # KuCoin
            if ccxt:
                kucoin_api_key = os.getenv('KUCOIN_API_KEY')
                kucoin_secret = os.getenv('KUCOIN_SECRET')
                kucoin_password = os.getenv('KUCOIN_PASSPHRASE')
                
                if kucoin_api_key and kucoin_secret and kucoin_password:
                    self.kucoin = ccxt.kucoin({
                        'apiKey': str(kucoin_api_key),
                        'secret': str(kucoin_secret),
                        'password': str(kucoin_password),
                        'enableRateLimit': True
                    })
                else:
                    self.kucoin = None
                    logger.warning("KuCoin API credentials not configured")
            else:
                self.kucoin = None
            
            logger.info("Exchange connections initialized")
            
        except Exception as e:
            logger.error(f"Error initializing exchanges: {e}")
    
    async def import_historical_csv_data(self, history_folder: str = "/Users/dansidanutz/Desktop/ZmartBot/History Data"):
        """Import historical data from CSV files"""
        
        logger.info(f"📂 Importing historical data from {history_folder}")
        
        csv_files = glob.glob(f"{history_folder}/*.csv")
        imported_count = 0
        
        for csv_file in csv_files:
            try:
                filename = os.path.basename(csv_file)
                
                # Parse symbol from filename
                symbol = self._parse_symbol_from_filename(filename)
                if not symbol:
                    continue
                
                logger.info(f"📊 Importing {symbol} from {filename}")
                
                # Read CSV
                df = pd.read_csv(csv_file, sep=';')
                
                # Process and store data
                for _, row in df.iterrows():
                    try:
                        # Parse timestamp
                        if 'timestamp' in row:
                            timestamp = pd.to_datetime(row['timestamp'])
                        elif 'timeOpen' in row:
                            timestamp = pd.to_datetime(row['timeOpen'])
                        else:
                            continue
                        
                        # Add to database
                        self.db.add_price_data(
                            symbol=symbol,
                            source='historical_csv',
                            timestamp=timestamp,
                            open=float(row.get('open', 0)),
                            high=float(row.get('high', 0)),
                            low=float(row.get('low', 0)),
                            close=float(row.get('close', 0)),
                            volume=float(row.get('volume', 0)),
                            market_cap=float(row.get('marketCap', 0)) if 'marketCap' in row else None
                        )
                        imported_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Error processing row: {e}")
                        continue
                
                logger.info(f"✅ Imported {symbol} data successfully")
                
            except Exception as e:
                logger.error(f"Error importing {csv_file}: {e}")
                continue
        
        logger.info(f"📊 Total records imported: {imported_count}")
        return imported_count
    
    def _parse_symbol_from_filename(self, filename: str) -> Optional[str]:
        """Parse trading symbol from CSV filename"""
        
        symbol_map = {
            'Bitcoin': 'BTC/USDT',
            'Ethereum': 'ETH/USDT',
            'BNB': 'BNB/USDT',
            'Cardano': 'ADA/USDT',
            'Solana': 'SOL/USDT',
            'XRP': 'XRP/USDT',
            'Polkadot': 'DOT/USDT',
            'Dogecoin': 'DOGE/USDT',
            'Avalanche': 'AVAX/USDT',
            'Chainlink': 'LINK/USDT',
            'Litecoin': 'LTC/USDT',
            'atom': 'ATOM/USDT',
            'mkr': 'MKR/USDT',
            'Aave': 'AAVE/USDT',
            'Monero': 'XMR/USDT',
            'Stellar': 'XLM/USDT',
            'VeChain': 'VET/USDT',
            'trx': 'TRX/USDT',
            'hbar': 'HBAR/USDT',
            'xtz': 'XTZ/USDT'
        }
        
        for key, symbol in symbol_map.items():
            if key.lower() in filename.lower():
                return symbol
        
        return None
    
    async def collect_binance_data(self, symbol: str, timeframe: str = '1h', limit: int = 500):
        """Collect data from Binance"""
        
        try:
            if not self.binance:
                return None
            
            logger.info(f"🔄 Collecting Binance data for {symbol}")
            
            # Fetch OHLCV data
            ohlcv = await self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Store in database
            for candle in ohlcv:
                timestamp = datetime.fromtimestamp(candle[0] / 1000)
                
                self.db.add_price_data(
                    symbol=symbol,
                    source='binance',
                    timestamp=timestamp,
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=candle[5]
                )
            
            logger.info(f"✅ Collected {len(ohlcv)} candles from Binance for {symbol}")
            return ohlcv
            
        except Exception as e:
            logger.error(f"Error collecting Binance data: {e}")
            return None
    
    async def collect_kucoin_data(self, symbol: str, timeframe: str = '1h', limit: int = 500):
        """Collect data from KuCoin"""
        
        try:
            if not self.kucoin:
                return None
            
            logger.info(f"🔄 Collecting KuCoin data for {symbol}")
            
            # Fetch OHLCV data
            ohlcv = await self.kucoin.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Store in database
            for candle in ohlcv:
                timestamp = datetime.fromtimestamp(candle[0] / 1000)
                
                self.db.add_price_data(
                    symbol=symbol,
                    source='kucoin',
                    timestamp=timestamp,
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=candle[5]
                )
            
            logger.info(f"✅ Collected {len(ohlcv)} candles from KuCoin for {symbol}")
            return ohlcv
            
        except Exception as e:
            logger.error(f"Error collecting KuCoin data: {e}")
            return None
    
    async def collect_coingecko_data(self, coin_id: str, days: int = 30):
        """Collect data from CoinGecko"""
        
        try:
            logger.info(f"🔄 Collecting CoinGecko data for {coin_id}")
            
            async with aiohttp.ClientSession() as session:
                # Market chart endpoint
                url = f"{self.coingecko_base_url}/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'hourly'
                }
                
                if self.coingecko_api_key:
                    params['x_cg_pro_api_key'] = self.coingecko_api_key
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process price data
                        prices = data.get('prices', [])
                        volumes = data.get('total_volumes', [])
                        market_caps = data.get('market_caps', [])
                        
                        symbol = f"{coin_id.upper()}/USDT"
                        
                        for i, price_point in enumerate(prices):
                            timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                            price = price_point[1]
                            
                            volume = volumes[i][1] if i < len(volumes) else 0
                            market_cap = market_caps[i][1] if i < len(market_caps) else 0
                            
                            # For CoinGecko, we only have close price
                            self.db.add_price_data(
                                symbol=symbol,
                                source='coingecko',
                                timestamp=timestamp,
                                open=price,
                                high=price,
                                low=price,
                                close=price,
                                volume=volume,
                                market_cap=market_cap
                            )
                        
                        logger.info(f"✅ Collected {len(prices)} data points from CoinGecko for {coin_id}")
                        return data
                    else:
                        logger.error(f"CoinGecko API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error collecting CoinGecko data: {e}")
            return None
    
    async def collect_cryptometer_data(self, symbol: str):
        """Collect data from Cryptometer"""
        
        try:
            logger.info(f"🔄 Collecting Cryptometer data for {symbol}")
            
            # Use existing cryptometer service if available
            if not cryptometer_service:
                logger.warning("Cryptometer service not available")
                return None
                
            if hasattr(cryptometer_service, 'analyze_multi_timeframe_symbol'):
                data = await cryptometer_service.analyze_multi_timeframe_symbol(symbol)  # type: ignore
            else:
                logger.warning("Cryptometer service doesn't have analyze_multi_timeframe_symbol method")
                return None
            
            if data and data.get('success'):
                # Store relevant metrics
                timestamp = datetime.utcnow()
                
                # Extract and store data
                analysis = data.get('data', {})
                
                # This would typically be stored in a separate metrics table
                logger.info(f"✅ Collected Cryptometer data for {symbol}")
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting Cryptometer data: {e}")
            return None
    
    async def collect_blockchain_data(self, symbol: str):
        """Collect on-chain data using blockchain agent"""
        
        try:
            logger.info(f"🔄 Collecting blockchain data for {symbol}")
            
            # Use blockchain agent if available
            if not blockchain_agent:
                logger.warning("Blockchain agent not available")
                return None
                
            if hasattr(blockchain_agent, 'analyze'):
                blockchain_data = await blockchain_agent.analyze(symbol)  # type: ignore
            else:
                logger.warning("Blockchain agent doesn't have analyze method")
                return None
            
            if blockchain_data:
                # Store in blockchain_data table
                logger.info(f"✅ Collected blockchain data for {symbol}")
                return blockchain_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting blockchain data: {e}")
            return None
    
    async def collect_all_sources(self, symbol: str):
        """Collect data from all available sources"""
        
        logger.info(f"📊 Starting comprehensive data collection for {symbol}")
        
        results = {
            'binance': None,
            'kucoin': None,
            'coingecko': None,
            'cryptometer': None,
            'blockchain': None
        }
        
        # Collect from each source
        tasks = []
        
        # Binance
        tasks.append(self.collect_binance_data(symbol))
        
        # KuCoin
        tasks.append(self.collect_kucoin_data(symbol))
        
        # CoinGecko (convert symbol to coin ID)
        coin_id = self._symbol_to_coingecko_id(symbol)
        if coin_id:
            tasks.append(self.collect_coingecko_data(coin_id))
        
        # Cryptometer
        tasks.append(self.collect_cryptometer_data(symbol))
        
        # Blockchain
        tasks.append(self.collect_blockchain_data(symbol))
        
        # Run all tasks concurrently
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results
        results['binance'] = results_list[0] if not isinstance(results_list[0], Exception) else None  # type: ignore
        results['kucoin'] = results_list[1] if not isinstance(results_list[1], Exception) else None  # type: ignore
        results['coingecko'] = results_list[2] if len(results_list) > 2 and not isinstance(results_list[2], Exception) else None  # type: ignore
        results['cryptometer'] = results_list[3] if len(results_list) > 3 and not isinstance(results_list[3], Exception) else None  # type: ignore
        results['blockchain'] = results_list[4] if len(results_list) > 4 and not isinstance(results_list[4], Exception) else None  # type: ignore
        
        # Update collection status
        self.collection_status[symbol] = {
            'timestamp': datetime.utcnow(),
            'sources_collected': sum(1 for v in results.values() if v is not None),
            'results': results
        }
        
        logger.info(f"✅ Data collection complete for {symbol}: {self.collection_status[symbol]['sources_collected']} sources")
        
        return results
    
    def _symbol_to_coingecko_id(self, symbol: str) -> Optional[str]:
        """Convert trading symbol to CoinGecko ID"""
        
        mapping = {
            'BTC/USDT': 'bitcoin',
            'ETH/USDT': 'ethereum',
            'BNB/USDT': 'binancecoin',
            'SOL/USDT': 'solana',
            'XRP/USDT': 'ripple',
            'ADA/USDT': 'cardano',
            'AVAX/USDT': 'avalanche-2',
            'DOT/USDT': 'polkadot',
            'LINK/USDT': 'chainlink',
            'LTC/USDT': 'litecoin',
            'ATOM/USDT': 'cosmos',
            'UNI/USDT': 'uniswap',
            'AAVE/USDT': 'aave',
            'MKR/USDT': 'maker'
        }
        
        return mapping.get(symbol)
    
    async def run_continuous_collection(self, interval_minutes: int = 60):
        """Run continuous data collection for all symbols"""
        
        logger.info(f"🚀 Starting continuous data collection (interval: {interval_minutes} min)")
        
        while True:
            try:
                # Collect for all symbols
                for symbol in self.symbols:
                    await self.collect_all_sources(symbol)
                    await asyncio.sleep(5)  # Small delay between symbols
                
                # Wait for next collection cycle
                logger.info(f"💤 Waiting {interval_minutes} minutes until next collection...")
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in continuous collection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def close(self):
        """Close all connections"""
        
        if self.binance:
            await self.binance.close()
        
        if self.kucoin:
            await self.kucoin.close()
        
        self.db.close()
        
        logger.info("Data collector closed")

# Global instance
pattern_data_collector = PatternDataCollector()

async def main():
    """Test data collection"""
    
    collector = PatternDataCollector()
    
    # Import historical data
    await collector.import_historical_csv_data()
    
    # Collect real-time data
    await collector.collect_all_sources('BTC/USDT')
    
    # Close connections
    await collector.close()

if __name__ == "__main__":
    asyncio.run(main())