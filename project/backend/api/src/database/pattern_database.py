#!/usr/bin/env python3
"""
Pattern Database Schema and Models
PostgreSQL database for storing pattern data, historical prices, and indicators
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON, Text, Index, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid
import os
from typing import Optional

Base = declarative_base()

class PriceData(Base):
    """Historical price data from multiple sources"""
    __tablename__ = 'price_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # binance, kucoin, coingecko, cryptometer
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Additional metrics
    market_cap = Column(Float)
    volume_24h = Column(Float)
    circulating_supply = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for fast queries
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_source_symbol', 'source', 'symbol'),
        UniqueConstraint('symbol', 'source', 'timestamp', name='uq_price_data'),
    )

class TechnicalIndicators(Base):
    """Calculated technical indicators for each price point"""
    __tablename__ = 'technical_indicators'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price_data_id = Column(UUID(as_uuid=True), ForeignKey('price_data.id'), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 1. EMA Crossovers
    ema_9 = Column(Float)
    ema_21 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    ema_cross_signal = Column(String(20))  # golden_cross, death_cross, none
    
    # 2. RSI
    rsi = Column(Float)
    rsi_14 = Column(Float)
    rsi_signal = Column(String(20))  # overbought, oversold, neutral
    rsi_divergence = Column(String(20))  # bullish, bearish, none
    
    # 3. MACD
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    macd_cross = Column(String(20))  # bullish_cross, bearish_cross, none
    
    # 4. Volume Profile / OBV
    obv = Column(Float)
    volume_sma = Column(Float)
    volume_spike = Column(Boolean)
    volume_divergence = Column(String(20))  # bullish, bearish, none
    
    # 5. Bollinger Bands
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    bb_squeeze = Column(Boolean)
    bb_breakout = Column(String(20))  # upper, lower, none
    
    # 6. Fibonacci Levels
    fib_0 = Column(Float)
    fib_236 = Column(Float)
    fib_382 = Column(Float)
    fib_500 = Column(Float)
    fib_618 = Column(Float)
    fib_786 = Column(Float)
    fib_1000 = Column(Float)
    fib_1618 = Column(Float)
    
    # 7. Ichimoku Cloud
    tenkan_sen = Column(Float)  # Conversion Line
    kijun_sen = Column(Float)   # Base Line
    senkou_span_a = Column(Float)  # Leading Span A
    senkou_span_b = Column(Float)  # Leading Span B
    chikou_span = Column(Float)    # Lagging Span
    kumo_breakout = Column(String(20))  # bullish, bearish, none
    tk_cross = Column(String(20))  # bullish, bearish, none
    
    # 8. Stochastic RSI
    stoch_rsi_k = Column(Float)
    stoch_rsi_d = Column(Float)
    stoch_rsi_signal = Column(String(20))  # overbought, oversold, neutral
    stoch_rsi_cross = Column(String(20))  # bullish, bearish, none
    
    # 9. Divergence Analysis
    price_trend = Column(String(20))  # up, down, sideways
    oscillator_trend = Column(String(20))  # up, down, sideways
    divergence_type = Column(String(20))  # bullish, bearish, none
    divergence_strength = Column(Float)  # 0-100
    
    # 10. Support/Resistance
    support_levels = Column(ARRAY(Float))
    resistance_levels = Column(ARRAY(Float))
    current_support = Column(Float)
    current_resistance = Column(Float)
    sr_breakout = Column(String(20))  # support_break, resistance_break, none
    
    # Composite scores
    bullish_score = Column(Float)  # 0-100
    bearish_score = Column(Float)  # 0-100
    neutral_score = Column(Float)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    price_data = relationship("PriceData", backref="indicators")
    
    __table_args__ = (
        Index('idx_indicators_symbol_timestamp', 'symbol', 'timestamp'),
    )

class DetectedPattern(Base):
    """Detected patterns from analysis"""
    __tablename__ = 'detected_patterns'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Pattern identification
    pattern_name = Column(String(100), nullable=False)
    pattern_category = Column(String(50), nullable=False)  # reversal, continuation, breakout, etc.
    pattern_subcategory = Column(String(50))
    
    # Pattern metrics
    confidence = Column(Float, nullable=False)  # 0-1
    strength = Column(String(20))  # weak, moderate, strong, very_strong
    direction = Column(String(20), nullable=False)  # long, short, neutral
    time_horizon = Column(String(20))  # immediate, short_term, medium_term, long_term
    
    # Trading parameters
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    take_profit_3 = Column(Float)
    risk_reward_ratio = Column(Float)
    
    # Pattern specifics
    pattern_data = Column(JSONB)  # Store pattern-specific data
    chart_points = Column(JSONB)  # Key points for charting
    
    # Validation
    pattern_valid_until = Column(DateTime)
    pattern_invalidation_price = Column(Float)
    
    # Performance tracking
    pattern_triggered = Column(Boolean, default=False)
    pattern_completed = Column(Boolean, default=False)
    actual_outcome = Column(String(20))  # success, failure, partial, expired
    actual_return = Column(Float)
    
    # Quality metrics
    quality_score = Column(Float)  # 0-100, from QA agent
    data_completeness = Column(Float)  # 0-100
    
    # Metadata
    source_indicators = Column(JSONB)  # Which indicators contributed
    detection_method = Column(String(50))  # algorithm used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_patterns_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_patterns_category', 'pattern_category'),
        Index('idx_patterns_confidence', 'confidence'),
    )

class PatternStatistics(Base):
    """Aggregated statistics for pattern performance"""
    __tablename__ = 'pattern_statistics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_name = Column(String(100), nullable=False, unique=True)
    pattern_category = Column(String(50), nullable=False)
    
    # Performance metrics
    total_occurrences = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    expired_patterns = Column(Integer, default=0)
    
    # Win rate metrics
    win_rate = Column(Float)  # Percentage
    avg_profit = Column(Float)  # Percentage
    avg_loss = Column(Float)  # Percentage
    profit_factor = Column(Float)  # Total profit / Total loss
    
    # Risk metrics
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    
    # Time metrics
    avg_pattern_duration = Column(Float)  # Hours
    avg_time_to_target = Column(Float)  # Hours
    
    # By timeframe
    performance_by_timeframe = Column(JSONB)
    
    # By market condition
    performance_by_condition = Column(JSONB)
    
    # Recent performance (last 30 days)
    recent_win_rate = Column(Float)
    recent_occurrences = Column(Integer)
    
    # Quality metrics
    avg_confidence = Column(Float)
    avg_quality_score = Column(Float)
    
    last_updated = Column(DateTime, default=datetime.utcnow)

class CombinationPattern(Base):
    """Patterns formed by multiple indicator combinations"""
    __tablename__ = 'combination_patterns'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Combination details
    combination_name = Column(String(200), nullable=False)
    indicators_used = Column(ARRAY(String))
    
    # Examples of combinations:
    # EMA Cross + RSI Divergence
    # Bollinger Band Squeeze + MACD Cross
    # Ichimoku Cloud Breakout + Volume Spike
    # Stochastic RSI Overbought + Bearish Engulfing on Resistance
    
    # Signals from each indicator
    indicator_signals = Column(JSONB)
    
    # Combined analysis
    combined_confidence = Column(Float)
    combined_direction = Column(String(20))
    synergy_score = Column(Float)  # How well indicators confirm each other
    
    # Trading parameters
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profits = Column(ARRAY(Float))
    
    # Performance
    historical_win_rate = Column(Float)
    expected_return = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class BlockchainData(Base):
    """On-chain data from blockchain agent"""
    __tablename__ = 'blockchain_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    blockchain = Column(String(50), nullable=False)  # ethereum, bitcoin, etc.
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # On-chain metrics
    active_addresses = Column(Integer)
    transaction_count = Column(Integer)
    transaction_volume = Column(Float)
    average_transaction_value = Column(Float)
    
    # Exchange flows
    exchange_inflow = Column(Float)
    exchange_outflow = Column(Float)
    exchange_netflow = Column(Float)
    
    # Holder metrics
    unique_holders = Column(Integer)
    whale_transactions = Column(Integer)  # Large transactions
    retail_transactions = Column(Integer)  # Small transactions
    
    # Network metrics
    hash_rate = Column(Float)
    difficulty = Column(Float)
    block_time = Column(Float)
    
    # DeFi metrics (if applicable)
    total_value_locked = Column(Float)
    defi_volume = Column(Float)
    
    # Sentiment indicators
    network_growth = Column(Float)
    nvt_ratio = Column(Float)  # Network Value to Transactions
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_blockchain_symbol_timestamp', 'symbol', 'timestamp'),
    )

class PatternAlert(Base):
    """Real-time pattern alerts for users"""
    __tablename__ = 'pattern_alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey('detected_patterns.id'))
    
    # Alert details
    alert_type = Column(String(50))  # new_pattern, pattern_triggered, target_reached
    urgency = Column(String(20))  # low, medium, high, critical
    
    # User targeting
    subscription_tier = Column(String(20))  # free, basic, premium, institutional
    
    # Alert content
    title = Column(String(200))
    message = Column(Text)
    action_required = Column(String(100))
    
    # Delivery status
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    acknowledged = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationship
    pattern = relationship("DetectedPattern", backref="alerts")

class UserPatternAccess(Base):
    """Track user access to pattern data (for monetization)"""
    __tablename__ = 'user_pattern_access'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False, index=True)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey('detected_patterns.id'))
    
    # Access details
    access_type = Column(String(50))  # view, download, api_call
    access_tier = Column(String(20))  # free, paid, premium
    
    # Usage tracking
    access_count = Column(Integer, default=1)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Monetization
    credits_used = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    pattern = relationship("DetectedPattern", backref="user_accesses")

# Database initialization
def init_database(connection_string: Optional[str] = None):
    """Initialize the pattern database"""
    
    if not connection_string:
        connection_string = os.getenv(
            'PATTERN_DATABASE_URL',
            'postgresql://zmart_user:zmart_pass@localhost:5432/pattern_db'
        )
    
    engine = create_engine(connection_string, echo=False)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session

def get_session():
    """Get a database session"""
    _, Session = init_database()
    return Session()

# Utility functions for common queries
class PatternDB:
    """Database utility class for pattern operations"""
    
    def __init__(self, session=None):
        self.session = session or get_session()
    
    def add_price_data(self, symbol: str, source: str, timestamp: datetime, 
                      open: float, high: float, low: float, close: float, volume: float, **kwargs):
        """Add price data to database"""
        price_data = PriceData(
            symbol=symbol,
            source=source,
            timestamp=timestamp,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            **kwargs
        )
        self.session.add(price_data)
        self.session.commit()
        return price_data
    
    def add_pattern(self, symbol: str, pattern_name: str, confidence: float, **kwargs):
        """Add detected pattern to database"""
        pattern = DetectedPattern(
            symbol=symbol,
            pattern_name=pattern_name,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        self.session.add(pattern)
        self.session.commit()
        return pattern
    
    def get_recent_patterns(self, symbol: Optional[str] = None, limit: int = 100):
        """Get recent detected patterns"""
        query = self.session.query(DetectedPattern)
        if symbol:
            query = query.filter_by(symbol=symbol)
        return query.order_by(DetectedPattern.timestamp.desc()).limit(limit).all()
    
    def get_pattern_statistics(self, pattern_name: Optional[str] = None):
        """Get pattern performance statistics"""
        query = self.session.query(PatternStatistics)
        if pattern_name:
            query = query.filter_by(pattern_name=pattern_name)
        return query.all()
    
    def update_pattern_outcome(self, pattern_id: str, outcome: str, actual_return: float):
        """Update pattern with actual outcome"""
        pattern = self.session.query(DetectedPattern).filter_by(id=pattern_id).first()
        if pattern:
            pattern.pattern_completed = True  # type: ignore
            pattern.actual_outcome = outcome  # type: ignore
            pattern.actual_return = actual_return  # type: ignore
            pattern.updated_at = datetime.utcnow()  # type: ignore
            self.session.commit()
        return pattern
    
    def close(self):
        """Close database session"""
        self.session.close()

if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing Pattern Database...")
    engine, Session = init_database()
    print("✅ Pattern Database initialized successfully!")
    print(f"Tables created: {', '.join(Base.metadata.tables.keys())}")