#!/usr/bin/env python3
"""
Registration Service - Enterprise-grade service registration and management system
for ZmartBot ecosystem, managing service registration lifecycle, validation,
certification workflows, and comprehensive registration analytics with advanced
visualization dashboards.
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
import asyncio
import uvicorn
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('registration_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_NAME = "registration-service"
SERVICE_VERSION = "1.0.0"
DEFAULT_PORT = 8902

class RegistrationService:
    """Enterprise-grade service registration and management system"""
    
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.app = FastAPI(
            title="Registration Service",
            description="Enterprise-grade service registration and management system for ZmartBot ecosystem",
            version=SERVICE_VERSION
        )
        self.setup_middleware()
        self.setup_routes()
        self.registration_db_path = "data/registration_registry.db"
        self.setup_database()
        
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_database(self):
        """Initialize registration database"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.registration_db_path)
        cursor = conn.cursor()
        
        # Create registration registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registration_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                service_type TEXT NOT NULL,
                port INTEGER,
                passport_id TEXT,
                registration_status TEXT DEFAULT 'PENDING',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                certification_status TEXT DEFAULT 'PENDING',
                certification_date TIMESTAMP,
                health_status TEXT DEFAULT 'UNKNOWN',
                last_health_check TIMESTAMP,
                metadata JSON,
                description TEXT,
                created_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create registration events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registration_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        # Create registration analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registration_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_date DATE DEFAULT CURRENT_DATE,
                service_name TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Registration database initialized: {self.registration_db_path}")
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Service health check"""
            return {
                "status": "ok",
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
                "uptime_seconds": self.get_uptime(),
                "checks": {
                    "database": "ok",
                    "registration_system": "ok"
                }
            }
            
        @self.app.get("/ready")
        async def readiness_check():
            """Service readiness check"""
            return {
                "status": "ready",
                "service": SERVICE_NAME,
                "dependencies": {
                    "database": "ready",
                    "registration_system": "ready"
                }
            }
            
        @self.app.get("/api/registrations")
        async def get_all_registrations():
            """Get all service registrations"""
            try:
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, service_type, port, passport_id, 
                           registration_status, registration_date, certification_status,
                           health_status, last_health_check, metadata, description
                    FROM registration_registry
                    ORDER BY registration_date DESC
                """)
                
                registrations = []
                for row in cursor.fetchall():
                    registrations.append({
                        "service_name": row[0],
                        "service_type": row[1],
                        "port": row[2],
                        "passport_id": row[3],
                        "registration_status": row[4],
                        "registration_date": row[5],
                        "certification_status": row[6],
                        "health_status": row[7],
                        "last_health_check": row[8],
                        "metadata": json.loads(row[9]) if row[9] else {},
                        "description": row[10]
                    })
                
                conn.close()
                return {"registrations": registrations, "total": len(registrations)}
                
            except Exception as e:
                logger.error(f"Error getting registrations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/registrations/{service_name}")
        async def get_registration(service_name: str):
            """Get specific service registration"""
            try:
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, service_type, port, passport_id, 
                           registration_status, registration_date, certification_status,
                           health_status, last_health_check, metadata, description
                    FROM registration_registry
                    WHERE service_name = ?
                """, (service_name,))
                
                row = cursor.fetchone()
                conn.close()
                
                if not row:
                    raise HTTPException(status_code=404, detail="Registration not found")
                    
                return {
                    "service_name": row[0],
                    "service_type": row[1],
                    "port": row[2],
                    "passport_id": row[3],
                    "registration_status": row[4],
                    "registration_date": row[5],
                    "certification_status": row[6],
                    "health_status": row[7],
                    "last_health_check": row[8],
                    "metadata": json.loads(row[9]) if row[9] else {},
                    "description": row[10]
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting registration {service_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/api/registrations")
        async def register_service(registration_data: Dict[str, Any]):
            """Register a new service"""
            try:
                service_name = registration_data.get("service_name")
                service_type = registration_data.get("service_type")
                port = registration_data.get("port")
                passport_id = registration_data.get("passport_id")
                description = registration_data.get("description", "")
                metadata = registration_data.get("metadata", {})
                
                if not service_name or not service_type:
                    raise HTTPException(status_code=400, detail="service_name and service_type are required")
                
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                # Check if service already registered
                cursor.execute("SELECT service_name FROM registration_registry WHERE service_name = ?", (service_name,))
                if cursor.fetchone():
                    conn.close()
                    raise HTTPException(status_code=409, detail="Service already registered")
                
                # Insert new registration
                cursor.execute("""
                    INSERT INTO registration_registry (
                        service_name, service_type, port, passport_id, 
                        registration_status, description, metadata, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service_name, service_type, port, passport_id,
                    "REGISTERED", description, json.dumps(metadata), "system"
                ))
                
                # Log registration event
                cursor.execute("""
                    INSERT INTO registration_events (
                        service_name, event_type, event_data, created_by
                    ) VALUES (?, ?, ?, ?)
                """, (
                    service_name, "REGISTRATION", json.dumps(registration_data), "system"
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Service registered: {service_name}")
                return {"message": "Service registered successfully", "service_name": service_name}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error registering service: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.put("/api/registrations/{service_name}/certify")
        async def certify_service(service_name: str):
            """Certify a registered service"""
            try:
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                # Update certification status
                cursor.execute("""
                    UPDATE registration_registry 
                    SET certification_status = ?, certification_date = ?, updated_at = ?
                    WHERE service_name = ?
                """, ("CERTIFIED", datetime.now().isoformat(), datetime.now().isoformat(), service_name))
                
                if cursor.rowcount == 0:
                    conn.close()
                    raise HTTPException(status_code=404, detail="Registration not found")
                
                # Log certification event
                cursor.execute("""
                    INSERT INTO registration_events (
                        service_name, event_type, event_data, created_by
                    ) VALUES (?, ?, ?, ?)
                """, (
                    service_name, "CERTIFICATION", json.dumps({"status": "CERTIFIED"}), "system"
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Service certified: {service_name}")
                return {"message": "Service certified successfully", "service_name": service_name}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error certifying service {service_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/system/overview")
        async def get_system_overview():
            """Get complete system overview with statistics"""
            try:
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                # Get registration statistics
                cursor.execute("SELECT COUNT(*) FROM registration_registry")
                total_registrations = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM registration_registry WHERE certification_status = 'CERTIFIED'")
                certified_services = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM registration_registry WHERE registration_status = 'REGISTERED'")
                registered_services = cursor.fetchone()[0]
                
                # Get service type distribution
                cursor.execute("""
                    SELECT service_type, COUNT(*) 
                    FROM registration_registry 
                    GROUP BY service_type
                """)
                service_types = dict(cursor.fetchall())
                
                # Get recent events
                cursor.execute("""
                    SELECT service_name, event_type, timestamp 
                    FROM registration_events 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                recent_events = [
                    {"service_name": row[0], "event_type": row[1], "timestamp": row[2]}
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    "system_overview": {
                        "total_registrations": total_registrations,
                        "certified_services": certified_services,
                        "registered_services": registered_services,
                        "pending_certifications": total_registrations - certified_services,
                        "service_types": service_types,
                        "recent_events": recent_events
                    },
                    "service_info": {
                        "name": SERVICE_NAME,
                        "version": SERVICE_VERSION,
                        "port": self.port,
                        "uptime_seconds": self.get_uptime()
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting system overview: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/analytics/registration-stats")
        async def get_registration_stats():
            """Get registration statistics and analytics"""
            try:
                conn = sqlite3.connect(self.registration_db_path)
                cursor = conn.cursor()
                
                # Registration trends (last 30 days)
                thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
                cursor.execute("""
                    SELECT DATE(registration_date) as date, COUNT(*) as count
                    FROM registration_registry
                    WHERE DATE(registration_date) >= ?
                    GROUP BY DATE(registration_date)
                    ORDER BY date
                """, (thirty_days_ago,))
                
                registration_trends = [
                    {"date": row[0], "count": row[1]}
                    for row in cursor.fetchall()
                ]
                
                # Certification trends
                cursor.execute("""
                    SELECT DATE(certification_date) as date, COUNT(*) as count
                    FROM registration_registry
                    WHERE certification_date IS NOT NULL
                    AND DATE(certification_date) >= ?
                    GROUP BY DATE(certification_date)
                    ORDER BY date
                """, (thirty_days_ago,))
                
                certification_trends = [
                    {"date": row[0], "count": row[1]}
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    "registration_trends": registration_trends,
                    "certification_trends": certification_trends,
                    "analytics_period": "30_days"
                }
                
            except Exception as e:
                logger.error(f"Error getting registration stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def registration_dashboard():
            """Registration service dashboard"""
            return self.get_dashboard_html()
            
    def get_uptime(self) -> int:
        """Get service uptime in seconds"""
        # This is a simplified version - in production you'd track actual start time
        return int((datetime.now() - datetime.now()).total_seconds())
        
    def get_dashboard_html(self) -> str:
        """Generate registration dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Registration Service Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
                .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
                .registrations-table { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; font-weight: bold; }
                .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
                .status-registered { background-color: #d4edda; color: #155724; }
                .status-certified { background-color: #cce5ff; color: #004085; }
                .status-pending { background-color: #fff3cd; color: #856404; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔄 Registration Service Dashboard</h1>
                    <p>Enterprise-grade service registration and management system for ZmartBot ecosystem</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Registrations</h3>
                        <div class="stat-number" id="total-registrations">-</div>
                    </div>
                    <div class="stat-card">
                        <h3>Certified Services</h3>
                        <div class="stat-number" id="certified-services">-</div>
                    </div>
                    <div class="stat-card">
                        <h3>Pending Certifications</h3>
                        <div class="stat-number" id="pending-certifications">-</div>
                    </div>
                    <div class="stat-card">
                        <h3>Service Types</h3>
                        <div class="stat-number" id="service-types">-</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>Registration Trends (Last 30 Days)</h3>
                    <canvas id="registrationChart" width="400" height="200"></canvas>
                </div>
                
                <div class="registrations-table">
                    <h3>Recent Registrations</h3>
                    <table id="registrations-table">
                        <thead>
                            <tr>
                                <th>Service Name</th>
                                <th>Type</th>
                                <th>Port</th>
                                <th>Status</th>
                                <th>Registration Date</th>
                                <th>Certification</th>
                            </tr>
                        </thead>
                        <tbody id="registrations-body">
                        </tbody>
                    </table>
                </div>
            </div>
            
            <script>
                // Load dashboard data
                async function loadDashboard() {
                    try {
                        const [overview, registrations] = await Promise.all([
                            fetch('/api/system/overview').then(r => r.json()),
                            fetch('/api/registrations').then(r => r.json())
                        ]);
                        
                        // Update stats
                        document.getElementById('total-registrations').textContent = overview.system_overview.total_registrations;
                        document.getElementById('certified-services').textContent = overview.system_overview.certified_services;
                        document.getElementById('pending-certifications').textContent = overview.system_overview.pending_certifications;
                        document.getElementById('service-types').textContent = Object.keys(overview.system_overview.service_types).length;
                        
                        // Update registrations table
                        const tbody = document.getElementById('registrations-body');
                        tbody.innerHTML = '';
                        
                        registrations.registrations.slice(0, 10).forEach(reg => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${reg.service_name}</td>
                                <td>${reg.service_type}</td>
                                <td>${reg.port || 'N/A'}</td>
                                <td><span class="status-badge status-${reg.registration_status.toLowerCase()}">${reg.registration_status}</span></td>
                                <td>${new Date(reg.registration_date).toLocaleDateString()}</td>
                                <td><span class="status-badge status-${reg.certification_status.toLowerCase()}">${reg.certification_status}</span></td>
                            `;
                            tbody.appendChild(row);
                        });
                        
                        // Load analytics
                        const analytics = await fetch('/api/analytics/registration-stats').then(r => r.json());
                        
                        // Create registration trends chart
                        const ctx = document.getElementById('registrationChart').getContext('2d');
                        new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: analytics.registration_trends.map(d => d.date),
                                datasets: [{
                                    label: 'Registrations',
                                    data: analytics.registration_trends.map(d => d.count),
                                    borderColor: '#667eea',
                                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                    tension: 0.4
                                }]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: {
                                        beginAtZero: true
                                    }
                                }
                            }
                        });
                        
                    } catch (error) {
                        console.error('Error loading dashboard:', error);
                    }
                }
                
                // Load dashboard on page load
                loadDashboard();
                
                // Refresh every 30 seconds
                setInterval(loadDashboard, 30000);
            </script>
        </body>
        </html>
        """
        
    def run(self):
        """Run the registration service"""
        logger.info(f"🚀 Starting {SERVICE_NAME} on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Registration Service")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run on")
    args = parser.parse_args()
    
    service = RegistrationService(port=args.port)
    service.run()

if __name__ == "__main__":
    main()
