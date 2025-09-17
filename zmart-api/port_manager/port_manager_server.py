#!/usr/bin/env python3
"""
Port Manager Server for ZmartBot Platform
Centralized port management service that prevents conflicts and ensures proper service isolation
"""

import os
import sys
import sqlite3
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PortAssignment:
    """Represents a port assignment"""
    service_name: str
    port: int
    service_type: str
    status: str = "active"
    pid: Optional[int] = None
    assigned_at: str = None
    updated_at: str = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.assigned_at is None:
            self.assigned_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

@dataclass
class PortRange:
    """Represents a port range for service types"""
    start_port: int
    end_port: int
    service_type: str
    description: str

class PortManagerService:
    """
    Port Manager Service that manages port allocations for all ZmartBot services
    """
    
    def __init__(self, project_root: str = None, port: int = 8610):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.port = port
        self.db_path = self.project_root / "zmart-api" / "port_registry.db"
        
        # Port ranges for different service types
        self.port_ranges = [
            PortRange(3400, 3499, "frontend", "Frontend services"),
            PortRange(8000, 8099, "backend", "Backend API services"),
            PortRange(8200, 8299, "internal_api", "Internal API services"),
            PortRange(8300, 8399, "worker", "Worker services"),
            PortRange(8500, 8599, "orchestration", "Orchestration services"),
            PortRange(8600, 8699, "management", "Management services")
        ]
        
        # Initialize database
        self.init_database()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        logger.info(f"Port Manager Service initialized - Port: {self.port}")
    
    def init_database(self):
        """Initialize the port registry database"""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create port_assignments table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS port_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    port INTEGER UNIQUE NOT NULL,
                    service_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    pid INTEGER,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Port registry database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "port-manager-service"
            })
        
        @self.app.route('/ready', methods=['GET'])
        def ready():
            """Readiness check endpoint"""
            try:
                # Test database connection
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM port_assignments")
                count = cursor.fetchone()[0]
                conn.close()
                
                return jsonify({
                    "status": "ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "port-manager-service",
                    "database": "connected",
                    "registered_services": count
                }), 200
                
            except Exception as e:
                return jsonify({
                    "status": "not_ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "port-manager-service",
                    "error": str(e)
                }), 503
        
        @self.app.route('/status', methods=['GET'])
        def status():
            """Complete system status"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get all port assignments
                cursor.execute("""
                    SELECT service_name, port, service_type, status, pid, assigned_at 
                    FROM port_assignments 
                    ORDER BY port
                """)
                assignments = cursor.fetchall()
                
                # Get statistics
                cursor.execute("SELECT COUNT(*) FROM port_assignments")
                total_services = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM port_assignments WHERE status = 'active'")
                active_services = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "port-manager-service",
                    "total_services": total_services,
                    "active_services": active_services,
                    "port_assignments": [
                        {
                            "service_name": row[0],
                            "port": row[1],
                            "service_type": row[2],
                            "status": row[3],
                            "pid": row[4],
                            "assigned_at": row[5]
                        }
                        for row in assignments
                    ]
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                    "service": "port-manager-service",
                    "error": str(e)
                }), 500
        
        @self.app.route('/assign', methods=['POST'])
        def assign_port():
            """Assign a port to a new service"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                service_name = data.get('service_name')
                service_type = data.get('service_type', 'backend')
                
                if not service_name:
                    return jsonify({"error": "service_name is required"}), 400
                
                # Check if service already exists
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT port FROM port_assignments WHERE service_name = ?", (service_name,))
                existing = cursor.fetchone()
                
                if existing:
                    conn.close()
                    return jsonify({
                        "error": f"Service '{service_name}' already exists with port {existing[0]}"
                    }), 409
                
                # Find available port
                available_port = self.find_available_port(service_type, cursor)
                
                if not available_port:
                    conn.close()
                    return jsonify({
                        "error": f"No available ports for service type '{service_type}'"
                    }), 503
                
                # Assign port
                cursor.execute("""
                    INSERT INTO port_assignments (service_name, port, service_type, status, assigned_at, updated_at)
                    VALUES (?, ?, ?, 'active', datetime('now'), datetime('now'))
                """, (service_name, available_port, service_type))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Assigned port {available_port} to service '{service_name}'")
                
                return jsonify({
                    "success": True,
                    "service_name": service_name,
                    "port": available_port,
                    "service_type": service_type,
                    "message": f"Port {available_port} assigned to {service_name}"
                })
                
            except Exception as e:
                logger.error(f"Port assignment failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/services', methods=['GET'])
        def get_services():
            """Get all registered services"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, port, service_type, status, pid, assigned_at 
                    FROM port_assignments 
                    ORDER BY port
                """)
                services = cursor.fetchall()
                conn.close()
                
                return jsonify({
                    "services": [
                        {
                            "service_name": row[0],
                            "port": row[1],
                            "service_type": row[2],
                            "status": row[3],
                            "pid": row[4],
                            "assigned_at": row[5]
                        }
                        for row in services
                    ]
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/assign-manual', methods=['POST'])
        def assign_manual_port():
            """Manually assign a specific port to a service"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                service_name = data.get('service_name')
                service_type = data.get('service_type', 'backend')
                requested_port = data.get('port')
                
                if not service_name:
                    return jsonify({"error": "service_name is required"}), 400
                
                if not requested_port:
                    return jsonify({"error": "port is required for manual assignment"}), 400
                
                # Check if service already exists
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT port FROM port_assignments WHERE service_name = ?", (service_name,))
                existing = cursor.fetchone()
                
                if existing:
                    conn.close()
                    return jsonify({
                        "error": f"Service '{service_name}' already exists with port {existing[0]}"
                    }), 409
                
                # Check if port is already in use
                cursor.execute("SELECT service_name FROM port_assignments WHERE port = ?", (requested_port,))
                port_in_use = cursor.fetchone()
                
                if port_in_use:
                    conn.close()
                    return jsonify({
                        "error": f"Port {requested_port} is already assigned to service '{port_in_use[0]}'"
                    }), 409
                
                # Assign the specific port
                cursor.execute("""
                    INSERT INTO port_assignments (service_name, port, service_type, status, assigned_at, updated_at)
                    VALUES (?, ?, ?, 'active', datetime('now'), datetime('now'))
                """, (service_name, requested_port, service_type))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Manually assigned port {requested_port} to service '{service_name}'")
                
                return jsonify({
                    "success": True,
                    "service_name": service_name,
                    "port": requested_port,
                    "service_type": service_type,
                    "message": f"Port {requested_port} manually assigned to {service_name}"
                })
                
            except Exception as e:
                logger.error(f"Manual port assignment failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/services/<service_name>', methods=['GET'])
        def get_service(service_name):
            """Get specific service information"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, port, service_type, status, pid, assigned_at, updated_at
                    FROM port_assignments 
                    WHERE service_name = ?
                """, (service_name,))
                service = cursor.fetchone()
                conn.close()
                
                if not service:
                    return jsonify({"error": f"Service '{service_name}' not found"}), 404
                
                return jsonify({
                    "service_name": service[0],
                    "port": service[1],
                    "service_type": service[2],
                    "status": service[3],
                    "pid": service[4],
                    "assigned_at": service[5],
                    "updated_at": service[6]
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/ports/available', methods=['GET'])
        def get_available_ports():
            """Get available ports by service type"""
            try:
                service_type = request.args.get('service_type', 'backend')
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get used ports for this service type
                cursor.execute("SELECT port FROM port_assignments WHERE service_type = ?", (service_type,))
                used_ports = {row[0] for row in cursor.fetchall()}
                conn.close()
                
                # Find port range for service type
                port_range = next((r for r in self.port_ranges if r.service_type == service_type), None)
                
                if not port_range:
                    return jsonify({"error": f"Unknown service type: {service_type}"}), 400
                
                # Find available ports
                available_ports = []
                for port in range(port_range.start_port, port_range.end_port + 1):
                    if port not in used_ports:
                        available_ports.append(port)
                
                return jsonify({
                    "service_type": service_type,
                    "port_range": {
                        "start": port_range.start_port,
                        "end": port_range.end_port
                    },
                    "used_ports": list(used_ports),
                    "available_ports": available_ports,
                    "total_available": len(available_ports)
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def find_available_port(self, service_type: str, cursor) -> Optional[int]:
        """Find an available port for the given service type"""
        # Find port range for service type
        port_range = next((r for r in self.port_ranges if r.service_type == service_type), None)
        
        if not port_range:
            return None
        
        # Get used ports for this service type
        cursor.execute("SELECT port FROM port_assignments WHERE service_type = ?", (service_type,))
        used_ports = {row[0] for row in cursor.fetchall()}
        
        # Find first available port
        for port in range(port_range.start_port, port_range.end_port + 1):
            if port not in used_ports:
                return port
        
        return None
    
    def run(self):
        """Run the Port Manager service"""
        logger.info(f"Starting Port Manager Service on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Port Manager Service')
    parser.add_argument('--port', type=int, default=8610, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    
    args = parser.parse_args()
    
    # Create and run service
    service = PortManagerService(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()
