#!/usr/bin/env python3
"""
Cryptometer Service with Integrated Rate Limiting
Enhanced protection against API rate limits
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import requests

from src.utils.rate_limiter import rate_limit, global_rate_limiter
from src.services.telegram_notifications import get_telegram_service, AlertLevel

logger = logging.getLogger(__name__)

class RateLimitedCryptometerService:
    """
    Cryptometer service with integrated rate limiting and monitoring
    """
    
    def __init__(self, api_key: str = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"):
        self.api_key = api_key
        self.base_url = "https://api.cryptometer.io"
        self.telegram = get_telegram_service()
        
        # Track rate limit status
        self.rate_limit_status = {
            'requests_made': 0,
            'requests_blocked': 0,
            'last_reset': datetime.now()
        }
    
    @rate_limit(max_calls=100, time_window=60, service='cryptometer')
    async def fetch_endpoint(self, endpoint: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
        Fetch data from Cryptometer endpoint with rate limiting
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            
        Returns:
            Tuple of (data, success)
        """
        try:
            # Check rate limit before making request
            if not await global_rate_limiter.check_limit('cryptometer', endpoint):
                # Wait if rate limited
                await global_rate_limiter.wait_if_needed('cryptometer', endpoint)
            
            # Add API key to params
            params['api_key'] = self.api_key
            
            # Make request
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=30)
            
            self.rate_limit_status['requests_made'] += 1
            
            if response.status_code == 200:
                return response.json(), True
            elif response.status_code == 429:
                # Rate limited - notify via Telegram
                self.rate_limit_status['requests_blocked'] += 1
                await self._notify_rate_limit(endpoint)
                logger.warning(f"Rate limited on {endpoint}")
                return {}, False
            else:
                logger.error(f"API error for {endpoint}: {response.status_code}")
                return {}, False
                
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return {}, False
    
    async def _notify_rate_limit(self, endpoint: str):
        """Send Telegram notification about rate limiting"""
        try:
            message = f"""
<b>Rate Limit Alert</b>

⚠️ <b>Service:</b> Cryptometer
📍 <b>Endpoint:</b> {endpoint}
📊 <b>Requests Made:</b> {self.rate_limit_status['requests_made']}
🚫 <b>Requests Blocked:</b> {self.rate_limit_status['requests_blocked']}

The system will automatically retry after the rate limit window resets.
"""
            await self.telegram.send_message(message, AlertLevel.WARNING)
        except Exception as e:
            logger.error(f"Failed to send rate limit notification: {e}")
    
    async def fetch_multiple_endpoints(self, endpoints: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fetch data from multiple endpoints with rate limiting
        
        Args:
            endpoints: Dictionary of endpoint configurations
            
        Returns:
            Combined results from all endpoints
        """
        results = {}
        
        for endpoint_name, config in endpoints.items():
            try:
                # Apply rate limiting between requests
                data, success = await self.fetch_endpoint(
                    config['url'],
                    config.get('params', {})
                )
                
                results[endpoint_name] = {
                    'success': success,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Small delay between requests to be respectful
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching {endpoint_name}: {e}")
                results[endpoint_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        stats = global_rate_limiter.tiers['cryptometer'].get_stats()
        
        return {
            'service': 'Cryptometer',
            'requests_made': self.rate_limit_status['requests_made'],
            'requests_blocked': self.rate_limit_status['requests_blocked'],
            'rate_limiter_stats': stats,
            'last_reset': self.rate_limit_status['last_reset'].isoformat()
        }
    
    async def reset_rate_limit_tracking(self):
        """Reset rate limit tracking"""
        self.rate_limit_status = {
            'requests_made': 0,
            'requests_blocked': 0,
            'last_reset': datetime.now()
        }
        global_rate_limiter.tiers['cryptometer'].reset_stats()
        
        logger.info("Rate limit tracking reset for Cryptometer")

# Example usage with specific endpoints
async def fetch_with_rate_limiting(symbol: str) -> Dict[str, Any]:
    """
    Example function to fetch data with rate limiting
    """
    service = RateLimitedCryptometerService()
    
    endpoints = {
        'ai_screener': {
            'url': 'ai-screener/',
            'params': {}
        },
        'ls_ratio': {
            'url': 'ls-ratio/',
            'params': {'e': 'binance_futures', 'pair': f'{symbol}-usdt', 'timeframe': '4h'}
        },
        'liquidation_data': {
            'url': 'liquidation-data-v2/',
            'params': {'symbol': symbol}
        },
        'trend_indicator': {
            'url': 'trend-indicator-v3/',
            'params': {}
        }
    }
    
    results = await service.fetch_multiple_endpoints(endpoints)
    
    # Get rate limit status
    status = await service.get_rate_limit_status()
    
    return {
        'symbol': symbol,
        'data': results,
        'rate_limit_status': status,
        'timestamp': datetime.now().isoformat()
    }