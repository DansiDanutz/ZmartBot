#!/usr/bin/env python3
"""
Enhanced Orchestration Agent with Signal Center Integration
Extends the base orchestration agent to work with Unified Signal Center
"""

import asyncio
import logging
from typing import Optional

from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.services.orchestration_signal_integration import signal_integration_service

logger = logging.getLogger(__name__)

class EnhancedOrchestrationAgent(OrchestrationAgent):
    """
    Enhanced orchestration agent that integrates with Unified Signal Center
    """
    
    def __init__(self):
        """Initialize enhanced orchestration agent"""
        super().__init__()
        
        # Signal integration service
        self.signal_integration = signal_integration_service
        self.signal_integration.orchestration_agent = self
        
        logger.info("Enhanced Orchestration Agent initialized with Signal Center integration")
    
    async def start(self):
        """Start the enhanced orchestration agent"""
        # Start base orchestration
        await super().start()
        
        # Start signal integration service
        await self.signal_integration.start()
        
        logger.info("Enhanced Orchestration Agent started with Signal Center monitoring")
    
    async def stop(self):
        """Stop the enhanced orchestration agent"""
        # Stop signal integration
        await self.signal_integration.stop()
        
        # Stop base orchestration
        await super().stop()
        
        logger.info("Enhanced Orchestration Agent stopped")
    
    async def process_signal(self, signal_data):
        """
        Override to add Signal Center specific processing
        
        Args:
            signal_data: Signal data from Unified Signal Center
        """
        # Log signal source
        if signal_data.get('source') == 'unified_signal_center':
            logger.info(f"Processing Unified Signal Center signal: {signal_data['symbol']} "
                       f"Score={signal_data['score']:.2f} Action={signal_data['action']}")
        
        # Call parent process_signal
        result = await super().process_signal(signal_data)
        
        # If signal is approved and has high score, consider for immediate execution
        if result.get('status') == 'queued' and signal_data.get('score', 0) > 80:
            logger.info(f"High score signal ({signal_data['score']:.2f}) - prioritizing execution")
            # Move to front of pending signals queue
            if self.pending_signals:
                # Find the signal and move it to front
                for i, sig in enumerate(self.pending_signals):
                    if sig.get('signal_id') == signal_data.get('signal_id'):
                        self.pending_signals.insert(0, self.pending_signals.pop(i))
                        break
        
        return result
    
    def get_integration_status(self):
        """Get Signal Center integration status"""
        return {
            "orchestration_status": self.get_system_status(),
            "signal_integration": self.signal_integration.get_status()
        }

# Create global enhanced instance
enhanced_orchestration_agent: Optional[EnhancedOrchestrationAgent] = None

async def get_enhanced_orchestration_agent() -> EnhancedOrchestrationAgent:
    """Get or create enhanced orchestration agent instance"""
    global enhanced_orchestration_agent
    if enhanced_orchestration_agent is None:
        enhanced_orchestration_agent = EnhancedOrchestrationAgent()
    return enhanced_orchestration_agent