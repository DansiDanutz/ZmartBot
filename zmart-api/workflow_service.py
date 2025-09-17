#!/usr/bin/env python3
"""
ZmartBot Workflow Service
Mandatory service validation and workflow orchestration system for ZmartBot ecosystem.
Defines exact requirements for each service level and validates service transitions.
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
import requests
from database.service_lifecycle_manager import ServiceLifecycleManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceWorkflow:
    """Service workflow information structure"""
    service_name: str
    current_level: int
    current_status: str
    requirements_met: List[str]
    requirements_pending: List[str]
    last_transition: datetime
    next_transition_eligible: datetime

@dataclass
class WorkflowRequirement:
    """Workflow requirement structure"""
    level: int
    requirement_type: str
    requirement_description: str
    validation_endpoint: Optional[str]
    mandatory: bool = True

class WorkflowService:
    """ZmartBot Workflow Service for service lifecycle management"""
    
    def __init__(self, port: int = 8950):
        self.port = port
        self.workflow_db_path = "workflow_registry.db"
        self.discovery_db_path = "discovery_registry.db"
        self.passport_db_path = "data/passport_registry.db"
        self.service_db_path = "src/data/service_registry.db"
        
        # Initialize Service Lifecycle Manager for dynamic validation
        self.lifecycle_manager = ServiceLifecycleManager()
        
        # Service level definitions
        self.service_levels = {
            1: "Discovery Service",
            2: "Active Service (Passport)",
            3: "Registered Service", 
            4: "Certified Service"
        }
        
        # Initialize systems
        self.init_workflow_database()
        self.load_workflow_requirements()
        
        # FastAPI app
        self.app = self.create_app()
    
    def init_workflow_database(self):
        """Initialize the Workflow Registry Database"""
        try:
            conn = sqlite3.connect(self.workflow_db_path)
            cursor = conn.cursor()
            
            # Create service_workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    current_level INTEGER NOT NULL CHECK (current_level IN (1, 2, 3, 4)),
                    current_status TEXT NOT NULL,
                    requirements_met TEXT, -- JSON of fulfilled requirements
                    requirements_pending TEXT, -- JSON of pending requirements  
                    last_transition TIMESTAMP,
                    next_transition_eligible TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create workflow_requirements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER NOT NULL CHECK (level IN (1, 2, 3, 4)),
                    requirement_type TEXT NOT NULL,
                    requirement_description TEXT NOT NULL,
                    validation_endpoint TEXT,
                    mandatory BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create workflow_transitions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    from_level INTEGER NOT NULL,
                    to_level INTEGER NOT NULL,
                    transition_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    requirements_validated TEXT, -- JSON
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    triggered_by TEXT -- system, manual, api
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Workflow Registry Database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing workflow database: {e}")
            raise
    
    def load_workflow_requirements(self):
        """Load predefined workflow requirements"""
        requirements = [
            # Level 1 Requirements
            WorkflowRequirement(1, "python_file", "Python file (.py) must exist", None),
            WorkflowRequirement(1, "mdc_file", "MDC file (.mdc) must be assigned and present", None),
            WorkflowRequirement(1, "no_interaction", "Service must not interact with other services", None),
            WorkflowRequirement(1, "isolation", "Service must remain isolated (no external calls)", None),
            
            # Level 2 Requirements  
            WorkflowRequirement(2, "service_interaction", "Service must interact with at least one other service", None),
            WorkflowRequirement(2, "port_assigned", "Port assigned by Port Manager (unique)", "/api/validate/port"),
            WorkflowRequirement(2, "passport_assigned", "Passport assigned by Passport Service", "/api/validate/passport"),
            WorkflowRequirement(2, "external_response", "Service must respond to external calls", None),
            
            # Level 3 Requirements
            WorkflowRequirement(3, "tests_passed", "All tests must pass (unit, integration)", "/api/validate/tests"),
            WorkflowRequirement(3, "health_check", "Health check endpoint must be functional", "/api/validate/health"),
            WorkflowRequirement(3, "no_duplicates", "No duplicate services in registry", "/api/conflicts/duplicates"),
            WorkflowRequirement(3, "orchestration_start", "OrchestrationStart assignment completed", "/api/validate/orchestration"),
            WorkflowRequirement(3, "master_orchestration", "Master Orchestration Agent assignment active", "/api/validate/orchestration"),
            
            # Level 4 Requirements
            WorkflowRequirement(4, "certification_audit", "Full certification process completed", "/api/validate/certification"),
            WorkflowRequirement(4, "certificate_assigned", "Certificate (CERT) assigned", "/api/validate/certificate"),
            WorkflowRequirement(4, "production_verified", "Production deployment verified", "/api/validate/production"),
            WorkflowRequirement(4, "performance_metrics", "Service performance metrics meet standards", "/api/validate/performance"),
        ]
        
        try:
            conn = sqlite3.connect(self.workflow_db_path)
            cursor = conn.cursor()
            
            for req in requirements:
                cursor.execute("""
                    INSERT OR REPLACE INTO workflow_requirements 
                    (level, requirement_type, requirement_description, validation_endpoint, mandatory)
                    VALUES (?, ?, ?, ?, ?)
                """, (req.level, req.requirement_type, req.requirement_description, 
                     req.validation_endpoint, req.mandatory))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Workflow requirements loaded")
            
        except Exception as e:
            logger.error(f"❌ Error loading workflow requirements: {e}")
    
    def sync_service_workflows(self):
        """Synchronize service workflows with actual database states"""
        try:
            conn = sqlite3.connect(self.workflow_db_path)
            cursor = conn.cursor()
            
            # Get all services from discovery database
            if os.path.exists(self.discovery_db_path):
                disc_conn = sqlite3.connect(self.discovery_db_path)
                disc_cursor = disc_conn.cursor()
                disc_cursor.execute("SELECT service_name, status FROM discovery_services")
                discovery_services = disc_cursor.fetchall()
                disc_conn.close()
                
                for service_name, status in discovery_services:
                    cursor.execute("""
                        INSERT OR REPLACE INTO service_workflows
                        (service_name, current_level, current_status, requirements_met, 
                         requirements_pending, last_transition, next_transition_eligible)
                        VALUES (?, 1, ?, ?, ?, ?, ?)
                    """, (service_name, status, 
                         json.dumps(["python_file", "mdc_file"]),
                         json.dumps(["no_interaction", "isolation"]),
                         datetime.now(), datetime.now()))
            
            # Get all services from passport database
            if os.path.exists(self.passport_db_path):
                pass_conn = sqlite3.connect(self.passport_db_path)
                pass_cursor = pass_conn.cursor()
                pass_cursor.execute("SELECT service_name, status FROM passport_registry")
                passport_services = pass_cursor.fetchall()
                pass_conn.close()
                
                for service_name, status in passport_services:
                    cursor.execute("""
                        INSERT OR REPLACE INTO service_workflows
                        (service_name, current_level, current_status, requirements_met, 
                         requirements_pending, last_transition, next_transition_eligible)
                        VALUES (?, 2, ?, ?, ?, ?, ?)
                    """, (service_name, status,
                         json.dumps(["python_file", "mdc_file", "service_interaction", "port_assigned", "passport_assigned"]),
                         json.dumps(["external_response"]),
                         datetime.now(), datetime.now()))
            
            # Get all services from service registry
            if os.path.exists(self.service_db_path):
                srv_conn = sqlite3.connect(self.service_db_path)
                srv_cursor = srv_conn.cursor()
                srv_cursor.execute("SELECT service_name, status FROM service_registry")
                registered_services = srv_cursor.fetchall()
                srv_conn.close()
                
                for service_name, status in registered_services:
                    cursor.execute("""
                        INSERT OR REPLACE INTO service_workflows
                        (service_name, current_level, current_status, requirements_met, 
                         requirements_pending, last_transition, next_transition_eligible)
                        VALUES (?, 3, ?, ?, ?, ?, ?)
                    """, (service_name, status,
                         json.dumps(["python_file", "mdc_file", "service_interaction", "port_assigned", 
                                   "passport_assigned", "external_response", "health_check"]),
                         json.dumps(["tests_passed", "no_duplicates", "orchestration_start", "master_orchestration"]),
                         datetime.now(), datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Service workflows synchronized")
            
        except Exception as e:
            logger.error(f"❌ Error synchronizing service workflows: {e}")
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="ZmartBot Workflow Service",
            description="Mandatory service validation and workflow orchestration system",
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
        
        @app.get("/health")
        async def health_check():
            """Workflow service health check"""
            return {
                "status": "healthy",
                "service": "workflow_service",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "port": self.port,
                "databases_connected": self.check_database_connections()
            }
        
        @app.get("/api/workflow/status")
        async def workflow_status():
            """Get overall workflow system status"""
            try:
                conn = sqlite3.connect(self.workflow_db_path)
                cursor = conn.cursor()
                
                # Get service counts by level (workflow internal tracking)
                cursor.execute("SELECT current_level, COUNT(*) FROM service_workflows GROUP BY current_level")
                level_counts = dict(cursor.fetchall())
                
                # Get dynamic lifecycle counts for validation
                try:
                    dynamic_counts = self.lifecycle_manager.get_unique_service_counts()
                    duplicates = self.lifecycle_manager.find_duplicate_services()
                    validation_report = self.lifecycle_manager.validate_system_integrity()
                except Exception as e:
                    dynamic_counts = {"error": f"Dynamic validation failed: {str(e)}"}
                    duplicates = {}
                    validation_report = {"integrity_status": "ERROR"}
                
                # Get recent transitions
                cursor.execute("""
                    SELECT service_name, from_level, to_level, transition_date, success 
                    FROM workflow_transitions 
                    ORDER BY transition_date DESC LIMIT 10
                """)
                recent_transitions = [
                    {
                        "service": row[0], "from_level": row[1], "to_level": row[2],
                        "date": row[3], "success": bool(row[4])
                    }
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    "status": "operational",
                    "timestamp": datetime.now().isoformat(),
                    "service_levels": {
                        "level_1_discovery": level_counts.get(1, 0),
                        "level_2_active": level_counts.get(2, 0), 
                        "level_3_registered": level_counts.get(3, 0),
                        "level_4_certified": level_counts.get(4, 0)
                    },
                    "dynamic_lifecycle_validation": {
                        "unique_counts": dynamic_counts,
                        "integrity_status": validation_report.get("integrity_status", "UNKNOWN"),
                        "violations": duplicates,
                        "violation_count": sum(len(v) for v in duplicates.values()) if duplicates else 0
                    },
                    "recent_transitions": recent_transitions,
                    "databases_synced": True
                }
                
            except Exception as e:
                logger.error(f"Error getting workflow status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/workflow/service/{service_name}")
        async def get_service_workflow(service_name: str):
            """Get complete workflow status for specific service"""
            try:
                conn = sqlite3.connect(self.workflow_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, current_level, current_status, requirements_met, 
                           requirements_pending, last_transition, next_transition_eligible
                    FROM service_workflows WHERE service_name = ?
                """, (service_name,))
                
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    raise HTTPException(status_code=404, detail=f"Service {service_name} not found in workflow")
                
                return {
                    "service_name": result[0],
                    "current_level": result[1],
                    "level_name": self.service_levels.get(result[1], "Unknown"),
                    "current_status": result[2],
                    "requirements_met": json.loads(result[3] or "[]"),
                    "requirements_pending": json.loads(result[4] or "[]"),
                    "last_transition": result[5],
                    "next_transition_eligible": result[6],
                    "can_transition": len(json.loads(result[4] or "[]")) == 0
                }
                
            except Exception as e:
                logger.error(f"Error getting service workflow: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/workflow/requirements/{level}")
        async def get_level_requirements(level: int):
            """Get requirements for specific service level"""
            try:
                conn = sqlite3.connect(self.workflow_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT requirement_type, requirement_description, validation_endpoint, mandatory
                    FROM workflow_requirements WHERE level = ?
                """, (level,))
                
                requirements = [
                    {
                        "type": row[0],
                        "description": row[1], 
                        "validation_endpoint": row[2],
                        "mandatory": bool(row[3])
                    }
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    "level": level,
                    "level_name": self.service_levels.get(level, "Unknown"),
                    "requirements": requirements,
                    "total_requirements": len(requirements)
                }
                
            except Exception as e:
                logger.error(f"Error getting level requirements: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/workflow/next-steps/{service_name}")
        async def get_next_steps(service_name: str):
            """Get next steps for service progression"""
            try:
                # Get current workflow status
                workflow_response = await get_service_workflow(service_name)
                current_level = workflow_response["current_level"]
                requirements_pending = workflow_response["requirements_pending"]
                
                if not requirements_pending:
                    # Ready for next level
                    next_level = min(current_level + 1, 4)
                    next_requirements_response = await get_level_requirements(next_level)
                    
                    return {
                        "service_name": service_name,
                        "current_level": current_level,
                        "ready_for_transition": True,
                        "next_level": next_level,
                        "next_level_name": self.service_levels.get(next_level),
                        "next_steps": ["Complete transition to Level " + str(next_level)],
                        "next_level_requirements": next_requirements_response["requirements"]
                    }
                else:
                    return {
                        "service_name": service_name,
                        "current_level": current_level,
                        "ready_for_transition": False,
                        "pending_requirements": requirements_pending,
                        "next_steps": [f"Complete requirement: {req}" for req in requirements_pending]
                    }
                    
            except Exception as e:
                logger.error(f"Error getting next steps: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/levels/{level_name}")
        async def get_services_by_level(level_name: str):
            """Get all services at specific level"""
            level_mapping = {
                "discovery": 1,
                "passport": 2,
                "active": 2,
                "registered": 3,
                "certified": 4
            }
            
            level = level_mapping.get(level_name.lower())
            if not level:
                raise HTTPException(status_code=400, detail=f"Invalid level name: {level_name}")
                
            try:
                conn = sqlite3.connect(self.workflow_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT service_name, current_status, requirements_met, requirements_pending
                    FROM service_workflows WHERE current_level = ?
                """, (level,))
                
                services = [
                    {
                        "service_name": row[0],
                        "status": row[1],
                        "requirements_met": json.loads(row[2] or "[]"),
                        "requirements_pending": json.loads(row[3] or "[]")
                    }
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    "level": level,
                    "level_name": self.service_levels.get(level),
                    "services": services,
                    "total_services": len(services)
                }
                
            except Exception as e:
                logger.error(f"Error getting services by level: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        return app
    
    def check_database_connections(self) -> Dict[str, bool]:
        """Check connections to all lifecycle databases"""
        connections = {}
        
        databases = {
            "workflow": self.workflow_db_path,
            "discovery": self.discovery_db_path, 
            "passport": self.passport_db_path,
            "service_registry": self.service_db_path
        }
        
        for name, path in databases.items():
            try:
                if os.path.exists(path):
                    conn = sqlite3.connect(path)
                    conn.execute("SELECT 1")
                    conn.close()
                    connections[name] = True
                else:
                    connections[name] = False
            except:
                connections[name] = False
                
        return connections
    
    def start_server(self):
        """Start the workflow service server"""
        logger.info(f"🚀 Starting ZmartBot Workflow Service on port {self.port}")
        logger.info(f"📊 Workflow Database: {self.workflow_db_path}")
        
        # Sync workflows before starting
        self.sync_service_workflows()
        
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="info"
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Workflow Service")
    parser.add_argument("--port", type=int, default=8950, help="Port to run the service on")
    
    args = parser.parse_args()
    
    try:
        workflow_service = WorkflowService(port=args.port)
        workflow_service.start_server()
        
    except KeyboardInterrupt:
        logger.info("🔄 Workflow Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting Workflow Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()