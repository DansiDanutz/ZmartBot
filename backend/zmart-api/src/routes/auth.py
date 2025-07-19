"""
Zmart Trading Bot Platform - Authentication Routes
JWT-based authentication and user management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from src.config.settings import settings
from src.utils.database import redis_set, redis_get, redis_delete

router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Mock user database (replace with actual database)
MOCK_USERS = {
    "admin": {
        "id": "1",
        "username": "admin",
        "email": "admin@zmart.com",
        "full_name": "System Administrator",
        "password_hash": "hashed_password_here",  # In real app, use proper hashing
        "role": "admin",
        "created_at": datetime.utcnow(),
        "last_login": None
    },
    "trader": {
        "id": "2",
        "username": "trader",
        "email": "trader@zmart.com",
        "full_name": "Trading User",
        "password_hash": "hashed_password_here",
        "role": "trader",
        "created_at": datetime.utcnow(),
        "last_login": None
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=settings.JWT_REFRESH_EXPIRATION)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is blacklisted
        is_blacklisted = await redis_get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Get user from database (using mock for now)
        user = MOCK_USERS.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Dependency to require specific role"""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        if current_user.get("role") != required_role and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """User login endpoint"""
    # Mock authentication (replace with proper authentication)
    if user_credentials.username not in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    user = MOCK_USERS[user_credentials.username]
    
    # Mock password check (replace with proper password verification)
    if user_credentials.password != "password":  # In real app, verify against hashed password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Update last login
    user["last_login"] = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    # Store refresh token in Redis
    await redis_set(f"refresh_token:{user['username']}", refresh_token, expire=settings.JWT_REFRESH_EXPIRATION)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRATION
    )

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """User registration endpoint"""
    # Check if username already exists
    if user_data.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user (in real app, hash password and store in database)
    new_user = {
        "id": str(len(MOCK_USERS) + 1),
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": "hashed_password_here",  # In real app, hash the password
        "role": "trader",
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    MOCK_USERS[user_data.username] = new_user
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_data.username})
    refresh_token = create_refresh_token(data={"sub": user_data.username})
    
    # Store refresh token in Redis
    await redis_set(f"refresh_token:{user_data.username}", refresh_token, expire=settings.JWT_REFRESH_EXPIRATION)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_EXPIRATION
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token is in Redis
        stored_token = await redis_get(f"refresh_token:{username}")
        if not stored_token or stored_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username})
        
        # Update refresh token in Redis
        await redis_set(f"refresh_token:{username}", new_refresh_token, expire=settings.JWT_REFRESH_EXPIRATION)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_EXPIRATION
        )
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """User logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just remove the refresh token from Redis
    await redis_delete(f"refresh_token:{current_user['username']}")
    
    return {"message": "Successfully logged out"}

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )

@router.put("/profile")
async def update_profile(
    profile_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update user profile"""
    # In a real implementation, validate and update user data in database
    # For now, we'll just return a success message
    return {"message": "Profile updated successfully"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Change user password"""
    # Mock password verification (replace with proper password verification)
    if password_data.current_password != "password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # In a real implementation, hash the new password and update in database
    # For now, we'll just return a success message
    return {"message": "Password changed successfully"}

@router.get("/users", dependencies=[Depends(require_role("admin"))])
async def get_users():
    """Get all users (admin only)"""
    # In a real implementation, fetch users from database
    # For now, return mock users without sensitive information
    users = []
    for username, user in MOCK_USERS.items():
        users.append({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "created_at": user["created_at"],
            "last_login": user.get("last_login")
        })
    
    return {"users": users} 