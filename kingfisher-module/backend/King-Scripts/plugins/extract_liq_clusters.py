#!/usr/bin/env python3
"""
Extract Liquidation Clusters Plugin for STEP-5
Handles liquidation cluster extraction and analysis
"""

import logging
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from PIL import Image
import cv2

# Import the base plugin class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from step5_runner import BasePlugin, ProcessingContext

logger = logging.getLogger(__name__)

class ExtractLiqClustersPlugin(BasePlugin):
    """Plugin for extracting liquidation clusters from images"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.cluster_threshold = config.get("cluster_threshold", 0.8)
        self.max_clusters = config.get("max_clusters", 10)
        self.min_cluster_size = config.get("min_cluster_size", 5)
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required image data"""
        if not context.image_path:
            logger.error("Image path is required for ExtractLiqClustersPlugin")
            return False
        
        if not os.path.exists(context.image_path):
            logger.error(f"Image file not found: {context.image_path}")
            return False
            
        return True
    
    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Execute liquidation cluster extraction logic"""
        logger.info(f"🎯 Extracting liquidation clusters from: {context.image_path}")
        
        # 1. Load and preprocess image
        image = self._load_image(context.image_path)
        if image is None:
            context.errors.append(f"Failed to load image: {context.image_path}")
            return context
        
        # 2. Detect liquidation zones
        liquidation_zones = self._detect_liquidation_zones(image)
        
        # 3. Extract clusters from zones
        clusters = self._extract_clusters(liquidation_zones, image)
        
        # 4. Analyze cluster properties
        analyzed_clusters = self._analyze_clusters(clusters, context.symbol)
        
        # 5. Update context with results
        context.liquidation_clusters = analyzed_clusters
        context.analysis_data["liquidation_extraction"] = {
            "total_zones": len(liquidation_zones),
            "total_clusters": len(analyzed_clusters),
            "image_dimensions": image.shape[:2],
            "threshold_used": self.cluster_threshold,
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Extracted {len(analyzed_clusters)} liquidation clusters")
        return context
    
    def _load_image(self, image_path: str):
        """Load image using OpenCV"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"OpenCV failed to load image: {image_path}")
                return None
                
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def _detect_liquidation_zones(self, image) -> List[Dict[str, Any]]:
        """Detect liquidation zones using color analysis"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Define color ranges for liquidation indicators (red zones typically)
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            
            # Create masks for red colors
            mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            red_mask = mask1 + mask2
            
            # Find contours in the mask
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            zones = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > self.min_cluster_size:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    zones.append({
                        "zone_id": i,
                        "contour": contour,
                        "area": area,
                        "bounding_box": {"x": x, "y": y, "width": w, "height": h},
                        "center": {"x": x + w//2, "y": y + h//2}
                    })
            
            logger.info(f"🔍 Detected {len(zones)} liquidation zones")
            return zones
            
        except Exception as e:
            logger.error(f"Error detecting liquidation zones: {e}")
            return []
    
    def _extract_clusters(self, zones: List[Dict[str, Any]], image) -> List[Dict[str, Any]]:
        """Extract clusters from detected zones"""
        clusters = []
        
        for zone in zones[:self.max_clusters]:  # Limit to max clusters
            try:
                # Extract cluster properties
                cluster = {
                    "cluster_id": len(clusters),
                    "zone_id": zone["zone_id"],
                    "area": zone["area"],
                    "center": zone["center"],
                    "bounding_box": zone["bounding_box"],
                    "confidence": min(zone["area"] / 1000.0, 1.0),  # Normalize confidence
                    "cluster_type": self._classify_cluster_position(zone["center"], image.shape)
                }
                
                clusters.append(cluster)
                
            except Exception as e:
                logger.error(f"Error extracting cluster from zone {zone['zone_id']}: {e}")
        
        return clusters
    
    def _classify_cluster_position(self, center: Dict[str, int], image_shape) -> str:
        """Classify cluster as support or resistance based on position"""
        height = image_shape[0]
        y_position = center["y"]
        
        # Bottom half = support, top half = resistance
        if y_position > height * 0.5:
            return "support"
        else:
            return "resistance"
    
    def _analyze_clusters(self, clusters: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
        """Analyze cluster properties and add trading insights"""
        analyzed_clusters = []
        
        for cluster in clusters:
            try:
                # Add analysis data
                analyzed_cluster = cluster.copy()
                analyzed_cluster.update({
                    "symbol": symbol,
                    "strength": self._calculate_cluster_strength(cluster),
                    "price_level": self._estimate_price_level(cluster, symbol),
                    "volume": self._estimate_volume(cluster),
                    "analysis_timestamp": datetime.now().isoformat()
                })
                
                analyzed_clusters.append(analyzed_cluster)
                
            except Exception as e:
                logger.error(f"Error analyzing cluster {cluster['cluster_id']}: {e}")
        
        # Sort by confidence (highest first)
        analyzed_clusters.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        logger.info(f"📊 Analyzed {len(analyzed_clusters)} clusters")
        return analyzed_clusters
    
    def _calculate_cluster_strength(self, cluster: Dict[str, Any]) -> float:
        """Calculate cluster strength based on area and confidence"""
        area_score = min(cluster["area"] / 5000.0, 1.0)  # Normalize area
        confidence_score = cluster.get("confidence", 0.5)
        
        # Weighted average
        strength = (area_score * 0.6) + (confidence_score * 0.4)
        return round(strength, 3)
    
    def _estimate_price_level(self, cluster: Dict[str, Any], symbol: str) -> float:
        """Estimate price level for cluster (placeholder implementation)"""
        # In real implementation, this would use chart analysis to map pixel positions to price levels
        # For now, return a placeholder based on cluster position
        y_position = cluster["center"]["y"]
        
        # Simulate price mapping (this would be much more sophisticated in reality)
        if symbol and symbol.endswith("USDT"):
            # Example: BTC price range simulation
            if "BTC" in symbol:
                price_range = (90000, 110000)  # Example BTC range
            elif "ETH" in symbol:
                price_range = (3000, 4000)     # Example ETH range
            else:
                price_range = (1, 100)         # Generic range
            
            # Map Y position to price (top = higher price)
            normalized_y = 1.0 - (y_position / 1000.0)  # Assuming 1000px height
            price = price_range[0] + (price_range[1] - price_range[0]) * normalized_y
            
            return round(price, 2)
        
        return 0.0
    
    def _estimate_volume(self, cluster: Dict[str, Any]) -> float:
        """Estimate liquidation volume for cluster"""
        # Volume estimation based on cluster area and position
        area = cluster["area"]
        confidence = cluster.get("confidence", 0.5)
        
        # Simple volume estimation (would be more sophisticated in reality)
        volume = area * confidence * 1000  # Scale factor
        
        return round(volume, 2)