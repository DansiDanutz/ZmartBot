"""
Zmart Trading Bot Platform - Signal Generator Agent
Multi-source signal generation and aggregation system
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
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
class SignalData:
    """Signal data structure"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    confidence: float
    sources: List[SignalSource]
    data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]

class SignalGeneratorAgent:
    """
    Signal generator agent that creates trading signals from multiple data sources.
    
    Responsibilities:
    - Multi-source data aggregation
    - Signal generation algorithms
    - Signal quality filtering
    - Real-time market data processing
    - Signal validation and enrichment
    """
    
    def __init__(self):
        """Initialize the signal generator agent"""
        self.agent_id = "signal_generator_agent"
        self.status = "stopped"
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        
        # Signal generation configuration
        self.min_confidence = 0.5
        self.max_signals_per_hour = settings.MAX_SIGNALS_PER_HOUR
        self.signal_rate_limit_window = settings.SIGNAL_RATE_LIMIT_WINDOW
        
        # Signal processing state
        self.generated_signals: List[SignalData] = []
        self.signal_count_by_hour: Dict[str, int] = {}
        self.active_symbols: List[str] = []
        
        # Data sources state
        self.kingfisher_data: Dict[str, Dict[str, Any]] = {}
        self.riskmetric_data: Dict[str, Dict[str, Any]] = {}
        self.cryptometer_data: Dict[str, Dict[str, Any]] = {}
        self.technical_data: Dict[str, Dict[str, Any]] = {}
        self.fundamental_data: Dict[str, Dict[str, Any]] = {}
        self.sentiment_data: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.generation_metrics = {
            "total_signals_generated": 0,
            "signals_by_source": {},
            "signals_by_symbol": {},
            "average_confidence": 0.0,
            "last_updated": datetime.now()
        }
        
        # Task management
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("Signal generator agent initialized")
    
    async def start(self):
        """Start the signal generator agent"""
        if self.status == "running":
            logger.warning("Signal generator agent already running")
            return
        
        logger.info("Starting signal generator agent")
        self.status = "starting"
        
        try:
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._signal_generation_loop()),
                asyncio.create_task(self._data_collection_loop()),
                asyncio.create_task(self._rate_limiting_loop()),
                asyncio.create_task(self._metrics_update_loop())
            ]
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Update status
            self.status = "running"
            logger.info("Signal generator agent started successfully")
            
            # Emit startup event
            startup_event = Event(
                type=EventType.AGENT_STARTED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(startup_event)
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to start signal generator agent: {e}")
            raise
    
    async def stop(self):
        """Stop the signal generator agent"""
        if self.status == "stopped":
            logger.warning("Signal generator agent already stopped")
            return
        
        logger.info("Stopping signal generator agent")
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
            logger.info("Signal generator agent stopped successfully")
            
            # Emit shutdown event
            shutdown_event = Event(
                type=EventType.AGENT_STOPPED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(shutdown_event)
            
        except Exception as e:
            logger.error(f"Error stopping signal generator agent: {e}")
            raise
    
    async def generate_signal(self, symbol: str, force: bool = False) -> Optional[SignalData]:
        """
        Generate a trading signal for a specific symbol
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            force: Force signal generation even if rate limited
            
        Returns:
            SignalData: Generated signal or None if rate limited
        """
        logger.info(f"Generating signal for {symbol}")
        
        # Check rate limiting
        if not force and not await self._check_rate_limit(symbol):
            logger.warning(f"Rate limit exceeded for {symbol}")
            return None
        
        try:
            # Collect data from all sources
            signal_data = await self._collect_signal_data(symbol)
            
            # Generate signal using algorithms
            signal = await self._generate_signal_algorithm(symbol, signal_data)
            
            if signal and signal.confidence >= self.min_confidence:
                # Store generated signal
                self.generated_signals.append(signal)
                
                # Update metrics
                await self._update_generation_metrics(signal)
                
                # Emit signal generated event
                signal_event = Event(
                    type=EventType.SIGNAL_GENERATED,
                    data={
                        "signal_id": signal.signal_id,
                        "symbol": symbol,
                        "signal_type": signal.signal_type.value,
                        "confidence": signal.confidence,
                        "sources": [source.value for source in signal.sources],
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.event_bus.emit(signal_event)
                
                logger.info(f"Generated signal for {symbol}: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
                return signal
            else:
                logger.info(f"No signal generated for {symbol} (confidence too low)")
                return None
                
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def get_recent_signals(self, symbol: Optional[str] = None, limit: int = 50) -> List[SignalData]:
        """Get recent generated signals, optionally filtered by symbol"""
        signals = self.generated_signals
        
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        
        return signals[-limit:] if limit else signals
    
    async def get_signal_statistics(self) -> Dict[str, Any]:
        """Get signal generation statistics"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "generation_metrics": self.generation_metrics,
            "active_symbols": len(self.active_symbols),
            "data_sources": {
                "kingfisher": len(self.kingfisher_data),
                "riskmetric": len(self.riskmetric_data),
                "cryptometer": len(self.cryptometer_data),
                "technical": len(self.technical_data),
                "fundamental": len(self.fundamental_data),
                "sentiment": len(self.sentiment_data)
            },
            "rate_limiting": {
                "signals_this_hour": sum(self.signal_count_by_hour.values()),
                "max_signals_per_hour": self.max_signals_per_hour
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_data_source(self, source: SignalSource, symbol: str, data: Dict[str, Any]):
        """Update data for a specific source and symbol"""
        if source == SignalSource.KINGFISHER:
            self.kingfisher_data[symbol] = data
        elif source == SignalSource.RISKMETRIC:
            self.riskmetric_data[symbol] = data
        elif source == SignalSource.CRYPTOMETER:
            self.cryptometer_data[symbol] = data
        elif source == SignalSource.TECHNICAL:
            self.technical_data[symbol] = data
        elif source == SignalSource.FUNDAMENTAL:
            self.fundamental_data[symbol] = data
        elif source == SignalSource.SENTIMENT:
            self.sentiment_data[symbol] = data
        
        logger.info(f"Updated {source.value} data for {symbol}")
    
    async def _register_event_handlers(self):
        """Register event handlers for the signal generator agent"""
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data)
    
    async def _signal_generation_loop(self):
        """Background task for continuous signal generation"""
        while self._running:
            try:
                await asyncio.sleep(30.0)  # Generate signals every 30 seconds
                
                # Generate signals for active symbols
                for symbol in self.active_symbols:
                    await self.generate_signal(symbol)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in signal generation loop: {e}")
    
    async def _data_collection_loop(self):
        """Background task for data collection"""
        while self._running:
            try:
                await asyncio.sleep(60.0)  # Collect data every minute
                
                # Collect data from external sources
                await self._collect_kingfisher_data()
                await self._collect_riskmetric_data()
                await self._collect_cryptometer_data()
                await self._collect_technical_data()
                await self._collect_fundamental_data()
                await self._collect_sentiment_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
    
    async def _rate_limiting_loop(self):
        """Background task for rate limiting management"""
        while self._running:
            try:
                await asyncio.sleep(3600.0)  # Reset counters every hour
                
                # Reset signal count by hour
                self.signal_count_by_hour.clear()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiting loop: {e}")
    
    async def _metrics_update_loop(self):
        """Background task for metrics updates"""
        while self._running:
            try:
                await asyncio.sleep(300.0)  # Update every 5 minutes
                
                # Update comprehensive metrics
                await self._update_comprehensive_metrics()
                
                # Emit signal metrics event
                metrics_event = Event(
                    type=EventType.SIGNAL_GENERATED,  # Reuse existing event type
                    data={
                        "agent_id": self.agent_id,
                        "metrics": self.generation_metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.event_bus.emit(metrics_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics update loop: {e}")
    
    async def _check_rate_limit(self, symbol: str) -> bool:
        """Check if signal generation is rate limited for a symbol"""
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_key = f"{symbol}_{current_hour.isoformat()}"
        
        current_count = self.signal_count_by_hour.get(hour_key, 0)
        return current_count < self.max_signals_per_hour
    
    async def _collect_signal_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from all sources for signal generation"""
        signal_data = {
            "kingfisher": self.kingfisher_data.get(symbol, {}),
            "riskmetric": self.riskmetric_data.get(symbol, {}),
            "cryptometer": self.cryptometer_data.get(symbol, {}),
            "technical": self.technical_data.get(symbol, {}),
            "fundamental": self.fundamental_data.get(symbol, {}),
            "sentiment": self.sentiment_data.get(symbol, {})
        }
        
        return signal_data
    
    async def _generate_signal_algorithm(self, symbol: str, signal_data: Dict[str, Any]) -> Optional[SignalData]:
        """Generate signal using multi-source algorithm"""
        try:
            # Analyze each data source
            kingfisher_score = await self._analyze_kingfisher(signal_data.get("kingfisher", {}))
            riskmetric_score = await self._analyze_riskmetric(signal_data.get("riskmetric", {}))
            cryptometer_score = await self._analyze_cryptometer(signal_data.get("cryptometer", {}))
            technical_score = await self._analyze_technical(signal_data.get("technical", {}))
            fundamental_score = await self._analyze_fundamental(signal_data.get("fundamental", {}))
            sentiment_score = await self._analyze_sentiment(signal_data.get("sentiment", {}))
            
            # Combine scores with weights
            confidence_scores = [
                kingfisher_score * 0.3,    # 30% weight
                riskmetric_score * 0.2,    # 20% weight
                cryptometer_score * 0.5    # 50% weight
            ]
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_scores)
            
            # Determine signal type
            signal_type = await self._determine_signal_type(confidence_scores)
            
            # Create signal data
            signal = SignalData(
                signal_id=f"signal_{datetime.now().timestamp()}",
                symbol=symbol,
                signal_type=signal_type,
                confidence=overall_confidence,
                sources=[SignalSource.KINGFISHER, SignalSource.RISKMETRIC, SignalSource.CRYPTOMETER],
                data=signal_data,
                timestamp=datetime.now(),
                metadata={
                    "kingfisher_score": kingfisher_score,
                    "riskmetric_score": riskmetric_score,
                    "cryptometer_score": cryptometer_score,
                    "technical_score": technical_score,
                    "fundamental_score": fundamental_score,
                    "sentiment_score": sentiment_score
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal algorithm for {symbol}: {e}")
            return None
    
    async def _analyze_kingfisher(self, kingfisher_data: Dict[str, Any]) -> float:
        """Analyze KingFisher liquidation data"""
        if not kingfisher_data:
            return 0.0
        
        # Simplified analysis
        score = 0.5  # Base score
        
        # Adjust based on liquidation clusters
        if "liquidation_clusters" in kingfisher_data:
            score += 0.2
        
        # Adjust based on toxic order flow
        if "toxic_order_flow" in kingfisher_data:
            score += 0.3
        
        return min(score, 1.0)
    
    async def _analyze_riskmetric(self, riskmetric_data: Dict[str, Any]) -> float:
        """Analyze RiskMetric data"""
        if not riskmetric_data:
            return 0.0
        
        # Simplified analysis
        score = 0.5  # Base score
        
        # Adjust based on risk metrics
        if "volatility" in riskmetric_data:
            volatility = riskmetric_data["volatility"]
            if volatility > 0.8:
                score += 0.3
            elif volatility < 0.2:
                score -= 0.2
        
        return min(max(score, 0.0), 1.0)
    
    async def _analyze_cryptometer(self, cryptometer_data: Dict[str, Any]) -> float:
        """Analyze Cryptometer data"""
        if not cryptometer_data:
            return 0.0
        
        # Simplified analysis
        score = 0.5  # Base score
        
        # Adjust based on market indicators
        if "market_sentiment" in cryptometer_data:
            sentiment = cryptometer_data["market_sentiment"]
            if sentiment > 0.7:
                score += 0.4
            elif sentiment < 0.3:
                score -= 0.3
        
        return min(max(score, 0.0), 1.0)
    
    async def _analyze_technical(self, technical_data: Dict[str, Any]) -> float:
        """Analyze technical indicators"""
        if not technical_data:
            return 0.0
        
        # Simplified technical analysis
        score = 0.5
        
        # RSI analysis
        if "rsi" in technical_data:
            rsi = technical_data["rsi"]
            if rsi < 30:  # Oversold
                score += 0.2
            elif rsi > 70:  # Overbought
                score -= 0.2
        
        return min(max(score, 0.0), 1.0)
    
    async def _analyze_fundamental(self, fundamental_data: Dict[str, Any]) -> float:
        """Analyze fundamental data"""
        if not fundamental_data:
            return 0.0
        
        # Simplified fundamental analysis
        return 0.5  # Neutral score
    
    async def _analyze_sentiment(self, sentiment_data: Dict[str, Any]) -> float:
        """Analyze sentiment data"""
        if not sentiment_data:
            return 0.0
        
        # Simplified sentiment analysis
        score = 0.5
        
        if "social_sentiment" in sentiment_data:
            sentiment = sentiment_data["social_sentiment"]
            if sentiment > 0.6:
                score += 0.3
            elif sentiment < 0.4:
                score -= 0.2
        
        return min(max(score, 0.0), 1.0)
    
    async def _determine_signal_type(self, confidence_scores: List[float]) -> SignalType:
        """Determine signal type based on confidence scores"""
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        if avg_confidence > 0.8:
            return SignalType.STRONG_BUY
        elif avg_confidence > 0.6:
            return SignalType.BUY
        elif avg_confidence < 0.2:
            return SignalType.STRONG_SELL
        elif avg_confidence < 0.4:
            return SignalType.SELL
        else:
            return SignalType.HOLD
    
    async def _update_generation_metrics(self, signal: SignalData):
        """Update signal generation metrics"""
        self.generation_metrics["total_signals_generated"] += 1
        
        # Update signals by source
        for source in signal.sources:
            source_key = source.value
            if source_key not in self.generation_metrics["signals_by_source"]:
                self.generation_metrics["signals_by_source"][source_key] = 0
            self.generation_metrics["signals_by_source"][source_key] += 1
        
        # Update signals by symbol
        if signal.symbol not in self.generation_metrics["signals_by_symbol"]:
            self.generation_metrics["signals_by_symbol"][signal.symbol] = 0
        self.generation_metrics["signals_by_symbol"][signal.symbol] += 1
        
        # Update average confidence
        total_signals = self.generation_metrics["total_signals_generated"]
        current_avg = self.generation_metrics["average_confidence"]
        self.generation_metrics["average_confidence"] = (current_avg * (total_signals - 1) + signal.confidence) / total_signals
        
        self.generation_metrics["last_updated"] = datetime.now()
    
    async def _update_comprehensive_metrics(self):
        """Update comprehensive metrics"""
        # Update metrics with current data
        pass
    
    async def _collect_kingfisher_data(self):
        """Collect KingFisher liquidation data"""
        # Placeholder for data collection
        pass
    
    async def _collect_riskmetric_data(self):
        """Collect RiskMetric data"""
        # Placeholder for data collection
        pass
    
    async def _collect_cryptometer_data(self):
        """Collect Cryptometer data"""
        # Placeholder for data collection
        pass
    
    async def _collect_technical_data(self):
        """Collect technical indicators"""
        # Placeholder for data collection
        pass
    
    async def _collect_fundamental_data(self):
        """Collect fundamental data"""
        # Placeholder for data collection
        pass
    
    async def _collect_sentiment_data(self):
        """Collect sentiment data"""
        # Placeholder for data collection
        pass
    
    async def _handle_market_data(self, event: Event):
        """Handle market data events"""
        market_data = event.data
        symbol = market_data.get("symbol")
        
        if symbol is not None:
            # Update data sources based on market data
            await self.update_data_source(SignalSource.TECHNICAL, symbol, market_data)
            await self.update_data_source(SignalSource.FUNDAMENTAL, symbol, market_data)
            await self.update_data_source(SignalSource.SENTIMENT, symbol, market_data) 