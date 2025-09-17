#!/usr/bin/env python3
"""
Discovery File Watcher - Professional Real-Time Monitoring System
Monitors for new .py and .mdc files and updates discovery database automatically
Advanced file system monitoring with professional features

Features:
- Professional logging and monitoring
- Health checks and self-recovery
- Performance metrics and analytics
- Error handling and resilience
- Integration with Discovery Database Service
- Configurable monitoring parameters
"""

import os
import sys
import sqlite3
import time
import json
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
import threading
from contextlib import contextmanager

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import psutil
except ImportError as e:
    print(f"❌ Missing required packages. Install with: pip install watchdog psutil")
    sys.exit(1)

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/discovery_watcher.log', mode='a')
    ]
)
logger = logging.getLogger("discovery_file_watcher")

# Ensure log directory exists
os.makedirs('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs', exist_ok=True)

# Global configuration
CONFIG = {
    "DISCOVERY_DB_PATH": "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db",
    "MDC_RULES_PATH": "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules",
    "ZMARTBOT_PATH": "/Users/dansidanutz/Desktop/ZmartBot",
    "PASSPORT_DB_PATH": "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db",
    "HEALTH_CHECK_INTERVAL": 60,  # seconds
    "METRICS_REPORT_INTERVAL": 300,  # seconds
    "MAX_EVENTS_PER_MINUTE": 100,
    "ENABLE_SELF_HEALING": True
}

class DiscoveryMetrics:
    """Professional metrics tracking"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.events_processed = 0
        self.events_successful = 0
        self.events_failed = 0
        self.events_skipped = 0
        self.response_times = []
        self.last_activity = None
        self.health_checks = 0
        self.errors_by_type = {}
        self.events_by_hour = {}
        self.lock = threading.Lock()
    
    def record_event(self, success: bool, response_time_ms: float, event_type: str = None, error_type: str = None):
        """Record event metrics"""
        with self.lock:
            self.events_processed += 1
            self.response_times.append(response_time_ms)
            self.last_activity = datetime.now()
            
            if success:
                self.events_successful += 1
            else:
                self.events_failed += 1
                if error_type:
                    self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
            
            # Track events by hour
            hour_key = self.last_activity.strftime("%Y-%m-%d %H:00")
            self.events_by_hour[hour_key] = self.events_by_hour.get(hour_key, 0) + 1
    
    def record_skip(self):
        """Record skipped event"""
        with self.lock:
            self.events_skipped += 1
    
    def record_health_check(self):
        """Record health check"""
        with self.lock:
            self.health_checks += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with self.lock:
            uptime = datetime.now() - self.start_time
            avg_response_time = sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0
            success_rate = (self.events_successful / max(self.events_processed, 1)) * 100
            
            return {
                "uptime_seconds": uptime.total_seconds(),
                "events_processed": self.events_processed,
                "events_successful": self.events_successful,
                "events_failed": self.events_failed,
                "events_skipped": self.events_skipped,
                "success_rate_percent": round(success_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "health_checks_performed": self.health_checks,
                "last_activity": self.last_activity.isoformat() if self.last_activity else None,
                "errors_by_type": self.errors_by_type.copy(),
                "events_by_hour": dict(list(self.events_by_hour.items())[-24:])  # Last 24 hours
            }

class DiscoveryService:
    """Professional discovery service integration"""
    
    def __init__(self):
        self.db_path = CONFIG["DISCOVERY_DB_PATH"]
        self.mdc_rules_path = CONFIG["MDC_RULES_PATH"]
        self.zmartbot_path = CONFIG["ZMARTBOT_PATH"]
        self.passport_db_path = CONFIG["PASSPORT_DB_PATH"]
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the discovery database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_name ON discovery_services(service_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_python_path ON discovery_services(python_file_path)')
            
            conn.commit()
            conn.close()
            logger.debug("✅ Discovery database initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    def has_passport(self, service_name: str) -> bool:
        """Check if service has passport"""
        if not os.path.exists(self.passport_db_path):
            return False
        
        try:
            with sqlite3.connect(self.passport_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE'", (service_name,))
                return cursor.fetchone()[0] > 0
        except Exception as e:
            logger.warning(f"⚠️ Error checking passport for {service_name}: {e}")
            return False
    
    def check_duplicates(self, service_name: str, python_file_path: str) -> Optional[str]:
        """Check for duplicates"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
                if cursor.fetchone()[0] > 0:
                    return f"Service name {service_name} already exists"
                
                cursor.execute("SELECT service_name FROM discovery_services WHERE python_file_path = ?", (python_file_path,))
                existing = cursor.fetchone()
                if existing:
                    return f"Python file already exists with name {existing[0]}"
                
                return None
        except Exception as e:
            logger.error(f"❌ Error checking duplicates: {e}")
            return f"Database error: {e}"
    
    def find_python_file(self, service_name: str) -> Optional[str]:
        """Find Python file efficiently"""
        exclude_dirs = {'venv', 'node_modules', '__pycache__', '.git', 'system_backups', 'Documentation', 'backups'}
        
        try:
            for root, dirs, files in os.walk(self.zmartbot_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                target_file = f"{service_name}.py"
                if target_file in files:
                    return os.path.join(root, target_file)
        except Exception as e:
            logger.error(f"❌ Error searching for {service_name}.py: {e}")
        
        return None
    
    def add_to_discovery(self, service_name: str, python_path: str, mdc_path: str) -> Dict[str, Any]:
        """Add service to discovery database"""
        start_time = time.time()
        
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO discovery_services 
                    (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path, updated_at) 
                    VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?, ?)
                ''', (service_name, datetime.now(), python_path, mdc_path, datetime.now()))
                
                conn.commit()
                
                response_time = (time.time() - start_time) * 1000
                return {
                    "success": True,
                    "service_name": service_name,
                    "response_time_ms": response_time
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Database insertion failed for {service_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service_name": service_name,
                "response_time_ms": response_time
            }

class ProfessionalDiscoveryFileHandler(FileSystemEventHandler):
    """Professional file system event handler"""
    
    def __init__(self, discovery_service: DiscoveryService, metrics: DiscoveryMetrics):
        super().__init__()
        self.discovery_service = discovery_service
        self.metrics = metrics
        self.recent_events: Set[str] = set()
        self.event_lock = threading.Lock()
        
        # Start cleanup thread for recent events
        self.cleanup_thread = threading.Thread(target=self._cleanup_recent_events, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_recent_events(self):
        """Clean up recent events to prevent memory leaks"""
        while True:
            time.sleep(300)  # Clean up every 5 minutes
            with self.event_lock:
                self.recent_events.clear()
    
    def _should_process_event(self, file_path: str) -> bool:
        """Check if event should be processed (debouncing)"""
        with self.event_lock:
            if file_path in self.recent_events:
                return False
            self.recent_events.add(file_path)
            return True
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if not (file_path.endswith('.py') or file_path.endswith('.mdc')):
            return
        
        if not self._should_process_event(file_path):
            self.metrics.record_skip()
            return
        
        logger.info(f"🔍 New file detected: {file_path}")
        self._process_file_event(file_path, "created")
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if not file_path.endswith('.mdc'):
            return
        
        if not self._should_process_event(file_path):
            self.metrics.record_skip()
            return
            
        logger.debug(f"🔄 MDC file modified: {file_path}")
        self._process_file_event(file_path, "modified")
    
    def _process_file_event(self, file_path: str, event_type: str):
        """Process file system event"""
        start_time = time.time()
        
        try:
            result = self._check_and_update_discovery(file_path)
            response_time = (time.time() - start_time) * 1000
            
            if result["success"]:
                if result.get("skipped"):
                    logger.info(f"⏭️  {result['service_name']} - {result['reason']}")
                    self.metrics.record_event(True, response_time, event_type)
                else:
                    logger.info(f"✅ {result['service_name']} added to discovery database")
                    self.metrics.record_event(True, response_time, event_type)
            else:
                logger.warning(f"⚠️ Discovery failed for {file_path}: {result['error']}")
                error_type = result.get("error_type", "unknown")
                self.metrics.record_event(False, response_time, event_type, error_type)
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Event processing failed for {file_path}: {e}")
            self.metrics.record_event(False, response_time, event_type, "processing_error")
    
    def _check_and_update_discovery(self, file_path: str) -> Dict[str, Any]:
        """Check file and update discovery database"""
        try:
            if file_path.endswith('.py'):
                service_name = Path(file_path).stem
                python_file_path = file_path
                mdc_file_path = os.path.join(self.discovery_service.mdc_rules_path, f"{service_name}.mdc")
                
                if not os.path.exists(mdc_file_path):
                    return {
                        "success": False,
                        "error": "No corresponding MDC file",
                        "error_type": "mdc_missing",
                        "service_name": service_name
                    }
                    
            elif file_path.endswith('.mdc'):
                service_name = Path(file_path).stem
                mdc_file_path = file_path
                
                python_file_path = self.discovery_service.find_python_file(service_name)
                if not python_file_path:
                    return {
                        "success": False,
                        "error": "No corresponding Python file",
                        "error_type": "python_missing",
                        "service_name": service_name
                    }
            else:
                return {
                    "success": False,
                    "error": "Unsupported file type",
                    "error_type": "unsupported_file"
                }
            
            # Check if service has passport
            if self.discovery_service.has_passport(service_name):
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Service has passport, not adding to discovery",
                    "service_name": service_name
                }
            
            # Check for duplicates
            duplicate_error = self.discovery_service.check_duplicates(service_name, python_file_path)
            if duplicate_error:
                return {
                    "success": False,
                    "error": duplicate_error,
                    "error_type": "duplicate",
                    "service_name": service_name
                }
            
            # Add to discovery database
            return self.discovery_service.add_to_discovery(service_name, python_file_path, mdc_file_path)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "processing_error"
            }

class DiscoveryFileWatcher:
    """Professional file watcher service"""
    
    def __init__(self):
        self.discovery_service = DiscoveryService()
        self.metrics = DiscoveryMetrics()
        self.observer = None
        self.health_thread = None
        self.metrics_thread = None
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self.running:
            try:
                time.sleep(CONFIG["HEALTH_CHECK_INTERVAL"])
                if not self.running:
                    break
                    
                self._perform_health_check()
                self.metrics.record_health_check()
                
            except Exception as e:
                logger.error(f"❌ Health check failed: {e}")
    
    def _perform_health_check(self):
        """Perform comprehensive health check"""
        health_issues = []
        
        # Check database connectivity
        try:
            with self.discovery_service.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM discovery_services")
                count = cursor.fetchone()[0]
                logger.debug(f"🏥 Health check: {count} services in discovery database")
        except Exception as e:
            health_issues.append(f"Database connectivity: {e}")
        
        # Check file system access
        for path_key, path_value in [("MDC_RULES_PATH", CONFIG["MDC_RULES_PATH"]), ("ZMARTBOT_PATH", CONFIG["ZMARTBOT_PATH"])]:
            if not os.path.exists(path_value) or not os.access(path_value, os.R_OK):
                health_issues.append(f"File system access: {path_key} not accessible")
        
        # Check observer status
        if not self.observer or not self.observer.is_alive():
            health_issues.append("File observer is not running")
        
        # Check memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > 500:  # 500MB threshold
            health_issues.append(f"High memory usage: {memory_mb:.1f}MB")
        
        if health_issues:
            logger.warning(f"⚠️ Health check issues: {'; '.join(health_issues)}")
            if CONFIG["ENABLE_SELF_HEALING"]:
                self._attempt_self_healing(health_issues)
        else:
            logger.debug("✅ Health check passed")
    
    def _attempt_self_healing(self, issues: list):
        """Attempt to self-heal from issues"""
        logger.info("🔧 Attempting self-healing...")
        
        for issue in issues:
            if "File observer is not running" in issue and self.running:
                try:
                    logger.info("🔄 Restarting file observer...")
                    if self.observer:
                        self.observer.stop()
                    self._start_observer()
                    logger.info("✅ File observer restarted successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to restart observer: {e}")
    
    def _metrics_report_loop(self):
        """Background metrics reporting loop"""
        while self.running:
            try:
                time.sleep(CONFIG["METRICS_REPORT_INTERVAL"])
                if not self.running:
                    break
                    
                stats = self.metrics.get_stats()
                logger.info(f"📊 METRICS: {stats['events_processed']} events processed, "
                           f"{stats['success_rate_percent']}% success rate, "
                           f"{stats['avg_response_time_ms']}ms avg response time")
                
            except Exception as e:
                logger.error(f"❌ Metrics reporting failed: {e}")
    
    def _start_observer(self):
        """Start file system observer"""
        event_handler = ProfessionalDiscoveryFileHandler(self.discovery_service, self.metrics)
        self.observer = Observer()
        
        # Watch ZmartBot folder for Python files
        self.observer.schedule(event_handler, CONFIG["ZMARTBOT_PATH"], recursive=True)
        
        # Watch MDC rules folder for MDC files
        self.observer.schedule(event_handler, CONFIG["MDC_RULES_PATH"], recursive=False)
        
        self.observer.start()
    
    def start(self):
        """Start the file watcher service"""
        logger.info("🚀 Starting Professional Discovery File Watcher")
        logger.info(f"📁 Monitoring: {CONFIG['ZMARTBOT_PATH']}")
        logger.info(f"📋 MDC Rules: {CONFIG['MDC_RULES_PATH']}")
        logger.info(f"📊 Database: {CONFIG['DISCOVERY_DB_PATH']}")
        logger.info(f"🔧 Config: Health checks every {CONFIG['HEALTH_CHECK_INTERVAL']}s, metrics every {CONFIG['METRICS_REPORT_INTERVAL']}s")
        logger.info("")
        
        try:
            self.running = True
            
            # Start file observer
            self._start_observer()
            
            # Start background threads
            self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
            self.health_thread.start()
            
            self.metrics_thread = threading.Thread(target=self._metrics_report_loop, daemon=True)
            self.metrics_thread.start()
            
            logger.info("👁️ File watcher started successfully")
            logger.info("📊 Monitoring for .py and .mdc file changes...")
            logger.info("⚡ Professional features: Health monitoring, metrics, self-healing")
            logger.info("🛑 Press Ctrl+C to stop")
            
            # Main loop
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Failed to start file watcher: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the file watcher service"""
        if not self.running:
            return
            
        logger.info("🛑 Stopping Discovery File Watcher...")
        self.running = False
        
        # Stop observer
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            logger.info("👁️ File observer stopped")
        
        # Wait for background threads
        if self.health_thread and self.health_thread.is_alive():
            self.health_thread.join(timeout=2)
        
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=2)
        
        # Final metrics report
        stats = self.metrics.get_stats()
        logger.info(f"📊 FINAL STATS: {stats['events_processed']} events processed, "
                   f"{stats['success_rate_percent']}% success rate, "
                   f"uptime: {stats['uptime_seconds']:.1f}s")
        
        logger.info("✅ Discovery File Watcher stopped successfully")

def main():
    """Main function"""
    print("🚀 Professional Discovery File Watcher")
    print("🔍 Real-time monitoring for .py and .mdc files")
    print("⚡ Features: Health monitoring, metrics, self-healing")
    print("")
    
    try:
        watcher = DiscoveryFileWatcher()
        watcher.start()
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()