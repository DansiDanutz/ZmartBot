#!/usr/bin/env python3
"""
Liquidation Ratio Long-Term Sub-Agent
Analyzes long-term liquidation ratio patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class LiqRatioLongTermAgent:
    """Sub-agent for analyzing long-term liquidation ratio images"""
    
    def __init__(self, airtable_service=None):
        self.agent_name = "liq_ratio_longterm_agent"
        self.airtable_service = airtable_service
        self.analysis_version = "1.0.0"
        logger.info("Liquidation Ratio Long-Term Agent initialized")
    
    async def analyze(self, image_data: bytes, symbol: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze long-term liquidation ratio image
        
        Returns:
            - trend_direction: Overall trend (bullish/bearish)
            - long_dominance_periods: Periods where longs dominate
            - short_dominance_periods: Periods where shorts dominate
            - trend_strength: Strength of the current trend
        """
        try:
            logger.info(f"Analyzing long-term liquidation ratio for {symbol}")
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Analyze trend patterns
            trend_data = self._analyze_trend_patterns(hsv)
            
            # Calculate dominance periods
            long_dominance = self._calculate_long_dominance(hsv)
            short_dominance = self._calculate_short_dominance(hsv)
            
            # Determine overall trend
            if long_dominance > short_dominance:
                trend_direction = "bullish"
                trend_strength = min((long_dominance - short_dominance) / 50, 1.0)
            elif short_dominance > long_dominance:
                trend_direction = "bearish"
                trend_strength = min((short_dominance - long_dominance) / 50, 1.0)
            else:
                trend_direction = "neutral"
                trend_strength = 0.0
            
            # Calculate long/short percentages for long-term
            long_percentage = long_dominance
            short_percentage = short_dominance
            
            # Normalize to 100%
            total = long_percentage + short_percentage
            if total > 0:
                long_percentage = (long_percentage / total) * 100
                short_percentage = (short_percentage / total) * 100
            else:
                long_percentage = 50.0
                short_percentage = 50.0
            
            # Calculate confidence
            confidence = self._calculate_confidence(trend_data, trend_strength)
            
            analysis_result = {
                'agent': self.agent_name,
                'symbol': symbol,
                'image_type': 'liq_ratio_longterm',
                'timeframe': 'long_term',
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'long_dominance_percentage': long_percentage,
                'short_dominance_percentage': short_percentage,
                'liquidation_ratio': {
                    'long': long_percentage,
                    'short': short_percentage
                },
                'trend_patterns': trend_data,
                'market_bias': 'long' if long_percentage > 60 else 'short' if short_percentage > 60 else 'balanced',
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Update Airtable
            if self.airtable_service:
                await self._update_airtable(analysis_result)
            
            logger.info(f"Long-term ratio analysis: {trend_direction} trend, Long {long_percentage:.1f}% vs Short {short_percentage:.1f}%")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing long-term ratio for {symbol}: {e}")
            return {
                'agent': self.agent_name,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_trend_patterns(self, hsv: np.ndarray) -> Dict[str, Any]:
        """Analyze trend patterns in the image"""
        height, width = hsv.shape[:2]
        
        # Divide image into time segments (left to right = past to present)
        segments = 10
        segment_width = width // segments
        
        patterns = []
        for i in range(segments):
            start_x = i * segment_width
            end_x = min((i + 1) * segment_width, width)
            segment = hsv[:, start_x:end_x]
            
            # Analyze segment
            long_intensity = self._calculate_long_intensity_in_segment(segment)
            short_intensity = self._calculate_short_intensity_in_segment(segment)
            
            patterns.append({
                'segment': i,
                'time_position': i / segments,  # 0 = oldest, 1 = newest
                'long_intensity': long_intensity,
                'short_intensity': short_intensity,
                'dominant': 'long' if long_intensity > short_intensity else 'short'
            })
        
        # Analyze pattern trends
        recent_patterns = patterns[-3:]  # Last 30% of time
        historical_patterns = patterns[:7]  # First 70% of time
        
        recent_long_avg = np.mean([p['long_intensity'] for p in recent_patterns])
        historical_long_avg = np.mean([p['long_intensity'] for p in historical_patterns])
        
        trend_analysis = {
            'patterns': patterns,
            'recent_long_dominance': recent_long_avg,
            'historical_long_dominance': historical_long_avg,
            'trend_changing': abs(recent_long_avg - historical_long_avg) > 0.2,
            'momentum': 'increasing' if recent_long_avg > historical_long_avg else 'decreasing'
        }
        
        return trend_analysis
    
    def _calculate_long_dominance(self, hsv: np.ndarray) -> float:
        """Calculate long dominance in the image"""
        # Red color range for long positions
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # Calculate percentage
        total_pixels = hsv.shape[0] * hsv.shape[1]
        red_pixels = np.count_nonzero(red_mask)
        
        return (red_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    def _calculate_short_dominance(self, hsv: np.ndarray) -> float:
        """Calculate short dominance in the image"""
        # Green color range for short positions
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        # Create mask
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Calculate percentage
        total_pixels = hsv.shape[0] * hsv.shape[1]
        green_pixels = np.count_nonzero(green_mask)
        
        return (green_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    def _calculate_long_intensity_in_segment(self, segment: np.ndarray) -> float:
        """Calculate long intensity in a segment"""
        # Red color detection
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        red_mask1 = cv2.inRange(segment, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(segment, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        total_pixels = segment.shape[0] * segment.shape[1]
        red_pixels = np.count_nonzero(red_mask)
        
        return red_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_short_intensity_in_segment(self, segment: np.ndarray) -> float:
        """Calculate short intensity in a segment"""
        # Green color detection
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        green_mask = cv2.inRange(segment, lower_green, upper_green)
        
        total_pixels = segment.shape[0] * segment.shape[1]
        green_pixels = np.count_nonzero(green_mask)
        
        return green_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_confidence(self, trend_data: Dict[str, Any], trend_strength: float) -> float:
        """Calculate confidence score"""
        # Base confidence
        confidence = 0.5
        
        # Add confidence for clear trend
        confidence += trend_strength * 0.2
        
        # Add confidence for consistent patterns
        patterns = trend_data.get('patterns', [])
        if patterns:
            dominant_counts = {'long': 0, 'short': 0}
            for p in patterns:
                dominant_counts[p['dominant']] += 1
            
            # More consistent = higher confidence
            max_count = max(dominant_counts.values())
            consistency = max_count / len(patterns) if patterns else 0
            confidence += consistency * 0.2
        
        # Add confidence if trend is changing (important signal)
        if trend_data.get('trend_changing', False):
            confidence += 0.1
        
        return min(max(confidence, 0.3), 1.0)
    
    async def _update_airtable(self, analysis_result: Dict[str, Any]):
        """Update Airtable with analysis results"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis_result['symbol'],
                    'Agent': self.agent_name,
                    'ImageType': 'liq_ratio_longterm',
                    'Timeframe': 'long_term',
                    'TrendDirection': analysis_result['trend_direction'],
                    'TrendStrength': analysis_result['trend_strength'],
                    'LongPercentage': analysis_result['long_dominance_percentage'],
                    'ShortPercentage': analysis_result['short_dominance_percentage'],
                    'MarketBias': analysis_result['market_bias'],
                    'Confidence': analysis_result['confidence'],
                    'Timestamp': analysis_result['timestamp']
                }
                await self.airtable_service.create_record('LiquidationAnalysis', record)
                logger.info(f"Airtable updated for {analysis_result['symbol']} long-term ratio")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")