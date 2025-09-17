#!/usr/bin/env python3
"""
ZmartBot Level Manager - Service Level Classification System
Scans all services twice daily and assigns correct levels based on 3-Database Service Lifecycle Architecture
Discovery (Level 1) → Active (Level 2) → Registered (Level 3)
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
import schedule
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('level_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """Service information structure"""
    name: str
    py_file: Optional[str]
    mdc_file: Optional[str]
    current_level: int
    correct_level: int
    port: Optional[int]
    passport_id: Optional[str]
    status: str
    database: str
    requires_update: bool = False

@dataclass
class LevelStats:
    """Level distribution statistics"""
    total_services: int
    level_1_count: int  # Discovery
    level_2_count: int  # Active
    level_3_count: int  # Registered
    promotions: int
    demotions: int
    violations: int

class LevelManager:
    """Service Level Classification and Management System"""
    
    def __init__(self, port: int = 8891):
        self.port = port
        self.app = self.create_app()
        
        # Database paths
        self.discovery_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
        self.passport_db_path = "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"
        self.service_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/service_registry.db"
        
        # File system paths
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.mdc_paths = [
            "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/rules/",
            "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/"
        ]
        
        # Statistics
        self.level_stats = LevelStats(0, 0, 0, 0, 0, 0, 0)
        self.last_scan_time = None
        self.level_changes = []
        
    def find_python_files(self) -> List[str]:
        """Find all Python service files"""
        py_files = []
        
        # Scan main directory
        pattern = os.path.join(self.base_path, "*.py")
        py_files.extend(glob.glob(pattern))
        
        # Scan subdirectories for service files
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    if any(keyword in file.lower() for keyword in ['service', 'agent', 'manager', 'server']):
                        py_files.append(os.path.join(root, file))
        
        return py_files
    
    def extract_service_name(self, py_file_path: str) -> str:
        """Extract service name from Python file path"""
        filename = os.path.basename(py_file_path)
        # Remove .py extension
        service_name = filename.replace('.py', '')
        
        # Clean up common suffixes
        suffixes_to_remove = ['_service', '_agent', '_manager', '_server']
        for suffix in suffixes_to_remove:
            if service_name.endswith(suffix):
                service_name = service_name[:-len(suffix)]
                break
                
        return service_name
    
    def find_corresponding_mdc(self, service_name: str) -> Optional[str]:
        """Find corresponding MDC file for a service"""
        # Try different naming conventions
        mdc_name_variants = [
            f"{service_name}.mdc",
            f"{service_name.replace('-', '_')}.mdc",
            f"{service_name.replace('_', '-')}.mdc",
            f"{service_name}Service.mdc",
            f"{service_name}Agent.mdc",
            f"{service_name}Manager.mdc"
        ]
        
        for mdc_path in self.mdc_paths:
            if not os.path.exists(mdc_path):
                continue
                
            for variant in mdc_name_variants:
                mdc_file = os.path.join(mdc_path, variant)
                if os.path.exists(mdc_file):
                    return mdc_file
                    
        return None
    
    def get_service_from_discovery_db(self, service_name: str) -> Optional[Dict]:
        """Get service info from discovery database"""
        try:
            if not os.path.exists(self.discovery_db_path):
                return None
                
            conn = sqlite3.connect(self.discovery_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, status, registered_at, description
                FROM discovery_services
                WHERE service_name = ?
            """, (service_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'service_name': row[0],
                    'status': row[1],
                    'registered_at': row[2],
                    'description': row[3],
                    'database': 'discovery_registry.db',
                    'level': 1
                }
                
        except Exception as e:
            logger.error(f"Error reading discovery database: {e}")
            
        return None
    
    def get_service_from_passport_db(self, service_name: str) -> Optional[Dict]:
        """Get service info from passport database"""
        try:
            if not os.path.exists(self.passport_db_path):
                return None
                
            conn = sqlite3.connect(self.passport_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, passport_id, status, service_type
                FROM passport_registry
                WHERE service_name = ?
            """, (service_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'service_name': row[0],
                    'port': row[1],
                    'passport_id': row[2],
                    'status': row[3],
                    'service_type': row[4],
                    'database': 'passport_registry.db',
                    'level': 2
                }
                
        except Exception as e:
            logger.error(f"Error reading passport database: {e}")
            
        return None
    
    def get_service_from_service_db(self, service_name: str) -> Optional[Dict]:
        """Get service info from service registry database"""
        try:
            if not os.path.exists(self.service_db_path):
                return None
                
            conn = sqlite3.connect(self.service_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, status, service_type, health_score
                FROM services
                WHERE service_name = ?
            """, (service_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'service_name': row[0],
                    'port': row[1],
                    'status': row[2],
                    'service_type': row[3],
                    'health_score': row[4],
                    'database': 'service_registry.db',
                    'level': 3
                }
                
        except Exception as e:
            logger.error(f"Error reading service registry database: {e}")
            
        return None
    
    def get_current_service_level(self, service_name: str) -> Tuple[int, Dict]:
        """Get current service level and database info"""
        # Check Level 3 first (highest priority)
        service_info = self.get_service_from_service_db(service_name)
        if service_info:
            return 3, service_info
            
        # Check Level 2
        service_info = self.get_service_from_passport_db(service_name)
        if service_info:
            return 2, service_info
            
        # Check Level 1
        service_info = self.get_service_from_discovery_db(service_name)
        if service_info:
            return 1, service_info
            
        # Not found in any database
        return 0, {}
    
    def classify_service_level(self, service_name: str, py_file: str, mdc_file: Optional[str]) -> int:
        """
        Classify correct service level based on current implementation
        Returns: 1 (Discovery), 2 (Active), 3 (Registered), 0 (Invalid)
        """
        
        # Both .py and .mdc files must exist
        if not mdc_file or not os.path.exists(py_file):
            return 0  # Invalid service
        
        # Check Level 3 (Registered) - Highest priority
        service_3_info = self.get_service_from_service_db(service_name)
        if service_3_info:
            # Must have port and be certified
            if service_3_info.get('port') and service_3_info.get('status') in ['REGISTERED', 'CERTIFIED']:
                return 3  # LEVEL 3: REGISTERED
        
        # Check Level 2 (Active) - Must have port
        service_2_info = self.get_service_from_passport_db(service_name)
        if service_2_info:
            port = service_2_info.get('port')
            passport_id = service_2_info.get('passport_id')
            
            # CRITICAL: ACTIVE service MUST have port
            if port and port > 0 and passport_id:
                return 2  # LEVEL 2: ACTIVE
            else:
                # VIOLATION: ACTIVE without port - must be demoted
                logger.warning(f"🚨 VIOLATION: {service_name} is ACTIVE without valid port - will be demoted")
                return 1  # Will be demoted to Discovery
        
        # Default to Level 1 (Discovery)
        return 1  # LEVEL 1: DISCOVERY
    
    def discover_all_services(self) -> List[ServiceInfo]:
        """Discover all services with .py and .mdc files and classify levels"""
        services = []
        
        logger.info("🔍 Discovering all services...")
        
        py_files = self.find_python_files()
        logger.info(f"📁 Found {len(py_files)} Python files")
        
        for py_file in py_files:
            service_name = self.extract_service_name(py_file)
            mdc_file = self.find_corresponding_mdc(service_name)
            
            if mdc_file:
                # Get current level from databases
                current_level, current_info = self.get_current_service_level(service_name)
                
                # Classify correct level
                correct_level = self.classify_service_level(service_name, py_file, mdc_file)
                
                if correct_level > 0:  # Valid service
                    service_info = ServiceInfo(
                        name=service_name,
                        py_file=py_file,
                        mdc_file=mdc_file,
                        current_level=current_level,
                        correct_level=correct_level,
                        port=current_info.get('port'),
                        passport_id=current_info.get('passport_id'),
                        status=current_info.get('status', 'UNKNOWN'),
                        database=current_info.get('database', 'none'),
                        requires_update=(current_level != correct_level)
                    )
                    
                    services.append(service_info)
                    
                    if service_info.requires_update:
                        logger.info(f"📊 {service_name}: Level {current_level} → {correct_level} (UPDATE NEEDED)")
                else:
                    logger.debug(f"⚠️ Invalid service: {service_name} (missing files)")
            else:
                logger.debug(f"📄 No MDC file found for: {service_name}")
        
        logger.info(f"✅ Discovered {len(services)} valid services")
        return services
    
    def validate_level_2_ports(self) -> List[str]:
        """Validate that ALL Level 2 (ACTIVE) services have ports"""
        violations = []
        
        try:
            if not os.path.exists(self.passport_db_path):
                return violations
                
            conn = sqlite3.connect(self.passport_db_path)
            cursor = conn.cursor()
            
            # Find ACTIVE services without valid ports
            cursor.execute("""
                SELECT service_name, port, passport_id
                FROM passport_registry
                WHERE status = 'ACTIVE' AND (port IS NULL OR port = '' OR port = 0)
            """)
            
            invalid_services = cursor.fetchall()
            conn.close()
            
            for service_name, port, passport_id in invalid_services:
                violations.append(service_name)
                logger.error(f"🚨 CRITICAL VIOLATION: {service_name} is ACTIVE without valid port (port: {port})")
                
                # Demote to Discovery immediately
                self.demote_to_discovery(service_name, "FORBIDDEN_ACTIVE_WITHOUT_PORT")
                
        except Exception as e:
            logger.error(f"❌ Error validating Level 2 ports: {e}")
            
        return violations
    
    def demote_to_discovery(self, service_name: str, reason: str):
        """Demote service to Discovery level"""
        try:
            # Remove from passport registry
            if os.path.exists(self.passport_db_path):
                conn = sqlite3.connect(self.passport_db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM passport_registry WHERE service_name = ?", (service_name,))
                conn.commit()
                conn.close()
                
            # Add to discovery registry if not already there
            if os.path.exists(self.discovery_db_path):
                conn = sqlite3.connect(self.discovery_db_path)
                cursor = conn.cursor()
                
                # Check if already exists
                cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    cursor.execute("""
                        INSERT INTO discovery_services (service_name, status, registered_at, description)
                        VALUES (?, 'DISCOVERED', datetime('now'), ?)
                    """, (service_name, f"Demoted due to: {reason}"))
                    conn.commit()
                    
                conn.close()
                
            logger.warning(f"📉 DEMOTED: {service_name} to Discovery level - Reason: {reason}")
            
        except Exception as e:
            logger.error(f"❌ Error demoting {service_name} to Discovery: {e}")
    
    def scan_all_services(self) -> Dict:
        """Scan all services and update levels"""
        logger.info("🚀 Starting comprehensive service level scan...")
        
        start_time = datetime.now()
        
        # Discover all services
        services = self.discover_all_services()
        
        # Validate Level 2 ports (critical)
        port_violations = self.validate_level_2_ports()
        
        # Count services by level
        level_1_count = len([s for s in services if s.correct_level == 1])
        level_2_count = len([s for s in services if s.correct_level == 2])
        level_3_count = len([s for s in services if s.correct_level == 3])
        
        # Count changes needed
        services_needing_updates = [s for s in services if s.requires_update]
        promotions = len([s for s in services_needing_updates if s.correct_level > s.current_level])
        demotions = len([s for s in services_needing_updates if s.correct_level < s.current_level])
        
        # Update statistics
        self.level_stats = LevelStats(
            total_services=len(services),
            level_1_count=level_1_count,
            level_2_count=level_2_count,
            level_3_count=level_3_count,
            promotions=promotions,
            demotions=demotions + len(port_violations),
            violations=len(port_violations)
        )
        
        # Update scan time
        self.last_scan_time = datetime.now()
        
        # Store services needing updates for API access
        self.level_changes = [
            {
                'service_name': s.name,
                'current_level': s.current_level,
                'correct_level': s.correct_level,
                'port': s.port,
                'status': s.status,
                'database': s.database,
                'requires_update': s.requires_update
            }
            for s in services
        ]
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Service level scan complete in {duration:.2f}s")
        logger.info(f"📊 Distribution: {level_1_count} Discovery | {level_2_count} Active | {level_3_count} Registered")
        logger.info(f"🔄 Changes needed: {promotions} promotions, {demotions} demotions")
        logger.info(f"🚨 Violations: {len(port_violations)} ACTIVE services without ports")
        
        return {
            "scan_time": self.last_scan_time.isoformat(),
            "duration_seconds": duration,
            "total_services": len(services),
            "level_distribution": {
                "level_1_discovery": level_1_count,
                "level_2_active": level_2_count,
                "level_3_registered": level_3_count
            },
            "changes_needed": {
                "promotions": promotions,
                "demotions": demotions,
                "port_violations": len(port_violations)
            },
            "services_needing_updates": len(services_needing_updates),
            "port_violations": port_violations
        }
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="ZmartBot Level Manager",
            description="Service Level Classification System - 3-Database Service Lifecycle",
            version="1.0.0"
        )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "level_manager",
                "timestamp": datetime.now().isoformat(),
                "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "total_services": self.level_stats.total_services
            }
        
        @app.get("/api/levels/scan")
        async def get_scan_results():
            """Get current level scan results"""
            if not self.last_scan_time:
                # Perform initial scan
                self.scan_all_services()
                
            return {
                "scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "statistics": asdict(self.level_stats),
                "services_by_level": {
                    "level_1_discovery": [s for s in self.level_changes if s['correct_level'] == 1],
                    "level_2_active": [s for s in self.level_changes if s['correct_level'] == 2],
                    "level_3_registered": [s for s in self.level_changes if s['correct_level'] == 3]
                }
            }
        
        @app.post("/api/levels/update")
        async def force_level_update():
            """Force level update for all services"""
            results = self.scan_all_services()
            
            return {
                "status": "success",
                "message": "Level scan and update completed",
                "results": results
            }
        
        @app.get("/api/levels/service/{service_name}")
        async def get_service_level(service_name: str):
            """Get level for specific service"""
            current_level, current_info = self.get_current_service_level(service_name)
            
            # Find service in scan results
            service_data = None
            for service in self.level_changes:
                if service['service_name'] == service_name:
                    service_data = service
                    break
            
            if not service_data:
                raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
            
            return {
                "service_name": service_name,
                "current_level": current_level,
                "correct_level": service_data['correct_level'],
                "requires_update": service_data['requires_update'],
                "database_info": current_info,
                "level_description": {
                    1: "Discovery - .py + .mdc files exist",
                    2: "Active - Port assigned, passport issued",
                    3: "Registered - Fully certified"
                }.get(service_data['correct_level'], "Unknown")
            }
        
        @app.get("/api/levels/stats")
        async def get_level_stats():
            """Get level distribution statistics"""
            return {
                "statistics": asdict(self.level_stats),
                "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "scan_schedule": "6:00 AM & 6:00 PM daily"
            }
        
        return app
    
    def setup_bi_daily_schedule(self):
        """Setup bi-daily level scanning"""
        # Morning scan at 6:00 AM
        schedule.every().day.at("06:00").do(self.morning_scan)
        
        # Evening scan at 6:00 PM
        schedule.every().day.at("18:00").do(self.evening_scan)
        
        logger.info("📅 Bi-daily level scan schedule configured (6:00 AM & 6:00 PM)")
    
    def morning_scan(self):
        """Morning level scan"""
        logger.info("🌅 Starting morning level scan...")
        results = self.scan_all_services()
        logger.info("✅ Morning scan completed")
    
    def evening_scan(self):
        """Evening level scan"""
        logger.info("🌆 Starting evening level scan...")
        results = self.scan_all_services()
        
        # Generate daily summary
        logger.info(f"📊 Daily Summary - Total: {self.level_stats.total_services} services")
        logger.info(f"   Level 1 (Discovery): {self.level_stats.level_1_count}")
        logger.info(f"   Level 2 (Active): {self.level_stats.level_2_count}")  
        logger.info(f"   Level 3 (Registered): {self.level_stats.level_3_count}")
        logger.info(f"   Promotions: {self.level_stats.promotions}")
        logger.info(f"   Demotions: {self.level_stats.demotions}")
        logger.info(f"   Violations: {self.level_stats.violations}")
        
        logger.info("✅ Evening scan completed")
    
    def run_scheduler(self):
        """Run the level scanning scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run(self):
        """Run the Level Manager"""
        logger.info(f"🚀 Starting ZmartBot Level Manager on port {self.port}")
        logger.info("📊 3-Database Service Lifecycle Management System")
        
        # Initial scan
        self.scan_all_services()
        
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
    
    parser = argparse.ArgumentParser(description="ZmartBot Level Manager")
    parser.add_argument("--port", type=int, default=8891, help="API server port")
    parser.add_argument("--scan", action="store_true", help="Force level scan and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    level_manager = LevelManager(port=args.port)
    
    if args.scan:
        results = level_manager.scan_all_services()
        print(json.dumps(results, indent=2))
        sys.exit(0)
    else:
        level_manager.run()