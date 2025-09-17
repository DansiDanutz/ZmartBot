#!/usr/bin/env python3
"""
Discovery Database Server - Professional API Service
Implements all endpoints and features defined in discovery-database-service.mdc
Complete RESTful API for ZmartBot 3-database service lifecycle management
"""

import os
import sys
import sqlite3
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError as e:
    print(f"❌ Missing required packages. Install with: pip install fastapi uvicorn watchdog pydantic")
    sys.exit(1)

# Configuration from environment variables
DISCOVERY_DB_PATH = os.getenv("DISCOVERY_DB_PATH", "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db")
MDC_RULES_PATH = os.getenv("MDC_RULES_PATH", "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules")
ZMARTBOT_PATH = os.getenv("ZMARTBOT_PATH", "/Users/dansidanutz/Desktop/ZmartBot")
PASSPORT_DB_PATH = os.getenv("PASSPORT_DB_PATH", "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8780"))

# Logging configuration
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discovery_database_service")

# Pydantic models for API
class DiscoveryService(BaseModel):
    id: Optional[int] = None
    service_name: str
    discovered_date: datetime
    status: str = "DISCOVERED"
    has_mdc_file: bool = True
    has_python_file: bool = True
    python_file_path: str
    mdc_file_path: str
    created_at: datetime
    updated_at: datetime

class TriggerRequest(BaseModel):
    file_path: str = Field(..., description="Path to Python or MDC file to trigger discovery")

class PromoteRequest(BaseModel):
    service_name: str = Field(..., description="Service name to promote to Level 2")

class DatabaseStats(BaseModel):
    total_services: int
    discovered_services: int
    database_size_bytes: int
    last_updated: datetime
    health_status: str

class ServiceMetrics(BaseModel):
    discovery_operations_total: int
    discovery_operations_success: int
    discovery_operations_failed: int
    response_time_avg_ms: float
    database_queries_total: int
    uptime_seconds: int

# Global variables for service state
service_start_time = datetime.now()
operations_counter = {"total": 0, "success": 0, "failed": 0, "response_times": []}
file_watcher_observer = None

class DiscoveryDatabaseService:
    """Core Discovery Database Service Logic"""
    
    def __init__(self):
        self.db_path = DISCOVERY_DB_PATH
        self.mdc_rules_path = MDC_RULES_PATH
        self.zmartbot_path = ZMARTBOT_PATH
        self.passport_db_path = PASSPORT_DB_PATH
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the discovery database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create discovery services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discovery_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'DISCOVERED',
                    has_mdc_file BOOLEAN DEFAULT 0,
                    has_python_file BOOLEAN DEFAULT 1,
                    python_file_path TEXT,
                    mdc_file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_name ON discovery_services(service_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_python_path ON discovery_services(python_file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON discovery_services(status)')
            
            conn.commit()
            conn.close()
            logger.info("✅ Discovery database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def check_duplicates(self, service_name: str, python_file_path: str) -> Optional[str]:
        """Check for ALL types of duplicates - returns error message if duplicate found"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check 1: Service name already exists
            cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
            name_count = cursor.fetchone()[0]
            
            if name_count > 0:
                conn.close()
                return f"DUPLICATE SERVICE NAME: {service_name} already exists in discovery database"
            
            # Check 2: Same Python file path with different name (CRITICAL)
            cursor.execute("SELECT service_name FROM discovery_services WHERE python_file_path = ?", (python_file_path,))
            existing_service = cursor.fetchone()
            
            if existing_service:
                conn.close()
                return f"DUPLICATE PYTHON FILE: {python_file_path} already exists with name '{existing_service[0]}'"
            
            conn.close()
            return None  # No duplicates found
            
        except Exception as e:
            logger.error(f"❌ Error checking duplicates: {e}")
            return f"Database error during duplicate check: {e}"
    
    def has_passport(self, service_name: str) -> bool:
        """Check if service has passport"""
        if not os.path.exists(self.passport_db_path):
            return False
        
        try:
            conn = sqlite3.connect(self.passport_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE'", (service_name,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logger.warning(f"⚠️ Error checking passport for {service_name}: {e}")
            return False
    
    def find_python_file(self, service_name: str) -> Optional[str]:
        """Find Python file with given name in ZmartBot folder"""
        exclude_dirs = ['venv', 'node_modules', '__pycache__', '.git', 'system_backups', 'Documentation', 'backups']
        
        for root, dirs, files in os.walk(self.zmartbot_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(excl in d for excl in exclude_dirs)]
            
            for file in files:
                if file == f"{service_name}.py":
                    return os.path.join(root, file)
        
        return None
    
    def trigger_discovery(self, file_path: str) -> Dict[str, Any]:
        """Trigger discovery for a specific file"""
        start_time = time.time()
        operations_counter["total"] += 1
        
        try:
            if not os.path.exists(file_path):
                operations_counter["failed"] += 1
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Determine service name and file types
            if file_path.endswith('.py'):
                service_name = Path(file_path).stem
                python_file_path = file_path
                mdc_file_path = os.path.join(self.mdc_rules_path, f"{service_name}.mdc")
                
                if not os.path.exists(mdc_file_path):
                    operations_counter["failed"] += 1
                    return {"success": False, "error": f"Python file exists but no MDC file for {service_name}"}
                    
            elif file_path.endswith('.mdc'):
                service_name = Path(file_path).stem
                mdc_file_path = file_path
                
                python_file_path = self.find_python_file(service_name)
                if not python_file_path:
                    operations_counter["failed"] += 1
                    return {"success": False, "error": f"MDC file exists but no Python file for {service_name}"}
            else:
                operations_counter["failed"] += 1
                return {"success": False, "error": f"Unsupported file type: {file_path}"}
            
            # Check if service has passport (exclude if it does)
            if self.has_passport(service_name):
                operations_counter["success"] += 1
                return {"success": True, "skipped": True, "reason": f"{service_name} has passport, not adding to discovery database"}
            
            # Check for duplicates
            duplicate_error = self.check_duplicates(service_name, python_file_path)
            if duplicate_error:
                operations_counter["failed"] += 1
                return {"success": False, "error": duplicate_error}
            
            # Add to discovery database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO discovery_services 
                (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path, updated_at) 
                VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?, ?)
            ''', (service_name, datetime.now(), python_file_path, mdc_file_path, datetime.now()))
            
            conn.commit()
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            operations_counter["response_times"].append(response_time)
            operations_counter["success"] += 1
            
            logger.info(f"✅ {service_name} added to discovery database")
            
            return {
                "success": True,
                "service_name": service_name,
                "python_file_path": python_file_path,
                "mdc_file_path": mdc_file_path,
                "response_time_ms": response_time
            }
            
        except Exception as e:
            operations_counter["failed"] += 1
            logger.error(f"❌ Discovery trigger failed for {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all discovered services"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM discovery_services ORDER BY discovered_date DESC')
            services = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"❌ Error fetching services: {e}")
            return []
    
    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get specific service by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM discovery_services WHERE service_name = ?', (service_name,))
            service = cursor.fetchone()
            
            conn.close()
            return dict(service) if service else None
            
        except Exception as e:
            logger.error(f"❌ Error fetching service {service_name}: {e}")
            return None
    
    def get_database_stats(self) -> DatabaseStats:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM discovery_services')
            total_services = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM discovery_services WHERE status = "DISCOVERED"')
            discovered_services = cursor.fetchone()[0]
            
            cursor.execute('SELECT MAX(updated_at) FROM discovery_services')
            last_updated_str = cursor.fetchone()[0]
            last_updated = datetime.fromisoformat(last_updated_str) if last_updated_str else datetime.now()
            
            conn.close()
            
            # Get database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return DatabaseStats(
                total_services=total_services,
                discovered_services=discovered_services,
                database_size_bytes=db_size,
                last_updated=last_updated,
                health_status="healthy"
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return DatabaseStats(
                total_services=0,
                discovered_services=0,
                database_size_bytes=0,
                last_updated=datetime.now(),
                health_status="error"
            )

# Initialize service
discovery_service = DiscoveryDatabaseService()

# File watcher for automatic detection
class DiscoveryFileHandler(FileSystemEventHandler):
    """Handle file system events for automatic discovery"""
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.py') or file_path.endswith('.mdc'):
                logger.info(f"🔍 New file detected: {file_path}")
                result = discovery_service.trigger_discovery(file_path)
                if result["success"]:
                    logger.info(f"✅ Automatic discovery successful for {file_path}")
                else:
                    logger.warning(f"⚠️ Automatic discovery failed for {file_path}: {result.get('error', 'Unknown error')}")

# FastAPI application with lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global file_watcher_observer
    
    # Startup
    logger.info("🚀 Discovery Database Service starting up...")
    
    # Optional: Start file watcher
    if os.getenv("ENABLE_FILE_WATCHER", "false").lower() == "true":
        try:
            event_handler = DiscoveryFileHandler()
            file_watcher_observer = Observer()
            file_watcher_observer.schedule(event_handler, ZMARTBOT_PATH, recursive=True)
            file_watcher_observer.schedule(event_handler, MDC_RULES_PATH, recursive=False)
            file_watcher_observer.start()
            logger.info("👁️ File watcher started")
        except Exception as e:
            logger.warning(f"⚠️ File watcher failed to start: {e}")
    
    logger.info(f"✅ Discovery Database Service ready on port {SERVICE_PORT}")
    yield
    
    # Shutdown
    if file_watcher_observer:
        file_watcher_observer.stop()
        file_watcher_observer.join()
        logger.info("👁️ File watcher stopped")
    
    logger.info("🛑 Discovery Database Service shut down")

# Create FastAPI application
app = FastAPI(
    title="Discovery Database Service",
    description="Professional API service for ZmartBot 3-database service lifecycle management",
    version="1.0.0",
    lifespan=lifespan
)

# Core Discovery Operations
@app.get("/health", summary="Service health check", tags=["Health"])
async def health_check():
    """Service health check and database connectivity"""
    try:
        # Test database connectivity
        conn = sqlite3.connect(DISCOVERY_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM discovery_services")
        count = cursor.fetchone()[0]
        conn.close()
        
        uptime = (datetime.now() - service_start_time).total_seconds()
        
        return {
            "status": "healthy",
            "service": "discovery-database-service",
            "version": "1.0.0",
            "uptime_seconds": uptime,
            "database_connectivity": "ok",
            "discovered_services": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

@app.get("/status", response_model=Dict[str, Any], summary="Service status and metrics", tags=["Status"])
async def get_status():
    """Service status and discovery database metrics"""
    stats = discovery_service.get_database_stats()
    uptime = (datetime.now() - service_start_time).total_seconds()
    
    avg_response_time = sum(operations_counter["response_times"][-100:]) / len(operations_counter["response_times"][-100:]) if operations_counter["response_times"] else 0
    
    return {
        "service_status": "running",
        "uptime_seconds": uptime,
        "database_stats": stats.dict(),
        "operations": {
            "total": operations_counter["total"],
            "successful": operations_counter["success"],
            "failed": operations_counter["failed"],
            "success_rate": operations_counter["success"] / max(operations_counter["total"], 1) * 100
        },
        "performance": {
            "avg_response_time_ms": avg_response_time,
            "recent_operations": len(operations_counter["response_times"][-10:])
        },
        "configuration": {
            "database_path": DISCOVERY_DB_PATH,
            "mdc_rules_path": MDC_RULES_PATH,
            "zmartbot_path": ZMARTBOT_PATH,
            "service_port": SERVICE_PORT
        }
    }

@app.get("/discover", summary="Manual discovery trigger for all services", tags=["Discovery"])
async def manual_discover():
    """Manual discovery trigger for all services - scans for new services"""
    try:
        discovered_count = 0
        errors = []
        
        # Scan Python files in zmart-api directory
        zmart_api_path = os.path.join(ZMARTBOT_PATH, "zmart-api")
        if os.path.exists(zmart_api_path):
            for file in os.listdir(zmart_api_path):
                if file.endswith('.py') and not file.startswith('test_') and not file.startswith('debug_'):
                    file_path = os.path.join(zmart_api_path, file)
                    result = discovery_service.trigger_discovery(file_path)
                    if result["success"] and not result.get("skipped"):
                        discovered_count += 1
                    elif not result["success"]:
                        errors.append(f"{file}: {result['error']}")
        
        return {
            "success": True,
            "discovered_services": discovered_count,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual discovery failed: {e}")

@app.post("/discover/trigger", response_model=Dict[str, Any], summary="Trigger discovery for specific file", tags=["Discovery"])
async def trigger_discovery(request: TriggerRequest):
    """Trigger discovery for specific file"""
    result = discovery_service.trigger_discovery(request.file_path)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/services", response_model=List[Dict[str, Any]], summary="List all discovered services", tags=["Services"])
async def get_services():
    """List all discovered services"""
    services = discovery_service.get_all_services()
    return services

@app.get("/services/{service_name}", response_model=Dict[str, Any], summary="Get specific service details", tags=["Services"])
async def get_service(service_name: str):
    """Get specific discovered service details"""
    service = discovery_service.get_service_by_name(service_name)
    
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    return service

# Database Management
@app.get("/database/stats", response_model=DatabaseStats, summary="Discovery database statistics", tags=["Database"])
async def get_database_stats():
    """Discovery database statistics and counts"""
    return discovery_service.get_database_stats()

@app.post("/database/cleanup", summary="Remove invalid entries", tags=["Database"])
async def cleanup_database():
    """Remove invalid or orphaned entries"""
    try:
        conn = sqlite3.connect(DISCOVERY_DB_PATH)
        cursor = conn.cursor()
        
        # Remove services where files no longer exist
        cursor.execute('SELECT id, service_name, python_file_path, mdc_file_path FROM discovery_services')
        services = cursor.fetchall()
        
        removed_count = 0
        for service_id, service_name, python_path, mdc_path in services:
            if not os.path.exists(python_path) or not os.path.exists(mdc_path):
                cursor.execute('DELETE FROM discovery_services WHERE id = ?', (service_id,))
                removed_count += 1
                logger.info(f"🧹 Removed orphaned service: {service_name}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "removed_services": removed_count,
            "message": f"Cleanup completed, removed {removed_count} invalid entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {e}")

@app.get("/metrics", summary="Prometheus-compatible metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus-compatible metrics"""
    uptime = (datetime.now() - service_start_time).total_seconds()
    stats = discovery_service.get_database_stats()
    avg_response_time = sum(operations_counter["response_times"][-100:]) / len(operations_counter["response_times"][-100:]) if operations_counter["response_times"] else 0
    
    metrics = f"""# HELP discovery_services_total Total number of discovered services
# TYPE discovery_services_total gauge
discovery_services_total {stats.total_services}

# HELP discovery_operations_total Total number of discovery operations
# TYPE discovery_operations_total counter
discovery_operations_total {operations_counter["total"]}

# HELP discovery_operations_success_total Successful discovery operations
# TYPE discovery_operations_success_total counter
discovery_operations_success_total {operations_counter["success"]}

# HELP discovery_operations_failed_total Failed discovery operations
# TYPE discovery_operations_failed_total counter
discovery_operations_failed_total {operations_counter["failed"]}

# HELP discovery_response_time_ms Average response time in milliseconds
# TYPE discovery_response_time_ms gauge
discovery_response_time_ms {avg_response_time}

# HELP discovery_service_uptime_seconds Service uptime in seconds
# TYPE discovery_service_uptime_seconds gauge
discovery_service_uptime_seconds {uptime}

# HELP discovery_database_size_bytes Database size in bytes
# TYPE discovery_database_size_bytes gauge
discovery_database_size_bytes {stats.database_size_bytes}
"""
    return JSONResponse(content=metrics, media_type="text/plain")

if __name__ == "__main__":
    print("🚀 Starting Discovery Database Service")
    print(f"📊 Database: {DISCOVERY_DB_PATH}")
    print(f"🔍 MDC Rules: {MDC_RULES_PATH}")
    print(f"📁 ZmartBot Path: {ZMARTBOT_PATH}")
    print(f"🌐 Service Port: {SERVICE_PORT}")
    print("")
    
    try:
        uvicorn.run(
            "discovery_database_server:app",
            host="127.0.0.1",
            port=SERVICE_PORT,
            reload=False,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⏹️ Discovery Database Service stopped by user")
    except Exception as e:
        print(f"❌ Service failed to start: {e}")
        sys.exit(1)