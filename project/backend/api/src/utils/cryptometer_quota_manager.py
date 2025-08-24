#!/usr/bin/env python3
"""
🔐 CRYPTOMETER QUOTA MANAGER - STRICT API PROTECTION SYSTEM
Protects 100,000 API calls/month with intelligent quotas and emergency shutoffs
"""

import json
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class DailyQuota:
    """Daily quota tracking"""
    date: str
    calls_made: int = 0
    calls_limit: int = 8500  # Increased based on 79k remaining calls / 9 days
    emergency_limit: int = 10000  # Hard emergency limit
    services_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.services_usage is None:
            self.services_usage = {}

@dataclass 
class MonthlyQuota:
    """Monthly quota tracking"""
    month: str  # YYYY-MM format
    calls_made: int = 0
    calls_limit: int = 100000  # 100k monthly limit
    daily_quotas: Dict[str, DailyQuota] = None
    
    def __post_init__(self):
        if self.daily_quotas is None:
            self.daily_quotas = {}

class CryptometerQuotaManager:
    """
    🛡️ CRITICAL PROTECTION SYSTEM for Cryptometer API
    
    Features:
    - Daily quota: 8,500 calls/day (based on current usage pattern)
    - Monthly quota: 100,000 calls/month
    - Emergency shutoff at 10,000 daily calls
    - Service-specific tracking
    - Priority-based allocation
    - Real-time monitoring
    """
    
    def __init__(self, quota_file: str = "config/cryptometer_quota.json"):
        self.quota_file = Path(quota_file)
        self.quota_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        
        # Load or create quota data
        self.monthly_quota = self._load_quota_data()
        
        # Service priorities (higher = more important)
        self.service_priorities = {
            'core_trading_signal': 10,        # Most critical
            'enhanced_alerts': 9,             # High priority  
            'real_time_technical': 8,         # Important
            'portfolio_analysis': 7,          # Medium-high
            'historical_analysis': 6,         # Medium
            'ai_predictions': 5,              # Medium-low
            'trend_analysis': 4,              # Lower
            'general_analysis': 3,            # Low
            'background_collection': 2,       # Very low
            'testing': 1                      # Lowest
        }
        
        # Emergency shutdown flag
        self._emergency_shutdown = False
        
        # Rate limiting toggle - default enabled
        self._rate_limiting_enabled = True
        
        logger.info(f"🔐 Cryptometer Quota Manager initialized")
        logger.info(f"📊 Monthly: {self.monthly_quota.calls_made}/{self.monthly_quota.calls_limit}")
        logger.info(f"📅 Today: {self.get_today_usage()}/{self.get_daily_limit()}")
    
    def _load_quota_data(self) -> MonthlyQuota:
        """Load quota data from file"""
        current_month = datetime.now().strftime('%Y-%m')
        
        if self.quota_file.exists():
            try:
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                
                # If it's a new month, reset quota
                if data.get('month') != current_month:
                    logger.info(f"🔄 New month detected, resetting quota")
                    return MonthlyQuota(month=current_month)
                
                # Load existing data
                monthly_quota = MonthlyQuota(
                    month=data['month'],
                    calls_made=data.get('calls_made', 0),
                    calls_limit=data.get('calls_limit', 100000)
                )
                
                # Load daily quotas
                daily_data = data.get('daily_quotas', {})
                for date_str, daily_info in daily_data.items():
                    monthly_quota.daily_quotas[date_str] = DailyQuota(
                        date=date_str,
                        calls_made=daily_info.get('calls_made', 0),
                        calls_limit=daily_info.get('calls_limit', 3200),
                        emergency_limit=daily_info.get('emergency_limit', 4000),
                        services_usage=daily_info.get('services_usage', {})
                    )
                
                return monthly_quota
                
            except Exception as e:
                logger.error(f"❌ Error loading quota data: {e}")
                return MonthlyQuota(month=current_month)
        
        # Create new quota
        return MonthlyQuota(month=current_month)
    
    def _save_quota_data(self):
        """Save quota data to file"""
        try:
            # Convert to dict format
            data = {
                'month': self.monthly_quota.month,
                'calls_made': self.monthly_quota.calls_made,
                'calls_limit': self.monthly_quota.calls_limit,
                'daily_quotas': {}
            }
            
            for date_str, daily_quota in self.monthly_quota.daily_quotas.items():
                data['daily_quotas'][date_str] = asdict(daily_quota)
            
            with open(self.quota_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving quota data: {e}")
    
    def can_make_request(self, service: str = 'general', priority: int = None) -> bool:
        """
        Check if a request can be made based on quotas
        
        Args:
            service: Service name making the request
            priority: Override priority (1-10, higher = more important)
        
        Returns:
            bool: True if request is allowed
        """
        with self.lock:
            # If rate limiting is disabled, allow all requests
            if not self._rate_limiting_enabled:
                logger.debug(f"🔓 Rate limiting disabled - allowing request: {service}")
                return True
            
            # Emergency shutdown check
            if self._emergency_shutdown:
                logger.warning(f"🚨 EMERGENCY SHUTDOWN - All Cryptometer requests blocked")
                return False
            
            today = date.today().strftime('%Y-%m-%d')
            today_quota = self._get_or_create_daily_quota(today)
            
            # Check monthly limit (hard stop at 95k to be safe)
            if self.monthly_quota.calls_made >= 95000:
                logger.error(f"🚨 MONTHLY LIMIT REACHED: {self.monthly_quota.calls_made}/100k")
                self._emergency_shutdown = True
                return False
            
            # Check daily emergency limit (hard stop)
            if today_quota.calls_made >= today_quota.emergency_limit:
                logger.error(f"🚨 DAILY EMERGENCY LIMIT REACHED: {today_quota.calls_made}/{today_quota.emergency_limit}")
                return False
            
            # Check daily regular limit
            if today_quota.calls_made >= today_quota.calls_limit:
                # Allow only high priority requests (priority 8+)
                request_priority = priority or self.service_priorities.get(service, 3)
                if request_priority < 8:
                    logger.warning(f"⚠️ Daily limit reached, blocking low priority request: {service} (priority {request_priority})")
                    return False
                else:
                    logger.info(f"🔥 Allowing high priority request despite daily limit: {service} (priority {request_priority})")
            
            return True
    
    def record_request(self, service: str = 'general', success: bool = True):
        """
        Record a successful API request
        
        Args:
            service: Service that made the request
            success: Whether the request was successful
        """
        with self.lock:
            if not success:
                return  # Don't count failed requests
                
            today = date.today().strftime('%Y-%m-%d')
            today_quota = self._get_or_create_daily_quota(today)
            
            # Increment counters
            today_quota.calls_made += 1
            self.monthly_quota.calls_made += 1
            
            # Track service usage
            if service not in today_quota.services_usage:
                today_quota.services_usage[service] = 0
            today_quota.services_usage[service] += 1
            
            # Save data
            self._save_quota_data()
            
            # Log warnings if approaching limits
            daily_percent = (today_quota.calls_made / today_quota.calls_limit) * 100
            monthly_percent = (self.monthly_quota.calls_made / self.monthly_quota.calls_limit) * 100
            
            if daily_percent >= 90:
                logger.warning(f"🟡 Daily quota 90% reached: {today_quota.calls_made}/{today_quota.calls_limit}")
            elif daily_percent >= 80:
                logger.info(f"📊 Daily quota 80% reached: {today_quota.calls_made}/{today_quota.calls_limit}")
            
            if monthly_percent >= 90:
                logger.warning(f"🔴 Monthly quota 90% reached: {self.monthly_quota.calls_made}/{self.monthly_quota.calls_limit}")
            elif monthly_percent >= 80:
                logger.warning(f"🟡 Monthly quota 80% reached: {self.monthly_quota.calls_made}/{self.monthly_quota.calls_limit}")
            
            logger.debug(f"✅ Recorded API call: {service} | Daily: {today_quota.calls_made} | Monthly: {self.monthly_quota.calls_made}")
    
    def _get_or_create_daily_quota(self, date_str: str) -> DailyQuota:
        """Get or create daily quota for given date"""
        if date_str not in self.monthly_quota.daily_quotas:
            self.monthly_quota.daily_quotas[date_str] = DailyQuota(date=date_str)
        return self.monthly_quota.daily_quotas[date_str]
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status"""
        today = date.today().strftime('%Y-%m-%d')
        today_quota = self._get_or_create_daily_quota(today)
        
        return {
            'emergency_shutdown': self._emergency_shutdown,
            'rate_limiting_enabled': self._rate_limiting_enabled,
            'monthly': {
                'used': self.monthly_quota.calls_made,
                'limit': self.monthly_quota.calls_limit,
                'remaining': self.monthly_quota.calls_limit - self.monthly_quota.calls_made,
                'percent_used': (self.monthly_quota.calls_made / self.monthly_quota.calls_limit) * 100
            },
            'daily': {
                'date': today,
                'used': today_quota.calls_made,
                'limit': today_quota.calls_limit,
                'emergency_limit': today_quota.emergency_limit,
                'remaining': today_quota.calls_limit - today_quota.calls_made,
                'percent_used': (today_quota.calls_made / today_quota.calls_limit) * 100
            },
            'services': today_quota.services_usage,
            'can_make_request': self.can_make_request()
        }
    
    def get_today_usage(self) -> int:
        """Get today's API call usage"""
        today = date.today().strftime('%Y-%m-%d')
        today_quota = self._get_or_create_daily_quota(today)
        return today_quota.calls_made
    
    def get_daily_limit(self) -> int:
        """Get daily limit"""
        today = date.today().strftime('%Y-%m-%d')
        today_quota = self._get_or_create_daily_quota(today)
        return today_quota.calls_limit
    
    def get_monthly_usage(self) -> int:
        """Get monthly API call usage"""
        return self.monthly_quota.calls_made
    
    def reset_emergency_shutdown(self):
        """Reset emergency shutdown (admin function)"""
        with self.lock:
            self._emergency_shutdown = False
            logger.info("🔓 Emergency shutdown reset by admin")
    
    def set_daily_limit(self, new_limit: int):
        """Set daily limit (admin function)"""
        with self.lock:
            today = date.today().strftime('%Y-%m-%d')
            today_quota = self._get_or_create_daily_quota(today)
            today_quota.calls_limit = new_limit
            self._save_quota_data()
            logger.info(f"📝 Daily limit set to {new_limit}")
    
    def enable_rate_limiting(self):
        """Enable rate limiting (admin function)"""
        with self.lock:
            self._rate_limiting_enabled = True
            logger.info("🔒 Rate limiting enabled")
    
    def disable_rate_limiting(self):
        """Disable rate limiting (admin function)"""
        with self.lock:
            self._rate_limiting_enabled = False
            logger.info("🔓 Rate limiting disabled - unlimited API calls allowed")
    
    def toggle_rate_limiting(self) -> bool:
        """Toggle rate limiting on/off (admin function)"""
        with self.lock:
            self._rate_limiting_enabled = not self._rate_limiting_enabled
            status = "enabled" if self._rate_limiting_enabled else "disabled"
            emoji = "🔒" if self._rate_limiting_enabled else "🔓"
            logger.info(f"{emoji} Rate limiting {status}")
            return self._rate_limiting_enabled
    
    def is_rate_limiting_enabled(self) -> bool:
        """Check if rate limiting is enabled"""
        return self._rate_limiting_enabled
    
    def get_service_usage_report(self) -> Dict[str, Any]:
        """Get detailed service usage report"""
        today = date.today().strftime('%Y-%m-%d')
        today_quota = self._get_or_create_daily_quota(today)
        
        # Calculate service percentages
        total_calls = today_quota.calls_made
        service_percentages = {}
        
        if total_calls > 0:
            for service, calls in today_quota.services_usage.items():
                service_percentages[service] = {
                    'calls': calls,
                    'percentage': (calls / total_calls) * 100,
                    'priority': self.service_priorities.get(service, 3)
                }
        
        return {
            'date': today,
            'total_calls': total_calls,
            'services': service_percentages,
            'top_consumers': sorted(
                service_percentages.items(), 
                key=lambda x: x[1]['calls'], 
                reverse=True
            )[:5]
        }

# Global instance
cryptometer_quota_manager = CryptometerQuotaManager()

# Helper functions
def can_make_cryptometer_request(service: str = 'general', priority: int = None) -> bool:
    """Check if Cryptometer request can be made"""
    return cryptometer_quota_manager.can_make_request(service, priority)

def record_cryptometer_request(service: str = 'general', success: bool = True):
    """Record Cryptometer API request"""
    return cryptometer_quota_manager.record_request(service, success)

def get_cryptometer_quota_status() -> Dict[str, Any]:
    """Get current Cryptometer quota status"""
    return cryptometer_quota_manager.get_quota_status()

def get_cryptometer_usage_report() -> Dict[str, Any]:
    """Get Cryptometer usage report"""
    return cryptometer_quota_manager.get_service_usage_report()