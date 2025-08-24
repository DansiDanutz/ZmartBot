#!/usr/bin/env python3
"""
Airtable CursorTable Service
Stores complete professional reports in CryptoTrade base, CursorTable
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AirtableCursorService:
    """Service for storing professional reports in Airtable CursorTable"""
    
    def __init__(self):
        # CryptoTrade base configuration
        self.base_id = "appAs9sZH7OmtYaTJ"  # CryptoTrade base
        self.api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
        self.table_name = "CursorTable"  # Using CursorTable as specified
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def store_professional_report(self, report_data: Dict[str, Any]) -> bool:
        """Store complete professional trading report in CursorTable"""
        try:
            # Prepare the complete report record
            record = {
                "fields": {
                    # Basic Information
                    "Symbol": report_data.get("symbol", ""),
                    "Timestamp": report_data.get("timestamp", datetime.now().isoformat()),
                    "Current_Price": report_data.get("current_price", 0),
                    
                    # Win Rates - 24H
                    "WinRate_24H_Long": report_data.get("win_rate_24h_long", 0),
                    "WinRate_24H_Short": report_data.get("win_rate_24h_short", 0),
                    "Score_24H": report_data.get("score_24h", 0),
                    
                    # Win Rates - 7D
                    "WinRate_7D_Long": report_data.get("win_rate_7d_long", 0),
                    "WinRate_7D_Short": report_data.get("win_rate_7d_short", 0),
                    "Score_7D": report_data.get("score_7d", 0),
                    
                    # Win Rates - 1M
                    "WinRate_1M_Long": report_data.get("win_rate_1m_long", 0),
                    "WinRate_1M_Short": report_data.get("win_rate_1m_short", 0),
                    "Score_1M": report_data.get("score_1m", 0),
                    
                    # Technical Indicators
                    "LPI": report_data.get("lpi", 0),
                    "MBR": report_data.get("mbr", 0),
                    "PPI": report_data.get("ppi", 0),
                    
                    # Market Analysis
                    "Long_Concentration": report_data.get("long_concentration", 0),
                    "Short_Concentration": report_data.get("short_concentration", 0),
                    "Overall_Sentiment": report_data.get("overall_sentiment", ""),
                    "Overall_Confidence": report_data.get("overall_confidence", 0),
                    "Risk_Level": report_data.get("risk_level", ""),
                    
                    # Trading Recommendation
                    "Recommendation": report_data.get("recommendation", ""),
                    
                    # Support/Resistance Levels (as JSON)
                    "Support_Resistance": json.dumps(report_data.get("support_resistance", {})),
                    
                    # Liquidation Clusters (as JSON)
                    "Liquidation_Clusters": json.dumps(report_data.get("liquidation_clusters", {})),
                    
                    # Full Professional Report (Long Text)
                    "Professional_Report": report_data.get("professional_report", ""),
                    
                    # Report Metadata
                    "Report_Version": "2.0",
                    "Data_Quality": "Professional Grade",
                    "Analysis_Type": "KingFisher AI Trading Intelligence"
                }
            }
            
            # Create record in Airtable CursorTable
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json={"records": [record]}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Professional report stored for {report_data.get('symbol')} in CursorTable")
                    return True
                elif response.status_code == 422:
                    # Field doesn't exist, try with minimal fields
                    minimal_record = {
                        "fields": {
                            "Symbol": report_data.get("symbol", ""),
                            "Report": report_data.get("professional_report", "")[:100000],  # Truncate if needed
                            "Timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/{self.table_name}",
                        headers=self.headers,
                        json={"records": [minimal_record]}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Professional report stored (minimal) for {report_data.get('symbol')} in CursorTable")
                        return True
                    else:
                        logger.error(f"❌ Failed to store in CursorTable: {response.status_code} - {response.text}")
                        return False
                else:
                    logger.error(f"❌ Failed to store in CursorTable: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing professional report in CursorTable: {e}")
            return False
    
    async def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent professional reports from CursorTable"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={
                        "maxRecords": limit,
                        "sort[0][field]": "Timestamp",
                        "sort[0][direction]": "desc"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    reports = []
                    for record in records:
                        fields = record.get("fields", {})
                        reports.append({
                            "id": record.get("id"),
                            "symbol": fields.get("Symbol", ""),
                            "timestamp": fields.get("Timestamp", ""),
                            "current_price": fields.get("Current_Price", 0),
                            "win_rate_24h_long": fields.get("WinRate_24H_Long", 0),
                            "win_rate_24h_short": fields.get("WinRate_24H_Short", 0),
                            "win_rate_7d_long": fields.get("WinRate_7D_Long", 0),
                            "win_rate_7d_short": fields.get("WinRate_7D_Short", 0),
                            "win_rate_1m_long": fields.get("WinRate_1M_Long", 0),
                            "win_rate_1m_short": fields.get("WinRate_1M_Short", 0),
                            "sentiment": fields.get("Overall_Sentiment", ""),
                            "confidence": fields.get("Overall_Confidence", 0),
                            "risk_level": fields.get("Risk_Level", ""),
                            "recommendation": fields.get("Recommendation", ""),
                            "professional_report": fields.get("Professional_Report", "")
                        })
                    
                    logger.info(f"✅ Retrieved {len(reports)} reports from CursorTable")
                    return reports
                else:
                    logger.error(f"❌ Failed to get reports from CursorTable: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting reports from CursorTable: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Test connection to CursorTable"""
        try:
            async with httpx.AsyncClient() as client:
                # First try to get table schema
                response = await client.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={"maxRecords": 1}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Connected to CursorTable in CryptoTrade base")
                    
                    # Try to get fields from first record to understand structure
                    data = response.json()
                    records = data.get("records", [])
                    if records:
                        fields = records[0].get("fields", {})
                        field_names = list(fields.keys())
                        logger.info(f"Available fields in CursorTable: {field_names}")
                    
                    return True
                elif response.status_code == 404:
                    logger.error(f"❌ CursorTable not found in base {self.base_id}")
                    return False
                else:
                    logger.error(f"❌ Connection to CursorTable failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error testing CursorTable connection: {e}")
            return False
    
    async def create_table_if_needed(self) -> bool:
        """Create CursorTable if it doesn't exist (requires higher permissions)"""
        # Note: Creating tables via API requires enterprise plan
        # This is just a placeholder - table should be created manually in Airtable
        logger.info("CursorTable should be created manually in Airtable if it doesn't exist")
        logger.info("Required fields: Symbol, Report, Timestamp (minimum)")
        logger.info("Optional fields: All win rates, scores, indicators, etc.")
        return True

# Create global instance
airtable_cursor_service = AirtableCursorService()