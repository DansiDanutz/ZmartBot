#!/usr/bin/env python3
"""
API Keys Manager Server for ZmartBot Platform
Secure storage, rotation, and access control for all external API credentials
"""

import os
import sys
import json
import logging
import argparse
import hashlib
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    """Represents an API key entry"""
    key_id: str
    service_name: str
    encrypted_key: str
    key_type: str
    created_at: str
    expires_at: Optional[str] = None
    last_rotated: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class APIKeysManagerService:
    """
    API Keys Manager Service that provides secure storage and management of API credentials
    """
    
    def __init__(self, project_root: str = None, port: int = 8006):
        self.project_root = Path(project_root) if project_root else Path("../.")
        self.port = port
        self.db_path = self.project_root / "zmart-api" / "api_keys.db"
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize database
        self.init_database()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        logger.info(f"API Keys Manager Service initialized - Port: {self.port}")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.project_root / "zmart-api" / "api_keys_manager" / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new encryption key")
            return key
    
    def init_database(self):
        """Initialize the API keys database"""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create api_keys table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_id TEXT UNIQUE NOT NULL,
                    service_name TEXT NOT NULL,
                    encrypted_key TEXT NOT NULL,
                    key_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_rotated TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    description TEXT
                )
            """)
            
            # Create key_usage_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS key_usage_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("API keys database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def encrypt_key(self, key: str) -> str:
        """Encrypt an API key"""
        return self.cipher_suite.encrypt(key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "api-keys-manager-service"
            })
        
        @self.app.route('/ready', methods=['GET'])
        def ready():
            """Readiness check endpoint"""
            try:
                # Test database connection
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM api_keys")
                count = cursor.fetchone()[0]
                conn.close()
                
                return jsonify({
                    "status": "ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "api-keys-manager-service",
                    "database": "connected",
                    "encryption": "active",
                    "total_keys": count
                }), 200
                
            except Exception as e:
                return jsonify({
                    "status": "not_ready",
                    "timestamp": datetime.now().isoformat(),
                    "service": "api-keys-manager-service",
                    "error": str(e)
                }), 503
        
        @self.app.route('/status', methods=['GET'])
        def status():
            """Complete system status"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get key statistics
                cursor.execute("SELECT COUNT(*) FROM api_keys")
                total_keys = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
                active_keys = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM api_keys WHERE expires_at < datetime('now')")
                expired_keys = cursor.fetchone()[0]
                
                # Get recent usage
                cursor.execute("""
                    SELECT action, COUNT(*) as count 
                    FROM key_usage_log 
                    WHERE timestamp > datetime('now', '-1 hour')
                    GROUP BY action
                """)
                recent_usage = dict(cursor.fetchall())
                
                conn.close()
                
                return jsonify({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "api-keys-manager-service",
                    "total_keys": total_keys,
                    "active_keys": active_keys,
                    "expired_keys": expired_keys,
                    "recent_usage": recent_usage
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                    "service": "api-keys-manager-service",
                    "error": str(e)
                }), 500
        
        @self.app.route('/keys', methods=['GET'])
        def get_keys():
            """Get all API keys (metadata only, no decrypted keys)"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT key_id, service_name, key_type, created_at, expires_at, 
                           last_rotated, is_active, description
                    FROM api_keys 
                    ORDER BY service_name, created_at
                """)
                keys = cursor.fetchall()
                conn.close()
                
                return jsonify({
                    "keys": [
                        {
                            "key_id": row[0],
                            "service_name": row[1],
                            "key_type": row[2],
                            "created_at": row[3],
                            "expires_at": row[4],
                            "last_rotated": row[5],
                            "is_active": bool(row[6]),
                            "description": row[7]
                        }
                        for row in keys
                    ]
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/keys', methods=['POST'])
        def create_key():
            """Create a new API key"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                service_name = data.get('service_name')
                api_key = data.get('api_key')
                key_type = data.get('key_type', 'api_key')
                description = data.get('description')
                expires_at = data.get('expires_at')
                
                if not service_name or not api_key:
                    return jsonify({"error": "service_name and api_key are required"}), 400
                
                # Generate unique key ID
                key_id = hashlib.sha256(f"{service_name}_{api_key}_{datetime.now()}".encode()).hexdigest()[:16]
                
                # Encrypt the API key
                encrypted_key = self.encrypt_key(api_key)
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO api_keys (key_id, service_name, encrypted_key, key_type, 
                                        description, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (key_id, service_name, encrypted_key, key_type, description, expires_at))
                
                # Log the action
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'created', ?, ?)
                """, (key_id, service_name, request.remote_addr, request.headers.get('User-Agent')))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Created API key for service '{service_name}'")
                
                return jsonify({
                    "success": True,
                    "key_id": key_id,
                    "service_name": service_name,
                    "message": f"API key created for {service_name}"
                })
                
            except Exception as e:
                logger.error(f"API key creation failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/keys/<key_id>', methods=['GET'])
        def get_key(key_id):
            """Get a specific API key (decrypted)"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT key_id, service_name, encrypted_key, key_type, created_at, 
                           expires_at, last_rotated, is_active, description
                    FROM api_keys 
                    WHERE key_id = ?
                """, (key_id,))
                key_data = cursor.fetchone()
                conn.close()
                
                if not key_data:
                    return jsonify({"error": f"API key '{key_id}' not found"}), 404
                
                # Decrypt the key
                decrypted_key = self.decrypt_key(key_data[2])
                
                # Log the access
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'accessed', ?, ?)
                """, (key_id, key_data[1], request.remote_addr, request.headers.get('User-Agent')))
                conn.commit()
                conn.close()
                
                return jsonify({
                    "key_id": key_data[0],
                    "service_name": key_data[1],
                    "api_key": decrypted_key,
                    "key_type": key_data[3],
                    "created_at": key_data[4],
                    "expires_at": key_data[5],
                    "last_rotated": key_data[6],
                    "is_active": bool(key_data[7]),
                    "description": key_data[8]
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/keys/<key_id>/rotate', methods=['POST'])
        def rotate_key(key_id):
            """Rotate an API key"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                new_api_key = data.get('new_api_key')
                if not new_api_key:
                    return jsonify({"error": "new_api_key is required"}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get current key info
                cursor.execute("SELECT service_name, encrypted_key FROM api_keys WHERE key_id = ?", (key_id,))
                key_data = cursor.fetchone()
                
                if not key_data:
                    conn.close()
                    return jsonify({"error": f"API key '{key_id}' not found"}), 404
                
                service_name = key_data[0]
                old_encrypted_key = key_data[1]
                
                # Encrypt new key
                new_encrypted_key = self.encrypt_key(new_api_key)
                
                # Update the key
                cursor.execute("""
                    UPDATE api_keys 
                    SET encrypted_key = ?, last_rotated = datetime('now')
                    WHERE key_id = ?
                """, (new_encrypted_key, key_id))
                
                # Log the rotation
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'rotated', ?, ?)
                """, (key_id, service_name, request.remote_addr, request.headers.get('User-Agent')))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Rotated API key for service '{service_name}'")
                
                return jsonify({
                    "success": True,
                    "key_id": key_id,
                    "service_name": service_name,
                    "message": f"API key rotated for {service_name}"
                })
                
            except Exception as e:
                logger.error(f"API key rotation failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/keys/<key_id>', methods=['DELETE'])
        def delete_key(key_id):
            """Delete an API key"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get key info before deletion
                cursor.execute("SELECT service_name FROM api_keys WHERE key_id = ?", (key_id,))
                key_data = cursor.fetchone()
                
                if not key_data:
                    conn.close()
                    return jsonify({"error": f"API key '{key_id}' not found"}), 404
                
                service_name = key_data[0]
                
                # Delete the key
                cursor.execute("DELETE FROM api_keys WHERE key_id = ?", (key_id,))
                
                # Log the deletion
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'deleted', ?, ?)
                """, (key_id, service_name, request.remote_addr, request.headers.get('User-Agent')))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Deleted API key for service '{service_name}'")
                
                return jsonify({
                    "success": True,
                    "key_id": key_id,
                    "service_name": service_name,
                    "message": f"API key deleted for {service_name}"
                })
                
            except Exception as e:
                logger.error(f"API key deletion failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/claude-api', methods=['GET'])
        def get_claude_api():
            """Get Claude API configuration and key"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get Claude API key (prefer premium version if available)
                cursor.execute("""
                    SELECT key_id, service_name, encrypted_key, key_type, created_at, 
                           expires_at, last_rotated, is_active, description
                    FROM api_keys 
                    WHERE service_name IN ('claude_premium', 'claude') AND is_active = 1
                    ORDER BY CASE WHEN service_name = 'claude_premium' THEN 1 ELSE 2 END, created_at DESC
                    LIMIT 1
                """)
                claude_key = cursor.fetchone()
                
                if not claude_key:
                    # Auto-create Claude API key with the provided key
                    api_key = "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"
                    key_id = hashlib.sha256(f"claude_{api_key}_{datetime.now()}".encode()).hexdigest()[:16]
                    encrypted_key = self.encrypt_key(api_key)
                    
                    cursor.execute("""
                        INSERT INTO api_keys (key_id, service_name, encrypted_key, key_type, 
                                            description, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    """, (key_id, 'claude', encrypted_key, 'api_key', 'Claude 3.5 Sonnet API key for Zmarty AI'))
                    
                    # Log the creation
                    cursor.execute("""
                        INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                        VALUES (?, ?, 'auto_created', ?, ?)
                    """, (key_id, 'claude', request.remote_addr, request.headers.get('User-Agent')))
                    
                    conn.commit()
                    decrypted_key = api_key
                    
                    logger.info("Auto-created Claude API key")
                else:
                    decrypted_key = self.decrypt_key(claude_key[2])
                    key_id = claude_key[0]
                
                # Log the access
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'accessed', ?, ?)
                """, (key_id, 'claude', request.remote_addr, request.headers.get('User-Agent')))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "service": "claude",
                    "api_key": decrypted_key,
                    "model": "claude-3-5-sonnet-20241022",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "version": "2023-06-01",
                    "capabilities": [
                        "conversational_ai",
                        "code_generation",
                        "analysis",
                        "mcp_integration",
                        "real_time_chat"
                    ],
                    "status": "active"
                })
                
            except Exception as e:
                logger.error(f"Claude API access failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/openai-api', methods=['GET'])
        def get_openai_api():
            """Get OpenAI API configuration and key"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get OpenAI API key
                cursor.execute("""
                    SELECT key_id, service_name, encrypted_key, key_type, created_at, 
                           expires_at, last_rotated, is_active, description
                    FROM api_keys 
                    WHERE service_name = 'openai' AND is_active = 1
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                openai_key = cursor.fetchone()
                
                if not openai_key:
                    return jsonify({
                        "error": "OpenAI API key not found",
                        "message": "Please add your OpenAI API key to the API manager",
                        "setup_instruction": "POST to /keys with service_name='openai' and your API key"
                    }), 404
                
                decrypted_key = self.decrypt_key(openai_key[2])
                key_id = openai_key[0]
                
                # Log the access
                cursor.execute("""
                    INSERT INTO key_usage_log (key_id, service_name, action, ip_address, user_agent)
                    VALUES (?, ?, 'accessed', ?, ?)
                """, (key_id, 'openai', request.remote_addr, request.headers.get('User-Agent')))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "service": "openai",
                    "api_key": decrypted_key,
                    "model": "gpt-4o",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "capabilities": [
                        "conversational_ai",
                        "advanced_reasoning",
                        "real_time_analysis",
                        "crypto_data_processing"
                    ],
                    "status": "active"
                })
                
            except Exception as e:
                logger.error(f"OpenAI API access failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/apis/all', methods=['GET'])
        def get_all_apis():
            """Get all configured AI API services"""
            try:
                claude_response = get_claude_api()
                openai_response = get_openai_api()
                
                apis = {}
                
                # Add Claude API if available
                if claude_response.status_code == 200:
                    apis['claude'] = claude_response.get_json()
                
                # Add OpenAI API if available
                if openai_response.status_code == 200:
                    apis['openai'] = openai_response.get_json()
                
                return jsonify({
                    "available_apis": apis,
                    "total_configured": len(apis),
                    "services": list(apis.keys())
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def run(self):
        """Run the API Keys Manager service"""
        logger.info(f"Starting API Keys Manager Service on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='API Keys Manager Service')
    parser.add_argument('--port', type=int, default=8006, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    
    args = parser.parse_args()
    
    # Create and run service
    service = APIKeysManagerService(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()
