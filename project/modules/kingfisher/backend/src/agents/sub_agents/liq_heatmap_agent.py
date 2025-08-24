#!/usr/bin/env python3
"""
Liquidation Heatmap Sub-Agent
Analyzes liquidation heatmap images showing concentration levels
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class LiqHeatmapAgent:
    """Sub-agent for analyzing liquidation heatmap images"""
    
    def __init__(self, airtable_service=None):
        self.agent_name = "liq_heatmap_agent"
        self.airtable_service = airtable_service
        self.analysis_version = "1.0.0"
        logger.info("Liquidation Heatmap Agent initialized")
    
    async def analyze(self, image_data: bytes, symbol: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze liquidation heatmap image
        
        Returns:
            - heat_zones: Identified heat zones and their intensities
            - concentration_levels: Price levels with high liquidation concentration
            - risk_assessment: Overall risk based on heatmap
            - optimal_entry_zones: Suggested entry zones based on heat distribution
        """
        try:
            logger.info(f"Analyzing liquidation heatmap for {symbol}")
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Identify heat zones
            heat_zones = self._identify_heat_zones(hsv)
            
            # Calculate concentration levels
            concentration_levels = self._calculate_concentration_levels(heat_zones)
            
            # Assess liquidation distribution
            long_heat, short_heat = self._assess_liquidation_distribution(heat_zones)
            
            # Normalize to percentages
            total_heat = long_heat + short_heat
            if total_heat > 0:
                long_percentage = (long_heat / total_heat) * 100
                short_percentage = (short_heat / total_heat) * 100
            else:
                long_percentage = 50.0
                short_percentage = 50.0
            
            # Risk assessment
            risk_assessment = self._assess_risk(heat_zones, concentration_levels)
            
            # Find optimal entry zones
            optimal_zones = self._find_optimal_entry_zones(heat_zones, concentration_levels)
            
            # Calculate confidence
            confidence = self._calculate_confidence(heat_zones, concentration_levels)
            
            analysis_result = {
                'agent': self.agent_name,
                'symbol': symbol,
                'image_type': 'liq_heatmap',
                'heat_zones': heat_zones,
                'concentration_levels': concentration_levels,
                'long_heat_percentage': long_percentage,
                'short_heat_percentage': short_percentage,
                'liquidation_ratio': {
                    'long': long_percentage,
                    'short': short_percentage
                },
                'risk_assessment': risk_assessment,
                'optimal_entry_zones': optimal_zones,
                'heat_intensity': {
                    'maximum': max([z['intensity'] for z in heat_zones]) if heat_zones else 0,
                    'average': np.mean([z['intensity'] for z in heat_zones]) if heat_zones else 0,
                    'distribution': 'concentrated' if len(concentration_levels) < 3 else 'distributed'
                },
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Update Airtable
            if self.airtable_service:
                await self._update_airtable(analysis_result)
            
            logger.info(f"Heatmap analysis: Risk {risk_assessment['level']}, Long {long_percentage:.1f}% vs Short {short_percentage:.1f}%")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing heatmap for {symbol}: {e}")
            return {
                'agent': self.agent_name,
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _identify_heat_zones(self, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Identify heat zones in the heatmap"""
        zones = []
        
        # Define color ranges for different heat levels
        # Hot zones (red/orange) - high liquidation
        hot_lower = np.array([0, 100, 100])
        hot_upper = np.array([20, 255, 255])
        
        # Warm zones (yellow) - medium liquidation
        warm_lower = np.array([20, 100, 100])
        warm_upper = np.array([40, 255, 255])
        
        # Cool zones (green/blue) - low liquidation
        cool_lower = np.array([40, 50, 50])
        cool_upper = np.array([120, 255, 255])
        
        # Create masks for each heat level
        hot_mask = cv2.inRange(hsv, hot_lower, hot_upper)
        warm_mask = cv2.inRange(hsv, warm_lower, warm_upper)
        cool_mask = cv2.inRange(hsv, cool_lower, cool_upper)
        
        # Process hot zones
        hot_contours, _ = cv2.findContours(hot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in hot_contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'type': 'hot',
                    'intensity': 1.0,
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'price_level': self._estimate_price_level(y, hsv.shape[0]),
                    'liquidation_type': 'high'
                })
        
        # Process warm zones
        warm_contours, _ = cv2.findContours(warm_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in warm_contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'type': 'warm',
                    'intensity': 0.6,
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'price_level': self._estimate_price_level(y, hsv.shape[0]),
                    'liquidation_type': 'medium'
                })
        
        # Process cool zones
        cool_contours, _ = cv2.findContours(cool_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cool_contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    'type': 'cool',
                    'intensity': 0.3,
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'price_level': self._estimate_price_level(y, hsv.shape[0]),
                    'liquidation_type': 'low'
                })
        
        return sorted(zones, key=lambda z: z['intensity'], reverse=True)
    
    def _calculate_concentration_levels(self, heat_zones: List[Dict]) -> List[Dict[str, Any]]:
        """Calculate concentration levels from heat zones"""
        if not heat_zones:
            return []
        
        # Group zones by price level
        price_levels = {}
        for zone in heat_zones:
            level = round(zone['price_level'], 2)
            if level not in price_levels:
                price_levels[level] = {
                    'intensity_sum': 0,
                    'area_sum': 0,
                    'zone_count': 0,
                    'types': []
                }
            
            price_levels[level]['intensity_sum'] += zone['intensity']
            price_levels[level]['area_sum'] += zone['area']
            price_levels[level]['zone_count'] += 1
            price_levels[level]['types'].append(zone['type'])
        
        # Convert to list and calculate scores
        concentration_levels = []
        for level, data in price_levels.items():
            concentration_score = (data['intensity_sum'] / data['zone_count']) * (data['area_sum'] / 1000)
            concentration_levels.append({
                'price_level': level,
                'concentration_score': min(concentration_score, 1.0),
                'zone_count': data['zone_count'],
                'dominant_type': max(set(data['types']), key=data['types'].count),
                'total_area': data['area_sum']
            })
        
        # Sort by concentration score
        return sorted(concentration_levels, key=lambda c: c['concentration_score'], reverse=True)[:5]
    
    def _assess_liquidation_distribution(self, heat_zones: List[Dict]) -> tuple:
        """Assess liquidation distribution between long and short"""
        long_heat = 0
        short_heat = 0
        
        for zone in heat_zones:
            # Determine if zone is for long or short liquidations based on position
            # Upper half typically shows short liquidations, lower half shows long liquidations
            if zone['price_level'] > 0.5:
                short_heat += zone['intensity'] * zone['area']
            else:
                long_heat += zone['intensity'] * zone['area']
        
        return long_heat, short_heat
    
    def _assess_risk(self, heat_zones: List[Dict], concentration_levels: List[Dict]) -> Dict[str, Any]:
        """Assess overall risk based on heatmap"""
        if not heat_zones:
            return {'level': 'low', 'score': 0.3, 'reasoning': 'No significant heat zones detected'}
        
        # Calculate risk factors
        hot_zones = [z for z in heat_zones if z['type'] == 'hot']
        total_hot_area = sum(z['area'] for z in hot_zones)
        
        # High concentration = high risk
        max_concentration = max([c['concentration_score'] for c in concentration_levels]) if concentration_levels else 0
        
        # Many hot zones = high risk
        hot_zone_ratio = len(hot_zones) / len(heat_zones) if heat_zones else 0
        
        # Calculate risk score
        risk_score = (max_concentration * 0.4 + hot_zone_ratio * 0.3 + min(total_hot_area / 10000, 1.0) * 0.3)
        
        # Determine risk level
        if risk_score > 0.7:
            level = 'high'
            reasoning = 'Multiple hot zones with high concentration detected'
        elif risk_score > 0.4:
            level = 'medium'
            reasoning = 'Moderate heat concentration detected'
        else:
            level = 'low'
            reasoning = 'Low heat concentration, safe for entry'
        
        return {
            'level': level,
            'score': risk_score,
            'reasoning': reasoning,
            'hot_zones': len(hot_zones),
            'max_concentration': max_concentration
        }
    
    def _find_optimal_entry_zones(self, heat_zones: List[Dict], concentration_levels: List[Dict]) -> List[Dict]:
        """Find optimal entry zones based on heat distribution"""
        optimal_zones = []
        
        # Find price levels with low heat (good for entry)
        all_price_levels = set([round(z['price_level'], 2) for z in heat_zones])
        high_concentration_levels = set([c['price_level'] for c in concentration_levels[:3]])
        
        # Safe zones are where there's low heat
        safe_levels = all_price_levels - high_concentration_levels
        
        for level in safe_levels:
            # Find zones at this level
            level_zones = [z for z in heat_zones if abs(z['price_level'] - level) < 0.05]
            if level_zones:
                avg_intensity = np.mean([z['intensity'] for z in level_zones])
                if avg_intensity < 0.5:  # Low intensity = good entry
                    optimal_zones.append({
                        'price_level': level,
                        'safety_score': 1.0 - avg_intensity,
                        'zone_type': 'entry',
                        'reasoning': 'Low liquidation concentration'
                    })
        
        # Also identify support/resistance based on high concentration
        for conc in concentration_levels[:2]:  # Top 2 concentration levels
            optimal_zones.append({
                'price_level': conc['price_level'],
                'safety_score': 0.3,  # Lower safety due to high concentration
                'zone_type': 'avoid',
                'reasoning': 'High liquidation concentration - potential volatility'
            })
        
        return sorted(optimal_zones, key=lambda z: z['safety_score'], reverse=True)
    
    def _estimate_price_level(self, y_position: int, image_height: int) -> float:
        """Estimate relative price level from Y position"""
        return 1.0 - (y_position / image_height)
    
    def _calculate_confidence(self, heat_zones: List[Dict], concentration_levels: List[Dict]) -> float:
        """Calculate confidence score"""
        confidence = 0.5
        
        # More zones = better analysis
        if len(heat_zones) > 10:
            confidence += 0.2
        elif len(heat_zones) > 5:
            confidence += 0.1
        
        # Clear concentration levels
        if len(concentration_levels) > 3:
            confidence += 0.15
        
        # Variety of zone types
        zone_types = set([z['type'] for z in heat_zones])
        if len(zone_types) >= 3:
            confidence += 0.15
        
        return min(max(confidence, 0.3), 1.0)
    
    async def _update_airtable(self, analysis_result: Dict[str, Any]):
        """Update Airtable with analysis results"""
        try:
            if self.airtable_service:
                record = {
                    'Symbol': analysis_result['symbol'],
                    'Agent': self.agent_name,
                    'ImageType': 'liq_heatmap',
                    'LongPercentage': analysis_result['long_heat_percentage'],
                    'ShortPercentage': analysis_result['short_heat_percentage'],
                    'RiskLevel': analysis_result['risk_assessment']['level'],
                    'RiskScore': analysis_result['risk_assessment']['score'],
                    'HeatZones': len(analysis_result['heat_zones']),
                    'MaxIntensity': analysis_result['heat_intensity']['maximum'],
                    'Distribution': analysis_result['heat_intensity']['distribution'],
                    'Confidence': analysis_result['confidence'],
                    'Timestamp': analysis_result['timestamp']
                }
                await self.airtable_service.create_record('LiquidationAnalysis', record)
                logger.info(f"Airtable updated for {analysis_result['symbol']} heatmap")
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")