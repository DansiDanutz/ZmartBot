#!/usr/bin/env python3
"""
KingFisher Advanced Features
Enhanced capabilities for production-grade liquidation analysis
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import deque
import json

logger = logging.getLogger(__name__)

class KingFisherAdvancedFeatures:
    """
    Advanced features for KingFisher liquidation analysis:
    1. Multi-timeframe correlation analysis
    2. Liquidation cascade prediction
    3. Smart position sizing based on liquidation clusters
    4. Historical pattern matching
    5. Risk-adjusted entry/exit points
    """
    
    def __init__(self):
        # Historical data storage
        self.liquidation_history = {}  # symbol -> deque of historical data
        self.pattern_library = {}  # Known profitable patterns
        self.cascade_thresholds = {
            'BTC': {'critical': 5000000, 'warning': 2000000},
            'ETH': {'critical': 3000000, 'warning': 1000000},
            'default': {'critical': 1000000, 'warning': 500000}
        }
        
        # Machine learning components
        self.ml_patterns = []
        self.confidence_weights = {
            'liquidation_cluster': 0.35,
            'volume_profile': 0.25,
            'historical_pattern': 0.20,
            'cascade_risk': 0.20
        }
        
        logger.info("KingFisher Advanced Features initialized")
    
    async def analyze_liquidation_cascade_risk(self, symbol: str, 
                                              current_price: float,
                                              liquidation_data: Dict) -> Dict[str, Any]:
        """
        Predict potential liquidation cascades
        
        Returns risk assessment and safe zones
        """
        try:
            # Get liquidation clusters
            clusters = liquidation_data.get('liquidation_clusters', [])
            if not clusters:
                return {
                    'cascade_risk': 'low',
                    'risk_score': 0,
                    'safe_zones': [],
                    'danger_zones': []
                }
            
            # Analyze cluster concentration
            total_liquidations = sum(c.get('size', 0) for c in clusters)
            thresholds = self.cascade_thresholds.get(symbol, self.cascade_thresholds['default'])
            
            # Identify danger zones (high liquidation concentration)
            danger_zones = []
            safe_zones = []
            
            for cluster in clusters:
                price_level = cluster.get('price', 0)
                size = cluster.get('size', 0)
                distance_pct = abs(price_level - current_price) / current_price * 100
                
                if size > thresholds['warning']:
                    danger_zones.append({
                        'price': price_level,
                        'size': size,
                        'distance_pct': distance_pct,
                        'risk_level': 'critical' if size > thresholds['critical'] else 'warning'
                    })
                elif distance_pct > 5:  # More than 5% away
                    safe_zones.append({
                        'price': price_level,
                        'distance_pct': distance_pct
                    })
            
            # Calculate cascade risk score
            risk_score = 0
            if danger_zones:
                # Weight by proximity and size
                for zone in danger_zones:
                    proximity_weight = max(0, 100 - zone['distance_pct']) / 100
                    size_weight = min(zone['size'] / thresholds['critical'], 1)
                    risk_score += proximity_weight * size_weight * 50
            
            risk_score = min(risk_score, 100)
            
            # Determine risk level
            if risk_score > 70:
                risk_level = 'critical'
            elif risk_score > 40:
                risk_level = 'high'
            elif risk_score > 20:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'cascade_risk': risk_level,
                'risk_score': risk_score,
                'safe_zones': sorted(safe_zones, key=lambda x: x['distance_pct']),
                'danger_zones': sorted(danger_zones, key=lambda x: x['distance_pct']),
                'total_liquidation_value': total_liquidations,
                'recommendation': self._get_cascade_recommendation(risk_level, danger_zones)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cascade risk: {e}")
            return {'cascade_risk': 'unknown', 'risk_score': 0}
    
    def _get_cascade_recommendation(self, risk_level: str, danger_zones: List) -> str:
        """Generate trading recommendation based on cascade risk"""
        if risk_level == 'critical':
            return "AVOID ENTRY - High cascade risk detected. Wait for liquidation event to complete."
        elif risk_level == 'high':
            if danger_zones and danger_zones[0]['distance_pct'] < 2:
                return "USE TIGHT STOPS - Liquidation cascade imminent within 2% range"
            return "REDUCE POSITION SIZE - Significant liquidation clusters nearby"
        elif risk_level == 'medium':
            return "PROCEED WITH CAUTION - Monitor liquidation levels closely"
        else:
            return "SAFE TO TRADE - Low liquidation cascade risk"
    
    async def calculate_smart_position_size(self, symbol: str,
                                           account_balance: float,
                                           liquidation_analysis: Dict,
                                           risk_tolerance: str = 'medium') -> Dict[str, Any]:
        """
        Calculate optimal position size based on liquidation clusters
        
        Risk tolerance: 'conservative', 'medium', 'aggressive'
        """
        try:
            # Base risk percentages
            risk_percentages = {
                'conservative': 0.01,  # 1% risk
                'medium': 0.02,        # 2% risk
                'aggressive': 0.03     # 3% risk
            }
            
            base_risk = risk_percentages.get(risk_tolerance, 0.02)
            risk_amount = account_balance * base_risk
            
            # Get cascade risk
            cascade_analysis = await self.analyze_liquidation_cascade_risk(
                symbol, 
                liquidation_analysis.get('current_price', 0),
                liquidation_analysis
            )
            
            # Adjust position size based on cascade risk
            cascade_multipliers = {
                'critical': 0.25,  # Reduce to 25% of normal size
                'high': 0.5,       # Reduce to 50%
                'medium': 0.75,    # Reduce to 75%
                'low': 1.0         # Full size
            }
            
            cascade_mult = cascade_multipliers.get(cascade_analysis['cascade_risk'], 0.5)
            
            # Find nearest liquidation cluster for stop loss
            danger_zones = cascade_analysis.get('danger_zones', [])
            if danger_zones:
                # Use the nearest danger zone as stop loss reference
                nearest_danger = danger_zones[0]
                stop_distance = nearest_danger['distance_pct']
                
                # Ensure minimum stop distance
                stop_distance = max(stop_distance, 1.5)  # At least 1.5%
            else:
                stop_distance = 3.0  # Default 3% stop
            
            # Calculate position size
            position_value = (risk_amount / (stop_distance / 100)) * cascade_mult
            
            # Apply maximum position limits
            max_position = account_balance * 0.1  # Max 10% of account
            position_value = min(position_value, max_position)
            
            return {
                'recommended_position_size': position_value,
                'position_size_btc': position_value / liquidation_analysis.get('current_price', 50000),
                'risk_amount': risk_amount,
                'stop_loss_distance': stop_distance,
                'cascade_adjustment': cascade_mult,
                'max_loss': position_value * (stop_distance / 100),
                'risk_reward_ratio': 3 / (stop_distance / 100),  # Assuming 3x target
                'notes': f"Position sized for {risk_tolerance} risk with {cascade_analysis['cascade_risk']} cascade risk"
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {
                'recommended_position_size': account_balance * 0.01,
                'error': str(e)
            }
    
    async def find_optimal_entry_zones(self, symbol: str,
                                      liquidation_data: Dict) -> Dict[str, Any]:
        """
        Identify optimal entry zones based on liquidation voids
        
        Liquidation voids are price areas with minimal liquidations
        """
        try:
            current_price = liquidation_data.get('current_price', 0)
            clusters = liquidation_data.get('liquidation_clusters', [])
            
            if not clusters or not current_price:
                return {'entry_zones': [], 'confidence': 0}
            
            # Sort clusters by price
            sorted_clusters = sorted(clusters, key=lambda x: x.get('price', 0))
            
            # Find gaps between clusters (liquidation voids)
            entry_zones = []
            
            for i in range(len(sorted_clusters) - 1):
                current_cluster = sorted_clusters[i]
                next_cluster = sorted_clusters[i + 1]
                
                gap_start = current_cluster.get('price', 0)
                gap_end = next_cluster.get('price', 0)
                gap_size = gap_end - gap_start
                
                # Check if gap is significant (at least 0.5% of price)
                if gap_size > current_price * 0.005:
                    midpoint = (gap_start + gap_end) / 2
                    
                    # Calculate zone strength
                    distance_from_current = abs(midpoint - current_price) / current_price
                    
                    # Prefer zones within 3% of current price
                    if distance_from_current <= 0.03:
                        strength = 100 - (distance_from_current * 1000)  # Scale to 0-100
                        
                        entry_zones.append({
                            'price': midpoint,
                            'range': [gap_start, gap_end],
                            'strength': min(strength, 100),
                            'type': 'long' if midpoint < current_price else 'short',
                            'distance_pct': distance_from_current * 100,
                            'protection': f"Protected by liquidations at ${gap_start:,.0f} and ${gap_end:,.0f}"
                        })
            
            # Sort by strength
            entry_zones = sorted(entry_zones, key=lambda x: x['strength'], reverse=True)[:5]
            
            # Calculate overall confidence
            confidence = 0
            if entry_zones:
                confidence = sum(z['strength'] for z in entry_zones[:3]) / 3
            
            return {
                'entry_zones': entry_zones,
                'confidence': confidence,
                'best_entry': entry_zones[0] if entry_zones else None,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error finding entry zones: {e}")
            return {'entry_zones': [], 'confidence': 0, 'error': str(e)}
    
    async def detect_liquidation_patterns(self, symbol: str,
                                         historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Detect recurring liquidation patterns that precede major moves
        """
        try:
            if len(historical_data) < 10:
                return {'patterns': [], 'confidence': 0}
            
            patterns_found = []
            
            # Pattern 1: Liquidation Squeeze (Both sides liquidated heavily)
            squeeze_pattern = self._detect_squeeze_pattern(historical_data)
            if squeeze_pattern['detected']:
                patterns_found.append(squeeze_pattern)
            
            # Pattern 2: One-sided Liquidation (Strong directional bias)
            directional_pattern = self._detect_directional_pattern(historical_data)
            if directional_pattern['detected']:
                patterns_found.append(directional_pattern)
            
            # Pattern 3: Liquidation Divergence (Price vs liquidation divergence)
            divergence_pattern = self._detect_divergence_pattern(historical_data)
            if divergence_pattern['detected']:
                patterns_found.append(divergence_pattern)
            
            # Calculate combined signal
            if patterns_found:
                avg_confidence = sum(p['confidence'] for p in patterns_found) / len(patterns_found)
                
                # Determine overall signal
                bullish_count = sum(1 for p in patterns_found if p['signal'] == 'bullish')
                bearish_count = sum(1 for p in patterns_found if p['signal'] == 'bearish')
                
                if bullish_count > bearish_count:
                    overall_signal = 'bullish'
                elif bearish_count > bullish_count:
                    overall_signal = 'bearish'
                else:
                    overall_signal = 'neutral'
                
                return {
                    'patterns': patterns_found,
                    'confidence': avg_confidence,
                    'overall_signal': overall_signal,
                    'pattern_count': len(patterns_found),
                    'recommendation': self._get_pattern_recommendation(patterns_found)
                }
            
            return {'patterns': [], 'confidence': 0, 'overall_signal': 'neutral'}
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {'patterns': [], 'confidence': 0, 'error': str(e)}
    
    def _detect_squeeze_pattern(self, data: List[Dict]) -> Dict:
        """Detect liquidation squeeze pattern"""
        recent = data[-5:]  # Last 5 periods
        
        total_longs = sum(d.get('long_liquidations', 0) for d in recent)
        total_shorts = sum(d.get('short_liquidations', 0) for d in recent)
        
        if total_longs > 1000000 and total_shorts > 1000000:
            ratio = min(total_longs, total_shorts) / max(total_longs, total_shorts)
            if ratio > 0.7:  # Both sides heavily liquidated
                return {
                    'detected': True,
                    'type': 'squeeze',
                    'signal': 'neutral',  # Squeeze often precedes big move either way
                    'confidence': ratio * 100,
                    'description': 'Heavy liquidations on both sides - expect volatility'
                }
        
        return {'detected': False}
    
    def _detect_directional_pattern(self, data: List[Dict]) -> Dict:
        """Detect one-sided liquidation pattern"""
        recent = data[-5:]
        
        total_longs = sum(d.get('long_liquidations', 0) for d in recent)
        total_shorts = sum(d.get('short_liquidations', 0) for d in recent)
        
        if total_longs > 0 or total_shorts > 0:
            long_ratio = total_longs / (total_longs + total_shorts)
            
            if long_ratio > 0.8:  # Mostly long liquidations
                return {
                    'detected': True,
                    'type': 'directional',
                    'signal': 'bearish',  # Long liquidations = bearish
                    'confidence': long_ratio * 100,
                    'description': 'Heavy long liquidations - bearish signal'
                }
            elif long_ratio < 0.2:  # Mostly short liquidations
                return {
                    'detected': True,
                    'type': 'directional',
                    'signal': 'bullish',  # Short liquidations = bullish
                    'confidence': (1 - long_ratio) * 100,
                    'description': 'Heavy short liquidations - bullish signal'
                }
        
        return {'detected': False}
    
    def _detect_divergence_pattern(self, data: List[Dict]) -> Dict:
        """Detect price vs liquidation divergence"""
        if len(data) < 10:
            return {'detected': False}
        
        # Compare price trend vs liquidation trend
        prices = [d.get('price', 0) for d in data[-10:]]
        long_liqs = [d.get('long_liquidations', 0) for d in data[-10:]]
        
        if prices[0] > 0 and prices[-1] > 0:
            price_change = (prices[-1] - prices[0]) / prices[0]
            liq_change = (long_liqs[-1] - long_liqs[0]) if long_liqs[0] > 0 else 0
            
            # Bullish divergence: price down but long liquidations decreasing
            if price_change < -0.02 and liq_change < 0:
                return {
                    'detected': True,
                    'type': 'divergence',
                    'signal': 'bullish',
                    'confidence': min(abs(price_change) * 1000, 100),
                    'description': 'Bullish divergence - price down but liquidations decreasing'
                }
            # Bearish divergence: price up but long liquidations increasing
            elif price_change > 0.02 and liq_change > 0:
                return {
                    'detected': True,
                    'type': 'divergence', 
                    'signal': 'bearish',
                    'confidence': min(price_change * 1000, 100),
                    'description': 'Bearish divergence - price up but liquidations increasing'
                }
        
        return {'detected': False}
    
    def _get_pattern_recommendation(self, patterns: List[Dict]) -> str:
        """Generate recommendation based on detected patterns"""
        if not patterns:
            return "No significant patterns detected"
        
        high_confidence = [p for p in patterns if p['confidence'] > 70]
        
        if high_confidence:
            signals = [p['signal'] for p in high_confidence]
            if all(s == 'bullish' for s in signals):
                return "STRONG BUY - Multiple bullish patterns with high confidence"
            elif all(s == 'bearish' for s in signals):
                return "STRONG SELL - Multiple bearish patterns with high confidence"
            elif 'squeeze' in [p['type'] for p in high_confidence]:
                return "WAIT FOR BREAKOUT - Squeeze pattern detected, expect volatility"
            else:
                return "MIXED SIGNALS - Conflicting patterns, trade with caution"
        else:
            return "WEAK SIGNALS - Low confidence patterns, wait for confirmation"
    
    async def generate_risk_report(self, symbol: str,
                                  liquidation_data: Dict,
                                  account_balance: float = 10000) -> Dict[str, Any]:
        """
        Generate comprehensive risk assessment report
        """
        try:
            # Gather all analyses
            cascade_risk = await self.analyze_liquidation_cascade_risk(
                symbol, 
                liquidation_data.get('current_price', 0),
                liquidation_data
            )
            
            position_sizing = await self.calculate_smart_position_size(
                symbol, account_balance, liquidation_data, 'medium'
            )
            
            entry_zones = await self.find_optimal_entry_zones(symbol, liquidation_data)
            
            # Generate risk score (0-100)
            risk_components = {
                'cascade': cascade_risk['risk_score'],
                'entry_quality': 100 - entry_zones.get('confidence', 50),
                'position_risk': min(position_sizing.get('max_loss', 0) / account_balance * 1000, 100)
            }
            
            overall_risk = sum(risk_components.values()) / len(risk_components)
            
            # Generate report
            report = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_risk_score': overall_risk,
                'risk_level': 'HIGH' if overall_risk > 70 else 'MEDIUM' if overall_risk > 40 else 'LOW',
                'cascade_analysis': cascade_risk,
                'position_recommendation': position_sizing,
                'entry_zones': entry_zones,
                'risk_components': risk_components,
                'recommendations': self._generate_recommendations(overall_risk, cascade_risk, entry_zones),
                'max_recommended_exposure': account_balance * (0.1 if overall_risk > 70 else 0.2 if overall_risk > 40 else 0.3)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return {
                'error': str(e),
                'overall_risk_score': 100,
                'risk_level': 'UNKNOWN'
            }
    
    def _generate_recommendations(self, risk_score: float, 
                                 cascade_risk: Dict,
                                 entry_zones: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score > 70:
            recommendations.append("⚠️ HIGH RISK: Consider reducing position size or waiting for better conditions")
        elif risk_score > 40:
            recommendations.append("📊 MEDIUM RISK: Trade with strict risk management")
        else:
            recommendations.append("✅ LOW RISK: Favorable conditions for trading")
        
        # Cascade-based recommendations
        if cascade_risk['cascade_risk'] == 'critical':
            recommendations.append("🚨 LIQUIDATION CASCADE IMMINENT: Avoid new positions")
        elif cascade_risk['cascade_risk'] == 'high':
            recommendations.append("⚡ HIGH CASCADE RISK: Use tight stops and reduced size")
        
        # Entry zone recommendations
        if entry_zones.get('best_entry'):
            best = entry_zones['best_entry']
            recommendations.append(f"🎯 BEST ENTRY: ${best['price']:,.2f} ({best['type']} position)")
        
        # Add safe zones if available
        if cascade_risk.get('safe_zones'):
            safe = cascade_risk['safe_zones'][0] if cascade_risk['safe_zones'] else None
            if safe:
                recommendations.append(f"🛡️ SAFE ZONE: ${safe['price']:,.2f} ({safe['distance_pct']:.1f}% away)")
        
        return recommendations

# Create global instance
advanced_kingfisher = KingFisherAdvancedFeatures()