#!/usr/bin/env python3
"""
YAML Governance Service - Integrated with ZmartBot Orchestration
Created: 2025-08-31
Purpose: Prevent YAML duplication and chaos, ensure governance compliance
Level: 2 (Production Ready)
Port: 8896 (Backup Instance)
Passport: YAML-GOVERNANCE-BACKUP-8896-L2
Owner: zmartbot-system
Status: STANDBY
"""

import os
import sys
import time
import json
import glob
import yaml
import hashlib
import sqlite3
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify, request
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YAMLGovernanceService:
    """Centralized YAML governance service integrated with orchestration"""
    
    def __init__(self, port=8897):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.governance_db = self.root_dir / ".yaml-governance" / "governance.db"
        self.running = True
        
        # Ensure governance directory exists
        self.governance_db.parent.mkdir(exist_ok=True)
        
        # Setup database
        self.setup_database()
        
        # Setup Flask routes
        self.setup_routes()
        
    def setup_database(self):
        """Setup governance database"""
        conn = sqlite3.connect(self.governance_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yaml_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                service_name TEXT,
                content_hash TEXT,
                port INTEGER,
                service_type TEXT,
                last_validated TIMESTAMP,
                status TEXT DEFAULT 'valid',
                issues TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS governance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                severity TEXT,
                file_path TEXT,
                description TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "yaml-governance",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/validate')
        def validate_all():
            """Validate all YAML files"""
            try:
                results = self.scan_and_validate_all()
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/scan')
        def scan_yamls():
            """Scan for YAML files"""
            try:
                yaml_files = self.scan_yaml_files()
                return jsonify({
                    "total_files": len(yaml_files),
                    "files": [{"path": f.get("path"), "service_name": f.get("service_name")} for f in yaml_files]
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/duplicates')
        def check_duplicates():
            """Check for duplicate YAML files"""
            try:
                duplicates = self.detect_duplicates()
                return jsonify({
                    "duplicates_found": len(duplicates) > 0,
                    "duplicate_count": len(duplicates),
                    "duplicates": duplicates
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/status')
        def governance_status():
            """Get overall governance status"""
            try:
                status = self.get_governance_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
    def scan_yaml_files(self) -> List[Dict]:
        """Scan all service.yaml files"""
        yaml_files = []
        
        for yaml_path in glob.glob("**/service.yaml", recursive=True):
            if "node_modules" in yaml_path or ".git" in yaml_path:
                continue
                
            try:
                with open(yaml_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if content:
                    service_name = content.get('service_name', 'unknown')
                    content_hash = hashlib.md5(yaml.dump(content, sort_keys=True).encode()).hexdigest()
                    
                    yaml_files.append({
                        "path": yaml_path,
                        "service_name": service_name,
                        "content_hash": content_hash,
                        "port": content.get('port'),
                        "service_type": content.get('service_type', 'unknown'),
                        "content": content
                    })
                    
            except Exception as e:
                logger.error(f"Error reading {yaml_path}: {e}")
                
        return yaml_files
    
    def detect_duplicates(self) -> Dict:
        """Detect duplicate YAML files"""
        yaml_files = self.scan_yaml_files()
        duplicates = {}
        
        # Group by service name
        by_name = {}
        for yaml_file in yaml_files:
            name = yaml_file["service_name"]
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(yaml_file)
        
        # Find duplicates
        for name, files in by_name.items():
            if len(files) > 1:
                duplicates[name] = [f["path"] for f in files]
                
        return duplicates
    
    def detect_port_conflicts(self) -> Dict:
        """Detect port conflicts"""
        yaml_files = self.scan_yaml_files()
        by_port = {}
        
        for yaml_file in yaml_files:
            port = yaml_file.get("port")
            if port:
                if port not in by_port:
                    by_port[port] = []
                by_port[port].append(yaml_file["path"])
        
        return {port: paths for port, paths in by_port.items() if len(paths) > 1}
    
    def scan_and_validate_all(self) -> Dict:
        """Complete scan and validation"""
        yaml_files = self.scan_yaml_files()
        duplicates = self.detect_duplicates()
        port_conflicts = self.detect_port_conflicts()
        
        # Update database
        self.update_database(yaml_files)
        
        # Log events
        if duplicates:
            self.log_event("DUPLICATES_DETECTED", "HIGH", 
                         f"Found {len(duplicates)} duplicate services")
        
        if port_conflicts:
            self.log_event("PORT_CONFLICTS", "CRITICAL", 
                         f"Found {len(port_conflicts)} port conflicts")
        
        status = "PASSED" if not duplicates and not port_conflicts else "FAILED"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "total_yaml_files": len(yaml_files),
            "duplicates": duplicates,
            "port_conflicts": port_conflicts,
            "services": len(set(f["service_name"] for f in yaml_files if f["service_name"] != "unknown"))
        }
    
    def update_database(self, yaml_files: List[Dict]):
        """Update governance database with current YAML files"""
        conn = sqlite3.connect(self.governance_db)
        cursor = conn.cursor()
        
        # Clear existing entries
        cursor.execute("DELETE FROM yaml_files")
        
        # Insert current files
        for yaml_file in yaml_files:
            cursor.execute("""
                INSERT INTO yaml_files 
                (file_path, service_name, content_hash, port, service_type, last_validated, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                yaml_file["path"],
                yaml_file["service_name"],
                yaml_file["content_hash"],
                yaml_file.get("port"),
                yaml_file["service_type"],
                datetime.now().isoformat(),
                "valid"
            ))
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type: str, severity: str, description: str, file_path: str = None):
        """Log governance event"""
        conn = sqlite3.connect(self.governance_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO governance_events (event_type, severity, file_path, description)
            VALUES (?, ?, ?, ?)
        """, (event_type, severity, file_path, description))
        
        conn.commit()
        conn.close()
        
        logger.info(f"[{severity}] {event_type}: {description}")
    
    def get_governance_status(self) -> Dict:
        """Get overall governance status"""
        try:
            results = self.scan_and_validate_all()
            
            conn = sqlite3.connect(self.governance_db)
            cursor = conn.cursor()
            
            # Get recent events
            cursor.execute("""
                SELECT event_type, severity, COUNT(*) as count
                FROM governance_events 
                WHERE datetime(created_at) > datetime('now', '-1 hour')
                GROUP BY event_type, severity
            """)
            recent_events = cursor.fetchall()
            
            conn.close()
            
            return {
                "overall_status": results["status"],
                "total_yaml_files": results["total_yaml_files"],
                "duplicates_count": len(results["duplicates"]),
                "port_conflicts_count": len(results["port_conflicts"]),
                "services_count": results["services"],
                "recent_events": [{"type": e[0], "severity": e[1], "count": e[2]} for e in recent_events],
                "last_scan": results["timestamp"]
            }
        except Exception as e:
            return {"error": str(e), "status": "ERROR"}
    
    def start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitor():
            while self.running:
                try:
                    # Run validation every 5 minutes
                    self.scan_and_validate_all()
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("Started YAML governance monitoring thread")
    
    def run(self):
        """Run the governance service"""
        logger.info(f"Starting YAML Governance Service on port {self.port}")
        
        # Start monitoring
        self.start_monitoring_thread()
        
        # Initial validation
        logger.info("Running initial YAML validation...")
        results = self.scan_and_validate_all()
        logger.info(f"Initial scan complete: {results['status']} - {results['total_yaml_files']} files")
        
        # Start Flask app
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("YAML Governance Service stopped")
            self.running = False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YAML Governance Service")
    parser.add_argument('--port', type=int, default=8897, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    
    args = parser.parse_args()
    
    if args.service:
        service = YAMLGovernanceService(port=args.port)
        service.run()
    else:
        print("Use --service flag to start the governance service")
        print(f"Example: python3 yaml_governance_service.py --service --port {args.port}")

if __name__ == "__main__":
    main()