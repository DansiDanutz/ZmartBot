"""
Diana Platform - Event-Driven Messaging System
Enterprise event bus with RabbitMQ, dead letter queues, and guaranteed delivery
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

import aio_pika
from aio_pika import ExchangeType, DeliveryMode, Message
from aio_pika.pool import Pool
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, Gauge

from ..core.http_client import CircuitBreaker, CircuitBreakerConfig


# Metrics
events_published_total = Counter(
    'diana_events_published_total',
    'Total events published',
    ['service', 'event_type', 'exchange']
)

events_consumed_total = Counter(
    'diana_events_consumed_total', 
    'Total events consumed',
    ['service', 'event_type', 'queue', 'status']
)

event_processing_duration = Histogram(
    'diana_event_processing_duration_seconds',
    'Event processing duration',
    ['service', 'event_type', 'handler']
)

active_consumers = Gauge(
    'diana_active_consumers',
    'Number of active event consumers',
    ['service', 'queue']
)

dead_letter_queue_size = Gauge(
    'diana_dead_letter_queue_size',
    'Dead letter queue size',
    ['service', 'queue']
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


@dataclass
class EventMetadata:
    """Event metadata for tracking and correlation"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source_service: str = ""
    event_version: str = "1.0"
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None
    headers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DianaEvent:
    """Standard Diana platform event"""
    event_type: str
    data: Dict[str, Any]
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'data': self.data,
            'metadata': {
                'event_id': self.metadata.event_id,
                'correlation_id': self.metadata.correlation_id,
                'timestamp': self.metadata.timestamp.isoformat(),
                'source_service': self.metadata.source_service,
                'event_version': self.metadata.event_version,
                'priority': self.metadata.priority.value,
                'retry_count': self.metadata.retry_count,
                'max_retries': self.metadata.max_retries,
                'ttl_seconds': self.metadata.ttl_seconds,
                'headers': self.metadata.headers
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DianaEvent':
        """Create event from dictionary"""
        metadata_dict = data.get('metadata', {})
        
        # Parse timestamp
        timestamp_str = metadata_dict.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')) if timestamp_str else datetime.now()
        
        metadata = EventMetadata(
            event_id=metadata_dict.get('event_id', str(uuid.uuid4())),
            correlation_id=metadata_dict.get('correlation_id', str(uuid.uuid4())),
            timestamp=timestamp,
            source_service=metadata_dict.get('source_service', ''),
            event_version=metadata_dict.get('event_version', '1.0'),
            priority=EventPriority(metadata_dict.get('priority', EventPriority.NORMAL.value)),
            retry_count=metadata_dict.get('retry_count', 0),
            max_retries=metadata_dict.get('max_retries', 3),
            ttl_seconds=metadata_dict.get('ttl_seconds'),
            headers=metadata_dict.get('headers', {})
        )
        
        return cls(
            event_type=data['event_type'],
            data=data['data'],
            metadata=metadata
        )


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: DianaEvent) -> bool:
        """
        Handle an event
        
        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_event_types(self) -> List[str]:
        """Get list of event types this handler can process"""
        pass
    
    def get_handler_name(self) -> str:
        """Get handler name for metrics and logging"""
        return self.__class__.__name__


@dataclass
class QueueConfig:
    """Queue configuration"""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    max_length: Optional[int] = None
    max_priority: int = 4
    message_ttl: Optional[int] = None
    dead_letter_exchange: Optional[str] = None
    dead_letter_routing_key: Optional[str] = None


@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    type: ExchangeType = ExchangeType.TOPIC
    durable: bool = True
    auto_delete: bool = False


@dataclass
class EventBusConfig:
    """Event bus configuration"""
    rabbitmq_url: str
    service_name: str
    connection_pool_size: int = 10
    channel_pool_size: int = 20
    prefetch_count: int = 10
    circuit_breaker: Optional[CircuitBreakerConfig] = field(default_factory=CircuitBreakerConfig)
    
    # Default exchanges
    events_exchange: str = "diana.events"
    dead_letter_exchange: str = "diana.dead_letter"
    
    # Retry configuration
    max_retry_delay: int = 300  # 5 minutes
    retry_multiplier: float = 2.0
    
    # Health check configuration
    health_check_interval: int = 30


class DianaEventBus:
    """Enterprise event bus with RabbitMQ backend"""
    
    def __init__(self, config: EventBusConfig):
        self.config = config
        self.service_name = config.service_name
        self.connection_pool: Optional[Pool] = None
        self.channel_pool: Optional[Pool] = None
        self.circuit_breaker = CircuitBreaker(
            f"{config.service_name}-eventbus", 
            config.circuit_breaker
        ) if config.circuit_breaker else None
        
        # Event handlers registry
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.active_consumers: Dict[str, asyncio.Task] = {}
        
        # Exchanges and queues
        self.exchanges: Dict[str, aio_pika.Exchange] = {}
        self.queues: Dict[str, aio_pika.Queue] = {}
        
        # Shutdown event
        self.shutdown_event = asyncio.Event()
        
        logger.info(f"Diana Event Bus initialized for service '{self.service_name}'")
    
    async def start(self) -> None:
        """Start the event bus"""
        logger.info(f"Starting Diana Event Bus for '{self.service_name}'...")
        
        try:
            # Create connection pool
            async def get_connection():
                return await aio_pika.connect_robust(
                    self.config.rabbitmq_url,
                    client_properties={
                        "connection_name": f"{self.service_name}-{uuid.uuid4()}",
                        "service": self.service_name
                    }
                )
            
            self.connection_pool = Pool(
                get_connection,
                max_size=self.config.connection_pool_size
            )
            
            # Create channel pool
            async def get_channel():
                async with self.connection_pool.acquire() as connection:
                    channel = await connection.channel()
                    await channel.set_qos(prefetch_count=self.config.prefetch_count)
                    return channel
            
            self.channel_pool = Pool(
                get_channel,
                max_size=self.config.channel_pool_size
            )
            
            # Setup default exchanges
            await self._setup_exchanges()
            
            logger.info(f"Diana Event Bus started successfully for '{self.service_name}'")
            
        except Exception as e:
            logger.error(f"Failed to start event bus: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the event bus"""
        logger.info(f"Stopping Diana Event Bus for '{self.service_name}'...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            
            # Stop all consumers
            for queue_name, task in self.active_consumers.items():
                logger.info(f"Stopping consumer for queue '{queue_name}'")
                task.cancel()
            
            # Wait for consumers to finish
            if self.active_consumers:
                await asyncio.gather(*self.active_consumers.values(), return_exceptions=True)
            
            self.active_consumers.clear()
            
            # Close pools
            if self.channel_pool:
                await self.channel_pool.close()
            
            if self.connection_pool:
                await self.connection_pool.close()
            
            logger.info(f"Diana Event Bus stopped successfully for '{self.service_name}'")
            
        except Exception as e:
            logger.error(f"Error stopping event bus: {str(e)}")
            raise
    
    async def _setup_exchanges(self):
        """Setup default exchanges"""
        async with self.channel_pool.acquire() as channel:
            # Events exchange
            self.exchanges[self.config.events_exchange] = await channel.declare_exchange(
                self.config.events_exchange,
                ExchangeType.TOPIC,
                durable=True
            )
            
            # Dead letter exchange
            self.exchanges[self.config.dead_letter_exchange] = await channel.declare_exchange(
                self.config.dead_letter_exchange,
                ExchangeType.DIRECT,
                durable=True
            )
            
            logger.info("Default exchanges created successfully")
    
    async def publish_event(
        self,
        event: DianaEvent,
        routing_key: str,
        exchange_name: str = None
    ) -> bool:
        """Publish an event to the event bus"""
        
        exchange_name = exchange_name or self.config.events_exchange
        event.metadata.source_service = self.service_name
        
        with tracer.start_as_current_span(f"publish_event_{event.event_type}") as span:
            span.set_attributes({
                "event.type": event.event_type,
                "event.id": event.metadata.event_id,
                "event.correlation_id": event.metadata.correlation_id,
                "event.source_service": event.metadata.source_service,
                "event.priority": event.metadata.priority.name,
                "messaging.exchange": exchange_name,
                "messaging.routing_key": routing_key
            })
            
            try:
                if self.circuit_breaker:
                    success = await self.circuit_breaker.call(
                        self._do_publish, event, routing_key, exchange_name
                    )
                else:
                    success = await self._do_publish(event, routing_key, exchange_name)
                
                if success:
                    events_published_total.labels(
                        service=self.service_name,
                        event_type=event.event_type,
                        exchange=exchange_name
                    ).inc()
                    
                    span.set_status(Status(StatusCode.OK))
                    logger.debug(f"Event published: {event.event_type} -> {routing_key}")
                else:
                    span.set_status(Status(StatusCode.ERROR, "Publish failed"))
                
                return success
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to publish event {event.event_type}: {str(e)}")
                raise
    
    async def _do_publish(
        self,
        event: DianaEvent,
        routing_key: str,
        exchange_name: str
    ) -> bool:
        """Internal method to publish event"""
        try:
            async with self.channel_pool.acquire() as channel:
                exchange = self.exchanges.get(exchange_name)
                if not exchange:
                    exchange = await channel.get_exchange(exchange_name)
                    self.exchanges[exchange_name] = exchange
                
                # Create message
                message_body = json.dumps(event.to_dict()).encode('utf-8')
                
                # Set message properties
                properties = {
                    'delivery_mode': DeliveryMode.PERSISTENT,
                    'priority': event.metadata.priority.value,
                    'message_id': event.metadata.event_id,
                    'correlation_id': event.metadata.correlation_id,
                    'timestamp': event.metadata.timestamp,
                    'headers': {
                        'event_type': event.event_type,
                        'source_service': event.metadata.source_service,
                        'event_version': event.metadata.event_version,
                        **event.metadata.headers
                    }
                }
                
                if event.metadata.ttl_seconds:
                    properties['expiration'] = str(event.metadata.ttl_seconds * 1000)
                
                message = Message(message_body, **properties)
                
                # Publish message
                await exchange.publish(message, routing_key=routing_key)
                
                return True
                
        except Exception as e:
            logger.error(f"Internal publish error: {str(e)}")
            return False
    
    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler"""
        for event_type in handler.get_event_types():
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            
            self.handlers[event_type].append(handler)
            logger.info(f"Registered handler '{handler.get_handler_name()}' for event type '{event_type}'")
    
    async def start_consuming(
        self,
        queue_name: str,
        routing_keys: List[str],
        exchange_name: str = None
    ) -> None:
        """Start consuming events from a queue"""
        
        exchange_name = exchange_name or self.config.events_exchange
        
        if queue_name in self.active_consumers:
            logger.warning(f"Consumer for queue '{queue_name}' is already active")
            return
        
        # Create dead letter queue
        dl_queue_name = f"{queue_name}.dead_letter"
        
        async with self.channel_pool.acquire() as channel:
            # Create dead letter queue
            dl_queue = await channel.declare_queue(
                dl_queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': 86400000,  # 24 hours
                    'x-expires': 7 * 86400000   # 7 days
                }
            )
            
            # Bind dead letter queue to dead letter exchange
            await dl_queue.bind(self.exchanges[self.config.dead_letter_exchange], routing_key=queue_name)
            
            # Create main queue with dead letter configuration
            queue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': self.config.dead_letter_exchange,
                    'x-dead-letter-routing-key': queue_name,
                    'x-max-priority': 4
                }
            )
            
            # Bind queue to exchange with routing keys
            exchange = self.exchanges[exchange_name]
            for routing_key in routing_keys:
                await queue.bind(exchange, routing_key=routing_key)
            
            self.queues[queue_name] = queue
        
        # Start consumer task
        consumer_task = asyncio.create_task(
            self._consume_messages(queue_name)
        )
        
        self.active_consumers[queue_name] = consumer_task
        
        # Update metrics
        active_consumers.labels(service=self.service_name, queue=queue_name).set(1)
        
        logger.info(f"Started consuming from queue '{queue_name}' with routing keys: {routing_keys}")
    
    async def _consume_messages(self, queue_name: str):
        """Internal message consumer"""
        queue = self.queues[queue_name]
        
        try:
            async with self.channel_pool.acquire() as channel:
                # Get fresh queue reference from channel
                queue = await channel.get_queue(queue_name)
                
                async for message in queue:
                    if self.shutdown_event.is_set():
                        break
                    
                    await self._process_message(message, queue_name)
                    
        except asyncio.CancelledError:
            logger.info(f"Consumer for queue '{queue_name}' was cancelled")
        except Exception as e:
            logger.error(f"Consumer error for queue '{queue_name}': {str(e)}")
        finally:
            # Update metrics
            active_consumers.labels(service=self.service_name, queue=queue_name).set(0)
    
    async def _process_message(self, message: aio_pika.IncomingMessage, queue_name: str):
        """Process a single message"""
        start_time = time.time()
        event = None
        
        try:
            # Parse event
            message_data = json.loads(message.body.decode('utf-8'))
            event = DianaEvent.from_dict(message_data)
            
            with tracer.start_as_current_span(f"process_event_{event.event_type}") as span:
                span.set_attributes({
                    "event.type": event.event_type,
                    "event.id": event.metadata.event_id,
                    "event.correlation_id": event.metadata.correlation_id,
                    "event.source_service": event.metadata.source_service,
                    "messaging.queue": queue_name,
                    "messaging.retry_count": event.metadata.retry_count
                })
                
                # Find handlers for this event type
                handlers = self.handlers.get(event.event_type, [])
                
                if not handlers:
                    logger.warning(f"No handlers found for event type '{event.event_type}'")
                    await message.ack()
                    return
                
                # Process with all handlers
                all_success = True
                for handler in handlers:
                    try:
                        handler_start = time.time()
                        success = await handler.handle(event)
                        handler_duration = time.time() - handler_start
                        
                        # Record handler metrics
                        event_processing_duration.labels(
                            service=self.service_name,
                            event_type=event.event_type,
                            handler=handler.get_handler_name()
                        ).observe(handler_duration)
                        
                        if success:
                            events_consumed_total.labels(
                                service=self.service_name,
                                event_type=event.event_type,
                                queue=queue_name,
                                status="success"
                            ).inc()
                        else:
                            all_success = False
                            events_consumed_total.labels(
                                service=self.service_name,
                                event_type=event.event_type,
                                queue=queue_name,
                                status="handler_failed"
                            ).inc()
                            
                    except Exception as e:
                        all_success = False
                        logger.error(f"Handler '{handler.get_handler_name()}' failed for event {event.event_type}: {str(e)}")
                        
                        events_consumed_total.labels(
                            service=self.service_name,
                            event_type=event.event_type,
                            queue=queue_name,
                            status="handler_error"
                        ).inc()
                
                if all_success:
                    await message.ack()
                    span.set_status(Status(StatusCode.OK))
                else:
                    # Check retry logic
                    if event.metadata.retry_count < event.metadata.max_retries:
                        await self._retry_message(message, event)
                    else:
                        # Send to dead letter queue
                        await message.reject(requeue=False)
                        logger.error(f"Event {event.event_type} sent to dead letter queue after {event.metadata.retry_count} retries")
                        
                        events_consumed_total.labels(
                            service=self.service_name,
                            event_type=event.event_type,
                            queue=queue_name,
                            status="dead_letter"
                        ).inc()
                    
                    span.set_status(Status(StatusCode.ERROR, "Processing failed"))
                
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")
            
            events_consumed_total.labels(
                service=self.service_name,
                event_type=event.event_type if event else "unknown",
                queue=queue_name,
                status="parse_error"
            ).inc()
            
            await message.reject(requeue=False)
        
        finally:
            duration = time.time() - start_time
            logger.debug(f"Message processed in {duration:.3f}s")
    
    async def _retry_message(self, message: aio_pika.IncomingMessage, event: DianaEvent):
        """Retry message with exponential backoff"""
        event.metadata.retry_count += 1
        
        # Calculate delay
        delay = min(
            self.config.retry_multiplier ** event.metadata.retry_count,
            self.config.max_retry_delay
        )
        
        # Republish with delay
        retry_routing_key = f"retry.{delay}.{event.event_type}"
        
        success = await self.publish_event(event, retry_routing_key)
        
        if success:
            await message.ack()
            logger.info(f"Event {event.event_type} scheduled for retry #{event.metadata.retry_count} in {delay}s")
        else:
            await message.reject(requeue=True)
            logger.error(f"Failed to schedule retry for event {event.event_type}")
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


# Factory functions
def create_event_bus_config(
    rabbitmq_url: str,
    service_name: str,
    **kwargs
) -> EventBusConfig:
    """Create event bus configuration"""
    return EventBusConfig(
        rabbitmq_url=rabbitmq_url,
        service_name=service_name,
        **kwargs
    )


def create_event(
    event_type: str,
    data: Dict[str, Any],
    correlation_id: str = None,
    priority: EventPriority = EventPriority.NORMAL,
    **metadata_kwargs
) -> DianaEvent:
    """Create a Diana event"""
    metadata = EventMetadata(
        correlation_id=correlation_id or str(uuid.uuid4()),
        priority=priority,
        **metadata_kwargs
    )
    
    return DianaEvent(
        event_type=event_type,
        data=data,
        metadata=metadata
    )