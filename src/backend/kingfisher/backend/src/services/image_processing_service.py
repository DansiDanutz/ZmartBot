#!/usr/bin/env python3
"""
Image Processing Service for KingFisher Screenshots
Analyzes KingFisher automation images for liquidation data
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import io

from src.config.settings import settings

logger = logging.getLogger(__name__)

class ImageProcessingService:
    """Service for processing KingFisher automation images"""
    
    def __init__(self):
        self.is_ready_flag = True
        self.supported_formats = settings.SUPPORTED_FORMATS
        self.max_image_size = settings.MAX_IMAGE_SIZE
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process a KingFisher automation image"""
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Validate image
            if not self._validate_image(image_path):
                return {"error": "Invalid image format or size"}
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Failed to load image"}
            
            # Analyze image
            analysis_result = await self._analyze_image(image)
            
            # Add metadata
            analysis_result.update({
                "image_path": image_path,
                "processed_at": self._get_timestamp(),
                "image_size": self._get_image_size(image),
                "analysis_version": "1.0.0"
            })
            
            logger.info(f"Successfully processed image: {image_path}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {"error": str(e)}

    async def analyze_liquidation_heatmap(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze liquidation heatmap image"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Failed to decode image data"}
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Analyze thermal zones (red = high liquidation, blue = low)
            thermal_zones = self._analyze_thermal_zones(hsv)
            
            # Calculate concentration ratios
            long_concentration = self._calculate_long_concentration(thermal_zones)
            short_concentration = self._calculate_short_concentration(thermal_zones)
            
            # Calculate intensity and momentum
            intensity_score = self._calculate_intensity_score(thermal_zones)
            momentum_score = self._calculate_momentum_score(thermal_zones)
            
            return {
                "long_concentration": long_concentration,
                "short_concentration": short_concentration,
                "thermal_zones": thermal_zones,
                "intensity_score": intensity_score,
                "momentum_score": momentum_score,
                "volatility_score": self._calculate_volatility_score(thermal_zones),
                "breakout_score": self._calculate_breakout_score(thermal_zones),
                "stability_score": self._calculate_stability_score(thermal_zones),
                "liquidation_risk": self._calculate_liquidation_risk(thermal_zones),
                "confidence": self._calculate_confidence_score(thermal_zones)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidation heatmap: {e}")
            return self._get_default_heatmap_analysis()

    async def analyze_liquidation_map(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze liquidation map image"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Failed to decode image data"}
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Detect liquidation zones
            liquidation_zones = self._detect_liquidation_zones(hsv)
            
            # Calculate cluster density
            cluster_density = self._calculate_cluster_density(liquidation_zones)
            
            # Calculate risk metrics
            liquidation_risk = self._calculate_liquidation_risk_from_zones(liquidation_zones)
            
            return {
                "liquidation_zones": liquidation_zones,
                "cluster_density": cluster_density,
                "liquidation_risk": liquidation_risk,
                "momentum_score": self._calculate_momentum_from_zones(liquidation_zones),
                "volatility_score": self._calculate_volatility_from_zones(liquidation_zones),
                "breakout_score": self._calculate_breakout_from_zones(liquidation_zones),
                "stability_score": self._calculate_stability_from_zones(liquidation_zones),
                "confidence": self._calculate_confidence_from_zones(liquidation_zones)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidation map: {e}")
            return self._get_default_map_analysis()

    async def analyze_multi_symbol_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze multi-symbol screener image"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Failed to decode image data"}
            
            # Convert to grayscale for text detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect symbols and their data
            symbols_data = self._detect_symbols_data(gray)
            
            # Calculate overall market sentiment
            market_sentiment = self._calculate_market_sentiment(symbols_data)
            
            return {
                "symbols_data": symbols_data,
                "market_sentiment": market_sentiment,
                "top_performers": self._get_top_performers(symbols_data),
                "risk_indicators": self._calculate_risk_indicators(symbols_data),
                "opportunity_indicators": self._calculate_opportunity_indicators(symbols_data),
                "confidence": self._calculate_screener_confidence(symbols_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing multi-symbol image: {e}")
            return self._get_default_screener_analysis()

    async def analyze_general_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze general trading image"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Failed to decode image data"}
            
            # General analysis
            analysis = await self._analyze_image(image)
            
            # Add general image specific metrics
            analysis.update({
                "image_type": "general",
                "general_sentiment": analysis.get("market_sentiment", "neutral"),
                "general_confidence": analysis.get("analysis_confidence", 0.5)
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing general image: {e}")
            return self._get_default_general_analysis()

    def _validate_image(self, image_path: str) -> bool:
        """Validate image format and size"""
        try:
            path = Path(image_path)
            
            # Check if file exists
            if not path.exists():
                return False
            
            # Check file size
            if path.stat().st_size > self.max_image_size:
                return False
            
            # Check file extension
            extension = path.suffix.lower().lstrip('.')
            if extension not in self.supported_formats:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False
    
    async def _analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze KingFisher image for liquidation data"""
        try:
            analysis = {
                "liquidation_clusters": [],
                "toxic_flow": 0.0,
                "market_sentiment": "neutral",
                "significance_score": 0.0,
                "detected_symbols": [],
                "analysis_confidence": 0.0
            }
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect liquidation clusters (red areas)
            liquidation_clusters = self._detect_liquidation_clusters(hsv)
            analysis["liquidation_clusters"] = liquidation_clusters
            
            # Detect toxic flow
            toxic_flow = self._detect_toxic_flow(hsv)
            analysis["toxic_flow"] = toxic_flow
            
            # Analyze market sentiment
            market_sentiment = self._analyze_market_sentiment(image, liquidation_clusters, toxic_flow)
            analysis["market_sentiment"] = market_sentiment
            
            # Detect trading symbols
            detected_symbols = self._detect_trading_symbols(gray)
            analysis["detected_symbols"] = detected_symbols
            
            # Calculate significance score
            significance_score = self._calculate_significance_score(analysis)
            analysis["significance_score"] = significance_score
            
            # Calculate confidence
            confidence = self._calculate_confidence(analysis)
            analysis["analysis_confidence"] = confidence
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in _analyze_image: {e}")
            return {"error": str(e)}

    # Helper methods for liquidation heatmap analysis
    def _analyze_thermal_zones(self, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze thermal zones in heatmap"""
        zones = []
        
        # Define color ranges for thermal analysis
        # Red zones (high liquidation)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Blue zones (low liquidation)
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # Create masks
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze red zones (high liquidation)
        for contour in red_contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    "type": "high_liquidation",
                    "intensity": "high",
                    "area": area,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "color": "red"
                })
        
        # Analyze blue zones (low liquidation)
        for contour in blue_contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    "type": "low_liquidation",
                    "intensity": "low",
                    "area": area,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "color": "blue"
                })
        
        return zones

    def _calculate_long_concentration(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate long concentration from thermal zones"""
        high_liquidation_areas = sum(zone["area"] for zone in thermal_zones if zone["type"] == "high_liquidation")
        total_analyzed_area = sum(zone["area"] for zone in thermal_zones)
        
        if total_analyzed_area == 0:
            return 0.5
        
        return min(high_liquidation_areas / total_analyzed_area, 1.0)

    def _calculate_short_concentration(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate short concentration from thermal zones"""
        low_liquidation_areas = sum(zone["area"] for zone in thermal_zones if zone["type"] == "low_liquidation")
        total_analyzed_area = sum(zone["area"] for zone in thermal_zones)
        
        if total_analyzed_area == 0:
            return 0.5
        
        return min(low_liquidation_areas / total_analyzed_area, 1.0)

    def _calculate_intensity_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate intensity score from thermal zones"""
        high_intensity_areas = sum(zone["area"] for zone in thermal_zones if zone["intensity"] == "high")
        total_analyzed_area = sum(zone["area"] for zone in thermal_zones)
        
        if total_analyzed_area == 0:
            return 0.5
        
        return min(high_intensity_areas / total_analyzed_area, 1.0)

    def _calculate_momentum_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate momentum score from thermal zones"""
        # Simple momentum calculation based on zone distribution
        high_zones = len([z for z in thermal_zones if z["intensity"] == "high"])
        total_zones = len(thermal_zones)
        
        if total_zones == 0:
            return 0.5
        
        return min(high_zones / total_zones, 1.0)

    def _calculate_volatility_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate volatility score"""
        # Based on zone distribution and intensity variation
        if not thermal_zones:
            return 0.5
        
        intensities = [zone["area"] for zone in thermal_zones]
        if not intensities:
            return 0.5
        
        # Calculate coefficient of variation
        mean_intensity = np.mean(intensities)
        std_intensity = np.std(intensities)
        
        if mean_intensity == 0:
            return 0.5
        
        cv = float(std_intensity / mean_intensity)
        return min(cv, 1.0)

    def _calculate_breakout_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate breakout potential score"""
        # Based on concentration of high-intensity zones
        high_zones = [z for z in thermal_zones if z["intensity"] == "high"]
        total_zones = len(thermal_zones)
        
        if total_zones == 0:
            return 0.5
        
        concentration = len(high_zones) / total_zones
        return min(concentration * 1.5, 1.0)  # Amplify the score

    def _calculate_stability_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate stability score"""
        # Inverse of volatility
        volatility = self._calculate_volatility_score(thermal_zones)
        return max(1.0 - volatility, 0.0)

    def _calculate_liquidation_risk(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate liquidation risk score"""
        high_risk_zones = sum(zone["area"] for zone in thermal_zones if zone["type"] == "high_liquidation")
        total_analyzed_area = sum(zone["area"] for zone in thermal_zones)
        
        if total_analyzed_area == 0:
            return 0.5
        
        return min(high_risk_zones / total_analyzed_area, 1.0)

    def _calculate_confidence_score(self, thermal_zones: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for heatmap analysis"""
        if not thermal_zones:
            return 0.3
        
        # Higher confidence with more zones and larger areas
        total_area = sum(zone["area"] for zone in thermal_zones)
        zone_count = len(thermal_zones)
        
        area_score = min(total_area / 10000, 1.0)  # Normalize by expected area
        count_score = min(zone_count / 10, 1.0)    # Normalize by expected count
        
        return (area_score + count_score) / 2

    # Helper methods for liquidation map analysis
    def _detect_liquidation_zones(self, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect liquidation zones in map"""
        zones = []
        
        # Define color ranges for liquidation zones
        # Red zones (long liquidation)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Green zones (short liquidation)
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        # Create masks
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Find contours
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze red zones (long liquidation)
        for contour in red_contours:
            area = cv2.contourArea(contour)
            if area > 50:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    "direction": "long",
                    "size": area,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "color": "red",
                    "intensity": "high" if area > 500 else "medium"
                })
        
        # Analyze green zones (short liquidation)
        for contour in green_contours:
            area = cv2.contourArea(contour)
            if area > 50:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                zones.append({
                    "direction": "short",
                    "size": area,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "color": "green",
                    "intensity": "high" if area > 500 else "medium"
                })
        
        return zones

    def _calculate_cluster_density(self, liquidation_zones: List[Dict[str, Any]]) -> float:
        """Calculate cluster density"""
        if not liquidation_zones:
            return 0.5
        
        total_area = sum(zone["size"] for zone in liquidation_zones)
        zone_count = len(liquidation_zones)
        
        # Normalize by expected values
        area_score = min(total_area / 5000, 1.0)
        count_score = min(zone_count / 20, 1.0)
        
        return (area_score + count_score) / 2

    def _calculate_liquidation_risk_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate liquidation risk from zones"""
        if not zones:
            return 0.5
        
        high_intensity_zones = [z for z in zones if z["intensity"] == "high"]
        total_zones = len(zones)
        
        return min(len(high_intensity_zones) / total_zones, 1.0)

    def _calculate_momentum_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate momentum from zones"""
        if not zones:
            return 0.5
        
        long_zones = [z for z in zones if z["direction"] == "long"]
        short_zones = [z for z in zones if z["direction"] == "short"]
        
        long_pressure = sum(z["size"] for z in long_zones)
        short_pressure = sum(z["size"] for z in short_zones)
        
        total_pressure = long_pressure + short_pressure
        if total_pressure == 0:
            return 0.5
        
        # Momentum based on pressure imbalance
        imbalance = abs(long_pressure - short_pressure) / total_pressure
        return min(imbalance * 2, 1.0)

    def _calculate_volatility_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate volatility from zones"""
        if not zones:
            return 0.5
        
        sizes = [zone["size"] for zone in zones]
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        
        if mean_size == 0:
            return 0.5
        
        cv = float(std_size / mean_size)
        return min(cv, 1.0)

    def _calculate_breakout_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate breakout potential from zones"""
        if not zones:
            return 0.5
        
        high_intensity_zones = [z for z in zones if z["intensity"] == "high"]
        total_zones = len(zones)
        
        concentration = len(high_intensity_zones) / total_zones
        return min(concentration * 1.3, 1.0)

    def _calculate_stability_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate stability from zones"""
        volatility = self._calculate_volatility_from_zones(zones)
        return max(1.0 - volatility, 0.0)

    def _calculate_confidence_from_zones(self, zones: List[Dict[str, Any]]) -> float:
        """Calculate confidence from zones"""
        if not zones:
            return 0.3
        
        total_area = sum(zone["size"] for zone in zones)
        zone_count = len(zones)
        
        area_score = min(total_area / 3000, 1.0)
        count_score = min(zone_count / 15, 1.0)
        
        return (area_score + count_score) / 2

    # Helper methods for multi-symbol analysis
    def _detect_symbols_data(self, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect symbols and their data from screener image"""
        # This is a simplified implementation
        # In a real scenario, you'd use OCR to extract text and parse symbol data
        symbols_data = []
        
        # Mock data for demonstration
        symbols_data.append({
            "symbol": "BTC/USDT",
            "price": 45000.0,
            "change_24h": 2.5,
            "volume": 1500000000,
            "sentiment": "bullish"
        })
        
        symbols_data.append({
            "symbol": "ETH/USDT",
            "price": 3200.0,
            "change_24h": -1.2,
            "volume": 800000000,
            "sentiment": "bearish"
        })
        
        return symbols_data

    def _calculate_market_sentiment(self, symbols_data: List[Dict[str, Any]]) -> str:
        """Calculate overall market sentiment from symbols data"""
        if not symbols_data:
            return "neutral"
        
        bullish_count = len([s for s in symbols_data if s.get("sentiment") == "bullish"])
        bearish_count = len([s for s in symbols_data if s.get("sentiment") == "bearish"])
        
        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"

    def _get_top_performers(self, symbols_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top performing symbols"""
        if not symbols_data:
            return []
        
        # Sort by 24h change
        sorted_symbols = sorted(symbols_data, key=lambda x: x.get("change_24h", 0), reverse=True)
        return sorted_symbols[:3]

    def _calculate_risk_indicators(self, symbols_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk indicators from symbols data"""
        if not symbols_data:
            return {"risk_level": "medium", "volatility": 0.5}
        
        changes = [s.get("change_24h", 0) for s in symbols_data]
        volatility = np.std(changes) if changes else 0.5
        
        if volatility > 5:
            risk_level = "high"
        elif volatility > 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "volatility": min(volatility / 10, 1.0)
        }

    def _calculate_opportunity_indicators(self, symbols_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate opportunity indicators from symbols data"""
        if not symbols_data:
            return {"opportunity_score": 0.5, "trend_strength": 0.5}
        
        positive_changes = [s.get("change_24h", 0) for s in symbols_data if s.get("change_24h", 0) > 0]
        negative_changes = [s.get("change_24h", 0) for s in symbols_data if s.get("change_24h", 0) < 0]
        
        avg_positive = np.mean(positive_changes) if positive_changes else 0
        avg_negative = abs(np.mean(negative_changes)) if negative_changes else 0
        
        opportunity_score = min((avg_positive - avg_negative) / 10 + 0.5, 1.0)
        trend_strength = min((avg_positive + avg_negative) / 10, 1.0)
        
        return {
            "opportunity_score": max(opportunity_score, 0.0),
            "trend_strength": trend_strength
        }

    def _calculate_screener_confidence(self, symbols_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence for screener analysis"""
        if not symbols_data:
            return 0.3
        
        # Higher confidence with more symbols and data
        symbol_count = len(symbols_data)
        data_completeness = sum(1 for s in symbols_data if all(k in s for k in ["price", "change_24h", "volume"]))
        
        count_score = min(symbol_count / 10, 1.0)
        completeness_score = data_completeness / symbol_count if symbol_count > 0 else 0
        
        return (count_score + completeness_score) / 2

    # Default analysis methods
    def _get_default_heatmap_analysis(self) -> Dict[str, Any]:
        """Get default heatmap analysis"""
        return {
            "long_concentration": 0.5,
            "short_concentration": 0.5,
            "thermal_zones": [],
            "intensity_score": 0.5,
            "momentum_score": 0.5,
            "volatility_score": 0.5,
            "breakout_score": 0.5,
            "stability_score": 0.5,
            "liquidation_risk": 0.5,
            "confidence": 0.3
        }

    def _get_default_map_analysis(self) -> Dict[str, Any]:
        """Get default map analysis"""
        return {
            "liquidation_zones": [],
            "cluster_density": 0.5,
            "liquidation_risk": 0.5,
            "momentum_score": 0.5,
            "volatility_score": 0.5,
            "breakout_score": 0.5,
            "stability_score": 0.5,
            "confidence": 0.3
        }

    def _get_default_screener_analysis(self) -> Dict[str, Any]:
        """Get default screener analysis"""
        return {
            "symbols_data": [],
            "market_sentiment": "neutral",
            "top_performers": [],
            "risk_indicators": {"risk_level": "medium", "volatility": 0.5},
            "opportunity_indicators": {"opportunity_score": 0.5, "trend_strength": 0.5},
            "confidence": 0.3
        }

    def _get_default_general_analysis(self) -> Dict[str, Any]:
        """Get default general analysis"""
        return {
            "image_type": "general",
            "general_sentiment": "neutral",
            "general_confidence": 0.3,
            "liquidation_clusters": [],
            "toxic_flow": 0.0,
            "market_sentiment": "neutral",
            "significance_score": 0.0,
            "detected_symbols": [],
            "analysis_confidence": 0.3
        }

    def _detect_liquidation_clusters(self, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect liquidation clusters in image"""
        clusters = []
        
        # Define color ranges for liquidation clusters
        # Red areas (high liquidation)
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
                clusters.append({
                    "area": area,
                    "position": {"x": x, "y": y, "width": w, "height": h},
                    "intensity": "high" if area > 500 else "medium"
                })
        
        return clusters
    
    def _detect_toxic_flow(self, hsv: np.ndarray) -> float:
        """Detect toxic flow in image"""
        # Define color ranges for toxic flow detection
        # Green areas (toxic flow)
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        # Create mask
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Calculate toxic flow percentage
        total_pixels = hsv.shape[0] * hsv.shape[1]
        toxic_pixels = np.count_nonzero(green_mask)
        
        if total_pixels == 0:
            return 0.0
        
        return min(toxic_pixels / total_pixels, 1.0)
    
    def _analyze_market_sentiment(self, image: np.ndarray, clusters: List[Dict], toxic_flow: float) -> str:
        """Analyze market sentiment based on clusters and toxic flow"""
        if not clusters:
            return "neutral"
        
        # Calculate cluster intensity
        total_cluster_area = sum(cluster["area"] for cluster in clusters)
        avg_cluster_area = total_cluster_area / len(clusters) if clusters else 0
        
        # Determine sentiment based on cluster intensity and toxic flow
        if avg_cluster_area > 1000 and toxic_flow > 0.1:
            return "bearish"
        elif avg_cluster_area < 200 and toxic_flow < 0.05:
            return "bullish"
        else:
            return "neutral"
    
    def _detect_trading_symbols(self, gray: np.ndarray) -> List[str]:
        """Detect trading symbols in image"""
        # This is a simplified implementation
        # In a real scenario, you'd use OCR to extract text
        symbols = []
        
        # Mock detection for demonstration
        # You would implement actual OCR here
        symbols = ["BTC/USDT", "ETH/USDT"]
        
        return symbols
    
    def _calculate_significance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate significance score of analysis"""
        score = 0.0
        
        # Factor in cluster count
        cluster_count = len(analysis.get("liquidation_clusters", []))
        score += min(cluster_count / 10, 1.0) * 0.3
        
        # Factor in toxic flow
        toxic_flow = analysis.get("toxic_flow", 0.0)
        score += toxic_flow * 0.3
        
        # Factor in sentiment
        sentiment = analysis.get("market_sentiment", "neutral")
        if sentiment == "bullish":
            score += 0.2
        elif sentiment == "bearish":
            score += 0.2
        
        # Factor in detected symbols
        symbol_count = len(analysis.get("detected_symbols", []))
        score += min(symbol_count / 5, 1.0) * 0.2
        
        return min(score, 1.0)
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence in analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence with more data
        if analysis.get("liquidation_clusters"):
            confidence += 0.2
        
        if analysis.get("toxic_flow", 0) > 0:
            confidence += 0.1
        
        if analysis.get("detected_symbols"):
            confidence += 0.1
        
        if analysis.get("market_sentiment") != "neutral":
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_image_size(self, image: np.ndarray) -> Dict[str, int]:
        """Get image dimensions"""
        height, width = image.shape[:2]
        return {"width": width, "height": height}
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.is_ready_flag
    
    async def test_processing(self, image_path: str) -> Dict[str, Any]:
        """Test image processing"""
        return await self.process_image(image_path) 