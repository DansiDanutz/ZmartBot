#!/usr/bin/env python3
"""
📅 SUBSCRIPTION MONITORING SYSTEM
Monitors Cryptometer API subscription and sends notifications before expiry
"""

import json
import logging
import smtplib
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

class SubscriptionMonitor:
    """
    📊 Monitor Cryptometer API subscription status
    
    Features:
    - Track subscription expiry date
    - Daily usage monitoring with alerts
    - Auto-notification 1 day before expiry
    - Email/console notifications
    - Usage pattern analysis
    """
    
    def __init__(self, config_file: str = "config/subscription_monitor.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load subscription config
        self.config = self._load_config()
        
        logger.info(f"📅 Subscription Monitor initialized")
        self._log_current_status()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load subscription configuration"""
        default_config = {
            "api_plan": "FULLACCESS129",
            "monthly_limit": 100000,
            "current_usage": 20793,
            "reset_date": "2025-08-30",
            "subscription_expiry": "2025-08-30",
            "notification_days_before": 1,
            "last_notification_sent": None,
            "notification_settings": {
                "email_enabled": False,
                "console_enabled": True,
                "admin_email": "dansidanutz@example.com"
            },
            "usage_thresholds": {
                "warning": 70,    # 70% usage warning
                "critical": 85,   # 85% usage critical
                "emergency": 95   # 95% usage emergency
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Update with any missing keys
                for key, value in default_config.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                return loaded_config
            except Exception as e:
                logger.error(f"❌ Error loading config: {e}")
                return default_config
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
    
    def update_usage(self, current_usage: int, reset_date: str = None, expiry_date: str = None):
        """Update current usage and dates"""
        self.config["current_usage"] = current_usage
        
        if reset_date:
            self.config["reset_date"] = reset_date
        
        if expiry_date:
            self.config["subscription_expiry"] = expiry_date
        
        self._save_config()
        logger.info(f"📊 Usage updated: {current_usage:,}/{self.config['monthly_limit']:,}")
    
    def check_subscription_status(self) -> Dict[str, Any]:
        """Check subscription status and trigger notifications if needed"""
        today = datetime.now().date()
        
        # Parse dates
        try:
            expiry_date = datetime.strptime(self.config["subscription_expiry"], "%Y-%m-%d").date()
            reset_date = datetime.strptime(self.config["reset_date"], "%Y-%m-%d").date()
        except ValueError as e:
            logger.error(f"❌ Error parsing dates: {e}")
            return {"error": "Invalid date format"}
        
        # Calculate days until expiry
        days_until_expiry = (expiry_date - today).days
        days_until_reset = (reset_date - today).days
        
        # Calculate usage percentage
        usage_percent = (self.config["current_usage"] / self.config["monthly_limit"]) * 100
        remaining_calls = self.config["monthly_limit"] - self.config["current_usage"]
        
        status = {
            "api_plan": self.config["api_plan"],
            "current_usage": self.config["current_usage"],
            "monthly_limit": self.config["monthly_limit"],
            "remaining_calls": remaining_calls,
            "usage_percent": round(usage_percent, 2),
            "days_until_expiry": days_until_expiry,
            "days_until_reset": days_until_reset,
            "expiry_date": self.config["subscription_expiry"],
            "reset_date": self.config["reset_date"],
            "status": "active"
        }
        
        # Check for expiry notification
        if days_until_expiry <= self.config["notification_days_before"]:
            self._send_expiry_notification(days_until_expiry, status)
        
        # Check usage thresholds
        self._check_usage_thresholds(usage_percent, remaining_calls)
        
        return status
    
    def _send_expiry_notification(self, days_until_expiry: int, status: Dict[str, Any]):
        """Send expiry notification"""
        # Check if we already sent notification today
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        if self.config.get("last_notification_sent") == today_str:
            return  # Already sent today
        
        if days_until_expiry == 1:
            urgency = "🚨 CRITICAL"
            message = "Your Cryptometer API subscription expires TOMORROW!"
        elif days_until_expiry == 0:
            urgency = "🔴 EMERGENCY"
            message = "Your Cryptometer API subscription expires TODAY!"
        else:
            urgency = "⚠️ WARNING"
            message = f"Your Cryptometer API subscription expires in {days_until_expiry} days!"
        
        notification_text = f"""
{urgency} - CRYPTOMETER API SUBSCRIPTION EXPIRY ALERT

Hello DANSIDANUTZ,

{message}

📊 Current Status:
- API Plan: {status['api_plan']}
- Usage: {status['current_usage']:,}/{status['monthly_limit']:,} calls ({status['usage_percent']}%)
- Remaining: {status['remaining_calls']:,} calls
- Expiry Date: {status['expiry_date']}
- Days Until Expiry: {days_until_expiry}

🔄 Next Reset: {status['reset_date']} ({status['days_until_reset']} days)

🎯 Action Required:
Please renew your Cryptometer API subscription before {status['expiry_date']} to avoid service interruption.

📈 ZmartBot Subscription Monitor
        """.strip()
        
        # Console notification (always enabled)
        if self.config["notification_settings"]["console_enabled"]:
            print("\n" + "="*70)
            print(notification_text)
            print("="*70 + "\n")
            logger.warning(f"{urgency} Subscription expires in {days_until_expiry} days")
        
        # Email notification (if enabled)
        if self.config["notification_settings"]["email_enabled"]:
            self._send_email_notification(notification_text, urgency)
        
        # Update last notification date
        self.config["last_notification_sent"] = today_str
        self._save_config()
    
    def _check_usage_thresholds(self, usage_percent: float, remaining_calls: int):
        """Check and alert on usage thresholds"""
        thresholds = self.config["usage_thresholds"]
        
        if usage_percent >= thresholds["emergency"]:
            logger.error(f"🚨 EMERGENCY: API usage at {usage_percent:.1f}% ({remaining_calls:,} calls remaining)")
        elif usage_percent >= thresholds["critical"]:
            logger.warning(f"🔴 CRITICAL: API usage at {usage_percent:.1f}% ({remaining_calls:,} calls remaining)")
        elif usage_percent >= thresholds["warning"]:
            logger.warning(f"🟡 WARNING: API usage at {usage_percent:.1f}% ({remaining_calls:,} calls remaining)")
        else:
            logger.info(f"✅ Usage healthy: {usage_percent:.1f}% ({remaining_calls:,} calls remaining)")
    
    def _send_email_notification(self, message: str, urgency: str):
        """Send email notification (if configured)"""
        try:
            # Email configuration (you'll need to set these up)
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("NOTIFICATION_EMAIL_USER")
            email_pass = os.getenv("NOTIFICATION_EMAIL_PASS")
            
            if not email_user or not email_pass:
                logger.warning("📧 Email credentials not configured, skipping email notification")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = self.config["notification_settings"]["admin_email"]
            msg['Subject'] = f"{urgency} - ZmartBot API Subscription Alert"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_pass)
            text = msg.as_string()
            server.sendmail(email_user, self.config["notification_settings"]["admin_email"], text)
            server.quit()
            
            logger.info(f"📧 Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")
    
    def _log_current_status(self):
        """Log current subscription status"""
        try:
            status = self.check_subscription_status()
            if "error" not in status:
                logger.info(f"📊 API Plan: {status['api_plan']}")
                logger.info(f"📈 Usage: {status['current_usage']:,}/{status['monthly_limit']:,} ({status['usage_percent']}%)")
                logger.info(f"📅 Expires: {status['expiry_date']} ({status['days_until_expiry']} days)")
                logger.info(f"🔄 Reset: {status['reset_date']} ({status['days_until_reset']} days)")
        except Exception as e:
            logger.error(f"❌ Error logging status: {e}")
    
    def get_usage_forecast(self) -> Dict[str, Any]:
        """Forecast usage based on current patterns"""
        try:
            today = datetime.now().date()
            reset_date = datetime.strptime(self.config["reset_date"], "%Y-%m-%d").date()
            days_remaining = (reset_date - today).days
            
            if days_remaining <= 0:
                return {"error": "Reset date has passed"}
            
            current_usage = self.config["current_usage"]
            daily_avg = current_usage / (31 - days_remaining) if days_remaining < 31 else current_usage / 1
            
            # Forecast remaining usage
            forecast_usage = current_usage + (daily_avg * days_remaining)
            forecast_percent = (forecast_usage / self.config["monthly_limit"]) * 100
            
            return {
                "current_usage": current_usage,
                "days_remaining": days_remaining,
                "daily_average": round(daily_avg, 1),
                "forecast_total": round(forecast_usage),
                "forecast_percent": round(forecast_percent, 2),
                "will_exceed_limit": forecast_usage > self.config["monthly_limit"],
                "recommended_daily_limit": round((self.config["monthly_limit"] - current_usage) / days_remaining, 1) if days_remaining > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating forecast: {e}")
            return {"error": str(e)}

# Global instance
subscription_monitor = SubscriptionMonitor()

# Helper functions
def check_subscription() -> Dict[str, Any]:
    """Check subscription status"""
    return subscription_monitor.check_subscription_status()

def update_subscription_usage(current_usage: int, reset_date: str = None, expiry_date: str = None):
    """Update subscription usage"""
    return subscription_monitor.update_usage(current_usage, reset_date, expiry_date)

def get_usage_forecast() -> Dict[str, Any]:
    """Get usage forecast"""
    return subscription_monitor.get_usage_forecast()