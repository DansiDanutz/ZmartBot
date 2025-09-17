#!/usr/bin/env python3
"""
Master Orchestration Agent - System Orchestration Controller
Central orchestration controller for ZmartBot system, managing service lifecycle, 
dependencies, health monitoring, and automated operations.

Port: 8002
Type: Backend Orchestration Service
Version: 1.0.0
"""

import os
import sys
import asyncio
import logging
import json
import time
import sqlite3
import threading
import subprocess
import signal
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@dataclass
class ServiceInfo:
    """Service information structure"""
    service_name: str
    port: int
    service_type: str
    status: str
    passport_id: Optional[str] = None
    description: str = ""
    health_status: str = "unknown"
    connection_status: str = "unknown"
    start_time: Optional[datetime] = None
    process_id: Optional[int] = None
    dependencies: List[str] = None
    startup_command: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class PassportProtection:
    """Passport protection system - prevents deletion of protected services"""
    
    def __init__(self, db_path: str = "src/data/service_registry.db"):
        self.db_path = db_path
        self.protected_services: Set[str] = set()
        self.load_protected_services()
    
    def load_protected_services(self):
        """Load services with passport IDs from registry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # First check if passport_id column exists
                cursor.execute("PRAGMA table_info(service_registry)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'passport_id' in columns:
                    cursor.execute("""
                        SELECT service_name FROM service_registry 
                        WHERE passport_id IS NOT NULL AND passport_id != ''
                    """)
                    self.protected_services = {row[0] for row in cursor.fetchall()}
                else:
                    # If no passport_id column, protect all services by default
                    cursor.execute("SELECT service_name FROM service_registry")
                    self.protected_services = {row[0] for row in cursor.fetchall()}
                    logger.warning("⚠️ No passport_id column found, protecting all services")
                
                logger.info(f"🛂 Loaded {len(self.protected_services)} passport-protected services")
        except Exception as e:
            logger.error(f"❌ Failed to load passport protection: {e}")
    
    def is_protected(self, service_name: str) -> bool:
        """Check if service is passport-protected"""
        return service_name in self.protected_services
    
    def validate_deletion(self, service_name: str) -> bool:
        """Validate if service can be deleted (passport protection check)"""
        if self.is_protected(service_name):
            logger.error(f"🚫 PASSPORT PROTECTION: Cannot delete protected service {service_name}")
            return False
        return True
    
    def get_protected_services(self) -> List[str]:
        """Get list of all protected services"""
        return list(self.protected_services)

class ServiceRegistry:
    """Service registry and database management"""
    
    def __init__(self, db_path: str = "src/data/service_registry.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize service registry database - work with existing schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if passport_id column exists, if not add it
            cursor.execute("PRAGMA table_info(service_registry)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'passport_id' not in columns:
                cursor.execute("ALTER TABLE service_registry ADD COLUMN passport_id TEXT")
            if 'health_status' not in columns:
                cursor.execute("ALTER TABLE service_registry ADD COLUMN health_status TEXT DEFAULT 'unknown'")
            if 'connection_status' not in columns:
                cursor.execute("ALTER TABLE service_registry ADD COLUMN connection_status TEXT DEFAULT 'unknown'")
            if 'process_id' not in columns:
                cursor.execute("ALTER TABLE service_registry ADD COLUMN process_id INTEGER")
            if 'description' not in columns:
                cursor.execute("ALTER TABLE service_registry ADD COLUMN description TEXT")
                
            conn.commit()
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services - compatible with existing schema"""
        services = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT service_name, port, kind, status, 
                           passport_id, description, health_status, connection_status, 
                           process_id, startup_command
                    FROM service_registry ORDER BY service_name
                """)
                for row in cursor.fetchall():
                    service = ServiceInfo(
                        service_name=row[0],
                        port=row[1],
                        service_type=row[2] or "unknown",  # kind -> service_type
                        status=row[3],
                        passport_id=row[4],
                        description=row[5] or "",
                        health_status=row[6] or "unknown",
                        connection_status=row[7] or "unknown",
                        process_id=row[8],
                        startup_command=row[9]
                    )
                    services.append(service)
        except Exception as e:
            logger.error(f"❌ Failed to load services: {e}")
        return services
    
    def update_service_status(self, service_name: str, status: str, health_status: str = None, 
                            connection_status: str = None, process_id: int = None):
        """Update service status in registry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
                values = [status]
                
                if health_status:
                    update_fields.append("health_status = ?")
                    values.append(health_status)
                if connection_status:
                    update_fields.append("connection_status = ?")
                    values.append(connection_status)
                if process_id:
                    update_fields.append("process_id = ?")
                    values.append(process_id)
                    if status == "ACTIVE":
                        update_fields.append("start_time = ?")
                        values.append(datetime.now().isoformat())
                
                values.append(service_name)
                
                cursor.execute(f"""
                    UPDATE service_registry 
                    SET {', '.join(update_fields)}
                    WHERE service_name = ?
                """, values)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to update service status: {e}")

class HealthMonitor:
    """Service health monitoring system"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.monitoring = False
        self.monitor_thread = None
    
    async def check_service_health(self, service: ServiceInfo) -> Dict[str, str]:
        """Check individual service health"""
        try:
            # Check if process is running
            if service.process_id:
                try:
                    process = psutil.Process(service.process_id)
                    if process.is_running():
                        # Try health endpoint
                        response = requests.get(f"http://localhost:{service.port}/health", timeout=5)
                        if response.status_code == 200:
                            return {"status": "healthy", "connection": "connected"}
                        else:
                            return {"status": "unhealthy", "connection": "connected"}
                    else:
                        return {"status": "offline", "connection": "disconnected"}
                except psutil.NoSuchProcess:
                    return {"status": "offline", "connection": "disconnected"}
            else:
                # Try to connect to service
                try:
                    response = requests.get(f"http://localhost:{service.port}/health", timeout=3)
                    return {"status": "healthy", "connection": "connected"}
                except requests.exceptions.RequestException:
                    return {"status": "offline", "connection": "disconnected"}
        except Exception as e:
            logger.error(f"❌ Health check failed for {service.service_name}: {e}")
            return {"status": "unknown", "connection": "unknown"}
    
    def start_monitoring(self):
        """Start health monitoring loop"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 Started health monitoring")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Health monitoring loop"""
        while self.monitoring:
            try:
                services = self.service_registry.get_all_services()
                for service in services:
                    if service.status == "ACTIVE":
                        health_result = asyncio.run(self.check_service_health(service))
                        self.service_registry.update_service_status(
                            service.service_name,
                            service.status,
                            health_result["status"],
                            health_result["connection"]
                        )
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(60)  # Wait longer on error

class ServiceManager:
    """Service lifecycle management"""
    
    def __init__(self, service_registry: ServiceRegistry, passport_protection: PassportProtection):
        self.service_registry = service_registry
        self.passport_protection = passport_protection
        self.service_processes: Dict[str, subprocess.Popen] = {}
    
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        try:
            services = self.service_registry.get_all_services()
            service = next((s for s in services if s.service_name == service_name), None)
            
            if not service:
                logger.error(f"❌ Service {service_name} not found in registry")
                return False
            
            if service.status == "ACTIVE" and service.health_status == "healthy":
                logger.info(f"⚠️ Service {service_name} already running and healthy")
                return True
            
            # Start the service process
            startup_cmd = self._get_startup_command(service)
            if not startup_cmd:
                logger.error(f"❌ No startup command for {service_name}")
                return False
            
            logger.info(f"🚀 Starting {service_name} with command: {startup_cmd}")
            
            # Start process
            process = subprocess.Popen(
                startup_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.service_processes[service_name] = process
            
            # Update registry
            self.service_registry.update_service_status(
                service_name, "ACTIVE", "starting", "connecting", process.pid
            )
            
            logger.info(f"✅ Started {service_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False
    
    async def stop_service(self, service_name: str, force: bool = False) -> bool:
        """Stop a specific service with passport protection"""
        try:
            # Check passport protection
            if not force and not self.passport_protection.validate_deletion(service_name):
                logger.error(f"🚫 Cannot stop passport-protected service {service_name}")
                return False
            
            services = self.service_registry.get_all_services()
            service = next((s for s in services if s.service_name == service_name), None)
            
            if not service:
                logger.error(f"❌ Service {service_name} not found")
                return False
            
            # Stop process
            stopped = False
            if service_name in self.service_processes:
                process = self.service_processes[service_name]
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=10)
                    stopped = True
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    stopped = True
                except Exception as e:
                    logger.error(f"❌ Failed to stop process for {service_name}: {e}")
                del self.service_processes[service_name]
            else:
                # Try to find and stop process by port
                for proc in psutil.process_iter(['pid', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline and any(f"--port {service.port}" in ' '.join(cmdline) for _ in [1]):
                            proc.terminate()
                            proc.wait(timeout=10)
                            stopped = True
                            logger.info(f"✅ Stopped process {proc.info['pid']} for {service_name}")
                            break
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired, Exception):
                        continue
            
            # Try to kill by port if process stop failed
            if service.process_id and not stopped:
                try:
                    process = psutil.Process(service.process_id)
                    process.terminate()
                    process.wait(timeout=10)
                    stopped = True
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        process.kill()
                        stopped = True
                    except:
                        pass
            
            # Update registry
            self.service_registry.update_service_status(
                service_name, "DISABLED", "offline", "disconnected", None
            )
            
            logger.info(f"🛑 Stopped {service_name}")
            return stopped
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {service_name}: {e}")
            return False
    
    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        try:
            logger.info(f"🔄 Restarting {service_name}")
            
            # Check if service is actually running first
            services = self.service_registry.get_all_services()
            service = next((s for s in services if s.service_name == service_name), None)
            
            if not service:
                logger.error(f"❌ Service {service_name} not found in registry")
                return False
            
            # If service is already offline/stopped, just start it
            if service.health_status == "offline" or service.connection_status == "disconnected":
                logger.info(f"Service {service_name} is already stopped, starting directly")
                start_result = await self.start_service(service_name)
                logger.info(f"Start result for {service_name}: {start_result}")
                return start_result
            
            # Otherwise, stop then start
            stop_result = await self.stop_service(service_name, force=True)
            logger.info(f"Stop result for {service_name}: {stop_result}")
            
            if stop_result:
                time.sleep(2)  # Brief pause
                start_result = await self.start_service(service_name)
                logger.info(f"Start result for {service_name}: {start_result}")
                return start_result
            else:
                logger.error(f"Failed to stop {service_name} during restart")
                return False
        except Exception as e:
            logger.error(f"❌ Exception during restart of {service_name}: {e}")
            return False
    
    def _get_startup_command(self, service: ServiceInfo) -> Optional[str]:
        """Get startup command for a service"""
        # Define startup commands for known services
        startup_commands = {
            "zmart-api": f"cd {os.path.dirname(__file__)} && python3 main.py --port {service.port}",
            "doctor-service": f"cd {os.path.dirname(__file__)} && python3 src/services/doctor_service.py --port {service.port}",
            "passport-service": f"cd {os.path.dirname(__file__)} && python3 src/services/passport_service.py --port {service.port}",
            "zmart-dashboard": f"cd {os.path.dirname(__file__)}/dashboard && python3 server.py --port {service.port}",
            "service-dashboard": f"cd {os.path.dirname(__file__)}/dashboard/Service-Dashboard && python3 server.py --port {service.port}",
        }
        
        if service.startup_command:
            return service.startup_command
        
        return startup_commands.get(service.service_name, 
                                  f"python3 {service.service_name}.py --port {service.port}")

class MasterOrchestrationAgent:
    """Main orchestration controller"""
    
    def __init__(self, port: int = 8002):
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize subsystems
        self.service_registry = ServiceRegistry()
        self.passport_protection = PassportProtection()
        self.health_monitor = HealthMonitor(self.service_registry)
        self.service_manager = ServiceManager(self.service_registry, self.passport_protection)
        
        self.running = False
        self.setup_routes()
        
        # Graceful shutdown handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health')
        def health_check():
            return jsonify({"status": "healthy", "service": "master-orchestration-agent", "port": self.port})
        
        @self.app.route('/ready')
        def readiness_check():
            return jsonify({"status": "ready", "services": len(self.service_registry.get_all_services())})
        
        @self.app.route('/api/orchestration/status')
        def get_status():
            services = self.service_registry.get_all_services()
            running_count = len([s for s in services if s.status == "ACTIVE"])
            protected_count = len(self.passport_protection.get_protected_services())
            
            return jsonify({
                "orchestration_status": "active",
                "total_services": len(services),
                "running_services": running_count,
                "protected_services": protected_count,
                "monitoring": self.health_monitor.monitoring,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/orchestration/services')
        def get_services():
            services = self.service_registry.get_all_services()
            return jsonify([asdict(service) for service in services])
        
        @self.app.route('/api/orchestration/services/<service_name>/start', methods=['POST'])
        def start_service_endpoint(service_name: str):
            try:
                result = asyncio.run(self.service_manager.start_service(service_name))
                if result:
                    return jsonify({"status": "success", "message": f"Started {service_name}"})
                else:
                    return jsonify({"status": "error", "message": f"Failed to start {service_name}"}), 500
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/api/orchestration/services/<service_name>/stop', methods=['POST'])
        def stop_service_endpoint(service_name: str):
            try:
                force = request.json.get('force', False) if request.is_json else False
                result = asyncio.run(self.service_manager.stop_service(service_name, force))
                if result:
                    return jsonify({"status": "success", "message": f"Stopped {service_name}"})
                else:
                    return jsonify({"status": "error", "message": f"Failed to stop {service_name}"}), 500
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/api/orchestration/services/<service_name>/restart', methods=['POST'])
        def restart_service_endpoint(service_name: str):
            try:
                result = asyncio.run(self.service_manager.restart_service(service_name))
                if result:
                    return jsonify({"status": "success", "message": f"Restarted {service_name}"})
                else:
                    return jsonify({"status": "error", "message": f"Failed to restart {service_name}"}), 500
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/api/orchestration/passport/protected')
        def get_protected_services():
            protected = self.passport_protection.get_protected_services()
            return jsonify({"protected_services": protected, "count": len(protected)})
        
        @self.app.route('/api/orchestration/services/<service_name>/logs')
        def get_service_logs(service_name: str):
            """Get logs for a specific service"""
            try:
                services = self.service_registry.get_all_services()
                service = next((s for s in services if s.service_name == service_name), None)
                
                if not service:
                    return jsonify({"status": "error", "message": f"Service {service_name} not found"}), 404
                
                # Try to find log file for service
                log_paths = [
                    f"{service_name}.log",
                    f"logs/{service_name}.log", 
                    f"../logs/{service_name}.log",
                    f"src/logs/{service_name}.log",
                    f"{service.service_name}_server.log",
                    f"nohup.out"  # Common fallback
                ]
                
                logs_content = ""
                log_file_found = False
                
                for log_path in log_paths:
                    try:
                        if os.path.exists(log_path):
                            with open(log_path, 'r') as f:
                                # Read last 1000 lines to avoid massive responses
                                lines = f.readlines()
                                logs_content = ''.join(lines[-1000:])
                                log_file_found = True
                                break
                    except Exception as e:
                        continue
                
                if not log_file_found:
                    # Try to get recent logs from system journal if available
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['journalctl', '-u', service_name, '--lines=100', '--no-pager'],
                            capture_output=True, text=True, timeout=5
                        )
                        if result.returncode == 0:
                            logs_content = result.stdout
                            log_file_found = True
                    except:
                        pass
                
                if log_file_found:
                    return jsonify({
                        "status": "success",
                        "service_name": service_name,
                        "logs": logs_content,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        "status": "success",
                        "service_name": service_name,
                        "logs": f"No log files found for {service_name}.\n\nSearched locations:\n" + "\n".join(log_paths),
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"❌ Failed to get logs for {service_name}: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        @self.app.route('/api/orchestration/services/<service_name>/doctor', methods=['POST'])
        def send_to_doctor(service_name: str):
            """Send service to Doctor Service for diagnosis"""
            try:
                services = self.service_registry.get_all_services()
                service = next((s for s in services if s.service_name == service_name), None)
                
                if not service:
                    return jsonify({"status": "error", "message": f"Service {service_name} not found"}), 404
                
                # Try to send to Doctor Service
                try:
                    doctor_response = requests.post('http://localhost:8700/api/doctor/diagnose', 
                        json={
                            "service_name": service_name,
                            "problem_description": f"Service {service_name} needs diagnosis. Status: {service.status}, Health: {service.health_status}, Connection: {service.connection_status}",
                            "service_details": {
                                "port": service.port,
                                "type": service.service_type,
                                "status": service.status,
                                "process_id": service.process_id,
                                "passport_id": service.passport_id
                            },
                            "health_status": {
                                "health_status": service.health_status,
                                "connection_status": service.connection_status
                            },
                            "priority": "normal"
                        }, 
                        timeout=10
                    )
                    
                    if doctor_response.status_code == 200:
                        diagnosis = doctor_response.json()
                        return jsonify({
                            "status": "success",
                            "message": f"Service {service_name} sent to Doctor Service successfully",
                            "diagnosis": diagnosis
                        })
                    else:
                        return jsonify({
                            "status": "error",
                            "message": f"Doctor Service responded with error: {doctor_response.status_code}"
                        }), 500
                        
                except requests.exceptions.RequestException as e:
                    return jsonify({
                        "status": "error",
                        "message": f"Failed to connect to Doctor Service: {str(e)}. Is Doctor Service running on port 8700?"
                    }), 500
                    
            except Exception as e:
                logger.error(f"❌ Failed to send {service_name} to Doctor Service: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
    
    def start(self):
        """Start the orchestration service"""
        try:
            logger.info(f"🎯 Starting Master Orchestration Agent on port {self.port}")
            
            # Start health monitoring
            self.health_monitor.start_monitoring()
            
            # Register self in service registry
            self._register_self()
            
            self.running = True
            logger.info(f"✅ Master Orchestration Agent ready on http://localhost:{self.port}")
            
            # Start Flask server
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
            
        except Exception as e:
            logger.error(f"❌ Failed to start orchestration service: {e}")
            self.stop()
    
    def stop(self):
        """Stop the orchestration service"""
        logger.info("🛑 Stopping Master Orchestration Agent...")
        self.running = False
        self.health_monitor.stop_monitoring()
        logger.info("✅ Master Orchestration Agent stopped")
    
    def _register_self(self):
        """Register orchestration service in registry"""
        try:
            with sqlite3.connect(self.service_registry.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO service_registry 
                    (service_name, port, kind, status, passport_id, description, health_status, connection_status, start_cmd, process_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "master-orchestration-agent",
                    self.port,
                    "orchestration",
                    "ACTIVE",
                    "ZMBT-AGT-20250826-430BAD",
                    "Central system orchestration controller",
                    "healthy",
                    "connected",
                    f"python3 orchestration_server.py --port {self.port}",
                    os.getpid()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to register self: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.stop()
        exit(0)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Master Orchestration Agent")
    parser.add_argument('--port', type=int, default=8002, help='Service port (default: 8002)')
    args = parser.parse_args()
    
    # Create and start orchestration agent
    orchestration_agent = MasterOrchestrationAgent(port=args.port)
    orchestration_agent.start()

if __name__ == "__main__":
    main()