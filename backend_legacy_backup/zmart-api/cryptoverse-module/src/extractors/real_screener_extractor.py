#!/usr/bin/env python3
"""
Real Screener Extractor
Production-ready extractor for cryptocurrency screener data from multiple sources
"""

import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time
import statistics

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.cryptoverse_database import DataExtractionResult

logger = logging.getLogger(__name__)

class RealScreenerExtractor:
    """Extracts real screener data from CoinGecko and Binance APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ZmartBot-Cryptoverse/1.0'
        })
        self.rate_limit_delay = 1.0  # seconds between requests
        logger.info("Real Screener Extractor initialized")
    
    async def extract_screener_data(self, symbols: Optional[List[str]] = None) -> DataExtractionResult:
        """Extract comprehensive screener data"""
        try:
            if symbols is None:
                symbols = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']
            
            # Extract market overview
            market_overview = await self.extract_market_overview()
            
            # Extract top performers
            top_performers = await self.extract_top_performers()
            
            # Extract technical indicators
            technical_data = {}
            for symbol in symbols:
                technical_data[symbol] = await self.extract_technical_indicators(symbol)
                time.sleep(self.rate_limit_delay)
            
            # Extract volume analysis
            volume_analysis = await self.extract_volume_analysis(symbols)
            
            # Extract market cap analysis
            market_cap_analysis = await self.extract_market_cap_analysis(symbols)
            
            screener_data = {
                'market_overview': market_overview,
                'top_performers': top_performers,
                'technical_indicators': technical_data,
                'volume_analysis': volume_analysis,
                'market_cap_analysis': market_cap_analysis,
                'extraction_timestamp': datetime.now().isoformat(),
                'symbols_analyzed': len(symbols)
            }
            
            return DataExtractionResult(
                source='screener_data',
                timestamp=datetime.now(),
                data=screener_data,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting screener data: {str(e)}")
            return DataExtractionResult(
                source='screener_data',
                timestamp=datetime.now(),
                data={},
                success=False,
                error_message=str(e)
            )
    
    async def extract_market_overview(self) -> Dict[str, Any]:
        """Extract overall market overview"""
        try:
            # CoinGecko global market data
            url = "https://api.coingecko.com/api/v3/global"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                global_data = data.get('data', {})
                
                return {
                    'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                    'total_volume_24h_usd': global_data.get('total_volume', {}).get('usd', 0),
                    'bitcoin_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
                    'ethereum_dominance': global_data.get('market_cap_percentage', {}).get('eth', 0),
                    'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                    'markets': global_data.get('markets', 0),
                    'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd', 0)
                }
            
            return {'error': f'API error: {response.status_code}'}
            
        except Exception as e:
            logger.error(f"Error extracting market overview: {str(e)}")
            return {'error': str(e)}
    
    async def extract_top_performers(self) -> Dict[str, Any]:
        """Extract top performing cryptocurrencies"""
        try:
            # CoinGecko trending coins
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                trending_coins = data.get('coins', [])
                
                performers = []
                for coin in trending_coins[:10]:  # Top 10
                    coin_data = coin.get('item', {})
                    performers.append({
                        'symbol': coin_data.get('symbol', ''),
                        'name': coin_data.get('name', ''),
                        'market_cap_rank': coin_data.get('market_cap_rank', 0),
                        'price_btc': coin_data.get('price_btc', 0)
                    })
                
                return {
                    'trending_coins': performers,
                    'count': len(performers)
                }
            
            return {'error': f'API error: {response.status_code}'}
            
        except Exception as e:
            logger.error(f"Error extracting top performers: {str(e)}")
            return {'error': str(e)}
    
    async def extract_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Extract technical indicators for a symbol"""
        try:
            # CoinGecko price data for technical analysis
            url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': '30',
                'interval': 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = [price[1] for price in data.get('prices', [])]
                volumes = [volume[1] for volume in data.get('total_volumes', [])]
                
                if len(prices) >= 20:
                    # Calculate technical indicators
                    current_price = prices[-1]
                    sma_20 = statistics.mean(prices[-20:])
                    sma_50 = statistics.mean(prices[-50:]) if len(prices) >= 50 else sma_20
                    
                    # Price changes
                    price_change_24h = ((current_price - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else 0
                    price_change_7d = ((current_price - prices[-7]) / prices[-7] * 100) if len(prices) >= 7 else 0
                    price_change_30d = ((current_price - prices[0]) / prices[0] * 100) if len(prices) >= 30 else 0
                    
                    # Volatility
                    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    volatility = statistics.stdev(returns) * 100 if len(returns) > 1 else 0
                    
                    return {
                        'current_price': current_price,
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'price_change_24h': price_change_24h,
                        'price_change_7d': price_change_7d,
                        'price_change_30d': price_change_30d,
                        'volatility_30d': volatility,
                        'volume_24h': volumes[-1] if volumes else 0,
                        'avg_volume_30d': statistics.mean(volumes) if volumes else 0
                    }
            
            return {'error': f'API error: {response.status_code}'}
            
        except Exception as e:
            logger.error(f"Error extracting technical indicators for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    async def extract_volume_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Extract volume analysis for symbols"""
        try:
            volume_data = {}
            
            for symbol in symbols:
                # Get volume data from CoinGecko
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    market_data = data.get('market_data', {})
                    
                    volume_data[symbol] = {
                        'total_volume_usd': market_data.get('total_volume', {}).get('usd', 0),
                        'volume_change_24h': market_data.get('volume_change_24h', 0),
                        'market_cap_usd': market_data.get('market_cap', {}).get('usd', 0),
                        'volume_to_market_cap_ratio': 0
                    }
                    
                    # Calculate volume to market cap ratio
                    if volume_data[symbol]['market_cap_usd'] > 0:
                        volume_data[symbol]['volume_to_market_cap_ratio'] = (
                            volume_data[symbol]['total_volume_usd'] / 
                            volume_data[symbol]['market_cap_usd']
                        )
                
                time.sleep(self.rate_limit_delay)
            
            return {
                'symbols': volume_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting volume analysis: {str(e)}")
            return {'error': str(e)}
    
    async def extract_market_cap_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Extract market capitalization analysis"""
        try:
            market_cap_data = {}
            
            for symbol in symbols:
                # Get market cap data from CoinGecko
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    market_data = data.get('market_data', {})
                    
                    market_cap_data[symbol] = {
                        'market_cap_usd': market_data.get('market_cap', {}).get('usd', 0),
                        'market_cap_rank': data.get('market_cap_rank', 0),
                        'market_cap_change_24h': market_data.get('market_cap_change_24h', 0),
                        'market_cap_change_percentage_24h': market_data.get('market_cap_change_percentage_24h', 0),
                        'fully_diluted_valuation': market_data.get('fully_diluted_valuation', {}).get('usd', 0),
                        'circulating_supply': market_data.get('circulating_supply', 0),
                        'total_supply': market_data.get('total_supply', 0),
                        'max_supply': market_data.get('max_supply', 0)
                    }
                
                time.sleep(self.rate_limit_delay)
            
            return {
                'symbols': market_cap_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting market cap analysis: {str(e)}")
            return {'error': str(e)}