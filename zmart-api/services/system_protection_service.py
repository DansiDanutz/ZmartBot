#!/usr/bin/env python3
"""
System Protection Service - CRITICAL PRIORITY
Prevents accidental mass deletions and ensures system integrity
"""

import os
import json
import time
import shutil
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_protection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SystemProtectionService')

class SystemProtectionService:
    """Critical system protection service"""
    
    def __init__(self, config_path: str = "system_protection_config.json"):
        self.config = self._load_config(config_path)
        self.running = False
        self.monitor_thread = None
        self.last_check = None
        self.backup_dir = Path(self.config['backup_directory'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Critical directories to protect
        self.critical_dirs = [
            Path(d) for d in self.config['critical_directories']
        ]
        
        logger.info("🛡️  System Protection Service initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration with safe defaults"""
        default_config = {
            "protection_enabled": True,
            "monitoring_interval": 60,
            "min_mdc_files": 50,
            "alert_threshold": 30,
            "auto_backup": True,
            "auto_restore": True,
            "backup_retention": 30,
            "backup_directory": "./system_backups",
            "critical_directories": [
                ".cursor/rules",
                "Dashboard/MDC-Dashboard",
                "Documentation"
            ],
            "protected_patterns": [
                "*.mdc",
                "*.py",
                "*.js",
                "*.html",
                "*.css",
                "CLAUDE.md",
                ".env*",
                "package.json",
                "requirements.txt"
            ]
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                
        return default_config
    
    def count_mdc_files(self) -> int:
        """Count MDC files in critical directories"""
        mdc_count = 0
        rules_dir = Path('.cursor/rules')
        
        if rules_dir.exists():
            mdc_files = list(rules_dir.glob('**/*.mdc'))
            mdc_count = len(mdc_files)
            
        logger.debug(f"📊 MDC file count: {mdc_count}")
        return mdc_count
    
    def verify_system_integrity(self) -> Tuple[bool, Dict]:
        """Verify system integrity and return status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'mdc_count': 0,
            'critical_dirs_ok': True,
            'issues': []
        }
        
        try:
            # Check MDC files
            mdc_count = self.count_mdc_files()
            status['mdc_count'] = mdc_count
            
            if mdc_count < self.config['alert_threshold']:
                status['issues'].append(f"MDC file count critically low: {mdc_count}")
                logger.critical(f"🚨 CRITICAL: MDC file count: {mdc_count} (threshold: {self.config['alert_threshold']})")
                
            # Check critical directories
            for dir_path in self.critical_dirs:
                if not dir_path.exists():
                    status['critical_dirs_ok'] = False
                    status['issues'].append(f"Critical directory missing: {dir_path}")
                    logger.critical(f"🚨 CRITICAL: Missing directory: {dir_path}")
            
            # Overall health assessment
            is_healthy = (
                mdc_count >= self.config['min_mdc_files'] and
                status['critical_dirs_ok'] and
                len(status['issues']) == 0
            )
            
            status['healthy'] = is_healthy
            
            if not is_healthy:
                logger.warning(f"⚠️  System integrity issues detected: {status['issues']}")
            else:
                logger.info("✅ System integrity verified")
                
            return is_healthy, status
            
        except Exception as e:
            logger.error(f"System verification failed: {e}")
            status['issues'].append(f"Verification error: {e}")
            status['healthy'] = False
            return False, status
    
    def create_emergency_backup(self) -> Dict:
        """Create emergency backup of critical files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"emergency_backup_{timestamp}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            files_backed_up = 0
            
            # Backup critical directories
            for dir_path in self.critical_dirs:
                if dir_path.exists():
                    dest_path = backup_path / dir_path.name
                    shutil.copytree(dir_path, dest_path, dirs_exist_ok=True)
                    files_backed_up += sum(1 for _ in dest_path.rglob('*') if _.is_file())
                    logger.info(f"📦 Backed up: {dir_path} -> {dest_path}")
            
            # Backup critical individual files
            critical_files = ['CLAUDE.md', 'package.json', 'requirements.txt', '.env']
            for file_name in critical_files:
                file_path = Path(file_name)
                if file_path.exists():
                    dest_file = backup_path / file_name
                    shutil.copy2(file_path, dest_file)
                    files_backed_up += 1
            
            backup_info = {
                'success': True,
                'backup_path': str(backup_path),
                'timestamp': timestamp,
                'files_backed_up': files_backed_up,
                'backup_size': self._get_directory_size(backup_path)
            }
            
            # Save backup manifest
            manifest_path = backup_path / 'backup_manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"🔒 Emergency backup created: {files_backed_up} files backed up to {backup_path}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Emergency backup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate directory size in bytes"""
        try:
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        except:
            return 0
    
    def attempt_git_restoration(self) -> bool:
        """Attempt to restore files from git"""
        try:
            logger.info("🔄 Attempting git restoration...")
            
            # Try to restore MDC files from last known good commit
            cmd = ['git', 'show', 'ca094a6', '--name-only']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                mdc_files = [line for line in result.stdout.splitlines() 
                           if line.endswith('.mdc') and '.cursor/rules' in line]
                
                restored_count = 0
                for mdc_file in mdc_files:
                    try:
                        # Create directory if needed
                        file_path = Path(mdc_file)
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Restore file content
                        restore_cmd = ['git', 'show', f'ca094a6:{mdc_file}']
                        restore_result = subprocess.run(restore_cmd, capture_output=True, text=True)
                        
                        if restore_result.returncode == 0:
                            with open(file_path, 'w') as f:
                                f.write(restore_result.stdout)
                            restored_count += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to restore {mdc_file}: {e}")
                
                logger.info(f"✅ Git restoration completed: {restored_count} files restored")
                return restored_count > 0
                
        except Exception as e:
            logger.error(f"Git restoration failed: {e}")
            
        return False
    
    def attempt_backup_restoration(self) -> bool:
        """Attempt to restore from most recent backup"""
        try:
            # Find most recent backup
            backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()], 
                           key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not backups:
                logger.warning("No backups available for restoration")
                return False
            
            latest_backup = backups[0]
            logger.info(f"🔄 Attempting restoration from: {latest_backup}")
            
            restored_count = 0
            
            # Restore critical directories
            for dir_path in self.critical_dirs:
                backup_dir_path = latest_backup / dir_path.name
                if backup_dir_path.exists():
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                    shutil.copytree(backup_dir_path, dir_path)
                    restored_count += sum(1 for _ in dir_path.rglob('*') if _.is_file())
            
            logger.info(f"✅ Backup restoration completed: {restored_count} files restored")
            return restored_count > 0
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return False
    
    def trigger_emergency_response(self) -> Dict:
        """Trigger comprehensive emergency response"""
        logger.critical("🚨 TRIGGERING EMERGENCY RESPONSE")
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'success': False
        }
        
        try:
            # Step 1: Create emergency backup of remaining files
            if self.config['auto_backup']:
                backup_result = self.create_emergency_backup()
                response['actions_taken'].append(f"Emergency backup: {'success' if backup_result['success'] else 'failed'}")
            
            # Step 2: Attempt automatic restoration if enabled
            if self.config['auto_restore']:
                # Try backup restoration first
                if self.attempt_backup_restoration():
                    response['actions_taken'].append("Backup restoration: success")
                    response['success'] = True
                # Fallback to git restoration
                elif self.attempt_git_restoration():
                    response['actions_taken'].append("Git restoration: success")
                    response['success'] = True
                else:
                    response['actions_taken'].append("All restoration attempts failed")
            
            # Step 3: Verify restoration success
            is_healthy, status = self.verify_system_integrity()
            response['post_restoration_health'] = status
            
            if is_healthy:
                logger.info("✅ Emergency response successful - system integrity restored")
                response['success'] = True
            else:
                logger.critical("❌ Emergency response partially failed - manual intervention required")
            
        except Exception as e:
            logger.critical(f"Emergency response failed: {e}")
            response['actions_taken'].append(f"Response error: {e}")
        
        return response
    
    def cleanup_old_backups(self):
        """Clean up backups older than retention period"""
        try:
            retention_days = self.config['backup_retention']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            removed_count = 0
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    backup_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                    if backup_time < cutoff_date:
                        shutil.rmtree(backup_dir)
                        removed_count += 1
            
            if removed_count > 0:
                logger.info(f"🧹 Cleaned up {removed_count} old backups")
                
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting system monitoring loop")
        
        while self.running:
            try:
                # Verify system integrity
                is_healthy, status = self.verify_system_integrity()
                self.last_check = status['timestamp']
                
                # Trigger emergency response if needed
                if not is_healthy and status['mdc_count'] < self.config['alert_threshold']:
                    self.trigger_emergency_response()
                
                # Cleanup old backups periodically
                if datetime.now().hour == 2 and datetime.now().minute < 5:  # 2 AM cleanup
                    self.cleanup_old_backups()
                
                # Wait for next check
                time.sleep(self.config['monitoring_interval'])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(30)  # Shorter wait on error
    
    def start(self):
        """Start the protection service"""
        if self.running:
            logger.warning("Service already running")
            return
        
        logger.info("🚀 Starting System Protection Service")
        
        # Initial system check
        is_healthy, status = self.verify_system_integrity()
        if not is_healthy:
            logger.warning("⚠️  System integrity issues detected at startup")
        
        # Create initial backup
        if self.config['auto_backup']:
            self.create_emergency_backup()
        
        # Start monitoring
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ System Protection Service started")
    
    def stop(self):
        """Stop the protection service"""
        logger.info("🛑 Stopping System Protection Service")
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("✅ System Protection Service stopped")
    
    def get_status(self) -> Dict:
        """Get current service status"""
        is_healthy, integrity_status = self.verify_system_integrity()
        
        return {
            'service_running': self.running,
            'last_check': self.last_check,
            'system_healthy': is_healthy,
            'integrity_status': integrity_status,
            'config': self.config,
            'available_backups': len([d for d in self.backup_dir.iterdir() if d.is_dir()])
        }

def main():
    """Main entry point for standalone service"""
    import signal
    import sys
    
    service = SystemProtectionService()
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        service.start()
        logger.info("System Protection Service running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while service.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        service.stop()

if __name__ == "__main__":
    main()