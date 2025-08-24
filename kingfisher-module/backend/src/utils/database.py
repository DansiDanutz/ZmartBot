#!/usr/bin/env python3
"""
Database utilities for KingFisher module
"""

import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

from src.config.settings import settings, get_database_url, get_redis_url

logger = logging.getLogger(__name__)

# Database setup
engine = None
SessionLocal = None
Base = declarative_base()

# Redis setup
redis_client = None

async def init_database():
    """Initialize database connections"""
    global engine, SessionLocal, redis_client
    
    try:
        # Initialize PostgreSQL
        database_url = get_database_url()
        if database_url.startswith('sqlite'):
            # Use SQLite for development
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            # Use PostgreSQL for production
            engine = create_engine(database_url)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database connection initialized successfully")
        
    except Exception as e:
        logger.warning(f"Failed to initialize PostgreSQL connection pool: {e}")
        logger.info("PostgreSQL connection will be skipped for development")
    
    try:
        # Initialize Redis
        redis_url = get_redis_url()
        redis_client = redis.from_url(redis_url)
        redis_client.ping()  # Test connection
        logger.info("Redis connection initialized successfully")
        
    except Exception as e:
        logger.warning(f"Failed to initialize Redis connection: {e}")
        logger.info("Redis connection will be skipped for development")
        redis_client = None

async def close_database():
    """Close database connections"""
    global engine, redis_client
    
    if engine:
        engine.dispose()
        logger.info("Database connection closed")
    
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")

def get_db():
    """Get database session"""
    if not SessionLocal:
        raise Exception("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client 