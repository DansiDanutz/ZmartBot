"""Database configuration and SQLAlchemy models."""

import asyncio
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Index, create_engine
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from .settings import get_settings

Base = declarative_base()
settings = get_settings()


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, index=True)
    api_key = Column(String(255), unique=True, index=True)
    webhook_url = Column(String(500))
    max_alerts = Column(Integer, default=100)
    rate_limit_per_minute = Column(Integer, default=60)
    notification_channels = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class Alert(Base):
    """Alert model."""
    __tablename__ = "alerts"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    conditions = Column(JSON, nullable=False)
    message = Column(Text)
    webhook_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    max_triggers = Column(Integer)
    cooldown_minutes = Column(Integer, default=5)
    trigger_count = Column(Integer, default=0)
    last_trigger = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    triggers = relationship("AlertTrigger", back_populates="alert", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_user_symbol', 'user_id', 'symbol'),
        Index('idx_alert_active', 'is_active'),
        Index('idx_alert_expires', 'expires_at'),
    )


class AlertTrigger(Base):
    """Alert trigger history model."""
    __tablename__ = "alert_triggers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), ForeignKey("alerts.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)
    trigger_price = Column(Float, nullable=False)
    trigger_value = Column(Float)
    message = Column(Text)
    market_data = Column(JSON)
    technical_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = relationship("Alert", back_populates="triggers")
    
    # Indexes
    __table_args__ = (
        Index('idx_trigger_alert', 'alert_id'),
        Index('idx_trigger_symbol', 'symbol'),
        Index('idx_trigger_created', 'created_at'),
    )


class MarketDataHistory(Base):
    """Market data history model."""
    __tablename__ = "market_data_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    bid = Column(Float)
    ask = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    change_24h = Column(Float)
    change_percent_24h = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_market_symbol_time', 'symbol', 'timestamp'),
    )


class TechnicalIndicatorHistory(Base):
    """Technical indicators history model."""
    __tablename__ = "technical_indicators_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    ema_12 = Column(Float)
    ema_26 = Column(Float)
    volume_sma = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_technical_symbol_timeframe_time', 'symbol', 'timeframe', 'timestamp'),
    )


class NotificationLog(Base):
    """Notification delivery log model."""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), nullable=False)
    notification_type = Column(String(50), nullable=False)  # webhook, email, etc.
    destination = Column(String(500), nullable=False)
    payload = Column(JSON)
    status = Column(String(20), nullable=False)  # sent, failed, retry
    response_code = Column(Integer)
    response_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_alert', 'alert_id'),
        Index('idx_notification_status', 'status'),
        Index('idx_notification_created', 'created_at'),
    )


class SystemMetrics(Base):
    """System metrics model."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    active_alerts = Column(Integer, nullable=False)
    monitored_symbols = Column(Integer, nullable=False)
    triggers_last_hour = Column(Integer, nullable=False)
    avg_processing_time_ms = Column(Float, nullable=False)
    memory_usage_mb = Column(Float, nullable=False)
    cpu_usage_percent = Column(Float, nullable=False)
    uptime_seconds = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class DatabaseManager:
    """Database manager for handling connections and operations."""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
    
    async def initialize(self):
        """Initialize database connections."""
        # Create async engine
        self.async_engine = create_async_engine(
            settings.database.url.replace('sqlite://', 'sqlite+aiosqlite://'),
            echo=settings.database.echo,
            pool_pre_ping=True
        )
        
        # Create sync engine for migrations
        sync_url = settings.database.url
        if sync_url.startswith('sqlite+aiosqlite://'):
            sync_url = sync_url.replace('sqlite+aiosqlite://', 'sqlite://')
        
        self.engine = create_engine(sync_url, echo=settings.database.echo)
        
        # Create session factories
        self.AsyncSessionLocal = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        await self.create_tables()
    
    async def create_tables(self):
        """Create database tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all database tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_async_session(self) -> AsyncSession:
        """Get async database session."""
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    def get_sync_session(self):
        """Get sync database session."""
        with self.SessionLocal() as session:
            try:
                yield session
            finally:
                session.close()
    
    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncSession:
    """Dependency for getting database session."""
    async for session in db_manager.get_async_session():
        yield session


async def init_database():
    """Initialize database."""
    await db_manager.initialize()


async def close_database():
    """Close database connections."""
    await db_manager.close()

