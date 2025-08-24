#!/usr/bin/env python3
"""
KingFisher Main Agent
Aggregates sub-agent analyses and calculates final win rate scores
Requires minimum 4 image analyses before providing full analysis
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.support_resistance_service import SupportResistanceService

logger = logging.getLogger(__name__)

class KingFisherMainAgent:
    """
    Main KingFisher Agent that aggregates sub-agent results
    Calculates win rate ratios for Long vs Short positions
    Provides 100-point scoring based on win rate percentage
    """
    
    def __init__(self, airtable_service=None, database_url: str = "sqlite:///kingfisher_levels.db"):
        self.agent_name = "kingfisher_main_agent"
        self.airtable_service = airtable_service
        self.analysis_buffer = defaultdict(list)  # Store analyses by symbol
        self.minimum_images_required = 4
        self.sr_service = SupportResistanceService(database_url)
        logger.info("KingFisher Main Agent initialized")
    
    async def receive_sub_agent_analysis(self, symbol: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive analysis from a sub-agent
        Store it and check if we have enough data for full analysis
        """
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
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def perform_full_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Perform full analysis when minimum images are available
        Calculate win rates for all timeframes
        """
        try:
            analyses = self.analysis_buffer[symbol]
            logger.info(f"Performing full analysis for {symbol} with {len(analyses)} image analyses")
            
            # Extract timeframe data from all analyses
            timeframe_data = self._extract_timeframe_data(analyses)
            
            # Extract and store support/resistance levels
            await self._process_support_resistance_levels(symbol, analyses)
            
            # Calculate win rates for each timeframe
            win_rates_24h = self._calculate_win_rates(timeframe_data['24h'])
            win_rates_7d = self._calculate_win_rates(timeframe_data['7d'])
            win_rates_1m = self._calculate_win_rates(timeframe_data['1m'])
            
            # Calculate final scores (100-point system based on win rate)
            final_score_24h = self._calculate_final_score(win_rates_24h)
            final_score_7d = self._calculate_final_score(win_rates_7d)
            final_score_1m = self._calculate_final_score(win_rates_1m)
            
            # Determine best timeframe and overall recommendation
            best_timeframe = self._determine_best_timeframe(
                final_score_24h, final_score_7d, final_score_1m
            )
            
            # Generate comprehensive analysis
            comprehensive_analysis = {
                'status': 'complete',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'analyses_count': len(analyses),
                'agent': self.agent_name,
                
                # 24-hour analysis
                '24h': {
                    'long_win_rate': win_rates_24h['long'],
                    'short_win_rate': win_rates_24h['short'],
                    'score': final_score_24h['score'],
                    'position': final_score_24h['position'],
                    'confidence': final_score_24h['confidence']
                },
                
                # 7-day analysis
                '7d': {
                    'long_win_rate': win_rates_7d['long'],
                    'short_win_rate': win_rates_7d['short'],
                    'score': final_score_7d['score'],
                    'position': final_score_7d['position'],
                    'confidence': final_score_7d['confidence']
                },
                
                # 1-month analysis
                '1m': {
                    'long_win_rate': win_rates_1m['long'],
                    'short_win_rate': win_rates_1m['short'],
                    'score': final_score_1m['score'],
                    'position': final_score_1m['position'],
                    'confidence': final_score_1m['confidence']
                },
                
                # Overall recommendation
                'recommendation': {
                    'best_timeframe': best_timeframe['timeframe'],
                    'best_position': best_timeframe['position'],
                    'best_score': best_timeframe['score'],
                    'overall_confidence': self._calculate_overall_confidence(analyses)
                },
                
                # Sub-agent breakdown
                'sub_agents_analyzed': self._get_sub_agents_summary(analyses)
            }
            
            # Update Airtable with comprehensive analysis
            if self.airtable_service:
                await self._update_airtable(comprehensive_analysis)
            
            # Clear buffer after successful analysis
            self.analysis_buffer[symbol] = []
            
            logger.info(f"Full analysis complete for {symbol}: Best {best_timeframe['position']} with score {best_timeframe['score']}")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error performing full analysis for {symbol}: {e}")
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_timeframe_data(self, analyses: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract and organize data by timeframe from all analyses"""
        timeframe_data = {
            '24h': [],
            '7d': [],
            '1m': []
        }
        
        for analysis in analyses:
            # Each sub-agent should provide liquidation_ratio with long/short percentages
            ratio = analysis.get('liquidation_ratio', {})
            
            # Extract timeframe-specific data if available
            if 'timeframe' in analysis:
                tf = analysis['timeframe']
                if tf == 'short_term':
                    # Short-term maps to 24h
                    timeframe_data['24h'].append({
                        'agent': analysis.get('agent'),
                        'long': ratio.get('long', 50),
                        'short': ratio.get('short', 50),
                        'confidence': analysis.get('confidence', 0.5)
                    })
                elif tf == 'long_term':
                    # Long-term maps to 1m
                    timeframe_data['1m'].append({
                        'agent': analysis.get('agent'),
                        'long': ratio.get('long', 50),
                        'short': ratio.get('short', 50),
                        'confidence': analysis.get('confidence', 0.5)
                    })
            else:
                # For agents without specific timeframe, distribute across all
                # This applies to liquidation maps, heatmaps, etc.
                data_point = {
                    'agent': analysis.get('agent'),
                    'long': ratio.get('long', 50),
                    'short': ratio.get('short', 50),
                    'confidence': analysis.get('confidence', 0.5)
                }
                
                # Adjust for different timeframes based on agent type
                agent_type = analysis.get('image_type', '')
                
                if 'shortterm' in agent_type:
                    timeframe_data['24h'].append(data_point)
                elif 'longterm' in agent_type:
                    timeframe_data['1m'].append(data_point)
                else:
                    # General analysis applies to all timeframes with different weights
                    timeframe_data['24h'].append({**data_point, 'weight': 1.0})
                    timeframe_data['7d'].append({**data_point, 'weight': 0.8})
                    timeframe_data['1m'].append({**data_point, 'weight': 0.6})
        
        return timeframe_data
    
    def _calculate_win_rates(self, timeframe_data: List[Dict]) -> Dict[str, float]:
        """Calculate weighted win rates for a specific timeframe"""
        if not timeframe_data:
            return {'long': 50.0, 'short': 50.0}
        
        total_long = 0
        total_short = 0
        total_weight = 0
        
        for data in timeframe_data:
            weight = data.get('weight', 1.0) * data.get('confidence', 0.5)
            total_long += data.get('long', 50) * weight
            total_short += data.get('short', 50) * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_long = total_long / total_weight
            avg_short = total_short / total_weight
            
            # Normalize to ensure they sum to 100
            total = avg_long + avg_short
            if total > 0:
                return {
                    'long': (avg_long / total) * 100,
                    'short': (avg_short / total) * 100
                }
        
        return {'long': 50.0, 'short': 50.0}
    
    def _calculate_final_score(self, win_rates: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate final score based on win rate
        Score = Win Rate Percentage (87% win rate = 87 score)
        """
        long_rate = win_rates['long']
        short_rate = win_rates['short']
        
        # Determine which position has higher win rate
        if long_rate > short_rate:
            score = long_rate  # Score is the win rate percentage
            position = 'LONG'
            confidence = min((long_rate - short_rate) / 50, 1.0)  # Confidence based on difference
        else:
            score = short_rate  # Score is the win rate percentage
            position = 'SHORT'
            confidence = min((short_rate - long_rate) / 50, 1.0)
        
        return {
            'score': round(score, 1),
            'position': position,
            'confidence': round(confidence, 2)
        }
    
    def _determine_best_timeframe(self, score_24h: Dict, score_7d: Dict, score_1m: Dict) -> Dict[str, Any]:
        """Determine the best timeframe and position based on scores"""
        timeframes = [
            {'timeframe': '24h', **score_24h},
            {'timeframe': '7d', **score_7d},
            {'timeframe': '1m', **score_1m}
        ]
        
        # Sort by score (highest win rate)
        best = max(timeframes, key=lambda x: x['score'])
        
        return {
            'timeframe': best['timeframe'],
            'position': best['position'],
            'score': best['score'],
            'confidence': best['confidence']
        }
    
    def _calculate_overall_confidence(self, analyses: List[Dict]) -> float:
        """Calculate overall confidence based on all analyses"""
        if not analyses:
            return 0.3
        
        # Average confidence from all sub-agents
        confidences = [a.get('confidence', 0.5) for a in analyses]
        avg_confidence = np.mean(confidences)
        
        # Boost confidence if we have more analyses
        analysis_boost = min(len(analyses) / 10, 0.2)
        
        # Check for consistency
        long_percentages = [a.get('liquidation_ratio', {}).get('long', 50) for a in analyses]
        consistency = 1.0 - (np.std(long_percentages) / 50)  # Lower std = higher consistency
        consistency_boost = consistency * 0.2
        
        overall = avg_confidence + analysis_boost + consistency_boost
        return min(max(overall, 0.3), 1.0)
    
    def _get_sub_agents_summary(self, analyses: List[Dict]) -> List[Dict[str, Any]]:
        """Get summary of sub-agents that contributed to analysis"""
        summary = []
        
        for analysis in analyses:
            summary.append({
                'agent': analysis.get('agent', 'unknown'),
                'image_type': analysis.get('image_type', 'unknown'),
                'confidence': analysis.get('confidence', 0),
                'timestamp': analysis.get('timestamp', '')
            })
        
        return summary
    
    async def _update_airtable(self, analysis: Dict[str, Any]):
        """Update Airtable with comprehensive analysis"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis['symbol'],
                    'Agent': self.agent_name,
                    'AnalysisType': 'comprehensive',
                    'Score24h': analysis['24h']['score'],
                    'Position24h': analysis['24h']['position'],
                    'Score7d': analysis['7d']['score'],
                    'Position7d': analysis['7d']['position'],
                    'Score1m': analysis['1m']['score'],
                    'Position1m': analysis['1m']['position'],
                    'BestTimeframe': analysis['recommendation']['best_timeframe'],
                    'BestPosition': analysis['recommendation']['best_position'],
                    'BestScore': analysis['recommendation']['best_score'],
                    'OverallConfidence': analysis['recommendation']['overall_confidence'],
                    'AnalysesCount': analysis['analyses_count'],
                    'Timestamp': analysis['timestamp']
                }
                await self.airtable_service.create_record('KingFisherAnalysis', record)
                logger.info(f"Airtable updated with comprehensive analysis for {analysis['symbol']}")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")
    
    async def get_current_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get current analysis status for a symbol"""
        analyses_count = len(self.analysis_buffer.get(symbol, []))
        
        if analyses_count == 0:
            return {
                'status': 'no_data',
                'symbol': symbol,
                'message': 'No analyses received yet',
                'timestamp': datetime.now().isoformat()
            }
        elif analyses_count < self.minimum_images_required:
            return {
                'status': 'partial',
                'symbol': symbol,
                'analyses_received': analyses_count,
                'analyses_required': self.minimum_images_required,
                'message': f"Need {self.minimum_images_required - analyses_count} more image analyses",
                'partial_data': self._get_partial_analysis(symbol),
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Perform and return full analysis
            return await self.perform_full_analysis(symbol)
    
    def _get_partial_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get partial analysis from available data"""
        analyses = self.analysis_buffer.get(symbol, [])
        if not analyses:
            return {}
        
        # Calculate preliminary win rates
        long_sum = sum(a.get('liquidation_ratio', {}).get('long', 50) for a in analyses)
        short_sum = sum(a.get('liquidation_ratio', {}).get('short', 50) for a in analyses)
        count = len(analyses)
        
        return {
            'preliminary_long_rate': long_sum / count,
            'preliminary_short_rate': short_sum / count,
            'agents_reported': [a.get('agent') for a in analyses]
        }
    
    async def _process_support_resistance_levels(self, symbol: str, analyses: List[Dict]):
        """Extract and store support/resistance levels from all analyses"""
        try:
            all_levels = {
                '24h': {'support': [], 'resistance': []},
                '7d': {'support': [], 'resistance': []},
                '1m': {'support': [], 'resistance': []}
            }
            
            # Collect all support/resistance levels from analyses
            for analysis in analyses:
                sr_data = analysis.get('support_resistance_levels', {})
                
                for timeframe in ['24h', '7d', '1m']:
                    tf_data = sr_data.get(timeframe, {})
                    
                    # Add support levels
                    for support in tf_data.get('support_levels', []):
                        all_levels[timeframe]['support'].append({
                            'price': support['price'],
                            'strength': support['strength'],
                            'volume': support.get('volume', 0),
                            'type': 'support',
                            'image_type': analysis.get('image_type'),
                            'confidence': analysis.get('confidence', 0.5)
                        })
                    
                    # Add resistance levels
                    for resistance in tf_data.get('resistance_levels', []):
                        all_levels[timeframe]['resistance'].append({
                            'price': resistance['price'],
                            'strength': resistance['strength'],
                            'volume': resistance.get('volume', 0),
                            'type': 'resistance',
                            'image_type': analysis.get('image_type'),
                            'confidence': analysis.get('confidence', 0.5)
                        })
            
            # Store levels in database for each timeframe
            for timeframe, levels_data in all_levels.items():
                # Store support levels
                if levels_data['support']:
                    await self.sr_service.store_support_resistance_levels(
                        symbol=symbol,
                        timeframe=timeframe,
                        levels=levels_data['support'],
                        source_agent=self.agent_name
                    )
                
                # Store resistance levels
                if levels_data['resistance']:
                    await self.sr_service.store_support_resistance_levels(
                        symbol=symbol,
                        timeframe=timeframe,
                        levels=levels_data['resistance'],
                        source_agent=self.agent_name
                    )
            
            logger.info(f"Stored support/resistance levels for {symbol}")
            
        except Exception as e:
            logger.error(f"Error processing support/resistance levels: {e}")
    
    async def get_trading_targets(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """Get trading targets for all timeframes based on stored levels"""
        try:
            targets = {}
            
            for timeframe in ['24h', '7d', '1m']:
                targets[timeframe] = await self.sr_service.get_trading_targets(
                    symbol=symbol,
                    timeframe=timeframe,
                    current_price=current_price
                )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'targets': targets,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting trading targets: {e}")
            return {'error': str(e)}
    
    def clear_buffer(self, symbol: str = None):
        """Clear analysis buffer for a symbol or all symbols"""
        if symbol:
            self.analysis_buffer[symbol] = []
            logger.info(f"Cleared buffer for {symbol}")
        else:
            self.analysis_buffer.clear()
            logger.info("Cleared all buffers")