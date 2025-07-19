"""
Zmart Trading Bot Platform - Database Utilities
Handles connections to PostgreSQL, Redis, and InfluxDB
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import asyncpg
import redis.asyncio as redis
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Global connection pools
postgres_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None
influx_client: Optional[InfluxDBClient] = None
influx_write_api: Optional[Any] = None

async def init_database():
    """Initialize all database connections"""
    global postgres_pool, redis_client, influx_client, influx_write_api
    
    try:
        # Initialize PostgreSQL connection pool
        postgres_pool = await asyncpg.create_pool(
            settings.get_database_url(),
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("PostgreSQL connection pool initialized")
        
        # Initialize Redis connection
        redis_client = redis.from_url(
            settings.get_redis_url(),
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connection initialized")
        
        # Initialize InfluxDB connection
        influx_config = settings.get_influx_config()
        influx_client = InfluxDBClient(
            url=f"http://{influx_config['host']}:{influx_config['port']}",
            username=influx_config['username'],
            password=influx_config['password'],
            org=settings.database.influx_org,
            token=settings.database.influx_token
        )
        influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        logger.info("InfluxDB connection initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        raise

async def close_database():
    """Close all database connections"""
    global postgres_pool, redis_client, influx_client, influx_write_api
    
    try:
        if postgres_pool:
            await postgres_pool.close()
            logger.info("PostgreSQL connection pool closed")
        
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
        
        if influx_client:
            influx_client.close()
            logger.info("InfluxDB connection closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

async def get_postgres_pool() -> asyncpg.Pool:
    """Get PostgreSQL connection pool"""
    if not postgres_pool:
        raise RuntimeError("PostgreSQL connection pool not initialized")
    return postgres_pool

async def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client

async def get_influx_client() -> InfluxDBClient:
    """Get InfluxDB client"""
    if not influx_client:
        raise RuntimeError("InfluxDB client not initialized")
    return influx_client

async def get_influx_write_api():
    """Get InfluxDB write API"""
    if not influx_write_api:
        raise RuntimeError("InfluxDB write API not initialized")
    return influx_write_api

# Database health check functions
async def check_postgres_health() -> Dict[str, Any]:
    """Check PostgreSQL health"""
    try:
        pool = await get_postgres_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            return {
                "status": "healthy",
                "database": "postgresql",
                "response_time": "ok"
            }
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(e)
        }

async def check_redis_health() -> Dict[str, Any]:
    """Check Redis health"""
    try:
        client = await get_redis_client()
        await client.ping()
        return {
            "status": "healthy",
            "database": "redis",
            "response_time": "ok"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "redis",
            "error": str(e)
        }

async def check_influx_health() -> Dict[str, Any]:
    """Check InfluxDB health"""
    try:
        client = await get_influx_client()
        health = client.health()
        return {
            "status": "healthy" if health.status == "pass" else "unhealthy",
            "database": "influxdb",
            "response_time": "ok"
        }
    except Exception as e:
        logger.error(f"InfluxDB health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "influxdb",
            "error": str(e)
        }

# Database utility functions
async def execute_query(query: str, *args) -> Any:
    """Execute a PostgreSQL query"""
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute_transaction(queries: list) -> bool:
    """Execute multiple queries in a transaction"""
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for query, args in queries:
                await conn.execute(query, *args)
    return True

async def cache_set(key: str, value: str, expire: int = 3600) -> bool:
    """Set a value in Redis cache"""
    try:
        client = await get_redis_client()
        await client.set(key, value, ex=expire)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache key {key}: {e}")
        return False

async def cache_get(key: str) -> Optional[str]:
    """Get a value from Redis cache"""
    try:
        client = await get_redis_client()
        return await client.get(key)
    except Exception as e:
        logger.error(f"Failed to get cache key {key}: {e}")
        return None

async def write_metric(measurement: str, tags: Dict[str, str], fields: Dict[str, Any]) -> bool:
    """Write a metric to InfluxDB"""
    try:
        write_api = await get_influx_write_api()
        point = {
            "measurement": measurement,
            "tags": tags,
            "fields": fields,
            "time": "now"
        }
        write_api.write(bucket=settings.database.influx_bucket, record=point)
        return True
    except Exception as e:
        logger.error(f"Failed to write metric {measurement}: {e}")
        return False 