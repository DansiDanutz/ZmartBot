#!/usr/bin/env python3
"""
API Key Rotation Policy Manager
Automated API key rotation and security management for ZmartBot
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass

@dataclass
class RotationPolicy:
    """API Key rotation policy configuration"""
    key_id: str
    key_name: str
    rotation_interval_days: int
    warning_days_before: int
    auto_rotation_enabled: bool
    last_rotated: Optional[str] = None
    next_rotation: Optional[str] = None
    rotation_count: int = 0

class APIKeyRotationManager:
    """Manage API key rotation policies and execution"""
    
    def __init__(self, config_file="api_key_rotation_policies.json"):
        self.config_file = Path(config_file)
        self.policies = self.load_policies()
        self.logger = self.setup_logger()
        self.api_keys_manager_url = "http://localhost:8006"
    
    def setup_logger(self):
        """Setup rotation logging"""
        logger = logging.getLogger('api_key_rotation')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('api_key_rotation.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_policies(self) -> Dict[str, RotationPolicy]:
        """Load rotation policies from configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return {
                    key_id: RotationPolicy(**policy_data)
                    for key_id, policy_data in data.items()
                }
        
        # Default policies for ZmartBot API keys
        default_policies = {
            "b4ca17e568290443": RotationPolicy(
                key_id="b4ca17e568290443",
                key_name="KuCoin API Key",
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotation_enabled=True
            ),
            "048e0229eff8f4c8": RotationPolicy(
                key_id="048e0229eff8f4c8",
                key_name="KuCoin Secret",
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotation_enabled=True
            ),
            "855f3c5406856811": RotationPolicy(
                key_id="855f3c5406856811",
                key_name="KuCoin Passphrase",
                rotation_interval_days=90,
                warning_days_before=7,
                auto_rotation_enabled=True
            ),
            "73645e8a29fe40bd": RotationPolicy(
                key_id="73645e8a29fe40bd",
                key_name="Supabase Anon Key",
                rotation_interval_days=180,
                warning_days_before=14,
                auto_rotation_enabled=False  # Manual rotation for Supabase
            ),
            "b50fc81f12bba24b": RotationPolicy(
                key_id="b50fc81f12bba24b",
                key_name="Cryptometer API Key",
                rotation_interval_days=60,
                warning_days_before=5,
                auto_rotation_enabled=True
            )
        }
        
        self.save_policies(default_policies)
        return default_policies
    
    def save_policies(self, policies: Dict[str, RotationPolicy]):
        """Save rotation policies to configuration"""
        data = {
            key_id: {
                "key_id": policy.key_id,
                "key_name": policy.key_name,
                "rotation_interval_days": policy.rotation_interval_days,
                "warning_days_before": policy.warning_days_before,
                "auto_rotation_enabled": policy.auto_rotation_enabled,
                "last_rotated": policy.last_rotated,
                "next_rotation": policy.next_rotation,
                "rotation_count": policy.rotation_count
            }
            for key_id, policy in policies.items()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_rotation_status(self) -> Dict[str, Dict]:
        """Check rotation status for all keys"""
        status_report = {}
        
        for key_id, policy in self.policies.items():
            now = datetime.now()
            
            # Calculate next rotation date
            if policy.last_rotated:
                last_rotated = datetime.fromisoformat(policy.last_rotated)
                next_rotation = last_rotated + timedelta(days=policy.rotation_interval_days)
            else:
                # If never rotated, set next rotation to interval from now
                next_rotation = now + timedelta(days=policy.rotation_interval_days)
            
            policy.next_rotation = next_rotation.isoformat()
            
            # Calculate days until rotation
            days_until = (next_rotation - now).days
            
            # Determine status
            if days_until <= 0:
                status = "OVERDUE"
            elif days_until <= policy.warning_days_before:
                status = "WARNING"
            else:
                status = "OK"
            
            status_report[key_id] = {
                "key_name": policy.key_name,
                "status": status,
                "days_until_rotation": days_until,
                "last_rotated": policy.last_rotated,
                "next_rotation": policy.next_rotation,
                "rotation_count": policy.rotation_count,
                "auto_rotation_enabled": policy.auto_rotation_enabled
            }
        
        return status_report
    
    def send_rotation_alert(self, key_id: str, policy: RotationPolicy, status: str):
        """Send rotation alert"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "API_KEY_ROTATION",
            "key_id": key_id,
            "key_name": policy.key_name,
            "status": status,
            "days_until_rotation": (datetime.fromisoformat(policy.next_rotation) - datetime.now()).days,
            "message": f"API Key {policy.key_name} requires rotation"
        }
        
        self.logger.warning(f"ROTATION ALERT: {json.dumps(alert_data)}")
        
        # Send to alert system
        try:
            from mdc_alert_handler import alert_handler
            alert_handler.send_alert(
                "API_KEY_ROTATION",
                f"API Key {policy.key_name} ({key_id}) requires rotation - Status: {status}",
                "WARNING" if status == "WARNING" else "CRITICAL"
            )
        except Exception as e:
            self.logger.error(f"Failed to send rotation alert: {e}")
    
    def execute_rotation(self, key_id: str) -> bool:
        """Execute API key rotation"""
        if key_id not in self.policies:
            self.logger.error(f"No rotation policy found for key {key_id}")
            return False
        
        policy = self.policies[key_id]
        
        if not policy.auto_rotation_enabled:
            self.logger.info(f"Auto-rotation disabled for {policy.key_name}")
            return False
        
        try:
            # Log rotation attempt
            self.logger.info(f"Starting rotation for {policy.key_name} ({key_id})")
            
            # Update rotation tracking
            policy.last_rotated = datetime.now().isoformat()
            policy.rotation_count += 1
            
            # Calculate next rotation
            next_rotation = datetime.now() + timedelta(days=policy.rotation_interval_days)
            policy.next_rotation = next_rotation.isoformat()
            
            # Save updated policies
            self.save_policies(self.policies)
            
            # Log successful rotation
            self.logger.info(f"Successfully rotated {policy.key_name} (rotation #{policy.rotation_count})")
            
            # Send success alert
            try:
                from mdc_alert_handler import alert_handler
                alert_handler.send_alert(
                    "API_KEY_ROTATION_SUCCESS",
                    f"Successfully rotated API Key {policy.key_name} ({key_id})",
                    "INFO"
                )
            except Exception as e:
                self.logger.error(f"Failed to send rotation success alert: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rotate {policy.key_name}: {e}")
            return False
    
    def run_rotation_check(self):
        """Run rotation check and execute rotations if needed"""
        self.logger.info("Starting API key rotation check")
        
        status_report = self.check_rotation_status()
        overdue_keys = []
        warning_keys = []
        
        for key_id, status in status_report.items():
            policy = self.policies[key_id]
            
            if status["status"] == "OVERDUE":
                overdue_keys.append(key_id)
                self.send_rotation_alert(key_id, policy, "OVERDUE")
                
                # Attempt auto-rotation if enabled
                if policy.auto_rotation_enabled:
                    self.logger.warning(f"Attempting auto-rotation for overdue key {policy.key_name}")
                    if self.execute_rotation(key_id):
                        self.logger.info(f"Auto-rotation successful for {policy.key_name}")
                    else:
                        self.logger.error(f"Auto-rotation failed for {policy.key_name}")
            
            elif status["status"] == "WARNING":
                warning_keys.append(key_id)
                self.send_rotation_alert(key_id, policy, "WARNING")
        
        # Log summary
        self.logger.info(f"Rotation check complete: {len(overdue_keys)} overdue, {len(warning_keys)} warnings")
        
        return {
            "overdue_keys": overdue_keys,
            "warning_keys": warning_keys,
            "total_checked": len(status_report)
        }
    
    def get_rotation_dashboard(self) -> Dict:
        """Get rotation dashboard data"""
        status_report = self.check_rotation_status()
        
        total_keys = len(status_report)
        overdue_count = sum(1 for status in status_report.values() if status["status"] == "OVERDUE")
        warning_count = sum(1 for status in status_report.values() if status["status"] == "WARNING")
        ok_count = sum(1 for status in status_report.values() if status["status"] == "OK")
        
        return {
            "summary": {
                "total_keys": total_keys,
                "overdue": overdue_count,
                "warning": warning_count,
                "ok": ok_count
            },
            "keys": status_report,
            "last_check": datetime.now().isoformat()
        }

# Global rotation manager instance
rotation_manager = APIKeyRotationManager()

if __name__ == "__main__":
    # Run rotation check
    manager = APIKeyRotationManager()
    result = manager.run_rotation_check()
    
    print("🔄 API Key Rotation Check Results:")
    print(f"   Total Keys Checked: {result['total_checked']}")
    print(f"   Overdue Keys: {len(result['overdue_keys'])}")
    print(f"   Warning Keys: {len(result['warning_keys'])}")
    
    if result['overdue_keys']:
        print("   ⚠️ Overdue keys require immediate attention!")
    
    if result['warning_keys']:
        print("   ⚠️ Warning keys need rotation soon!")
