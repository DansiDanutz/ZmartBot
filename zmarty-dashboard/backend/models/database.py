from sqlalchemy import Column, String, Integer, Decimal, DateTime, Boolean, Text, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    credit_balance = Column(Decimal(10, 2), default=0.00, nullable=False)
    tier = Column(String(50), default="basic", nullable=False)  # basic, premium, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    zmarty_requests = relationship("ZmartyRequest", back_populates="user")
    payment_history = relationship("PaymentHistory", back_populates="user")

class CreditPackage(Base):
    __tablename__ = "credit_packages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)  # "Starter", "Professional", "Enterprise"
    description = Column(Text)
    credits = Column(Integer, nullable=False)
    price = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    discount_percentage = Column(Decimal(5, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, usage, refund, bonus
    amount = Column(Integer, nullable=False)  # Credits amount (positive for add, negative for deduct)
    description = Column(String(500))
    reference_id = Column(UUID(as_uuid=True))  # Reference to payment or request
    balance_before = Column(Decimal(10, 2))
    balance_after = Column(Decimal(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")

class ZmartyRequest(Base):
    __tablename__ = "zmarty_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_type = Column(String(100), nullable=False)  # query, trading_analysis, market_signals, ai_predictions
    query = Column(Text, nullable=False)
    parameters = Column(Text)  # JSON string of additional parameters
    credits_cost = Column(Integer, nullable=False)
    response = Column(Text)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_time = Column(Integer)  # Processing time in seconds
    quality_score = Column(Decimal(3, 2))  # User rating of response quality
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="zmarty_requests")

class PaymentHistory(Base):
    __tablename__ = "payment_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    package_id = Column(UUID(as_uuid=True), ForeignKey("credit_packages.id"), nullable=False)
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50))  # stripe, paypal, crypto
    payment_intent_id = Column(String(255))  # Stripe payment intent ID
    status = Column(String(50), default="pending")  # pending, completed, failed, refunded
    credits_awarded = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payment_history")
    package = relationship("CreditPackage")

class ConversationMemory(Base):
    __tablename__ = "conversation_memory"
    
    id = Column(String(255), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(255), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False)  # conversation_turn, fact, preference, context
    content = Column(Text, nullable=False)  # JSON content
    importance = Column(Integer, default=5)  # 1-10 importance scale
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(500))
    is_public = Column(Boolean, default=False)  # Whether this config can be accessed by frontend
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())