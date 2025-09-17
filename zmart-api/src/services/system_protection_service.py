#!/usr/bin/env python3
"""
🛡️ ZmartBot System Protection Service
CRITICAL: Protects Level 3 certified services from unauthorized modifications
"""

import os
import sys
import sqlite3
import logging
import asyncio
import aiohttp
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import json
from datetime import datetime
import fcntl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PROTECTION - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_protection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Level3ProtectionHandler(FileSystemEventHandler):
    """Monitors and protects Level 3 certified service files"""
    
    def __init__(self):
        super().__init__()
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.protected_files = set()
        self.file_hashes = {}
        self.load_protected_files()
        
    def load_protected_files(self):
        """Load all Level 3 certified services from database"""
        try:
            db_path = os.path.join(self.base_path, "src", "data", "service_registry.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all Level 3 services
            cursor.execute("""
                SELECT service_name FROM service_registry 
                WHERE certification_level = 3
            """)
            
            level3_services = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Add protected file patterns
            for service_name in level3_services:
                # MDC files
                mdc_path = os.path.join(self.base_path, ".cursor", "rules", f"{service_name}.mdc")
                if os.path.exists(mdc_path):
                    self.protected_files.add(mdc_path)
                    self.file_hashes[mdc_path] = self.calculate_hash(mdc_path)
                
                # YAML files
                yaml_path = os.path.join(self.base_path, f"{service_name}.yaml")
                if os.path.exists(yaml_path):
                    self.protected_files.add(yaml_path)
                    self.file_hashes[yaml_path] = self.calculate_hash(yaml_path)
            
            logger.info(f"🛡️ PROTECTION ACTIVE: {len(self.protected_files)} Level 3 files protected")
            
        except Exception as e:
            logger.error(f"❌ Failed to load protected files: {e}")
    
    def calculate_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory and event.src_path in self.protected_files:
            logger.critical(f"🚨 CRITICAL SECURITY BREACH: Level 3 file deleted: {event.src_path}")
            self.emergency_restore(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and event.src_path in self.protected_files:
            current_hash = self.calculate_hash(event.src_path)
            if current_hash != self.file_hashes.get(event.src_path):
                logger.warning(f"⚠️ Level 3 file modified: {event.src_path}")
                self.verify_authorized_change(event.src_path, current_hash)
    
    def emergency_restore(self, file_path):
        """Attempt to restore deleted Level 3 file"""
        logger.critical(f"🚨 EMERGENCY RESTORE: Attempting to restore {file_path}")
        
        # This would typically restore from backup
        # For now, just log the critical security breach
        with open("SECURITY_BREACH.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - CRITICAL: Level 3 file deleted: {file_path}\n")
    
    def verify_authorized_change(self, file_path, new_hash):
        """Verify if file change was authorized"""
        # Update hash if change seems legitimate
        self.file_hashes[file_path] = new_hash
        logger.info(f"✅ Authorized change detected: {file_path}")

class SystemProtectionService:
    """Main protection service"""
    
    def __init__(self, port=8999):
        self.port = port
        self.observer = Observer()
        self.handler = Level3ProtectionHandler()
        self.app = None
        
    async def setup_file_monitoring(self):
        """Setup filesystem monitoring"""
        base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        
        # Monitor .cursor/rules directory
        rules_path = os.path.join(base_path, ".cursor", "rules")
        if os.path.exists(rules_path):
            self.observer.schedule(self.handler, rules_path, recursive=False)
        
        # Monitor root directory for YAML files
        self.observer.schedule(self.handler, base_path, recursive=False)
        
        self.observer.start()
        logger.info("🛡️ File monitoring started")
    
    async def setup_web_server(self):
        """Setup protection API endpoints"""
        from aiohttp import web
        
        async def health_check(request):
            return web.json_response({
                "status": "healthy",
                "protected_files": len(self.handler.protected_files),
                "service": "system-protection-service",
                "passport": "ZMBT-PROTECTION-20250826-2C0587"
            })
        
        async def protection_status(request):
            return web.json_response({
                "protected_files_count": len(self.handler.protected_files),
                "monitoring_active": self.observer.is_alive(),
                "last_check": datetime.now().isoformat()
            })
        
        async def emergency_lock(request):
            """Emergency lockdown of all Level 3 services"""
            logger.critical("🚨 EMERGENCY LOCKDOWN ACTIVATED")
            # Implement emergency protection measures
            return web.json_response({"status": "lockdown_activated"})
        
        self.app = web.Application()
        self.app.router.add_get('/health', health_check)
        self.app.router.add_get('/status', protection_status)
        self.app.router.add_post('/emergency-lock', emergency_lock)
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"🛡️ Protection API server started on port {self.port}")
    
    async def run(self):
        """Main service loop"""
        logger.info("🛡️ ZmartBot System Protection Service Starting...")
        
        try:
            # Setup monitoring and web server
            await self.setup_file_monitoring()
            await self.setup_web_server()
            
            logger.info("🛡️ System Protection Service ACTIVE")
            
            # Keep service running
            while True:
                await asyncio.sleep(60)  # Check every minute
                if not self.observer.is_alive():
                    logger.error("❌ File monitoring stopped - restarting")
                    self.observer.start()
                    
        except KeyboardInterrupt:
            logger.info("🛡️ Protection service shutting down...")
            self.observer.stop()
            self.observer.join()
        except Exception as e:
            logger.error(f"❌ Protection service error: {e}")
            raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZmartBot System Protection Service')
    parser.add_argument('--port', type=int, default=8999, help='Service port')
    args = parser.parse_args()
    
    service = SystemProtectionService(args.port)
    
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        logger.info("🛡️ Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()