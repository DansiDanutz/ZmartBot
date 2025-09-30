"""
RiskMetric Service - Complete Implementation with AI Win Rate Prediction
Based on Benjamin Cowen's methodology with 17 symbols
Extracted from Into The Cryptoverse platform

AI INTEGRATION:
- Uses AI models to predict win rates from Cowen methodology
- Multi-timeframe win rate predictions (24h, 7d, 1m)
- Converts risk bands to win rate percentages
- Provides detailed AI analysis reports
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from src.agents.database.riskmetric_database_agent import (
    ComprehensiveRiskMetricAgent, 
    RiskAssessment, 
    SymbolData
)
from src.utils.event_bus import EventBus, Event, EventType

# Import AI win rate predictor
from src.agents.scoring.ai_win_rate_predictor import (
    ai_predictor,
    AIModel,
    AIWinRatePrediction,
    MultiTimeframeAIPrediction
)

logger = logging.getLogger(__name__)

class RiskMetricService:
    """
    Complete RiskMetric Service based on Benjamin Cowen's methodology with AI integration
    
    Provides comprehensive risk assessment based on Benjamin Cowen's methodology:
    - Logarithmic regression analysis
    - Time-spent-in-risk-bands analysis
    - Manual update capabilities
    - Integration with scoring system
    - AI-Powered Win Rate Prediction
    """
    
    def __init__(self):
        """Initialize the RiskMetric Service"""
        self.service_id = "riskmetric_service"
        self.status = "stopped"
        self.event_bus = EventBus()
        self.ai_predictor = ai_predictor
        
        # Initialize the comprehensive database agent
        self.riskmetric_agent = ComprehensiveRiskMetricAgent()
        
        # Service state
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("RiskMetric Service with AI integration initialized")
    
    async def start(self):
        """Start the RiskMetric Service"""
        if self._running:
            logger.warning("RiskMetric Service is already running")
            return
        
        self._running = True
        self.status = "running"
        
        # Start the database agent
        await self.riskmetric_agent.start()
        
        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._service_monitoring_loop()),
            asyncio.create_task(self._integration_loop())
        ]
        
        logger.info("RiskMetric Service started")
    
    async def stop(self):
        """Stop the RiskMetric Service"""
        if not self._running:
            logger.warning("RiskMetric Service is not running")
            return
        
        self._running = False
        self.status = "stopped"
        
        # Stop the database agent
        await self.riskmetric_agent.stop()
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        
        logger.info("RiskMetric Service stopped")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get complete service status"""
        agent_status = await self.riskmetric_agent.get_status()
        
        return {
            "service_id": self.service_id,
            "status": self.status,
            "agent_status": agent_status,
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_all_symbols(self) -> List[str]:
        """Get list of all supported symbols"""
        return await self.riskmetric_agent.get_symbols()
    
    async def get_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get complete data for a specific symbol"""
        symbol_data = await self.riskmetric_agent.get_symbol_data(symbol)
        if symbol_data:
            return asdict(symbol_data)
        return None
    
    async def assess_risk(self, symbol: str, current_price: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Complete risk assessment for a symbol using Benjamin Cowen's methodology
        
        Returns comprehensive risk analysis including:
        - Current risk level
        - Trading signal
        - Risk band
        - Coefficient
        - Score for integration
        """
        assessment = await self.riskmetric_agent.assess_symbol(symbol, current_price)
        if assessment:
            return asdict(assessment)
        return None
    
    async def calculate_risk_from_price(self, symbol: str, price: float) -> Optional[float]:
        """Calculate risk level from price using Benjamin Cowen's methodology"""
        return self.riskmetric_agent.calculate_risk_from_price(symbol, price)
    
    async def calculate_price_from_risk(self, symbol: str, risk: float) -> Optional[float]:
        """Calculate price from risk level using Benjamin Cowen's methodology"""
        return self.riskmetric_agent.calculate_price_from_risk(symbol, risk)
    
    async def update_symbol_bounds(self, symbol: str, min_price: float, max_price: float, 
                                 reason: str = "Manual update") -> bool:
        """
        Update symbol bounds (for when Benjamin Cowen updates his models)
        
        This triggers automatic regeneration of all risk levels
        """
        success = await self.riskmetric_agent.update_symbol_bounds(symbol, min_price, max_price, reason)
        
        if success:
            # Emit bounds updated event
            event = Event(
                type=EventType.SIGNAL_PROCESSED,
                data={
                    "symbol": symbol.upper(),
                    "min_price": min_price,
                    "max_price": max_price,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(event)
        
        return success
    
    async def get_manual_updates(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get manual update history"""
        return await self.riskmetric_agent.get_manual_updates(symbol)
    
    async def get_comprehensive_screener(self) -> Dict[str, Any]:
        """
        Get comprehensive screener data for all symbols
        
        Returns complete risk assessment for all supported symbols
        """
        symbols = await self.riskmetric_agent.get_symbols()
        screener_data = {
            "total_symbols": len(symbols),
            "last_updated": datetime.now().isoformat(),
            "symbols": {}
        }
        
        for symbol in symbols:
            assessment = await self.assess_risk(symbol)
            if assessment:
                screener_data["symbols"][symbol] = assessment
        
        return screener_data
    
    async def get_portfolio_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get portfolio-level risk analysis
        
        Analyzes risk across multiple symbols for portfolio management
        """
        portfolio_data = {
            "total_symbols": len(symbols),
            "average_risk": 0.0,
            "highest_risk_symbol": None,
            "lowest_risk_symbol": None,
            "risk_distribution": {},
            "signals": {},
            "last_updated": datetime.now().isoformat()
        }
        
        total_risk = 0.0
        valid_assessments = 0
        risk_data = []
        
        for symbol in symbols:
            assessment = await self.assess_risk(symbol)
            if assessment:
                risk_data.append(assessment)
                total_risk += assessment["risk_value"]
                valid_assessments += 1
                
                # Track risk distribution
                risk_level = int(assessment["risk_value"] * 10) * 10
                portfolio_data["risk_distribution"][f"{risk_level}%"] = \
                    portfolio_data["risk_distribution"].get(f"{risk_level}%", 0) + 1
                
                # Track signals
                signal = assessment["signal"]
                portfolio_data["signals"][signal] = portfolio_data["signals"].get(signal, 0) + 1
        
        if valid_assessments > 0:
            portfolio_data["average_risk"] = total_risk / valid_assessments
            
            # Find highest and lowest risk symbols
            if risk_data:
                highest = max(risk_data, key=lambda x: x["risk_value"])
                lowest = min(risk_data, key=lambda x: x["risk_value"])
                
                portfolio_data["highest_risk_symbol"] = {
                    "symbol": highest["symbol"],
                    "risk": highest["risk_value"],
                    "signal": highest["signal"]
                }
                
                portfolio_data["lowest_risk_symbol"] = {
                    "symbol": lowest["symbol"],
                    "risk": lowest["risk_value"],
                    "signal": lowest["signal"]
                }
        
        return portfolio_data
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        agent_status = await self.riskmetric_agent.get_status()
        
        return {
            "service_id": self.service_id,
            "status": self.status,
            "symbols_count": agent_status["symbols_count"],
            "last_updated": datetime.now().isoformat(),
            "agent_status": agent_status
        }
    
    async def _service_monitoring_loop(self):
        """Background task for service monitoring"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Check service health
                await self._check_service_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in service monitoring loop: {e}")
    
    async def _integration_loop(self):
        """Background task for integration with other services"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Emit integration events
                await self._emit_integration_events()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
    
    async def _check_service_health(self):
        """Check service health and emit events"""
        try:
            # Check database agent health
            agent_status = await self.riskmetric_agent.get_status()
            
            if agent_status["status"] != "running":
                # Emit health warning
                health_event = Event(
                    type=EventType.SYSTEM_ERROR,
                    data={
                        "service": self.service_id,
                        "agent_status": agent_status["status"],
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.event_bus.emit(health_event)
            
        except Exception as e:
            logger.error(f"Error checking service health: {e}")
    
    async def _emit_integration_events(self):
        """Emit integration events for other services"""
        try:
            # Emit risk metrics for scoring system
            symbols = await self.riskmetric_agent.get_symbols()
            
            for symbol in symbols[:10]:  # Limit to first 10 symbols
                assessment = await self.assess_risk(symbol)
                if assessment:
                    risk_event = Event(
                        type=EventType.RISK_SCORE_UPDATED,
                        data={
                            "symbol": symbol,
                            "risk_score": assessment["risk_value"],
                            "signal": assessment["signal"],
                            "coefficient": assessment["coefficient"],
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    await self.event_bus.emit(risk_event)
            
        except Exception as e:
            logger.error(f"Error emitting integration events: {e}")
    
    # Integration with 25-point scoring system
    async def get_scoring_component(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get RiskMetric component for the 25-point scoring system
        
        RiskMetric contributes 5 points (20% weight) to the total score
        """
        assessment = await self.assess_risk(symbol)
        if not assessment:
            return None
        
        # Calculate RiskMetric score (0-5 points)
        risk_score = assessment["risk_value"]
        coefficient = assessment["coefficient"]
        
        # Base score calculation (lower risk = higher score)
        base_score = 5.0 * (1.0 - risk_score)
        
        # Coefficient adjustment
        coefficient_multiplier = coefficient / 1.6  # Normalize to 0-1
        adjusted_score = base_score * coefficient_multiplier
        
        return {
            "component": "RiskMetric",
            "symbol": symbol,
            "score": round(adjusted_score, 2),
            "max_score": 5.0,
            "weight": 0.2,  # 20% weight
            "risk_level": risk_score,
            "coefficient": coefficient,
            "signal": assessment["signal"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_all_scoring_components(self) -> Dict[str, Any]:
        """Get RiskMetric scoring components for all symbols"""
        symbols = await self.riskmetric_agent.get_symbols()
        components = {}
        
        for symbol in symbols:
            component = await self.get_scoring_component(symbol)
            if component:
                components[symbol] = component
        
        return {
            "service": "RiskMetric",
            "total_symbols": len(components),
            "components": components,
            "timestamp": datetime.now().isoformat()
        }

    async def get_manual_update_history(self, symbol: str) -> List[Dict[str, Any]]:
        """Get manual update history for a symbol (Cowen Guide requirement)"""
        try:
            # Query manual_overrides table directly
            import sqlite3
            conn = sqlite3.connect(self.riskmetric_agent.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT override_type, previous_value, override_value, override_reason, created_by, created_date
                FROM manual_overrides 
                WHERE symbol = ?
                ORDER BY created_date DESC
                LIMIT 50
            """, (symbol,))
            
            updates = []
            for row in cursor.fetchall():
                updates.append({
                    'override_type': row[0],
                    'old_value': row[1],
                    'new_value': row[2],
                    'reason': row[3],
                    'updated_by': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return updates
        except Exception as e:
            logger.error(f"Error getting manual update history for {symbol}: {str(e)}")
            return []
    
    async def get_regression_formulas(self, symbol: str) -> Dict[str, Any]:
        """Get regression formula constants for a symbol (Cowen Guide requirement)"""
        try:
            # Query regression_formulas table directly
            import sqlite3
            conn = sqlite3.connect(self.riskmetric_agent.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT formula_type, constant_a, constant_b, r_squared, created_date, last_fitted
                FROM regression_formulas 
                WHERE symbol = ?
            """, (symbol,))
            
            formulas = {}
            for row in cursor.fetchall():
                formulas[row[0]] = {
                    'constant_a': row[1],
                    'constant_b': row[2],
                    'r_squared': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            
            conn.close()
            return formulas
        except Exception as e:
            logger.error(f"Error getting regression formulas for {symbol}: {str(e)}")
            return {}

    # AI Integration Methods
    async def get_riskmetric_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get RiskMetric win rate prediction using AI analysis of Cowen methodology"""
        try:
            # Get risk assessment
            risk_assessment = await self.assess_risk(symbol)
            if not risk_assessment:
                return {'symbol': symbol, 'win_rate_prediction': 0.0, 'error': 'No risk assessment available'}
            
            # Get AI win rate prediction
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, risk_assessment)
            
            return {
                'symbol': symbol,
                'win_rate_prediction': ai_prediction.win_rate_prediction,
                'confidence': ai_prediction.confidence,
                'direction': ai_prediction.direction,
                'reasoning': ai_prediction.reasoning,
                'ai_analysis': ai_prediction.ai_analysis,
                'data_summary': ai_prediction.data_summary,
                'risk_level': risk_assessment.get('risk_value', 0.5),
                'time_in_risk': risk_assessment.get('time_in_risk', 0.5),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting RiskMetric win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'win_rate_prediction': 0.0, 'error': str(e)}
    
    async def get_multi_timeframe_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get multi-timeframe win rate predictions using AI analysis"""
        try:
            # Get risk assessment
            risk_assessment = await self.assess_risk(symbol)
            if not risk_assessment:
                return {'symbol': symbol, 'error': 'No risk assessment available'}
            
            # Get multi-timeframe AI prediction
            multi_prediction = await self._get_multi_timeframe_ai_prediction(symbol, risk_assessment)
            
            return {
                'symbol': symbol,
                'short_term_24h': {
                    'win_rate': multi_prediction.short_term_24h.win_rate_prediction,
                    'confidence': multi_prediction.short_term_24h.confidence,
                    'direction': multi_prediction.short_term_24h.direction,
                    'reasoning': multi_prediction.short_term_24h.reasoning
                },
                'medium_term_7d': {
                    'win_rate': multi_prediction.medium_term_7d.win_rate_prediction,
                    'confidence': multi_prediction.medium_term_7d.confidence,
                    'direction': multi_prediction.medium_term_7d.direction,
                    'reasoning': multi_prediction.medium_term_7d.reasoning
                },
                'long_term_1m': {
                    'win_rate': multi_prediction.long_term_1m.win_rate_prediction,
                    'confidence': multi_prediction.long_term_1m.confidence,
                    'direction': multi_prediction.long_term_1m.direction,
                    'reasoning': multi_prediction.long_term_1m.reasoning
                },
                'overall_confidence': multi_prediction.overall_confidence,
                'best_opportunity': {
                    'timeframe': multi_prediction.best_opportunity.timeframe,
                    'win_rate': multi_prediction.best_opportunity.win_rate_prediction,
                    'direction': multi_prediction.best_opportunity.direction
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def _get_ai_win_rate_prediction(self, symbol: str, riskmetric_data: Dict[str, Any]) -> AIWinRatePrediction:
        """Get AI win rate prediction for RiskMetric Cowen methodology"""
        try:
            return await self.ai_predictor.predict_riskmetric_win_rate(
                symbol=symbol,
                riskmetric_data=riskmetric_data,
                model=AIModel.ANTHROPIC_CLAUDE
            )
        except Exception as e:
            logger.error(f"Error getting AI win rate prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return self.ai_predictor._create_fallback_prediction(symbol, "riskmetric", f"AI error: {str(e)}")
    
    async def _get_multi_timeframe_ai_prediction(self, symbol: str, riskmetric_data: Dict[str, Any]) -> MultiTimeframeAIPrediction:
        """Get multi-timeframe AI prediction for RiskMetric Cowen methodology"""
        try:
            return await self.ai_predictor.predict_multi_timeframe_win_rate(
                symbol=symbol,
                agent_type="riskmetric",
                agent_data=riskmetric_data,
                model=AIModel.ANTHROPIC_CLAUDE
            )
        except Exception as e:
            logger.error(f"Error getting multi-timeframe AI prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return self.ai_predictor._create_fallback_multi_prediction(symbol, "riskmetric")

# Global service instance
riskmetric_service = RiskMetricService() 