#!/usr/bin/env python3
"""
Transactional Outbox Pattern Implementation for KingFisher
Ensures reliable event publishing even when RabbitMQ is temporarily unavailable
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncpg
import aio_pika
from aio_pika import Message

logger = logging.getLogger(__name__)

@dataclass
class OutboxEvent:
    """Represents an event in the outbox"""
    id: str
    event_type: str
    payload: Dict[str, Any]
    routing_key: str
    exchange: str = "kingfisher"
    created_at: datetime = None
    published_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 5
    next_attempt: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class TransactionalOutbox:
    """Transactional outbox for reliable event publishing"""
    
    def __init__(self, db_pool: asyncpg.Pool, rabbitmq_url: str):
        self.db_pool = db_pool
        self.rabbitmq_url = rabbitmq_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.is_running = False
        self.publisher_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the outbox publisher"""
        if self.is_running:
            logger.warning("Outbox publisher already running")
            return
            
        logger.info("🚀 Starting transactional outbox publisher")
        
        # Create outbox table if it doesn't exist
        await self._ensure_outbox_table()
        
        # Start the publisher loop
        self.is_running = True
        self.publisher_task = asyncio.create_task(self._publisher_loop())
        
        logger.info("✅ Transactional outbox publisher started")
    
    async def stop(self):
        """Stop the outbox publisher"""
        if not self.is_running:
            return
            
        logger.info("🛑 Stopping transactional outbox publisher")
        
        self.is_running = False
        
        if self.publisher_task:
            self.publisher_task.cancel()
            try:
                await self.publisher_task
            except asyncio.CancelledError:
                pass
        
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
            
        logger.info("✅ Transactional outbox publisher stopped")
    
    async def publish_event(self, event_type: str, payload: Dict[str, Any], 
                           routing_key: str, exchange: str = "kingfisher", 
                           conn: Optional[asyncpg.Connection] = None) -> str:
        """
        Publish an event through the transactional outbox
        
        Args:
            event_type: Type of event (e.g., 'kingfisher.image.downloaded.v1')
            payload: Event payload
            routing_key: RabbitMQ routing key
            exchange: RabbitMQ exchange name
            conn: Existing database connection (for transactional publishing)
            
        Returns:
            Event ID
        """
        event = OutboxEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            payload=payload,
            routing_key=routing_key,
            exchange=exchange
        )
        
        # Insert into outbox table
        query = """
            INSERT INTO kingfisher.events_outbox 
            (id, event_type, payload, routing_key, exchange, created_at, attempts, max_attempts)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        values = (
            event.id,
            event.event_type,
            json.dumps(event.payload),
            event.routing_key,
            event.exchange,
            event.created_at,
            event.attempts,
            event.max_attempts
        )
        
        if conn:
            # Use existing transaction
            await conn.execute(query, *values)
        else:
            # Create new transaction
            async with self.db_pool.acquire() as connection:
                await connection.execute(query, *values)
        
        logger.info(f"📝 Event queued in outbox: {event.event_type} ({event.id})")
        return event.id
    
    async def _ensure_outbox_table(self):
        """Ensure the outbox table exists"""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS kingfisher.events_outbox (
                id UUID PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                payload JSONB NOT NULL,
                routing_key VARCHAR(100) NOT NULL,
                exchange VARCHAR(50) NOT NULL DEFAULT 'kingfisher',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                published_at TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,
                next_attempt TIMESTAMP,
                error_message TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_outbox_unpublished 
            ON kingfisher.events_outbox (published_at) 
            WHERE published_at IS NULL;
            
            CREATE INDEX IF NOT EXISTS idx_outbox_retry 
            ON kingfisher.events_outbox (next_attempt) 
            WHERE published_at IS NULL AND next_attempt IS NOT NULL;
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_table_query)
            
        logger.debug("✅ Outbox table ensured")
    
    async def _publisher_loop(self):
        """Main publisher loop that processes outbox events"""
        logger.info("🔄 Starting outbox publisher loop")
        
        while self.is_running:
            try:
                # Ensure RabbitMQ connection
                await self._ensure_rabbitmq_connection()
                
                # Process pending events
                await self._process_pending_events()
                
                # Clean up old published events
                await self._cleanup_old_events()
                
                # Sleep before next iteration
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in publisher loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _ensure_rabbitmq_connection(self):
        """Ensure RabbitMQ connection is established"""
        if self.connection and not self.connection.is_closed:
            return
            
        try:
            logger.info("🔌 Connecting to RabbitMQ")
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Declare exchange
            await self.channel.declare_exchange(
                "kingfisher", 
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            logger.info("✅ RabbitMQ connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            raise
    
    async def _process_pending_events(self):
        """Process all pending events in the outbox"""
        if not self.channel:
            logger.warning("No RabbitMQ channel available, skipping event processing")
            return
            
        # Get pending events
        query = """
            SELECT id, event_type, payload, routing_key, exchange, created_at, attempts, max_attempts
            FROM kingfisher.events_outbox 
            WHERE published_at IS NULL 
            AND (next_attempt IS NULL OR next_attempt <= NOW())
            ORDER BY created_at ASC
            LIMIT 100
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            for row in rows:
                try:
                    event = OutboxEvent(
                        id=str(row['id']),
                        event_type=row['event_type'],
                        payload=json.loads(row['payload']),
                        routing_key=row['routing_key'],
                        exchange=row['exchange'],
                        created_at=row['created_at'],
                        attempts=row['attempts'],
                        max_attempts=row['max_attempts']
                    )
                    
                    await self._publish_event(event, conn)
                    
                except Exception as e:
                    logger.error(f"Error processing event {row['id']}: {e}")
                    await self._handle_publish_error(row['id'], str(e), conn)
    
    async def _publish_event(self, event: OutboxEvent, conn: asyncpg.Connection):
        """Publish a single event to RabbitMQ"""
        try:
            # Create message
            message_body = json.dumps({
                "event_id": event.id,
                "event_type": event.event_type,
                "timestamp": event.created_at.isoformat(),
                "payload": event.payload
            })
            
            message = Message(
                message_body.encode(),
                content_type="application/json",
                message_id=event.id,
                timestamp=event.created_at,
                headers={
                    "event_type": event.event_type,
                    "source": "kingfisher",
                    "version": "v1"
                }
            )
            
            # Get exchange
            exchange = await self.channel.get_exchange(event.exchange)
            
            # Publish message
            await exchange.publish(message, routing_key=event.routing_key)
            
            # Mark as published
            await conn.execute("""
                UPDATE kingfisher.events_outbox 
                SET published_at = NOW(), attempts = attempts + 1
                WHERE id = $1
            """, uuid.UUID(event.id))
            
            logger.info(f"📤 Event published: {event.event_type} ({event.id})")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.id}: {e}")
            raise
    
    async def _handle_publish_error(self, event_id: str, error_message: str, 
                                   conn: asyncpg.Connection):
        """Handle publish error with retry logic"""
        # Get current event state
        row = await conn.fetchrow("""
            SELECT attempts, max_attempts FROM kingfisher.events_outbox 
            WHERE id = $1
        """, uuid.UUID(event_id))
        
        if not row:
            logger.error(f"Event {event_id} not found for error handling")
            return
            
        attempts = row['attempts'] + 1
        max_attempts = row['max_attempts']
        
        if attempts >= max_attempts:
            # Max attempts reached - mark as failed
            await conn.execute("""
                UPDATE kingfisher.events_outbox 
                SET attempts = $1, error_message = $2, next_attempt = NULL
                WHERE id = $3
            """, attempts, error_message, uuid.UUID(event_id))
            
            logger.error(f"❌ Event {event_id} failed permanently after {attempts} attempts")
        else:
            # Schedule retry with exponential backoff
            retry_delay = min(2 ** attempts, 300)  # Max 5 minutes
            next_attempt = datetime.utcnow() + timedelta(seconds=retry_delay)
            
            await conn.execute("""
                UPDATE kingfisher.events_outbox 
                SET attempts = $1, error_message = $2, next_attempt = $3
                WHERE id = $4
            """, attempts, error_message, next_attempt, uuid.UUID(event_id))
            
            logger.warning(f"⏰ Event {event_id} scheduled for retry in {retry_delay}s (attempt {attempts}/{max_attempts})")
    
    async def _cleanup_old_events(self):
        """Clean up old published events"""
        try:
            # Remove events published more than 7 days ago
            cleanup_query = """
                DELETE FROM kingfisher.events_outbox 
                WHERE published_at IS NOT NULL 
                AND published_at < NOW() - INTERVAL '7 days'
            """
            
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(cleanup_query)
                
                # Parse result to get row count
                if result.startswith('DELETE '):
                    deleted_count = int(result.split(' ')[1])
                    if deleted_count > 0:
                        logger.info(f"🧹 Cleaned up {deleted_count} old published events")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old events: {e}")
    
    async def get_outbox_stats(self) -> Dict[str, Any]:
        """Get outbox statistics"""
        query = """
            SELECT 
                COUNT(*) as total_events,
                COUNT(*) FILTER (WHERE published_at IS NULL) as pending_events,
                COUNT(*) FILTER (WHERE published_at IS NOT NULL) as published_events,
                COUNT(*) FILTER (WHERE attempts >= max_attempts AND published_at IS NULL) as failed_events,
                COUNT(*) FILTER (WHERE next_attempt > NOW() AND published_at IS NULL) as retrying_events
            FROM kingfisher.events_outbox
        """
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query)
            
            return {
                "total_events": row['total_events'],
                "pending_events": row['pending_events'], 
                "published_events": row['published_events'],
                "failed_events": row['failed_events'],
                "retrying_events": row['retrying_events'],
                "publisher_running": self.is_running,
                "rabbitmq_connected": bool(self.connection and not self.connection.is_closed),
                "last_check": datetime.utcnow().isoformat()
            }


# Convenience functions for common events
class KingfisherEvents:
    """Helper class for publishing KingFisher-specific events"""
    
    def __init__(self, outbox: TransactionalOutbox):
        self.outbox = outbox
    
    async def image_downloaded(self, image_path: str, symbol: str, source: str = "telegram",
                              conn: Optional[asyncpg.Connection] = None) -> str:
        """Publish image downloaded event"""
        payload = {
            "image_path": image_path,
            "symbol": symbol,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.outbox.publish_event(
            event_type="kingfisher.image.downloaded.v1",
            payload=payload,
            routing_key="kingfisher.image.downloaded",
            conn=conn
        )
    
    async def image_deduplicated(self, image_path: str, duplicate_of: str,
                                conn: Optional[asyncpg.Connection] = None) -> str:
        """Publish image deduplicated event"""
        payload = {
            "image_path": image_path,
            "duplicate_of": duplicate_of,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.outbox.publish_event(
            event_type="kingfisher.image.deduplicated.v1", 
            payload=payload,
            routing_key="kingfisher.image.deduplicated",
            conn=conn
        )
    
    async def analysis_completed(self, symbol: str, analysis_data: Dict[str, Any],
                                conn: Optional[asyncpg.Connection] = None) -> str:
        """Publish analysis completed event"""
        payload = {
            "symbol": symbol,
            "analysis_data": analysis_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.outbox.publish_event(
            event_type="kingfisher.analysis.completed.v1",
            payload=payload,
            routing_key="kingfisher.analysis.completed",
            conn=conn
        )
    
    async def report_generated(self, symbol: str, report_id: str, report_type: str,
                              conn: Optional[asyncpg.Connection] = None) -> str:
        """Publish report generated event"""
        payload = {
            "symbol": symbol,
            "report_id": report_id,
            "report_type": report_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.outbox.publish_event(
            event_type="kingfisher.report.generated.v1",
            payload=payload,
            routing_key="kingfisher.report.generated", 
            conn=conn
        )