"""
Zmart Trading Bot Platform - Scoring Agent
AI-powered signal scoring and confidence assessment system
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from src.config.settings import settings
from src.utils.event_bus import EventBus, EventType, Event
from src.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class SignalSource(Enum):
    """Signal source enumeration"""
    KINGFISHER = "kingfisher"
    RISKMETRIC = "riskmetric"
    CRYPTOMETER = "cryptometer"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"

class SignalType(Enum):
    """Signal type enumeration"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

@dataclass
class SignalScore:
    """Signal scoring result"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    confidence: float
    score: float
    sources: List[SignalSource]
    factors: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any]

class ScoringAgent:
    """
    AI-powered scoring agent that processes multiple signal sources
    and provides confidence metrics and explanations.
    
    Responsibilities:
    - Multi-source signal aggregation
    - Confidence scoring and validation
    - Risk assessment integration
    - Historical performance analysis
    - Signal quality filtering
    """
    
    def __init__(self):
        """Initialize the scoring agent"""
        self.agent_id = "scoring_agent"
        self.status = "stopped"
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        
        # Scoring configuration
        self.confidence_threshold = settings.SIGNAL_CONFIDENCE_THRESHOLD
        self.min_sources = 2  # Minimum sources required for scoring
        self.max_signal_age = 300  # 5 minutes in seconds
        
        # Signal processing state
        self.pending_signals: List[Dict] = []
        self.processed_signals: Dict[str, SignalScore] = {}
        self.signal_history: List[SignalScore] = []
        
        # Performance tracking
        self.accuracy_metrics = {
            "total_signals": 0,
            "correct_predictions": 0,
            "accuracy_rate": 0.0,
            "last_updated": datetime.now()
        }
        
        # Task management
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("Scoring agent initialized")
    
    async def start(self):
        """Start the scoring agent"""
        if self.status == "running":
            logger.warning("Scoring agent already running")
            return
        
        logger.info("Starting scoring agent")
        self.status = "starting"
        
        try:
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._signal_processing_loop()),
                asyncio.create_task(self._performance_monitoring_loop()),
                asyncio.create_task(self._cleanup_loop())
            ]
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Update status
            self.status = "running"
            logger.info("Scoring agent started successfully")
            
            # Emit startup event
            await self.event_bus.emit(Event(
                type=EventType.AGENT_STARTED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            ))
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to start scoring agent: {e}")
            raise
    
    async def stop(self):
        """Stop the scoring agent"""
        if self.status == "stopped":
            logger.warning("Scoring agent already stopped")
            return
        
        logger.info("Stopping scoring agent")
        self.status = "stopping"
        
        try:
            # Stop background tasks
            self._running = False
            
            # Cancel all tasks
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Update status
            self.status = "stopped"
            logger.info("Scoring agent stopped successfully")
            
            # Emit shutdown event
            await self.event_bus.emit(Event(
                type=EventType.AGENT_STOPPED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            ))
            
        except Exception as e:
            logger.error(f"Error stopping scoring agent: {e}")
            raise
    
    async def score_signal(self, signal_data: Dict[str, Any]) -> SignalScore:
        """
        Score a trading signal using multiple sources and AI models
        
        Args:
            signal_data: Raw signal data from various sources
            
        Returns:
            SignalScore: Scored signal with confidence metrics
        """
        signal_id = signal_data.get("signal_id", f"signal_{datetime.now().timestamp()}")
        symbol = signal_data.get("symbol", "unknown")
        
        logger.info(f"Scoring signal {signal_id} for {symbol}")
        
        try:
            # Extract signal sources
            sources = self._extract_signal_sources(signal_data)
            
            # Validate minimum sources
            if len(sources) < self.min_sources:
                raise ValueError(f"Insufficient signal sources: {len(sources)} < {self.min_sources}")
            
            # Calculate individual source scores
            source_scores = await self._calculate_source_scores(signal_data, sources)
            
            # Aggregate scores using ensemble method
            aggregated_score = await self._aggregate_scores(source_scores)
            
            # Determine signal type and confidence
            signal_type, confidence = await self._determine_signal_type(aggregated_score)
            
            # Calculate contributing factors
            factors = await self._calculate_contributing_factors(source_scores)
            
            # Create signal score
            signal_score = SignalScore(
                signal_id=signal_id,
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                score=aggregated_score,
                sources=sources,
                factors=factors,
                timestamp=datetime.now(),
                metadata={
                    "source_scores": source_scores,
                    "aggregation_method": "ensemble_weighted",
                    "processing_time": datetime.now().isoformat()
                }
            )
            
            # Store processed signal
            self.processed_signals[signal_id] = signal_score
            self.signal_history.append(signal_score)
            
            # Update metrics
            await self._update_metrics(signal_score)
            
            logger.info(f"Signal {signal_id} scored: {signal_type.value} (confidence: {confidence:.2f})")
            
            # Emit scored signal event
            await self.event_bus.emit(Event(
                type=EventType.SIGNAL_PROCESSED,
                data={
                    "signal_id": signal_id,
                    "symbol": symbol,
                    "signal_type": signal_type.value,
                    "confidence": confidence,
                    "score": aggregated_score,
                    "timestamp": datetime.now().isoformat()
                }
            ))
            
            return signal_score
            
        except Exception as e:
            logger.error(f"Error scoring signal {signal_id}: {e}")
            raise
    
    async def get_signal_score(self, signal_id: str) -> Optional[SignalScore]:
        """Get a processed signal score by ID"""
        return self.processed_signals.get(signal_id)
    
    async def get_signal_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[SignalScore]:
        """Get signal history, optionally filtered by symbol"""
        history = self.signal_history
        
        if symbol:
            history = [s for s in history if s.symbol == symbol]
        
        return history[-limit:] if limit else history
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get scoring agent performance metrics"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "accuracy_metrics": self.accuracy_metrics,
            "signal_counts": {
                "pending": len(self.pending_signals),
                "processed": len(self.processed_signals),
                "historical": len(self.signal_history)
            },
            "confidence_distribution": await self._calculate_confidence_distribution(),
            "source_usage": await self._calculate_source_usage(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _register_event_handlers(self):
        """Register event handlers for the scoring agent"""
        self.event_bus.subscribe(EventType.SIGNAL_GENERATED, self._handle_signal_generated)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data_updated)
        self.event_bus.subscribe(EventType.RISK_SCORE_UPDATED, self._handle_risk_score_updated)
        self.event_bus.subscribe(EventType.SYSTEM_ERROR, self._handle_system_error)
    
    async def _signal_processing_loop(self):
        """Background task for processing pending signals"""
        while self._running:
            try:
                await asyncio.sleep(1.0)  # Process every second
                
                if not self.pending_signals:
                    continue
                
                # Process signals in order
                signal = self.pending_signals.pop(0)
                await self.score_signal(signal)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in signal processing loop: {e}")
    
    async def _performance_monitoring_loop(self):
        """Background task for performance monitoring"""
        while self._running:
            try:
                await asyncio.sleep(300.0)  # Check every 5 minutes
                
                # Update accuracy metrics
                await self._update_accuracy_metrics()
                
                # Emit performance metrics
                await self.event_bus.emit(Event(
                    type=EventType.AGENT_TASK_COMPLETED,
                    data={
                        "agent_id": self.agent_id,
                        "metrics": await self.get_performance_metrics(),
                        "timestamp": datetime.now().isoformat()
                    }
                ))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
    
    async def _cleanup_loop(self):
        """Background task for cleanup operations"""
        while self._running:
            try:
                await asyncio.sleep(3600.0)  # Cleanup every hour
                
                # Remove old processed signals
                cutoff_time = datetime.now() - timedelta(hours=24)
                old_signals = [
                    signal_id for signal_id, signal in self.processed_signals.items()
                    if signal.timestamp < cutoff_time
                ]
                
                for signal_id in old_signals:
                    del self.processed_signals[signal_id]
                
                if old_signals:
                    logger.info(f"Cleaned up {len(old_signals)} old signals")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def _extract_signal_sources(self, signal_data: Dict[str, Any]) -> List[SignalSource]:
        """Extract signal sources from signal data"""
        sources = []
        
        # Check for KingFisher data
        if "kingfisher" in signal_data:
            sources.append(SignalSource.KINGFISHER)
        
        # Check for RiskMetric data
        if "riskmetric" in signal_data:
            sources.append(SignalSource.RISKMETRIC)
        
        # Check for Cryptometer data
        if "cryptometer" in signal_data:
            sources.append(SignalSource.CRYPTOMETER)
        
        # Check for technical analysis data
        if "technical" in signal_data:
            sources.append(SignalSource.TECHNICAL)
        
        # Check for fundamental analysis data
        if "fundamental" in signal_data:
            sources.append(SignalSource.FUNDAMENTAL)
        
        # Check for sentiment analysis data
        if "sentiment" in signal_data:
            sources.append(SignalSource.SENTIMENT)
        
        return sources
    
    async def _calculate_source_scores(self, signal_data: Dict[str, Any], sources: List[SignalSource]) -> Dict[SignalSource, float]:
        """Calculate individual source scores"""
        source_scores = {}
        
        for source in sources:
            try:
                if source == SignalSource.KINGFISHER:
                    score = await self._score_kingfisher(signal_data.get("kingfisher", {}))
                elif source == SignalSource.RISKMETRIC:
                    score = await self._score_riskmetric(signal_data.get("riskmetric", {}))
                elif source == SignalSource.CRYPTOMETER:
                    score = await self._score_cryptometer(signal_data.get("cryptometer", {}))
                elif source == SignalSource.TECHNICAL:
                    score = await self._score_technical(signal_data.get("technical", {}))
                elif source == SignalSource.FUNDAMENTAL:
                    score = await self._score_fundamental(signal_data.get("fundamental", {}))
                elif source == SignalSource.SENTIMENT:
                    score = await self._score_sentiment(signal_data.get("sentiment", {}))
                else:
                    score = 0.0
                
                source_scores[source] = score
                
            except Exception as e:
                logger.error(f"Error calculating score for {source.value}: {e}")
                source_scores[source] = 0.0
        
        return source_scores
    
    async def _score_kingfisher(self, kingfisher_data: Dict[str, Any]) -> float:
        """Score KingFisher liquidation data"""
        try:
            # Extract liquidation metrics
            long_liquidation_ratio = kingfisher_data.get("long_liquidation_ratio", 0.0)
            short_liquidation_ratio = kingfisher_data.get("short_liquidation_ratio", 0.0)
            
            # Calculate liquidation pressure score
            liquidation_pressure = abs(long_liquidation_ratio - short_liquidation_ratio)
            
            # Normalize to 0-1 scale
            score = min(liquidation_pressure / 0.1, 1.0)  # 10% threshold
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring KingFisher data: {e}")
            return 0.0
    
    async def _score_riskmetric(self, riskmetric_data: Dict[str, Any]) -> float:
        """Score RiskMetric data"""
        try:
            # Extract risk metrics
            volatility_score = riskmetric_data.get("volatility_score", 0.0)
            correlation_score = riskmetric_data.get("correlation_score", 0.0)
            drawdown_score = riskmetric_data.get("drawdown_score", 0.0)
            
            # Calculate weighted risk score
            risk_score = (
                volatility_score * 0.4 +
                correlation_score * 0.3 +
                drawdown_score * 0.3
            )
            
            # Invert for scoring (lower risk = higher score)
            score = 1.0 - risk_score
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error scoring RiskMetric data: {e}")
            return 0.0
    
    async def _score_cryptometer(self, cryptometer_data: Dict[str, Any]) -> float:
        """Score Cryptometer data"""
        try:
            # Extract Cryptometer metrics
            fear_greed_index = cryptometer_data.get("fear_greed_index", 50.0)
            market_sentiment = cryptometer_data.get("market_sentiment", 0.0)
            volume_analysis = cryptometer_data.get("volume_analysis", 0.0)
            
            # Calculate sentiment score
            sentiment_score = (fear_greed_index / 100.0 + market_sentiment + volume_analysis) / 3.0
            
            return max(0.0, min(1.0, sentiment_score))
            
        except Exception as e:
            logger.error(f"Error scoring Cryptometer data: {e}")
            return 0.0
    
    async def _score_technical(self, technical_data: Dict[str, Any]) -> float:
        """Score technical analysis data"""
        try:
            # Extract technical indicators
            rsi = technical_data.get("rsi", 50.0)
            macd = technical_data.get("macd", 0.0)
            bollinger_position = technical_data.get("bollinger_position", 0.5)
            
            # Calculate technical score
            rsi_score = 1.0 - abs(rsi - 50.0) / 50.0  # Closer to 50 = better
            macd_score = max(0.0, min(1.0, (macd + 1.0) / 2.0))  # Normalize to 0-1
            bollinger_score = 1.0 - abs(bollinger_position - 0.5)  # Middle = better
            
            technical_score = (rsi_score + macd_score + bollinger_score) / 3.0
            
            return technical_score
            
        except Exception as e:
            logger.error(f"Error scoring technical data: {e}")
            return 0.0
    
    async def _score_fundamental(self, fundamental_data: Dict[str, Any]) -> float:
        """Score fundamental analysis data"""
        try:
            # Extract fundamental metrics
            market_cap = fundamental_data.get("market_cap", 0.0)
            volume_24h = fundamental_data.get("volume_24h", 0.0)
            price_change_24h = fundamental_data.get("price_change_24h", 0.0)
            
            # Calculate fundamental score
            market_cap_score = min(market_cap / 1e9, 1.0)  # Normalize by 1B
            volume_score = min(volume_24h / 1e8, 1.0)  # Normalize by 100M
            price_score = max(0.0, min(1.0, (price_change_24h + 50.0) / 100.0))
            
            fundamental_score = (market_cap_score + volume_score + price_score) / 3.0
            
            return fundamental_score
            
        except Exception as e:
            logger.error(f"Error scoring fundamental data: {e}")
            return 0.0
    
    async def _score_sentiment(self, sentiment_data: Dict[str, Any]) -> float:
        """Score sentiment analysis data"""
        try:
            # Extract sentiment metrics
            social_sentiment = sentiment_data.get("social_sentiment", 0.0)
            news_sentiment = sentiment_data.get("news_sentiment", 0.0)
            reddit_sentiment = sentiment_data.get("reddit_sentiment", 0.0)
            
            # Calculate sentiment score
            sentiment_score = (social_sentiment + news_sentiment + reddit_sentiment) / 3.0
            
            # Normalize to 0-1 scale
            normalized_score = (sentiment_score + 1.0) / 2.0
            
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            logger.error(f"Error scoring sentiment data: {e}")
            return 0.0
    
    async def _aggregate_scores(self, source_scores: Dict[SignalSource, float]) -> float:
        """Aggregate source scores using ensemble method"""
        if not source_scores:
            return 0.0
        
        # Weighted average based on source reliability
        weights = {
            SignalSource.KINGFISHER: 0.3,
            SignalSource.RISKMETRIC: 0.2,
            SignalSource.CRYPTOMETER: 0.25,
            SignalSource.TECHNICAL: 0.15,
            SignalSource.FUNDAMENTAL: 0.05,
            SignalSource.SENTIMENT: 0.05
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for source, score in source_scores.items():
            weight = weights.get(source, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0.0:
            return 0.0
        
        return weighted_sum / total_weight
    
    async def _determine_signal_type(self, score: float) -> Tuple[SignalType, float]:
        """Determine signal type and confidence based on score"""
        if score >= 0.8:
            signal_type = SignalType.STRONG_BUY
            confidence = score
        elif score >= 0.6:
            signal_type = SignalType.BUY
            confidence = score
        elif score >= 0.4:
            signal_type = SignalType.HOLD
            confidence = 0.5
        elif score >= 0.2:
            signal_type = SignalType.SELL
            confidence = 1.0 - score
        else:
            signal_type = SignalType.STRONG_SELL
            confidence = 1.0 - score
        
        return signal_type, confidence
    
    async def _calculate_contributing_factors(self, source_scores: Dict[SignalSource, float]) -> Dict[str, float]:
        """Calculate contributing factors for the signal"""
        factors = {}
        
        for source, score in source_scores.items():
            factors[source.value] = score
        
        return factors
    
    async def _update_metrics(self, signal_score: SignalScore):
        """Update performance metrics"""
        self.accuracy_metrics["total_signals"] += 1
        # Additional metric updates would go here
    
    async def _update_accuracy_metrics(self):
        """Update accuracy metrics based on historical performance"""
        # This would implement accuracy tracking logic
        pass
    
    async def _calculate_confidence_distribution(self) -> Dict[str, int]:
        """Calculate confidence distribution across processed signals"""
        distribution = {
            "very_high": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "very_low": 0
        }
        
        for signal in self.signal_history:
            if signal.confidence >= 0.9:
                distribution["very_high"] += 1
            elif signal.confidence >= 0.7:
                distribution["high"] += 1
            elif signal.confidence >= 0.5:
                distribution["medium"] += 1
            elif signal.confidence >= 0.3:
                distribution["low"] += 1
            else:
                distribution["very_low"] += 1
        
        return distribution
    
    async def _calculate_source_usage(self) -> Dict[str, int]:
        """Calculate usage statistics for each signal source"""
        usage = {}
        
        for signal in self.signal_history:
            for source in signal.sources:
                source_name = source.value
                usage[source_name] = usage.get(source_name, 0) + 1
        
        return usage
    
    async def _handle_signal_generated(self, event_data: Dict[str, Any]):
        """Handle signal generated events"""
        signal_data = event_data.get("signal_data", {})
        self.pending_signals.append(signal_data)
    
    async def _handle_market_data_updated(self, event_data: Dict[str, Any]):
        """Handle market data update events"""
        # Process market data updates
        pass
    
    async def _handle_risk_score_updated(self, event_data: Dict[str, Any]):
        """Handle risk score update events"""
        # Process risk score updates
        pass
    
    async def _handle_system_error(self, event_data: Dict[str, Any]):
        """Handle system error events"""
        logger.error(f"System error in scoring agent: {event_data}") 