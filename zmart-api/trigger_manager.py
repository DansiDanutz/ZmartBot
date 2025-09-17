#!/usr/bin/env python3
"""
ZmartBot Trigger Manager - Level 2 & 3 Services Only
Manages triggers for ACTIVE (Level 2) and REGISTERED (Level 3) services exclusively
Discovery services are excluded from trigger management
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml
import re
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trigger_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TriggerDefinition:
    """Trigger definition structure"""
    name: str
    source_mdc: str
    service_name: str
    service_level: int  # 2 for ACTIVE, 3 for REGISTERED
    event: str
    condition: str
    action: str
    frequency: str
    validation: str
    port: Optional[int] = None
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 100.0

class TriggerManager:
    """Level 2 & 3 Trigger Management System"""
    
    def __init__(self, port: int = 8890):
        self.port = port
        self.app = self.create_app()
        self.trigger_registry: Dict[str, TriggerDefinition] = {}
        self.mdc_paths = [
            "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/rules/",
            "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/"
        ]
        self.passport_db_path = "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"
        self.service_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/service_registry.db"
        self.level_2_3_services_only = True
        self.last_sync_time = None
        
    def get_active_services(self) -> List[Dict]:
        """Get Level 2 (ACTIVE) services with valid ports"""
        services = []
        
        try:
            if not os.path.exists(self.passport_db_path):
                logger.warning(f"Passport registry not found: {self.passport_db_path}")
                return services
                
            conn = sqlite3.connect(self.passport_db_path)
            cursor = conn.cursor()
            
            # CRITICAL: Only ACTIVE services with valid ports
            cursor.execute("""
                SELECT service_name, port, passport_id, status, service_type
                FROM passport_registry
                WHERE status = 'ACTIVE' AND port IS NOT NULL AND port != '' AND port != 0
            """)
            
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'port': row[1],
                    'passport_id': row[2],
                    'status': row[3],
                    'service_type': row[4] or 'backend',
                    'level': 2
                })
                
            conn.close()
            logger.info(f"🎫 Found {len(services)} Level 2 (ACTIVE) services with valid ports")
            
        except Exception as e:
            logger.error(f"❌ Error reading ACTIVE services: {e}")
            
        return services
    
    def get_registered_services(self) -> List[Dict]:
        """Get Level 3 (REGISTERED) services"""
        services = []
        
        try:
            if not os.path.exists(self.service_db_path):
                logger.warning(f"Service registry not found: {self.service_db_path}")
                return services
                
            conn = sqlite3.connect(self.service_db_path)
            cursor = conn.cursor()
            
            # Get REGISTERED/CERTIFIED services
            cursor.execute("""
                SELECT service_name, port, status, service_type, health_score
                FROM services
                WHERE status = 'REGISTERED' OR status = 'CERTIFIED'
            """)
            
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'port': row[1],
                    'status': row[2],
                    'service_type': row[3] or 'backend',
                    'health_score': row[4] or 100,
                    'level': 3
                })
                
            conn.close()
            logger.info(f"🏆 Found {len(services)} Level 3 (REGISTERED) services")
            
        except Exception as e:
            logger.error(f"❌ Error reading REGISTERED services: {e}")
            
        return services
    
    def get_level_2_3_services(self) -> List[Dict]:
        """Get all Level 2 and 3 services"""
        active_services = self.get_active_services()
        registered_services = self.get_registered_services()
        
        # Combine and deduplicate
        all_services = active_services + registered_services
        unique_services = {}
        
        for service in all_services:
            service_name = service['service_name']
            if service_name not in unique_services:
                unique_services[service_name] = service
            else:
                # Prefer Level 3 over Level 2
                if service.get('level', 2) > unique_services[service_name].get('level', 2):
                    unique_services[service_name] = service
                    
        return list(unique_services.values())
    
    def find_service_mdc_file(self, service_name: str) -> Optional[str]:
        """Find MDC file for a specific service"""
        # Convert service name variations
        mdc_name_variants = [
            f"{service_name}.mdc",
            f"{service_name.replace('-', '_')}.mdc",
            f"{service_name.replace('_', '-')}.mdc",
            f"{service_name.replace('-', '')}.mdc"
        ]
        
        for mdc_path in self.mdc_paths:
            if not os.path.exists(mdc_path):
                continue
                
            for variant in mdc_name_variants:
                mdc_file = os.path.join(mdc_path, variant)
                if os.path.exists(mdc_file):
                    return mdc_file
                    
        return None
    
    def extract_triggers_from_mdc(self, mdc_file_path: str, service_info: Dict) -> List[TriggerDefinition]:
        """Extract trigger definitions from MDC file"""
        triggers = []
        
        try:
            with open(mdc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for trigger patterns in MDC content
            trigger_patterns = [
                r'trigger[s]?:\s*"([^"]+)"',
                r'event:\s*"([^"]+)"',
                r'condition:\s*"([^"]+)"',
                r'action:\s*"([^"]+)"',
                r'frequency:\s*"([^"]+)"'
            ]
            
            # Extract basic trigger information
            service_name = service_info['service_name']
            service_level = service_info.get('level', 2)
            port = service_info.get('port')
            
            # Create default trigger for the service
            trigger = TriggerDefinition(
                name=f"{service_name}_main_trigger",
                source_mdc=os.path.basename(mdc_file_path),
                service_name=service_name,
                service_level=service_level,
                event="service_operation",
                condition=f"service_active AND port_assigned={port}" if port else "service_active",
                action=f"monitor_{service_name}",
                frequency="continuous",
                validation="level_2_3_validation",
                port=port
            )
            
            triggers.append(trigger)
            logger.debug(f"📋 Extracted trigger for {service_name} (Level {service_level})")
            
        except Exception as e:
            logger.error(f"❌ Error extracting triggers from {mdc_file_path}: {e}")
            
        return triggers
    
    def discover_level_2_3_triggers(self) -> Dict[str, TriggerDefinition]:
        """Discover triggers for Level 2 and 3 services only"""
        logger.info("🔍 Discovering triggers for Level 2 (ACTIVE) and Level 3 (REGISTERED) services...")
        
        triggers = {}
        level_2_3_services = self.get_level_2_3_services()
        
        logger.info(f"📊 Processing {len(level_2_3_services)} validated services")
        
        for service_info in level_2_3_services:
            service_name = service_info['service_name']
            service_level = service_info.get('level', 2)
            
            # Find corresponding MDC file
            mdc_file = self.find_service_mdc_file(service_name)
            
            if mdc_file:
                logger.info(f"📄 Processing MDC file for {service_name} (Level {service_level}): {mdc_file}")
                service_triggers = self.extract_triggers_from_mdc(mdc_file, service_info)
                
                for trigger in service_triggers:
                    triggers[trigger.name] = trigger
            else:
                logger.warning(f"⚠️ No MDC file found for Level {service_level} service: {service_name}")
                
        logger.info(f"✅ Discovered {len(triggers)} triggers from {len(level_2_3_services)} Level 2/3 services")
        return triggers
    
    def validate_production_triggers(self) -> Dict[str, bool]:
        """Validate triggers for production readiness"""
        validation_results = {}
        
        for trigger_name, trigger in self.trigger_registry.items():
            is_valid = True
            
            # Validate Level 2/3 service has proper port
            if trigger.service_level == 2 and not trigger.port:
                logger.error(f"❌ Level 2 trigger {trigger_name} missing port - FORBIDDEN")
                is_valid = False
                
            # Validate trigger conditions
            if not trigger.condition or trigger.condition == "":
                logger.warning(f"⚠️ Trigger {trigger_name} has empty condition")
                is_valid = False
                
            # Validate trigger actions
            if not trigger.action or trigger.action == "":
                logger.warning(f"⚠️ Trigger {trigger_name} has empty action")
                is_valid = False
                
            validation_results[trigger_name] = is_valid
            
        valid_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        logger.info(f"✅ Validation complete: {valid_count}/{total_count} triggers are valid")
        return validation_results
    
    def sync_level_2_3_triggers(self) -> bool:
        """Synchronize triggers for Level 2 and 3 services"""
        try:
            logger.info("🔄 Starting Level 2/3 trigger synchronization...")
            
            # Discover current triggers
            new_triggers = self.discover_level_2_3_triggers()
            
            # Update trigger registry
            self.trigger_registry = new_triggers
            
            # Validate triggers
            validation_results = self.validate_production_triggers()
            
            # Update sync time
            self.last_sync_time = datetime.now()
            
            logger.info(f"✅ Trigger synchronization complete: {len(new_triggers)} triggers synced")
            return True
            
        except Exception as e:
            logger.error(f"❌ Trigger synchronization failed: {e}")
            return False
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="ZmartBot Trigger Manager",
            description="Level 2 & 3 Service Trigger Management System",
            version="1.0.0"
        )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "trigger_manager",
                "timestamp": datetime.now().isoformat(),
                "level_2_3_only": self.level_2_3_services_only,
                "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None
            }
        
        @app.get("/api/triggers/list")
        async def list_triggers():
            """Get all Level 2/3 service triggers"""
            triggers_data = []
            
            for trigger_name, trigger in self.trigger_registry.items():
                triggers_data.append({
                    "name": trigger.name,
                    "service_name": trigger.service_name,
                    "service_level": trigger.service_level,
                    "source_mdc": trigger.source_mdc,
                    "event": trigger.event,
                    "condition": trigger.condition,
                    "action": trigger.action,
                    "frequency": trigger.frequency,
                    "port": trigger.port,
                    "last_executed": trigger.last_executed.isoformat() if trigger.last_executed else None,
                    "execution_count": trigger.execution_count,
                    "success_rate": trigger.success_rate
                })
                
            return {
                "triggers": triggers_data,
                "total_count": len(triggers_data),
                "level_2_count": len([t for t in triggers_data if t["service_level"] == 2]),
                "level_3_count": len([t for t in triggers_data if t["service_level"] == 3]),
                "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None
            }
        
        @app.get("/api/triggers/services")
        async def list_level_2_3_services():
            """Get all Level 2 and 3 services"""
            services = self.get_level_2_3_services()
            
            return {
                "services": services,
                "total_count": len(services),
                "level_2_count": len([s for s in services if s.get("level") == 2]),
                "level_3_count": len([s for s in services if s.get("level") == 3])
            }
        
        @app.post("/api/triggers/sync")
        async def sync_triggers():
            """Force trigger synchronization"""
            success = self.sync_level_2_3_triggers()
            
            if success:
                return {
                    "status": "success",
                    "message": "Level 2/3 triggers synchronized successfully",
                    "trigger_count": len(self.trigger_registry),
                    "sync_time": self.last_sync_time.isoformat()
                }
            else:
                raise HTTPException(status_code=500, detail="Trigger synchronization failed")
        
        @app.post("/api/triggers/validate")
        async def validate_triggers():
            """Validate all triggers"""
            validation_results = self.validate_production_triggers()
            valid_count = sum(validation_results.values())
            total_count = len(validation_results)
            
            return {
                "validation_results": validation_results,
                "valid_count": valid_count,
                "total_count": total_count,
                "validation_percentage": (valid_count / total_count * 100) if total_count > 0 else 100
            }
        
        return app
    
    def setup_bi_daily_schedule(self):
        """Setup bi-daily trigger synchronization"""
        # Morning sync at 6:00 AM
        schedule.every().day.at("06:00").do(self.morning_sync)
        
        # Evening sync at 6:00 PM  
        schedule.every().day.at("18:00").do(self.evening_sync)
        
        logger.info("📅 Bi-daily trigger sync schedule configured (6:00 AM & 6:00 PM)")
    
    def morning_sync(self):
        """Morning trigger synchronization"""
        logger.info("🌅 Starting morning trigger sync...")
        success = self.sync_level_2_3_triggers()
        
        if success:
            logger.info("✅ Morning sync completed successfully")
        else:
            logger.error("❌ Morning sync failed")
    
    def evening_sync(self):
        """Evening trigger synchronization"""
        logger.info("🌆 Starting evening trigger sync...")
        success = self.sync_level_2_3_triggers()
        
        if success:
            # Generate daily report
            level_2_count = len([t for t in self.trigger_registry.values() if t.service_level == 2])
            level_3_count = len([t for t in self.trigger_registry.values() if t.service_level == 3])
            
            logger.info(f"✅ Evening sync completed: {level_2_count} Level 2 triggers, {level_3_count} Level 3 triggers")
        else:
            logger.error("❌ Evening sync failed")
    
    def run_scheduler(self):
        """Run the trigger scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def run_api_server(self):
        """Run the FastAPI server"""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the Trigger Manager"""
        logger.info(f"🚀 Starting ZmartBot Trigger Manager on port {self.port}")
        logger.info("🎯 LEVEL 2 & 3 SERVICES ONLY - Discovery services excluded")
        
        # Initial sync
        self.sync_level_2_3_triggers()
        
        # Setup bi-daily schedule
        self.setup_bi_daily_schedule()
        
        # Start scheduler in background
        import threading
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Run API server
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="info"
        )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Trigger Manager")
    parser.add_argument("--port", type=int, default=8890, help="API server port")
    parser.add_argument("--sync", action="store_true", help="Force trigger sync and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    trigger_manager = TriggerManager(port=args.port)
    
    if args.sync:
        success = trigger_manager.sync_level_2_3_triggers()
        sys.exit(0 if success else 1)
    else:
        trigger_manager.run()