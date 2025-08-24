#!/usr/bin/env python3
"""
RSI Heatmap Sub-Agent
Analyzes RSI heatmap images showing overbought/oversold conditions
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class RSIHeatmapAgent:
    """Sub-agent for analyzing RSI heatmap images"""
    
    def __init__(self, airtable_service=None):
        self.agent_name = "rsi_heatmap_agent"
        self.airtable_service = airtable_service
        self.analysis_version = "1.0.0"
        logger.info("RSI Heatmap Agent initialized")
    
    async def analyze(self, image_data: bytes, symbol: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze RSI heatmap image
        
        Returns:
            - rsi_zones: Overbought/oversold zones
            - divergence_signals: RSI divergence patterns
            - momentum_strength: Current momentum based on RSI
            - reversal_probability: Probability of trend reversal
        """
        try:
            logger.info(f"Analyzing RSI heatmap for {symbol}")
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Identify RSI zones
            rsi_zones = self._identify_rsi_zones(hsv)
            
            # Detect divergence patterns
            divergence_signals = self._detect_divergences(hsv, rsi_zones)
            
            # Calculate momentum strength
            momentum = self._calculate_momentum_strength(rsi_zones)
            
            # Assess market condition based on RSI
            market_condition = self._assess_market_condition(rsi_zones)
            
            # Calculate reversal probability
            reversal_prob = self._calculate_reversal_probability(rsi_zones, divergence_signals)
            
            # Determine bias based on RSI levels
            long_bias, short_bias = self._calculate_position_bias(rsi_zones, market_condition)
            
            # Normalize to percentages
            total_bias = long_bias + short_bias
            if total_bias > 0:
                long_percentage = (long_bias / total_bias) * 100
                short_percentage = (short_bias / total_bias) * 100
            else:
                long_percentage = 50.0
                short_percentage = 50.0
            
            # Generate trading signal
            trading_signal = self._generate_trading_signal(
                market_condition, momentum, reversal_prob, divergence_signals
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(rsi_zones, divergence_signals)
            
            analysis_result = {
                'agent': self.agent_name,
                'symbol': symbol,
                'image_type': 'rsi_heatmap',
                'rsi_zones': rsi_zones,
                'market_condition': market_condition,
                'divergence_signals': divergence_signals,
                'momentum_strength': momentum,
                'reversal_probability': reversal_prob,
                'long_bias_percentage': long_percentage,
                'short_bias_percentage': short_percentage,
                'liquidation_ratio': {
                    'long': long_percentage,
                    'short': short_percentage
                },
                'trading_signal': trading_signal,
                'rsi_analysis': {
                    'overbought_zones': len([z for z in rsi_zones if z['condition'] == 'overbought']),
                    'oversold_zones': len([z for z in rsi_zones if z['condition'] == 'oversold']),
                    'neutral_zones': len([z for z in rsi_zones if z['condition'] == 'neutral']),
                    'current_trend': momentum['trend']
                },
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Update Airtable
            if self.airtable_service:
                await self._update_airtable(analysis_result)
            
            logger.info(f"RSI analysis: {market_condition['state']}, Long {long_percentage:.1f}% vs Short {short_percentage:.1f}%")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing RSI heatmap for {symbol}: {e}")
            return {
                'agent': self.agent_name,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _identify_rsi_zones(self, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Identify RSI zones (overbought, oversold, neutral)"""
        zones = []
        height, width = hsv.shape[:2]
        
        # Define color ranges for RSI levels
        # Purple/Pink (overbought, RSI > 70)
        overbought_lower = np.array([140, 50, 50])
        overbought_upper = np.array([170, 255, 255])
        
        # Blue/Cyan (oversold, RSI < 30)
        oversold_lower = np.array([90, 50, 50])
        oversold_upper = np.array([120, 255, 255])
        
        # Green/Yellow (neutral, RSI 30-70)
        neutral_lower = np.array([30, 50, 50])
        neutral_upper = np.array([90, 255, 255])
        
        # Create masks
        overbought_mask = cv2.inRange(hsv, overbought_lower, overbought_upper)
        oversold_mask = cv2.inRange(hsv, oversold_lower, oversold_upper)
        neutral_mask = cv2.inRange(hsv, neutral_lower, neutral_upper)
        
        # Process overbought zones
        ob_contours, _ = cv2.findContours(overbought_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in ob_contours:
            area = cv2.contourArea(contour)
            if area > 50:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'condition': 'overbought',
                    'rsi_level': 80 + (y / height) * 20,  # Estimate RSI 80-100
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'time_position': x / width,  # 0 = oldest, 1 = newest
                    'strength': min(area / 500, 1.0)
                })
        
        # Process oversold zones
        os_contours, _ = cv2.findContours(oversold_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in os_contours:
            area = cv2.contourArea(contour)
            if area > 50:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'condition': 'oversold',
                    'rsi_level': 20 - (y / height) * 20,  # Estimate RSI 0-20
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'time_position': x / width,
                    'strength': min(area / 500, 1.0)
                })
        
        # Process neutral zones
        n_contours, _ = cv2.findContours(neutral_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in n_contours:
            area = cv2.contourArea(contour)
            if area > 50:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'condition': 'neutral',
                    'rsi_level': 50,  # Estimate RSI around 50
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'time_position': x / width,
                    'strength': min(area / 500, 1.0)
                })
        
        return sorted(zones, key=lambda z: z['time_position'])
    
    def _detect_divergences(self, hsv: np.ndarray, rsi_zones: List[Dict]) -> List[Dict[str, Any]]:
        """Detect RSI divergence patterns"""
        divergences = []
        
        if len(rsi_zones) < 3:
            return divergences
        
        # Look for bullish divergence (price lower low, RSI higher low)
        oversold_zones = [z for z in rsi_zones if z['condition'] == 'oversold']
        if len(oversold_zones) >= 2:
            for i in range(len(oversold_zones) - 1):
                current = oversold_zones[i]
                next_zone = oversold_zones[i + 1]
                
                if current['rsi_level'] < next_zone['rsi_level']:
                    divergences.append({
                        'type': 'bullish',
                        'strength': abs(next_zone['rsi_level'] - current['rsi_level']) / 20,
                        'time_position': next_zone['time_position'],
                        'confidence': min(current['strength'] + next_zone['strength'], 1.0)
                    })
        
        # Look for bearish divergence (price higher high, RSI lower high)
        overbought_zones = [z for z in rsi_zones if z['condition'] == 'overbought']
        if len(overbought_zones) >= 2:
            for i in range(len(overbought_zones) - 1):
                current = overbought_zones[i]
                next_zone = overbought_zones[i + 1]
                
                if current['rsi_level'] > next_zone['rsi_level']:
                    divergences.append({
                        'type': 'bearish',
                        'strength': abs(current['rsi_level'] - next_zone['rsi_level']) / 20,
                        'time_position': next_zone['time_position'],
                        'confidence': min(current['strength'] + next_zone['strength'], 1.0)
                    })
        
        return divergences
    
    def _calculate_momentum_strength(self, rsi_zones: List[Dict]) -> Dict[str, Any]:
        """Calculate momentum strength from RSI zones"""
        if not rsi_zones:
            return {'strength': 0.5, 'trend': 'neutral', 'direction': 0}
        
        # Get recent zones (last 30%)
        recent_zones = [z for z in rsi_zones if z['time_position'] > 0.7]
        
        if not recent_zones:
            recent_zones = rsi_zones[-3:] if len(rsi_zones) >= 3 else rsi_zones
        
        # Calculate average RSI level
        avg_rsi = np.mean([z['rsi_level'] for z in recent_zones])
        
        # Determine trend
        if avg_rsi > 70:
            trend = 'strong_bullish'
            strength = min((avg_rsi - 70) / 30 + 0.5, 1.0)
            direction = 1
        elif avg_rsi > 50:
            trend = 'bullish'
            strength = (avg_rsi - 50) / 20 * 0.5 + 0.25
            direction = 1
        elif avg_rsi < 30:
            trend = 'strong_bearish'
            strength = min((30 - avg_rsi) / 30 + 0.5, 1.0)
            direction = -1
        elif avg_rsi < 50:
            trend = 'bearish'
            strength = (50 - avg_rsi) / 20 * 0.5 + 0.25
            direction = -1
        else:
            trend = 'neutral'
            strength = 0.5
            direction = 0
        
        return {
            'strength': strength,
            'trend': trend,
            'direction': direction,
            'avg_rsi': avg_rsi
        }
    
    def _assess_market_condition(self, rsi_zones: List[Dict]) -> Dict[str, Any]:
        """Assess overall market condition from RSI"""
        overbought_count = len([z for z in rsi_zones if z['condition'] == 'overbought'])
        oversold_count = len([z for z in rsi_zones if z['condition'] == 'oversold'])
        neutral_count = len([z for z in rsi_zones if z['condition'] == 'neutral'])
        
        total_zones = len(rsi_zones)
        
        if total_zones == 0:
            return {'state': 'undefined', 'strength': 0, 'description': 'No RSI data available'}
        
        # Calculate percentages
        overbought_pct = overbought_count / total_zones
        oversold_pct = oversold_count / total_zones
        
        # Determine market state
        if overbought_pct > 0.5:
            state = 'overbought'
            description = 'Market is overbought, potential reversal down'
            strength = overbought_pct
        elif oversold_pct > 0.5:
            state = 'oversold'
            description = 'Market is oversold, potential reversal up'
            strength = oversold_pct
        elif overbought_pct > 0.3:
            state = 'bullish'
            description = 'Bullish momentum, approaching overbought'
            strength = overbought_pct
        elif oversold_pct > 0.3:
            state = 'bearish'
            description = 'Bearish momentum, approaching oversold'
            strength = oversold_pct
        else:
            state = 'neutral'
            description = 'Market in equilibrium'
            strength = 0.5
        
        return {
            'state': state,
            'strength': strength,
            'description': description,
            'overbought_percentage': overbought_pct,
            'oversold_percentage': oversold_pct
        }
    
    def _calculate_reversal_probability(self, rsi_zones: List[Dict], divergences: List[Dict]) -> float:
        """Calculate probability of trend reversal"""
        probability = 0.0
        
        # Recent extreme RSI increases reversal probability
        recent_zones = [z for z in rsi_zones if z['time_position'] > 0.8]
        for zone in recent_zones:
            if zone['condition'] == 'overbought' and zone['rsi_level'] > 80:
                probability += 0.2
            elif zone['condition'] == 'oversold' and zone['rsi_level'] < 20:
                probability += 0.2
        
        # Divergences strongly indicate reversal
        for div in divergences:
            if div['time_position'] > 0.7:  # Recent divergence
                probability += div['strength'] * 0.3
        
        # Extended time in extreme zones
        consecutive_extreme = 0
        for zone in reversed(rsi_zones):
            if zone['condition'] in ['overbought', 'oversold']:
                consecutive_extreme += 1
            else:
                break
        
        if consecutive_extreme > 3:
            probability += 0.2
        
        return min(probability, 1.0)
    
    def _calculate_position_bias(self, rsi_zones: List[Dict], market_condition: Dict) -> tuple:
        """Calculate position bias based on RSI"""
        long_bias = 0.5
        short_bias = 0.5
        
        state = market_condition['state']
        strength = market_condition['strength']
        
        if state == 'oversold':
            long_bias = 0.7 + strength * 0.2  # Favor longs in oversold
            short_bias = 0.3 - strength * 0.1
        elif state == 'overbought':
            short_bias = 0.7 + strength * 0.2  # Favor shorts in overbought
            long_bias = 0.3 - strength * 0.1
        elif state == 'bullish':
            long_bias = 0.6 + strength * 0.1
            short_bias = 0.4 - strength * 0.05
        elif state == 'bearish':
            short_bias = 0.6 + strength * 0.1
            long_bias = 0.4 - strength * 0.05
        
        return max(long_bias, 0.1), max(short_bias, 0.1)
    
    def _generate_trading_signal(self, market_condition: Dict, momentum: Dict, 
                                reversal_prob: float, divergences: List[Dict]) -> Dict[str, Any]:
        """Generate trading signal based on RSI analysis"""
        signal = {
            'action': 'wait',
            'confidence': 0.5,
            'reasoning': []
        }
        
        state = market_condition['state']
        
        # Strong oversold with bullish divergence = long
        if state == 'oversold' and any(d['type'] == 'bullish' for d in divergences):
            signal['action'] = 'long'
            signal['confidence'] = min(0.8 + reversal_prob * 0.2, 1.0)
            signal['reasoning'].append('Oversold with bullish divergence')
        
        # Strong overbought with bearish divergence = short
        elif state == 'overbought' and any(d['type'] == 'bearish' for d in divergences):
            signal['action'] = 'short'
            signal['confidence'] = min(0.8 + reversal_prob * 0.2, 1.0)
            signal['reasoning'].append('Overbought with bearish divergence')
        
        # Oversold bounce opportunity
        elif state == 'oversold' and reversal_prob > 0.5:
            signal['action'] = 'long'
            signal['confidence'] = reversal_prob
            signal['reasoning'].append('Oversold bounce opportunity')
        
        # Overbought reversal opportunity
        elif state == 'overbought' and reversal_prob > 0.5:
            signal['action'] = 'short'
            signal['confidence'] = reversal_prob
            signal['reasoning'].append('Overbought reversal opportunity')
        
        # Follow momentum in trending market
        elif momentum['trend'] in ['strong_bullish', 'bullish'] and state not in ['overbought']:
            signal['action'] = 'long'
            signal['confidence'] = momentum['strength']
            signal['reasoning'].append(f"Following {momentum['trend']} momentum")
        elif momentum['trend'] in ['strong_bearish', 'bearish'] and state not in ['oversold']:
            signal['action'] = 'short'
            signal['confidence'] = momentum['strength']
            signal['reasoning'].append(f"Following {momentum['trend']} momentum")
        
        return signal
    
    def _calculate_confidence(self, rsi_zones: List[Dict], divergences: List[Dict]) -> float:
        """Calculate confidence score"""
        confidence = 0.5
        
        # More zones = better analysis
        if len(rsi_zones) > 10:
            confidence += 0.15
        elif len(rsi_zones) > 5:
            confidence += 0.1
        
        # Clear divergences = high confidence signal
        if divergences:
            confidence += 0.2
        
        # Recent zones = more relevant
        recent_zones = [z for z in rsi_zones if z['time_position'] > 0.7]
        if len(recent_zones) > 3:
            confidence += 0.15
        
        return min(max(confidence, 0.3), 1.0)
    
    async def _update_airtable(self, analysis_result: Dict[str, Any]):
        """Update Airtable with analysis results"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis_result['symbol'],
                    'Agent': self.agent_name,
                    'ImageType': 'rsi_heatmap',
                    'MarketCondition': analysis_result['market_condition']['state'],
                    'LongBias': analysis_result['long_bias_percentage'],
                    'ShortBias': analysis_result['short_bias_percentage'],
                    'MomentumTrend': analysis_result['momentum_strength']['trend'],
                    'ReversalProbability': analysis_result['reversal_probability'],
                    'TradingSignal': analysis_result['trading_signal']['action'],
                    'SignalConfidence': analysis_result['trading_signal']['confidence'],
                    'DivergenceCount': len(analysis_result['divergence_signals']),
                    'Confidence': analysis_result['confidence'],
                    'Timestamp': analysis_result['timestamp']
                }
                await self.airtable_service.create_record('LiquidationAnalysis', record)
                logger.info(f"Airtable updated for {analysis_result['symbol']} RSI heatmap")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")