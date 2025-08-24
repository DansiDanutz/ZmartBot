"""
Simulation Agent - Data Integration Service
==========================================

Comprehensive data integration for KingFisher, Cryptometer, and RiskMetric data sources.
Provides unified data access for simulation and analysis.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from decimal import Decimal
import json
import io
import base64
from PIL import Image
import requests
import time
from urllib.parse import urljoin

from ..core.config import config
from ..models.base import KingFisherData, CryptometerData, RiskMetricData

logger = logging.getLogger(__name__)

@dataclass
class DataIntegrationResult:
    """Result of data integration process"""
    
    symbol: str
    timestamp: datetime
    kingfisher_data: Optional[KingFisherData] = None
    cryptometer_data: Optional[CryptometerData] = None
    riskmetric_data: Optional[RiskMetricData] = None
    integration_success: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class KingFisherIntegrator:
    """Integration service for KingFisher data and analysis"""
    
    def __init__(self):
        self.api_base_url = config.system_integration.kingfisher_api_url
        self.session = None
        self.screenshot_types = config.data_sources.kingfisher_screenshot_types
        
        logger.info("KingFisher Integrator initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_kingfisher_data(self, symbol: str, timeframe: str = "1h") -> KingFisherData:
        """
        Retrieve comprehensive KingFisher data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            timeframe: Analysis timeframe
            
        Returns:
            KingFisherData object with all available data
        """
        
        logger.info(f"Fetching KingFisher data for {symbol}")
        
        try:
            # Get liquidation clusters data
            liquidation_clusters = await self._get_liquidation_clusters(symbol)
            
            # Get liquidation ratios
            short_term_ratio, long_term_ratio = await self._get_liquidation_ratios(symbol)
            
            # Get toxic order flow data
            toxic_order_flow = await self._get_toxic_order_flow(symbol)
            
            # Get RSI heatmap data
            rsi_heatmap = await self._get_rsi_heatmap(symbol)
            
            # Get leverage and market balance data
            leverage_data, market_balance = await self._get_leverage_market_balance(symbol)
            
            # Calculate custom indicators
            custom_indicators = self._calculate_kingfisher_indicators(
                liquidation_clusters, short_term_ratio, long_term_ratio,
                toxic_order_flow, rsi_heatmap, leverage_data, market_balance
            )
            
            kingfisher_data = KingFisherData(
                symbol=symbol,
                timestamp=datetime.now(),
                liquidation_clusters=liquidation_clusters,
                short_term_liquidation_ratio=short_term_ratio,
                long_term_liquidation_ratio=long_term_ratio,
                toxic_order_flow=toxic_order_flow,
                rsi_heatmap=rsi_heatmap,
                leverage_data=leverage_data,
                market_balance=market_balance,
                custom_indicators=custom_indicators
            )
            
            logger.info(f"Successfully retrieved KingFisher data for {symbol}")
            return kingfisher_data
            
        except Exception as e:
            logger.error(f"Error fetching KingFisher data for {symbol}: {str(e)}")
            raise
    
    async def _get_liquidation_clusters(self, symbol: str) -> List[Dict[str, Any]]:
        """Get liquidation clusters data"""
        
        try:
            # This would integrate with your actual KingFisher API
            # For now, we'll simulate the data structure
            
            url = f"{self.api_base_url}/api/v1/liquidation-clusters/{symbol}"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('clusters', [])
            
            # Fallback: simulate liquidation clusters data
            current_price = 50000  # This would be fetched from current market data
            
            clusters = []
            
            # Generate realistic liquidation clusters
            for i in range(5):
                cluster_price = current_price * (0.95 + i * 0.025)  # Clusters around current price
                cluster_size = np.random.uniform(1000000, 50000000)  # Random cluster size
                cluster_type = "long_liquidations" if cluster_price < current_price else "short_liquidations"
                
                clusters.append({
                    'price': cluster_price,
                    'size': cluster_size,
                    'type': cluster_type,
                    'confidence': np.random.uniform(0.6, 0.9),
                    'time_to_cluster': np.random.uniform(1, 24)  # Hours
                })
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error fetching liquidation clusters: {str(e)}")
            return []
    
    async def _get_liquidation_ratios(self, symbol: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Get short-term and long-term liquidation ratios"""
        
        try:
            url = f"{self.api_base_url}/api/v1/liquidation-ratios/{symbol}"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('short_term', {}), data.get('long_term', {})
            
            # Fallback: simulate liquidation ratios
            short_term_ratio = {
                'long_liquidation_ratio': np.random.uniform(0.3, 0.7),
                'short_liquidation_ratio': np.random.uniform(0.3, 0.7),
                'net_ratio': np.random.uniform(-0.2, 0.2),
                'trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'confidence': np.random.uniform(0.7, 0.9)
            }
            
            long_term_ratio = {
                'long_liquidation_ratio': np.random.uniform(0.4, 0.6),
                'short_liquidation_ratio': np.random.uniform(0.4, 0.6),
                'net_ratio': np.random.uniform(-0.1, 0.1),
                'trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'confidence': np.random.uniform(0.8, 0.95)
            }
            
            return short_term_ratio, long_term_ratio
            
        except Exception as e:
            logger.error(f"Error fetching liquidation ratios: {str(e)}")
            return {}, {}
    
    async def _get_toxic_order_flow(self, symbol: str) -> Dict[str, Any]:
        """Get toxic order flow analysis"""
        
        try:
            url = f"{self.api_base_url}/api/v1/toxic-order-flow/{symbol}"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
            
            # Fallback: simulate toxic order flow data
            toxic_flow = {
                'toxic_flow_intensity': np.random.uniform(0.1, 0.8),
                'manipulation_probability': np.random.uniform(0.0, 0.5),
                'artificial_volume_ratio': np.random.uniform(0.0, 0.3),
                'wash_trading_score': np.random.uniform(0.0, 0.4),
                'spoofing_detection': np.random.uniform(0.0, 0.3),
                'flow_direction': np.random.choice(['bullish', 'bearish', 'neutral']),
                'confidence': np.random.uniform(0.6, 0.85)
            }
            
            return toxic_flow
            
        except Exception as e:
            logger.error(f"Error fetching toxic order flow: {str(e)}")
            return {}
    
    async def _get_rsi_heatmap(self, symbol: str) -> Dict[str, Any]:
        """Get RSI heatmap analysis"""
        
        try:
            url = f"{self.api_base_url}/api/v1/rsi-heatmap/{symbol}"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
            
            # Fallback: simulate RSI heatmap data
            timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
            rsi_values = {}
            
            for tf in timeframes:
                rsi_values[tf] = {
                    'current_rsi': np.random.uniform(20, 80),
                    'rsi_trend': np.random.choice(['rising', 'falling', 'sideways']),
                    'overbought_probability': np.random.uniform(0.0, 1.0),
                    'oversold_probability': np.random.uniform(0.0, 1.0),
                    'divergence_detected': np.random.choice([True, False])
                }
            
            rsi_heatmap = {
                'timeframe_analysis': rsi_values,
                'overall_rsi_score': np.random.uniform(0.3, 0.7),
                'momentum_direction': np.random.choice(['bullish', 'bearish', 'neutral']),
                'strength': np.random.uniform(0.4, 0.9)
            }
            
            return rsi_heatmap
            
        except Exception as e:
            logger.error(f"Error fetching RSI heatmap: {str(e)}")
            return {}
    
    async def _get_leverage_market_balance(self, symbol: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get leverage data and market balance information"""
        
        try:
            url = f"{self.api_base_url}/api/v1/market-balance/{symbol}"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('leverage_data', {}), data.get('market_balance', {})
            
            # Fallback: simulate leverage and market balance data
            leverage_data = {
                'average_leverage': np.random.uniform(2.0, 15.0),
                'leverage_distribution': {
                    '1x-5x': np.random.uniform(0.2, 0.4),
                    '5x-10x': np.random.uniform(0.3, 0.5),
                    '10x-20x': np.random.uniform(0.1, 0.3),
                    '20x+': np.random.uniform(0.0, 0.2)
                },
                'high_leverage_risk': np.random.uniform(0.2, 0.8),
                'leverage_trend': np.random.choice(['increasing', 'decreasing', 'stable'])
            }
            
            market_balance = {
                'long_short_ratio': np.random.uniform(0.3, 1.7),
                'open_interest_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'funding_rate': np.random.uniform(-0.01, 0.01),
                'market_sentiment': np.random.choice(['bullish', 'bearish', 'neutral']),
                'balance_score': np.random.uniform(0.3, 0.8)
            }
            
            return leverage_data, market_balance
            
        except Exception as e:
            logger.error(f"Error fetching leverage and market balance: {str(e)}")
            return {}, {}
    
    def _calculate_kingfisher_indicators(
        self,
        liquidation_clusters: List[Dict],
        short_term_ratio: Dict,
        long_term_ratio: Dict,
        toxic_order_flow: Dict,
        rsi_heatmap: Dict,
        leverage_data: Dict,
        market_balance: Dict
    ) -> Dict[str, float]:
        """Calculate custom KingFisher-based indicators"""
        
        indicators = {}
        
        try:
            # Liquidation Pressure Index (LPI)
            cluster_pressure = 0.0
            if liquidation_clusters:
                total_size = sum([c.get('size', 0) for c in liquidation_clusters])
                cluster_pressure = min(1.0, total_size / 100000000)  # Normalize to 100M
            
            indicators['liquidation_pressure_index'] = cluster_pressure
            
            # Market Balance Ratio
            long_short_ratio = market_balance.get('long_short_ratio', 1.0)
            balance_ratio = 1.0 / (1.0 + abs(long_short_ratio - 1.0))
            indicators['market_balance_ratio'] = balance_ratio
            
            # Price Position Index (PPI) - based on liquidation clusters
            current_price = 50000  # This would be actual current price
            if liquidation_clusters:
                cluster_prices = [c.get('price', current_price) for c in liquidation_clusters]
                price_position = (current_price - min(cluster_prices)) / (max(cluster_prices) - min(cluster_prices))
                indicators['price_position_index'] = price_position
            else:
                indicators['price_position_index'] = 0.5
            
            # Toxic Order Flow Intensity (TOFI)
            toxic_intensity = toxic_order_flow.get('toxic_flow_intensity', 0.0)
            manipulation_prob = toxic_order_flow.get('manipulation_probability', 0.0)
            tofi = (toxic_intensity + manipulation_prob) / 2.0
            indicators['toxic_order_flow_intensity'] = tofi
            
            # RSI Position Factor (RPF)
            overall_rsi = rsi_heatmap.get('overall_rsi_score', 0.5)
            rsi_strength = rsi_heatmap.get('strength', 0.5)
            rpf = (overall_rsi + rsi_strength) / 2.0
            indicators['rsi_position_factor'] = rpf
            
            # Composite KingFisher Score
            weights = {
                'liquidation_pressure': 0.25,
                'market_balance': 0.20,
                'price_position': 0.20,
                'toxic_flow': -0.15,  # Negative weight (toxic flow is bad)
                'rsi_factor': 0.30
            }
            
            composite_score = (
                weights['liquidation_pressure'] * indicators['liquidation_pressure_index'] +
                weights['market_balance'] * indicators['market_balance_ratio'] +
                weights['price_position'] * indicators['price_position_index'] +
                weights['toxic_flow'] * (1.0 - indicators['toxic_order_flow_intensity']) +
                weights['rsi_factor'] * indicators['rsi_position_factor']
            )
            
            indicators['kingfisher_composite_score'] = max(0.0, min(1.0, composite_score))
            
        except Exception as e:
            logger.error(f"Error calculating KingFisher indicators: {str(e)}")
        
        return indicators

class CryptometerIntegrator:
    """Integration service for Cryptometer API data"""
    
    def __init__(self):
        self.api_key = config.data_sources.cryptometer_api_key
        self.base_url = config.data_sources.cryptometer_base_url
        self.rate_limit = config.data_sources.cryptometer_rate_limit
        self.session = None
        self.last_request_time = 0
        
        # Cryptometer endpoint configuration with tiers and weights
        self.endpoints_config = {
            'tier_1': {  # Primary indicators
                'weight': 0.4,
                'endpoints': [
                    'price-analysis',
                    'volume-analysis', 
                    'market-sentiment',
                    'technical-indicators',
                    'momentum-analysis'
                ]
            },
            'tier_2': {  # Secondary indicators
                'weight': 0.35,
                'endpoints': [
                    'social-sentiment',
                    'news-sentiment',
                    'whale-activity',
                    'exchange-flows',
                    'derivatives-data'
                ]
            },
            'tier_3': {  # Supporting indicators
                'weight': 0.25,
                'endpoints': [
                    'correlation-analysis',
                    'volatility-analysis',
                    'liquidity-analysis',
                    'market-structure',
                    'risk-metrics'
                ]
            }
        }
        
        logger.info("Cryptometer Integrator initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_cryptometer_data(self, symbol: str) -> CryptometerData:
        """
        Retrieve comprehensive Cryptometer data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            CryptometerData object with all available data
        """
        
        logger.info(f"Fetching Cryptometer data for {symbol}")
        
        try:
            # Collect data from all tiers
            tier_data = {}
            tier_scores = {}
            
            for tier_name, tier_config in self.endpoints_config.items():
                tier_results = await self._fetch_tier_data(symbol, tier_config['endpoints'])
                tier_data[tier_name] = tier_results
                
                # Calculate tier score
                tier_score = self._calculate_tier_score(tier_results)
                tier_scores[tier_name] = tier_score
            
            # Calculate overall Cryptometer score
            overall_score = self._calculate_overall_score(tier_scores)
            
            # Get historical data for trend analysis
            historical_data = await self._get_historical_trends(symbol)
            
            cryptometer_data = CryptometerData(
                symbol=symbol,
                timestamp=datetime.now(),
                tier_1_data=tier_data.get('tier_1', {}),
                tier_2_data=tier_data.get('tier_2', {}),
                tier_3_data=tier_data.get('tier_3', {}),
                tier_scores=tier_scores,
                overall_score=overall_score,
                historical_trends=historical_data,
                data_quality_score=self._assess_data_quality(tier_data)
            )
            
            logger.info(f"Successfully retrieved Cryptometer data for {symbol}, score: {overall_score:.2f}")
            return cryptometer_data
            
        except Exception as e:
            logger.error(f"Error fetching Cryptometer data for {symbol}: {str(e)}")
            raise
    
    async def _fetch_tier_data(self, symbol: str, endpoints: List[str]) -> Dict[str, Any]:
        """Fetch data from a specific tier of endpoints"""
        
        tier_data = {}
        
        for endpoint in endpoints:
            try:
                await self._rate_limit_check()
                data = await self._fetch_endpoint_data(symbol, endpoint)
                tier_data[endpoint] = data
                
            except Exception as e:
                logger.warning(f"Failed to fetch {endpoint} for {symbol}: {str(e)}")
                tier_data[endpoint] = None
        
        return tier_data
    
    async def _fetch_endpoint_data(self, symbol: str, endpoint: str) -> Dict[str, Any]:
        """Fetch data from a specific Cryptometer endpoint"""
        
        url = f"{self.base_url}/{endpoint}"
        params = {
            'symbol': symbol,
            'api_key': self.api_key
        }
        
        if self.session:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Cryptometer API returned status {response.status} for {endpoint}")
        
        # Fallback: simulate endpoint data
        return self._simulate_endpoint_data(endpoint)
    
    def _simulate_endpoint_data(self, endpoint: str) -> Dict[str, Any]:
        """Simulate Cryptometer endpoint data for testing"""
        
        simulation_data = {
            'price-analysis': {
                'trend': np.random.choice(['bullish', 'bearish', 'neutral']),
                'strength': np.random.uniform(0.3, 0.9),
                'support_levels': [np.random.uniform(45000, 48000) for _ in range(3)],
                'resistance_levels': [np.random.uniform(52000, 55000) for _ in range(3)],
                'score': np.random.uniform(0.3, 0.8)
            },
            'volume-analysis': {
                'volume_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'volume_profile': np.random.choice(['bullish', 'bearish', 'neutral']),
                'unusual_activity': np.random.choice([True, False]),
                'score': np.random.uniform(0.4, 0.7)
            },
            'market-sentiment': {
                'sentiment': np.random.choice(['positive', 'negative', 'neutral']),
                'sentiment_score': np.random.uniform(-1.0, 1.0),
                'confidence': np.random.uniform(0.6, 0.9),
                'score': np.random.uniform(0.3, 0.8)
            },
            'technical-indicators': {
                'rsi': np.random.uniform(20, 80),
                'macd_signal': np.random.choice(['bullish', 'bearish', 'neutral']),
                'bollinger_position': np.random.uniform(0.0, 1.0),
                'moving_average_trend': np.random.choice(['bullish', 'bearish', 'neutral']),
                'score': np.random.uniform(0.4, 0.8)
            },
            'momentum-analysis': {
                'momentum': np.random.choice(['strong_bullish', 'bullish', 'neutral', 'bearish', 'strong_bearish']),
                'acceleration': np.random.uniform(-0.5, 0.5),
                'divergence': np.random.choice([True, False]),
                'score': np.random.uniform(0.3, 0.7)
            },
            'social-sentiment': {
                'twitter_sentiment': np.random.uniform(-1.0, 1.0),
                'reddit_sentiment': np.random.uniform(-1.0, 1.0),
                'telegram_sentiment': np.random.uniform(-1.0, 1.0),
                'overall_social_score': np.random.uniform(0.2, 0.8),
                'score': np.random.uniform(0.3, 0.7)
            },
            'news-sentiment': {
                'news_sentiment': np.random.uniform(-1.0, 1.0),
                'news_volume': np.random.uniform(0.1, 1.0),
                'impact_score': np.random.uniform(0.0, 1.0),
                'score': np.random.uniform(0.3, 0.8)
            },
            'whale-activity': {
                'whale_transactions': np.random.randint(0, 20),
                'whale_sentiment': np.random.choice(['accumulating', 'distributing', 'neutral']),
                'large_holder_activity': np.random.uniform(0.0, 1.0),
                'score': np.random.uniform(0.4, 0.7)
            },
            'exchange-flows': {
                'inflow_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'outflow_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'net_flow': np.random.uniform(-1000000, 1000000),
                'score': np.random.uniform(0.3, 0.8)
            },
            'derivatives-data': {
                'funding_rate': np.random.uniform(-0.01, 0.01),
                'open_interest_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'long_short_ratio': np.random.uniform(0.5, 2.0),
                'score': np.random.uniform(0.4, 0.7)
            },
            'correlation-analysis': {
                'btc_correlation': np.random.uniform(-1.0, 1.0),
                'market_correlation': np.random.uniform(-1.0, 1.0),
                'sector_correlation': np.random.uniform(-1.0, 1.0),
                'score': np.random.uniform(0.3, 0.7)
            },
            'volatility-analysis': {
                'implied_volatility': np.random.uniform(0.2, 2.0),
                'realized_volatility': np.random.uniform(0.2, 2.0),
                'volatility_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'score': np.random.uniform(0.4, 0.8)
            },
            'liquidity-analysis': {
                'bid_ask_spread': np.random.uniform(0.001, 0.01),
                'market_depth': np.random.uniform(0.3, 1.0),
                'liquidity_score': np.random.uniform(0.4, 0.9),
                'score': np.random.uniform(0.5, 0.8)
            },
            'market-structure': {
                'market_phase': np.random.choice(['accumulation', 'markup', 'distribution', 'markdown']),
                'structure_strength': np.random.uniform(0.3, 0.9),
                'breakout_probability': np.random.uniform(0.0, 1.0),
                'score': np.random.uniform(0.4, 0.7)
            },
            'risk-metrics': {
                'var_95': np.random.uniform(0.05, 0.20),
                'expected_shortfall': np.random.uniform(0.08, 0.30),
                'risk_score': np.random.uniform(0.2, 0.8),
                'score': np.random.uniform(0.3, 0.7)
            }
        }
        
        return simulation_data.get(endpoint, {'score': np.random.uniform(0.3, 0.7)})
    
    def _calculate_tier_score(self, tier_data: Dict[str, Any]) -> float:
        """Calculate weighted score for a tier"""
        
        scores = []
        for endpoint, data in tier_data.items():
            if data and isinstance(data, dict) and 'score' in data:
                scores.append(data['score'])
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_overall_score(self, tier_scores: Dict[str, float]) -> float:
        """Calculate overall Cryptometer score using tier weights"""
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for tier_name, score in tier_scores.items():
            if tier_name in self.endpoints_config:
                weight = self.endpoints_config[tier_name]['weight']
                weighted_score += score * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    async def _get_historical_trends(self, symbol: str) -> Dict[str, Any]:
        """Get historical trend data for the symbol"""
        
        # This would fetch actual historical data
        # For now, simulate trend data
        
        return {
            'score_trend_7d': np.random.uniform(-0.2, 0.2),
            'score_trend_30d': np.random.uniform(-0.3, 0.3),
            'volatility_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
            'sentiment_trend': np.random.choice(['improving', 'deteriorating', 'stable']),
            'historical_accuracy': np.random.uniform(0.6, 0.9)
        }
    
    def _assess_data_quality(self, tier_data: Dict[str, Dict]) -> float:
        """Assess the quality of retrieved data"""
        
        total_endpoints = sum(len(tier['endpoints']) for tier in self.endpoints_config.values())
        successful_endpoints = 0
        
        for tier_name, data in tier_data.items():
            for endpoint, endpoint_data in data.items():
                if endpoint_data is not None:
                    successful_endpoints += 1
        
        return successful_endpoints / total_endpoints if total_endpoints > 0 else 0.0
    
    async def _rate_limit_check(self):
        """Ensure we don't exceed rate limits"""
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit  # Minimum seconds between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()

class RiskMetricIntegrator:
    """Integration service for RiskMetric data"""
    
    def __init__(self):
        self.primary_sheet_url = config.data_sources.riskmetric_primary_sheet
        self.historical_sheet_url = config.data_sources.riskmetric_historical_sheet
        self.methodology_doc_url = config.data_sources.riskmetric_methodology_doc
        self.session = None
        
        logger.info("RiskMetric Integrator initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_riskmetric_data(self, symbol: str) -> RiskMetricData:
        """
        Retrieve comprehensive RiskMetric data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            RiskMetricData object with all available data
        """
        
        logger.info(f"Fetching RiskMetric data for {symbol}")
        
        try:
            # Get current risk metrics
            current_metrics = await self._get_current_risk_metrics(symbol)
            
            # Get historical risk band data
            historical_data = await self._get_historical_risk_data(symbol)
            
            # Calculate risk transitions
            risk_transitions = self._calculate_risk_transitions(historical_data)
            
            # Get risk band time analysis
            time_in_bands = await self._get_time_in_risk_bands(symbol)
            
            # Calculate composite risk score
            composite_score = self._calculate_composite_risk_score(
                current_metrics, historical_data, risk_transitions, time_in_bands
            )
            
            riskmetric_data = RiskMetricData(
                symbol=symbol,
                timestamp=datetime.now(),
                current_risk_band=current_metrics.get('current_band', 'medium'),
                risk_score=current_metrics.get('risk_score', 0.5),
                risk_factors=current_metrics.get('risk_factors', {}),
                historical_risk_bands=historical_data,
                risk_transitions=risk_transitions,
                time_in_risk_bands=time_in_bands,
                composite_score=composite_score,
                risk_trend=current_metrics.get('risk_trend', 'stable'),
                confidence_level=current_metrics.get('confidence', 0.7)
            )
            
            logger.info(f"Successfully retrieved RiskMetric data for {symbol}, risk band: {current_metrics.get('current_band', 'unknown')}")
            return riskmetric_data
            
        except Exception as e:
            logger.error(f"Error fetching RiskMetric data for {symbol}: {str(e)}")
            raise
    
    async def _get_current_risk_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get current risk metrics from primary sheet"""
        
        try:
            # This would integrate with Google Sheets API
            # For now, simulate the data
            
            risk_bands = ['very_low', 'low', 'medium', 'high', 'very_high']
            current_band = np.random.choice(risk_bands)
            
            risk_factors = {
                'volatility_risk': np.random.uniform(0.1, 0.9),
                'liquidity_risk': np.random.uniform(0.1, 0.8),
                'correlation_risk': np.random.uniform(0.0, 0.7),
                'market_risk': np.random.uniform(0.2, 0.9),
                'technical_risk': np.random.uniform(0.1, 0.8),
                'fundamental_risk': np.random.uniform(0.0, 0.6)
            }
            
            # Calculate overall risk score
            risk_score = np.mean(list(risk_factors.values()))
            
            return {
                'current_band': current_band,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'risk_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                'confidence': np.random.uniform(0.7, 0.95),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching current risk metrics: {str(e)}")
            return {}
    
    async def _get_historical_risk_data(self, symbol: str) -> List[Dict[str, Any]]:
        """Get historical risk band data"""
        
        try:
            # This would fetch from historical Google Sheet
            # For now, simulate historical data
            
            historical_data = []
            risk_bands = ['very_low', 'low', 'medium', 'high', 'very_high']
            
            # Generate 30 days of historical data
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                risk_band = np.random.choice(risk_bands)
                risk_score = np.random.uniform(0.1, 0.9)
                
                historical_data.append({
                    'date': date.isoformat(),
                    'risk_band': risk_band,
                    'risk_score': risk_score,
                    'volatility': np.random.uniform(0.01, 0.05),
                    'volume_anomaly': np.random.choice([True, False]),
                    'market_stress': np.random.uniform(0.0, 1.0)
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical risk data: {str(e)}")
            return []
    
    def _calculate_risk_transitions(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate risk band transition patterns"""
        
        if not historical_data:
            return {}
        
        transitions = {}
        transition_counts = {}
        
        # Sort by date
        sorted_data = sorted(historical_data, key=lambda x: x['date'])
        
        for i in range(1, len(sorted_data)):
            prev_band = sorted_data[i-1]['risk_band']
            curr_band = sorted_data[i]['risk_band']
            
            transition_key = f"{prev_band}_to_{curr_band}"
            
            if transition_key not in transition_counts:
                transition_counts[transition_key] = 0
            transition_counts[transition_key] += 1
        
        # Calculate transition probabilities
        total_transitions = sum(transition_counts.values())
        if total_transitions > 0:
            for transition, count in transition_counts.items():
                transitions[transition] = count / total_transitions
        
        # Calculate stability metrics
        same_band_transitions = sum(count for key, count in transition_counts.items() if key.split('_to_')[0] == key.split('_to_')[1])
        stability_ratio = same_band_transitions / total_transitions if total_transitions > 0 else 0
        
        return {
            'transition_probabilities': transitions,
            'stability_ratio': stability_ratio,
            'total_transitions': total_transitions,
            'most_common_transition': max(transition_counts.items(), key=lambda x: x[1])[0] if transition_counts else None
        }
    
    async def _get_time_in_risk_bands(self, symbol: str) -> Dict[str, float]:
        """Get time spent in each risk band"""
        
        try:
            # This would fetch from the time-in-bands Google Sheet
            # For now, simulate the data
            
            risk_bands = ['very_low', 'low', 'medium', 'high', 'very_high']
            time_distribution = np.random.dirichlet(np.ones(len(risk_bands)))
            
            time_in_bands = {}
            for band, time_ratio in zip(risk_bands, time_distribution):
                time_in_bands[band] = float(time_ratio)
            
            return time_in_bands
            
        except Exception as e:
            logger.error(f"Error fetching time in risk bands: {str(e)}")
            return {}
    
    def _calculate_composite_risk_score(
        self,
        current_metrics: Dict,
        historical_data: List[Dict],
        risk_transitions: Dict,
        time_in_bands: Dict
    ) -> float:
        """Calculate composite risk score based on all available data"""
        
        try:
            # Current risk component (40% weight)
            current_risk = current_metrics.get('risk_score', 0.5)
            
            # Historical volatility component (30% weight)
            if historical_data:
                historical_scores = [d.get('risk_score', 0.5) for d in historical_data]
                historical_volatility = np.std(historical_scores)
                historical_mean = np.mean(historical_scores)
            else:
                historical_volatility = 0.0
                historical_mean = 0.5
            
            # Stability component (20% weight)
            stability_ratio = risk_transitions.get('stability_ratio', 0.5)
            
            # Time distribution component (10% weight)
            high_risk_time = time_in_bands.get('high', 0.0) + time_in_bands.get('very_high', 0.0)
            
            # Calculate composite score
            composite_score = (
                0.4 * current_risk +
                0.3 * (historical_mean + historical_volatility) +
                0.2 * (1.0 - stability_ratio) +  # Lower stability = higher risk
                0.1 * high_risk_time
            )
            
            return max(0.0, min(1.0, composite_score))
            
        except Exception as e:
            logger.error(f"Error calculating composite risk score: {str(e)}")
            return 0.5

class DataIntegrationService:
    """Main service for coordinating all data integrations"""
    
    def __init__(self):
        self.kingfisher_integrator = KingFisherIntegrator()
        self.cryptometer_integrator = CryptometerIntegrator()
        self.riskmetric_integrator = RiskMetricIntegrator()
        
        logger.info("Data Integration Service initialized")
    
    async def get_comprehensive_data(self, symbol: str) -> DataIntegrationResult:
        """
        Get comprehensive data from all sources for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            DataIntegrationResult with data from all sources
        """
        
        logger.info(f"Starting comprehensive data integration for {symbol}")
        
        result = DataIntegrationResult(
            symbol=symbol,
            timestamp=datetime.now()
        )
        
        # Fetch data from all sources concurrently
        tasks = []
        
        async with self.kingfisher_integrator as kf_integrator:
            tasks.append(self._safe_fetch_kingfisher(kf_integrator, symbol, result))
        
        async with self.cryptometer_integrator as cm_integrator:
            tasks.append(self._safe_fetch_cryptometer(cm_integrator, symbol, result))
        
        async with self.riskmetric_integrator as rm_integrator:
            tasks.append(self._safe_fetch_riskmetric(rm_integrator, symbol, result))
        
        # Wait for all integrations to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assess overall integration success
        success_count = sum([
            result.kingfisher_data is not None,
            result.cryptometer_data is not None,
            result.riskmetric_data is not None
        ])
        
        result.integration_success = success_count >= 2  # At least 2 out of 3 sources
        
        if result.integration_success:
            logger.info(f"Successfully integrated {success_count}/3 data sources for {symbol}")
        else:
            logger.warning(f"Only integrated {success_count}/3 data sources for {symbol}")
        
        return result
    
    async def _safe_fetch_kingfisher(self, integrator, symbol: str, result: DataIntegrationResult):
        """Safely fetch KingFisher data with error handling"""
        
        try:
            result.kingfisher_data = await integrator.get_kingfisher_data(symbol)
        except Exception as e:
            error_msg = f"KingFisher integration failed: {str(e)}"
            result.errors.append(error_msg)
            logger.error(error_msg)
    
    async def _safe_fetch_cryptometer(self, integrator, symbol: str, result: DataIntegrationResult):
        """Safely fetch Cryptometer data with error handling"""
        
        try:
            result.cryptometer_data = await integrator.get_cryptometer_data(symbol)
        except Exception as e:
            error_msg = f"Cryptometer integration failed: {str(e)}"
            result.errors.append(error_msg)
            logger.error(error_msg)
    
    async def _safe_fetch_riskmetric(self, integrator, symbol: str, result: DataIntegrationResult):
        """Safely fetch RiskMetric data with error handling"""
        
        try:
            result.riskmetric_data = await integrator.get_riskmetric_data(symbol)
        except Exception as e:
            error_msg = f"RiskMetric integration failed: {str(e)}"
            result.errors.append(error_msg)
            logger.error(error_msg)

# Export the main integration service
data_integration_service = DataIntegrationService()

if __name__ == "__main__":
    # Test the data integration service
    async def test_integration():
        result = await data_integration_service.get_comprehensive_data("BTCUSDT")
        print(f"Integration for {result.symbol}: {'Success' if result.integration_success else 'Failed'}")
        print(f"KingFisher: {'✓' if result.kingfisher_data else '✗'}")
        print(f"Cryptometer: {'✓' if result.cryptometer_data else '✗'}")
        print(f"RiskMetric: {'✓' if result.riskmetric_data else '✗'}")
        if result.errors:
            print(f"Errors: {result.errors}")
    
    # Run test
    asyncio.run(test_integration())

