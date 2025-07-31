#!/usr/bin/env python3
"""
Enhanced Workflow Service for KingFisher
Integrates Master Agent for comprehensive analysis and Airtable updates
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .master_agent import MasterAgent, MasterReport  # type: ignore
from .enhanced_airtable_service import EnhancedAirtableService  # type: ignore
from .market_data_service import MarketDataService  # type: ignore
from .image_processing_service import ImageProcessingService  # type: ignore

logger = logging.getLogger(__name__)

class EnhancedWorkflowService:
    """Enhanced workflow service with Master Agent integration"""
    
    def __init__(self):
        self.master_agent = MasterAgent()
        self.airtable_service = EnhancedAirtableService()
        self.market_data_service = MarketDataService()
        self.image_processing_service = ImageProcessingService()
    
    async def process_telegram_image(self, symbol: str, image_data: bytes, 
                                   image_type: str, caption: str = "") -> Dict[str, Any]:
        """Process Telegram image with Master Agent orchestration"""
        
        logger.info(f"🚀 Enhanced Workflow: Processing {symbol} image ({image_type})")
        
        try:
            # 1. Get real-time market data
            market_data = await self._get_market_data(symbol)
            
            # 2. Analyze image by type
            image_analysis = await self._analyze_image_by_type(image_data, image_type)
            
            # 3. Collect data from all 5 agents via Master Agent
            agent_results = await self.master_agent.collect_agent_data(
                symbol=symbol,
                image_data=image_data,
                image_type=image_type,
                market_data=market_data
            )
            
            # 4. Create comprehensive Master Report
            master_report = await self.master_agent.create_master_report(symbol, agent_results)
            
            # 5. Update Airtable with Master Agent results
            airtable_result = await self._update_airtable_with_master_report(symbol, master_report, image_type)
            
            # 6. Calculate timeframe win rates
            timeframe_rates = self._calculate_timeframe_win_rates(master_report)
            
            # 7. Update timeframe fields in Airtable
            await self._update_timeframe_fields(symbol, timeframe_rates)
            
            # 8. Update liquidation clusters
            await self._update_liquidation_clusters(symbol, master_report.liquidation_clusters)
            
            logger.info(f"✅ Enhanced Workflow: Successfully processed {symbol}")
            
            return {
                "status": "success",
                "symbol": symbol,
                "master_report": master_report,
                "airtable_updated": airtable_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced Workflow Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data"""
        try:
            market_data = await self.market_data_service.get_real_time_price(symbol)
            # Convert MarketData object to dict if needed
            if hasattr(market_data, '__dict__'):
                return market_data.__dict__
            elif isinstance(market_data, dict):
                return market_data
            else:
                # Convert to dict with basic fields
                return {
                    "price": getattr(market_data, 'price', 0.0),
                    "change_24h": getattr(market_data, 'change_24h', 0.0),
                    "volume": getattr(market_data, 'volume', 0.0),
                    "market_cap": getattr(market_data, 'market_cap', 0.0),
                    "volatility": getattr(market_data, 'volatility', 0.0)
                }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {
                "price": 0.0,
                "change_24h": 0.0,
                "volume": 0.0,
                "market_cap": 0.0,
                "volatility": 0.0
            }
    
    async def _analyze_image_by_type(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze image based on type"""
        try:
            if image_type == "liquidation_heatmap":
                return await self.image_processing_service.analyze_liquidation_heatmap(image_data)
            elif image_type == "liquidation_map":
                return await self.image_processing_service.analyze_liquidation_map(image_data)
            elif image_type == "multi_symbol":
                return await self.image_processing_service.analyze_multi_symbol_image(image_data)
            else:
                return await self.image_processing_service.analyze_general_image(image_data)
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": str(e)}
    
    async def _update_airtable_with_master_report(self, symbol: str, master_report: MasterReport, 
                                                image_type: str) -> Dict[str, Any]:
        """Update Airtable with Master Agent report"""
        try:
            # Prepare record data based on image type
            record_data = {
                "Symbol": symbol,
                "MarketPrice": master_report.current_price
            }
            
            # Add image-specific analysis
            if image_type == "liquidation_heatmap":
                record_data["Liq_Heatmap"] = master_report.detailed_analysis
            elif image_type == "liquidation_map":
                record_data["Liquidation_Map"] = master_report.professional_summary
            else:
                # For other image types, use the professional summary
                record_data["Liquidation_Map"] = master_report.professional_summary
            
            # Create or update the record
            result = await self.airtable_service.create_or_update_symbol_record(symbol, record_data)
            
            logger.info(f"✅ Airtable updated for {symbol}: {result}")
            return {"status": "success", "result": result} if result else {"status": "error", "result": None}
            
        except Exception as e:
            logger.error(f"Error updating Airtable for {symbol}: {e}")
            return {"error": str(e)}
    
    def _calculate_timeframe_win_rates(self, master_report: MasterReport) -> Dict[str, str]:
        """Calculate timeframe win rates from Master Agent data"""
        timeframe_scores = master_report.timeframe_scores
        
        # Convert scores to win rate format "Long X%,Short Y%"
        win_rates = {}
        
        for timeframe, score in timeframe_scores.items():
            # Calculate complementary rates (if long is 80%, short is 20%)
            long_rate = score
            short_rate = 100 - score
            
            # Ensure rates are within 0-100 range
            long_rate = max(0, min(100, long_rate))
            short_rate = max(0, min(100, short_rate))
            
            win_rates[timeframe] = f"Long {long_rate}%,Short {short_rate}%"
        
        return win_rates
    
    async def _update_timeframe_fields(self, symbol: str, timeframe_rates: Dict[str, str]) -> None:
        """Update timeframe fields in Airtable"""
        try:
            # Map timeframe keys to Airtable field names
            field_mapping = {
                "24h": "24h48h",  # Combined field for 24h and 48h
                "48h": "24h48h",  # Combined field for 24h and 48h
                "7d": "7days",
                "1M": "1Month"
            }
            
            for timeframe, rate in timeframe_rates.items():
                if timeframe in field_mapping:
                    airtable_field = field_mapping[timeframe]
                    await self.airtable_service.update_timeframe_win_rates(symbol, {airtable_field: rate})
            
            logger.info(f"✅ Timeframe fields updated for {symbol}")
            
        except Exception as e:
            logger.error(f"Error updating timeframe fields for {symbol}: {e}")
    
    async def _update_liquidation_clusters(self, symbol: str, liquidation_clusters: Dict[str, Any]) -> None:
        """Update liquidation clusters in Airtable"""
        try:
            # Extract cluster prices
            cluster_data = {
                "Liqcluster1": int(liquidation_clusters.get("Liqcluster1", 0)),
                "Liqcluster2": int(liquidation_clusters.get("Liqcluster2", 0))
            }
            
            await self.airtable_service.update_liquidation_clusters(symbol, cluster_data)
            
            logger.info(f"✅ Liquidation clusters updated for {symbol}")
            
        except Exception as e:
            logger.error(f"Error updating liquidation clusters for {symbol}: {e}")
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow service status"""
        return {
            "status": "operational",
            "master_agent": "active",
            "airtable_service": "connected",
            "market_data_service": "connected",
            "image_processing_service": "active",
            "timestamp": datetime.now().isoformat()
        } 