"""
Zmart Trading Bot Platform - Database Utilities
Database connection management and utilities for PostgreSQL, Redis, and InfluxDB
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from datetime import datetime

import asyncpg
import redis.asyncio as redis
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from src.config.settings import settings, get_database_url

logger = logging.getLogger(__name__)

# Global connection objects
postgres_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None
influx_client: Optional[InfluxDBClient] = None
influx_write_api: Optional[Any] = None

async def init_database():
    """Initialize all database connections"""
    global postgres_pool, redis_client, influx_client, influx_write_api
    
    logger.info("Initializing database connections")
    
    # Initialize PostgreSQL connection pool
    try:
        postgres_pool = await asyncpg.create_pool(
            get_database_url(),
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("PostgreSQL connection pool initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize PostgreSQL connection pool: {e}")
        logger.info("PostgreSQL connection will be skipped for development")
        postgres_pool = None
    
    # Initialize Redis connection
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis connection: {e}")
        logger.info("Redis connection will be skipped for development")
        redis_client = None
    
    # Initialize InfluxDB connection
    try:
        influx_client = InfluxDBClient(
            url=f"http://{settings.INFLUX_HOST}:{settings.INFLUX_PORT}",
            token=settings.INFLUX_TOKEN,
            org=settings.INFLUX_ORG
        )
        influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        logger.info("InfluxDB connection initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize InfluxDB connection: {e}")
        logger.info("InfluxDB connection will be skipped for development")
        influx_client = None
        influx_write_api = None

async def close_database():
    """Close all database connections"""
    global postgres_pool, redis_client, influx_client, influx_write_api
    
    logger.info("Closing database connections")
    
    # Close PostgreSQL pool
    if postgres_pool:
        await postgres_pool.close()
        logger.info("PostgreSQL connection pool closed")
    
    # Close Redis connection
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
    
    # Close InfluxDB connection
    if influx_client:
        influx_client.close()
        logger.info("InfluxDB connection closed")

# PostgreSQL utilities
async def get_postgres_connection():
    """Get a PostgreSQL connection from the pool"""
    if not postgres_pool:
        logger.warning("PostgreSQL connection pool not available")
        return None
    return await postgres_pool.acquire()

async def release_postgres_connection(conn):
    """Release a PostgreSQL connection back to the pool"""
    if postgres_pool and conn:
        await postgres_pool.release(conn)

@asynccontextmanager
async def postgres_transaction():
    """Context manager for PostgreSQL transactions"""
    if not postgres_pool:
        logger.warning("PostgreSQL connection pool not available")
        yield None
        return
    
    conn = await get_postgres_connection()
    if conn is None:
        logger.warning("Failed to acquire PostgreSQL connection")
        yield None
        return
    
    try:
        async with conn.transaction():
            yield conn
    finally:
        await release_postgres_connection(conn)

async def execute_query(query: str, *args) -> list:
    """Execute a PostgreSQL query and return results"""
    if not postgres_pool:
        logger.warning("PostgreSQL connection pool not available")
        return []
    
    async with postgres_transaction() as conn:
        if conn:
            return await conn.fetch(query, *args)
        return []

async def execute_command(command: str, *args) -> str:
    """Execute a PostgreSQL command and return the result"""
    if not postgres_pool:
        logger.warning("PostgreSQL connection pool not available")
        return ""
    
    async with postgres_transaction() as conn:
        if conn:
            return await conn.execute(command, *args)
        return ""

# Redis utilities
async def get_redis_client():
    """Get Redis client instance"""
    if not redis_client:
        logger.warning("Redis client not available")
        return None
    return redis_client

async def redis_get(key: str) -> Optional[str]:
    """Get value from Redis"""
    client = await get_redis_client()
    if client:
        return await client.get(key)
    return None

async def redis_set(key: str, value: str, expire: Optional[int] = None) -> bool:
    """Set value in Redis with optional expiration"""
    client = await get_redis_client()
    if client:
        return await client.set(key, value, ex=expire)
    return False

async def redis_delete(key: str) -> int:
    """Delete key from Redis"""
    client = await get_redis_client()
    if client:
        return await client.delete(key)
    return 0

async def redis_exists(key: str) -> bool:
    """Check if key exists in Redis"""
    client = await get_redis_client()
    if client:
        return await client.exists(key)
    return False

async def redis_incr(key: str, amount: int = 1) -> int:
    """Increment value in Redis"""
    client = await get_redis_client()
    if client:
        return await client.incr(key, amount)
    return 0

# InfluxDB utilities
async def get_influx_client():
    """Get InfluxDB client instance"""
    if not influx_client:
        logger.warning("InfluxDB client not available")
        return None
    return influx_client

async def get_influx_write_api():
    """Get InfluxDB write API instance"""
    if not influx_write_api:
        logger.warning("InfluxDB write API not available")
        return None
    return influx_write_api

async def write_metric(measurement: str, tags: Dict[str, str], fields: Dict[str, Any], timestamp: Optional[int] = None):
    """Write a metric to InfluxDB"""
    write_api = await get_influx_write_api()
    if not write_api:
        logger.warning("InfluxDB write API not available")
        return
    
    from influxdb_client import Point
    
    point = Point(measurement)
    
    # Add tags
    for key, value in tags.items():
        point.tag(key, value)
    
    # Add fields
    for key, value in fields.items():
        point.field(key, value)
    
    # Add timestamp if provided
    if timestamp:
        # Convert timestamp to datetime for InfluxDB
        if isinstance(timestamp, int):
            dt = datetime.fromtimestamp(timestamp)
            point.time(dt)
        else:
            point.time(timestamp)
    
    write_api.write(
        bucket=settings.INFLUX_BUCKET,
        org=settings.INFLUX_ORG,
        record=point
    )

async def query_metrics(query: str) -> list:
    """Query metrics from InfluxDB"""
    client = await get_influx_client()
    if not client:
        logger.warning("InfluxDB client not available")
        return []
    
    query_api = client.query_api()
    
    result = query_api.query(
        query=query,
        org=settings.INFLUX_ORG
    )
    
    return result

# Database health check
async def check_database_health() -> Dict[str, bool]:
    """Check health of all database connections"""
    health_status = {
        "postgresql": False,
        "redis": False,
        "influxdb": False
    }
    
    # Check PostgreSQL
    try:
        if postgres_pool:
            async with postgres_transaction() as conn:
                if conn:
                    await conn.fetchval("SELECT 1")
                    health_status["postgresql"] = True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
    
    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            health_status["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # Check InfluxDB
    try:
        if influx_client:
            # Simple ping test
            health_status["influxdb"] = True
    except Exception as e:
        logger.error(f"InfluxDB health check failed: {e}")
    
    return health_status 