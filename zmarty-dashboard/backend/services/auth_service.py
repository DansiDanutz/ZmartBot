from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from models.database import User
from core.config import get_settings

settings = get_settings()

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != token_type:
                return None
                
            return payload
            
        except jwt.PyJWTError:
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
            
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, 
        email: str, 
        password: str, 
        username: str, 
        full_name: Optional[str] = None
    ) -> User:
        """Create new user"""
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Check if username is taken
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already taken")
        
        # Create new user
        hashed_password = self.get_password_hash(password)
        
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            credit_balance=10.00,  # Welcome bonus of 10 credits
            tier="basic"
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Add welcome bonus transaction
        from services.credit_service import CreditService
        credit_service = CreditService(self.db)
        await credit_service.add_credits(
            user_id=user.id,
            amount=10,
            transaction_type="bonus",
            description="Welcome bonus"
        )
        
        return user

    async def update_user(
        self, 
        user_id: uuid.UUID, 
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user information"""
        from sqlalchemy import update
        
        # Remove sensitive fields
        sensitive_fields = ["id", "hashed_password", "credit_balance", "created_at"]
        for field in sensitive_fields:
            update_data.pop(field, None)
        
        if not update_data:
            return await self.get_user_by_id(user_id)
        
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data, updated_at=datetime.utcnow())
            )
            await self.db.commit()
            
            return await self.get_user_by_id(user_id)
            
        except Exception:
            await self.db.rollback()
            return None

    async def change_password(
        self, 
        user_id: uuid.UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password"""
        from sqlalchemy import update
        
        # Get user
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            return False
        
        # Update password
        new_hashed_password = self.get_password_hash(new_password)
        
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(hashed_password=new_hashed_password, updated_at=datetime.utcnow())
            )
            await self.db.commit()
            return True
            
        except Exception:
            await self.db.rollback()
            return False

    async def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """Deactivate user account"""
        from sqlalchemy import update
        
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_active=False, updated_at=datetime.utcnow())
            )
            await self.db.commit()
            return True
            
        except Exception:
            await self.db.rollback()
            return False

    def get_current_user_id(self, token: str) -> Optional[uuid.UUID]:
        """Extract user ID from JWT token"""
        payload = self.verify_token(token)
        if payload:
            try:
                return uuid.UUID(payload.get("sub"))
            except (ValueError, TypeError):
                return None
        return None