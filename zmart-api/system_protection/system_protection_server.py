#!/usr/bin/env python3
"""
System Protection Service - FastAPI Server
CRITICAL service that prevents accidental mass deletions and ensures system integrity
"""

import asyncio
import logging
import sys
import os
import shutil
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import threading
import subprocess

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="System Protection Service",
    description="CRITICAL system protection service that prevents accidental mass deletions and ensures system integrity",
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
protection_active = True
monitoring_thread = None

# Protection configuration
PROTECTION_CONFIG = {
    'critical_dirs': ['.cursor/rules', 'Dashboard/MDC-Dashboard', 'Documentation', 'services', 'src'],
    'min_mdc_count': 50,
    'backup_dir': './system_backups',
    'alert_threshold': 30,
    'monitoring_interval': 60,
    'protected_files': [
        'run_dev.py', 'src/main.py', 'src/routes/', 'src/services/', 'src/config/',
        'professional_dashboard_server.py', 'professional_dashboard/App.jsx',
        'professional_dashboard/api-proxy.js', 'professional_dashboard/components/',
        'professional_dashboard/App.css', 'professional_dashboard/index.html'
    ]
}

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    service: str
    version: str
    protection_active: bool

class SystemIntegrityResponse(BaseModel):
    integrity_status: str
    mdc_file_count: int
    critical_dirs_status: Dict[str, bool]
    last_backup: Optional[str]
    protection_active: bool
    alerts: List[str]

class EmergencyBackupRequest(BaseModel):
    backup_name: Optional[str] = None
    include_logs: bool = True

class ServiceProtectionRequest(BaseModel):
    service_name: str
    protected_files: List[str]
    protected_ports: List[int]
    backup_required: bool = True
    integrity_checks: List[str] = []

class SystemProtectionService:
    """System protection service implementation"""
    
    def __init__(self):
        self.critical_dirs = PROTECTION_CONFIG['critical_dirs']
        self.min_mdc_count = PROTECTION_CONFIG['min_mdc_count']
        self.backup_dir = Path(project_root) / PROTECTION_CONFIG['backup_dir']
        self.alert_threshold = PROTECTION_CONFIG['alert_threshold']
        self.monitoring_interval = PROTECTION_CONFIG['monitoring_interval']
        self.protected_files = PROTECTION_CONFIG['protected_files']
        
        # Initialize backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Service protection registry
        self.registered_services = {}
        self.service_protection_rules = {}
        
        # Monitoring state
        self.baseline_mdc_count = self.count_mdc_files()
        self.last_backup_time = None
        self.alerts = []
        
        logger.info("✅ System Protection Service initialized")
    
    def count_mdc_files(self) -> int:
        """Count MDC files in the system"""
        try:
            mdc_count = 0
            for root, dirs, files in os.walk(project_root):
                for file in files:
                    if file.endswith('.mdc'):
                        mdc_count += 1
            return mdc_count
        except Exception as e:
            logger.error(f"Error counting MDC files: {e}")
            return 0
    
    def check_critical_directories(self) -> Dict[str, bool]:
        """Check if critical directories exist"""
        status = {}
        for dir_path in self.critical_dirs:
            full_path = project_root / dir_path
            status[dir_path] = full_path.exists() and any(full_path.iterdir())
        return status
    
    def check_system_integrity(self) -> bool:
        """Check overall system integrity"""
        try:
            # Check MDC file count
            current_mdc_count = self.count_mdc_files()
            if current_mdc_count < self.min_mdc_count:
                self.alerts.append(f"CRITICAL: MDC file count too low: {current_mdc_count}")
                return False
            
            # Check critical directories
            dir_status = self.check_critical_directories()
            if not all(dir_status.values()):
                missing_dirs = [k for k, v in dir_status.items() if not v]
                self.alerts.append(f"CRITICAL: Missing critical directories: {missing_dirs}")
                return False
            
            # Check protected files
            for file_path in self.protected_files:
                full_path = project_root / file_path
                if not full_path.exists():
                    self.alerts.append(f"WARNING: Protected file missing: {file_path}")
            
            return len([a for a in self.alerts if a.startswith("CRITICAL")]) == 0
            
        except Exception as e:
            logger.error(f"Error checking system integrity: {e}")
            self.alerts.append(f"ERROR: System integrity check failed: {e}")
            return False
    
    def create_emergency_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create emergency backup"""
        try:
            if not backup_name:
                backup_name = f"emergency_backup_{int(time.time())}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Copy critical files
            critical_files_copied = 0
            for root, dirs, files in os.walk(project_root):
                for file in files:
                    if file.endswith(('.mdc', '.py', '.yaml', '.json', '.md')):
                        src_path = Path(root) / file
                        rel_path = src_path.relative_to(project_root)
                        dst_path = backup_path / rel_path
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        critical_files_copied += 1
            
            self.last_backup_time = datetime.now().isoformat()
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "files_copied": critical_files_copied,
                "timestamp": self.last_backup_time
            }
            
        except Exception as e:
            logger.error(f"Error creating emergency backup: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def register_service_protection(self, service_config: Dict[str, Any]) -> bool:
        """Register a service for protection"""
        try:
            service_name = service_config['service_name']
            self.registered_services[service_name] = service_config
            self.service_protection_rules[service_name] = {
                'protected_files': service_config.get('protected_files', []),
                'protected_ports': service_config.get('protected_ports', []),
                'backup_required': service_config.get('backup_required', False),
                'integrity_checks': service_config.get('integrity_checks', [])
            }
            
            logger.info(f"✅ Service {service_name} registered for protection")
            return True
            
        except Exception as e:
            logger.error(f"Error registering service protection: {e}")
            return False
    
    def start_monitoring(self):
        """Start system monitoring thread"""
        def monitor_system():
            while protection_active:
                try:
                    if not self.check_system_integrity():
                        logger.warning("⚠️ System integrity compromised - triggering emergency response")
                        self.trigger_emergency_response()
                    
                    time.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring thread: {e}")
                    time.sleep(self.monitoring_interval)
        
        self.monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        self.monitoring_thread.start()
        logger.info("✅ System monitoring started")
    
    def trigger_emergency_response(self):
        """Trigger emergency response procedures"""
        try:
            logger.critical("🚨 EMERGENCY RESPONSE TRIGGERED")
            
            # Create emergency backup
            backup_result = self.create_emergency_backup()
            logger.info(f"Emergency backup created: {backup_result}")
            
            # Log critical alert
            self.alerts.append("CRITICAL: System integrity compromised - emergency response triggered")
            
            # Send notifications (placeholder)
            logger.critical("Sending emergency notifications...")
            
        except Exception as e:
            logger.error(f"Error in emergency response: {e}")

# Global protection service instance
protection_service = SystemProtectionService()

@app.on_event("startup")
async def startup_event():
    """Initialize the protection service on startup"""
    logger.info("🚀 Starting System Protection Service")
    
    # Start system monitoring
    protection_service.start_monitoring()
    
    # Create initial backup
    backup_result = protection_service.create_emergency_backup("initial_startup_backup")
    logger.info(f"Initial backup created: {backup_result}")
    
    logger.info("✅ System Protection Service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - service_start_time
    return HealthResponse(
        status="healthy" if protection_service.check_system_integrity() else "critical",
        timestamp=time.time(),
        uptime=uptime,
        service="system-protection-service",
        version="1.0.0",
        protection_active=protection_active
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if protection service is ready
        integrity_ok = protection_service.check_system_integrity()
        monitoring_active = protection_service.monitoring_thread and protection_service.monitoring_thread.is_alive()
        
        if integrity_ok and monitoring_active:
            return {"status": "ready", "service": "system-protection-service", "protection_active": True}
        else:
            return {"status": "not_ready", "service": "system-protection-service", "protection_active": False}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    uptime = time.time() - service_start_time
    return {
        "service": "system-protection-service",
        "uptime_seconds": uptime,
        "status": "running",
        "timestamp": time.time(),
        "protection": {
            "mdc_file_count": protection_service.count_mdc_files(),
            "registered_services": len(protection_service.registered_services),
            "alerts_count": len(protection_service.alerts),
            "last_backup": protection_service.last_backup_time
        }
    }

@app.get("/api/system/integrity", response_model=SystemIntegrityResponse)
async def check_system_integrity():
    """Check system integrity"""
    try:
        integrity_ok = protection_service.check_system_integrity()
        dir_status = protection_service.check_critical_directories()
        
        return SystemIntegrityResponse(
            integrity_status="healthy" if integrity_ok else "compromised",
            mdc_file_count=protection_service.count_mdc_files(),
            critical_dirs_status=dir_status,
            last_backup=protection_service.last_backup_time,
            protection_active=protection_active,
            alerts=protection_service.alerts[-10:]  # Last 10 alerts
        )
        
    except Exception as e:
        logger.error(f"Error checking system integrity: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking integrity: {str(e)}")

@app.post("/api/system/emergency-backup")
async def create_emergency_backup(request: EmergencyBackupRequest):
    """Create emergency backup"""
    try:
        backup_result = protection_service.create_emergency_backup(request.backup_name)
        
        if backup_result["success"]:
            return {
                "success": True,
                "message": "Emergency backup created successfully",
                "backup": backup_result
            }
        else:
            raise HTTPException(status_code=500, detail=f"Backup failed: {backup_result['error']}")
            
    except Exception as e:
        logger.error(f"Error creating emergency backup: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")

@app.post("/api/system/register-service")
async def register_service_for_protection(request: ServiceProtectionRequest):
    """Register a service for protection"""
    try:
        service_config = {
            'service_name': request.service_name,
            'protected_files': request.protected_files,
            'protected_ports': request.protected_ports,
            'backup_required': request.backup_required,
            'integrity_checks': request.integrity_checks
        }
        
        success = protection_service.register_service_protection(service_config)
        
        if success:
            return {
                "success": True,
                "message": f"Service {request.service_name} registered for protection",
                "service": request.service_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to register service for protection")
            
    except Exception as e:
        logger.error(f"Error registering service protection: {e}")
        raise HTTPException(status_code=500, detail=f"Error registering service: {str(e)}")

@app.get("/api/system/registered-services")
async def get_registered_services():
    """Get list of registered services"""
    try:
        return {
            "success": True,
            "services": list(protection_service.registered_services.keys()),
            "total_services": len(protection_service.registered_services)
        }
        
    except Exception as e:
        logger.error(f"Error getting registered services: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting services: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "System Protection Service",
        "version": "1.0.0",
        "status": "running",
        "priority": "CRITICAL",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "integrity": "/api/system/integrity",
            "emergency_backup": "/api/system/emergency-backup",
            "register_service": "/api/system/register-service",
            "registered_services": "/api/system/registered-services"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="System Protection Service")
    parser.add_argument("--port", type=int, default=8999, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting System Protection Service on {args.host}:{args.port}")
    
    uvicorn.run(
        "system_protection_server:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="info" if not args.debug else "debug"
    )
