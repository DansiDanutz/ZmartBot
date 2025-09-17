#!/usr/bin/env python3
"""
ZmartBot Status Manager - MDC File Status Management System
Scans all MDC files twice daily and updates their status based on service level:
Discovery files = Level 1, ACTIVE files = Level 2, Certified files = Level 3
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
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('status_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MDCFileInfo:
    """MDC file information structure"""
    file_path: str
    service_name: str
    current_status: str
    correct_status: str
    service_level: int
    port: Optional[int]
    requires_update: bool

@dataclass
class StatusStats:
    """Status distribution statistics"""
    total_mdc_files: int
    discovery_status_count: int
    active_status_count: int
    certified_status_count: int
    unknown_status_count: int
    updates_needed: int
    last_scan_time: Optional[datetime] = None

class StatusManager:
    """MDC File Status Management System"""
    
    def __init__(self, port: int = 8892):
        self.port = port
        self.app = self.create_app()
        
        # Database paths
        self.discovery_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
        self.passport_db_path = "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"
        self.service_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/service_registry.db"
        
        # MDC file paths
        self.mdc_paths = [
            "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/rules/",
            "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/"
        ]
        
        # Level Manager integration
        self.level_manager_api = "http://127.0.0.1:8891"
        
        # Statistics
        self.status_stats = StatusStats(0, 0, 0, 0, 0, 0)
        self.last_scan_time = None
        self.status_changes = []
        
    def discover_mdc_files(self) -> List[str]:
        """Discover all MDC files in the system"""
        mdc_files = []
        
        for mdc_path in self.mdc_paths:
            if os.path.exists(mdc_path):
                pattern = os.path.join(mdc_path, "*.mdc")
                found_files = glob.glob(pattern)
                mdc_files.extend(found_files)
                
        logger.info(f"📁 Discovered {len(mdc_files)} MDC files")
        return mdc_files
    
    def extract_service_name_from_mdc(self, mdc_file_path: str) -> str:
        """Extract service name from MDC file"""
        filename = os.path.basename(mdc_file_path)
        service_name = filename.replace('.mdc', '')
        
        # Handle common naming patterns
        if service_name.startswith('mdc-'):
            service_name = service_name[4:]
        if service_name.endswith('-mdc'):
            service_name = service_name[:-4]
            
        return service_name
    
    def get_current_mdc_status(self, mdc_file_path: str) -> str:
        """Extract current status from MDC file header"""
        try:
            with open(mdc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for status in the header line (usually line 2)
            lines = content.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                if line.startswith('>') and 'Status:' in line:
                    if 'Status: Certified' in line:
                        return 'Certified'
                    elif 'Status: ACTIVE' in line:
                        return 'ACTIVE'
                    elif 'Status: Discovery' in line:
                        return 'Discovery'
                    # Check for other status patterns
                    status_match = re.search(r'Status:\s*([A-Za-z]+)', line)
                    if status_match:
                        return status_match.group(1)
            
            return 'Unknown'
            
        except Exception as e:
            logger.error(f"Error reading MDC status from {mdc_file_path}: {e}")
            return 'Unknown'
    
    def get_service_level_from_databases(self, service_name: str) -> Tuple[int, Optional[int]]:
        """Get service level and port from databases"""
        # Check Level 3 (Certified) first
        try:
            if os.path.exists(self.service_db_path):
                conn = sqlite3.connect(self.service_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT port FROM services WHERE service_name = ? AND (status = 'REGISTERED' OR status = 'CERTIFIED')", (service_name,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return 3, result[0]  # Level 3, port
        except Exception as e:
            logger.debug(f"Error checking service registry for {service_name}: {e}")
        
        # Check Level 2 (ACTIVE)
        try:
            if os.path.exists(self.passport_db_path):
                conn = sqlite3.connect(self.passport_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT port FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE' AND port IS NOT NULL AND port != '' AND port != 0", (service_name,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return 2, result[0]  # Level 2, port
        except Exception as e:
            logger.debug(f"Error checking passport registry for {service_name}: {e}")
        
        # Check Level 1 (Discovery)
        try:
            if os.path.exists(self.discovery_db_path):
                conn = sqlite3.connect(self.discovery_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0] > 0:
                    return 1, None  # Level 1, no port
        except Exception as e:
            logger.debug(f"Error checking discovery registry for {service_name}: {e}")
        
        return 0, None  # Not found in any database
    
    def determine_correct_status(self, service_level: int) -> str:
        """Determine correct MDC status based on service level"""
        if service_level == 3:
            return 'Certified'
        elif service_level == 2:
            return 'ACTIVE'
        elif service_level == 1:
            return 'Discovery'
        else:
            return 'Unknown'
    
    def extract_mdc_metadata(self, mdc_file_path: str) -> Dict[str, str]:
        """Extract metadata from MDC file header"""
        metadata = {
            'type': 'service',
            'version': '1.0.0',
            'owner': 'zmartbot'
        }
        
        try:
            with open(mdc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                if line.startswith('>'):
                    # Extract Type
                    type_match = re.search(r'Type:\s*([^|]+)', line)
                    if type_match:
                        metadata['type'] = type_match.group(1).strip()
                    
                    # Extract Version
                    version_match = re.search(r'Version:\s*([^|]+)', line)
                    if version_match:
                        metadata['version'] = version_match.group(1).strip()
                    
                    # Extract Owner
                    owner_match = re.search(r'Owner:\s*([^|]+)', line)
                    if owner_match:
                        metadata['owner'] = owner_match.group(1).strip()
                    
                    break
        except Exception as e:
            logger.debug(f"Error extracting metadata from {mdc_file_path}: {e}")
        
        return metadata
    
    def update_mdc_status(self, mdc_file_path: str, new_status: str, service_level: int, port: Optional[int] = None) -> bool:
        """Update MDC file header with correct status"""
        try:
            # Read current content
            with open(mdc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Extract current metadata
            metadata = self.extract_mdc_metadata(mdc_file_path)
            
            # Generate new header based on status
            if new_status == 'Discovery':
                new_header = f"# {os.path.basename(mdc_file_path).replace('.mdc', '')}.mdc\n> Type: {metadata['type']} | Version: {metadata['version']} | Owner: {metadata['owner']} | Status: Discovery | Level: 1"
            elif new_status == 'ACTIVE' and port:
                new_header = f"# {os.path.basename(mdc_file_path).replace('.mdc', '')}.mdc\n> Type: {metadata['type']} | Version: {metadata['version']} | Owner: {metadata['owner']} | Status: ACTIVE | Level: 2 | Port: {port}"
            elif new_status == 'Certified' and port:
                new_header = f"# {os.path.basename(mdc_file_path).replace('.mdc', '')}.mdc\n> Type: {metadata['type']} | Version: {metadata['version']} | Owner: {metadata['owner']} | Status: Certified | Level: 3 | Port: {port}"
            else:
                # Fallback header
                new_header = f"# {os.path.basename(mdc_file_path).replace('.mdc', '')}.mdc\n> Type: {metadata['type']} | Version: {metadata['version']} | Owner: {metadata['owner']} | Status: {new_status}"
            
            # Find and replace the header lines (first two lines)
            if len(lines) >= 2:
                lines[0] = new_header.split('\n')[0]  # Title line
                lines[1] = new_header.split('\n')[1]  # Header line
            else:
                # Insert header at the beginning
                lines = new_header.split('\n') + lines
            
            # Write updated content
            updated_content = '\n'.join(lines)
            
            # Create backup before updating
            backup_path = mdc_file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated file
            with open(mdc_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Updated {os.path.basename(mdc_file_path)} status: {new_status} (Level {service_level})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating MDC status for {mdc_file_path}: {e}")
            return False
    
    def scan_all_mdc_files(self) -> Dict:
        """Scan all MDC files and update their status"""
        logger.info("🚀 Starting comprehensive MDC status scan...")
        
        start_time = datetime.now()
        
        # Discover all MDC files
        mdc_files = self.discover_mdc_files()
        
        # Process each MDC file
        mdc_infos = []
        status_updates = []
        
        for mdc_file_path in mdc_files:
            service_name = self.extract_service_name_from_mdc(mdc_file_path)
            current_status = self.get_current_mdc_status(mdc_file_path)
            service_level, port = self.get_service_level_from_databases(service_name)
            correct_status = self.determine_correct_status(service_level)
            
            mdc_info = MDCFileInfo(
                file_path=mdc_file_path,
                service_name=service_name,
                current_status=current_status,
                correct_status=correct_status,
                service_level=service_level,
                port=port,
                requires_update=(current_status != correct_status and correct_status != 'Unknown')
            )
            
            mdc_infos.append(mdc_info)
            
            # Update if needed
            if mdc_info.requires_update:
                success = self.update_mdc_status(mdc_file_path, correct_status, service_level, port)
                if success:
                    status_updates.append({
                        'service_name': service_name,
                        'mdc_file': os.path.basename(mdc_file_path),
                        'old_status': current_status,
                        'new_status': correct_status,
                        'level': service_level,
                        'port': port
                    })
        
        # Calculate statistics
        discovery_count = len([m for m in mdc_infos if m.correct_status == 'Discovery'])
        active_count = len([m for m in mdc_infos if m.correct_status == 'ACTIVE'])
        certified_count = len([m for m in mdc_infos if m.correct_status == 'Certified'])
        unknown_count = len([m for m in mdc_infos if m.correct_status == 'Unknown'])
        updates_needed = len([m for m in mdc_infos if m.requires_update])
        
        # Update statistics
        self.status_stats = StatusStats(
            total_mdc_files=len(mdc_infos),
            discovery_status_count=discovery_count,
            active_status_count=active_count,
            certified_status_count=certified_count,
            unknown_status_count=unknown_count,
            updates_needed=updates_needed,
            last_scan_time=datetime.now()
        )
        
        self.last_scan_time = datetime.now()
        self.status_changes = status_updates
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ MDC status scan complete in {duration:.2f}s")
        logger.info(f"📊 Distribution: {discovery_count} Discovery | {active_count} ACTIVE | {certified_count} Certified | {unknown_count} Unknown")
        logger.info(f"🔄 Updates applied: {len(status_updates)} MDC files updated")
        
        return {
            "scan_time": self.last_scan_time.isoformat(),
            "duration_seconds": duration,
            "total_mdc_files": len(mdc_infos),
            "status_distribution": {
                "discovery": discovery_count,
                "active": active_count,
                "certified": certified_count,
                "unknown": unknown_count
            },
            "updates_applied": len(status_updates),
            "status_changes": status_updates
        }
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="ZmartBot Status Manager",
            description="MDC File Status Management System",
            version="1.0.0"
        )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "status_manager",
                "timestamp": datetime.now().isoformat(),
                "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "total_mdc_files": self.status_stats.total_mdc_files
            }
        
        @app.get("/api/status/scan")
        async def get_scan_results():
            """Get current status scan results"""
            if not self.last_scan_time:
                # Perform initial scan
                self.scan_all_mdc_files()
            
            return {
                "scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "statistics": asdict(self.status_stats),
                "recent_changes": self.status_changes[-20:] if self.status_changes else []  # Last 20 changes
            }
        
        @app.post("/api/status/update")
        async def force_status_update():
            """Force status update for all MDC files"""
            results = self.scan_all_mdc_files()
            
            return {
                "status": "success",
                "message": "MDC status scan and update completed",
                "results": results
            }
        
        @app.get("/api/status/stats")
        async def get_status_stats():
            """Get status distribution statistics"""
            return {
                "statistics": asdict(self.status_stats),
                "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "scan_schedule": "6:00 AM & 6:00 PM daily"
            }
        
        @app.get("/api/status/level/{level}")
        async def get_mdc_files_by_level(level: int):
            """Get all MDC files by status level"""
            level_status_map = {1: 'Discovery', 2: 'ACTIVE', 3: 'Certified'}
            target_status = level_status_map.get(level, 'Unknown')
            
            matching_changes = [
                change for change in self.status_changes 
                if change['level'] == level
            ]
            
            return {
                "level": level,
                "status": target_status,
                "mdc_files": matching_changes,
                "count": len(matching_changes)
            }
        
        return app
    
    def setup_bi_daily_schedule(self):
        """Setup bi-daily status scanning"""
        # Morning scan at 6:00 AM
        schedule.every().day.at("06:00").do(self.morning_scan)
        
        # Evening scan at 6:00 PM
        schedule.every().day.at("18:00").do(self.evening_scan)
        
        logger.info("📅 Bi-daily MDC status scan schedule configured (6:00 AM & 6:00 PM)")
    
    def morning_scan(self):
        """Morning status scan"""
        logger.info("🌅 Starting morning MDC status scan...")
        results = self.scan_all_mdc_files()
        logger.info("✅ Morning scan completed")
    
    def evening_scan(self):
        """Evening status scan"""
        logger.info("🌆 Starting evening MDC status scan...")
        results = self.scan_all_mdc_files()
        
        # Generate daily summary
        logger.info(f"📊 Daily MDC Status Summary:")
        logger.info(f"   Total MDC Files: {self.status_stats.total_mdc_files}")
        logger.info(f"   Discovery Status: {self.status_stats.discovery_status_count}")
        logger.info(f"   ACTIVE Status: {self.status_stats.active_status_count}")
        logger.info(f"   Certified Status: {self.status_stats.certified_status_count}")
        logger.info(f"   Updates Today: {len(self.status_changes)}")
        
        logger.info("✅ Evening scan completed")
    
    def run_scheduler(self):
        """Run the status scanning scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run(self):
        """Run the Status Manager"""
        logger.info(f"🚀 Starting ZmartBot Status Manager on port {self.port}")
        logger.info("📄 MDC File Status Management System")
        
        # Initial scan
        self.scan_all_mdc_files()
        
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
    
    parser = argparse.ArgumentParser(description="ZmartBot Status Manager")
    parser.add_argument("--port", type=int, default=8892, help="API server port")
    parser.add_argument("--scan", action="store_true", help="Force status scan and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    status_manager = StatusManager(port=args.port)
    
    if args.scan:
        results = status_manager.scan_all_mdc_files()
        print(json.dumps(results, indent=2))
        sys.exit(0)
    else:
        status_manager.run()