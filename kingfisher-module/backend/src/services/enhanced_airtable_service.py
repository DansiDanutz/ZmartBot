#!/usr/bin/env python3
"""
Enhanced Airtable Service for KingFisher
Handles specific Airtable fields and logic for finding/creating/updating records
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .airtable_service import AirtableService

logger = logging.getLogger(__name__)

class EnhancedAirtableService:
    """Enhanced Airtable service with specific field handling"""
    
    def __init__(self):
        self.airtable_service = AirtableService()
    
    async def create_or_update_symbol_record(self, symbol: str, record_data: Dict[str, Any]) -> Optional[str]:
        """Create or update symbol record in Airtable"""
        try:
            # Check if symbol exists
            existing_record = await self._find_symbol_record(symbol)
            
            if existing_record:
                # Update existing record
                logger.info(f"📝 Updating existing record for {symbol}")
                record_id = existing_record.get('id')
                if not record_id:
                    logger.error(f"No record ID found for {symbol}")
                    return None
                # Use direct HTTP update since AirtableService doesn't have update_record method
                success = await self._update_record_direct(record_id, record_data)
                return record_id if success else None
            else:
                # Create new record
                logger.info(f"🆕 Creating new record for {symbol}")
                success = await self._create_record_direct(record_data)
                return "new_record" if success else None
                
        except Exception as e:
            logger.error(f"Error creating/updating record for {symbol}: {e}")
            return None
    
    async def update_timeframe_win_rates(self, symbol: str, timeframe_data: Dict[str, str]) -> bool:
        """Update timeframe win rates for a symbol"""
        try:
            existing_record = await self._find_symbol_record(symbol)
            if not existing_record:
                logger.error(f"Symbol {symbol} not found for timeframe update")
                return False
            
            record_id = existing_record.get('id')
            if not record_id:
                logger.error(f"No record ID found for {symbol}")
                return False
            
            # Update timeframe fields
            update_data = {}
            for timeframe, rate in timeframe_data.items():
                if timeframe == "24h48h":
                    update_data["24h48h"] = rate
                elif timeframe == "7days":
                    update_data["7days"] = rate
                elif timeframe == "1Month":
                    update_data["1Month"] = rate
            
            if update_data:
                success = await self._update_record_direct(record_id, update_data)
                if success:
                    logger.info(f"✅ Timeframe win rates updated for {symbol}")
                    return True
                else:
                    logger.error(f"❌ Failed to update timeframe win rates for {symbol}")
                    return False
            else:
                logger.warning(f"No valid timeframe data to update for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating timeframe win rates for {symbol}: {e}")
            return False
    
    async def update_liquidation_clusters(self, symbol: str, cluster_data: Dict[str, Any]) -> bool:
        """Update liquidation clusters for a symbol"""
        try:
            existing_record = await self._find_symbol_record(symbol)
            if not existing_record:
                logger.error(f"Symbol {symbol} not found for cluster update")
                return False
            
            record_id = existing_record.get('id')
            if not record_id:
                logger.error(f"No record ID found for {symbol}")
                return False
            
            # Update cluster fields with correct field names
            update_data = {}
            
            # Left clusters (below current price) - Liqcluster-1, Liqcluster-2
            if "Liqcluster-1" in cluster_data:
                update_data["Liqcluster-1"] = int(cluster_data["Liqcluster-1"])
            if "Liqcluster-2" in cluster_data:
                update_data["Liqcluster-2"] = int(cluster_data["Liqcluster-2"])
            
            # Right clusters (above current price) - Liqcluster1, Liqcluster2
            if "Liqcluster1" in cluster_data:
                update_data["Liqcluster1"] = int(cluster_data["Liqcluster1"])
            if "Liqcluster2" in cluster_data:
                update_data["Liqcluster2"] = int(cluster_data["Liqcluster2"])
            
            if update_data:
                success = await self._update_record_direct(record_id, update_data)
                if success:
                    logger.info(f"✅ Liquidation clusters updated for {symbol}")
                    return True
                else:
                    logger.error(f"❌ Failed to update liquidation clusters for {symbol}")
                    return False
            else:
                logger.warning(f"No valid cluster data to update for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating liquidation clusters for {symbol}: {e}")
            return False
    
    async def get_symbol_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get complete analysis for a symbol"""
        try:
            record = await self._find_symbol_record(symbol)
            if not record:
                return None
            
            return {
                "symbol": symbol,
                "liquidation_map": record.get("Liquidation_Map", ""),
                "liq_heatmap": record.get("Liq_Heatmap", ""),
                "market_price": record.get("MarketPrice", 0.0),
                "timeframe_24h48h": record.get("24h48h", ""),
                "timeframe_7days": record.get("7days", ""),
                "timeframe_1Month": record.get("1Month", ""),
                "cluster_left_1": record.get("Liqcluster-1", 0),
                "cluster_left_2": record.get("Liqcluster-2", 0),
                "cluster_right_1": record.get("Liqcluster1", 0),
                "cluster_right_2": record.get("Liqcluster2", 0),
                "last_update": record.get("Last_Update", "")
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol analysis for {symbol}: {e}")
            return None
    
    async def get_all_symbols(self) -> List[str]:
        """Get all symbols from Airtable"""
        try:
            records = await self._get_all_records_direct()
            symbols = []
            
            for record in records:
                symbol = record.get("fields", {}).get("Symbol")
                if symbol:
                    symbols.append(symbol)
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting all symbols: {e}")
            return []
    
    async def delete_symbol_record(self, symbol: str) -> bool:
        """Delete symbol record from Airtable"""
        try:
            existing_record = await self._find_symbol_record(symbol)
            if not existing_record:
                logger.warning(f"Symbol {symbol} not found for deletion")
                return False
            
            record_id = existing_record.get('id')
            if not record_id:
                logger.error(f"No record ID found for {symbol}")
                return False
            
            # Use direct HTTP delete since AirtableService doesn't have delete_record method
            success = await self._delete_record_direct(record_id)
            
            if success:
                logger.info(f"✅ Deleted record for {symbol}")
            else:
                logger.error(f"❌ Failed to delete record for {symbol}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting record for {symbol}: {e}")
            return False
    
    async def _find_symbol_record(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Find symbol record in Airtable"""
        try:
            # Use direct HTTP request since AirtableService doesn't have get_all_records
            records = await self._get_all_records_direct()
            
            for record in records:
                if record.get("fields", {}).get("Symbol") == symbol:
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding symbol record for {symbol}: {e}")
            return None
    
    async def _create_record_direct(self, record_data: Dict[str, Any]) -> bool:
        """Create record directly via HTTP"""
        try:
            import httpx
            record = {"fields": record_data}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.airtable_service.base_url}/{self.airtable_service.table_name}",
                    headers=self.airtable_service.headers,
                    json={"records": [record]}
                )
                
                if response.status_code == 200:
                    logger.info("✅ Record created successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to create record: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating record: {e}")
            return False
    
    async def _update_record_direct(self, record_id: str, record_data: Dict[str, Any]) -> bool:
        """Update record directly via HTTP"""
        try:
            import httpx
            record = {"fields": record_data}
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.airtable_service.base_url}/{self.airtable_service.table_name}/{record_id}",
                    headers=self.airtable_service.headers,
                    json=record
                )
                
                if response.status_code == 200:
                    logger.info("✅ Record updated successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to update record: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            return False
    
    async def _get_all_records_direct(self) -> List[Dict[str, Any]]:
        """Get all records directly via HTTP"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.airtable_service.base_url}/{self.airtable_service.table_name}",
                    headers=self.airtable_service.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("records", [])
                else:
                    logger.error(f"❌ Failed to get records: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting records: {e}")
            return []
    
    async def _delete_record_direct(self, record_id: str) -> bool:
        """Delete record directly via HTTP"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.airtable_service.base_url}/{self.airtable_service.table_name}/{record_id}",
                    headers=self.airtable_service.headers
                )
                
                if response.status_code == 200:
                    logger.info("✅ Record deleted successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to delete record: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting record: {e}")
            return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            # Test connection
            records = await self._get_all_records_direct()
            
            return {
                "status": "connected",
                "table_name": self.airtable_service.table_name,
                "record_count": len(records),
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

# Create global instance
enhanced_airtable_service = EnhancedAirtableService() 