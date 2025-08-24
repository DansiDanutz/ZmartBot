#!/usr/bin/env python3
"""
API Response Tracker Service
Tracks API request/response flow for real data flow monitoring
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class APIRequestRecord:
    """Record of an API request/response"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    payload_size: int = 0
    error_message: Optional[str] = None

class APIResponseTracker:
    """
    Tracks API requests and responses for monitoring real data flow
    """
    
    def __init__(self):
        """Initialize the API response tracker"""
        self.service_id = "api_response_tracker"
        self.status = "stopped"
        
        # Request tracking
        self.request_history: List[APIRequestRecord] = []
        self.request_stats: Dict[str, Any] = defaultdict(int)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Configuration
        self.max_history_size = 10000
        self.cleanup_interval_hours = 24
        
        logger.info("API Response Tracker initialized")
    
    async def start(self):
        """Start the tracker service"""
        self.status = "running"
        logger.info("API Response Tracker started")
    
    async def stop(self):
        """Stop the tracker service"""
        self.status = "stopped"
        logger.info("API Response Tracker stopped")
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      response_time_ms: float, payload_size: int = 0, 
                      error_message: Optional[str] = None):
        """Record an API request/response"""
        with self.lock:
            # Create request record
            record = APIRequestRecord(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
                payload_size=payload_size,
                error_message=error_message
            )
            
            # Add to history
            self.request_history.append(record)
            
            # Update statistics
            self.request_stats['total_requests'] += 1
            self.request_stats[f'{method}_{endpoint}'] += 1
            self.request_stats[f'status_{status_code}'] += 1
            
            if status_code >= 200 and status_code < 300:
                self.request_stats['successful_requests'] += 1
            else:
                self.request_stats['failed_requests'] += 1
            
            # Update response time stats
            if 'total_response_time' not in self.request_stats:
                self.request_stats['total_response_time'] = 0
            self.request_stats['total_response_time'] += response_time_ms
            
            # Cleanup old records if needed
            if len(self.request_history) > self.max_history_size:
                self.request_history = self.request_history[-self.max_history_size//2:]
            
            logger.debug(f"Recorded API request: {method} {endpoint} -> {status_code} ({response_time_ms}ms)")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive API statistics"""
        with self.lock:
            total_requests = self.request_stats.get('total_requests', 0)
            successful_requests = self.request_stats.get('successful_requests', 0)
            failed_requests = self.request_stats.get('failed_requests', 0)
            total_response_time = self.request_stats.get('total_response_time', 0)
            
            # Calculate derived metrics
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            avg_response_time = (total_response_time / total_requests) if total_requests > 0 else 0
            
            # Get recent activity (last hour)
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_requests = [r for r in self.request_history if r.timestamp >= recent_cutoff]
            
            # Get endpoint statistics
            endpoint_stats = {}
            for record in self.request_history:
                key = f"{record.method}_{record.endpoint}"
                if key not in endpoint_stats:
                    endpoint_stats[key] = {
                        'count': 0,
                        'success_count': 0,
                        'total_response_time': 0,
                        'avg_response_time': 0,
                        'success_rate': 0
                    }
                
                endpoint_stats[key]['count'] += 1
                endpoint_stats[key]['total_response_time'] += record.response_time_ms
                
                if record.status_code >= 200 and record.status_code < 300:
                    endpoint_stats[key]['success_count'] += 1
            
            # Calculate endpoint averages
            for key, stats in endpoint_stats.items():
                if stats['count'] > 0:
                    stats['avg_response_time'] = stats['total_response_time'] / stats['count']
                    stats['success_rate'] = (stats['success_count'] / stats['count']) * 100
            
            return {
                'service_status': self.status,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate_percent': round(success_rate, 2),
                'average_response_time_ms': round(avg_response_time, 2),
                'recent_requests_last_hour': len(recent_requests),
                'endpoint_statistics': endpoint_stats,
                'request_history_size': len(self.request_history),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent API requests"""
        with self.lock:
            recent = self.request_history[-limit:] if limit > 0 else self.request_history
            
            return [
                {
                    'endpoint': record.endpoint,
                    'method': record.method,
                    'status_code': record.status_code,
                    'response_time_ms': record.response_time_ms,
                    'timestamp': record.timestamp.isoformat(),
                    'payload_size': record.payload_size,
                    'error_message': record.error_message
                }
                for record in recent
            ]
    
    def get_endpoint_performance(self, endpoint: str, method: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for a specific endpoint"""
        with self.lock:
            matching_requests = [
                r for r in self.request_history 
                if r.endpoint == endpoint and (method is None or r.method == method)
            ]
            
            if not matching_requests:
                return {
                    'endpoint': endpoint,
                    'method': method,
                    'total_requests': 0,
                    'performance_data': None
                }
            
            # Calculate performance metrics
            total_requests = len(matching_requests)
            successful_requests = sum(1 for r in matching_requests if 200 <= r.status_code < 300)
            total_response_time = sum(r.response_time_ms for r in matching_requests)
            
            response_times = [r.response_time_ms for r in matching_requests]
            response_times.sort()
            
            return {
                'endpoint': endpoint,
                'method': method,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'success_rate_percent': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'average_response_time_ms': total_response_time / total_requests if total_requests > 0 else 0,
                'min_response_time_ms': min(response_times) if response_times else 0,
                'max_response_time_ms': max(response_times) if response_times else 0,
                'p50_response_time_ms': response_times[len(response_times)//2] if response_times else 0,
                'p95_response_time_ms': response_times[int(len(response_times)*0.95)] if response_times else 0,
                'recent_requests': len([r for r in matching_requests if r.timestamp >= datetime.now() - timedelta(hours=1)])
            }
    
    def cleanup_old_records(self, hours_to_keep: int = 24):
        """Clean up old request records"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
            
            old_count = len(self.request_history)
            self.request_history = [r for r in self.request_history if r.timestamp >= cutoff_time]
            new_count = len(self.request_history)
            
            cleaned_count = old_count - new_count
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old API request records")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'service_id': self.service_id,
            'status': self.status,
            'request_history_size': len(self.request_history),
            'total_requests_tracked': self.request_stats.get('total_requests', 0),
            'max_history_size': self.max_history_size,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
api_response_tracker = APIResponseTracker()

# Decorator for automatic request tracking
def track_api_request(endpoint_name: Optional[str] = None):
    """Decorator to automatically track API requests"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000
                
                # Record successful request
                api_response_tracker.record_request(
                    endpoint=endpoint,
                    method='FUNCTION',
                    status_code=200,
                    response_time_ms=response_time
                )
                
                return result
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                
                # Record failed request
                api_response_tracker.record_request(
                    endpoint=endpoint,
                    method='FUNCTION',
                    status_code=500,
                    response_time_ms=response_time,
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator