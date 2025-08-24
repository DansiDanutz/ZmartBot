#!/usr/bin/env python3
"""
Liquidation Ratio Short-Term Sub-Agent
Analyzes short-term liquidation ratio patterns (24h, 4h, 1h)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class LiqRatioShortTermAgent:
    """Sub-agent for analyzing short-term liquidation ratio images"""
    
    def __init__(self, airtable_service=None):
        self.agent_name = "liq_ratio_shortterm_agent"
        self.airtable_service = airtable_service
        self.analysis_version = "1.0.0"
        logger.info("Liquidation Ratio Short-Term Agent initialized")
    
    async def analyze(self, image_data: bytes, symbol: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze short-term liquidation ratio image
        
        Returns:
            - immediate_pressure: Current liquidation pressure
            - momentum: Short-term momentum direction
            - volatility: Short-term volatility measure
            - entry_signal: Potential entry signal based on short-term data
        """
        try:
            logger.info(f"Analyzing short-term liquidation ratio for {symbol}")
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Analyze recent patterns (focus on right side of image)
            recent_data = self._analyze_recent_patterns(hsv)
            
            # Calculate immediate pressure
            immediate_pressure = self._calculate_immediate_pressure(hsv)
            
            # Calculate momentum
            momentum = self._calculate_short_term_momentum(hsv)
            
            # Calculate volatility
            volatility = self._calculate_volatility(hsv)
            
            # Determine liquidation ratios
            long_ratio = immediate_pressure['long_pressure']
            short_ratio = immediate_pressure['short_pressure']
            
            # Normalize to 100%
            total = long_ratio + short_ratio
            if total > 0:
                long_percentage = (long_ratio / total) * 100
                short_percentage = (short_ratio / total) * 100
            else:
                long_percentage = 50.0
                short_percentage = 50.0
            
            # Generate entry signal
            entry_signal = self._generate_entry_signal(
                long_percentage, short_percentage, momentum, volatility
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(recent_data, volatility)
            
            analysis_result = {
                'agent': self.agent_name,
                'symbol': symbol,
                'image_type': 'liq_ratio_shortterm',
                'timeframe': 'short_term',
                'immediate_pressure': immediate_pressure,
                'momentum': momentum,
                'volatility': volatility,
                'long_percentage': long_percentage,
                'short_percentage': short_percentage,
                'liquidation_ratio': {
                    'long': long_percentage,
                    'short': short_percentage
                },
                'entry_signal': entry_signal,
                'recent_patterns': recent_data,
                'market_state': self._determine_market_state(volatility, momentum),
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Update Airtable
            if self.airtable_service:
                await self._update_airtable(analysis_result)
            
            logger.info(f"Short-term ratio analysis: {entry_signal['action']}, Long {long_percentage:.1f}% vs Short {short_percentage:.1f}%")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing short-term ratio for {symbol}: {e}")
            return {
                'agent': self.agent_name,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_recent_patterns(self, hsv: np.ndarray) -> Dict[str, Any]:
        """Analyze recent patterns (last 20% of image)"""
        height, width = hsv.shape[:2]
        
        # Focus on recent data (rightmost 20%)
        recent_start = int(width * 0.8)
        recent_section = hsv[:, recent_start:]
        
        # Analyze color distribution
        long_intensity = self._calculate_long_intensity(recent_section)
        short_intensity = self._calculate_short_intensity(recent_section)
        
        # Detect spikes
        spikes = self._detect_liquidation_spikes(recent_section)
        
        return {
            'recent_long_intensity': long_intensity,
            'recent_short_intensity': short_intensity,
            'spike_detected': len(spikes) > 0,
            'spike_count': len(spikes),
            'dominant_recent': 'long' if long_intensity > short_intensity else 'short'
        }
    
    def _calculate_immediate_pressure(self, hsv: np.ndarray) -> Dict[str, float]:
        """Calculate immediate liquidation pressure"""
        height, width = hsv.shape[:2]
        
        # Focus on most recent data (rightmost 10%)
        immediate_start = int(width * 0.9)
        immediate_section = hsv[:, immediate_start:]
        
        long_pressure = self._calculate_long_intensity(immediate_section)
        short_pressure = self._calculate_short_intensity(immediate_section)
        
        return {
            'long_pressure': long_pressure * 100,  # Convert to percentage
            'short_pressure': short_pressure * 100,
            'total_pressure': (long_pressure + short_pressure) * 100,
            'pressure_ratio': long_pressure / max(short_pressure, 0.01)
        }
    
    def _calculate_short_term_momentum(self, hsv: np.ndarray) -> Dict[str, Any]:
        """Calculate short-term momentum"""
        height, width = hsv.shape[:2]
        
        # Divide recent history into segments
        segments = 5
        segment_width = width // segments
        
        long_trend = []
        short_trend = []
        
        for i in range(segments):
            start_x = i * segment_width
            end_x = min((i + 1) * segment_width, width)
            segment = hsv[:, start_x:end_x]
            
            long_trend.append(self._calculate_long_intensity(segment))
            short_trend.append(self._calculate_short_intensity(segment))
        
        # Calculate momentum (slope of trend)
        long_momentum = np.polyfit(range(len(long_trend)), long_trend, 1)[0]
        short_momentum = np.polyfit(range(len(short_trend)), short_trend, 1)[0]
        
        # Determine overall momentum
        if long_momentum > short_momentum and long_momentum > 0:
            direction = "bullish"
            strength = min(abs(long_momentum) * 100, 1.0)
        elif short_momentum > long_momentum and short_momentum > 0:
            direction = "bearish"
            strength = min(abs(short_momentum) * 100, 1.0)
        else:
            direction = "neutral"
            strength = 0.0
        
        return {
            'direction': direction,
            'strength': strength,
            'long_momentum': long_momentum,
            'short_momentum': short_momentum,
            'accelerating': abs(long_momentum - short_momentum) > 0.01
        }
    
    def _calculate_volatility(self, hsv: np.ndarray) -> float:
        """Calculate short-term volatility"""
        height, width = hsv.shape[:2]
        
        # Sample multiple points
        samples = 10
        sample_width = width // samples
        
        intensities = []
        for i in range(samples):
            start_x = i * sample_width
            end_x = min((i + 1) * sample_width, width)
            segment = hsv[:, start_x:end_x]
            
            long_int = self._calculate_long_intensity(segment)
            short_int = self._calculate_short_intensity(segment)
            intensities.append(long_int - short_int)
        
        # Calculate standard deviation as volatility measure
        if len(intensities) > 1:
            volatility = np.std(intensities)
            return min(volatility * 10, 1.0)  # Normalize to 0-1
        return 0.5
    
    def _generate_entry_signal(self, long_pct: float, short_pct: float, 
                              momentum: Dict, volatility: float) -> Dict[str, Any]:
        """Generate entry signal based on short-term analysis"""
        signal = {
            'action': 'wait',
            'confidence': 0.5,
            'reasoning': []
        }
        
        # Strong long signal
        if long_pct > 70 and momentum['direction'] == 'bullish':
            signal['action'] = 'long'
            signal['confidence'] = min(long_pct / 100 + momentum['strength'] * 0.3, 1.0)
            signal['reasoning'].append('Strong long liquidation pressure')
            signal['reasoning'].append('Bullish momentum detected')
        
        # Strong short signal
        elif short_pct > 70 and momentum['direction'] == 'bearish':
            signal['action'] = 'short'
            signal['confidence'] = min(short_pct / 100 + momentum['strength'] * 0.3, 1.0)
            signal['reasoning'].append('Strong short liquidation pressure')
            signal['reasoning'].append('Bearish momentum detected')
        
        # High volatility - wait
        elif volatility > 0.7:
            signal['action'] = 'wait'
            signal['confidence'] = 0.3
            signal['reasoning'].append('High volatility detected')
        
        # Neutral with momentum
        elif momentum['strength'] > 0.5:
            signal['action'] = 'long' if momentum['direction'] == 'bullish' else 'short'
            signal['confidence'] = momentum['strength']
            signal['reasoning'].append(f"Following {momentum['direction']} momentum")
        
        return signal
    
    def _determine_market_state(self, volatility: float, momentum: Dict) -> str:
        """Determine current market state"""
        if volatility > 0.7:
            return "volatile"
        elif momentum['strength'] > 0.6:
            return "trending"
        elif volatility < 0.3:
            return "consolidating"
        else:
            return "normal"
    
    def _detect_liquidation_spikes(self, image_section: np.ndarray) -> list:
        """Detect liquidation spikes in image section"""
        spikes = []
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image_section, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find vertical lines (spikes)
        lines = cv2.HoughLinesP(edges, 1, np.pi/2, threshold=50, minLineLength=30, maxLineGap=5)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Check if line is mostly vertical
                if abs(x2 - x1) < 10:  # Nearly vertical
                    spikes.append({
                        'position': x1,
                        'height': abs(y2 - y1)
                    })
        
        return spikes
    
    def _calculate_long_intensity(self, section: np.ndarray) -> float:
        """Calculate long intensity in a section"""
        # Red color detection
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        red_mask1 = cv2.inRange(section, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(section, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        total_pixels = section.shape[0] * section.shape[1]
        red_pixels = np.count_nonzero(red_mask)
        
        return red_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_short_intensity(self, section: np.ndarray) -> float:
        """Calculate short intensity in a section"""
        # Green color detection
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        green_mask = cv2.inRange(section, lower_green, upper_green)
        
        total_pixels = section.shape[0] * section.shape[1]
        green_pixels = np.count_nonzero(green_mask)
        
        return green_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_confidence(self, recent_data: Dict, volatility: float) -> float:
        """Calculate confidence score"""
        confidence = 0.5
        
        # Clear recent pattern = higher confidence
        if recent_data.get('recent_long_intensity', 0) > 0.6 or recent_data.get('recent_short_intensity', 0) > 0.6:
            confidence += 0.2
        
        # Spikes detected = important signal
        if recent_data.get('spike_detected', False):
            confidence += 0.15
        
        # Lower volatility = higher confidence
        if volatility < 0.3:
            confidence += 0.15
        elif volatility > 0.7:
            confidence -= 0.1
        
        return min(max(confidence, 0.3), 1.0)
    
    async def _update_airtable(self, analysis_result: Dict[str, Any]):
        """Update Airtable with analysis results"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis_result['symbol'],
                    'Agent': self.agent_name,
                    'ImageType': 'liq_ratio_shortterm',
                    'Timeframe': 'short_term',
                    'LongPercentage': analysis_result['long_percentage'],
                    'ShortPercentage': analysis_result['short_percentage'],
                    'Momentum': analysis_result['momentum']['direction'],
                    'Volatility': analysis_result['volatility'],
                    'EntrySignal': analysis_result['entry_signal']['action'],
                    'SignalConfidence': analysis_result['entry_signal']['confidence'],
                    'MarketState': analysis_result['market_state'],
                    'Confidence': analysis_result['confidence'],
                    'Timestamp': analysis_result['timestamp']
                }
                await self.airtable_service.create_record('LiquidationAnalysis', record)
                logger.info(f"Airtable updated for {analysis_result['symbol']} short-term ratio")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")