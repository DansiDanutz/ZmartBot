#!/usr/bin/env python3
"""
🛡️ IMMEDIATE PROTECTION ACTIVATOR
Activates protection IMMEDIATELY when service reaches Level 3
This runs in the background monitoring the database for Level 3 promotions
"""

import os
import sys
import sqlite3
import time
import logging
import threading
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IMMEDIATE-PROTECTION - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('immediate_protection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImmediateProtectionActivator:
    """Monitors database and activates protection immediately for Level 3 services"""
    
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.db_path = os.path.join(self.base_path, "src", "data", "service_registry.db")
        self.protected_services = set()
        self.running = True
        self.file_locks = {}
        
    def get_level3_services(self):
        """Get all current Level 3 services"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name FROM service_registry 
                WHERE certification_level = 3
            """)
            
            services = {row[0] for row in cursor.fetchall()}
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return set()
    
    def protect_file_immediately(self, file_path):
        """Apply immediate file protection"""
        try:
            if os.path.exists(file_path):
                # Make file read-only
                os.chmod(file_path, 0o444)
                
                # Add file attribute protection (macOS)
                try:
                    subprocess.run(['chflags', 'schg', file_path], check=True)
                    logger.info(f"🔒 IMMEDIATE PROTECTION: {file_path}")
                except:
                    logger.warning(f"⚠️ Could not set system immutable flag on {file_path}")
                    
                return True
        except Exception as e:
            logger.error(f"❌ Failed to protect {file_path}: {e}")
            return False
    
    def activate_service_protection(self, service_name):
        """Activate immediate protection for a newly promoted Level 3 service"""
        logger.critical(f"🚨 IMMEDIATE PROTECTION ACTIVATION: {service_name}")
        
        # Protect MDC file
        mdc_path = os.path.join(self.base_path, ".cursor", "rules", f"{service_name}.mdc")
        if os.path.exists(mdc_path):
            self.protect_file_immediately(mdc_path)
        
        # Protect YAML file
        yaml_path = os.path.join(self.base_path, f"{service_name}.yaml")
        if os.path.exists(yaml_path):
            self.protect_file_immediately(yaml_path)
        
        # Create protection marker
        marker_path = os.path.join(self.base_path, f".protection_active_{service_name}")
        with open(marker_path, 'w') as f:
            f.write(f"PROTECTED: {service_name} - Level 3 - {time.time()}")
        
        logger.info(f"✅ PROTECTION ACTIVE: {service_name}")
    
    def monitor_level3_promotions(self):
        """Continuously monitor for new Level 3 promotions"""
        logger.info("🛡️ IMMEDIATE PROTECTION MONITOR: Starting continuous surveillance")
        
        while self.running:
            try:
                current_level3 = self.get_level3_services()
                
                # Check for newly promoted services
                new_promotions = current_level3 - self.protected_services
                
                if new_promotions:
                    logger.critical(f"🚨 NEW LEVEL 3 PROMOTIONS DETECTED: {new_promotions}")
                    
                    for service_name in new_promotions:
                        self.activate_service_protection(service_name)
                        self.protected_services.add(service_name)
                
                # Update protected set
                self.protected_services = current_level3
                
                # Log status every 30 seconds
                if int(time.time()) % 30 == 0:
                    logger.info(f"🛡️ PROTECTION STATUS: {len(self.protected_services)} services protected")
                
                time.sleep(1)  # Check every second for immediate response
                
            except KeyboardInterrupt:
                logger.info("🛡️ Protection monitor stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def create_file_watchers(self):
        """Create filesystem watchers for protected files"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class ProtectionHandler(FileSystemEventHandler):
            def __init__(self, activator):
                self.activator = activator
                
            def on_deleted(self, event):
                if not event.is_directory:
                    file_name = os.path.basename(event.src_path)
                    if file_name.endswith('.mdc') or file_name.endswith('.yaml'):
                        service_name = file_name.replace('.mdc', '').replace('.yaml', '')
                        if service_name in self.activator.protected_services:
                            logger.critical(f"🚨 CRITICAL SECURITY BREACH: Level 3 file deleted: {event.src_path}")
                            # Immediate restore attempt would go here
            
            def on_modified(self, event):
                if not event.is_directory:
                    file_name = os.path.basename(event.src_path)
                    if file_name.endswith('.mdc') or file_name.endswith('.yaml'):
                        service_name = file_name.replace('.mdc', '').replace('.yaml', '')
                        if service_name in self.activator.protected_services:
                            logger.warning(f"⚠️ Protected file modified: {event.src_path}")
        
        observer = Observer()
        handler = ProtectionHandler(self)
        
        # Watch .cursor/rules directory
        rules_path = os.path.join(self.base_path, ".cursor", "rules")
        if os.path.exists(rules_path):
            observer.schedule(handler, rules_path, recursive=False)
        
        # Watch root directory for YAML files
        observer.schedule(handler, self.base_path, recursive=False)
        
        observer.start()
        return observer
    
    def run(self):
        """Main protection loop"""
        logger.critical("🛡️ IMMEDIATE PROTECTION ACTIVATOR: STARTING")
        
        # Initial protection for existing Level 3 services
        current_level3 = self.get_level3_services()
        logger.info(f"🔍 Found {len(current_level3)} existing Level 3 services")
        
        for service_name in current_level3:
            self.activate_service_protection(service_name)
            self.protected_services.add(service_name)
        
        # Start filesystem watcher
        observer = None
        try:
            observer = self.create_file_watchers()
            logger.info("🛡️ Filesystem watchers activated")
        except Exception as e:
            logger.error(f"❌ Could not start filesystem watchers: {e}")
        
        # Start continuous monitoring
        try:
            self.monitor_level3_promotions()
        finally:
            if observer:
                observer.stop()
                observer.join()
            logger.info("🛡️ Immediate Protection Activator stopped")

def main():
    """Entry point"""
    activator = ImmediateProtectionActivator()
    
    try:
        activator.run()
    except KeyboardInterrupt:
        logger.info("🛡️ Stopped by user")
    except Exception as e:
        logger.error(f"❌ Activator failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()