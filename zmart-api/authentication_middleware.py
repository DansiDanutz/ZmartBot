#!/usr/bin/env python3
"""
Authentication Middleware Service for ZmartBot Platform
Provides JWT-based authentication, session management, and access control
Fixes CRITICAL authentication bypass vulnerability from audit
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
import bcrypt
import jwt
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """User information"""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True

@dataclass
class Session:
    """User session information"""
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    ip_address: str
    user_agent: str
    is_active: bool = True

class AuthenticationMiddleware:
    """
    Authentication Middleware Service - JWT-based auth for ZmartBot
    Fixes CRITICAL authentication bypass vulnerability
    """
    
    def __init__(self, project_root: str = None, port: int = 8894):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.api_root = self.project_root / "zmart-api"
        self.port = port
        
        # Authentication databases
        self.auth_db = self.api_root / "authentication.db"
        self.session_db = self.api_root / "sessions.db"
        
        # JWT settings
        self.jwt_secret = self._get_or_create_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.jwt_expiry = timedelta(hours=24)
        
        # Initialize databases
        self.init_auth_databases()
        self.create_default_users()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        
        # Configure CORS
        allowed_origins = [
            "http://localhost:3401", "http://localhost:3402", "http://localhost:3403",
            "http://127.0.0.1:3401", "http://127.0.0.1:3402", "http://127.0.0.1:3403"
        ]
        CORS(self.app, origins=allowed_origins, supports_credentials=True)
        
        self.setup_routes()
        
        # Authentication metrics
        self.auth_attempts = 0
        self.auth_successes = 0
        self.active_sessions = 0
        
        logger.info(f"🔐 Authentication Middleware initialized - Port: {self.port}")
    
    def _get_or_create_jwt_secret(self) -> str:
        """Get or create JWT secret key"""
        secret_file = self.api_root / ".auth_jwt_secret"
        
        if secret_file.exists():
            with open(secret_file, 'r') as f:
                return f.read().strip()
        else:
            secret = secrets.token_urlsafe(64)
            secret_file.parent.mkdir(parents=True, exist_ok=True)
            with open(secret_file, 'w') as f:
                f.write(secret)
            logger.info("🔑 Generated new JWT secret for authentication")
            return secret
    
    def init_auth_databases(self):
        """Initialize authentication databases"""
        try:
            # Users database
            conn = sqlite3.connect(self.auth_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'viewer',
                    permissions TEXT NOT NULL DEFAULT '["read"]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    username TEXT,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Sessions database
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    jwt_token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revoked_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jwt_token_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("🔐 Authentication databases initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize auth databases: {e}")
            raise
    
    def create_default_users(self):
        """Create default system users"""
        try:
            conn = sqlite3.connect(self.auth_db)
            cursor = conn.cursor()
            
            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Create admin user
                admin_password = "zmartbot_admin_2025"  # Change in production!
                password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
                admin_id = hashlib.sha256(f"admin_{datetime.now()}".encode()).hexdigest()[:16]
                
                cursor.execute("""
                    INSERT INTO users (user_id, username, password_hash, role, permissions)
                    VALUES (?, 'admin', ?, 'admin', ?)
                """, (admin_id, password_hash, json.dumps(["read", "write", "admin", "security"])))
                
                logger.info("🔐 Created default admin user: admin / zmartbot_admin_2025")
            
            # Check if service user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'service'")
            if cursor.fetchone()[0] == 0:
                # Create service user
                service_password = "zmartbot_service_2025"
                password_hash = bcrypt.hashpw(service_password.encode(), bcrypt.gensalt()).decode()
                service_id = hashlib.sha256(f"service_{datetime.now()}".encode()).hexdigest()[:16]
                
                cursor.execute("""
                    INSERT INTO users (user_id, username, password_hash, role, permissions)
                    VALUES (?, 'service', ?, 'service', ?)
                """, (service_id, password_hash, json.dumps(["service", "api", "read", "write"])))
                
                logger.info("🔐 Created default service user: service / zmartbot_service_2025")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to create default users: {e}")
    
    def log_auth_event(self, user_id: str, username: str, action: str, success: bool, 
                      details: str = None, ip: str = None, user_agent: str = None):
        """Log authentication event"""
        try:
            conn = sqlite3.connect(self.auth_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO auth_audit_log 
                (user_id, username, action, ip_address, user_agent, success, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, action, ip, user_agent, success, details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log auth event: {e}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect(self.auth_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, password_hash, role, permissions, created_at, last_login, is_active
                FROM users WHERE username = ? AND is_active = TRUE
            """, (username,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode(), user_data[2].encode()):
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = datetime('now') WHERE user_id = ?
                """, (user_data[0],))
                conn.commit()
                
                # Create User object
                user = User(
                    user_id=user_data[0],
                    username=user_data[1],
                    role=user_data[3],
                    permissions=json.loads(user_data[4]),
                    created_at=user_data[5],
                    last_login=user_data[6],
                    is_active=bool(user_data[7])
                )
                
                conn.close()
                return user
            else:
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    def create_jwt_token(self, user: User, session_id: str) -> str:
        """Create JWT token for user"""
        try:
            payload = {
                "user_id": user.user_id,
                "username": user.username,
                "session_id": session_id,
                "role": user.role,
                "permissions": user.permissions,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + self.jwt_expiry
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"❌ JWT creation error: {e}")
            return None
    
    def validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token"""
        try:
            # Check if token is revoked
            if self.is_token_revoked(token):
                return None
            
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("🔒 Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("🔒 Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"❌ JWT validation error: {e}")
            return None
    
    def create_session(self, user: User, jwt_token: str, ip: str, user_agent: str) -> str:
        """Create user session"""
        try:
            session_id = hashlib.sha256(f"{user.user_id}_{time.time()}".encode()).hexdigest()[:16]
            expires_at = (datetime.now() + self.jwt_expiry).isoformat()
            
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO active_sessions 
                (session_id, user_id, jwt_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user.user_id, jwt_token, expires_at, ip, user_agent))
            
            conn.commit()
            conn.close()
            
            self.active_sessions += 1
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            return None
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session is active"""
        try:
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM active_sessions 
                WHERE session_id = ? AND is_active = TRUE AND expires_at > datetime('now')
            """, (session_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"❌ Session validation error: {e}")
            return False
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked"""
        try:
            # Get token ID from payload
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm], options={"verify_exp": False})
            token_id = hashlib.sha256(token.encode()).hexdigest()[:16]
            
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM revoked_tokens WHERE jwt_token_id = ?
            """, (token_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            return False  # If we can't check, assume not revoked
    
    def revoke_token(self, token: str, reason: str = "Manual revocation"):
        """Revoke JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm], options={"verify_exp": False})
            token_id = hashlib.sha256(token.encode()).hexdigest()[:16]
            
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO revoked_tokens (jwt_token_id, user_id, reason)
                VALUES (?, ?, ?)
            """, (token_id, payload.get("user_id"), reason))
            
            # Deactivate session
            cursor.execute("""
                UPDATE active_sessions SET is_active = FALSE 
                WHERE session_id = ?
            """, (payload.get("session_id"),))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🔒 Token revoked for user {payload.get('username')}: {reason}")
            
        except Exception as e:
            logger.error(f"❌ Token revocation error: {e}")
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "authentication-middleware",
                "version": "1.0.0"
            })
        
        @self.app.route('/ready', methods=['GET'])
        def ready():
            """Readiness check endpoint"""
            try:
                # Test database connections
                conn = sqlite3.connect(self.auth_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                conn.close()
                
                conn = sqlite3.connect(self.session_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active = TRUE")
                session_count = cursor.fetchone()[0]
                conn.close()
                
                return jsonify({
                    "status": "ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "authentication-middleware",
                    "databases": "connected",
                    "users": user_count,
                    "active_sessions": session_count
                }), 200
                
            except Exception as e:
                return jsonify({
                    "status": "not_ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "authentication-middleware",
                    "error": str(e)
                }), 503
        
        @self.app.route('/auth/login', methods=['POST'])
        def login():
            """User login endpoint"""
            try:
                data = request.get_json()
                if not data or not data.get('username') or not data.get('password'):
                    return jsonify({"error": "Username and password required"}), 400
                
                username = data['username']
                password = data['password']
                ip = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
                self.auth_attempts += 1
                
                # Authenticate user
                user = self.authenticate_user(username, password)
                if not user:
                    self.log_auth_event(None, username, "login_failed", False, 
                                       "Invalid credentials", ip, user_agent)
                    return jsonify({"error": "Invalid credentials"}), 401
                
                # Create session and JWT
                session_id = hashlib.sha256(f"{user.user_id}_{time.time()}".encode()).hexdigest()[:16]
                jwt_token = self.create_jwt_token(user, session_id)
                
                if not jwt_token:
                    return jsonify({"error": "Token generation failed"}), 500
                
                # Create session
                session_id = self.create_session(user, jwt_token, ip, user_agent)
                
                self.auth_successes += 1
                self.log_auth_event(user.user_id, username, "login_success", True, 
                                   f"Session: {session_id}", ip, user_agent)
                
                return jsonify({
                    "success": True,
                    "token": jwt_token,
                    "session_id": session_id,
                    "user": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "role": user.role,
                        "permissions": user.permissions
                    },
                    "expires_at": (datetime.now() + self.jwt_expiry).isoformat()
                })
                
            except Exception as e:
                logger.error(f"❌ Login error: {e}")
                return jsonify({"error": "Authentication service error"}), 500
        
        @self.app.route('/auth/validate', methods=['POST'])
        def validate_token():
            """Validate JWT token"""
            try:
                data = request.get_json()
                token = data.get('token') if data else None
                
                # Try header if not in body
                if not token:
                    auth_header = request.headers.get('Authorization')
                    if auth_header and auth_header.startswith('Bearer '):
                        token = auth_header[7:]
                
                if not token:
                    return jsonify({"error": "Token required"}), 400
                
                payload = self.validate_jwt_token(token)
                if not payload:
                    return jsonify({"error": "Invalid or expired token"}), 401
                
                # Validate session
                session_id = payload.get('session_id')
                if not self.validate_session(session_id):
                    return jsonify({"error": "Session expired"}), 401
                
                return jsonify({
                    "valid": True,
                    "user_id": payload.get('user_id'),
                    "username": payload.get('username'),
                    "role": payload.get('role'),
                    "permissions": payload.get('permissions'),
                    "expires_at": datetime.fromtimestamp(payload.get('exp')).isoformat()
                })
                
            except Exception as e:
                logger.error(f"❌ Token validation error: {e}")
                return jsonify({"error": "Validation service error"}), 500
        
        @self.app.route('/auth/logout', methods=['POST'])
        def logout():
            """User logout endpoint"""
            try:
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Authorization header required"}), 400
                
                token = auth_header[7:]
                payload = self.validate_jwt_token(token)
                
                if payload:
                    # Revoke token and session
                    self.revoke_token(token, "User logout")
                    self.log_auth_event(payload.get('user_id'), payload.get('username'), 
                                       "logout", True, "User initiated logout", 
                                       request.remote_addr, request.headers.get('User-Agent'))
                
                return jsonify({
                    "success": True,
                    "message": "Logged out successfully"
                })
                
            except Exception as e:
                logger.error(f"❌ Logout error: {e}")
                return jsonify({"error": "Logout service error"}), 500
        
        @self.app.route('/auth/status', methods=['GET'])
        def auth_status():
            """Authentication service status"""
            try:
                # Get statistics
                conn = sqlite3.connect(self.auth_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
                active_users = cursor.fetchone()[0]
                conn.close()
                
                conn = sqlite3.connect(self.session_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active = TRUE AND expires_at > datetime('now')")
                active_sessions = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM revoked_tokens WHERE revoked_at > datetime('now', '-24 hours')")
                revoked_tokens_24h = cursor.fetchone()[0]
                conn.close()
                
                success_rate = (self.auth_successes / self.auth_attempts * 100) if self.auth_attempts > 0 else 0
                
                return jsonify({
                    "status": "operational",
                    "timestamp": datetime.now().isoformat(),
                    "service": "authentication-middleware",
                    "active_users": active_users,
                    "active_sessions": active_sessions,
                    "auth_attempts_total": self.auth_attempts,
                    "auth_successes_total": self.auth_successes,
                    "success_rate_percent": round(success_rate, 2),
                    "tokens_revoked_24h": revoked_tokens_24h,
                    "jwt_expiry_hours": self.jwt_expiry.total_seconds() / 3600
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def run(self):
        """Run the Authentication Middleware service"""
        logger.info(f"🔐 Starting Authentication Middleware on port {self.port}")
        logger.info(f"🔐 Default admin user: admin / zmartbot_admin_2025")
        logger.info(f"🔐 Default service user: service / zmartbot_service_2025")
        self.app.run(host='127.0.0.1', port=self.port, debug=False)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Authentication Middleware Service')
    parser.add_argument('--port', type=int, default=8894, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Create and run service
    service = AuthenticationMiddleware(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()