"""
Diana Platform - Transactional Outbox Pattern
Reliable event publishing with guaranteed delivery and consistency
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

import asyncpg
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Gauge, Histogram

from ..messaging.event_bus import DianaEventBus, DianaEvent, EventPriority
from ..observability.telemetry import get_tracer, trace_function


# Metrics
outbox_events_created = Counter(
    'diana_outbox_events_created_total',
    'Total outbox events created',
    ['service', 'event_type']
)

outbox_events_processed = Counter(
    'diana_outbox_events_processed_total',
    'Total outbox events processed',
    ['service', 'event_type', 'status']
)

outbox_events_failed = Counter(
    'diana_outbox_events_failed_total',
    'Total outbox events failed',
    ['service', 'event_type', 'error_type']
)

outbox_processing_duration = Histogram(
    'diana_outbox_processing_duration_seconds',
    'Outbox event processing duration',
    ['service', 'event_type']
)

outbox_queue_size = Gauge(
    'diana_outbox_queue_size',
    'Current outbox queue size',
    ['service']
)

outbox_processor_lag = Gauge(
    'diana_outbox_processor_lag_seconds',
    'Outbox processor lag in seconds',
    ['service']
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


# Database models
Base = declarative_base()


class OutboxEvent(Base):
    """Outbox event database model"""
    __tablename__ = 'outbox_events'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    aggregate_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(255), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)
    
    # Metadata
    correlation_id = Column(String(255), nullable=True, index=True)
    source_service = Column(String(100), nullable=False, index=True)
    event_version = Column(String(20), default='1.0')
    
    # Routing and delivery
    routing_key = Column(String(255), nullable=False)
    exchange_name = Column(String(255), nullable=False)
    priority = Column(Integer, default=2)  # EventPriority.NORMAL
    
    # State tracking
    status = Column(String(20), default='pending', index=True)  # pending, processing, processed, failed
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True, index=True)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    
    # Error handling
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    
    # Partitioning support
    partition_key = Column(String(50), nullable=True, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_outbox_pending_events', 'status', 'next_retry_at', 'created_at'),
        Index('ix_outbox_correlation_id', 'correlation_id'),
        Index('ix_outbox_aggregate_type', 'aggregate_id', 'event_type'),
        Index('ix_outbox_service_status', 'source_service', 'status'),
    )


class EventProcessingStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class OutboxConfig:
    """Outbox pattern configuration"""
    database_url: str
    service_name: str
    
    # Processing configuration
    batch_size: int = 100
    processing_interval_seconds: int = 5
    max_retry_attempts: int = 3
    retry_backoff_multiplier: float = 2.0
    max_retry_delay_seconds: int = 300
    
    # Dead letter configuration
    dead_letter_after_retries: bool = True
    dead_letter_retention_days: int = 7
    
    # Performance tuning
    connection_pool_size: int = 10
    max_overflow: int = 20
    
    # Cleanup configuration
    cleanup_interval_hours: int = 24
    cleanup_processed_after_days: int = 7
    cleanup_failed_after_days: int = 30


@dataclass
class OutboxResult:
    """Result of outbox operation"""
    success: bool
    event_id: str
    error: Optional[str] = None
    retry_count: int = 0


class OutboxRepository:
    """Repository for outbox operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_event(
        self,
        aggregate_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        routing_key: str,
        exchange_name: str = "diana.events",
        correlation_id: str = None,
        source_service: str = "",
        priority: EventPriority = EventPriority.NORMAL,
        max_retries: int = 3
    ) -> OutboxEvent:
        """Create a new outbox event"""
        
        outbox_event = OutboxEvent(
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_data=event_data,
            routing_key=routing_key,
            exchange_name=exchange_name,
            correlation_id=correlation_id or str(uuid.uuid4()),
            source_service=source_service,
            priority=priority.value,
            max_retries=max_retries,
            partition_key=f"{source_service}:{aggregate_id}"
        )
        
        self.session.add(outbox_event)
        await self.session.flush()  # Get the ID without committing
        
        return outbox_event
    
    async def get_pending_events(
        self,
        batch_size: int = 100,
        service_name: str = None
    ) -> List[OutboxEvent]:
        """Get pending events for processing"""
        
        query = (
            sa.select(OutboxEvent)
            .where(
                OutboxEvent.status == EventProcessingStatus.PENDING.value,
                sa.or_(
                    OutboxEvent.next_retry_at.is_(None),
                    OutboxEvent.next_retry_at <= datetime.utcnow()
                )
            )
            .order_by(OutboxEvent.created_at)
            .limit(batch_size)
        )
        
        if service_name:
            query = query.where(OutboxEvent.source_service == service_name)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def mark_as_processing(self, event_ids: List[str]) -> None:
        """Mark events as processing"""
        await self.session.execute(
            sa.update(OutboxEvent)
            .where(OutboxEvent.id.in_(event_ids))
            .values(
                status=EventProcessingStatus.PROCESSING.value,
                processed_at=datetime.utcnow()
            )
        )
    
    async def mark_as_processed(self, event_id: str) -> None:
        """Mark event as successfully processed"""
        await self.session.execute(
            sa.update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=EventProcessingStatus.PROCESSED.value,
                processed_at=datetime.utcnow()
            )
        )
    
    async def mark_as_failed(
        self,
        event_id: str,
        error_message: str,
        increment_retry: bool = True
    ) -> None:
        """Mark event as failed and schedule retry"""
        
        # Get current event to calculate retry delay
        result = await self.session.execute(
            sa.select(OutboxEvent).where(OutboxEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return
        
        # Calculate next retry time with exponential backoff
        retry_count = event.retry_count + (1 if increment_retry else 0)
        
        if retry_count <= event.max_retries:
            # Schedule retry
            delay_seconds = min(
                2 ** retry_count,  # Exponential backoff
                300  # Max 5 minutes
            )
            next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            status = EventProcessingStatus.PENDING.value
        else:
            # Exceeded max retries
            next_retry_at = None
            status = EventProcessingStatus.DEAD_LETTER.value
        
        await self.session.execute(
            sa.update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=status,
                retry_count=retry_count,
                error_count=event.error_count + 1,
                last_error=error_message,
                next_retry_at=next_retry_at,
                processed_at=datetime.utcnow()
            )
        )
    
    async def get_queue_size(self, service_name: str = None) -> int:
        """Get current queue size"""
        query = sa.select(sa.func.count(OutboxEvent.id)).where(
            OutboxEvent.status == EventProcessingStatus.PENDING.value
        )
        
        if service_name:
            query = query.where(OutboxEvent.source_service == service_name)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def cleanup_old_events(
        self,
        processed_before: datetime,
        failed_before: datetime
    ) -> int:
        """Clean up old processed and failed events"""
        
        # Delete old processed events
        processed_result = await self.session.execute(
            sa.delete(OutboxEvent)
            .where(
                OutboxEvent.status == EventProcessingStatus.PROCESSED.value,
                OutboxEvent.processed_at < processed_before
            )
        )
        
        # Delete old failed events
        failed_result = await self.session.execute(
            sa.delete(OutboxEvent)
            .where(
                OutboxEvent.status.in_([
                    EventProcessingStatus.FAILED.value,
                    EventProcessingStatus.DEAD_LETTER.value
                ]),
                OutboxEvent.processed_at < failed_before
            )
        )
        
        return processed_result.rowcount + failed_result.rowcount


class DianaOutboxProcessor:
    """Diana Platform Outbox Processor"""
    
    def __init__(
        self,
        config: OutboxConfig,
        event_bus: DianaEventBus,
        engine: sa.ext.asyncio.AsyncEngine = None
    ):
        self.config = config
        self.event_bus = event_bus
        
        # Database setup
        if engine:
            self.engine = engine
        else:
            self.engine = create_async_engine(
                config.database_url,
                pool_size=config.connection_pool_size,
                max_overflow=config.max_overflow,
                echo=False
            )
        
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Processing control
        self.processing_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
        
        # Metrics tracking
        self.last_processing_time = time.time()
        
        logger.info(f"Diana Outbox Processor initialized for service '{config.service_name}'")
    
    async def start(self) -> None:
        """Start the outbox processor"""
        logger.info("Starting Diana Outbox Processor...")
        
        try:
            # Create database tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Start processing task
            self.processing_task = asyncio.create_task(self._processing_loop())
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Diana Outbox Processor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start outbox processor: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the outbox processor"""
        logger.info("Stopping Diana Outbox Processor...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            
            # Cancel tasks
            if self.processing_task and not self.processing_task.done():
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            if self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Close database connections
            await self.engine.dispose()
            
            logger.info("Diana Outbox Processor stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping outbox processor: {str(e)}")
    
    @trace_function("outbox_create_event")
    async def create_event(
        self,
        session: AsyncSession,
        aggregate_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        routing_key: str,
        **kwargs
    ) -> OutboxResult:
        """
        Create an outbox event within a database transaction
        
        This method should be called within an existing database transaction
        to ensure atomicity between business operations and event creation.
        """
        
        with tracer.start_as_current_span(f"create_outbox_event_{event_type}") as span:
            span.set_attributes({
                "outbox.aggregate_id": aggregate_id,
                "outbox.event_type": event_type,
                "outbox.routing_key": routing_key,
                "outbox.service": self.config.service_name
            })
            
            try:
                repo = OutboxRepository(session)
                
                outbox_event = await repo.create_event(
                    aggregate_id=aggregate_id,
                    event_type=event_type,
                    event_data=event_data,
                    routing_key=routing_key,
                    source_service=self.config.service_name,
                    **kwargs
                )
                
                # Update metrics
                outbox_events_created.labels(
                    service=self.config.service_name,
                    event_type=event_type
                ).inc()
                
                span.set_status(Status(StatusCode.OK))
                
                logger.debug(f"Created outbox event: {event_type} for aggregate {aggregate_id}")
                
                return OutboxResult(
                    success=True,
                    event_id=str(outbox_event.id)
                )
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to create outbox event: {str(e)}")
                
                return OutboxResult(
                    success=False,
                    event_id="",
                    error=str(e)
                )
    
    async def _processing_loop(self):
        """Main processing loop"""
        while not self.shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Process batch of events
                processed_count = await self._process_batch()
                
                # Update metrics
                processing_duration = time.time() - start_time
                self.last_processing_time = time.time()
                
                # Calculate lag
                lag = time.time() - self.last_processing_time
                outbox_processor_lag.labels(service=self.config.service_name).set(lag)
                
                if processed_count > 0:
                    logger.debug(f"Processed {processed_count} outbox events in {processing_duration:.2f}s")
                
                # Wait before next iteration
                await asyncio.sleep(self.config.processing_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in outbox processing loop: {str(e)}")
                await asyncio.sleep(self.config.processing_interval_seconds)
    
    async def _process_batch(self) -> int:
        """Process a batch of outbox events"""
        async with self.SessionLocal() as session:
            try:
                repo = OutboxRepository(session)
                
                # Get pending events
                pending_events = await repo.get_pending_events(
                    batch_size=self.config.batch_size,
                    service_name=self.config.service_name
                )
                
                if not pending_events:
                    # Update queue size metric
                    outbox_queue_size.labels(service=self.config.service_name).set(0)
                    return 0
                
                # Mark events as processing
                event_ids = [str(event.id) for event in pending_events]
                await repo.mark_as_processing(event_ids)
                await session.commit()
                
                # Update queue size metric
                queue_size = await repo.get_queue_size(self.config.service_name)
                outbox_queue_size.labels(service=self.config.service_name).set(queue_size)
                
                # Process each event
                processed_count = 0
                for event in pending_events:
                    try:
                        success = await self._process_event(event)
                        
                        if success:
                            await repo.mark_as_processed(str(event.id))
                            outbox_events_processed.labels(
                                service=self.config.service_name,
                                event_type=event.event_type,
                                status="success"
                            ).inc()
                            processed_count += 1
                        else:
                            await repo.mark_as_failed(
                                str(event.id),
                                "Event publishing failed"
                            )
                            outbox_events_processed.labels(
                                service=self.config.service_name,
                                event_type=event.event_type,
                                status="failed"
                            ).inc()
                            
                    except Exception as e:
                        await repo.mark_as_failed(str(event.id), str(e))
                        outbox_events_failed.labels(
                            service=self.config.service_name,
                            event_type=event.event_type,
                            error_type=type(e).__name__
                        ).inc()
                
                await session.commit()
                return processed_count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing outbox batch: {str(e)}")
                return 0
    
    async def _process_event(self, outbox_event: OutboxEvent) -> bool:
        """Process a single outbox event"""
        
        with tracer.start_as_current_span(f"process_outbox_event_{outbox_event.event_type}") as span:
            span.set_attributes({
                "outbox.event_id": str(outbox_event.id),
                "outbox.aggregate_id": outbox_event.aggregate_id,
                "outbox.event_type": outbox_event.event_type,
                "outbox.retry_count": outbox_event.retry_count
            })
            
            start_time = time.time()
            
            try:
                # Create Diana event
                diana_event = DianaEvent(
                    event_type=outbox_event.event_type,
                    data=outbox_event.event_data,
                )
                
                # Set metadata
                diana_event.metadata.event_id = str(outbox_event.id)
                diana_event.metadata.correlation_id = outbox_event.correlation_id
                diana_event.metadata.source_service = outbox_event.source_service
                diana_event.metadata.priority = EventPriority(outbox_event.priority)
                diana_event.metadata.retry_count = outbox_event.retry_count
                diana_event.metadata.timestamp = outbox_event.created_at
                
                # Publish event
                success = await self.event_bus.publish_event(
                    diana_event,
                    routing_key=outbox_event.routing_key,
                    exchange_name=outbox_event.exchange_name
                )
                
                # Record processing time
                duration = time.time() - start_time
                outbox_processing_duration.labels(
                    service=self.config.service_name,
                    event_type=outbox_event.event_type
                ).observe(duration)
                
                if success:
                    span.set_status(Status(StatusCode.OK))
                    logger.debug(f"Published outbox event {outbox_event.event_type}")
                else:
                    span.set_status(Status(StatusCode.ERROR, "Publishing failed"))
                
                return success
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to process outbox event {outbox_event.id}: {str(e)}")
                return False
    
    async def _cleanup_loop(self):
        """Cleanup old events periodically"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval_hours * 3600)
                
                if self.shutdown_event.is_set():
                    break
                
                await self._cleanup_old_events()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
    
    async def _cleanup_old_events(self):
        """Clean up old processed and failed events"""
        async with self.SessionLocal() as session:
            try:
                repo = OutboxRepository(session)
                
                # Calculate cleanup timestamps
                now = datetime.utcnow()
                processed_before = now - timedelta(days=self.config.cleanup_processed_after_days)
                failed_before = now - timedelta(days=self.config.cleanup_failed_after_days)
                
                # Perform cleanup
                deleted_count = await repo.cleanup_old_events(processed_before, failed_before)
                await session.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old outbox events")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error during outbox cleanup: {str(e)}")
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


# High-level integration class
class TransactionalOutbox:
    """High-level transactional outbox integration"""
    
    def __init__(
        self,
        config: OutboxConfig,
        event_bus: DianaEventBus,
        session_factory: async_sessionmaker
    ):
        self.config = config
        self.event_bus = event_bus
        self.session_factory = session_factory
        self.processor = DianaOutboxProcessor(config, event_bus)
    
    async def start(self):
        """Start the outbox system"""
        await self.processor.start()
    
    async def stop(self):
        """Stop the outbox system"""
        await self.processor.stop()
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for transactional operations with outbox support
        
        Usage:
            async with outbox.transaction() as tx:
                # Perform business operations
                await tx.session.execute(...)
                
                # Create outbox events
                await tx.create_event(
                    aggregate_id="user-123",
                    event_type="user.created",
                    event_data={"user_id": "123"},
                    routing_key="user.created"
                )
        """
        async with self.session_factory() as session:
            async with session.begin():
                tx = OutboxTransaction(session, self.processor)
                try:
                    yield tx
                except Exception:
                    await session.rollback()
                    raise
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


@dataclass
class OutboxTransaction:
    """Transactional context with outbox support"""
    session: AsyncSession
    processor: DianaOutboxProcessor
    
    async def create_event(
        self,
        aggregate_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        routing_key: str,
        **kwargs
    ) -> OutboxResult:
        """Create an outbox event within the current transaction"""
        return await self.processor.create_event(
            self.session,
            aggregate_id,
            event_type,
            event_data,
            routing_key,
            **kwargs
        )


# Factory functions
def create_outbox_config(
    database_url: str,
    service_name: str,
    **kwargs
) -> OutboxConfig:
    """Create outbox configuration"""
    return OutboxConfig(
        database_url=database_url,
        service_name=service_name,
        **kwargs
    )


async def create_outbox_processor(
    config: OutboxConfig,
    event_bus: DianaEventBus
) -> DianaOutboxProcessor:
    """Create and start outbox processor"""
    processor = DianaOutboxProcessor(config, event_bus)
    await processor.start()
    return processor


async def create_transactional_outbox(
    config: OutboxConfig,
    event_bus: DianaEventBus,
    engine: sa.ext.asyncio.AsyncEngine
) -> TransactionalOutbox:
    """Create transactional outbox with session factory"""
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    outbox = TransactionalOutbox(config, event_bus, session_factory)
    await outbox.start()
    return outbox