#!/usr/bin/env python3
"""
Liquidation Service for KingFisher Module
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LiquidationService:
    """Service for analyzing liquidation data"""
    
    def __init__(self):
        self.is_ready_flag = True
        self.threshold = 0.7
        self.cluster_density_threshold = 0.5
        self.toxic_flow_threshold = 0.3
    
    async def analyze_liquidation_clusters(self, clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze liquidation clusters"""
        try:
            if not clusters:
                return {
                    "total_clusters": 0,
                    "average_density": 0.0,
                    "significance": 0.0,
                    "risk_level": "low"
                }
            
            # Calculate metrics
            total_clusters = len(clusters)
            total_area = sum(cluster.get("area", 0) for cluster in clusters)
            avg_density = sum(cluster.get("density", 0) for cluster in clusters) / total_clusters
            
            # Determine significance
            significance = min(avg_density * total_clusters * 0.1, 1.0)
            
            # Determine risk level
            if significance > 0.8:
                risk_level = "high"
            elif significance > 0.5:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "total_clusters": total_clusters,
                "total_area": total_area,
                "average_density": avg_density,
                "significance": significance,
                "risk_level": risk_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidation clusters: {e}")
            return {"error": str(e)}
    
    async def analyze_toxic_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze toxic flow data"""
        try:
            flow_percentage = flow_data.get("percentage", 0.0)
            flow_intensity = flow_data.get("intensity", 0.0)
            
            # Calculate significance
            significance = min(flow_percentage * flow_intensity, 1.0)
            
            # Determine sentiment
            if flow_percentage > 0.5:
                sentiment = "bullish"
            elif flow_percentage > 0.2:
                sentiment = "neutral"
            else:
                sentiment = "bearish"
            
            return {
                "flow_percentage": flow_percentage,
                "flow_intensity": flow_intensity,
                "significance": significance,
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing toxic flow: {e}")
            return {"error": str(e)}
    
    async def calculate_market_sentiment(self, cluster_analysis: Dict[str, Any], flow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall market sentiment"""
        try:
            cluster_significance = cluster_analysis.get("significance", 0.0)
            flow_significance = flow_analysis.get("significance", 0.0)
            flow_sentiment = flow_analysis.get("sentiment", "neutral")
            
            # Weighted sentiment calculation
            if cluster_significance > 0.7:
                sentiment = "bearish"
                confidence = cluster_significance
            elif flow_significance > 0.6:
                sentiment = flow_sentiment
                confidence = flow_significance
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            # Overall significance
            overall_significance = max(cluster_significance, flow_significance)
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "significance": overall_significance,
                "factors": {
                    "liquidation_clusters": cluster_significance,
                    "toxic_flow": flow_significance
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return {"error": str(e)}
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.is_ready_flag
    
    async def test_analysis(self) -> Dict[str, Any]:
        """Test liquidation analysis with sample data"""
        try:
            # Sample cluster data
            clusters = [
                {"area": 1500, "density": 0.8},
                {"area": 1000, "density": 0.6}
            ]
            
            # Sample flow data
            flow_data = {"percentage": 0.25, "intensity": 0.65}
            
            # Run analysis
            cluster_analysis = await self.analyze_liquidation_clusters(clusters)
            flow_analysis = await self.analyze_toxic_flow(flow_data)
            sentiment_analysis = await self.calculate_market_sentiment(cluster_analysis, flow_analysis)
            
            return {
                "cluster_analysis": cluster_analysis,
                "flow_analysis": flow_analysis,
                "sentiment_analysis": sentiment_analysis,
                "test_mode": True
            }
            
        except Exception as e:
            return {"error": f"Test analysis failed: {e}"} 