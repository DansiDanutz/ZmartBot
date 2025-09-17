#!/usr/bin/env python3
"""
SnapshotService - FastAPI Server
CRITICAL disaster recovery service providing comprehensive system state snapshots
"""

import asyncio
import logging
import sys
import os
import time
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import threading
import sqlite3
import zipfile
import tempfile

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the existing snapshot service
try:
    from services.snapshot_service import SnapshotService
except ImportError:
    # Fallback if import fails
    SnapshotService = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="SnapshotService",
    description="CRITICAL disaster recovery service providing comprehensive system state snapshots, automated backup scheduling, and complete restoration capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
service_start_time = time.time()
snapshot_service = None
snapshot_active = True
scheduler_thread = None

# Snapshot configuration
SNAPSHOT_CONFIG = {
    'storage_path': str(project_root / 'system_backups'),
    'max_snapshots': 100,
    'retention_days': 90,
    'compression_level': 6,
    'automatic_cleanup': True,
    'parallel_processing': True,
    'max_workers': 4,
    
    'schedules': {
        'full_snapshot': '0 2 * * *',      # Daily at 2 AM
        'incremental': '0 */2 * * *',       # Every 2 hours
        'differential': '0 8,16 * * *',     # 8 AM and 4 PM
        'cleanup': '0 3 * * 0'              # Weekly cleanup
    },
    
    'components': {
        'include_services': True,
        'include_databases': True,
        'include_configuration': True,
        'include_logs': False,
        'include_temp_files': False
    },
    
    'thresholds': {
        'max_file_size_mb': 1000,
        'max_snapshot_size_gb': 10,
        'warning_disk_usage_percent': 80,
        'critical_disk_usage_percent': 90
    }
}

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    service: str
    version: str
    snapshot_active: bool

class SnapshotRequest(BaseModel):
    name: str
    description: Optional[str] = None
    snapshot_type: str = "full"  # full, incremental, differential
    components: Optional[List[str]] = None

class SnapshotResponse(BaseModel):
    snapshot_id: str
    name: str
    timestamp: str
    snapshot_type: str
    size_bytes: int
    file_count: int
    status: str

class RestorationRequest(BaseModel):
    snapshot_id: str
    target_path: Optional[str] = None
    components: Optional[List[str]] = None
    emergency: bool = False

class SystemProtectionRequest(BaseModel):
    service_name: str
    protected_files: List[str]
    protected_ports: List[int]
    backup_required: bool = True
    integrity_checks: List[str] = []

class SnapshotEngine:
    """Snapshot engine implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = Path(config['storage_path'])
        self.storage_path.mkdir(exist_ok=True)
        self.db_path = self.storage_path / 'snapshots.db'
        self.initialize_database()
        
        logger.info("✅ SnapshotEngine initialized")
    
    def initialize_database(self):
        """Initialize the snapshots database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    snapshot_type TEXT NOT NULL,
                    parent_snapshot TEXT,
                    compressed_size INTEGER,
                    uncompressed_size INTEGER,
                    file_count INTEGER,
                    checksum TEXT,
                    system_state TEXT,
                    services_state TEXT,
                    database_states TEXT,
                    git_commit_hash TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create restoration history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restoration_history (
                    restoration_id TEXT PRIMARY KEY,
                    snapshot_id TEXT,
                    timestamp TEXT NOT NULL,
                    target_path TEXT,
                    components_restored TEXT,
                    status TEXT,
                    error_details TEXT,
                    duration_seconds REAL,
                    restored_file_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create system events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    component TEXT,
                    details TEXT,
                    severity TEXT,
                    snapshot_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Snapshot database initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize snapshot database: {e}")
    
    def create_snapshot(self, name: str, description: str, snapshot_type: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new snapshot"""
        try:
            snapshot_id = f"snapshot_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            timestamp = datetime.now().isoformat()
            
            # Create snapshot directory
            snapshot_dir = self.storage_path / snapshot_id
            snapshot_dir.mkdir(exist_ok=True)
            
            # Determine what to include
            if components is None:
                components = ['services', 'databases', 'configuration']
            
            total_size = 0
            file_count = 0
            
            # Copy system components
            for component in components:
                if component == 'services':
                    self._backup_services(snapshot_dir, total_size, file_count)
                elif component == 'databases':
                    self._backup_databases(snapshot_dir, total_size, file_count)
                elif component == 'configuration':
                    self._backup_configuration(snapshot_dir, total_size, file_count)
            
            # Create compressed archive
            archive_path = snapshot_dir / f"{snapshot_id}.zip"
            self._create_compressed_archive(snapshot_dir, archive_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(archive_path)
            
            # Store metadata
            metadata = {
                'snapshot_id': snapshot_id,
                'timestamp': timestamp,
                'name': name,
                'description': description,
                'snapshot_type': snapshot_type,
                'compressed_size': archive_path.stat().st_size,
                'uncompressed_size': total_size,
                'file_count': file_count,
                'checksum': checksum,
                'status': 'active'
            }
            
            self._store_snapshot_metadata(metadata)
            
            # Cleanup temporary files
            shutil.rmtree(snapshot_dir)
            
            logger.info(f"✅ Snapshot created: {snapshot_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to create snapshot: {e}")
            return {'error': str(e)}
    
    def _backup_services(self, snapshot_dir: Path, total_size: int, file_count: int):
        """Backup service files"""
        services_dir = snapshot_dir / 'services'
        services_dir.mkdir(exist_ok=True)
        
        # Copy service files
        source_services = project_root / 'services'
        if source_services.exists():
            shutil.copytree(source_services, services_dir, dirs_exist_ok=True)
            total_size += sum(f.stat().st_size for f in services_dir.rglob('*') if f.is_file())
            file_count += len(list(services_dir.rglob('*')))
    
    def _backup_databases(self, snapshot_dir: Path, total_size: int, file_count: int):
        """Backup database files"""
        db_dir = snapshot_dir / 'databases'
        db_dir.mkdir(exist_ok=True)
        
        # Copy database files
        for db_file in project_root.glob('*.db'):
            shutil.copy2(db_file, db_dir)
            total_size += db_file.stat().st_size
            file_count += 1
    
    def _backup_configuration(self, snapshot_dir: Path, total_size: int, file_count: int):
        """Backup configuration files"""
        config_dir = snapshot_dir / 'configuration'
        config_dir.mkdir(exist_ok=True)
        
        # Copy configuration files
        config_files = ['service.yaml', 'requirements.txt', 'README.md', 'CLAUDE.md']
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                shutil.copy2(config_path, config_dir)
                total_size += config_path.stat().st_size
                file_count += 1
    
    def _create_compressed_archive(self, source_dir: Path, archive_path: Path):
        """Create compressed archive of snapshot"""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _store_snapshot_metadata(self, metadata: Dict[str, Any]):
        """Store snapshot metadata in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO snapshots (
                    snapshot_id, timestamp, name, description, snapshot_type,
                    compressed_size, uncompressed_size, file_count, checksum, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata['snapshot_id'], metadata['timestamp'], metadata['name'],
                metadata['description'], metadata['snapshot_type'], metadata['compressed_size'],
                metadata['uncompressed_size'], metadata['file_count'], metadata['checksum'],
                metadata['status']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store snapshot metadata: {e}")
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT snapshot_id, timestamp, name, description, snapshot_type,
                       compressed_size, file_count, status
                FROM snapshots
                ORDER BY timestamp DESC
            ''')
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append({
                    'snapshot_id': row[0],
                    'timestamp': row[1],
                    'name': row[2],
                    'description': row[3],
                    'snapshot_type': row[4],
                    'compressed_size': row[5],
                    'file_count': row[6],
                    'status': row[7]
                })
            
            conn.close()
            return snapshots
            
        except Exception as e:
            logger.error(f"❌ Failed to list snapshots: {e}")
            return []
    
    def get_snapshot_details(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM snapshots WHERE snapshot_id = ?
            ''', (snapshot_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'snapshot_id': row[0],
                    'timestamp': row[1],
                    'name': row[2],
                    'description': row[3],
                    'snapshot_type': row[4],
                    'parent_snapshot': row[5],
                    'compressed_size': row[6],
                    'uncompressed_size': row[7],
                    'file_count': row[8],
                    'checksum': row[9],
                    'status': row[10]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get snapshot details: {e}")
            return None

def register_with_system_protection():
    """Register this service with the System Protection Service"""
    try:
        import requests
        
        protection_config = {
            'service_name': 'snapshot-service',
            'protected_files': [
                'system_backups/',
                'system_backups/snapshots.db',
                'services/snapshot_service.py'
            ],
            'protected_ports': [8085],
            'backup_required': True,
            'integrity_checks': ['snapshot_integrity', 'storage_space', 'database_health']
        }
        
        response = requests.post(
            'http://localhost:8999/api/system/register-service',
            json=protection_config,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Registered with System Protection Service")
            return True
        else:
            logger.warning(f"⚠️ Failed to register with System Protection Service: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Could not register with System Protection Service: {e}")
        return False

def start_snapshot_scheduler():
    """Start the snapshot scheduler thread"""
    global scheduler_thread
    
    def run_scheduler():
        while snapshot_active:
            try:
                # Check if scheduled snapshots are needed
                current_time = datetime.now()
                
                # Daily full snapshot at 2 AM
                if current_time.hour == 2 and current_time.minute == 0:
                    logger.info("🔄 Starting scheduled daily full snapshot")
                    result = snapshot_service.create_snapshot(
                        name=f"daily_snapshot_{current_time.strftime('%Y%m%d')}",
                        description="Daily full system snapshot",
                        snapshot_type="full"
                    )
                    if 'error' not in result:
                        logger.info(f"✅ Daily snapshot completed: {result['snapshot_id']}")
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in snapshot scheduler: {e}")
                time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("✅ Snapshot scheduler started")

# Global snapshot engine instance
snapshot_service = SnapshotEngine(SNAPSHOT_CONFIG)

@app.on_event("startup")
async def startup_event():
    """Initialize the snapshot service on startup"""
    logger.info("🚀 Starting SnapshotService")
    
    # Register with system protection
    register_with_system_protection()
    
    # Start snapshot scheduler
    start_snapshot_scheduler()
    
    logger.info("✅ SnapshotService started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - service_start_time
    
    # Check if snapshot service is healthy
    service_healthy = snapshot_service is not None and snapshot_active
    
    return HealthResponse(
        status="healthy" if service_healthy else "unhealthy",
        timestamp=time.time(),
        uptime=uptime,
        service="snapshot-service",
        version="1.0.0",
        snapshot_active=snapshot_active
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if snapshot service is ready
        service_ready = (
            snapshot_service is not None and 
            snapshot_active and 
            scheduler_thread and 
            scheduler_thread.is_alive()
        )
        
        if service_ready:
            return {"status": "ready", "service": "snapshot-service", "snapshot_active": True}
        else:
            return {"status": "not_ready", "service": "snapshot-service", "snapshot_active": False}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    uptime = time.time() - service_start_time
    
    # Get snapshot statistics
    snapshots = snapshot_service.list_snapshots()
    total_snapshots = len(snapshots)
    total_size = sum(s.get('compressed_size', 0) for s in snapshots)
    
    return {
        "service": "snapshot-service",
        "uptime_seconds": uptime,
        "status": "running",
        "timestamp": time.time(),
        "snapshots": {
            "total_count": total_snapshots,
            "total_size_bytes": total_size,
            "active_snapshots": len([s for s in snapshots if s.get('status') == 'active']),
            "scheduler_running": scheduler_thread and scheduler_thread.is_alive() if scheduler_thread else False
        }
    }

@app.post("/api/snapshots/create", response_model=SnapshotResponse)
async def create_snapshot(request: SnapshotRequest):
    """Create a new snapshot"""
    try:
        logger.info(f"🔄 Creating snapshot: {request.name}")
        
        result = snapshot_service.create_snapshot(
            name=request.name,
            description=request.description or "",
            snapshot_type=request.snapshot_type,
            components=request.components
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=f"Snapshot creation failed: {result['error']}")
        
        return SnapshotResponse(
            snapshot_id=result['snapshot_id'],
            name=result['name'],
            timestamp=result['timestamp'],
            snapshot_type=result['snapshot_type'],
            size_bytes=result['compressed_size'],
            file_count=result['file_count'],
            status=result['status']
        )
        
    except Exception as e:
        logger.error(f"Error creating snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating snapshot: {str(e)}")

@app.get("/api/snapshots/list")
async def list_snapshots():
    """List all snapshots"""
    try:
        snapshots = snapshot_service.list_snapshots()
        
        return {
            "success": True,
            "snapshots": snapshots,
            "total_count": len(snapshots)
        }
        
    except Exception as e:
        logger.error(f"Error listing snapshots: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing snapshots: {str(e)}")

@app.get("/api/snapshots/{snapshot_id}")
async def get_snapshot_details(snapshot_id: str):
    """Get detailed information about a snapshot"""
    try:
        details = snapshot_service.get_snapshot_details(snapshot_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {
            "success": True,
            "snapshot": details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting snapshot details: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting snapshot details: {str(e)}")

@app.get("/api/snapshots/status")
async def get_snapshot_status():
    """Get snapshot service status"""
    try:
        snapshots = snapshot_service.list_snapshots()
        recent_snapshots = snapshots[:5]  # Last 5 snapshots
        
        return {
            "success": True,
            "status": "active" if snapshot_active else "inactive",
            "total_snapshots": len(snapshots),
            "recent_snapshots": recent_snapshots,
            "scheduler_running": scheduler_thread and scheduler_thread.is_alive() if scheduler_thread else False,
            "storage_path": str(snapshot_service.storage_path)
        }
        
    except Exception as e:
        logger.error(f"Error getting snapshot status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "SnapshotService",
        "version": "1.0.0",
        "status": "running",
        "priority": "CRITICAL",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "create_snapshot": "/api/snapshots/create",
            "list_snapshots": "/api/snapshots/list",
            "get_snapshot": "/api/snapshots/{snapshot_id}",
            "status": "/api/snapshots/status"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SnapshotService")
    parser.add_argument("--port", type=int, default=8085, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting SnapshotService on {args.host}:{args.port}")
    
    uvicorn.run(
        "snapshot_service_server:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="info" if not args.debug else "debug"
    )
