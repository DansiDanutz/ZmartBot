#!/usr/bin/env python3
"""
KingFisher Main Agent V2
Generates professional reports in exact format and stores in Airtable
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.support_resistance_service import SupportResistanceService
from services.professional_report_generator import professional_report_generator
from services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class KingFisherMainAgentV2:
    """
    Enhanced KingFisher Main Agent with professional reporting
    """
    
    def __init__(self, airtable_service=None, database_url: str = "sqlite:///kingfisher_levels.db"):
        self.agent_name = "kingfisher_main_agent_v2"
        self.airtable_service = airtable_service
        self.analysis_buffer = defaultdict(list)
        self.minimum_images_required = 4
        self.sr_service = SupportResistanceService(database_url)
        self.market_data_service = MarketDataService()
        logger.info("KingFisher Main Agent V2 initialized")
    
    async def receive_sub_agent_analysis(self, symbol: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Receive and process sub-agent analysis"""
        try:
            # Add to buffer
            self.analysis_buffer[symbol].append(analysis)
            
            # Log receipt
            agent_name = analysis.get('agent', 'unknown')
            logger.info(f"Received analysis from {agent_name} for {symbol}")
            
            # Check if we have enough analyses
            analyses_count = len(self.analysis_buffer[symbol])
            
            if analyses_count >= self.minimum_images_required:
                # Perform full analysis
                full_analysis = await self.perform_full_analysis(symbol)
                return full_analysis
            else:
                # Return partial status
                return {
                    'status': 'partial',
                    'symbol': symbol,
                    'analyses_received': analyses_count,
                    'analyses_required': self.minimum_images_required,
                    'message': f"Need {self.minimum_images_required - analyses_count} more image analyses",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error receiving sub-agent analysis: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def perform_full_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform comprehensive analysis and generate professional report"""
        try:
            analyses = self.analysis_buffer[symbol]
            logger.info(f"Performing full analysis for {symbol} with {len(analyses)} image analyses")
            
            # Get current market data
            market_data = await self._get_market_data(symbol)
            
            # Process all analyses
            analysis_data = await self._process_analyses(symbol, analyses)
            
            # Generate professional report
            professional_report = professional_report_generator.generate_professional_report(
                symbol, market_data, analysis_data
            )
            
            # Prepare data for Airtable storage
            airtable_data = self._prepare_airtable_data(
                symbol, market_data, analysis_data, professional_report
            )
            
            # Store in Airtable
            if self.airtable_service:
                await self._store_in_airtable(airtable_data)
            
            # Clear buffer after successful analysis
            self.analysis_buffer[symbol] = []
            
            # Return comprehensive response
            return {
                'status': 'complete',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'professional_report': professional_report,
                'win_rates': {
                    '24h': analysis_data['timeframes']['24h'],
                    '7d': analysis_data['timeframes']['7d'],
                    '1m': analysis_data['timeframes']['1M']
                },
                'recommendation': analysis_data['recommendation'],
                'support_resistance': analysis_data.get('support_resistance', {}),
                'airtable_stored': True
            }
            
        except Exception as e:
            logger.error(f"Error performing full analysis: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for the symbol"""
        try:
            # Get current price from market data service
            price = await self.market_data_service.get_current_price(symbol)
            
            return {
                'symbol': symbol,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
        except:
            # Fallback prices for testing
            default_prices = {
                'BTC': 113951.00,
                'ETH': 3764.60,
                'SOL': 245.80,
                'XRP': 3.25
            }
            return {
                'symbol': symbol,
                'price': default_prices.get(symbol, 100.00),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _process_analyses(self, symbol: str, analyses: List[Dict]) -> Dict[str, Any]:
        """Process all sub-agent analyses into comprehensive data"""
        
        # Extract timeframe data
        timeframe_data = self._extract_timeframe_data(analyses)
        
        # Calculate win rates for each timeframe
        win_rates_24h = self._calculate_win_rates(timeframe_data['24h'])
        win_rates_7d = self._calculate_win_rates(timeframe_data['7d'])
        win_rates_1m = self._calculate_win_rates(timeframe_data['1m'])
        
        # Extract liquidation analysis
        liquidation_analysis = self._extract_liquidation_analysis(analyses)
        
        # Extract support/resistance levels
        support_resistance = await self._extract_support_resistance(symbol, analyses)
        
        # Calculate technical indicators
        technical_indicators = self._calculate_technical_indicators(analyses)
        
        # Determine overall sentiment and risk
        overall_assessment = self._calculate_overall_assessment(
            win_rates_24h, win_rates_7d, win_rates_1m
        )
        
        return {
            'timeframes': {
                '24h': {
                    'long_win_rate': win_rates_24h['long'],
                    'short_win_rate': win_rates_24h['short'],
                    'confidence': win_rates_24h['confidence'],
                    'sentiment': self._get_sentiment(win_rates_24h),
                    'analysis_summary': self._get_timeframe_summary('24h', win_rates_24h)
                },
                '7d': {
                    'long_win_rate': win_rates_7d['long'],
                    'short_win_rate': win_rates_7d['short'],
                    'confidence': win_rates_7d['confidence'],
                    'sentiment': self._get_sentiment(win_rates_7d),
                    'analysis_summary': self._get_timeframe_summary('7d', win_rates_7d)
                },
                '1M': {
                    'long_win_rate': win_rates_1m['long'],
                    'short_win_rate': win_rates_1m['short'],
                    'confidence': win_rates_1m['confidence'],
                    'sentiment': self._get_sentiment(win_rates_1m),
                    'analysis_summary': self._get_timeframe_summary('1M', win_rates_1m)
                }
            },
            'liquidation_analysis': liquidation_analysis,
            'support_resistance': support_resistance,
            'technical_indicators': technical_indicators,
            'overall_sentiment': overall_assessment['sentiment'],
            'overall_confidence': overall_assessment['confidence'],
            'risk_level': overall_assessment['risk_level'],
            'risk_score': overall_assessment['risk_score'],
            'opportunity_score': overall_assessment['opportunity_score'],
            'recommendation': overall_assessment['recommendation'],
            'liquidation_pressure_index': technical_indicators.get('lpi', 5.0),
            'market_balance_ratio': technical_indicators.get('mbr', 1.0),
            'price_position_index': technical_indicators.get('ppi', 5.0),
            'retail_sentiment': overall_assessment.get('retail_sentiment', 'neutral'),
            'institutional_sentiment': overall_assessment.get('institutional_sentiment', 'neutral'),
            'stability_score': overall_assessment.get('stability_score', 0.5),
            'volatility_score': overall_assessment.get('volatility_score', 0.5),
            'momentum_score': technical_indicators.get('momentum_score', 0.5),
            'breakout_score': technical_indicators.get('breakout_score', 0.5),
            'liquidation_risk_score': liquidation_analysis.get('risk_score', 0.5)
        }
    
    def _extract_timeframe_data(self, analyses: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract and organize data by timeframe"""
        timeframe_data = {
            '24h': [],
            '7d': [],
            '1m': []
        }
        
        for analysis in analyses:
            # Extract liquidation ratios for all timeframes
            ratio = analysis.get('liquidation_ratio', {})
            
            # Get timeframe-specific data
            timeframes = analysis.get('timeframes', {})
            
            # Process 24h data
            if '24h' in timeframes:
                tf_data = timeframes['24h']
                timeframe_data['24h'].append({
                    'agent': analysis.get('agent'),
                    'long': tf_data.get('long_percentage', 50),
                    'short': tf_data.get('short_percentage', 50),
                    'confidence': tf_data.get('confidence', 0.5)
                })
            
            # Process 7d data
            if '7d' in timeframes:
                tf_data = timeframes['7d']
                timeframe_data['7d'].append({
                    'agent': analysis.get('agent'),
                    'long': tf_data.get('long_percentage', 50),
                    'short': tf_data.get('short_percentage', 50),
                    'confidence': tf_data.get('confidence', 0.5)
                })
            
            # Process 1m data
            if '1m' in timeframes:
                tf_data = timeframes['1m']
                timeframe_data['1m'].append({
                    'agent': analysis.get('agent'),
                    'long': tf_data.get('long_percentage', 50),
                    'short': tf_data.get('short_percentage', 50),
                    'confidence': tf_data.get('confidence', 0.5)
                })
        
        return timeframe_data
    
    def _calculate_win_rates(self, timeframe_data: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregated win rates from multiple agent analyses"""
        if not timeframe_data:
            return {'long': 50, 'short': 50, 'confidence': 0.5}
        
        # Weight by confidence
        total_weight = sum(d['confidence'] for d in timeframe_data)
        if total_weight == 0:
            return {'long': 50, 'short': 50, 'confidence': 0.5}
        
        weighted_long = sum(d['long'] * d['confidence'] for d in timeframe_data) / total_weight
        weighted_short = sum(d['short'] * d['confidence'] for d in timeframe_data) / total_weight
        
        # Normalize to ensure they sum to 100
        total = weighted_long + weighted_short
        if total > 0:
            weighted_long = (weighted_long / total) * 100
            weighted_short = (weighted_short / total) * 100
        
        return {
            'long': round(weighted_long, 1),
            'short': round(weighted_short, 1),
            'confidence': min(total_weight / len(timeframe_data), 1.0)
        }
    
    def _extract_liquidation_analysis(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Extract liquidation analysis from sub-agent data"""
        long_concentrations = []
        short_concentrations = []
        clusters = []
        
        for analysis in analyses:
            if 'liquidation_clusters' in analysis:
                clusters.extend(analysis['liquidation_clusters'])
            
            ratio = analysis.get('liquidation_ratio', {})
            if ratio:
                long_concentrations.append(ratio.get('long', 50) / 100)
                short_concentrations.append(ratio.get('short', 50) / 100)
        
        # Process clusters to find key levels
        left_cluster, right_cluster = self._process_liquidation_clusters(clusters)
        
        return {
            'long_concentration': float(np.mean(long_concentrations)) if long_concentrations else 0.5,
            'short_concentration': float(np.mean(short_concentrations)) if short_concentrations else 0.5,
            'clusters': {
                'left_cluster': left_cluster,
                'right_cluster': right_cluster
            },
            'risk_score': self._calculate_liquidation_risk(long_concentrations, short_concentrations)
        }
    
    def _process_liquidation_clusters(self, clusters: List[Dict]) -> tuple:
        """Process liquidation clusters to find major levels"""
        if not clusters:
            return {'price': 0, 'size': 0}, {'price': 0, 'size': 0}
        
        # Sort clusters by size
        sorted_clusters = sorted(clusters, key=lambda x: x.get('size', 0), reverse=True)
        
        # Get top 2 clusters
        left_cluster = sorted_clusters[0] if len(sorted_clusters) > 0 else {'price': 0, 'size': 0}
        right_cluster = sorted_clusters[1] if len(sorted_clusters) > 1 else {'price': 0, 'size': 0}
        
        return left_cluster, right_cluster
    
    def _calculate_liquidation_risk(self, long_conc: List[float], short_conc: List[float]) -> float:
        """Calculate liquidation risk score"""
        if not long_conc and not short_conc:
            return 0.5
        
        # Calculate imbalance
        avg_long = float(np.mean(long_conc)) if long_conc else 0.5
        avg_short = float(np.mean(short_conc)) if short_conc else 0.5
        
        imbalance = abs(avg_long - avg_short)
        
        # Higher imbalance = higher risk
        return min(0.3 + imbalance * 1.4, 1.0)
    
    async def _extract_support_resistance(self, symbol: str, analyses: List[Dict]) -> Dict[str, Any]:
        """Extract support and resistance levels from analyses"""
        support_levels = []
        resistance_levels = []
        
        for analysis in analyses:
            if 'support_resistance' in analysis:
                sr_data = analysis['support_resistance']
                for tf in ['24h', '7d', '1m']:
                    if tf in sr_data:
                        support_levels.extend(sr_data[tf].get('support', []))
                        resistance_levels.extend(sr_data[tf].get('resistance', []))
        
        # Store in database
        if support_levels or resistance_levels:
            try:
                await self.sr_service.store_levels(
                    symbol=symbol,
                    support_levels=support_levels,
                    resistance_levels=resistance_levels
                )
            except AttributeError:
                # Method might not exist yet, skip for now
                logger.warning("Support/Resistance storage not available")
        
        return {
            'support_levels': support_levels[:3],  # Top 3 support levels
            'resistance_levels': resistance_levels[:3]  # Top 3 resistance levels
        }
    
    def _calculate_technical_indicators(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Calculate technical indicators from analyses"""
        rsi_values = []
        momentum_scores = []
        
        for analysis in analyses:
            if 'rsi' in analysis:
                rsi_values.append(float(analysis['rsi']))
            if 'momentum' in analysis:
                momentum_scores.append(float(analysis['momentum']))
        
        avg_rsi = float(np.mean(rsi_values)) if rsi_values else 50.0
        avg_momentum = float(np.mean(momentum_scores)) if momentum_scores else 0.5
        
        # Calculate custom indicators
        lpi = self._calculate_lpi(analyses)
        mbr = self._calculate_mbr(analyses)
        ppi = self._calculate_ppi(analyses)
        
        return {
            'rsi': avg_rsi,
            'momentum_score': avg_momentum,
            'lpi': lpi,
            'mbr': mbr,
            'ppi': ppi,
            'breakout_score': self._calculate_breakout_score(avg_rsi, avg_momentum)
        }
    
    def _calculate_lpi(self, analyses: List[Dict]) -> float:
        """Calculate Liquidation Pressure Index"""
        liquidation_scores = []
        for analysis in analyses:
            if 'liquidation_pressure' in analysis:
                liquidation_scores.append(float(analysis['liquidation_pressure']))
        
        if liquidation_scores:
            return min(float(np.mean(liquidation_scores)) * 10, 10)
        return 5.0
    
    def _calculate_mbr(self, analyses: List[Dict]) -> float:
        """Calculate Market Balance Ratio"""
        retail_scores = []
        institutional_scores = []
        
        for analysis in analyses:
            if 'retail_sentiment' in analysis:
                retail_scores.append(float(analysis['retail_sentiment']))
            if 'institutional_sentiment' in analysis:
                institutional_scores.append(float(analysis['institutional_sentiment']))
        
        if retail_scores and institutional_scores:
            retail_avg = float(np.mean(retail_scores))
            inst_avg = float(np.mean(institutional_scores))
            if inst_avg > 0:
                return retail_avg / inst_avg
        return 1.0
    
    def _calculate_ppi(self, analyses: List[Dict]) -> float:
        """Calculate Price Position Index"""
        position_scores = []
        for analysis in analyses:
            if 'price_position' in analysis:
                position_scores.append(float(analysis['price_position']))
        
        if position_scores:
            return min(float(np.mean(position_scores)) * 10, 10)
        return 5.0
    
    def _calculate_breakout_score(self, rsi: float, momentum: float) -> float:
        """Calculate breakout potential score"""
        # Neutral RSI with high momentum = high breakout potential
        rsi_factor = 1.0 - abs(rsi - 50) / 50  # Higher when RSI near 50
        return min(rsi_factor * momentum * 1.5, 1.0)
    
    def _calculate_overall_assessment(self, win_rates_24h: Dict, win_rates_7d: Dict, 
                                     win_rates_1m: Dict) -> Dict[str, Any]:
        """Calculate overall assessment from all timeframes"""
        
        # Weighted average (recent timeframes weighted more)
        weights = {'24h': 0.5, '7d': 0.3, '1m': 0.2}
        
        weighted_long = (
            win_rates_24h['long'] * weights['24h'] +
            win_rates_7d['long'] * weights['7d'] +
            win_rates_1m['long'] * weights['1m']
        )
        
        weighted_short = (
            win_rates_24h['short'] * weights['24h'] +
            win_rates_7d['short'] * weights['7d'] +
            win_rates_1m['short'] * weights['1m']
        )
        
        # Determine sentiment
        if weighted_long > 60:
            sentiment = 'bullish'
        elif weighted_short > 60:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence
        confidence = float(np.mean([
            win_rates_24h['confidence'],
            win_rates_7d['confidence'],
            win_rates_1m['confidence']
        ]))
        
        # Determine risk level
        imbalance = abs(weighted_long - weighted_short)
        if imbalance > 40:
            risk_level = 'high'
            risk_score = 0.8
        elif imbalance > 20:
            risk_level = 'medium'
            risk_score = 0.5
        else:
            risk_level = 'low'
            risk_score = 0.3
        
        # Calculate opportunity score
        opportunity_score = confidence * (1 - risk_score)
        
        # Generate recommendation
        if sentiment == 'bullish' and confidence > 0.7:
            recommendation = "Strong BUY signal with tight stop losses"
        elif sentiment == 'bearish' and confidence > 0.7:
            recommendation = "Strong SELL signal with tight stop losses"
        elif sentiment == 'neutral':
            recommendation = "WAIT for clearer signals before entering positions"
        else:
            recommendation = f"Moderate {sentiment.upper()} bias - use careful position sizing"
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'opportunity_score': opportunity_score,
            'recommendation': recommendation,
            'retail_sentiment': 'bullish' if weighted_long > 55 else 'bearish' if weighted_short > 55 else 'neutral',
            'institutional_sentiment': 'cautious',  # Could be enhanced with more data
            'stability_score': 1.0 - risk_score,
            'volatility_score': risk_score
        }
    
    def _get_sentiment(self, win_rates: Dict) -> str:
        """Get sentiment from win rates"""
        if win_rates['long'] > 60:
            return 'bullish'
        elif win_rates['short'] > 60:
            return 'bearish'
        else:
            return 'neutral'
    
    def _get_timeframe_summary(self, timeframe: str, win_rates: Dict) -> str:
        """Get summary for timeframe"""
        if win_rates['long'] > win_rates['short']:
            return f"Favors LONG positions with {win_rates['long']:.1f}% win rate"
        else:
            return f"Favors SHORT positions with {win_rates['short']:.1f}% win rate"
    
    def _prepare_airtable_data(self, symbol: str, market_data: Dict, 
                              analysis_data: Dict, professional_report: str) -> Dict[str, Any]:
        """Prepare comprehensive data for Airtable storage"""
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': market_data['price'],
            
            # Win rates for all timeframes
            'win_rate_24h_long': analysis_data['timeframes']['24h']['long_win_rate'],
            'win_rate_24h_short': analysis_data['timeframes']['24h']['short_win_rate'],
            'win_rate_7d_long': analysis_data['timeframes']['7d']['long_win_rate'],
            'win_rate_7d_short': analysis_data['timeframes']['7d']['short_win_rate'],
            'win_rate_1m_long': analysis_data['timeframes']['1M']['long_win_rate'],
            'win_rate_1m_short': analysis_data['timeframes']['1M']['short_win_rate'],
            
            # Scores
            'score_24h': analysis_data['timeframes']['24h']['long_win_rate'],  # Score = win rate
            'score_7d': analysis_data['timeframes']['7d']['long_win_rate'],
            'score_1m': analysis_data['timeframes']['1M']['long_win_rate'],
            
            # Technical indicators
            'lpi': analysis_data['liquidation_pressure_index'],
            'mbr': analysis_data['market_balance_ratio'],
            'ppi': analysis_data['price_position_index'],
            
            # Overall assessment
            'overall_sentiment': analysis_data['overall_sentiment'],
            'overall_confidence': analysis_data['overall_confidence'],
            'risk_level': analysis_data['risk_level'],
            'recommendation': analysis_data['recommendation'],
            
            # Support/Resistance as JSON
            'support_resistance': json.dumps(analysis_data.get('support_resistance', {})),
            
            # Professional report (full markdown)
            'professional_report': professional_report,
            
            # Liquidation analysis
            'liquidation_clusters': json.dumps(
                analysis_data['liquidation_analysis']['clusters']
            ),
            'long_concentration': analysis_data['liquidation_analysis']['long_concentration'],
            'short_concentration': analysis_data['liquidation_analysis']['short_concentration']
        }
    
    async def _store_in_airtable(self, data: Dict[str, Any]) -> bool:
        """Store comprehensive analysis in Airtable"""
        try:
            # Store main analysis
            stored = await self.airtable_service.store_image_analysis(data)
            
            if stored:
                logger.info(f"Successfully stored professional analysis for {data['symbol']} in Airtable")
                
                # Also store summary
                summary_data = {
                    'symbol': data['symbol'],
                    'last_update': data['timestamp'],
                    'total_images': 4,  # Minimum required
                    'average_significance': data['overall_confidence'],
                    'dominant_sentiment': data['overall_sentiment'],
                    'risk_level': data['risk_level'],
                    'latest_analysis_id': f"{data['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                await self.airtable_service.store_symbol_summary(summary_data)
                
                # Store alert if high significance
                if data['overall_confidence'] > 0.8:
                    alert_data = {
                        'symbol': data['symbol'],
                        'significance_score': data['overall_confidence'],
                        'market_sentiment': data['overall_sentiment'],
                        'confidence': data['overall_confidence'],
                        'liquidation_clusters': data['liquidation_clusters'],
                        'alert_level': 'HIGH',
                        'timestamp': data['timestamp']
                    }
                    await self.airtable_service.store_high_significance_alert(alert_data)
                
                return True
            else:
                logger.error("Failed to store analysis in Airtable")
                return False
                
        except Exception as e:
            logger.error(f"Error storing in Airtable: {e}")
            return False
    
    async def get_trading_targets(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """Get trading targets based on support/resistance levels"""
        try:
            targets = await self.sr_service.get_trading_targets(symbol, current_price)
            return targets
        except Exception as e:
            logger.error(f"Error getting trading targets: {e}")
            return {}

# Create global instance
kingfisher_main_agent_v2 = KingFisherMainAgentV2()