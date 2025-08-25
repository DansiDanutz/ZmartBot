#!/usr/bin/env python3
"""
Liquidation Map Sub-Agent
Analyzes liquidation map images to determine long/short liquidation zones
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class LiquidationMapAgent:
    """Sub-agent for analyzing liquidation map images"""
    
    def __init__(self, airtable_service=None):
        self.agent_name = "liquidation_map_agent"
        self.airtable_service = airtable_service
        self.analysis_version = "1.0.0"
        logger.info("Liquidation Map Agent initialized")
    
    async def analyze(self, image_data: bytes, symbol: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze liquidation map image
        
        Returns:
            - long_liquidation_zones: Number and intensity of long liquidation zones
            - short_liquidation_zones: Number and intensity of short liquidation zones
            - liquidation_ratio: Ratio of long to short liquidations
            - critical_levels: Price levels with high liquidation concentration
            - support_resistance_levels: Extracted support and resistance levels for all timeframes
        """
        try:
            logger.info(f"Analyzing liquidation map for {symbol}")
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Detect long liquidation zones (typically red)
            long_zones = self._detect_long_liquidation_zones(hsv)
            
            # Detect short liquidation zones (typically green)
            short_zones = self._detect_short_liquidation_zones(hsv)
            
            # Calculate liquidation metrics
            total_long_intensity = sum(zone['intensity'] * zone['size'] for zone in long_zones)
            total_short_intensity = sum(zone['intensity'] * zone['size'] for zone in short_zones)
            
            total_intensity = total_long_intensity + total_short_intensity
            
            if total_intensity > 0:
                long_percentage = (total_long_intensity / total_intensity) * 100
                short_percentage = (total_short_intensity / total_intensity) * 100
            else:
                long_percentage = 50.0
                short_percentage = 50.0
            
            # Identify critical levels
            critical_levels = self._identify_critical_levels(long_zones, short_zones)
            
            # Extract support and resistance levels for all timeframes
            support_resistance_24h = self._extract_support_resistance(long_zones, short_zones, '24h')
            support_resistance_7d = self._extract_support_resistance(long_zones, short_zones, '7d')
            support_resistance_1m = self._extract_support_resistance(long_zones, short_zones, '1m')
            
            # Calculate confidence based on zone detection quality
            confidence = self._calculate_confidence(long_zones, short_zones)
            
            analysis_result = {
                'agent': self.agent_name,
                'symbol': symbol,
                'image_type': 'liquidation_map',
                'long_liquidation_zones': len(long_zones),
                'short_liquidation_zones': len(short_zones),
                'long_intensity': total_long_intensity,
                'short_intensity': total_short_intensity,
                'long_percentage': long_percentage,
                'short_percentage': short_percentage,
                'liquidation_ratio': {
                    'long': long_percentage,
                    'short': short_percentage
                },
                'critical_levels': critical_levels,
                'zones_detail': {
                    'long': long_zones,
                    'short': short_zones
                },
                'support_resistance_levels': {
                    '24h': support_resistance_24h,
                    '7d': support_resistance_7d,
                    '1m': support_resistance_1m
                },
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Update Airtable
            if self.airtable_service:
                await self._update_airtable(analysis_result)
            
            logger.info(f"Liquidation map analysis complete: Long {long_percentage:.1f}% vs Short {short_percentage:.1f}%")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing liquidation map for {symbol}: {e}")
            return {
                'agent': self.agent_name,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _detect_long_liquidation_zones(self, hsv: np.ndarray) -> list:
        """Detect long liquidation zones (red areas)"""
        zones = []
        
        # Define color ranges for red (long liquidations)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # Find contours
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate intensity based on area and position
                intensity = min(area / 1000, 1.0)  # Normalize intensity
                
                zones.append({
                    'type': 'long',
                    'size': area,
                    'intensity': intensity,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'price_level': self._estimate_price_level(y, hsv.shape[0])
                })
        
        return sorted(zones, key=lambda z: z['intensity'], reverse=True)
    
    def _detect_short_liquidation_zones(self, hsv: np.ndarray) -> list:
        """Detect short liquidation zones (green areas)"""
        zones = []
        
        # Define color ranges for green (short liquidations)
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        # Create mask
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Find contours
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate intensity based on area and position
                intensity = min(area / 1000, 1.0)  # Normalize intensity
                
                zones.append({
                    'type': 'short',
                    'size': area,
                    'intensity': intensity,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'price_level': self._estimate_price_level(y, hsv.shape[0])
                })
        
        return sorted(zones, key=lambda z: z['intensity'], reverse=True)
    
    def _identify_critical_levels(self, long_zones: list, short_zones: list) -> list:
        """Identify critical price levels with high liquidation concentration"""
        critical_levels = []
        
        # Combine all zones
        all_zones = long_zones + short_zones
        
        # Group by price level
        price_levels = {}
        for zone in all_zones:
            level = zone['price_level']
            if level not in price_levels:
                price_levels[level] = {'long': 0, 'short': 0, 'total': 0}
            
            if zone['type'] == 'long':
                price_levels[level]['long'] += zone['intensity']
            else:
                price_levels[level]['short'] += zone['intensity']
            
            price_levels[level]['total'] += zone['intensity']
        
        # Sort by total intensity and get top levels
        sorted_levels = sorted(price_levels.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for level, data in sorted_levels[:5]:  # Top 5 critical levels
            critical_levels.append({
                'price_level': level,
                'intensity': data['total'],
                'long_intensity': data['long'],
                'short_intensity': data['short'],
                'dominant_side': 'long' if data['long'] > data['short'] else 'short'
            })
        
        return critical_levels
    
    def _estimate_price_level(self, y_position: int, image_height: int) -> float:
        """Estimate relative price level from Y position (0-1 scale)"""
        # Top of image = higher price, bottom = lower price
        return 1.0 - (y_position / image_height)
    
    def _calculate_confidence(self, long_zones: list, short_zones: list) -> float:
        """Calculate confidence score based on zone detection quality"""
        total_zones = len(long_zones) + len(short_zones)
        
        if total_zones == 0:
            return 0.3
        
        # More zones = higher confidence
        zone_score = min(total_zones / 20, 1.0)
        
        # Balanced distribution = higher confidence
        if total_zones > 0:
            balance = min(len(long_zones), len(short_zones)) / max(len(long_zones), len(short_zones), 1)
        else:
            balance = 0
        
        # Average intensity
        all_intensities = [z['intensity'] for z in long_zones + short_zones]
        avg_intensity = np.mean(all_intensities) if all_intensities else 0
        
        confidence = (zone_score * 0.4 + balance * 0.3 + avg_intensity * 0.3)
        return min(max(confidence, 0.3), 1.0)
    
    def _extract_support_resistance(self, long_zones: list, short_zones: list, timeframe: str) -> Dict[str, Any]:
        """Extract support and resistance levels from liquidation zones"""
        support_levels = []
        resistance_levels = []
        
        # Long liquidation zones create support (buyers stepping in)
        for zone in long_zones:
            if zone['intensity'] > 0.3:  # Significant zones only
                support_levels.append({
                    'price': zone['price_level'],
                    'strength': zone['intensity'],
                    'volume': zone['size'],
                    'type': 'support',
                    'source': 'long_liquidation',
                    'timeframe': timeframe
                })
        
        # Short liquidation zones create resistance (sellers stepping in)
        for zone in short_zones:
            if zone['intensity'] > 0.3:  # Significant zones only
                resistance_levels.append({
                    'price': zone['price_level'],
                    'strength': zone['intensity'],
                    'volume': zone['size'],
                    'type': 'resistance',
                    'source': 'short_liquidation',
                    'timeframe': timeframe
                })
        
        # Sort by strength
        support_levels.sort(key=lambda x: x['strength'], reverse=True)
        resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        # Get top 3 of each
        top_supports = support_levels[:3]
        top_resistances = resistance_levels[:3]
        
        # Calculate targets based on levels
        targets = self._calculate_targets(top_supports, top_resistances, timeframe)
        
        return {
            'support_levels': top_supports,
            'resistance_levels': top_resistances,
            'strongest_support': top_supports[0] if top_supports else None,
            'strongest_resistance': top_resistances[0] if top_resistances else None,
            'targets': targets,
            'total_levels': len(support_levels) + len(resistance_levels)
        }
    
    def _calculate_targets(self, supports: list, resistances: list, timeframe: str) -> Dict[str, Any]:
        """Calculate trading targets based on support/resistance levels"""
        if not supports or not resistances:
            return {}
        
        # Adjust target distances based on timeframe
        if timeframe == '24h':
            target_multiplier = 1.02  # 2% for 24h
            stop_multiplier = 0.99   # 1% stop
        elif timeframe == '7d':
            target_multiplier = 1.05  # 5% for 7d
            stop_multiplier = 0.97   # 3% stop
        else:  # 1m
            target_multiplier = 1.10  # 10% for 1m
            stop_multiplier = 0.95   # 5% stop
        
        # Long targets
        long_targets = {
            'entry': supports[0]['price'] if supports else 0,
            'target_1': resistances[0]['price'] if resistances else 0,
            'target_2': resistances[1]['price'] if len(resistances) > 1 else resistances[0]['price'] * target_multiplier if resistances else 0,
            'target_3': resistances[2]['price'] if len(resistances) > 2 else resistances[0]['price'] * (target_multiplier ** 2) if resistances else 0,
            'stop_loss': supports[0]['price'] * stop_multiplier if supports else 0
        }
        
        # Short targets
        short_targets = {
            'entry': resistances[0]['price'] if resistances else 0,
            'target_1': supports[0]['price'] if supports else 0,
            'target_2': supports[1]['price'] if len(supports) > 1 else supports[0]['price'] / target_multiplier if supports else 0,
            'target_3': supports[2]['price'] if len(supports) > 2 else supports[0]['price'] / (target_multiplier ** 2) if supports else 0,
            'stop_loss': resistances[0]['price'] / stop_multiplier if resistances else 0
        }
        
        return {
            'long': long_targets,
            'short': short_targets
        }
    
    async def _update_airtable(self, analysis_result: Dict[str, Any]):
        """Update Airtable with analysis results"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis_result['symbol'],
                    'Agent': self.agent_name,
                    'ImageType': 'liquidation_map',
                    'LongPercentage': analysis_result['long_percentage'],
                    'ShortPercentage': analysis_result['short_percentage'],
                    'LongZones': analysis_result['long_liquidation_zones'],
                    'ShortZones': analysis_result['short_liquidation_zones'],
                    'Confidence': analysis_result['confidence'],
                    'Timestamp': analysis_result['timestamp']
                }
                
                # Add support/resistance data
                for tf in ['24h', '7d', '1m']:
                    sr_data = analysis_result['support_resistance_levels'].get(tf, {})
                    if sr_data:
                        record[f'Support_{tf}'] = str(sr_data.get('strongest_support', {}).get('price', 0))
                        record[f'Resistance_{tf}'] = str(sr_data.get('strongest_resistance', {}).get('price', 0))
                
                await self.airtable_service.create_record('LiquidationAnalysis', record)
                logger.info(f"Airtable updated for {analysis_result['symbol']} liquidation map")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")