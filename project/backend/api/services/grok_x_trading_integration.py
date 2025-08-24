#!/usr/bin/env python3
"""
Grok-X Trading Integration Service
Connects Grok-X signals with existing trading agents and signal center
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import sqlite3

from .grok_x_production_service import GrokXProductionService, GrokXSignal
from ..agents.orchestration.orchestration_agent import OrchestrationAgent
from ..services.signal_center import SignalCenterService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Enhanced trading signal with Grok-X integration"""
    id: str
    symbol: str
    action: str
    confidence: float
    sentiment: float
    risk_level: str
    entry_price_min: float
    entry_price_max: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: str
    source: str = "grok_x_module"
    status: str = "active"
    priority: str = "medium"  # low, medium, high
    execution_status: str = "pending"  # pending, executed, cancelled, failed

class GrokXTradingIntegration:
    """Trading integration service for Grok-X signals"""
    
    def __init__(self):
        """Initialize the trading integration service"""
        self.grok_service = GrokXProductionService()
        self.orchestration_agent = None
        self.signal_center = None
        self.monitoring_active = False
        self.monitored_symbols = []
        self.signal_threshold = 0.7  # Minimum confidence for auto-execution
        self.max_position_size = 1000  # Maximum position size in USDT
        
    async def initialize(self):
        """Initialize trading components"""
        try:
            # Initialize orchestration agent
            from ..agents.orchestration.orchestration_agent import OrchestrationAgent
            self.orchestration_agent = OrchestrationAgent()
            await self.orchestration_agent.start()
            
            # Initialize signal center
            self.signal_center = SignalCenterService()
            
            logger.info("✅ Grok-X Trading Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize trading integration: {e}")
            return False
    
    async def process_grok_signals(self, symbols: List[str]) -> List[TradingSignal]:
        """Process Grok-X signals and convert to trading signals"""
        
        try:
            # Run Grok-X analysis
            result = await self.grok_service.run_production_analysis(symbols)
            
            # Convert to trading signals
            trading_signals = []
            for signal_data in result['signals']:
                # Only process high-confidence signals
                if signal_data['confidence'] >= self.signal_threshold:
                    trading_signal = TradingSignal(
                        id=signal_data['id'],
                        symbol=signal_data['symbol'],
                        action=signal_data['action'],
                        confidence=signal_data['confidence'],
                        sentiment=signal_data['sentiment'],
                        risk_level=signal_data['risk_level'],
                        entry_price_min=signal_data['entry_price_min'],
                        entry_price_max=signal_data['entry_price_max'],
                        stop_loss=signal_data['stop_loss'],
                        take_profit=signal_data['take_profit'],
                        reasoning=signal_data['reasoning'],
                        timestamp=signal_data['timestamp'],
                        priority=self._calculate_priority(signal_data),
                        execution_status="pending"
                    )
                    trading_signals.append(trading_signal)
            
            logger.info(f"✅ Processed {len(trading_signals)} high-confidence signals")
            return trading_signals
            
        except Exception as e:
            logger.error(f"❌ Failed to process Grok-X signals: {e}")
            return []
    
    def _calculate_priority(self, signal: Dict[str, Any]) -> str:
        """Calculate signal priority based on confidence and sentiment"""
        
        confidence = signal['confidence']
        sentiment = abs(signal['sentiment'])
        
        # High priority: High confidence + strong sentiment
        if confidence >= 0.85 and sentiment >= 0.7:
            return "high"
        
        # Medium priority: Good confidence + moderate sentiment
        elif confidence >= 0.75 and sentiment >= 0.5:
            return "medium"
        
        # Low priority: Lower confidence or weak sentiment
        else:
            return "low"
    
    async def execute_trading_signal(self, signal: TradingSignal) -> Dict[str, Any]:
        """Execute a trading signal through the orchestration agent"""
        
        try:
            if not self.orchestration_agent:
                raise RuntimeError("Orchestration agent not initialized")
            
            # Prepare trade parameters
            trade_params = {
                "symbol": signal.symbol,
                "side": signal.action.lower(),
                "order_type": "MARKET",
                "quantity": self._calculate_position_size(signal),
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "reasoning": signal.reasoning,
                "source": "grok_x_module",
                "confidence": signal.confidence,
                "sentiment": signal.sentiment
            }
            
            # Execute trade through orchestration agent
            result = await self.orchestration_agent.execute_trade(trade_params)
            
            # Update signal status
            signal.execution_status = "executed" if result.get("success") else "failed"
            
            logger.info(f"✅ Executed trade for {signal.symbol}: {signal.action}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to execute trading signal: {e}")
            signal.execution_status = "failed"
            return {"success": False, "error": str(e)}
    
    def _calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate position size based on confidence and risk level"""
        
        base_size = self.max_position_size
        
        # Adjust based on confidence
        confidence_multiplier = signal.confidence
        
        # Adjust based on risk level
        risk_multiplier = {
            "LOW": 1.0,
            "MEDIUM": 0.7,
            "HIGH": 0.4
        }.get(signal.risk_level, 0.7)
        
        # Calculate final position size
        position_size = base_size * confidence_multiplier * risk_multiplier
        
        # Ensure minimum and maximum limits
        position_size = max(100, min(position_size, self.max_position_size))
        
        return position_size
    
    async def auto_execute_signals(self, signals: List[TradingSignal]) -> Dict[str, Any]:
        """Automatically execute high-priority signals"""
        
        executed_count = 0
        failed_count = 0
        results = []
        
        for signal in signals:
            # Only auto-execute high priority signals
            if signal.priority == "high" and signal.confidence >= 0.85:
                try:
                    result = await self.execute_trading_signal(signal)
                    results.append({
                        "signal_id": signal.id,
                        "symbol": signal.symbol,
                        "action": signal.action,
                        "status": signal.execution_status,
                        "result": result
                    })
                    
                    if signal.execution_status == "executed":
                        executed_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Auto-execution failed for {signal.symbol}: {e}")
                    failed_count += 1
                    results.append({
                        "signal_id": signal.id,
                        "symbol": signal.symbol,
                        "action": signal.action,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return {
            "executed_count": executed_count,
            "failed_count": failed_count,
            "total_signals": len(signals),
            "results": results
        }
    
    async def integrate_with_signal_center(self, signals: List[TradingSignal]):
        """Integrate signals with the signal center"""
        
        try:
            if not self.signal_center:
                logger.warning("Signal center not initialized")
                return
            
            for signal in signals:
                # Convert to signal center format
                signal_data = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "type": signal.action,
                    "confidence": signal.confidence,
                    "source": signal.source,
                    "timestamp": signal.timestamp,
                    "metadata": {
                        "sentiment": signal.sentiment,
                        "risk_level": signal.risk_level,
                        "entry_price_min": signal.entry_price_min,
                        "entry_price_max": signal.entry_price_max,
                        "stop_loss": signal.stop_loss,
                        "take_profit": signal.take_profit,
                        "reasoning": signal.reasoning,
                        "priority": signal.priority
                    }
                }
                
                # Add to signal center
                await self.signal_center.ingest_signal(signal_data)
            
            logger.info(f"✅ Integrated {len(signals)} signals with signal center")
            
        except Exception as e:
            logger.error(f"❌ Failed to integrate with signal center: {e}")
    
    async def start_monitoring(self, symbols: List[str], interval_minutes: int = 30):
        """Start continuous monitoring and trading"""
        
        self.monitored_symbols = symbols
        self.monitoring_active = True
        
        logger.info(f"🔄 Starting Grok-X trading monitoring for: {symbols}")
        
        while self.monitoring_active:
            try:
                # Process signals
                signals = await self.process_grok_signals(symbols)
                
                if signals:
                    # Integrate with signal center
                    await self.integrate_with_signal_center(signals)
                    
                    # Auto-execute high-priority signals
                    execution_results = await self.auto_execute_signals(signals)
                    
                    logger.info(f"📊 Monitoring cycle completed:")
                    logger.info(f"   Signals processed: {len(signals)}")
                    logger.info(f"   Executed: {execution_results['executed_count']}")
                    logger.info(f"   Failed: {execution_results['failed_count']}")
                
                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"❌ Monitoring cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        
        self.monitoring_active = False
        logger.info("🛑 Grok-X trading monitoring stopped")
    
    async def get_trading_metrics(self) -> Dict[str, Any]:
        """Get trading performance metrics"""
        
        try:
            # Get signal statistics from database
            conn = sqlite3.connect(self.grok_service.db_path)
            cursor = conn.cursor()
            
            # Get executed signals
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_executed,
                    COUNT(CASE WHEN action = 'BUY' THEN 1 END) as buy_executed,
                    COUNT(CASE WHEN action = 'SELL' THEN 1 END) as sell_executed,
                    AVG(confidence) as avg_confidence,
                    AVG(sentiment) as avg_sentiment
                FROM grok_x_signals 
                WHERE status = 'executed'
            """)
            
            executed_stats = cursor.fetchone()
            
            # Get pending signals
            cursor.execute("""
                SELECT COUNT(*) as total_pending
                FROM grok_x_signals 
                WHERE status = 'pending'
            """)
            
            pending_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "executed_signals": {
                    "total": executed_stats[0],
                    "buy_signals": executed_stats[1],
                    "sell_signals": executed_stats[2],
                    "avg_confidence": executed_stats[3],
                    "avg_sentiment": executed_stats[4]
                },
                "pending_signals": pending_count,
                "monitoring_status": {
                    "active": self.monitoring_active,
                    "monitored_symbols": self.monitored_symbols
                },
                "settings": {
                    "signal_threshold": self.signal_threshold,
                    "max_position_size": self.max_position_size
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get trading metrics: {e}")
            return {}
    
    async def update_trading_settings(self, settings: Dict[str, Any]):
        """Update trading settings"""
        
        if "signal_threshold" in settings:
            self.signal_threshold = settings["signal_threshold"]
        
        if "max_position_size" in settings:
            self.max_position_size = settings["max_position_size"]
        
        logger.info(f"✅ Trading settings updated: {settings}")

# Example usage
async def main():
    """Example usage of the trading integration"""
    
    integration = GrokXTradingIntegration()
    
    # Initialize
    success = await integration.initialize()
    if not success:
        print("❌ Failed to initialize trading integration")
        return
    
    # Test symbols
    symbols = ['BTC', 'ETH', 'SOL']
    
    # Process signals
    signals = await integration.process_grok_signals(symbols)
    
    print(f"📊 Generated {len(signals)} trading signals")
    
    for signal in signals:
        print(f"   📈 {signal.symbol}: {signal.action} (Confidence: {signal.confidence:.3f}, Priority: {signal.priority})")
    
    # Get metrics
    metrics = await integration.get_trading_metrics()
    print(f"📊 Trading Metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main()) 