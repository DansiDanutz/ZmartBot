#!/usr/bin/env python3
"""
Real Crypto Risk Indicators Extractor
Extracts real crypto risk indicators from multiple public APIs
Implements actual data extraction instead of placeholder functionality
"""

import logging
import asyncio
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time
import statistics

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.cryptoverse_database import DataExtractionResult

logger = logging.getLogger(__name__)

class RealCryptoRiskExtractor:
    """Extracts real crypto risk indicators from multiple data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API endpoints for real data
        self.apis = {
            'coingecko': 'https://api.coingecko.com/api/v3',
            'binance': 'https://api.binance.com/api/v3',
            'coinmarketcap': 'https://pro-api.coinmarketcap.com/v1',
            'fear_greed': 'https://api.alternative.me/fng/',
            'blockchain_info': 'https://api.blockchain.info/stats'
        }
        
        # Major cryptocurrencies to analyze
        self.major_coins = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana', 'polkadot', 'chainlink']
        self.coin_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT', 'LINK']
    
    async def extract_comprehensive_risk_data(self) -> DataExtractionResult:
        """Extract comprehensive crypto risk indicators from multiple sources"""
        timestamp = datetime.now()
        
        try:
            logger.info("🔍 Starting comprehensive crypto risk data extraction")
            
            # Extract data from multiple sources
            market_data = await self._extract_market_data()
            fear_greed_data = await self._extract_fear_greed_index()
            volatility_data = await self._extract_volatility_metrics()
            onchain_data = await self._extract_onchain_metrics()
            social_sentiment = await self._extract_social_sentiment()
            
            # Calculate comprehensive risk metrics
            risk_analysis = self._calculate_comprehensive_risk(
                market_data, fear_greed_data, volatility_data, onchain_data, social_sentiment
            )
            
            # Compile final risk data
            comprehensive_data = {
                'timestamp': timestamp.isoformat(),
                'extraction_time': datetime.now().isoformat(),
                'data_sources': len([d for d in [market_data, fear_greed_data, volatility_data, onchain_data] if d]),
                'market_data': market_data,
                'fear_greed_index': fear_greed_data,
                'volatility_metrics': volatility_data,
                'onchain_metrics': onchain_data,
                'social_sentiment': social_sentiment,
                'risk_analysis': risk_analysis,
                'overall_risk_score': risk_analysis.get('overall_risk', 0.5),
                'risk_level': risk_analysis.get('risk_level', 'Moderate'),
                'recommendations': risk_analysis.get('recommendations', [])
            }
            
            logger.info(f"✅ Successfully extracted comprehensive risk data: {len(comprehensive_data)} components")
            
            return DataExtractionResult(
                source="crypto_risk_indicators",
                timestamp=timestamp,
                data=comprehensive_data,
                success=True,
                confidence_score=0.95
            )
            
        except Exception as e:
            logger.error(f"❌ Error extracting comprehensive risk data: {str(e)}")
            return DataExtractionResult(
                source="crypto_risk_indicators",
                timestamp=timestamp,
                data={},
                success=False,
                error_message=str(e),
                confidence_score=0.0
            )
    
    async def _extract_market_data(self) -> Dict[str, Any]:
        """Extract real market data from CoinGecko API"""
        try:
            logger.info("📊 Extracting market data from CoinGecko")
            
            # Get market data for major coins
            coins_param = ','.join(self.major_coins)
            url = f"{self.apis['coingecko']}/simple/price"
            params = {
                'ids': coins_param,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process market data
            market_metrics = {
                'total_market_cap': sum(coin_data.get('usd_market_cap', 0) for coin_data in data.values()),
                'average_24h_change': statistics.mean([coin_data.get('usd_24h_change', 0) for coin_data in data.values()]),
                'total_24h_volume': sum(coin_data.get('usd_24h_vol', 0) for coin_data in data.values()),
                'coins_analyzed': len(data),
                'coins_positive': len([c for c in data.values() if c.get('usd_24h_change', 0) > 0]),
                'coins_negative': len([c for c in data.values() if c.get('usd_24h_change', 0) < 0]),
                'individual_coins': data,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Market data extracted: {len(data)} coins analyzed")
            return market_metrics
            
        except Exception as e:
            logger.error(f"❌ Error extracting market data: {str(e)}")
            return {}
    
    async def _extract_fear_greed_index(self) -> Dict[str, Any]:
        """Extract Fear & Greed Index from Alternative.me API"""
        try:
            logger.info("😨 Extracting Fear & Greed Index")
            
            response = self.session.get(f"{self.apis['fear_greed']}?limit=10", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0]
                historical = data['data'][:7]  # Last 7 days
                
                fear_greed_data = {
                    'current_value': int(current['value']),
                    'current_classification': current['value_classification'],
                    'timestamp': current['timestamp'],
                    'historical_average': statistics.mean([int(item['value']) for item in historical]),
                    'trend': self._calculate_fear_greed_trend(historical),
                    'raw_data': historical,
                    'interpretation': self._interpret_fear_greed(int(current['value']))
                }
                
                logger.info(f"✅ Fear & Greed Index: {current['value']} ({current['value_classification']})")
                return fear_greed_data
            else:
                logger.warning("⚠️  No Fear & Greed data available")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error extracting Fear & Greed Index: {str(e)}")
            return {}
    
    async def _extract_volatility_metrics(self) -> Dict[str, Any]:
        """Extract volatility metrics from price data"""
        try:
            logger.info("📈 Calculating volatility metrics")
            
            # Get historical price data for BTC (as market indicator)
            url = f"{self.apis['coingecko']}/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': '30',
                'interval': 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' in data and len(data['prices']) > 1:
                prices = [price[1] for price in data['prices']]
                
                # Calculate volatility metrics
                daily_returns = []
                for i in range(1, len(prices)):
                    daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                    daily_returns.append(daily_return)
                
                volatility_metrics = {
                    'btc_30d_volatility': statistics.stdev(daily_returns) * (365 ** 0.5),  # Annualized
                    'average_daily_return': statistics.mean(daily_returns),
                    'max_daily_gain': max(daily_returns),
                    'max_daily_loss': min(daily_returns),
                    'positive_days': len([r for r in daily_returns if r > 0]),
                    'negative_days': len([r for r in daily_returns if r < 0]),
                    'volatility_level': self._classify_volatility(statistics.stdev(daily_returns)),
                    'price_range': {
                        'high': max(prices),
                        'low': min(prices),
                        'current': prices[-1]
                    },
                    'calculation_period': '30 days',
                    'data_points': len(prices)
                }
                
                logger.info(f"✅ Volatility metrics calculated: {volatility_metrics['btc_30d_volatility']:.2%} annualized")
                return volatility_metrics
            else:
                logger.warning("⚠️  Insufficient price data for volatility calculation")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error calculating volatility metrics: {str(e)}")
            return {}
    
    async def _extract_onchain_metrics(self) -> Dict[str, Any]:
        """Extract on-chain metrics from Blockchain.info API"""
        try:
            logger.info("⛓️  Extracting on-chain metrics")
            
            response = self.session.get(self.apis['blockchain_info'], timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Calculate additional metrics
            onchain_metrics = {
                'total_bitcoins': data.get('totalbc', 0) / 100000000,  # Convert from satoshis
                'market_price_usd': data.get('market_price_usd', 0),
                'hash_rate': data.get('hash_rate', 0),
                'difficulty': data.get('difficulty', 0),
                'minutes_between_blocks': data.get('minutes_between_blocks', 0),
                'number_of_transactions': data.get('n_tx', 0),
                'total_fees_btc': data.get('total_fees_btc', 0) / 100000000,
                'mempool_size': data.get('mempool_size', 0),
                'unconfirmed_count': data.get('unconfirmed_count', 0),
                'network_health': self._assess_network_health(data),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ On-chain metrics extracted: Hash rate {onchain_metrics['hash_rate']}")
            return onchain_metrics
            
        except Exception as e:
            logger.error(f"❌ Error extracting on-chain metrics: {str(e)}")
            return {}
    
    async def _extract_social_sentiment(self) -> Dict[str, Any]:
        """Extract social sentiment indicators"""
        try:
            logger.info("💬 Analyzing social sentiment")
            
            # This would integrate with social media APIs, news APIs, etc.
            # For now, we'll create a composite sentiment based on market data
            
            # Get trending coins data
            url = f"{self.apis['coingecko']}/search/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            trending_data = response.json()
            
            social_sentiment = {
                'trending_coins': [coin['item']['name'] for coin in trending_data.get('coins', [])[:5]],
                'trending_count': len(trending_data.get('coins', [])),
                'sentiment_score': self._calculate_sentiment_from_trends(trending_data),
                'social_indicators': {
                    'trending_activity': 'high' if len(trending_data.get('coins', [])) > 5 else 'moderate',
                    'market_attention': self._assess_market_attention(trending_data)
                },
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Social sentiment analyzed: {len(social_sentiment['trending_coins'])} trending coins")
            return social_sentiment
            
        except Exception as e:
            logger.error(f"❌ Error extracting social sentiment: {str(e)}")
            return {}
    
    def _calculate_comprehensive_risk(self, market_data: Dict, fear_greed: Dict, 
                                    volatility: Dict, onchain: Dict, social: Dict) -> Dict[str, Any]:
        """Calculate comprehensive risk score from all data sources"""
        try:
            risk_components = {}
            
            # Market risk (30% weight)
            if market_data:
                market_risk = self._calculate_market_risk(market_data)
                risk_components['market_risk'] = market_risk
            
            # Fear & Greed risk (25% weight)
            if fear_greed:
                fg_risk = (100 - fear_greed.get('current_value', 50)) / 100  # Inverse fear & greed
                risk_components['sentiment_risk'] = fg_risk
            
            # Volatility risk (25% weight)
            if volatility:
                vol_risk = min(volatility.get('btc_30d_volatility', 0.5), 2.0) / 2.0  # Cap at 200%
                risk_components['volatility_risk'] = vol_risk
            
            # On-chain risk (20% weight)
            if onchain:
                onchain_risk = self._calculate_onchain_risk(onchain)
                risk_components['onchain_risk'] = onchain_risk
            
            # Calculate weighted overall risk
            weights = {'market_risk': 0.3, 'sentiment_risk': 0.25, 'volatility_risk': 0.25, 'onchain_risk': 0.2}
            overall_risk = sum(risk_components.get(key, 0.5) * weight for key, weight in weights.items())
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_risk)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(overall_risk, risk_components)
            
            return {
                'overall_risk': overall_risk,
                'risk_level': risk_level,
                'risk_components': risk_components,
                'component_weights': weights,
                'recommendations': recommendations,
                'confidence': min(len(risk_components) / 4, 1.0),  # Based on data availability
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating comprehensive risk: {str(e)}")
            return {'overall_risk': 0.5, 'risk_level': 'Moderate', 'error': str(e)}
    
    def _calculate_market_risk(self, market_data: Dict) -> float:
        """Calculate market risk from market data"""
        try:
            avg_change = market_data.get('average_24h_change', 0)
            negative_ratio = market_data.get('coins_negative', 0) / max(market_data.get('coins_analyzed', 1), 1)
            
            # Higher negative change and more negative coins = higher risk
            change_risk = max(0, -avg_change / 10)  # Normalize to 0-1 scale
            ratio_risk = negative_ratio
            
            return min((change_risk + ratio_risk) / 2, 1.0)
        except:
            return 0.5
    
    def _calculate_onchain_risk(self, onchain_data: Dict) -> float:
        """Calculate on-chain risk from network metrics"""
        try:
            # Lower hash rate and higher mempool = higher risk
            hash_rate = onchain_data.get('hash_rate', 0)
            mempool_size = onchain_data.get('mempool_size', 0)
            unconfirmed = onchain_data.get('unconfirmed_count', 0)
            
            # Normalize metrics (these are rough approximations)
            hash_risk = max(0, 1 - (hash_rate / 200_000_000_000_000_000))  # Rough normalization
            mempool_risk = min(mempool_size / 100_000_000, 1.0)  # Cap at 100MB
            
            return min((hash_risk + mempool_risk) / 2, 1.0)
        except:
            return 0.5
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score <= 0.2:
            return "Very Low"
        elif risk_score <= 0.4:
            return "Low"
        elif risk_score <= 0.6:
            return "Moderate"
        elif risk_score <= 0.8:
            return "High"
        else:
            return "Very High"
    
    def _generate_risk_recommendations(self, overall_risk: float, components: Dict) -> List[str]:
        """Generate actionable risk recommendations"""
        recommendations = []
        
        if overall_risk <= 0.3:
            recommendations.append("Low risk environment - Consider increasing position sizes")
            recommendations.append("Good time for accumulation strategies")
        elif overall_risk <= 0.7:
            recommendations.append("Moderate risk - Maintain balanced portfolio")
            recommendations.append("Monitor market conditions closely")
        else:
            recommendations.append("High risk environment - Consider reducing exposure")
            recommendations.append("Implement strict risk management")
            recommendations.append("Avoid leverage in current conditions")
        
        # Component-specific recommendations
        if components.get('volatility_risk', 0) > 0.7:
            recommendations.append("High volatility detected - Use smaller position sizes")
        
        if components.get('sentiment_risk', 0) > 0.7:
            recommendations.append("Extreme sentiment detected - Contrarian opportunities may exist")
        
        return recommendations
    
    # Helper methods for data processing
    def _calculate_fear_greed_trend(self, historical: List) -> str:
        if len(historical) < 2:
            return "insufficient_data"
        
        recent = statistics.mean([int(item['value']) for item in historical[:3]])
        older = statistics.mean([int(item['value']) for item in historical[3:]])
        
        if recent > older + 5:
            return "improving"
        elif recent < older - 5:
            return "deteriorating"
        else:
            return "stable"
    
    def _interpret_fear_greed(self, value: int) -> str:
        if value <= 25:
            return "Extreme fear - potential buying opportunity"
        elif value <= 45:
            return "Fear - market pessimism"
        elif value <= 55:
            return "Neutral - balanced sentiment"
        elif value <= 75:
            return "Greed - market optimism"
        else:
            return "Extreme greed - potential selling opportunity"
    
    def _classify_volatility(self, daily_vol: float) -> str:
        annualized = daily_vol * (365 ** 0.5)
        if annualized < 0.3:
            return "Low"
        elif annualized < 0.6:
            return "Moderate"
        elif annualized < 1.0:
            return "High"
        else:
            return "Very High"
    
    def _assess_network_health(self, data: Dict) -> str:
        hash_rate = data.get('hash_rate', 0)
        mempool_size = data.get('mempool_size', 0)
        
        if hash_rate > 150_000_000_000_000_000 and mempool_size < 50_000_000:
            return "Excellent"
        elif hash_rate > 100_000_000_000_000_000 and mempool_size < 100_000_000:
            return "Good"
        else:
            return "Fair"
    
    def _calculate_sentiment_from_trends(self, trending_data: Dict) -> float:
        # Simple sentiment calculation based on trending activity
        coin_count = len(trending_data.get('coins', []))
        return min(coin_count / 10, 1.0)  # Normalize to 0-1
    
    def _assess_market_attention(self, trending_data: Dict) -> str:
        coin_count = len(trending_data.get('coins', []))
        if coin_count > 8:
            return "Very High"
        elif coin_count > 5:
            return "High"
        elif coin_count > 2:
            return "Moderate"
        else:
            return "Low"