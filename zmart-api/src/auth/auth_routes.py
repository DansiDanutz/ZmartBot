"""
Authentication Routes
Provides login, logout, and token management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import bcrypt
import sqlite3
import os
from datetime import datetime
import uuid
import logging

from .auth_middleware import auth_manager, get_current_user, check_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = ""

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    created_at: str
    permissions: Dict[str, bool]

# Database operations
def get_user_db():
    """Get database connection for user management"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'users.db')
    return sqlite3.connect(db_path)

def init_user_database():
    """Initialize user database tables"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        """)
        
        # Create user_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone()[0] == 0:
            admin_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, full_name, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (admin_id, "admin", "admin@zmartbot.com", password_hash, "System Administrator", 1))
            
            logger.info("✅ Default admin user created: admin/admin123")
        
        conn.commit()
        conn.close()
        logger.info("✅ User database initialized")
        
    except Exception as e:
        logger.error(f"❌ Error initializing user database: {e}")

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("""
            SELECT id, username, email, password_hash, full_name, is_active, is_admin, 
                   failed_login_attempts, locked_until
            FROM users WHERE username = ? OR email = ?
        """, (username, username))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return None
        
        user_id, username, email, password_hash, full_name, is_active, is_admin, failed_attempts, locked_until = user_data
        
        # Check if account is locked
        if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
            raise HTTPException(status_code=423, detail="Account is temporarily locked")
        
        # Check if account is active
        if not is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            # Increment failed attempts
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET failed_login_attempts = failed_login_attempts + 1
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            conn.close()
            return None
        
        # Reset failed attempts on successful login
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET failed_login_attempts = 0, last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
        
        # Get user permissions
        permissions = {
            "read_alerts": True,
            "create_alerts": True,
            "edit_alerts": True,
            "delete_alerts": True,
            "manage_system": is_admin,
            "view_analytics": True,
            "configure_notifications": True
        }
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "is_admin": is_admin,
            "permissions": permissions
        }
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request, _: bool = Depends(check_rate_limit)):
    """User login endpoint"""
    
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Create session
    session_id = str(uuid.uuid4())
    
    # Create tokens
    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "session_id": session_id,
        "permissions": user["permissions"]
    }
    
    access_token = auth_manager.create_access_token(token_data)
    refresh_token = auth_manager.create_refresh_token(token_data)
    
    # Store refresh token in database
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        
        refresh_token_hash = bcrypt.hashpw(refresh_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO user_sessions (id, user_id, refresh_token_hash, expires_at)
            VALUES (?, ?, ?, datetime('now', '+7 days'))
        """, (session_id, user["user_id"], refresh_token_hash))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error storing session: {e}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """User logout endpoint"""
    
    try:
        # Invalidate session in database
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_sessions SET is_active = 0 
            WHERE id = ? AND user_id = ?
        """, (current_user["session_id"], current_user["user_id"]))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, email, full_name, created_at
            FROM users WHERE id = ?
        """, (current_user["user_id"],))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        username, email, full_name, created_at = user_data
        
        return UserResponse(
            user_id=current_user["user_id"],
            username=username,
            email=email,
            full_name=full_name or "",
            created_at=created_at,
            permissions=current_user["permissions"]
        )
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, req: Request, _: bool = Depends(check_rate_limit)):
    """User registration endpoint"""
    
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE username = ? OR email = ?
        """, (request.username, request.email))
        
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, request.username, request.email, password_hash, request.full_name))
        
        conn.commit()
        
        # Get created user data
        cursor.execute("""
            SELECT username, email, full_name, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        username, email, full_name, created_at = user_data
        
        # Default permissions for new users
        permissions = {
            "read_alerts": True,
            "create_alerts": True,
            "edit_alerts": True,
            "delete_alerts": True,
            "manage_system": False,
            "view_analytics": True,
            "configure_notifications": True
        }
        
        return UserResponse(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name or "",
            created_at=created_at,
            permissions=permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Initialize database on module import
init_user_database()