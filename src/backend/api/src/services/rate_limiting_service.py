#!/usr/bin/env python3
"""
Rate Limiting Service for ZmartBot
Centralized rate limiting management for all external APIs
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from src.utils.enhanced_rate_limiter import (
    global_rate_limiter, 
    rate_limited_request, 
    get_rate_limit_status,
    configure_api_limits,
    RateLimitConfig
)

logger = logging.getLogger(__name__)

class RateLimitingService:
    """
    Centralized rate limiting service for all external APIs
    
    Manages rate limits for:
    - Cryptometer API (free tier: 30 req/min)
    - CoinGecko API (free tier: 10 req/min)
    - Binance API (1200 req/min)
    - KuCoin API (100 req/10s)
    - Alternative.me API (30 req/min)
    - Blockchain.info API (60 req/min)
    """
    
    def __init__(self):
        """Initialize the rate limiting service"""
        self.service_id = "rate_limiting_service"
        self.status = "stopped"
        
        # Initialize API configurations with conservative free tier limits
        self._init_api_configurations()
        
        # Statistics tracking
        self.start_time = datetime.now()
        
        logger.info("Rate Limiting Service initialized")
    
    def _init_api_configurations(self):
        """Initialize rate limit configurations for all known APIs"""
        
        # Cryptometer API - Free tier (very conservative)
        configure_api_limits(
            'cryptometer', 
            max_requests=30,     # 30 requests per minute
            time_window=60,      # 1 minute window
            burst_limit=5,       # max 5 burst requests
            backoff_factor=2.0,  # exponential backoff
            max_backoff=300.0    # max 5 minute backoff
        )
        
        # CoinGecko API - Free tier
        configure_api_limits(
            'coingecko',
            max_requests=10,     # 10 requests per minute
            time_window=60,
            burst_limit=3,
            backoff_factor=2.0,
            max_backoff=600.0    # max 10 minute backoff
        )
        
        # Binance API - More generous limits
        configure_api_limits(
            'binance',
            max_requests=1200,   # 1200 requests per minute
            time_window=60,
            burst_limit=20,
            backoff_factor=1.5,
            max_backoff=60.0     # max 1 minute backoff
        )
        
        # KuCoin API - 100 requests per 10 seconds
        configure_api_limits(
            'kucoin',
            max_requests=100,
            time_window=10,      # 10 second window
            burst_limit=10,
            backoff_factor=2.0,
            max_backoff=120.0    # max 2 minute backoff
        )
        
        # Alternative.me API (Fear & Greed Index)
        configure_api_limits(
            'alternative_me',
            max_requests=30,
            time_window=60,
            burst_limit=5,
            backoff_factor=2.0,
            max_backoff=300.0
        )
        
        # Blockchain.info API
        configure_api_limits(
            'blockchain_info',
            max_requests=60,
            time_window=60,
            burst_limit=10,
            backoff_factor=2.0,
            max_backoff=300.0
        )
        
        # X (Twitter) API - Very conservative
        configure_api_limits(
            'x_api',
            max_requests=300,    # 300 requests per 15 minutes
            time_window=900,     # 15 minute window
            burst_limit=5,
            backoff_factor=3.0,
            max_backoff=1800.0   # max 30 minute backoff
        )
        
        # Default configuration for unknown APIs
        configure_api_limits(
            'default',
            max_requests=30,
            time_window=60,
            burst_limit=5,
            backoff_factor=2.0,
            max_backoff=300.0
        )
        
        logger.info("Rate limit configurations initialized for all APIs")
    
    async def start(self):
        """Start the rate limiting service"""
        self.status = "running"
        logger.info("Rate Limiting Service started")
    
    async def stop(self):
        """Stop the rate limiting service"""
        self.status = "stopped"
        logger.info("Rate Limiting Service stopped")
    
    async def execute_request(self, api_name: str, request_func, *args, **kwargs):
        """
        Execute a request with rate limiting
        
        Args:
            api_name: Name of the API (e.g., 'cryptometer', 'binance')
            request_func: Function to execute
            *args, **kwargs: Arguments for the request function
        
        Returns:
            (result, success) tuple
        """
        return await rate_limited_request(api_name, request_func, *args, **kwargs)
    
    def get_api_status(self, api_name: str) -> Dict[str, Any]:
        """Get current status for a specific API"""
        return get_rate_limit_status(api_name)
    
    def get_all_api_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all configured APIs"""
        api_names = [
            'cryptometer', 'coingecko', 'binance', 'kucoin', 
            'alternative_me', 'blockchain_info', 'x_api', 'default'
        ]
        
        statuses = {}
        for api_name in api_names:
            statuses[api_name] = self.get_api_status(api_name)
        
        return statuses
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        all_stats = global_rate_limiter.get_statistics()
        
        # Calculate totals
        total_requests = sum(stats.get('total_requests', 0) for stats in all_stats.values())
        total_successful = sum(stats.get('successful_requests', 0) for stats in all_stats.values())
        total_rate_limited = sum(stats.get('rate_limited_requests', 0) for stats in all_stats.values())
        total_failed = sum(stats.get('failed_requests', 0) for stats in all_stats.values())
        
        # Calculate success rate
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        # Get currently rate-limited APIs
        rate_limited_apis = []
        backoff_apis = []
        
        for api_name in ['cryptometer', 'coingecko', 'binance', 'kucoin', 'alternative_me', 'blockchain_info', 'x_api']:
            status = self.get_api_status(api_name)
            if status.get('is_rate_limited', False):
                rate_limited_apis.append(api_name)
            if status.get('is_in_backoff', False):
                backoff_apis.append({
                    'api': api_name,
                    'backoff_remaining': status.get('backoff_remaining', 0)
                })
        
        return {
            'service_id': self.service_id,
            'status': self.status,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'total_requests': total_requests,
            'successful_requests': total_successful,
            'rate_limited_requests': total_rate_limited,
            'failed_requests': total_failed,
            'success_rate_percent': round(success_rate, 2),
            'currently_rate_limited_apis': rate_limited_apis,
            'apis_in_backoff': backoff_apis,
            'api_statistics': all_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_api_limits(self, api_name: str, max_requests: int, time_window: int, **kwargs):
        """Update rate limits for a specific API"""
        configure_api_limits(api_name, max_requests, time_window, **kwargs)
        logger.info(f"Updated rate limits for {api_name}: {max_requests} req/{time_window}s")
    
    def is_api_healthy(self, api_name: str) -> bool:
        """Check if an API is healthy (not rate limited or in backoff)"""
        status = self.get_api_status(api_name)
        return not (status.get('is_rate_limited', False) or status.get('is_in_backoff', False))
    
    def get_healthy_apis(self) -> List[str]:
        """Get list of APIs that are currently healthy"""
        api_names = ['cryptometer', 'coingecko', 'binance', 'kucoin', 'alternative_me', 'blockchain_info', 'x_api']
        return [api for api in api_names if self.is_api_healthy(api)]
    
    def get_rate_limited_apis(self) -> List[str]:
        """Get list of APIs that are currently rate limited"""
        api_names = ['cryptometer', 'coingecko', 'binance', 'kucoin', 'alternative_me', 'blockchain_info', 'x_api']
        return [api for api in api_names if not self.is_api_healthy(api)]
    
    async def wait_for_api_recovery(self, api_name: str, max_wait_time: float = 300.0) -> bool:
        """
        Wait for an API to recover from rate limiting
        
        Args:
            api_name: Name of the API
            max_wait_time: Maximum time to wait in seconds
        
        Returns:
            True if API recovered, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            if self.is_api_healthy(api_name):
                logger.info(f"API {api_name} recovered from rate limiting")
                return True
            
            # Wait 5 seconds before checking again
            await asyncio.sleep(5)
        
        logger.warning(f"API {api_name} did not recover within {max_wait_time} seconds")
        return False
    
    def generate_rate_limit_report(self) -> str:
        """Generate a comprehensive rate limiting report"""
        stats = self.get_service_statistics()
        
        report = []
        report.append("🛡️  RATE LIMITING SERVICE REPORT")
        report.append("=" * 50)
        report.append(f"Service Status: {stats['status']}")
        report.append(f"Uptime: {stats['uptime_seconds']:.0f} seconds")
        report.append(f"Total Requests: {stats['total_requests']}")
        report.append(f"Success Rate: {stats['success_rate_percent']}%")
        report.append("")
        
        # API Status Summary
        report.append("📊 API STATUS SUMMARY:")
        healthy_apis = self.get_healthy_apis()
        rate_limited_apis = self.get_rate_limited_apis()
        
        report.append(f"✅ Healthy APIs ({len(healthy_apis)}): {', '.join(healthy_apis)}")
        report.append(f"⚠️  Rate Limited APIs ({len(rate_limited_apis)}): {', '.join(rate_limited_apis)}")
        report.append("")
        
        # Detailed API Statistics
        report.append("📈 DETAILED API STATISTICS:")
        for api_name, api_stats in stats['api_statistics'].items():
            if api_stats.get('total_requests', 0) > 0:
                success_rate = (api_stats.get('successful_requests', 0) / api_stats['total_requests'] * 100)
                report.append(f"  {api_name}:")
                report.append(f"    Total: {api_stats['total_requests']}")
                report.append(f"    Success: {api_stats.get('successful_requests', 0)} ({success_rate:.1f}%)")
                report.append(f"    Rate Limited: {api_stats.get('rate_limited_requests', 0)}")
                report.append(f"    Failed: {api_stats.get('failed_requests', 0)}")
        
        # Current Backoffs
        if stats['apis_in_backoff']:
            report.append("")
            report.append("⏳ APIS IN BACKOFF:")
            for backoff_info in stats['apis_in_backoff']:
                report.append(f"  {backoff_info['api']}: {backoff_info['backoff_remaining']:.1f}s remaining")
        
        return "\n".join(report)

# Global rate limiting service instance
rate_limiting_service = RateLimitingService()