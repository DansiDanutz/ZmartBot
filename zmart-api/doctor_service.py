#!/usr/bin/env python3
"""
Doctor Service - System Health Monitoring and Diagnostics
Created: 2025-08-31
Purpose: Monitor system health and provide diagnostic capabilities
Level: 2 (Active Production)
Port: 8700
Passport: SR-DOCTOR_SERVICE-8700-L2
Owner: zmartbot-system
Status: ACTIVE
"""

import os
import sys
import sqlite3
import json
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoctorService:
    """System health monitoring and diagnostic service"""
    
    def __init__(self, port=8700):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "doctor-service",
                "port": self.port,
                "timestamp": datetime.now().isoformat(),
                "system_status": "operational"
            })
        
        @self.app.route('/api/system-diagnosis')
        def system_diagnosis():
            """Complete system diagnosis"""
            try:
                diagnosis = self.perform_system_diagnosis()
                return jsonify(diagnosis)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/service-health')
        def service_health():
            """Check health of all services"""
            try:
                health_report = self.check_all_services_health()
                return jsonify(health_report)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system-resources')
        def system_resources():
            """Get system resource usage"""
            try:
                resources = self.get_system_resources()
                return jsonify(resources)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def perform_system_diagnosis(self) -> Dict:
        """Perform complete system diagnosis"""
        logger.info("🩺 Performing system diagnosis...")
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "system_health": "unknown",
            "critical_issues": [],
            "warnings": [],
            "system_resources": self.get_system_resources(),
            "database_health": self.check_database_health(),
            "service_status": self.check_service_status(),
            "recommendations": []
        }
        
        # Analyze system health
        critical_count = len(diagnosis["critical_issues"])
        warning_count = len(diagnosis["warnings"])
        
        if critical_count == 0 and warning_count == 0:
            diagnosis["system_health"] = "excellent"
        elif critical_count == 0 and warning_count <= 2:
            diagnosis["system_health"] = "good"
        elif critical_count <= 1:
            diagnosis["system_health"] = "warning"
        else:
            diagnosis["system_health"] = "critical"
        
        # Generate recommendations
        diagnosis["recommendations"] = self.generate_recommendations(diagnosis)
        
        return diagnosis
    
    def get_system_resources(self) -> Dict:
        """Get system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": psutil.cpu_count(),
                    "status": "good" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "good" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "status": "good" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
                }
            }
        except Exception as e:
            return {
                "error": f"Failed to get system resources: {e}",
                "cpu": {"status": "unknown"},
                "memory": {"status": "unknown"},
                "disk": {"status": "unknown"}
            }
    
    def check_database_health(self) -> Dict:
        """Check health of system databases"""
        databases = [
            ("Level1.db", "Level 1 Discovery Services"),
            ("Level2.db", "Level 2 Active Services"),
            ("Level3.db", "Level 3 Certified Services"),
            ("CERT.db", "Certification Database")
        ]
        
        db_health = {
            "status": "unknown",
            "databases": {},
            "total_databases": len(databases),
            "healthy_databases": 0,
            "issues": []
        }
        
        for db_file, description in databases:
            db_path = self.root_dir / db_file
            
            if not db_path.exists():
                db_health["databases"][db_file] = {
                    "status": "missing",
                    "description": description,
                    "issue": "Database file not found"
                }
                db_health["issues"].append(f"{db_file} database missing")
                continue
            
            try:
                # Test database connection
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                db_health["databases"][db_file] = {
                    "status": "healthy",
                    "description": description,
                    "tables_count": len(tables),
                    "file_size_mb": round(db_path.stat().st_size / (1024*1024), 2)
                }
                db_health["healthy_databases"] += 1
                
            except Exception as e:
                db_health["databases"][db_file] = {
                    "status": "error",
                    "description": description,
                    "issue": str(e)
                }
                db_health["issues"].append(f"{db_file} database error: {e}")
        
        # Overall database health status
        if db_health["healthy_databases"] == db_health["total_databases"]:
            db_health["status"] = "excellent"
        elif db_health["healthy_databases"] >= db_health["total_databases"] * 0.8:
            db_health["status"] = "good"
        elif db_health["healthy_databases"] >= db_health["total_databases"] * 0.5:
            db_health["status"] = "warning"
        else:
            db_health["status"] = "critical"
        
        return db_health
    
    def check_service_status(self) -> Dict:
        """Check status of key services"""
        key_services = [
            ("Level 1 Database Creator", 8903),
            ("Level 2 Database Creator", 8904),
            ("Level 3 Database Creator", 8905),
            ("CERT Database Creator", 8906),
            ("Level 3 Promotion Service", 8907),
            ("Service Requirements Audit", 8908),
            ("Level 2 Python File Fixer", 8909),
            ("MDC File Creator", 8910)
        ]
        
        service_status = {
            "status": "unknown",
            "services": {},
            "total_services": len(key_services),
            "running_services": 0,
            "issues": []
        }
        
        for service_name, port in key_services:
            try:
                # Check if port is in use (service likely running)
                connections = psutil.net_connections()
                port_in_use = any(conn.laddr.port == port for conn in connections if conn.laddr)
                
                service_status["services"][service_name] = {
                    "port": port,
                    "status": "running" if port_in_use else "stopped",
                    "health_url": f"http://127.0.0.1:{port}/health"
                }
                
                if port_in_use:
                    service_status["running_services"] += 1
                else:
                    service_status["issues"].append(f"{service_name} not running on port {port}")
                    
            except Exception as e:
                service_status["services"][service_name] = {
                    "port": port,
                    "status": "error",
                    "issue": str(e)
                }
                service_status["issues"].append(f"{service_name} check failed: {e}")
        
        # Overall service status
        running_ratio = service_status["running_services"] / service_status["total_services"]
        if running_ratio >= 0.9:
            service_status["status"] = "excellent"
        elif running_ratio >= 0.7:
            service_status["status"] = "good"
        elif running_ratio >= 0.5:
            service_status["status"] = "warning"
        else:
            service_status["status"] = "critical"
        
        return service_status
    
    def check_all_services_health(self) -> Dict:
        """Check health of all services"""
        return {
            "timestamp": datetime.now().isoformat(),
            "service_health_summary": self.check_service_status(),
            "database_health": self.check_database_health(),
            "system_resources": self.get_system_resources()
        }
    
    def generate_recommendations(self, diagnosis: Dict) -> List[str]:
        """Generate recommendations based on diagnosis"""
        recommendations = []
        
        # Resource recommendations
        resources = diagnosis.get("system_resources", {})
        if resources.get("memory", {}).get("status") == "warning":
            recommendations.append("Consider freeing up memory or adding more RAM")
        if resources.get("cpu", {}).get("status") == "warning":
            recommendations.append("High CPU usage detected - check running processes")
        if resources.get("disk", {}).get("status") == "warning":
            recommendations.append("Disk space running low - clean up unnecessary files")
        
        # Database recommendations
        db_health = diagnosis.get("database_health", {})
        if db_health.get("status") in ["warning", "critical"]:
            recommendations.append("Database issues detected - run database maintenance")
        
        # Service recommendations
        service_status = diagnosis.get("service_status", {})
        if service_status.get("status") in ["warning", "critical"]:
            recommendations.append("Some services are not running - check service status")
        
        if not recommendations:
            recommendations.append("System is running optimally")
        
        return recommendations
    
    def run(self):
        """Run the doctor service"""
        logger.info(f"Starting Doctor Service on port {self.port}")
        logger.info("🩺 System Health Monitoring Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Doctor Service stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Doctor Service")
    parser.add_argument('--port', type=int, default=8700, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--diagnosis', action='store_true', help='Run system diagnosis')
    
    args = parser.parse_args()
    
    doctor = DoctorService(port=args.port)
    
    if args.diagnosis:
        diagnosis = doctor.perform_system_diagnosis()
        print(f"System Diagnosis: {json.dumps(diagnosis, indent=2)}")
    elif args.service:
        doctor.run()
    else:
        print("Doctor Service - System Health Monitoring")
        print("Commands:")
        print("  --service     : Run as API service")
        print("  --diagnosis   : Run system diagnosis")

if __name__ == "__main__":
    main()