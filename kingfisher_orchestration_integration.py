#!/usr/bin/env python3
"""
KingFisher Multi-Agent System Orchestration Integration
Integrates KingFisher system with main Zmart platform orchestration
"""
import asyncio
import logging
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """KingFisher event types"""
    KINGFISHER_IMAGE_RECEIVED = "kingfisher_image_received"
    KINGFISHER_ANALYSIS_COMPLETE = "kingfisher_analysis_complete"
    KINGFISHER_REPORT_GENERATED = "kingfisher_report_generated"
    KINGFISHER_MASTER_SUMMARY_READY = "kingfisher_master_summary_ready"
    KINGFISHER_PROFESSIONAL_REPORT_READY = "kingfisher_professional_report_ready"

@dataclass
class KingFisherEvent:
    """KingFisher event structure"""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "kingfisher"

class KingFisherOrchestrationIntegration:
    """Integration between KingFisher system and main Zmart platform"""
    
    def __init__(self):
        self.kingfisher_base_url = "http://localhost:8100"
        self.zmart_base_url = "http://localhost:8000"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Event handlers
        self.event_handlers = {
            EventType.KINGFISHER_IMAGE_RECEIVED: self.handle_image_received,
            EventType.KINGFISHER_ANALYSIS_COMPLETE: self.handle_analysis_complete,
            EventType.KINGFISHER_REPORT_GENERATED: self.handle_report_generated,
            EventType.KINGFISHER_MASTER_SUMMARY_READY: self.handle_master_summary_ready,
            EventType.KINGFISHER_PROFESSIONAL_REPORT_READY: self.handle_professional_report_ready
        }
        
        logger.info("KingFisher Orchestration Integration initialized")
    
    async def start(self):
        """Start the integration service"""
        logger.info("🚀 Starting KingFisher Orchestration Integration")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession()
        
        # Test connections
        await self.test_connections()
        
        # Start monitoring
        await self.start_monitoring()
        
        logger.info("✅ KingFisher Orchestration Integration started")
    
    async def stop(self):
        """Stop the integration service"""
        logger.info("🛑 Stopping KingFisher Orchestration Integration")
        
        if self.session:
            await self.session.close()
        
        logger.info("✅ KingFisher Orchestration Integration stopped")
    
    async def test_connections(self):
        """Test connections to both systems"""
        logger.info("🔍 Testing system connections...")
        
        if not self.session:
            logger.error("❌ Session not initialized")
            return
        
        # Test KingFisher connection
        try:
            async with self.session.get(f"{self.kingfisher_base_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ KingFisher system connection successful")
                else:
                    logger.warning(f"⚠️ KingFisher system connection failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ KingFisher system connection error: {e}")
        
        # Test Zmart platform connection
        try:
            async with self.session.get(f"{self.zmart_base_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ Zmart platform connection successful")
                else:
                    logger.warning(f"⚠️ Zmart platform connection failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Zmart platform connection error: {e}")
    
    async def start_monitoring(self):
        """Start monitoring KingFisher events"""
        logger.info("📡 Starting KingFisher event monitoring")
        
        if not self.session:
            logger.error("❌ Session not initialized")
            return
        
        # Start real-time monitoring
        try:
            async with self.session.post(f"{self.kingfisher_base_url}/api/v1/realtime/start-monitoring") as response:
                if response.status == 200:
                    logger.info("✅ KingFisher real-time monitoring started")
                else:
                    logger.warning(f"⚠️ Failed to start KingFisher monitoring: {response.status}")
        except Exception as e:
            logger.error(f"❌ Error starting KingFisher monitoring: {e}")
    
    async def process_kingfisher_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process KingFisher image through complete workflow"""
        logger.info("🖼️ Processing KingFisher image through complete workflow")
        
        if not self.session:
            logger.error("❌ Session not initialized")
            return {"error": "Session not initialized"}
        
        try:
            # Execute complete workflow
            async with self.session.post(
                f"{self.kingfisher_base_url}/api/v1/complete-workflow/process-complete-workflow",
                json=image_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ KingFisher workflow completed successfully")
                    
                    # Trigger event
                    await self.trigger_event(EventType.KINGFISHER_ANALYSIS_COMPLETE, result)
                    
                    return result
                else:
                    logger.error(f"❌ KingFisher workflow failed: {response.status}")
                    return {"error": f"Workflow failed: {response.status}"}
        except Exception as e:
            logger.error(f"❌ Error processing KingFisher image: {e}")
            return {"error": str(e)}
    
    async def generate_professional_report(self, symbol: str, analysis_type: str) -> Dict[str, Any]:
        """Generate professional report for symbol"""
        logger.info(f"📊 Generating professional report for {symbol}")
        
        try:
            # Add job to automated report system
            job_data = {
                "symbol": symbol,
                "analysis_type": analysis_type,
                "priority": 1
            }
            
            async with self.session.post(
                f"{self.kingfisher_base_url}/api/v1/automated-reports/add-job",
                json=job_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Professional report job added successfully")
                    
                    # Trigger event
                    await self.trigger_event(EventType.KINGFISHER_PROFESSIONAL_REPORT_READY, result)
                    
                    return result
                else:
                    logger.error(f"❌ Failed to add report job: {response.status}")
                    return {"error": f"Job addition failed: {response.status}"}
        except Exception as e:
            logger.error(f"❌ Error generating professional report: {e}")
            return {"error": str(e)}
    
    async def generate_master_summary(self) -> Dict[str, Any]:
        """Generate master summary from all analyses"""
        logger.info("🎯 Generating master summary")
        
        try:
            async with self.session.post(
                f"{self.kingfisher_base_url}/api/v1/master-summary/generate"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Master summary generated successfully")
                    
                    # Trigger event
                    await self.trigger_event(EventType.KINGFISHER_MASTER_SUMMARY_READY, result)
                    
                    return result
                else:
                    logger.error(f"❌ Failed to generate master summary: {response.status}")
                    return {"error": f"Master summary generation failed: {response.status}"}
        except Exception as e:
            logger.error(f"❌ Error generating master summary: {e}")
            return {"error": str(e)}
    
    async def trigger_event(self, event_type: EventType, data: Dict[str, Any]):
        """Trigger event for orchestration"""
        event = KingFisherEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data
        )
        
        # Call appropriate handler
        handler = self.event_handlers.get(event_type)
        if handler:
            await handler(event)
        else:
            logger.warning(f"⚠️ No handler found for event type: {event_type}")
    
    async def handle_image_received(self, event: KingFisherEvent):
        """Handle new KingFisher image"""
        logger.info("📱 Handling new KingFisher image")
        
        # Process image through workflow
        result = await self.process_kingfisher_image(event.data)
        
        # Update Zmart platform with new data
        await self.update_zmart_platform(event.data, result)
    
    async def handle_analysis_complete(self, event: KingFisherEvent):
        """Handle completed analysis"""
        logger.info("📊 Handling completed KingFisher analysis")
        
        # Extract trading signals
        signals = self.extract_trading_signals(event.data)
        
        # Update Zmart trading signals
        await self.update_trading_signals(signals)
    
    async def handle_report_generated(self, event: KingFisherEvent):
        """Handle generated report"""
        logger.info("📝 Handling generated KingFisher report")
        
        # Store professional documentation
        await self.store_professional_documentation(event.data)
    
    async def handle_master_summary_ready(self, event: KingFisherEvent):
        """Handle master summary"""
        logger.info("🎯 Handling KingFisher master summary")
        
        # Update market overview
        await self.update_market_overview(event.data)
    
    async def handle_professional_report_ready(self, event: KingFisherEvent):
        """Handle professional report"""
        logger.info("📊 Handling KingFisher professional report")
        
        # Store commercial documentation
        await self.store_commercial_documentation(event.data)
    
    def extract_trading_signals(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract trading signals from analysis data"""
        signals = []
        
        try:
            # Extract symbol and sentiment
            symbol = analysis_data.get('symbol', '')
            sentiment = analysis_data.get('sentiment', 'neutral')
            confidence = analysis_data.get('confidence', 0.0)
            
            if symbol and confidence > 70.0:
                signal = {
                    'symbol': symbol,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'source': 'kingfisher',
                    'timestamp': datetime.utcnow().isoformat(),
                    'analysis_type': analysis_data.get('analysis_type', 'unknown')
                }
                signals.append(signal)
                
                logger.info(f"📈 Extracted trading signal: {symbol} - {sentiment} ({confidence}%)")
        
        except Exception as e:
            logger.error(f"❌ Error extracting trading signals: {e}")
        
        return signals
    
    async def update_zmart_platform(self, image_data: Dict[str, Any], analysis_result: Dict[str, Any]):
        """Update Zmart platform with KingFisher data"""
        logger.info("🔄 Updating Zmart platform with KingFisher data")
        
        try:
            # Prepare update data
            update_data = {
                'source': 'kingfisher',
                'image_data': image_data,
                'analysis_result': analysis_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to Zmart platform
            async with self.session.post(
                f"{self.zmart_base_url}/api/v1/agents/kingfisher-update",
                json=update_data
            ) as response:
                if response.status == 200:
                    logger.info("✅ Zmart platform updated successfully")
                else:
                    logger.warning(f"⚠️ Failed to update Zmart platform: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error updating Zmart platform: {e}")
    
    async def update_trading_signals(self, signals: List[Dict[str, Any]]):
        """Update trading signals in Zmart platform"""
        logger.info(f"📈 Updating {len(signals)} trading signals")
        
        try:
            for signal in signals:
                async with self.session.post(
                    f"{self.zmart_base_url}/api/v1/signals/kingfisher",
                    json=signal
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Trading signal updated: {signal['symbol']}")
                    else:
                        logger.warning(f"⚠️ Failed to update trading signal: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error updating trading signals: {e}")
    
    async def store_professional_documentation(self, report_data: Dict[str, Any]):
        """Store professional documentation"""
        logger.info("📚 Storing professional documentation")
        
        try:
            # Store in documentation system
            async with self.session.post(
                f"{self.zmart_base_url}/api/v1/analytics/kingfisher-documentation",
                json=report_data
            ) as response:
                if response.status == 200:
                    logger.info("✅ Professional documentation stored successfully")
                else:
                    logger.warning(f"⚠️ Failed to store documentation: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error storing professional documentation: {e}")
    
    async def update_market_overview(self, summary_data: Dict[str, Any]):
        """Update market overview with master summary"""
        logger.info("📊 Updating market overview")
        
        try:
            # Update market overview
            async with self.session.post(
                f"{self.zmart_base_url}/api/v1/analytics/market-overview",
                json=summary_data
            ) as response:
                if response.status == 200:
                    logger.info("✅ Market overview updated successfully")
                else:
                    logger.warning(f"⚠️ Failed to update market overview: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error updating market overview: {e}")
    
    async def store_commercial_documentation(self, report_data: Dict[str, Any]):
        """Store commercial documentation"""
        logger.info("💼 Storing commercial documentation")
        
        try:
            # Store in commercial documentation system
            async with self.session.post(
                f"{self.zmart_base_url}/api/v1/analytics/commercial-documentation",
                json=report_data
            ) as response:
                if response.status == 200:
                    logger.info("✅ Commercial documentation stored successfully")
                else:
                    logger.warning(f"⚠️ Failed to store commercial documentation: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error storing commercial documentation: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get integration system status"""
        logger.info("📊 Getting system status")
        
        status = {
            'kingfisher_connected': False,
            'zmart_connected': False,
            'monitoring_active': False,
            'last_event': None,
            'total_events': 0
        }
        
        try:
            # Check KingFisher status
            async with self.session.get(f"{self.kingfisher_base_url}/health") as response:
                status['kingfisher_connected'] = response.status == 200
            
            # Check Zmart status
            async with self.session.get(f"{self.zmart_base_url}/health") as response:
                status['zmart_connected'] = response.status == 200
            
            # Check monitoring status
            async with self.session.get(f"{self.kingfisher_base_url}/api/v1/realtime/statistics") as response:
                if response.status == 200:
                    stats = await response.json()
                    status['monitoring_active'] = stats.get('monitoring_active', False)
            
            logger.info("✅ System status retrieved successfully")
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {e}")
        
        return status

async def main():
    """Main function to run the integration"""
    logger.info("🚀 Starting KingFisher Orchestration Integration")
    
    integration = KingFisherOrchestrationIntegration()
    
    try:
        # Start integration
        await integration.start()
        
        # Keep running
        while True:
            await asyncio.sleep(30)
            
            # Check system status
            status = await integration.get_system_status()
            logger.info(f"📊 System Status: {status}")
    
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Integration error: {e}")
    finally:
        # Stop integration
        await integration.stop()
        logger.info("✅ KingFisher Orchestration Integration stopped")

if __name__ == "__main__":
    asyncio.run(main()) 