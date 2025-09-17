#!/usr/bin/env python3
"""
Passport Service - Comprehensive Service Registration & Identity Management
Port: 8620
Author: ZmartBot Team
"""

import os
import sys
import argparse
import asyncio
import sqlite3
import hashlib
import secrets
import uuid
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
import json

# Models
class ServiceRegistrationRequest(BaseModel):
    service_name: str = Field(..., description="Service name")
    service_type: str = Field(..., description="Service type (SRV, AGT, API, ENG, BOT, DB)")
    port: int = Field(..., description="Service port")
    manifest: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Service manifest")
    description: Optional[str] = Field(None, description="Service description")

class ServiceResponse(BaseModel):
    passport_id: str
    service_name: str
    service_type: str
    port: Optional[int]
    status: str
    registered_at: str
    activated_at: Optional[str] = None
    last_seen: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PassportStatsResponse(BaseModel):
    total_services: int
    active_services: int
    pending_services: int
    service_types: Dict[str, int]
    registrations_today: int

class PassportService:
    """Main Passport Service class"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"
        self.secret_key = os.getenv("PASSPORT_SECRET_KEY", "zmartbot-passport-key")
        self.init_database()
    
    def get_db_connection(self):
        """Get database connection with proper timeout and retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.execute("PRAGMA busy_timeout = 30000")  # 30 second timeout
                conn.execute("PRAGMA journal_mode = WAL")    # WAL mode for better concurrency
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                raise e
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_db_connection() as conn:
            # Passport registry table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS passport_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passport_id TEXT UNIQUE NOT NULL,
                    service_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    port INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activated_at TIMESTAMP,
                    last_seen TIMESTAMP,
                    metadata JSON,
                    description TEXT,
                    created_by TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS passport_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passport_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_agent TEXT,
                    ip_address TEXT
                );
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_passport_id ON passport_registry(passport_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_service_name ON passport_registry(service_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON passport_registry(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_passport_audit ON passport_audit_log(passport_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action ON passport_audit_log(action);")
            
            conn.commit()
            print("✅ Passport Service database initialized")
    
    def generate_passport_id(self, service_name: str, service_type: str) -> str:
        """Generate unique Passport ID with format: ZMBT-{TYPE}-{DATE}-{HASH}"""
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Generate unique hash
        hash_input = f"{service_name}-{service_type}-{datetime.now().isoformat()}-{secrets.token_hex(8)}"
        hash_obj = hashlib.sha256(hash_input.encode())
        unique_hash = hash_obj.hexdigest()[:6].upper()
        
        # Validate service type
        valid_types = ["SRV", "AGT", "API", "ENG", "BOT", "DB"]
        if service_type.upper() not in valid_types:
            service_type = "SRV"  # Default to service
        
        passport_id = f"ZMBT-{service_type.upper()}-{date_str}-{unique_hash}"
        
        # Ensure uniqueness
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE passport_id = ?", (passport_id,))
            if cursor.fetchone()[0] > 0:
                # Regenerate if collision
                return self.generate_passport_id(service_name, service_type)
        
        return passport_id
    
    def register_service(self, request: ServiceRegistrationRequest, client_ip: str = None) -> Dict[str, Any]:
        """Register new service and issue Passport ID"""
        
        # Check for existing service
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT passport_id, status FROM passport_registry 
                WHERE service_name = ? AND port = ?
            """, (request.service_name, request.port))
            
            existing = cursor.fetchone()
            if existing:
                if existing[1] in ['ACTIVE', 'REGISTERED']:
                    raise HTTPException(
                        status_code=409, 
                        detail=f"Service {request.service_name} already registered with Passport ID: {existing[0]}"
                    )
        
        # Generate Passport ID
        passport_id = self.generate_passport_id(request.service_name, request.service_type)
        
        # Register service
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO passport_registry 
                (passport_id, service_name, service_type, port, status, metadata, description)
                VALUES (?, ?, ?, ?, 'REGISTERED', ?, ?)
            """, (
                passport_id, 
                request.service_name, 
                request.service_type.upper(), 
                request.port,
                json.dumps(request.manifest),
                request.description
            ))
            
            # Log audit entry
            self.log_audit(passport_id, "REGISTERED", {
                "service_name": request.service_name,
                "service_type": request.service_type,
                "port": request.port
            }, client_ip)
            
            conn.commit()
        
        print(f"✅ Service registered: {request.service_name} -> {passport_id}")
        return {
            "passport_id": passport_id,
            "service_name": request.service_name,
            "service_type": request.service_type.upper(),
            "status": "REGISTERED",
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "port": request.port
        }
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all registered services"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM passport_registry 
                ORDER BY registered_at DESC
            """)
            
            services = []
            for row in cursor.fetchall():
                service = dict(row)
                if service['metadata']:
                    service['metadata'] = json.loads(service['metadata'])
                services.append(service)
            
            return services
    
    def get_service_by_passport(self, passport_id: str) -> Optional[Dict[str, Any]]:
        """Get service by Passport ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM passport_registry WHERE passport_id = ?", (passport_id,))
            
            row = cursor.fetchone()
            if row:
                service = dict(row)
                if service['metadata']:
                    service['metadata'] = json.loads(service['metadata'])
                return service
            return None
    
    def activate_service(self, passport_id: str, client_ip: str = None) -> bool:
        """Activate registered service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE passport_registry 
                SET status = 'ACTIVE', activated_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE passport_id = ? AND status = 'REGISTERED'
            """, (passport_id,))
            
            if cursor.rowcount > 0:
                self.log_audit(passport_id, "ACTIVATED", {"status": "ACTIVE"}, client_ip)
                conn.commit()
                print(f"✅ Service activated: {passport_id}")
                return True
            return False
    
    def deactivate_service(self, passport_id: str, client_ip: str = None) -> bool:
        """Deactivate service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE passport_registry 
                SET status = 'INACTIVE', updated_at = CURRENT_TIMESTAMP
                WHERE passport_id = ? AND status = 'ACTIVE'
            """, (passport_id,))
            
            if cursor.rowcount > 0:
                self.log_audit(passport_id, "DEACTIVATED", {"status": "INACTIVE"}, client_ip)
                conn.commit()
                print(f"⚠️ Service deactivated: {passport_id}")
                return True
            return False
    
    def unregister_service(self, passport_id: str, client_ip: str = None) -> bool:
        """Unregister service and revoke Passport ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE passport_registry 
                SET status = 'REVOKED', updated_at = CURRENT_TIMESTAMP
                WHERE passport_id = ?
            """, (passport_id,))
            
            if cursor.rowcount > 0:
                self.log_audit(passport_id, "REVOKED", {"status": "REVOKED"}, client_ip)
                conn.commit()
                print(f"🚫 Service unregistered: {passport_id}")
                return True
            return False
    
    def get_audit_trail(self, passport_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for service"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM passport_audit_log 
                WHERE passport_id = ? 
                ORDER BY timestamp DESC
            """, (passport_id,))
            
            audit_entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                if entry['details']:
                    entry['details'] = json.loads(entry['details'])
                audit_entries.append(entry)
            
            return audit_entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registration statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total services
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status != 'REVOKED'")
            total_services = cursor.fetchone()[0]
            
            # Active services
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status = 'ACTIVE'")
            active_services = cursor.fetchone()[0]
            
            # Pending services
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status IN ('PENDING', 'REGISTERED')")
            pending_services = cursor.fetchone()[0]
            
            # Service types
            cursor.execute("""
                SELECT service_type, COUNT(*) FROM passport_registry 
                WHERE status != 'REVOKED' 
                GROUP BY service_type
            """)
            service_types = dict(cursor.fetchall())
            
            # Registrations today
            cursor.execute("""
                SELECT COUNT(*) FROM passport_registry 
                WHERE DATE(registered_at) = DATE('now')
            """)
            registrations_today = cursor.fetchone()[0]
            
            return {
                "total_services": total_services,
                "active_services": active_services,
                "pending_services": pending_services,
                "service_types": service_types,
                "registrations_today": registrations_today
            }
    
    def log_audit(self, passport_id: str, action: str, details: Dict[str, Any], client_ip: str = None):
        """Log audit entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO passport_audit_log (passport_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            """, (passport_id, action, json.dumps(details), client_ip))
            conn.commit()

# FastAPI app initialization
app = FastAPI(
    title="ZmartBot Passport Service",
    description="Comprehensive Service Registration & Identity Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
passport_service = PassportService()

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.client.host

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token (simplified for demo)"""
    # In production, implement proper JWT/API key validation
    if credentials.credentials != "zmartbot-passport-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials

# Health endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "passport-service", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Test database connection
        stats = passport_service.get_stats()
        return {"status": "ready", "service": "passport-service", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/metrics", tags=["Health"])
async def metrics():
    """Prometheus metrics endpoint"""
    stats = passport_service.get_stats()
    metrics_text = f"""
# HELP passport_services_total Total registered services
# TYPE passport_services_total counter
passport_services_total {stats['total_services']}

# HELP passport_services_active Active services
# TYPE passport_services_active gauge
passport_services_active {stats['active_services']}

# HELP passport_services_pending Pending services
# TYPE passport_services_pending gauge
passport_services_pending {stats['pending_services']}

# HELP passport_registrations_today Registrations today
# TYPE passport_registrations_today counter
passport_registrations_today {stats['registrations_today']}
    """
    return JSONResponse(content=metrics_text, media_type="text/plain")

# API endpoints
@app.post("/api/passport/register", response_model=Dict[str, Any], tags=["Registration"])
async def register_service(
    request: ServiceRegistrationRequest, 
    client_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Register new service and issue Passport ID (Authenticated)"""
    try:
        client_ip = get_client_ip(client_request)
        result = passport_service.register_service(request, client_ip)
        # Log the passport assignment
        print(f"🛂 Service {request.service_name} registered with Passport ID: {result['passport_id']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/passport/register-public", response_model=Dict[str, Any], tags=["Public Registration"])
async def register_service_public(
    request: ServiceRegistrationRequest, 
    client_request: Request
):
    """Register new service and issue Passport ID (Public endpoint for service self-registration)"""
    try:
        client_ip = get_client_ip(client_request)
        result = passport_service.register_service(request, client_ip)
        # Log the passport assignment with clear message
        print(f"🛂 ✅ PASSPORT ASSIGNED: Service '{request.service_name}' → Passport ID: {result['passport_id']} (Port: {request.port})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/passport/services", tags=["Services"])
async def get_all_services(credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    """Get all registered services with Passport IDs (Authenticated)"""
    try:
        services = passport_service.get_all_services()
        return {"services": services, "count": len(services)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")

@app.get("/api/passport/services-public", tags=["Public Services"])
async def get_services_public():
    """Get basic service count and active services (Public endpoint for dashboard)"""
    try:
        stats = passport_service.get_stats()
        return {
            "total_services": stats["total_services"], 
            "active_services": stats["active_services"],
            "service_types": stats["service_types"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch service stats: {str(e)}")

@app.get("/api/passport/services/{passport_id}", tags=["Services"])
async def get_service_by_passport_id(
    passport_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get service details by Passport ID"""
    service = passport_service.get_service_by_passport(passport_id)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service with Passport ID {passport_id} not found")
    return service

@app.post("/api/passport/services/{passport_id}/activate", tags=["Lifecycle"])
async def activate_service(
    passport_id: str,
    client_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Activate registered service"""
    client_ip = get_client_ip(client_request)
    success = passport_service.activate_service(passport_id, client_ip)
    if not success:
        raise HTTPException(status_code=404, detail=f"Service {passport_id} not found or not in REGISTERED state")
    return {"message": f"Service {passport_id} activated successfully"}

@app.post("/api/passport/services/{passport_id}/deactivate", tags=["Lifecycle"])
async def deactivate_service(
    passport_id: str,
    client_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Deactivate service"""
    client_ip = get_client_ip(client_request)
    success = passport_service.deactivate_service(passport_id, client_ip)
    if not success:
        raise HTTPException(status_code=404, detail=f"Service {passport_id} not found or not active")
    return {"message": f"Service {passport_id} deactivated successfully"}

@app.delete("/api/passport/services/{passport_id}", tags=["Lifecycle"])
async def unregister_service(
    passport_id: str,
    client_request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Unregister service and revoke Passport ID"""
    client_ip = get_client_ip(client_request)
    success = passport_service.unregister_service(passport_id, client_ip)
    if not success:
        raise HTTPException(status_code=404, detail=f"Service {passport_id} not found")
    return {"message": f"Service {passport_id} unregistered successfully"}

@app.get("/api/passport/audit/{passport_id}", tags=["Audit"])
async def get_audit_trail(
    passport_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get service audit trail"""
    audit_trail = passport_service.get_audit_trail(passport_id)
    return {"passport_id": passport_id, "audit_trail": audit_trail, "entries": len(audit_trail)}

@app.get("/api/passport/stats", response_model=PassportStatsResponse, tags=["Statistics"])
async def get_passport_stats(credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    """Get registration statistics"""
    try:
        stats = passport_service.get_stats()
        return PassportStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ZmartBot Passport Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8620, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("🛂 Starting ZmartBot Passport Service...")
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        "passport_service:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()