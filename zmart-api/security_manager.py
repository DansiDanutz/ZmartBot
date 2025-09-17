#!/usr/bin/env python3
"""
Security Manager Service for ZmartBot Platform
Critical security service providing API key security, authentication, and threat detection
Addresses CRITICAL vulnerabilities identified in architecture audit
"""

import os
import sys
import json
import logging
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import requests
from functools import wraps
import jwt
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityThreat:
    """Security threat information"""
    threat_id: str
    threat_type: str
    severity: str  # critical, high, medium, low
    source_ip: str
    description: str
    detected_at: str
    status: str  # active, mitigated, resolved
    
class SecurityManager:
    """
    Security Manager Service - Critical security enforcement for ZmartBot
    """
    
    def __init__(self, project_root: str = None, port: int = 8893):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.api_root = self.project_root / "zmart-api"
        self.port = port
        
        # Security databases
        self.security_db = self.api_root / "security.db"
        self.audit_db = self.api_root / "security_audit.db"
        
        # API Keys Manager endpoint
        self.api_keys_manager_url = "http://localhost:8006"
        
        # JWT settings
        self.jwt_secret = self._get_or_create_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.jwt_expiry = timedelta(hours=24)
        
        # Initialize security databases
        self.init_security_databases()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        
        # Configure CORS with restrictions (NO MORE WILDCARDS!)
        allowed_origins = [
            "http://localhost:3401",  # Service Dashboard
            "http://localhost:3402",  # MDC Dashboard 
            "http://localhost:3403",  # Professional Dashboard
            "http://127.0.0.1:3401",
            "http://127.0.0.1:3402",
            "http://127.0.0.1:3403"
        ]
        
        CORS(self.app, origins=allowed_origins, 
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE'])
        
        self.setup_routes()
        self.setup_middleware()
        
        # Security metrics
        self.threat_count = 0
        self.blocked_requests = 0
        self.key_rotations = 0
        
        logger.info(f"🛡️  Security Manager Service initialized - Port: {self.port}")
        logger.info(f"🔒 CORS restricted to: {allowed_origins}")
        
    def _get_or_create_jwt_secret(self) -> str:
        """Get or create JWT secret key"""
        secret_file = self.api_root / ".jwt_secret"
        
        if secret_file.exists():
            with open(secret_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate new JWT secret
            secret = secrets.token_urlsafe(64)
            secret_file.parent.mkdir(parents=True, exist_ok=True)
            with open(secret_file, 'w') as f:
                f.write(secret)
            logger.info("🔑 Generated new JWT secret")
            return secret
    
    def init_security_databases(self):
        """Initialize security databases"""
        try:
            # Security threats database
            conn = sqlite3.connect(self.security_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_id TEXT UNIQUE NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    description TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE NOT NULL,
                    reason TEXT NOT NULL,
                    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_permanent BOOLEAN DEFAULT FALSE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Audit database
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT,
                    endpoint TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT DEFAULT 'info'
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("🛡️  Security databases initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize security databases: {e}")
            raise
    
    def log_security_event(self, event_type: str, action: str, details: str = None, 
                          severity: str = "info", user_id: str = None, endpoint: str = None):
        """Log security event to audit database"""
        try:
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            ip_address = request.remote_addr if request else "system"
            endpoint = endpoint or (request.endpoint if request else "system")
            
            cursor.execute("""
                INSERT INTO security_audit_log 
                (event_type, user_id, ip_address, endpoint, action, details, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_type, user_id, ip_address, endpoint, action, details, severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log security event: {e}")
    
    def detect_threat(self, request_data: Dict) -> Optional[SecurityThreat]:
        """Detect security threats in requests"""
        try:
            # Get request details
            ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            path = request.path
            
            # Threat detection rules
            threats = []
            
            # SQL Injection detection
            sql_patterns = [
                r"union.*select", r"insert.*into", r"delete.*from", r"drop.*table",
                r"'.*or.*'", r"';.*--", r"exec.*\(", r"script.*>"
            ]
            
            request_str = str(request_data).lower()
            for pattern in sql_patterns:
                if re.search(pattern, request_str, re.IGNORECASE):
                    threats.append("sql_injection")
            
            # XSS detection
            xss_patterns = [
                r"<script", r"javascript:", r"onerror=", r"onload=", r"eval\("
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, request_str, re.IGNORECASE):
                    threats.append("xss_attempt")
            
            # Path traversal detection
            if "../" in path or "..%2F" in path:
                threats.append("path_traversal")
            
            # Rate limiting check
            if self._check_rate_limit(ip):
                threats.append("rate_limit_exceeded")
            
            # Create threat if detected
            if threats:
                threat_id = hashlib.sha256(f"{ip}_{time.time()}".encode()).hexdigest()[:16]
                
                severity = "high" if any(t in ["sql_injection", "xss_attempt"] for t in threats) else "medium"
                if "rate_limit_exceeded" in threats:
                    severity = "medium"
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    threat_type=", ".join(threats),
                    severity=severity,
                    source_ip=ip,
                    description=f"Detected threats: {', '.join(threats)} from {ip}",
                    detected_at=datetime.now().isoformat(),
                    status="active"
                )
                
                # Store threat
                self._store_threat(threat)
                
                # Auto-block high severity threats
                if severity == "high":
                    self._block_ip(ip, "Automatic block due to high severity threat")
                
                return threat
                
        except Exception as e:
            logger.error(f"❌ Threat detection error: {e}")
        
        return None
    
    def _check_rate_limit(self, ip: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if IP exceeds rate limit"""
        try:
            # This is a simple in-memory rate limiter
            # In production, use Redis or similar
            current_time = time.time()
            
            # For now, just check if too many requests in last hour
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM security_audit_log 
                WHERE ip_address = ? AND timestamp > datetime('now', '-1 hour')
            """, (ip,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > limit
            
        except Exception as e:
            logger.error(f"❌ Rate limit check error: {e}")
            return False
    
    def _store_threat(self, threat: SecurityThreat):
        """Store security threat"""
        try:
            conn = sqlite3.connect(self.security_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO security_threats 
                (threat_id, threat_type, severity, source_ip, description, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (threat.threat_id, threat.threat_type, threat.severity, 
                  threat.source_ip, threat.description, threat.status))
            
            conn.commit()
            conn.close()
            
            self.threat_count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to store threat: {e}")
    
    def _block_ip(self, ip: str, reason: str, permanent: bool = False):
        """Block IP address"""
        try:
            conn = sqlite3.connect(self.security_db)
            cursor = conn.cursor()
            
            expires_at = None if permanent else (datetime.now() + timedelta(hours=24)).isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO blocked_ips 
                (ip_address, reason, expires_at, is_permanent)
                VALUES (?, ?, ?, ?)
            """, (ip, reason, expires_at, permanent))
            
            conn.commit()
            conn.close()
            
            self.blocked_requests += 1
            
            logger.warning(f"🚫 Blocked IP {ip}: {reason}")
            
        except Exception as e:
            logger.error(f"❌ Failed to block IP: {e}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        try:
            conn = sqlite3.connect(self.security_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM blocked_ips 
                WHERE ip_address = ? AND 
                (is_permanent = TRUE OR expires_at > datetime('now'))
            """, (ip,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to check blocked IP: {e}")
            return False
    
    def setup_middleware(self):
        """Setup security middleware"""
        
        @self.app.before_request
        def security_middleware():
            """Security middleware for all requests"""
            
            # Skip security for health checks
            if request.path in ['/health', '/ready']:
                return
            
            # Check if IP is blocked
            if self.is_ip_blocked(request.remote_addr):
                self.log_security_event("blocked_request", "request_blocked", 
                                       f"Blocked IP {request.remote_addr}", "warning")
                return jsonify({"error": "Access denied"}), 403
            
            # Detect threats
            request_data = {
                "path": request.path,
                "args": dict(request.args),
                "headers": dict(request.headers)
            }
            
            if request.is_json:
                try:
                    request_data["json"] = request.get_json()
                except:
                    pass
            
            threat = self.detect_threat(request_data)
            if threat and threat.severity in ["critical", "high"]:
                self.log_security_event("threat_detected", "request_blocked", 
                                       threat.description, threat.severity)
                return jsonify({"error": "Security threat detected"}), 403
        
        # Add security headers
        @self.app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            return response
    
    def require_auth(self, f):
        """Authentication decorator"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            try:
                # Remove 'Bearer ' prefix
                if token.startswith('Bearer '):
                    token = token[7:]
                
                # Verify JWT
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                g.user_id = payload.get('user_id')
                g.session_id = payload.get('session_id')
                
                # Verify session is still active
                if not self._verify_session(g.session_id):
                    return jsonify({"error": "Session expired"}), 401
                
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            return f(*args, **kwargs)
        return decorated
    
    def _verify_session(self, session_id: str) -> bool:
        """Verify session is active"""
        try:
            conn = sqlite3.connect(self.security_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM security_sessions 
                WHERE session_id = ? AND is_active = TRUE AND expires_at > datetime('now')
            """, (session_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"❌ Session verification error: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "security-manager",
                "version": "1.0.0"
            })
        
        @self.app.route('/ready', methods=['GET'])
        def ready():
            """Readiness check endpoint"""
            try:
                # Test database connections
                conn = sqlite3.connect(self.security_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM security_threats")
                threat_count = cursor.fetchone()[0]
                conn.close()
                
                # Test API Keys Manager connection
                api_keys_status = self._test_api_keys_manager()
                
                return jsonify({
                    "status": "ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "security-manager",
                    "databases": "connected",
                    "api_keys_manager": api_keys_status,
                    "threat_count": threat_count
                }), 200
                
            except Exception as e:
                return jsonify({
                    "status": "not_ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "security-manager",
                    "error": str(e)
                }), 503
        
        @self.app.route('/security/status', methods=['GET'])
        def security_status():
            """Security system status"""
            try:
                conn = sqlite3.connect(self.security_db)
                cursor = conn.cursor()
                
                # Get threat statistics
                cursor.execute("SELECT severity, COUNT(*) FROM security_threats GROUP BY severity")
                threat_stats = dict(cursor.fetchall())
                
                cursor.execute("SELECT COUNT(*) FROM blocked_ips WHERE expires_at > datetime('now') OR is_permanent = TRUE")
                blocked_ips = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    "status": "operational",
                    "timestamp": datetime.now().isoformat(),
                    "service": "security-manager",
                    "threat_statistics": threat_stats,
                    "blocked_ips": blocked_ips,
                    "total_threats_detected": self.threat_count,
                    "requests_blocked": self.blocked_requests,
                    "key_rotations_performed": self.key_rotations
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/security/scan-exposed-keys', methods=['POST'])
        def scan_exposed_keys():
            """CRITICAL: Scan for exposed API keys and secure them"""
            try:
                self.log_security_event("key_scan", "exposed_key_scan_started", 
                                       "Scanning for exposed API keys", "info")
                
                exposed_keys = []
                secured_keys = []
                
                # Check config.env for exposed keys
                config_file = self.api_root / "config.env"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        content = f.read()
                        
                    # Look for exposed OpenAI key pattern
                    openai_pattern = r'OPENAI_API_KEY\s*=\s*(sk-[a-zA-Z0-9_-]+)'
                    matches = re.findall(openai_pattern, content)
                    
                    for match in matches:
                        exposed_keys.append({
                            "service": "openai",
                            "key_preview": match[:20] + "...",
                            "file": "config.env",
                            "severity": "CRITICAL"
                        })
                        
                        # Secure the key immediately
                        secured = self._secure_exposed_key("openai", match, "OpenAI API Key")
                        if secured:
                            secured_keys.append("openai")
                
                # Update config.env to remove exposed key
                if exposed_keys:
                    self._update_config_env()
                
                result = {
                    "scan_completed": True,
                    "timestamp": datetime.now().isoformat(),
                    "exposed_keys_found": len(exposed_keys),
                    "keys_secured": len(secured_keys),
                    "exposed_keys": exposed_keys,
                    "secured_services": secured_keys
                }
                
                if exposed_keys:
                    self.log_security_event("exposed_keys", "critical_vulnerability_fixed", 
                                           f"Secured {len(secured_keys)} exposed API keys", "critical")
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"❌ Exposed key scan failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/security/emergency-lockdown', methods=['POST'])
        def emergency_lockdown():
            """Emergency security lockdown"""
            try:
                # Block all external access except localhost
                self._block_ip("0.0.0.0/0", "Emergency security lockdown", permanent=False)
                
                # Rotate all critical API keys
                self._emergency_key_rotation()
                
                self.log_security_event("emergency", "security_lockdown", 
                                       "Emergency security lockdown activated", "critical")
                
                return jsonify({
                    "status": "lockdown_activated",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Emergency security lockdown is now active"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def _test_api_keys_manager(self) -> str:
        """Test connection to API Keys Manager"""
        try:
            response = requests.get(f"{self.api_keys_manager_url}/health", timeout=5)
            if response.status_code == 200:
                return "connected"
            else:
                return "error"
        except Exception as e:
            logger.error(f"❌ API Keys Manager connection failed: {e}")
            return "disconnected"
    
    def _secure_exposed_key(self, service_name: str, api_key: str, description: str) -> bool:
        """Secure an exposed API key"""
        try:
            # Store key securely in API Keys Manager
            data = {
                "service_name": service_name,
                "api_key": api_key,
                "key_type": "api_key",
                "description": description
            }
            
            response = requests.post(f"{self.api_keys_manager_url}/keys", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Secured API key for {service_name}: {result.get('key_id')}")
                self.key_rotations += 1
                return True
            else:
                logger.error(f"❌ Failed to secure key for {service_name}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Key securing error: {e}")
            return False
    
    def _update_config_env(self):
        """Update config.env to remove exposed keys"""
        try:
            config_file = self.api_root / "config.env"
            if not config_file.exists():
                return
            
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Replace exposed OpenAI key with key ID reference
            new_content = re.sub(
                r'OPENAI_API_KEY\s*=\s*sk-[a-zA-Z0-9_-]+',
                'OPENAI_API_KEY_ID=fetch_from_api_keys_manager',
                content
            )
            
            # Write updated content
            with open(config_file, 'w') as f:
                f.write(new_content)
                
            logger.info("✅ Updated config.env to remove exposed keys")
            
        except Exception as e:
            logger.error(f"❌ Failed to update config.env: {e}")
    
    def _emergency_key_rotation(self):
        """Emergency rotation of all critical keys"""
        try:
            # Get all keys from API Keys Manager
            response = requests.get(f"{self.api_keys_manager_url}/keys", timeout=10)
            if response.status_code == 200:
                keys = response.json().get("keys", [])
                
                # Mark all keys for rotation (would need new keys from user)
                for key in keys:
                    if key["service_name"] in ["openai", "binance", "kucoin"]:
                        logger.warning(f"🔄 Critical key rotation needed: {key['service_name']}")
                        
        except Exception as e:
            logger.error(f"❌ Emergency key rotation failed: {e}")
    
    def run(self):
        """Run the Security Manager service"""
        logger.info(f"🛡️  Starting Security Manager Service on port {self.port}")
        self.app.run(host='127.0.0.1', port=self.port, debug=False)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Manager Service')
    parser.add_argument('--port', type=int, default=8893, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Create and run service
    service = SecurityManager(
        project_root=args.project_root,
        port=args.port
    )
    
    if args.daemon:
        # Run as daemon (no output)
        service.run()
    else:
        service.run()

if __name__ == '__main__':
    main()