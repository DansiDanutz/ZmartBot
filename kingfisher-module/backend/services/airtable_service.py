#!/usr/bin/env python3
"""
Airtable Service for KingFisher Analysis
Stores analysis data in CryptoTrade base
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

class AirtableService:
    """Service for storing KingFisher analysis data in Airtable"""
    
    def __init__(self):
        self.base_id = "appAs9sZH7OmtYaTJ"
        self.api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
        self.table_name = "CursorTable"
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def store_image_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Store image analysis in Airtable"""
        try:
            # Prepare record data
            record = {
                "fields": {
                    "Image ID": analysis_data.get("image_id", ""),
                    "Symbol": analysis_data.get("symbol", ""),
                    "Timestamp": analysis_data.get("timestamp", ""),
                    "Significance Score": analysis_data.get("significance_score", 0),
                    "Market Sentiment": analysis_data.get("market_sentiment", ""),
                    "Confidence": analysis_data.get("confidence", 0),
                    "Liquidation Clusters": json.dumps(analysis_data.get("liquidation_clusters", [])),
                    "Toxic Flow": analysis_data.get("toxic_flow", 0),
                    "Image Path": analysis_data.get("image_path", ""),
                    "Analysis Data": json.dumps(analysis_data.get("analysis_data", {})),
                    "Alert Level": self._get_alert_level(analysis_data.get("significance_score", 0)),
                    "Status": "Active"
                }
            }
            
            # Create record in Airtable
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json={"records": [record]}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Stored analysis for {analysis_data.get('symbol')} in Airtable")
                    return True
                else:
                    logger.error(f"❌ Failed to store in Airtable: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing analysis in Airtable: {e}")
            return False
    
    async def store_symbol_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Store symbol summary in Airtable"""
        try:
            # Prepare record data
            record = {
                "fields": {
                    "Symbol": summary_data.get("symbol", ""),
                    "Last Update": summary_data.get("last_update", ""),
                    "Total Images": summary_data.get("total_images", 0),
                    "Average Significance": summary_data.get("average_significance", 0),
                    "Dominant Sentiment": summary_data.get("dominant_sentiment", ""),
                    "High Significance Count": summary_data.get("high_significance_count", 0),
                    "Recent Trend": summary_data.get("recent_trend", ""),
                    "Risk Level": summary_data.get("risk_level", ""),
                    "Latest Analysis ID": summary_data.get("latest_analysis_id", ""),
                    "Status": "Active"
                }
            }
            
            # Create or update record in Airtable
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json={"records": [record]}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Stored summary for {summary_data.get('symbol')} in Airtable")
                    return True
                else:
                    logger.error(f"❌ Failed to store summary in Airtable: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing summary in Airtable: {e}")
            return False
    
    async def store_high_significance_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Store high significance alert in Airtable"""
        try:
            # Prepare record data
            record = {
                "fields": {
                    "Alert Type": "High Significance",
                    "Symbol": alert_data.get("symbol", ""),
                    "Significance Score": alert_data.get("significance_score", 0),
                    "Market Sentiment": alert_data.get("market_sentiment", ""),
                    "Confidence": alert_data.get("confidence", 0),
                    "Liquidation Clusters": json.dumps(alert_data.get("liquidation_clusters", [])),
                    "Toxic Flow": alert_data.get("toxic_flow", 0),
                    "Alert Level": alert_data.get("alert_level", ""),
                    "Timestamp": alert_data.get("timestamp", ""),
                    "Status": "Active"
                }
            }
            
            # Create record in Airtable
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json={"records": [record]}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Stored high significance alert for {alert_data.get('symbol')} in Airtable")
                    return True
                else:
                    logger.error(f"❌ Failed to store alert in Airtable: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing alert in Airtable: {e}")
            return False
    
    async def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analyses from Airtable"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={
                        "maxRecords": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    analyses = []
                    for record in records:
                        fields = record.get("fields", {})
                        if "Image ID" in fields:  # This is an analysis record
                            analyses.append({
                                "image_id": fields.get("Image ID", ""),
                                "symbol": fields.get("Symbol", ""),
                                "timestamp": fields.get("Timestamp", ""),
                                "significance_score": fields.get("Significance Score", 0),
                                "market_sentiment": fields.get("Market Sentiment", ""),
                                "confidence": fields.get("Confidence", 0),
                                "liquidation_clusters": json.loads(fields.get("Liquidation Clusters", "[]")),
                                "toxic_flow": fields.get("Toxic Flow", 0),
                                "image_path": fields.get("Image Path", ""),
                                "alert_level": fields.get("Alert Level", "")
                            })
                    
                    return analyses
                else:
                    logger.error(f"❌ Failed to get analyses from Airtable: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting analyses from Airtable: {e}")
            return []
    
    async def get_symbol_summaries(self) -> List[Dict[str, Any]]:
        """Get symbol summaries from Airtable"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={
                        "maxRecords": 100
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    summaries = []
                    for record in records:
                        fields = record.get("fields", {})
                        if "Symbol" in fields and "Total Images" in fields:  # This is a summary record
                            summaries.append({
                                "symbol": fields.get("Symbol", ""),
                                "last_update": fields.get("Last Update", ""),
                                "total_images": fields.get("Total Images", 0),
                                "average_significance": fields.get("Average Significance", 0),
                                "dominant_sentiment": fields.get("Dominant Sentiment", ""),
                                "high_significance_count": fields.get("High Significance Count", 0),
                                "recent_trend": fields.get("Recent Trend", ""),
                                "risk_level": fields.get("Risk Level", "")
                            })
                    
                    return summaries
                else:
                    logger.error(f"❌ Failed to get summaries from Airtable: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting summaries from Airtable: {e}")
            return []
    
    async def get_high_significance_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high significance alerts from Airtable"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={
                        "maxRecords": limit,
                        "filterByFormula": "{Alert Type} = 'High Significance'"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    alerts = []
                    for record in records:
                        fields = record.get("fields", {})
                        alerts.append({
                            "symbol": fields.get("Symbol", ""),
                            "significance_score": fields.get("Significance Score", 0),
                            "market_sentiment": fields.get("Market Sentiment", ""),
                            "confidence": fields.get("Confidence", 0),
                            "liquidation_clusters": json.loads(fields.get("Liquidation Clusters", "[]")),
                            "toxic_flow": fields.get("Toxic Flow", 0),
                            "alert_level": fields.get("Alert Level", ""),
                            "timestamp": fields.get("Timestamp", "")
                        })
                    
                    return alerts
                else:
                    logger.error(f"❌ Failed to get alerts from Airtable: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting alerts from Airtable: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Test Airtable connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={"maxRecords": 1}
                )
                
                if response.status_code == 200:
                    logger.info("✅ Airtable connection successful")
                    return True
                else:
                    logger.error(f"❌ Airtable connection failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error testing Airtable connection: {e}")
            return False
    
    def _get_alert_level(self, significance_score: float) -> str:
        """Determine alert level based on significance score"""
        if significance_score > 0.8:
            return "High"
        elif significance_score > 0.7:
            return "Medium"
        else:
            return "Low" 