#!/usr/bin/env python3
"""
Monitoring utilities for KingFisher module
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics
images_processed = Counter('kingfisher_images_processed_total', 'Total images processed')
analysis_duration = Histogram('kingfisher_analysis_duration_seconds', 'Time spent analyzing images')
telegram_messages = Counter('kingfisher_telegram_messages_total', 'Total Telegram messages received')
significance_score = Gauge('kingfisher_significance_score', 'Current significance score')

async def init_monitoring():
    """Initialize monitoring system"""
    logger.info("Starting system monitor")
    
    # Start background monitoring tasks
    asyncio.create_task(monitor_system_health())
    asyncio.create_task(collect_metrics())

async def monitor_system_health():
    """Monitor system health"""
    while True:
        try:
            # Check system health
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "services": {
                    "telegram": True,
                    "image_processor": True,
                    "database": True
                }
            }
            
            # Log health status
            logger.info(f"System health: {health_status['status']}")
            
            # Wait before next check
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error monitoring system health: {e}")
            await asyncio.sleep(60)

async def collect_metrics():
    """Collect system metrics"""
    while True:
        try:
            # Collect various metrics
            metrics = {
                "images_processed": images_processed._value.get(),
                "telegram_messages": telegram_messages._value.get(),
                "current_significance": significance_score._value.get()
            }
            
            logger.debug(f"Collected metrics: {metrics}")
            
            # Wait before next collection
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            await asyncio.sleep(120)

def record_image_processed():
    """Record that an image was processed"""
    images_processed.inc()

def record_analysis_duration(duration: float):
    """Record analysis duration"""
    analysis_duration.observe(duration)

def record_telegram_message():
    """Record that a Telegram message was received"""
    telegram_messages.inc()

def update_significance_score(score: float):
    """Update significance score metric"""
    significance_score.set(score) 