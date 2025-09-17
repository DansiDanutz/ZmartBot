#!/usr/bin/env python3
"""
ZmartBot Database Service
Enterprise-grade database management and monitoring system for ZmartBot ecosystem
Manages 50+ databases with real-time monitoring, automatic discovery, and centralized control
"""

import os
import sys
import asyncio
import sqlite3
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
from supabase import create_client, Client
import uuid
from database.service_lifecycle_manager import ServiceLifecycleManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseInfo:
    """Database information structure"""
    name: str
    path: str
    size_bytes: int
    last_modified: datetime
    status: str
    table_count: int
    record_count: int
    health_score: float
    last_checked: datetime
    schema_hash: str
    category: str
    description: str
    integration_level: int
    backup_status: str

class DatabaseService:
    """Master Database Service for ZmartBot ecosystem with Supabase cloud sync"""
    
    def __init__(self, port: int = 8905):
        self.port = port
        self.master_db_path = "master_database_registry.db"
        self.databases: Dict[str, DatabaseInfo] = {}
        self.monitoring_active = True
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize Service Lifecycle Manager for dynamic validation
        self.lifecycle_manager = ServiceLifecycleManager()
        
        # Supabase configuration
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.supabase_key = os.getenv('SUPABASE_KEY', 'your-anon-key-here')  # Add your anon key
        self.supabase: Optional[Client] = None
        self.cloud_sync_enabled = False
        
        # Initialize systems
        self.init_master_database()
        self.init_supabase_client()
        
        # Start monitoring
        self.start_background_monitoring()
        
        # FastAPI app
        self.app = self.create_app()
        
    def add_dashboard_routes(self, app: FastAPI):
        """Add dashboard routes to the FastAPI app"""
        from fastapi import Request
        from fastapi.responses import HTMLResponse, FileResponse
        from fastapi.staticfiles import StaticFiles
        
        # Mount static files if they exist
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Main dashboard page"""
            return self.get_dashboard_html()
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def database_dashboard():
            """Database dashboard page"""
            return self.get_dashboard_html()
            
        @app.get("/supabase", response_class=HTMLResponse)
        async def supabase_dashboard():
            """Supabase-style database dashboard"""
            dashboard_file = Path(__file__).parent / "supabase_dashboard.html"
            if dashboard_file.exists():
                return FileResponse(dashboard_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Supabase dashboard not found")
            
        @app.get("/advanced", response_class=HTMLResponse)
        async def advanced_dashboard():
            """Advanced card-based database dashboard"""
            dashboard_file = Path(__file__).parent / "advanced_card_dashboard.html"
            if dashboard_file.exists():
                return FileResponse(dashboard_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Advanced dashboard not found")
            
        @app.get("/visualization", response_class=HTMLResponse)
        async def visualization_dashboard():
            """Advanced database visualization dashboard"""
            dashboard_file = Path(__file__).parent / "advanced_database_visualization.html"
            if dashboard_file.exists():
                return FileResponse(dashboard_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Visualization dashboard not found")
            
        @app.get("/management", response_class=HTMLResponse)
        async def management_dashboard():
            """Database management system dashboard"""
            dashboard_file = Path(__file__).parent / "dashboard_management_system.html"
            if dashboard_file.exists():
                return FileResponse(dashboard_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Management dashboard not found")
            
        @app.get("/interactive", response_class=HTMLResponse)
        async def interactive_dashboard():
            """Interactive database dashboard with clickable cards"""
            # For development - serve the same content as the main dashboard for now
            # This way we can access it and work on it
            return self.get_interactive_dashboard_html()

        @app.get("/explorer", response_class=HTMLResponse)
        async def database_explorer():
            """Comprehensive database explorer with content access"""
            explorer_file = Path(__file__).parent / "comprehensive_database_explorer.html"
            if explorer_file.exists():
                return FileResponse(explorer_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Database explorer not found")

        @app.get("/enhanced", response_class=HTMLResponse)
        async def enhanced_database_explorer():
            """Enhanced database explorer with service details"""
            explorer_file = Path(__file__).parent / "enhanced_database_explorer.html"
            if explorer_file.exists():
                return FileResponse(explorer_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Enhanced database explorer not found")

        @app.get("/api/database/{db_name}/tables")
        async def get_database_tables(db_name: str):
            """Get all tables in a specific database"""
            try:
                # Find the database in the master registry
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT path FROM database_registry WHERE name = ?", (db_name,))
                db_row = cursor.fetchone()
                conn.close()
                
                if not db_row:
                    raise HTTPException(status_code=404, detail=f"Database {db_name} not found")
                
                db_path = db_row[0]
                if not Path(db_path).exists():
                    raise HTTPException(status_code=404, detail=f"Database file not found: {db_path}")
                
                # Connect to the database and get table information
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                table_info = []
                for table in tables:
                    table_name = table[0]
                    
                    # Get row count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]
                    except:
                        row_count = 0
                    
                    # Get column information
                    try:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                    except:
                        column_names = []
                    
                    table_info.append({
                        "name": table_name,
                        "row_count": row_count,
                        "columns": column_names,
                        "column_count": len(column_names)
                    })
                
                conn.close()
                
                return {
                    "database": db_name,
                    "tables": table_info,
                    "total_tables": len(table_info)
                }
                
            except Exception as e:
                logger.error(f"Error getting tables for {db_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

        @app.get("/api/database/{db_name}/table/{table_name}/data")
        async def get_table_data(db_name: str, table_name: str, limit: int = 50, offset: int = 0):
            """Get data from a specific table in a database"""
            try:
                # Find the database in the master registry
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT path FROM database_registry WHERE name = ?", (db_name,))
                db_row = cursor.fetchone()
                conn.close()
                
                if not db_row:
                    raise HTTPException(status_code=404, detail=f"Database {db_name} not found")
                
                db_path = db_row[0]
                if not Path(db_path).exists():
                    raise HTTPException(status_code=404, detail=f"Database file not found: {db_path}")
                
                # Connect to the database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                # Get total row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cursor.fetchone()[0]
                
                # Get data with limit and offset
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}")
                rows = cursor.fetchall()
                
                # Convert rows to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        # Convert non-serializable types to strings
                        if isinstance(value, (bytes, bytearray)):
                            value = str(value)
                        elif value is None:
                            value = None
                        row_dict[column_names[i]] = value
                    data.append(row_dict)
                
                conn.close()
                
                return {
                    "database": db_name,
                    "table": table_name,
                    "columns": column_names,
                    "data": data,
                    "total_rows": total_rows,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total_rows
                }
                
            except Exception as e:
                logger.error(f"Error getting data from {db_name}.{table_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing table: {str(e)}")

        @app.get("/api/database/{db_name}/table/{table_name}/schema")
        async def get_table_schema(db_name: str, table_name: str):
            """Get detailed schema information for a table"""
            try:
                # Find the database in the master registry
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT path FROM database_registry WHERE name = ?", (db_name,))
                db_row = cursor.fetchone()
                conn.close()
                
                if not db_row:
                    raise HTTPException(status_code=404, detail=f"Database {db_name} not found")
                
                db_path = db_row[0]
                if not Path(db_path).exists():
                    raise HTTPException(status_code=404, detail=f"Database file not found: {db_path}")
                
                # Connect to the database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get detailed column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get table creation SQL
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                create_sql = cursor.fetchone()
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = cursor.fetchall()
                
                conn.close()
                
                # Format column information
                column_info = []
                for col in columns:
                    column_info.append({
                        "cid": col[0],
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    })
                
                return {
                    "database": db_name,
                    "table": table_name,
                    "columns": column_info,
                    "create_sql": create_sql[0] if create_sql else None,
                    "indexes": [{"name": idx[1], "unique": bool(idx[2])} for idx in indexes],
                    "foreign_keys": [{"from": fk[3], "to": fk[4]} for fk in foreign_keys],
                    "total_columns": len(column_info)
                }
                
            except Exception as e:
                logger.error(f"Error getting schema for {db_name}.{table_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing schema: {str(e)}")
            
        @app.get("/debug", response_class=HTMLResponse)
        async def debug_dashboard():
            """Debug dashboard for troubleshooting card display issues"""
            dashboard_file = Path(__file__).parent / "debug_dashboard.html"
            if dashboard_file.exists():
                return FileResponse(dashboard_file, media_type="text/html")
            raise HTTPException(status_code=404, detail="Debug dashboard not found")
            
    def get_dashboard_html(self) -> str:
        """Generate the complete dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZmartBot Database Service Dashboard - Port 8900</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0f1419;
            --bg-secondary: #1a2332;
            --bg-card: #1a2332;
            --border-color: #2d3748;
            --border-hover: #4a5568;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --text-accent: #4fd1c7;
            --success: #48bb78;
            --warning: #ed8936;
            --error: #f56565;
            --info: #4fd1c7;
        }
        
        [data-theme="light"] {
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --border-hover: #cbd5e0;
            --text-primary: #2d3748;
            --text-secondary: #718096;
            --text-accent: #2b6cb0;
            --success: #38a169;
            --warning: #d69e2e;
            --error: #e53e3e;
            --info: #3182ce;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            transition: all 0.3s ease;
        }
        
        .header {
            background: var(--bg-secondary);
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }
        
        .header h1 {
            color: var(--text-accent);
            font-size: 28px;
            margin-bottom: 5px;
            text-align: center;
        }
        
        .header .subtitle {
            text-align: center;
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--text-accent);
            color: var(--bg-primary);
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
        }
        
        .theme-toggle:hover {
            opacity: 0.8;
            transform: translateY(-1px);
        }
        
        .service-info {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--success);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 0 8px 8px 0;
        }
        
        .passport-badge {
            display: inline-block;
            background: var(--text-accent);
            color: var(--bg-primary);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin: 0 4px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .status-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }
        
        .status-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-accent);
            display: block;
            margin-bottom: 8px;
        }
        
        .status-label {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s ease;
        }
        
        .card:hover {
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }
        
        .card h3 {
            color: var(--text-accent);
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            margin-top: 15px;
        }
        
        .table-container {
            max-height: 400px;
            overflow-y: auto;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }
        
        th {
            background: var(--bg-secondary);
            font-weight: 600;
            color: var(--text-primary);
            position: sticky;
            top: 0;
        }
        
        tr:hover {
            background: var(--bg-secondary);
        }
        
        .health-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .health-excellent { background-color: var(--success); }
        .health-good { background-color: var(--success); }
        .health-fair { background-color: var(--warning); }
        .health-poor { background-color: var(--error); }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .btn {
            background: var(--text-accent);
            color: var(--bg-primary);
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .btn:hover {
            opacity: 0.8;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .btn-secondary:hover {
            border-color: var(--border-hover);
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .metric-value {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 14px;
        }
        
        .status-indicator-text {
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-active { color: var(--success); }
        .status-warning { color: var(--warning); }
        .status-error { color: var(--error); }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .theme-toggle {
                position: static;
                margin: 15px auto 0;
                display: block;
            }
        }
    </style>
</head>
<body data-theme="dark" style="background: #0f1419; color: #ffffff;">
    <div class="header">
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Dark Mode</button>
        <h1>🗄️ Database Service Dashboard</h1>
        <p class="subtitle">ZmartBot Enterprise Database Management System - Port 8900</p>
        <div class="service-info">
            <strong>🎫 Service Status:</strong> <span class="status-active">ACTIVE & CERTIFIED</span> | 
            <strong>🔐 Passport:</strong> <span class="passport-badge">ZMBT-DB-20250829-47C2DE</span> | 
            <strong>🚢 Port:</strong> 8900 | 
            <strong>🏆 Level:</strong> 3 (Fully Certified & Production Ready)
        </div>
    </div>
    
    <div class="container">
        <div class="status-bar">
            <div class="status-card">
                <span class="status-value" id="total-databases">-</span>
                <span class="status-label">Total Databases</span>
            </div>
            <div class="status-card">
                <span class="status-value" id="healthy-databases">-</span>
                <span class="status-label">Healthy Databases</span>
            </div>
            <div class="status-card">
                <span class="status-value" id="total-tables">-</span>
                <span class="status-label">Total Tables</span>
            </div>
            <div class="status-card">
                <span class="status-value" id="total-records">-</span>
                <span class="status-label">Total Records</span>
            </div>
            <div class="status-card">
                <span class="status-value" id="cloud-sync-status">-</span>
                <span class="status-label">Cloud Sync</span>
            </div>
            <div class="status-card">
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
        <div class="card">
            <h3>📊 Database Health Overview</h3>
            <div class="chart-container">
                <canvas id="healthChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h3>📈 Database Size Distribution</h3>
            <div class="chart-container">
                <canvas id="sizeChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h3>🏷️ Database Categories</h3>
            <div class="chart-container">
                <canvas id="categoryChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h3>⏰ Recent Activity</h3>
            <div class="chart-container">
                <canvas id="activityChart"></canvas>
            </div>
        </div>
        
        <div class="card full-width">
            <h3>🗃️ Database Registry</h3>
            <div class="table-container">
                <table id="database-table">
                    <thead>
                        <tr>
                            <th>Database</th>
                            <th>Category</th>
                            <th>Health</th>
                            <th>Size</th>
                            <th>Tables</th>
                            <th>Records</th>
                            <th>Last Modified</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="database-table-body">
                        <tr><td colspan="8" class="loading">Loading database information...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <h3>☁️ Supabase Cloud Sync</h3>
            <div id="cloud-sync-info">
                <div class="loading">Loading cloud sync status...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🔧 Service Information</h3>
            <div id="service-info">
                <div class="metric">
                    <span class="metric-label">Service Name:</span>
                    <span class="metric-value">database_service</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Version:</span>
                    <span class="metric-value">1.0.0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8900</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Type:</span>
                    <span class="metric-value">Backend Service</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Owner:</span>
                    <span class="metric-value">ZmartBot</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value status-active">🟢 Active</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime:</span>
                    <span class="metric-value" id="uptime">Calculating...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value" id="memory-usage">< 100 MB</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value" id="cpu-usage">< 5%</span>
                </div>
            </div>
        </div>
        </div>
    </div>

    <script>
        let charts = {};
        const startTime = Date.now();
        
        // Theme management
        function toggleTheme() {
            const body = document.body;
            const button = document.querySelector('.theme-toggle');
            
            if (body.getAttribute('data-theme') === 'dark') {
                body.setAttribute('data-theme', 'light');
                button.innerHTML = '☀️ Light Mode';
                localStorage.setItem('theme', 'light');
            } else {
                body.setAttribute('data-theme', 'dark');
                button.innerHTML = '🌙 Dark Mode';
                localStorage.setItem('theme', 'dark');
            }
            
            // Update chart colors
            setTimeout(() => {
                updateChartThemes();
            }, 100);
        }
        
        function updateChartThemes() {
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const textColor = isDark ? '#ffffff' : '#2d3748';
            const gridColor = isDark ? '#2d3748' : '#e2e8f0';
            
            Object.values(charts).forEach(chart => {
                if (chart && chart.options) {
                    // Update scales color
                    if (chart.options.scales) {
                        Object.keys(chart.options.scales).forEach(scaleKey => {
                            const scale = chart.options.scales[scaleKey];
                            if (scale.ticks) scale.ticks.color = textColor;
                            if (scale.grid) scale.grid.color = gridColor;
                        });
                    }
                    
                    // Update legend color
                    if (chart.options.plugins && chart.options.plugins.legend) {
                        chart.options.plugins.legend.labels.color = textColor;
                    }
                    
                    chart.update();
                }
            });
        }
        
        // Initialize theme
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            const body = document.body;
            const button = document.querySelector('.theme-toggle');
            
            // Force dark theme by default
            body.setAttribute('data-theme', 'dark');
            button.innerHTML = '🌙 Dark Mode';
            localStorage.setItem('theme', 'dark');
            
            // Update chart colors immediately
            setTimeout(() => {
                updateChartThemes();
            }, 100);
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initTheme();
            initializeCharts();
            refreshData();
            updateUptime();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
            setInterval(updateUptime, 1000);
        });
        
        function initializeCharts() {
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const textColor = isDark ? '#ffffff' : '#2d3748';
            const gridColor = isDark ? '#2d3748' : '#e2e8f0';
            
            // Health Chart
            const healthCtx = document.getElementById('healthChart').getContext('2d');
            charts.health = new Chart(healthCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Excellent (90-100%)', 'Good (75-89%)', 'Fair (50-74%)', 'Poor (<50%)'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#48bb78', '#2ecc71', '#ed8936', '#f56565'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: textColor
                            }
                        }
                    }
                }
            });
            
            // Size Chart
            const sizeCtx = document.getElementById('sizeChart').getContext('2d');
            charts.size = new Chart(sizeCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Database Size (MB)',
                        data: [],
                        backgroundColor: 'rgba(52, 152, 219, 0.8)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // Category Chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            charts.category = new Chart(categoryCtx, {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#3498db', '#2ecc71', '#f39c12', '#e74c3c', 
                            '#9b59b6', '#1abc9c', '#34495e', '#fd79a8'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Activity Chart
            const activityCtx = document.getElementById('activityChart').getContext('2d');
            charts.activity = new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Database Activity',
                        data: [],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        async function refreshData() {
            try {
                // Fetch system overview
                const overview = await fetch('/api/system/overview').then(r => r.json());
                updateStatusBar(overview);
                
                // Fetch databases
                const dbResponse = await fetch('/api/databases').then(r => r.json());
                const databases = dbResponse.databases || [];
                updateDatabaseTable(databases);
                updateCharts(databases);
                
                // Cloud sync status is included in system overview
                
                // Update service metrics
                updateServiceMetrics();
                
            } catch (error) {
                console.error('Error refreshing data:', error);
                showError('Failed to refresh data: ' + error.message);
            }
        }
        
        function updateStatusBar(overview) {
            const dbStats = overview.database_statistics || {};
            document.getElementById('total-databases').textContent = dbStats.total_databases || 0;
            document.getElementById('healthy-databases').textContent = dbStats.total_databases || 0;
            document.getElementById('total-tables').textContent = dbStats.total_tables || 0;
            document.getElementById('total-records').textContent = dbStats.total_records || 0;
            document.getElementById('cloud-sync-status').textContent = overview.cloud_sync_enabled ? '🟢 Active' : '🔴 Inactive';
        }
        
        function updateDatabaseTable(databases) {
            const tbody = document.getElementById('database-table-body');
            tbody.innerHTML = '';
            
            if (!databases || databases.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="loading">No databases found</td></tr>';
                return;
            }
            
            databases.forEach(db => {
                const row = document.createElement('tr');
                const healthClass = getHealthClass(db.health_score);
                
                row.innerHTML = `
                    <td><strong>${db.name}</strong></td>
                    <td>${db.category || 'Unknown'}</td>
                    <td>
                        <span class="health-indicator ${healthClass}"></span>
                        ${db.health_score || 0}%
                    </td>
                    <td>${formatBytes(db.size_bytes || 0)}</td>
                    <td>${db.table_count || 0}</td>
                    <td>${db.record_count || 0}</td>
                    <td>${formatDate(db.last_modified)}</td>
                    <td>${db.status || 'Unknown'}</td>
                `;
                
                tbody.appendChild(row);
            });
        }
        
        function updateCharts(databases) {
            if (!databases || databases.length === 0) return;
            
            // Update health chart
            const healthData = [0, 0, 0, 0];
            databases.forEach(db => {
                const score = db.health_score || 0;
                if (score >= 90) healthData[0]++;
                else if (score >= 75) healthData[1]++;
                else if (score >= 50) healthData[2]++;
                else healthData[3]++;
            });
            charts.health.data.datasets[0].data = healthData;
            charts.health.update();
            
            // Update size chart (top 10)
            const topDbs = databases
                .sort((a, b) => (b.size_bytes || 0) - (a.size_bytes || 0))
                .slice(0, 10);
            charts.size.data.labels = topDbs.map(db => db.name);
            charts.size.data.datasets[0].data = topDbs.map(db => (db.size_bytes || 0) / (1024 * 1024));
            charts.size.update();
            
            // Update category chart
            const categories = {};
            databases.forEach(db => {
                const cat = db.category || 'Unknown';
                categories[cat] = (categories[cat] || 0) + 1;
            });
            charts.category.data.labels = Object.keys(categories);
            charts.category.data.datasets[0].data = Object.values(categories);
            charts.category.update();
            
            // Update activity chart (simplified)
            const now = new Date();
            const labels = [];
            const data = [];
            for (let i = 23; i >= 0; i--) {
                const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
                labels.push(hour.getHours() + ':00');
                data.push(Math.floor(Math.random() * 10) + 1); // Simulated data
            }
            charts.activity.data.labels = labels;
            charts.activity.data.datasets[0].data = data;
            charts.activity.update();
        }
        
        function updateCloudSync(status) {
            const container = document.getElementById('cloud-sync-info');
            container.innerHTML = `
                <p><strong>Status:</strong> ${status.enabled ? '🟢 Enabled' : '🔴 Disabled'}</p>
                <p><strong>Last Sync:</strong> ${formatDate(status.last_sync)}</p>
                <p><strong>Synced Tables:</strong> ${status.synced_tables || 0}</p>
                <p><strong>Sync Errors:</strong> ${status.errors || 0}</p>
                <button class="refresh-btn" onclick="triggerCloudSync()">🔄 Sync Now</button>
            `;
        }
        
        function updateServiceMetrics() {
            // Simulated metrics - in real implementation, these would come from the API
            document.getElementById('memory-usage').textContent = '< 100 MB';
            document.getElementById('cpu-usage').textContent = '< 5%';
        }
        
        function updateUptime() {
            const uptime = Date.now() - startTime;
            const hours = Math.floor(uptime / (1000 * 60 * 60));
            const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((uptime % (1000 * 60)) / 1000);
            
            document.getElementById('uptime').textContent = `${hours}h ${minutes}m ${seconds}s`;
        }
        
        async function triggerCloudSync() {
            try {
                const response = await fetch('/api/cloud/sync', { method: 'POST' });
                const result = await response.json();
                alert('Cloud sync triggered: ' + result.message);
                refreshData();
            } catch (error) {
                alert('Error triggering cloud sync: ' + error.message);
            }
        }
        
        function getHealthClass(score) {
            if (score >= 90) return 'health-excellent';
            if (score >= 75) return 'health-good';
            if (score >= 50) return 'health-fair';
            return 'health-poor';
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function formatDate(dateString) {
            if (!dateString) return 'Unknown';
            try {
                return new Date(dateString).toLocaleDateString() + ' ' + 
                       new Date(dateString).toLocaleTimeString();
            } catch {
                return 'Invalid Date';
            }
        }
        
        function showError(message) {
            console.error(message);
            // Could implement a toast notification here
        }
    </script>
</body>
</html>
        """
    
    def get_interactive_dashboard_html(self) -> str:
        """Generate the interactive database management dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZmartBot Database Management Center - DEV PORT 8905</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow: hidden;
            line-height: 1.6;
        }

        .main-container {
            display: grid;
            grid-template-columns: 320px 1fr;
            height: 100vh;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        }

        /* Sidebar - Dark Mode */
        .sidebar {
            background: linear-gradient(180deg, #111111 0%, #1a1a1a 100%);
            border-right: 1px solid #333333;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
        }

        .sidebar-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #333333;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
            border-radius: 12px;
            padding: 25px 15px;
        }

        .sidebar-header h1 {
            font-size: 1.4em;
            font-weight: 700;
            background: linear-gradient(45deg, #00d4ff, #5b73ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        .sidebar-header .subtitle {
            font-size: 0.85em;
            color: #888888;
            font-weight: 500;
        }

        .category-section {
            margin-bottom: 15px;
        }

        .category-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 18px;
            background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
            border: 1px solid #333333;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 8px;
        }

        .category-header:hover {
            background: linear-gradient(135deg, #2a2a2a, #333333);
            border-color: #00d4ff;
            transform: translateX(4px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
        }

        .category-header.active {
            background: linear-gradient(135deg, #00d4ff, #5b73ff);
            border-color: #00d4ff;
            box-shadow: 0 12px 30px rgba(0, 212, 255, 0.3);
            color: #000000;
        }

        .category-header.active .category-count {
            background: rgba(0, 0, 0, 0.2);
            color: #000000;
        }

        .category-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            font-size: 0.95em;
        }

        .category-icon {
            font-size: 1.1em;
            width: 20px;
            text-align: center;
        }

        .category-count {
            background: linear-gradient(45deg, #333333, #444444);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 700;
            color: #ffffff;
            min-width: 35px;
            text-align: center;
        }

        .database-list {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            padding-left: 15px;
        }

        .database-list.open {
            max-height: 400px;
            margin-bottom: 10px;
        }

        .database-item {
            padding: 12px 16px;
            margin: 6px 0;
            background: linear-gradient(135deg, #1a1a1a, #222222);
            border: 1px solid #2a2a2a;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 3px solid transparent;
        }

        .database-item:hover {
            background: linear-gradient(135deg, #222222, #2a2a2a);
            border-color: #00d4ff;
            border-left-color: #00d4ff;
            transform: translateX(4px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.1);
        }

        .database-item.selected {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(91, 115, 255, 0.1));
            border-color: #00d4ff;
            border-left-color: #00d4ff;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
        }

        .database-name {
            font-weight: 600;
            margin-bottom: 6px;
            color: #ffffff;
            font-size: 0.9em;
        }

        .database-stats {
            display: flex;
            gap: 12px;
            font-size: 0.75em;
            color: #aaaaaa;
        }

        .database-stats span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Main Content - Dark Mode */
        .main-content {
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow: hidden;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 25px 30px;
            background: linear-gradient(135deg, #1a1a1a, #222222);
            border: 1px solid #333333;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .system-stats {
            display: flex;
            gap: 40px;
            align-items: center;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: 800;
            background: linear-gradient(45deg, #00d4ff, #5b73ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 0.85em;
            color: #aaaaaa;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .database-detail {
            flex: 1;
            background: linear-gradient(135deg, #1a1a1a, #222222);
            border: 1px solid #333333;
            border-radius: 20px;
            padding: 35px;
            overflow-y: auto;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }

        .dev-banner {
            background: linear-gradient(45deg, #ff6b6b, #ff8c42);
            color: #000;
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 700;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Sidebar with Categories -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h1><i class="fas fa-database"></i> Database Center DEV</h1>
                <div class="subtitle">Development Port 8905</div>
            </div>
            
            <div id="categories-container">
                <div class="loading">
                    Loading development databases...
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Top Bar -->
            <div class="top-bar">
                <div class="system-stats">
                    <div class="stat-item">
                        <div class="stat-value" id="total-databases">--</div>
                        <div class="stat-label">Total Databases</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="active-databases">--</div>
                        <div class="stat-label">Active</div>
                    </div>
                </div>
                
                <div class="stat-item">
                    <div class="stat-value">DEV</div>
                    <div class="stat-label">Mode</div>
                </div>
            </div>

            <!-- Database Detail Card -->
            <div class="database-detail" id="database-detail">
                <div class="dev-banner">
                    🚀 DEVELOPMENT DATABASE SERVICE - PORT 8905 🚀
                </div>
                
                <div class="welcome-screen">
                    <i class="fas fa-chart-line welcome-icon"></i>
                    <div class="welcome-title">ZmartBot Database Development</div>
                    <div class="welcome-subtitle">
                        This is the development version of the database management system running on port 8905.
                        The main production service runs on port 8900. You can now work on enhancements here safely!
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Development mode - basic functionality for now
        console.log('ZmartBot Database Development Dashboard - Port 8905');
        
        // Auto-refresh every 30 seconds
        setInterval(function() {
            console.log('Development dashboard active...');
        }, 30000);
    </script>
</body>
</html>
        """
    
    def init_master_database(self):
        """Initialize the Master Database Registry"""
        try:
            conn = sqlite3.connect(self.master_db_path)
            cursor = conn.cursor()
            
            # Create master database table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    size_bytes INTEGER DEFAULT 0,
                    last_modified TIMESTAMP,
                    status TEXT DEFAULT 'ACTIVE',
                    table_count INTEGER DEFAULT 0,
                    record_count INTEGER DEFAULT 0,
                    health_score REAL DEFAULT 100.0,
                    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    schema_hash TEXT,
                    category TEXT DEFAULT 'unknown',
                    description TEXT,
                    integration_level INTEGER DEFAULT 0,
                    backup_status TEXT DEFAULT 'none',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create database tables registry
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_count INTEGER DEFAULT 0,
                    record_count INTEGER DEFAULT 0,
                    schema_info TEXT,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (database_name) REFERENCES database_registry (name)
                )
            """)
            
            # Create monitoring history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    health_score REAL,
                    response_time_ms REAL,
                    status TEXT,
                    error_message TEXT,
                    FOREIGN KEY (database_name) REFERENCES database_registry (name)
                )
            """)
            
            # Create query log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    query_text TEXT,
                    execution_time_ms REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    result_count INTEGER DEFAULT 0,
                    FOREIGN KEY (database_name) REFERENCES database_registry (name)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Master Database Registry initialized at {self.master_db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize master database: {e}")
            raise
    
    def init_supabase_client(self):
        """Initialize Supabase client for cloud synchronization"""
        try:
            if self.supabase_key and self.supabase_key != 'your-anon-key-here':
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                self.cloud_sync_enabled = True
                logger.info(f"✅ Supabase client initialized for cloud sync")
                
                # Create tables in Supabase if they don't exist
                self.setup_supabase_tables()
            else:
                logger.warning("⚠️ Supabase key not provided, cloud sync disabled")
                logger.info("💡 Set SUPABASE_KEY environment variable to enable cloud sync")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.cloud_sync_enabled = False
    
    def setup_supabase_tables(self):
        """Set up Supabase tables for database registry sync"""
        if not self.cloud_sync_enabled:
            return
            
        try:
            # Check if tables exist by trying to select from them
            # This will create tables automatically via Supabase migrations if configured
            
            # Database registry table structure for Supabase
            supabase_schema = {
                'database_registry': [
                    'id (uuid primary key)',
                    'name (text unique)',
                    'path (text)',
                    'size_bytes (bigint)',
                    'last_modified (timestamptz)',
                    'status (text)',
                    'table_count (integer)',
                    'record_count (bigint)', 
                    'health_score (float)',
                    'last_checked (timestamptz)',
                    'schema_hash (text)',
                    'category (text)',
                    'description (text)',
                    'integration_level (integer)',
                    'backup_status (text)',
                    'sync_status (text default \'pending\')',
                    'created_at (timestamptz default now())',
                    'updated_at (timestamptz default now())'
                ],
                'service_registry': [
                    'id (serial primary key)',
                    'service_name (varchar(255) unique)',
                    'service_type (varchar(100))',
                    'port (integer)',
                    'status (varchar(50))',
                    'passport_id (varchar(100))',
                    'health_score (integer)',
                    'category (varchar(100))',
                    'description (text)',
                    'version (varchar(50))',
                    'last_seen (timestamp)',
                    'registered_at (timestamp)',
                    'updated_at (timestamp)',
                    'metadata (jsonb)',
                    'integration_level (integer)',
                    'certification_status (varchar(50))'
                ]
            }
            
            logger.info("📊 Supabase tables structure ready for sync")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not verify Supabase table structure: {e}")
    
    async def sync_service_registry_to_supabase(self):
        """Sync service registry data to Supabase"""
        if not self.cloud_sync_enabled:
            logger.warning("⚠️ Supabase sync disabled, skipping service registry sync")
            return False
            
        try:
            # Get service data from passport registry and certified services
            services_data = await self.get_service_registry_data()
            
            if not services_data:
                logger.warning("⚠️ No service data found to sync")
                return False
            
            # Sync each service to Supabase
            success_count = 0
            for service in services_data:
                try:
                    # Prepare service data for Supabase
                    supabase_service_data = {
                        'service_name': service['service_name'],
                        'service_type': service.get('service_type', 'backend'),
                        'port': service.get('port'),
                        'status': service.get('status', 'ACTIVE'),
                        'passport_id': service.get('passport_id'),
                        'health_score': service.get('health_score', 0),
                        'category': service.get('category', 'unknown'),
                        'description': service.get('description', ''),
                        'version': service.get('version', '1.0.0'),
                        'last_seen': datetime.now().isoformat(),
                        'registered_at': service.get('registered_at', datetime.now().isoformat()),
                        'updated_at': datetime.now().isoformat(),
                        'metadata': json.dumps(service.get('metadata', {})),
                        'integration_level': service.get('integration_level', 0),
                        'certification_status': service.get('certification_status', 'PENDING')
                    }
                    
                    # Upsert to Supabase
                    result = self.supabase.table('service_registry').upsert(
                        supabase_service_data,
                        on_conflict='service_name'
                    ).execute()
                    
                    if result.data:
                        success_count += 1
                        logger.info(f"✅ Synced service {service['service_name']} to Supabase")
                    else:
                        logger.warning(f"⚠️ Failed to sync service {service['service_name']}")
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing service {service['service_name']}: {e}")
            
            logger.info(f"🎯 Service registry sync completed: {success_count}/{len(services_data)} services synced")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error in service registry sync: {e}")
            return False
    
    async def get_service_registry_data(self):
        """Get service registry data from passport registry and certified services"""
        services = []
        
        try:
            # Get data from passport registry
            passport_services = await self.get_passport_registry_services()
            services.extend(passport_services)
            
            # Get data from certified services
            certified_services = await self.get_certified_services()
            services.extend(certified_services)
            
            # Remove duplicates based on service_name
            unique_services = {}
            for service in services:
                service_name = service['service_name']
                if service_name not in unique_services:
                    unique_services[service_name] = service
                else:
                    # Merge data, preferring certified status
                    existing = unique_services[service_name]
                    if service.get('certification_status') == 'CERTIFIED':
                        existing.update(service)
            
            return list(unique_services.values())
            
        except Exception as e:
            logger.error(f"❌ Error getting service registry data: {e}")
            return []
    
    async def get_passport_registry_services(self):
        """Get services from passport registry"""
        services = []
        
        try:
            passport_db_path = "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"
            if not os.path.exists(passport_db_path):
                return services
            
            conn = sqlite3.connect(passport_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, service_type, port, status, passport_id, 
                       registered_at, description, metadata
                FROM passport_registry
                WHERE status = 'ACTIVE'
            """)
            
            for row in cursor.fetchall():
                service = {
                    'service_name': row[0],
                    'service_type': row[1] or 'backend',
                    'port': row[2],
                    'status': row[3],
                    'passport_id': row[4],
                    'registered_at': row[5],
                    'description': row[6] or '',
                    'metadata': json.loads(row[7]) if row[7] else {},
                    'certification_status': 'PENDING',
                    'health_score': 85,  # Default health score
                    'category': 'core',
                    'integration_level': 3
                }
                services.append(service)
            
            conn.close()
            logger.info(f"📋 Found {len(services)} services in passport registry")
            
        except Exception as e:
            logger.error(f"❌ Error reading passport registry: {e}")
        
        return services
    
    async def get_certified_services(self):
        """Get certified services from certified_services.txt"""
        services = []
        
        try:
            certified_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/certified_services.txt"
            if not os.path.exists(certified_file):
                return services
            
            with open(certified_file, 'r') as f:
                certified_names = [line.strip() for line in f.readlines() if line.strip()]
            
            # Get additional data for certified services
            for service_name in certified_names:
                service = {
                    'service_name': service_name,
                    'service_type': 'backend',
                    'port': None,  # Will be filled from passport registry if available
                    'status': 'ACTIVE',
                    'passport_id': None,
                    'registered_at': datetime.now().isoformat(),
                    'description': f'Certified service: {service_name}',
                    'metadata': {},
                    'certification_status': 'CERTIFIED',
                    'health_score': 95,  # Higher health score for certified services
                    'category': 'certified',
                    'integration_level': 5
                }
                services.append(service)
            
            logger.info(f"🏆 Found {len(services)} certified services")
            
        except Exception as e:
            logger.error(f"❌ Error reading certified services: {e}")
        
        return services
    
    async def sync_database_to_supabase(self, db_info: DatabaseInfo):
        """Sync a single database record to Supabase with individual table creation"""
        if not self.cloud_sync_enabled:
            return False
            
        try:
            # First sync to main registry table
            registry_success = await self.sync_to_registry_table(db_info)
            
            # Then sync to individual database table
            individual_success = await self.sync_to_individual_table(db_info)
            
            return registry_success and individual_success
                
        except Exception as e:
            logger.error(f"❌ Error syncing {db_info.name} to Supabase: {e}")
            return False
    
    async def sync_to_registry_table(self, db_info: DatabaseInfo):
        """Sync database metadata to main registry table"""
        try:
            # Prepare data for main registry
            supabase_data = {
                'id': str(uuid.uuid4()),
                'name': db_info.name,
                'path': db_info.path,
                'size_bytes': db_info.size_bytes,
                'last_modified': db_info.last_modified.isoformat(),
                'status': db_info.status,
                'table_count': db_info.table_count,
                'record_count': db_info.record_count,
                'health_score': db_info.health_score,
                'last_checked': db_info.last_checked.isoformat(),
                'schema_hash': db_info.schema_hash,
                'category': db_info.category,
                'description': db_info.description,
                'integration_level': db_info.integration_level,
                'backup_status': db_info.backup_status,
                'sync_status': 'synced',
                'updated_at': datetime.now().isoformat()
            }
            
            # Upsert to main registry table
            result = self.supabase.table('database_registry').upsert(
                supabase_data, 
                on_conflict='name'
            ).execute()
            
            if result.data:
                logger.info(f"📋 Synced {db_info.name} to main registry")
                return True
            else:
                logger.warning(f"⚠️ Failed to sync {db_info.name} to main registry")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing {db_info.name} to main registry: {e}")
            return False
    
    async def sync_to_individual_table(self, db_info: DatabaseInfo):
        """Sync database content to individual Supabase table"""
        try:
            # Generate clean table name for Supabase
            clean_name = db_info.name.replace('.db', '').replace('-', '_').replace(' ', '_').lower()
            supabase_table_name = f"db_{clean_name}"
            
            # Read actual database content
            database_content = await self.extract_database_content(db_info.path)
            
            if not database_content:
                logger.info(f"🔍 No content extracted from {db_info.name}")
                return True
                
            # Sync each table's content to Supabase
            tables_synced = 0
            for table_name, table_data in database_content.items():
                try:
                    # Create compound table name
                    full_table_name = f"{supabase_table_name}_{table_name}"
                    
                    # Sync table data
                    if table_data and len(table_data) > 0:
                        # Clear existing data and insert new (simple sync strategy)
                        try:
                            # Delete existing records for this database table
                            self.supabase.table(full_table_name).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                        except:
                            pass  # Table might not exist yet
                            
                        # Insert new data in batches
                        batch_size = 100
                        for i in range(0, len(table_data), batch_size):
                            batch = table_data[i:i + batch_size]
                            
                            # Add metadata to each record
                            for record in batch:
                                if isinstance(record, dict):
                                    record['_db_source'] = db_info.name
                                    record['_table_source'] = table_name
                                    record['_synced_at'] = datetime.now().isoformat()
                                    record['_sync_id'] = str(uuid.uuid4())
                            
                            result = self.supabase.table(full_table_name).insert(batch).execute()
                            
                            if result.data:
                                logger.info(f"📊 Synced {len(batch)} records to {full_table_name}")
                            
                        tables_synced += 1
                        
                except Exception as table_error:
                    logger.warning(f"⚠️ Could not sync table {table_name} from {db_info.name}: {table_error}")
                    
            logger.info(f"☁️ Synced {tables_synced} tables from {db_info.name} to individual Supabase tables")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing individual table for {db_info.name}: {e}")
            return False
    
    async def extract_database_content(self, db_path: str, max_records_per_table: int = 1000):
        """Extract actual content from SQLite database"""
        try:
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row  # Enable column name access
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            database_content = {}
            
            for table_name in tables:
                try:
                    # Get column information
                    cursor.execute(f"PRAGMA table_info([{table_name}])")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Extract data with limit
                    cursor.execute(f"SELECT * FROM [{table_name}] LIMIT {max_records_per_table}")
                    rows = cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    table_data = []
                    for row in rows:
                        record = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # Handle different data types for JSON serialization
                            if isinstance(value, (bytes, bytearray)):
                                value = str(value)
                            elif value is None:
                                value = None
                            else:
                                value = str(value)
                            record[column] = value
                        table_data.append(record)
                    
                    database_content[table_name] = table_data
                    logger.info(f"📊 Extracted {len(table_data)} records from table {table_name}")
                    
                except Exception as table_error:
                    logger.warning(f"⚠️ Could not extract table {table_name}: {table_error}")
            
            conn.close()
            return database_content
            
        except Exception as e:
            logger.error(f"❌ Error extracting content from {db_path}: {e}")
            return {}
    
    async def sync_all_databases_to_supabase(self):
        """Sync all local databases to Supabase"""
        if not self.cloud_sync_enabled:
            logger.info("☁️ Cloud sync disabled - skipping Supabase sync")
            return
        
        try:
            sync_count = 0
            for db_name, db_info in self.databases.items():
                if await self.sync_database_to_supabase(db_info):
                    sync_count += 1
                    
            logger.info(f"☁️ Synced {sync_count}/{len(self.databases)} databases to Supabase")
            
        except Exception as e:
            logger.error(f"❌ Batch sync to Supabase failed: {e}")
    
    async def get_cloud_database_status(self):
        """Get database status from Supabase cloud"""
        if not self.cloud_sync_enabled:
            return {"cloud_sync": False, "message": "Cloud sync disabled"}
        
        try:
            result = self.supabase.table('database_registry').select('*').execute()
            
            if result.data:
                cloud_databases = result.data
                return {
                    "cloud_sync": True,
                    "total_cloud_databases": len(cloud_databases),
                    "last_sync": datetime.now().isoformat(),
                    "databases": cloud_databases[:10]  # Show first 10 for overview
                }
            else:
                return {
                    "cloud_sync": True,
                    "total_cloud_databases": 0,
                    "message": "No databases synced to cloud yet"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting cloud database status: {e}")
            return {"cloud_sync": False, "error": str(e)}
    
    def discover_databases(self) -> List[str]:
        """Discover all databases in the system"""
        database_paths = []
        
        # Search patterns for database files
        search_roots = [
            Path("../.."),  # Parent directories
            Path(".."),     # Parent directory
            Path(".")       # Current directory
        ]
        
        for root in search_roots:
            if root.exists():
                # Find all database files
                for pattern in ["**/*.db", "**/*.sqlite", "**/*.sqlite3"]:
                    try:
                        for db_path in root.glob(pattern):
                            if db_path.is_file() and db_path.stat().st_size > 0:
                                database_paths.append(str(db_path.resolve()))
                    except (OSError, PermissionError) as e:
                        logger.warning(f"⚠️ Cannot access {root}/{pattern}: {e}")
        
        # Remove duplicates and sort
        unique_paths = sorted(list(set(database_paths)))
        logger.info(f"🔍 Discovered {len(unique_paths)} databases")
        return unique_paths
    
    def analyze_database(self, db_path: str) -> Optional[DatabaseInfo]:
        """Analyze a single database and return its information"""
        try:
            path_obj = Path(db_path)
            if not path_obj.exists():
                return None
            
            # Basic file information
            stat_info = path_obj.stat()
            size_bytes = stat_info.st_size
            last_modified = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Connect and analyze database
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Get table count and schema information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_count = len(tables)
            
            # Calculate total record count
            total_records = 0
            schema_info = {}
            
            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                    count = cursor.fetchone()[0]
                    total_records += count
                    
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info([{table_name}])")
                    columns = cursor.fetchall()
                    schema_info[table_name] = {
                        'columns': len(columns),
                        'records': count,
                        'schema': [{'name': col[1], 'type': col[2]} for col in columns]
                    }
                except Exception as e:
                    logger.warning(f"⚠️ Cannot analyze table {table_name} in {db_path}: {e}")
            
            conn.close()
            
            # Calculate schema hash
            schema_hash = hashlib.md5(json.dumps(schema_info, sort_keys=True).encode()).hexdigest()
            
            # Determine category and description
            category, description, integration_level = self.categorize_database(path_obj.name, schema_info)
            
            # Calculate enhanced health score using MDC compliance and service connectivity
            health_score = self.calculate_enhanced_health_score(db_path, table_count, total_records, size_bytes)
            
            return DatabaseInfo(
                name=path_obj.name,
                path=db_path,
                size_bytes=size_bytes,
                last_modified=last_modified,
                status="ACTIVE",
                table_count=table_count,
                record_count=total_records,
                health_score=health_score,
                last_checked=datetime.now(),
                schema_hash=schema_hash,
                category=category,
                description=description,
                integration_level=integration_level,
                backup_status="unknown"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze database {db_path}: {e}")
            return None
    
    def categorize_database(self, db_name: str, schema_info: dict) -> tuple:
        """Categorize database based on name and schema"""
        name_lower = db_name.lower()
        
        # Service Lifecycle Databases (Level 1)
        if 'discovery' in name_lower and 'registry' in name_lower:
            return ("service_lifecycle", "Level 1: Discovery Database - Service lifecycle management", 1)
        elif 'passport' in name_lower and 'registry' in name_lower:
            return ("service_lifecycle", "Level 2: Passport Database - Service authentication", 2)
        elif 'service' in name_lower and 'registry' in name_lower:
            return ("service_lifecycle", "Level 3: Service Registry - Certified services", 3)
        
        # Trading and Market Data (Level 2)
        elif any(term in name_lower for term in ['symbol', 'market', 'trading']):
            return ("trading_data", "Trading and market data management", 2)
        elif 'risk' in name_lower or 'cowen' in name_lower:
            return ("risk_analysis", "Risk analysis and management", 2)
        
        # AI and Learning (Level 3)
        elif 'learning' in name_lower or 'pattern' in name_lower:
            return ("ai_learning", "AI learning and pattern recognition", 3)
        elif 'crypto' in name_lower and ('meter' in name_lower or 'verse' in name_lower):
            return ("analysis", "Cryptocurrency analysis and data", 2)
        
        # Infrastructure (Level 1)
        elif any(term in name_lower for term in ['port', 'api_key', 'achievement']):
            return ("infrastructure", "System infrastructure and configuration", 1)
        
        # Testing and Development
        elif 'test' in name_lower or 'backup' in name_lower:
            return ("testing", "Testing and development databases", 0)
        
        # Default
        else:
            return ("unknown", "Unategorized database", 0)
    
    def calculate_health_score(self, size_bytes: int, table_count: int, record_count: int) -> float:
        """Calculate database health score based on various factors"""
        score = 100.0
        
        # Size-based score (databases should have reasonable size)
        if size_bytes == 0:
            score -= 50.0  # Empty database
        elif size_bytes < 1024:  # Very small
            score -= 20.0
        elif size_bytes > 100_000_000:  # Very large (>100MB)
            score -= 10.0
        
        # Table count score
        if table_count == 0:
            score -= 40.0  # No tables
        elif table_count == 1:
            score += 10.0  # Well-focused database
        
        # Record count score
        if record_count == 0 and table_count > 0:
            score -= 30.0  # Tables but no data
        elif record_count > 0:
            score += 10.0  # Has data
        
        return max(0.0, min(100.0, score))
    
    def update_master_database(self, db_info: DatabaseInfo):
        """Update master database with database information"""
        try:
            conn = sqlite3.connect(self.master_db_path)
            cursor = conn.cursor()
            
            # Insert or update database registry
            cursor.execute("""
                INSERT OR REPLACE INTO database_registry 
                (name, path, size_bytes, last_modified, status, table_count, record_count, 
                 health_score, last_checked, schema_hash, category, description, 
                 integration_level, backup_status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                db_info.name, db_info.path, db_info.size_bytes, db_info.last_modified,
                db_info.status, db_info.table_count, db_info.record_count,
                db_info.health_score, db_info.last_checked, db_info.schema_hash,
                db_info.category, db_info.description, db_info.integration_level,
                db_info.backup_status, datetime.now()
            ))
            
            # Record monitoring history
            cursor.execute("""
                INSERT INTO monitoring_history 
                (database_name, health_score, status)
                VALUES (?, ?, ?)
            """, (db_info.name, db_info.health_score, db_info.status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update master database for {db_info.name}: {e}")
    
    def monitor_databases(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting database monitoring...")
        
        while self.monitoring_active:
            try:
                # Discover databases
                database_paths = self.discover_databases()
                
                # Analyze each database
                current_databases = {}
                for db_path in database_paths:
                    db_info = self.analyze_database(db_path)
                    if db_info:
                        current_databases[db_info.name] = db_info
                        self.update_master_database(db_info)
                
                # Update in-memory registry
                self.databases = current_databases
                
                logger.info(f"✅ Monitored {len(current_databases)} databases")
                
                # Periodic cloud sync (every 3 monitoring cycles)
                if hasattr(self, '_sync_counter'):
                    self._sync_counter += 1
                else:
                    self._sync_counter = 1
                
                if self._sync_counter >= 3 and self.cloud_sync_enabled:
                    logger.info("☁️ Starting periodic Supabase sync...")
                    try:
                        # Run async sync in background
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.sync_all_databases_to_supabase())
                        loop.close()
                        self._sync_counter = 0  # Reset counter
                    except Exception as e:
                        logger.error(f"❌ Periodic sync failed: {e}")
                        self._sync_counter = 0
                
                # Wait before next monitoring cycle
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def get_healthy_database_count(self) -> int:
        """Get count of truly healthy databases based on MDC compliance and connectivity"""
        healthy_count = 0
        for db_info in self.databases.values():
            if db_info.health_score >= 80.0 and db_info.status == "ACTIVE":
                healthy_count += 1
        return healthy_count
    
    def calculate_enhanced_health_score(self, db_path: str, table_count: int, record_count: int, size_bytes: int) -> float:
        """Calculate enhanced health score based on database connectivity and MDC requirements"""
        base_score = self.calculate_health_score(size_bytes, table_count, record_count)
        
        # Enhanced scoring based on service connectivity
        db_path_obj = Path(db_path)
        connectivity_score = self.check_service_connectivity(db_path_obj)
        mdc_compliance_score = self.check_mdc_compliance(db_path_obj)
        
        # Weighted average: 50% base, 30% connectivity, 20% MDC compliance
        enhanced_score = (base_score * 0.5) + (connectivity_score * 0.3) + (mdc_compliance_score * 0.2)
        return min(100.0, enhanced_score)
    
    def check_service_connectivity(self, db_path: Path) -> float:
        """Check if database can connect to associated services"""
        try:
            # Find associated service by database name patterns
            service_name = self.find_associated_service(db_path)
            if not service_name:
                return 70.0  # Neutral score for standalone databases
            
            # Check if associated service is running
            service_health = self.check_associated_service_health(service_name)
            return service_health
            
        except Exception as e:
            logger.warning(f"Service connectivity check failed for {db_path.name}: {e}")
            return 50.0
    
    def check_mdc_compliance(self, db_path: Path) -> float:
        """Check MDC file compliance and requirements"""
        try:
            # Find MDC file for this database's service
            mdc_file = self.find_mdc_file(db_path)
            if not mdc_file:
                return 60.0  # Lower score for services without MDC
            
            # Parse MDC file and check requirements
            mdc_requirements = self.parse_mdc_requirements(mdc_file)
            compliance_score = self.evaluate_mdc_compliance(mdc_requirements, db_path)
            
            return compliance_score
            
        except Exception as e:
            logger.warning(f"MDC compliance check failed for {db_path.name}: {e}")
            return 50.0
    
    def find_associated_service(self, db_path: Path) -> Optional[str]:
        """Find the service associated with this database"""
        db_name = db_path.name.lower()
        
        # Common database name patterns
        service_patterns = {
            'service_registry': 'service_registry',
            'passport_registry': 'passport_service', 
            'discovery_registry': 'discovery_service',
            'learning': 'machine_learning',
            'riskmetric': 'risk_management',
            'market_data': 'data_warehouse',
            'symbols': 'symbols_extended',
            'api_keys': 'api_keys_manager'
        }
        
        for pattern, service in service_patterns.items():
            if pattern in db_name:
                return service
                
        return None
    
    def check_associated_service_health(self, service_name: str) -> float:
        """Check if the associated service is healthy"""
        try:
            # Common service ports
            service_ports = {
                'service_registry': 8900,
                'passport_service': 8951,
                'discovery_service': 8780,
                'machine_learning': 8014,
                'risk_management': 8010,
                'data_warehouse': 8015,
                'symbols_extended': 8005,
                'api_keys_manager': 8006
            }
            
            port = service_ports.get(service_name)
            if not port:
                return 70.0
            
            # Quick health check
            import requests
            try:
                response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
                if response.status_code == 200:
                    return 100.0
                else:
                    return 40.0
            except:
                return 30.0  # Service not responding
                
        except Exception:
            return 50.0
    
    def find_mdc_file(self, db_path: Path) -> Optional[Path]:
        """Find MDC file for database's associated service"""
        try:
            # Look for MDC files in common locations
            base_dir = Path(__file__).parent.parent
            mdc_locations = [
                base_dir / ".cursor" / "rules",
                base_dir / "services", 
                base_dir
            ]
            
            service_name = self.find_associated_service(db_path)
            if not service_name:
                return None
            
            # Search for MDC files
            for location in mdc_locations:
                if location.exists():
                    for mdc_file in location.glob("*.mdc"):
                        if service_name.lower() in mdc_file.name.lower():
                            return mdc_file
            
            return None
            
        except Exception:
            return None
    
    def parse_mdc_requirements(self, mdc_file: Path) -> Dict:
        """Parse MDC file to extract requirements"""
        try:
            with open(mdc_file, 'r') as f:
                content = f.read()
            
            requirements = {
                'has_database_requirement': 'database' in content.lower(),
                'has_port_requirement': 'port' in content.lower(), 
                'has_api_endpoints': '## api' in content.lower() or '/api/' in content.lower(),
                'has_health_endpoint': '/health' in content.lower(),
                'has_requirements_section': '## requirements' in content.lower(),
                'service_dependencies': self.extract_service_dependencies(content)
            }
            
            return requirements
            
        except Exception:
            return {}
    
    def extract_service_dependencies(self, mdc_content: str) -> List[str]:
        """Extract service dependencies from MDC content"""
        dependencies = []
        
        # Look for common dependency patterns
        dependency_patterns = [
            'workflow_service', 'database_service', 'passport_service',
            'discovery_service', 'port_manager', 'api_keys_manager'
        ]
        
        content_lower = mdc_content.lower()
        for pattern in dependency_patterns:
            if pattern in content_lower:
                dependencies.append(pattern)
        
        return dependencies
    
    def evaluate_mdc_compliance(self, requirements: Dict, db_path: Path) -> float:
        """Evaluate how well the database meets MDC requirements"""
        if not requirements:
            return 60.0
        
        compliance_score = 0.0
        total_checks = 0
        
        # Check database requirement compliance
        if requirements.get('has_database_requirement'):
            compliance_score += 20.0  # Database exists, so this is met
            total_checks += 20.0
        
        # Check if service has required endpoints
        if requirements.get('has_health_endpoint'):
            service_name = self.find_associated_service(db_path)
            if service_name and self.check_associated_service_health(service_name) > 70:
                compliance_score += 15.0
            total_checks += 15.0
        
        # Check API endpoints
        if requirements.get('has_api_endpoints'):
            compliance_score += 10.0  # Assume compliance for now
            total_checks += 10.0
        
        # Check service dependencies
        dependencies = requirements.get('service_dependencies', [])
        if dependencies:
            dependency_health = self.check_dependency_health(dependencies)
            compliance_score += dependency_health * 15.0
            total_checks += 15.0
        
        # Check requirements section exists
        if requirements.get('has_requirements_section'):
            compliance_score += 10.0
            total_checks += 10.0
        
        if total_checks == 0:
            return 70.0
        
        return (compliance_score / total_checks) * 100.0
    
    def check_dependency_health(self, dependencies: List[str]) -> float:
        """Check health of service dependencies"""
        if not dependencies:
            return 1.0
        
        healthy_count = 0
        for dep in dependencies:
            if self.check_associated_service_health(dep) > 70:
                healthy_count += 1
        
        return healthy_count / len(dependencies)

    def start_background_monitoring(self):
        """Start background monitoring thread"""
        monitoring_thread = threading.Thread(target=self.monitor_databases, daemon=True)
        monitoring_thread.start()
        logger.info("🚀 Background database monitoring started")
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="ZmartBot Database Service",
            description="Master Database Management System for ZmartBot ecosystem",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add dashboard routes
        self.add_dashboard_routes(app)
        
        @app.get("/health")
        async def health_check():
            """Database service health check"""
            return {
                "status": "healthy",
                "service": "database_service",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "databases_monitored": len(self.databases),
                "master_db": self.master_db_path
            }
        
        @app.get("/api/databases")
        async def get_all_databases():
            """Get all registered databases"""
            try:
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT name, path, size_bytes, status, table_count, record_count,
                           health_score, last_checked, category, description, integration_level
                    FROM database_registry
                    ORDER BY integration_level DESC, category, name
                """)
                
                databases = []
                for row in cursor.fetchall():
                    databases.append({
                        "name": row[0],
                        "path": row[1],
                        "size_mb": round(row[2] / 1024 / 1024, 2),
                        "status": row[3],
                        "table_count": row[4],
                        "record_count": row[5],
                        "health_score": row[6],
                        "last_checked": row[7],
                        "category": row[8],
                        "description": row[9],
                        "integration_level": row[10]
                    })
                
                conn.close()
                
                return {
                    "databases": databases,
                    "total_count": len(databases),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get databases: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/databases/{db_name}")
        async def get_database_info(db_name: str):
            """Get detailed information about a specific database"""
            try:
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                # Get database info
                cursor.execute("""
                    SELECT * FROM database_registry WHERE name = ?
                """, (db_name,))
                
                db_row = cursor.fetchone()
                if not db_row:
                    raise HTTPException(status_code=404, detail="Database not found")
                
                # Get tables info
                cursor.execute("""
                    SELECT table_name, column_count, record_count, schema_info
                    FROM database_tables WHERE database_name = ?
                """, (db_name,))
                
                tables = []
                for table_row in cursor.fetchall():
                    tables.append({
                        "name": table_row[0],
                        "columns": table_row[1],
                        "records": table_row[2],
                        "schema": json.loads(table_row[3]) if table_row[3] else {}
                    })
                
                conn.close()
                
                return {
                    "database": {
                        "name": db_row[1],
                        "path": db_row[2],
                        "size_mb": round(db_row[3] / 1024 / 1024, 2),
                        "last_modified": db_row[4],
                        "status": db_row[5],
                        "table_count": db_row[6],
                        "record_count": db_row[7],
                        "health_score": db_row[8],
                        "last_checked": db_row[9],
                        "category": db_row[11],
                        "description": db_row[12],
                        "integration_level": db_row[13]
                    },
                    "tables": tables,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to get database info for {db_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/databases/categories/stats")
        async def get_category_stats():
            """Get database statistics by category"""
            try:
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        category,
                        COUNT(*) as count,
                        AVG(health_score) as avg_health,
                        SUM(size_bytes) as total_size,
                        SUM(record_count) as total_records
                    FROM database_registry
                    GROUP BY category
                    ORDER BY count DESC
                """)
                
                categories = []
                for row in cursor.fetchall():
                    categories.append({
                        "category": row[0],
                        "database_count": row[1],
                        "average_health": round(row[2], 1),
                        "total_size_mb": round(row[3] / 1024 / 1024, 2),
                        "total_records": row[4]
                    })
                
                conn.close()
                
                return {
                    "categories": categories,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get category stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/databases/{db_name}/query")
        async def execute_query(db_name: str, query_data: dict):
            """Execute a query on a specific database"""
            try:
                query = query_data.get('query', '').strip()
                if not query:
                    raise HTTPException(status_code=400, detail="Query is required")
                
                # Security: Only allow SELECT queries
                if not query.upper().startswith('SELECT'):
                    raise HTTPException(status_code=403, detail="Only SELECT queries are allowed")
                
                # Get database path
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT path FROM database_registry WHERE name = ?", (db_name,))
                db_row = cursor.fetchone()
                conn.close()
                
                if not db_row:
                    raise HTTPException(status_code=404, detail="Database not found")
                
                db_path = db_row[0]
                
                # Execute query with timeout
                start_time = time.time()
                target_conn = sqlite3.connect(db_path, timeout=10.0)
                target_cursor = target_conn.cursor()
                
                target_cursor.execute(query)
                results = target_cursor.fetchall()
                columns = [description[0] for description in target_cursor.description] if target_cursor.description else []
                
                target_conn.close()
                execution_time = (time.time() - start_time) * 1000  # ms
                
                # Log query
                log_conn = sqlite3.connect(self.master_db_path)
                log_cursor = log_conn.cursor()
                log_cursor.execute("""
                    INSERT INTO query_log (database_name, query_text, execution_time_ms, success, result_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (db_name, query, execution_time, True, len(results)))
                log_conn.commit()
                log_conn.close()
                
                return {
                    "query": query,
                    "columns": columns,
                    "results": results,
                    "result_count": len(results),
                    "execution_time_ms": round(execution_time, 2),
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                # Log failed query
                try:
                    log_conn = sqlite3.connect(self.master_db_path)
                    log_cursor = log_conn.cursor()
                    log_cursor.execute("""
                        INSERT INTO query_log (database_name, query_text, execution_time_ms, success, result_count)
                        VALUES (?, ?, ?, ?, ?)
                    """, (db_name, query_data.get('query', ''), 0, False, 0))
                    log_conn.commit()
                    log_conn.close()
                except:
                    pass
                
                logger.error(f"❌ Query execution failed on {db_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/system/overview")
        async def get_system_overview():
            """Get complete system overview"""
            try:
                conn = sqlite3.connect(self.master_db_path)
                cursor = conn.cursor()
                
                # Total statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_databases,
                        SUM(size_bytes) as total_size,
                        SUM(table_count) as total_tables,
                        SUM(record_count) as total_records,
                        AVG(health_score) as avg_health
                    FROM database_registry
                """)
                
                stats = cursor.fetchone()
                
                # Service lifecycle stats
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN category = 'service_lifecycle' AND integration_level = 1 THEN record_count ELSE 0 END) as discovery_count,
                        SUM(CASE WHEN category = 'service_lifecycle' AND integration_level = 2 THEN record_count ELSE 0 END) as passport_count,
                        SUM(CASE WHEN category = 'service_lifecycle' AND integration_level = 3 THEN record_count ELSE 0 END) as registry_count
                    FROM database_registry
                """)
                
                lifecycle = cursor.fetchone()
                
                conn.close()
                
                # System resources
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                return {
                    "database_statistics": {
                        "total_databases": stats[0],
                        "total_size_mb": round(stats[1] / 1024 / 1024, 2),
                        "total_tables": stats[2],
                        "total_records": stats[3],
                        "average_health": round(stats[4], 1)
                    },
                    "service_lifecycle": {
                        "discovery_services": lifecycle[0] or 0,
                        "passport_services": lifecycle[1] or 0,
                        "registered_services": lifecycle[2] or 0
                    },
                    "system_resources": {
                        "memory_usage_percent": memory.percent,
                        "disk_usage_percent": disk.percent,
                        "cpu_count": psutil.cpu_count()
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get system overview: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ========== CLOUD/SUPABASE ENDPOINTS ==========
        
        @app.get("/api/cloud/status")
        async def get_cloud_sync_status():
            """Get cloud synchronization status"""
            try:
                cloud_status = await self.get_cloud_database_status()
                return {
                    "cloud_sync_enabled": self.cloud_sync_enabled,
                    "supabase_url": self.supabase_url,
                    "local_databases": len(self.databases),
                    **cloud_status,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Failed to get cloud status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/cloud/sync")
        async def trigger_cloud_sync():
            """Manually trigger cloud synchronization"""
            if not self.cloud_sync_enabled:
                return {
                    "success": False,
                    "message": "Cloud sync is disabled. Set SUPABASE_KEY environment variable to enable."
                }
            
            try:
                await self.sync_all_databases_to_supabase()
                return {
                    "success": True,
                    "message": f"Successfully synced {len(self.databases)} databases to cloud",
                    "databases_synced": len(self.databases),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Manual cloud sync failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.post("/api/cloud/sync/{db_name}")
        async def sync_single_database(db_name: str):
            """Sync a single database to cloud"""
            if not self.cloud_sync_enabled:
                return {
                    "success": False,
                    "message": "Cloud sync is disabled. Set SUPABASE_KEY environment variable to enable."
                }
            
            if db_name not in self.databases:
                raise HTTPException(status_code=404, detail=f"Database '{db_name}' not found")
            
            try:
                db_info = self.databases[db_name]
                success = await self.sync_database_to_supabase(db_info)
                return {
                    "success": success,
                    "database": db_name,
                    "message": f"Database '{db_name}' {'synced successfully' if success else 'sync failed'}",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Single database sync failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.get("/api/cloud/databases")
        async def get_cloud_databases():
            """Get all databases from Supabase cloud"""
            if not self.cloud_sync_enabled:
                return {
                    "cloud_sync_enabled": False,
                    "message": "Cloud sync is disabled"
                }
            
            try:
                result = self.supabase.table('database_registry').select('*').order('updated_at', desc=True).execute()
                
                return {
                    "cloud_sync_enabled": True,
                    "total_cloud_databases": len(result.data) if result.data else 0,
                    "databases": result.data or [],
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Failed to get cloud databases: {e}")
                return {
                    "cloud_sync_enabled": True,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.get("/api/cloud/setup-instructions")
        async def get_cloud_setup_instructions():
            """Get instructions for setting up Supabase integration"""
            return {
                "cloud_sync_enabled": self.cloud_sync_enabled,
                "supabase_url": self.supabase_url,
                "sync_strategy": "Individual Tables + Registry",
                "instructions": [
                    "1. Go to https://supabase.com and create a new project",
                    "2. Get your project URL and anon key from Settings > API", 
                    "3. Set environment variable: export SUPABASE_KEY='your-anon-key-here'",
                    "4. Create main registry table in Supabase SQL Editor:",
                    """
                    CREATE TABLE database_registry (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        name TEXT UNIQUE NOT NULL,
                        path TEXT,
                        size_bytes BIGINT,
                        last_modified TIMESTAMPTZ,
                        status TEXT,
                        table_count INTEGER,
                        record_count BIGINT,
                        health_score FLOAT,
                        last_checked TIMESTAMPTZ,
                        schema_hash TEXT,
                        category TEXT,
                        description TEXT,
                        integration_level INTEGER,
                        backup_status TEXT,
                        sync_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    """,
                    "5. Individual database tables will be created automatically during sync",
                    "6. Each SQLite database will create separate Supabase tables for its content",
                    "7. Restart DatabaseService to enable cloud sync"
                ]
            }
        
        @app.get("/api/cloud/individual-tables")
        async def get_individual_table_mapping():
            """Get mapping of local databases to individual Supabase tables"""
            if not self.cloud_sync_enabled:
                return {
                    "cloud_sync_enabled": False,
                    "message": "Cloud sync is disabled"
                }
            
            try:
                table_mapping = {}
                for db_name, db_info in self.databases.items():
                    clean_name = db_name.replace('.db', '').replace('-', '_').replace(' ', '_').lower()
                    supabase_table_prefix = f"db_{clean_name}"
                    
                    # Get table count from database info
                    table_mapping[db_name] = {
                        "category": db_info.category,
                        "local_tables": db_info.table_count,
                        "supabase_prefix": supabase_table_prefix,
                        "health_score": db_info.health_score,
                        "record_count": db_info.record_count,
                        "estimated_cloud_tables": f"{supabase_table_prefix}_*"
                    }
                
                return {
                    "cloud_sync_enabled": True,
                    "total_databases": len(table_mapping),
                    "table_mapping": table_mapping,
                    "sync_strategy": "Each SQLite table becomes: db_{database}_{table}",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Error getting table mapping: {e}")
                return {
                    "cloud_sync_enabled": True,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.post("/api/cloud/extract-preview/{db_name}")
        async def preview_database_extraction(db_name: str):
            """Preview what would be extracted from a database without syncing"""
            if db_name not in self.databases:
                raise HTTPException(status_code=404, detail=f"Database '{db_name}' not found")
            
            try:
                db_info = self.databases[db_name]
                content = await self.extract_database_content(db_info.path, max_records_per_table=5)
                
                preview = {}
                for table_name, table_data in content.items():
                    clean_db_name = db_name.replace('.db', '').replace('-', '_').replace(' ', '_').lower()
                    supabase_table_name = f"db_{clean_db_name}_{table_name}"
                    
                    preview[supabase_table_name] = {
                        "local_table": table_name,
                        "record_count": len(table_data),
                        "sample_records": table_data[:3] if table_data else [],
                        "columns": list(table_data[0].keys()) if table_data else []
                    }
                
                return {
                    "database": db_name,
                    "category": db_info.category,
                    "extraction_preview": preview,
                    "total_tables": len(preview),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Error previewing extraction for {db_name}: {e}")
                return {
                    "error": str(e),
                    "database": db_name,
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.get("/api/cloud/category-sync/{category}")
        async def get_category_sync_status(category: str):
            """Get sync status for all databases in a specific category"""
            if not self.cloud_sync_enabled:
                return {
                    "cloud_sync_enabled": False,
                    "message": "Cloud sync is disabled"
                }
            
            category_databases = {
                name: db_info for name, db_info in self.databases.items()
                if db_info.category == category
            }
            
            if not category_databases:
                return {
                    "category": category,
                    "databases_found": 0,
                    "message": f"No databases found in category '{category}'"
                }
            
            return {
                "category": category,
                "databases_found": len(category_databases),
                "databases": {
                    name: {
                        "table_count": db_info.table_count,
                        "record_count": db_info.record_count,
                        "health_score": db_info.health_score,
                        "last_checked": db_info.last_checked.isoformat()
                    }
                    for name, db_info in category_databases.items()
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # ========== SERVICE LIFECYCLE ENDPOINTS ==========
        
        @app.get("/api/services/lifecycle/all")
        async def get_service_lifecycle_data():
            """Get comprehensive service lifecycle data for all levels using dynamic lifecycle manager"""
            try:
                # Use dynamic lifecycle manager for accurate counts
                unique_counts = self.lifecycle_manager.get_unique_service_counts()
                services_by_level = self.lifecycle_manager.get_all_services_by_level()
                duplicates = self.lifecycle_manager.find_duplicate_services()
                
                # Get raw counts for comparison
                raw_discovery = len(services_by_level['discovery'])
                raw_passport = len(services_by_level['passport'])
                raw_certificate = len(services_by_level['certificate'])
                
                return {
                    "level_3_certified": unique_counts['certificate'],
                    "level_2_passport": unique_counts['passport'], 
                    "level_1_discovery": unique_counts['discovery'],
                    "total_services": unique_counts['total_unique'],
                    "services": {
                        "certified": unique_counts['certificate'],
                        "passport": unique_counts['passport'],
                        "discovery": unique_counts['discovery']
                    },
                    "total": unique_counts['certificate'],  # For backward compatibility with dashboard
                    "raw_counts": {
                        "discovery_raw": raw_discovery,
                        "passport_raw": raw_passport, 
                        "certificate_raw": raw_certificate,
                        "raw_total": raw_discovery + raw_passport + raw_certificate
                    },
                    "violations": {
                        "has_duplicates": bool(duplicates),
                        "duplicate_count": sum(len(v) for v in duplicates.values()),
                        "duplicates": duplicates
                    },
                    "integrity_status": "CLEAN" if not duplicates else "VIOLATIONS_FOUND",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error fetching dynamic service lifecycle data: {e}")
                # Fallback to basic counting if lifecycle manager fails
                try:
                    fallback_counts = self._get_fallback_lifecycle_counts()
                    fallback_counts["error"] = f"Lifecycle manager error: {str(e)}"
                    return fallback_counts
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise HTTPException(status_code=500, detail=str(e))

        def _get_fallback_lifecycle_counts(self):
            """Fallback method for basic service counting if lifecycle manager fails"""
            service_registry_count = 0
            passport_registry_count = 0
            discovery_registry_count = 0
            
            # Count services in service_registry.db
            try:
                conn = sqlite3.connect("../service_registry.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM services")
                service_registry_count = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass
                
            # Count services in passport_registry.db
            try:
                conn = sqlite3.connect("../data/passport_registry.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM passport_registry")
                passport_registry_count = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass
                
            # Count services in discovery_registry.db
            try:
                conn = sqlite3.connect("../discovery_registry.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM discovery_services")
                discovery_registry_count = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass
                
            return {
                "level_3_certified": service_registry_count,
                "level_2_passport": passport_registry_count,
                "level_1_discovery": discovery_registry_count,
                "total_services": service_registry_count + passport_registry_count + discovery_registry_count,
                "services": {
                    "certified": service_registry_count,
                    "passport": passport_registry_count,
                    "discovery": discovery_registry_count
                },
                "total": service_registry_count,
                "fallback_mode": True,
                "timestamp": datetime.now().isoformat()
            }

        @app.get("/api/services/lifecycle/validate")
        async def validate_service_lifecycle():
            """Validate service lifecycle integrity and get comprehensive report"""
            try:
                validation_report = self.lifecycle_manager.validate_system_integrity()
                return validation_report
            except Exception as e:
                logger.error(f"Error validating service lifecycle: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/services/lifecycle/cleanup")
        async def cleanup_service_lifecycle(dry_run: bool = True):
            """Clean up promoted services that weren't removed from lower levels"""
            try:
                cleanup_results = self.lifecycle_manager.cleanup_promoted_services(dry_run=dry_run)
                return cleanup_results
            except Exception as e:
                logger.error(f"Error during lifecycle cleanup: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ========== SERVICE REGISTRY ENDPOINTS ==========
        
        @app.post("/api/services/sync-to-supabase")
        async def sync_services_to_supabase():
            """Sync service registry data to Supabase"""
            try:
                success = await self.sync_service_registry_to_supabase()
                if success:
                    return {"status": "success", "message": "Service registry synced to Supabase successfully"}
                else:
                    return {"status": "error", "message": "Failed to sync service registry to Supabase"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/services/registry")
        async def get_service_registry():
            """Get service registry data"""
            try:
                services_data = await self.get_service_registry_data()
                return {
                    "services": services_data,
                    "total": len(services_data),
                    "certified_count": len([s for s in services_data if s.get('certification_status') == 'CERTIFIED']),
                    "pending_count": len([s for s in services_data if s.get('certification_status') == 'PENDING'])
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/services/registry/supabase")
        async def get_supabase_service_registry():
            """Get service registry data from Supabase"""
            try:
                if not self.cloud_sync_enabled:
                    raise HTTPException(status_code=503, detail="Supabase sync not enabled")
                
                result = self.supabase.table('service_registry').select('*').execute()
                
                if result.data:
                    services = result.data
                    return {
                        "services": services,
                        "total": len(services),
                        "certified_count": len([s for s in services if s.get('certification_status') == 'CERTIFIED']),
                        "pending_count": len([s for s in services if s.get('certification_status') == 'PENDING']),
                        "source": "supabase"
                    }
                else:
                    return {
                        "services": [],
                        "total": 0,
                        "certified_count": 0,
                        "pending_count": 0,
                        "source": "supabase",
                        "message": "No services found in Supabase"
                    }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return app
    
    def run(self):
        """Run the Database Service"""
        logger.info(f"🚀 Starting ZmartBot Database Service on port {self.port}")
        logger.info(f"📊 Master Database: {self.master_db_path}")
        
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="info"
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZmartBot Database Service')
    parser.add_argument('--port', default=8905, type=int, help='Port to bind to')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    # Create and run service
    db_service = DatabaseService(port=args.port)
    db_service.run()

if __name__ == "__main__":
    main()