#!/usr/bin/env python3
"""
Enhanced Cryptometer Endpoint Analyzer V2
Updated with Data Appendix specifications and multi-model AI integration
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class EndpointScore:
    """Score for individual endpoint analysis"""
    endpoint: str
    success: bool
    score: float
    confidence: float
    patterns: List[str]
    data_quality: float = 0.0
    processing_time: float = 0.0
    error_message: Optional[str] = None

@dataclass
class CryptometerAnalysis:
    """Complete Cryptometer analysis result"""
    symbol: str
    endpoint_scores: List[EndpointScore]
    calibrated_score: float
    confidence: float
    direction: str
    analysis_summary: str
    successful_endpoints: int
    total_endpoints: int
    processing_time: float
    data_appendix_compliance: bool = True

class CryptometerEndpointAnalyzerV2:
    """
    Enhanced Cryptometer Endpoint Analyzer based on Data Appendix specifications
    Optimized for multi-model AI integration with 18 validated endpoints
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize enhanced analyzer with Data Appendix endpoint configurations"""
        from src.config.settings import settings
        
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        if not self.api_key:
            raise ValueError("Cryptometer API key is required")
        
        self.base_url = "https://api.cryptometer.io"
        
        # Enhanced 18-endpoint configuration based on Data Appendix findings
        # Prioritized by ETH analysis value and success rates
        self.endpoints = {
            # TIER 1: Highest Value Endpoints (Data Appendix: "Most Valuable for ETH Analysis")
            'liquidity_lens': {
                'url': 'liquidity-lens/',
                'params': {'timeframe': '1h', 'e': 'binance'},
                'weight': 15,
                'description': 'ETH-specific liquidity flow analysis',
                'purpose': 'Direct ETH inflow/outflow data - highest priority for ETH',
                'success_indicators': ['inflow', 'outflow', 'netflow'],
                'data_appendix_priority': 1,
                'expected_keys': ['ETH', 'inflow', 'outflow', 'netflow']
            },
            'ls_ratio': {
                'url': 'ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': '{symbol}-usdt', 'timeframe': '1h'},
                'weight': 14,
                'description': 'ETH-USDT Long/Short positioning',
                'purpose': 'ETH-USDT specific positioning analysis',
                'success_indicators': ['ratio', 'buy_percentage', 'sell_percentage'],
                'data_appendix_priority': 2,
                'expected_keys': ['ratio', 'buy_percentage', 'sell_percentage']
            },
            'large_trades_activity': {
                'url': 'large-trades-activity/',
                'params': {'e': 'binance', 'pair': '{symbol}-USDT'},
                'weight': 13,
                'description': 'ETH-USDT institutional activity',
                'purpose': 'Large order flow and institutional activity for ETH-USDT',
                'success_indicators': ['large_trades', 'institutional_flow'],
                'data_appendix_priority': 3,
                'expected_keys': ['trades', 'volume', 'activity']
            },
            'total_liquidation_data': {
                'url': 'liquidation-data-v2/',
                'params': {'symbol': 'BTC'},  # Use BTC as market proxy per Data Appendix
                'weight': 12,
                'description': 'Cross-exchange liquidation tracking',
                'purpose': 'Market sentiment analysis through liquidation data',
                'success_indicators': ['binance_futures', 'bybit', 'okx', 'bitmex'],
                'data_appendix_priority': 4,
                'expected_keys': ['binance_futures', 'bybit', 'okx', 'bitmex', 'longs', 'shorts']
            },
            'trend_indicator_v3': {
                'url': 'trend-indicator-v3/',
                'params': {},
                'weight': 11,
                'description': 'Advanced trend analysis',
                'purpose': 'Overall market direction assessment',
                'success_indicators': ['trend_score', 'buy_pressure', 'sell_pressure'],
                'data_appendix_priority': 5,
                'expected_keys': ['trend_score', 'buy_pressure', 'sell_pressure']
            },
            
            # TIER 2: Supporting Data Endpoints (Data Appendix: "Supporting Data")
            'volume_flow': {
                'url': 'volume-flow/',
                'params': {'timeframe': '1h'},
                'weight': 10,
                'description': 'Money flow analysis',
                'purpose': 'General market flow patterns',
                'success_indicators': ['inflow_data', 'outflow_data', 'net_flow'],
                'data_appendix_priority': 6,
                'expected_keys': ['inflow', 'outflow', 'currencies']
            },
            'volatility_index': {
                'url': 'volatility-index/',
                'params': {'e': 'binance', 'timeframe': '1h'},
                'weight': 9,
                'description': 'Market volatility measurement',
                'purpose': 'Risk assessment metrics',
                'success_indicators': ['volatility_level', 'risk_metrics'],
                'data_appendix_priority': 7,
                'expected_keys': ['volatility', 'exchange', 'timeframe']
            },
            'ohlcv': {
                'url': 'ohlcv/',
                'params': {'pair': '{symbol}-USDT', 'e': 'binance', 'timeframe': '1h'},
                'weight': 10,
                'description': 'Historical price data',
                'purpose': 'Technical analysis foundation with OHLCV data',
                'success_indicators': ['open', 'high', 'low', 'close', 'volume'],
                'data_appendix_priority': 8,
                'expected_keys': ['open', 'high', 'low', 'close', 'volume']
            },
            'ai_screener': {
                'url': 'ai-screener/',
                'params': {'type': 'full'},
                'weight': 12,
                'description': 'AI-driven market analysis',
                'purpose': 'AI-generated trading signals and market assessments',
                'success_indicators': ['ai_signals', 'market_assessment'],
                'data_appendix_priority': 9,
                'expected_keys': ['signals', 'analysis', 'recommendations']
            },
            'whale_trades': {
                'url': 'xtrades/',
                'params': {'e': 'binance', 'symbol': 'BTC'},  # Use BTC as market proxy
                'weight': 8,
                'description': 'Large transaction tracking',
                'purpose': 'Institutional trading activity and market impact',
                'success_indicators': ['whale_transactions', 'market_impact'],
                'data_appendix_priority': 10,
                'expected_keys': ['trades', 'volume', 'exchange']
            },
            
            # TIER 3: Market Context Endpoints (Data Appendix: "Market Context")
            'market_list': {
                'url': 'coinlist/',
                'params': {'e': 'binance'},
                'weight': 3,
                'description': 'Available trading pairs validation',
                'purpose': 'Trading pair validation - confirms ETH-USDT availability',
                'success_indicators': ['trading_pairs', 'pair_validation'],
                'data_appendix_priority': 11,
                'expected_keys': ['pairs', 'symbols', 'markets']
            },
            'cryptocurrency_info': {
                'url': 'cryptocurrency-info/',
                'params': {'algorithm': 'DeFi', 'e': 'binance'},
                'weight': 6,
                'description': 'Cryptocurrency detailed information',
                'purpose': 'Comprehensive crypto asset data including supply metrics',
                'success_indicators': ['supply_metrics', 'fundamental_data'],
                'data_appendix_priority': 12,
                'expected_keys': ['algorithm', 'supply', 'metrics']
            },
            'coin_info': {
                'url': 'coininfo/',
                'params': {},
                'weight': 4,
                'description': 'General cryptocurrency information',
                'purpose': 'Symbol information, market cap data, price metrics',
                'success_indicators': ['market_cap', 'price_metrics'],
                'data_appendix_priority': 13,
                'expected_keys': ['symbol', 'market_cap', 'price']
            },
            'forex_rates': {
                'url': 'forex-rates/',
                'params': {'source': 'USD'},
                'weight': 2,
                'description': 'Currency conversion rates',
                'purpose': 'Currency context for international analysis',
                'success_indicators': ['exchange_rates', 'currency_data'],
                'data_appendix_priority': 14,
                'expected_keys': ['USD', 'rates', 'currencies']
            },
            'rapid_movements': {
                'url': 'rapid-movements/',
                'params': {},
                'weight': 6,
                'description': 'Sudden price movement detection',
                'purpose': 'Market volatility and momentum indicators',
                'success_indicators': ['rapid_changes', 'momentum_indicators'],
                'data_appendix_priority': 15,
                'expected_keys': ['movements', 'changes', 'volatility']
            },
            'tickerlist_pro': {
                'url': 'tickerlist-pro/',
                'params': {'e': 'binance'},
                'weight': 7,
                'description': 'Comprehensive market data',
                'purpose': 'Real-time pricing, volume, and change metrics for all pairs',
                'success_indicators': ['pricing_data', 'volume_metrics', 'change_data'],
                'data_appendix_priority': 16,
                'expected_keys': ['tickers', 'prices', 'volume', 'change']
            },
            'merged_buy_sell_volume': {
                'url': '24h-trade-volume-v2/',
                'params': {'pair': '{symbol}-USDT', 'e': 'binance'},
                'weight': 8,
                'description': 'Aggregated trading volume analysis',
                'purpose': 'Buy vs Sell volume comparison for ETH',
                'success_indicators': ['buy_volume', 'sell_volume', 'volume_ratio'],
                'data_appendix_priority': 17,
                'expected_keys': ['buy_volume', 'sell_volume', 'symbol', 'timeframe']
            },
            'ai_screener_analysis': {
                'url': 'ai-screener-analysis/',
                'params': {'symbol': '{symbol}'},
                'weight': 12,
                'description': 'Symbol-specific AI analysis',
                'purpose': 'Detailed AI-driven trade recommendations for specific symbols',
                'success_indicators': ['ai_recommendations', 'symbol_analysis'],
                'data_appendix_priority': 18,
                'expected_keys': ['symbol', 'analysis', 'recommendations']
            }
        }
        
        # Data Appendix compliance metrics
        self.data_appendix_metrics = {
            'total_endpoints': 18,
            'success_rate_target': 100,  # Data Appendix achieved 100% success
            'collection_time_target': 18,  # 18 seconds for all endpoints
            'rate_limit_compliance': True,  # 1 second per request
            'data_completeness_target': 100,  # Full dataset availability
            'timestamp_consistency': True  # All within 18-second window
        }
        
        logger.info(f"Enhanced Cryptometer Analyzer V2 initialized with {len(self.endpoints)} endpoints")
        logger.info(f"Data Appendix compliance: {self.data_appendix_metrics}")
    
    async def analyze_symbol_complete(self, symbol: str) -> CryptometerAnalysis:
        """
        Complete analysis using all 18 endpoints with Data Appendix compliance
        """
        start_time = time.time()
        logger.info(f"Starting enhanced Cryptometer analysis for {symbol} (Data Appendix V2)")
        
        endpoint_scores = []
        successful_endpoints = 0
        
        # Process all endpoints with 1-second delay (Data Appendix compliance)
        for i, (endpoint_name, config) in enumerate(self.endpoints.items(), 1):
            logger.info(f"Analyzing endpoint {i}/{len(self.endpoints)}: {endpoint_name}")
            
            try:
                # Apply symbol substitution to parameters
                params = self._substitute_symbol_params(config['params'], symbol)
                
                # Make API request
                success, data, processing_time = await self._make_request(
                    config['url'], 
                    params, 
                    endpoint_name
                )
                
                if success:
                    # Analyze endpoint data with enhanced scoring
                    score, confidence, patterns, data_quality = self._analyze_endpoint_enhanced(
                        endpoint_name, data, symbol, config
                    )
                    
                    endpoint_scores.append(EndpointScore(
                        endpoint=endpoint_name,
                        success=True,
                        score=score,
                        confidence=confidence,
                        patterns=patterns,
                        data_quality=data_quality,
                        processing_time=processing_time
                    ))
                    successful_endpoints += 1
                    logger.info(f"✅ {endpoint_name}: {score:.1f}% (confidence: {confidence:.2f})")
                else:
                    endpoint_scores.append(EndpointScore(
                        endpoint=endpoint_name,
                        success=False,
                        score=0.0,
                        confidence=0.0,
                        patterns=[],
                        data_quality=0.0,
                        processing_time=processing_time,
                        error_message=str(data)
                    ))
                    logger.warning(f"❌ {endpoint_name}: Failed - {data}")
                
            except Exception as e:
                endpoint_scores.append(EndpointScore(
                    endpoint=endpoint_name,
                    success=False,
                    score=0.0,
                    confidence=0.0,
                    patterns=[],
                    error_message=str(e)
                ))
                logger.error(f"❌ {endpoint_name}: Exception - {e}")
            
            # Rate limiting compliance (1 second delay)
            await asyncio.sleep(1)
        
        # Calculate calibrated score with enhanced algorithm
        calibrated_result = self._calibrate_scores_enhanced(symbol, endpoint_scores)
        
        total_time = time.time() - start_time
        
        # Assess Data Appendix compliance
        data_appendix_compliance = self._assess_data_appendix_compliance(
            successful_endpoints, total_time
        )
        
        logger.info(f"Enhanced analysis complete for {symbol}: {calibrated_result['final_score']:.1f}% "
                   f"({successful_endpoints}/{len(self.endpoints)} endpoints, {total_time:.1f}s)")
        
        return CryptometerAnalysis(
            symbol=symbol,
            endpoint_scores=endpoint_scores,
            calibrated_score=calibrated_result['final_score'],
            confidence=calibrated_result['confidence'],
            direction=calibrated_result['direction'],
            analysis_summary=calibrated_result['summary'],
            successful_endpoints=successful_endpoints,
            total_endpoints=len(self.endpoints),
            processing_time=total_time,
            data_appendix_compliance=data_appendix_compliance
        )
    
    def _substitute_symbol_params(self, params: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Substitute symbol placeholders in parameters"""
        substituted = {}
        for key, value in params.items():
            if isinstance(value, str):
                substituted[key] = value.format(
                    symbol=symbol,
                    symbol_lower=symbol.lower()
                )
            else:
                substituted[key] = value
        return substituted
    
    async def _make_request(self, url: str, params: Dict[str, Any], endpoint_name: str) -> Tuple[bool, Any, float]:
        """Make API request with enhanced error handling"""
        start_time = time.time()
        
        try:
            full_url = f"{self.base_url}/{url}"
            params['api_key'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, params=params, timeout=10) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return True, data, processing_time
                    else:
                        error_text = await response.text()
                        return False, f"HTTP {response.status}: {error_text}", processing_time
                        
        except Exception as e:
            processing_time = time.time() - start_time
            return False, str(e), processing_time
    
    def _analyze_endpoint_enhanced(self, endpoint_name: str, data: Any, symbol: str, 
                                 config: Dict[str, Any]) -> Tuple[float, float, List[str], float]:
        """Enhanced endpoint analysis with Data Appendix compliance"""
        
        if not data:
            return 0.0, 0.0, [], 0.0
        
        try:
            # Convert list responses to dict format for consistent processing
            if isinstance(data, list) and data:
                data = {'data': data, 'count': len(data)}
            
            if not isinstance(data, dict):
                return 0.0, 0.0, [], 0.0
            
            # Data quality assessment based on expected keys
            expected_keys = config.get('expected_keys', [])
            data_quality = self._assess_data_quality(data, expected_keys)
            
            # Enhanced scoring based on endpoint priority and data quality
            base_score = config.get('weight', 5) * 5  # Convert weight to percentage base
            priority_multiplier = self._get_priority_multiplier(config.get('data_appendix_priority', 18))
            quality_multiplier = data_quality
            
            # Calculate final score
            score = min(100.0, base_score * priority_multiplier * quality_multiplier)
            
            # Enhanced confidence based on data completeness and structure
            confidence = self._calculate_enhanced_confidence(data, expected_keys, data_quality)
            
            # Pattern identification based on Data Appendix insights
            patterns = self._identify_enhanced_patterns(endpoint_name, data, symbol)
            
            return score, confidence, patterns, data_quality
            
        except Exception as e:
            logger.error(f"Error analyzing {endpoint_name}: {e}")
            return 0.0, 0.0, [], 0.0
    
    def _assess_data_quality(self, data: Dict[str, Any], expected_keys: List[str]) -> float:
        """Assess data quality based on expected keys from Data Appendix"""
        if not expected_keys:
            return 0.8  # Default quality for endpoints without specific expectations
        
        # Check for presence of expected keys
        found_keys = 0
        for key in expected_keys:
            if self._deep_key_search(data, key):
                found_keys += 1
        
        # Calculate quality score
        quality_score = found_keys / len(expected_keys) if expected_keys else 0.8
        
        # Bonus for data richness
        if isinstance(data, dict):
            data_richness = min(1.0, len(data) / 10)  # Bonus for more data fields
            quality_score = min(1.0, quality_score + (data_richness * 0.2))
        
        return quality_score
    
    def _deep_key_search(self, data: Any, key: str) -> bool:
        """Deep search for key in nested data structures"""
        if isinstance(data, dict):
            if key.lower() in [k.lower() for k in data.keys()]:
                return True
            for value in data.values():
                if self._deep_key_search(value, key):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._deep_key_search(item, key):
                    return True
        return False
    
    def _get_priority_multiplier(self, priority: int) -> float:
        """Get priority multiplier based on Data Appendix priority ranking"""
        # Higher priority (lower number) gets higher multiplier
        if priority <= 5:  # Tier 1: Most valuable
            return 1.2
        elif priority <= 10:  # Tier 2: Supporting data
            return 1.0
        else:  # Tier 3: Market context
            return 0.8
    
    def _calculate_enhanced_confidence(self, data: Dict[str, Any], expected_keys: List[str], 
                                     data_quality: float) -> float:
        """Calculate enhanced confidence score"""
        base_confidence = 0.5
        
        # Data quality contribution
        quality_contribution = data_quality * 0.4
        
        # Data completeness contribution
        completeness = min(1.0, len(data) / 5) * 0.3 if isinstance(data, dict) else 0.0
        
        # Structure consistency contribution
        structure_score = 0.2 if isinstance(data, dict) and data else 0.0
        
        return min(0.95, base_confidence + quality_contribution + completeness + structure_score)
    
    def _identify_enhanced_patterns(self, endpoint_name: str, data: Dict[str, Any], 
                                  symbol: str) -> List[str]:
        """Identify trading patterns based on Data Appendix insights"""
        patterns = []
        
        try:
            # Endpoint-specific pattern identification based on Data Appendix findings
            if endpoint_name == 'liquidity_lens':
                patterns.extend(self._analyze_liquidity_patterns(data))
            elif endpoint_name == 'ls_ratio':
                patterns.extend(self._analyze_ls_ratio_patterns(data))
            elif endpoint_name == 'total_liquidation_data':
                patterns.extend(self._analyze_liquidation_patterns(data))
            elif endpoint_name == 'trend_indicator_v3':
                patterns.extend(self._analyze_trend_patterns(data))
            elif endpoint_name == 'large_trades_activity':
                patterns.extend(self._analyze_institutional_patterns(data))
            else:
                # Generic pattern identification
                patterns.extend(self._analyze_generic_patterns(data))
            
        except Exception as e:
            logger.debug(f"Pattern identification error for {endpoint_name}: {e}")
            patterns.append('data_available')
        
        return patterns or ['endpoint_responsive']
    
    def _analyze_liquidity_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Analyze liquidity patterns based on Data Appendix findings"""
        patterns = []
        
        # Look for ETH-specific liquidity data (Data Appendix: ETH Inflow: 37,983,823.22)
        if self._deep_key_search(data, 'ETH') or self._deep_key_search(data, 'inflow'):
            patterns.append('eth_liquidity_data')
        
        if self._deep_key_search(data, 'netflow') or self._deep_key_search(data, 'net_flow'):
            patterns.append('net_flow_analysis')
        
        # Check for positive/negative flow patterns
        for key, value in data.items() if isinstance(data, dict) else []:
            if isinstance(value, (int, float)):
                if 'inflow' in key.lower() and value > 0:
                    patterns.append('positive_inflow')
                elif 'outflow' in key.lower() and value > 0:
                    patterns.append('outflow_pressure')
        
        return patterns
    
    def _analyze_ls_ratio_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Analyze Long/Short ratio patterns"""
        patterns = []
        
        if self._deep_key_search(data, 'ratio'):
            patterns.append('ls_ratio_data')
        
        if self._deep_key_search(data, 'buy_percentage'):
            patterns.append('positioning_data')
        
        return patterns
    
    def _analyze_liquidation_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Analyze liquidation patterns based on Data Appendix (4.33:1 long liquidations)"""
        patterns = []
        
        # Check for exchange-specific liquidation data
        exchanges = ['binance_futures', 'bybit', 'okx', 'bitmex']
        for exchange in exchanges:
            if self._deep_key_search(data, exchange):
                patterns.append(f'{exchange}_liquidations')
        
        if self._deep_key_search(data, 'longs') and self._deep_key_search(data, 'shorts'):
            patterns.append('long_short_liquidation_ratio')
        
        return patterns
    
    def _analyze_trend_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Analyze trend patterns"""
        patterns = []
        
        if self._deep_key_search(data, 'trend_score'):
            patterns.append('trend_analysis')
        
        if self._deep_key_search(data, 'buy_pressure'):
            patterns.append('buy_pressure_data')
        
        if self._deep_key_search(data, 'sell_pressure'):
            patterns.append('sell_pressure_data')
        
        return patterns
    
    def _analyze_institutional_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Analyze institutional trading patterns"""
        patterns = []
        
        if self._deep_key_search(data, 'large_trades'):
            patterns.append('institutional_activity')
        
        if self._deep_key_search(data, 'volume'):
            patterns.append('volume_analysis')
        
        return patterns
    
    def _analyze_generic_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Generic pattern analysis for any endpoint"""
        patterns = []
        
        if isinstance(data, dict) and data:
            patterns.append('structured_data')
            
            # Check for common trading data patterns
            trading_keys = ['price', 'volume', 'change', 'high', 'low', 'open', 'close']
            for key in trading_keys:
                if self._deep_key_search(data, key):
                    patterns.append(f'{key}_data')
        
        return patterns
    
    def _calibrate_scores_enhanced(self, symbol: str, endpoint_scores: List[EndpointScore]) -> Dict[str, Any]:
        """Enhanced score calibration with Data Appendix compliance"""
        
        if not endpoint_scores:
            return {
                'final_score': 0.0,
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'summary': 'No endpoint data available'
            }
        
        # Separate successful and failed endpoints
        successful_scores = [score for score in endpoint_scores if score.success]
        failed_count = len(endpoint_scores) - len(successful_scores)
        
        if not successful_scores:
            return {
                'final_score': 0.0,
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'summary': f'All {len(endpoint_scores)} endpoints failed'
            }
        
        # Calculate weighted score with dynamic redistribution
        total_possible_weight = sum(self.endpoints[config_name]['weight'] 
                                  for config_name in self.endpoints.keys())
        
        successful_weight = 0.0
        weighted_score_sum = 0.0
        
        for endpoint_score in successful_scores:
            if endpoint_score.endpoint in self.endpoints:
                weight = self.endpoints[endpoint_score.endpoint]['weight']
                priority = self.endpoints[endpoint_score.endpoint].get('data_appendix_priority', 18)
                
                # Apply priority multiplier
                priority_multiplier = self._get_priority_multiplier(priority)
                adjusted_weight = weight * priority_multiplier
                
                successful_weight += adjusted_weight
                weighted_score_sum += endpoint_score.score * adjusted_weight
        
        # Dynamic weight redistribution to maintain 100-point scale
        if successful_weight > 0:
            weight_redistribution_factor = 100.0 / successful_weight
            base_score = weighted_score_sum / successful_weight
        else:
            weight_redistribution_factor = 1.0
            base_score = 0.0
        
        # Data Appendix compliance bonus
        success_rate = len(successful_scores) / len(endpoint_scores)
        compliance_bonus = 0.0
        
        if success_rate >= 0.9:  # 90%+ success rate
            compliance_bonus = 5.0
        elif success_rate >= 0.8:  # 80%+ success rate
            compliance_bonus = 2.0
        
        # Calculate final score
        final_score = min(100.0, base_score + compliance_bonus)
        
        # Enhanced confidence calculation
        avg_confidence = sum(score.confidence for score in successful_scores) / len(successful_scores)
        data_quality_avg = sum(score.data_quality for score in successful_scores) / len(successful_scores)
        
        # Confidence penalties for failed endpoints
        failure_penalty = min(0.3, failed_count * 0.05)
        enhanced_confidence = max(0.1, (avg_confidence + data_quality_avg) / 2 - failure_penalty)
        
        # Determine direction based on enhanced analysis
        direction = self._determine_enhanced_direction(final_score, successful_scores)
        
        # Generate enhanced summary
        summary = self._generate_enhanced_summary(
            symbol, final_score, len(successful_scores), len(endpoint_scores), direction
        )
        
        logger.info(f"Enhanced calibration: {final_score:.1f}% from {len(successful_scores)}/{len(endpoint_scores)} endpoints")
        
        return {
            'final_score': final_score,
            'confidence': enhanced_confidence,
            'direction': direction,
            'summary': summary,
            'successful_endpoints': len(successful_scores),
            'total_endpoints': len(endpoint_scores),
            'success_rate': success_rate,
            'data_appendix_compliance': success_rate >= 0.8
        }
    
    def _determine_enhanced_direction(self, score: float, successful_scores: List[EndpointScore]) -> str:
        """Determine market direction with enhanced logic"""
        
        # Score-based direction
        if score >= 70:
            score_direction = 'BULLISH'
        elif score <= 30:
            score_direction = 'BEARISH'
        else:
            score_direction = 'NEUTRAL'
        
        # Pattern-based direction analysis
        bullish_patterns = 0
        bearish_patterns = 0
        
        for endpoint_score in successful_scores:
            for pattern in endpoint_score.patterns:
                if any(word in pattern.lower() for word in ['positive', 'buy', 'bullish', 'inflow']):
                    bullish_patterns += 1
                elif any(word in pattern.lower() for word in ['negative', 'sell', 'bearish', 'outflow']):
                    bearish_patterns += 1
        
        # Combine score and pattern analysis
        if score_direction == 'BULLISH' and bullish_patterns > bearish_patterns:
            return 'BULLISH'
        elif score_direction == 'BEARISH' and bearish_patterns > bullish_patterns:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _generate_enhanced_summary(self, symbol: str, score: float, successful: int, 
                                 total: int, direction: str) -> str:
        """Generate enhanced analysis summary"""
        
        success_rate = (successful / total) * 100
        
        summary = f"Enhanced Cryptometer analysis for {symbol}: {score:.1f}% ({direction}). "
        summary += f"Data Appendix compliance: {successful}/{total} endpoints ({success_rate:.0f}% success rate). "
        
        if success_rate >= 90:
            summary += "Excellent data coverage with high reliability."
        elif success_rate >= 80:
            summary += "Good data coverage with reliable analysis."
        elif success_rate >= 60:
            summary += "Moderate data coverage, analysis may be limited."
        else:
            summary += "Limited data coverage, use with caution."
        
        return summary
    
    def _assess_data_appendix_compliance(self, successful_endpoints: int, total_time: float) -> bool:
        """Assess compliance with Data Appendix standards"""
        
        success_rate = successful_endpoints / self.data_appendix_metrics['total_endpoints']
        time_compliance = total_time <= (self.data_appendix_metrics['collection_time_target'] + 5)  # 5s buffer
        
        # Data Appendix achieved 100% success in 18 seconds
        # We consider 80%+ success in reasonable time as compliant
        return success_rate >= 0.8 and time_compliance
    
    def get_endpoint_status(self) -> Dict[str, Any]:
        """Get detailed endpoint status and Data Appendix compliance info"""
        
        return {
            'total_endpoints': len(self.endpoints),
            'endpoint_tiers': {
                'tier_1_high_value': [name for name, config in self.endpoints.items() 
                                    if config.get('data_appendix_priority', 18) <= 5],
                'tier_2_supporting': [name for name, config in self.endpoints.items() 
                                    if 6 <= config.get('data_appendix_priority', 18) <= 10],
                'tier_3_context': [name for name, config in self.endpoints.items() 
                                 if config.get('data_appendix_priority', 18) > 10]
            },
            'data_appendix_compliance': self.data_appendix_metrics,
            'optimization_focus': 'ETH analysis with cross-exchange liquidation tracking',
            'rate_limiting': '1 second per request for API compliance',
            'expected_performance': {
                'success_rate': '80-100%',
                'analysis_time': '18-25 seconds',
                'data_quality': 'High with structured validation'
            }
        }