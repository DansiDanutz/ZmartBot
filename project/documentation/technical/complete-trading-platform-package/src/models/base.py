"""
Trade Strategy Module - Base Models
===================================

SQLAlchemy base models and common model utilities for the Trade Strategy module.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar, Generic
from decimal import Decimal

from sqlalchemy import (
    Column, String, DateTime, Boolean, Text, Integer, 
    Numeric, JSON, UUID, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

# Type variables for generic models
ModelType = TypeVar("ModelType", bound="BaseModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound="BaseModel")
UpdateSchemaType = TypeVar("UpdateSchemaType", bound="BaseModel")


class BaseTable:
    """Base class for all database tables with common fields and methods."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    # Primary key
    id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    def get_column_names(cls) -> list[str]:
        """Get list of column names for the model."""
        return [column.name for column in cls.__table__.columns]
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


# Create the declarative base
Base = declarative_base(cls=BaseTable)


class AuditMixin:
    """Mixin for tables that need audit trail functionality."""
    
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    def set_audit_fields(self, user_id: Optional[uuid.UUID] = None) -> None:
        """Set audit fields for create/update operations."""
        if not self.created_by:
            self.created_by = user_id
        self.updated_by = user_id


class SoftDeleteMixin:
    """Mixin for tables that support soft deletion."""
    
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    def soft_delete(self, user_id: Optional[uuid.UUID] = None) -> None:
        """Perform soft deletion."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = user_id
    
    def restore(self) -> None:
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class VersionMixin:
    """Mixin for tables that need version tracking."""
    
    version = Column(Integer, nullable=False, default=1)
    
    def increment_version(self) -> None:
        """Increment version number."""
        self.version += 1


class MetadataMixin:
    """Mixin for tables that store JSON metadata."""
    
    metadata = Column(JSON, nullable=False, default=dict)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def remove_metadata(self, key: str) -> None:
        """Remove metadata key."""
        if self.metadata and key in self.metadata:
            del self.metadata[key]


# Pydantic base models for API schemas
class BaseSchema(BaseModel):
    """Base Pydantic model for API schemas."""
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class BaseCreateSchema(BaseSchema):
    """Base schema for create operations."""
    pass


class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations."""
    pass


class BaseResponseSchema(TimestampSchema):
    """Base schema for API responses."""
    id: uuid.UUID = Field(..., description="Unique identifier")


class PaginationParams(BaseSchema):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(GenericModel, Generic[ModelType]):
    """Generic paginated response model."""
    items: list[ModelType] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    @validator('pages', always=True)
    def calculate_pages(cls, v, values):
        """Calculate total pages based on total and size."""
        total = values.get('total', 0)
        size = values.get('size', 1)
        return (total + size - 1) // size if total > 0 else 0


class ErrorResponse(BaseSchema):
    """Standard error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheckResponse(BaseSchema):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(..., description="Service version")
    components: Dict[str, str] = Field(..., description="Component status")


# Database session management
class DatabaseManager:
    """Database session and connection management."""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.session_factory()
    
    def create_tables(self, engine) -> None:
        """Create all tables."""
        Base.metadata.create_all(bind=engine)
    
    def drop_tables(self, engine) -> None:
        """Drop all tables."""
        Base.metadata.drop_all(bind=engine)


# Repository base class for database operations
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class for database operations."""
    
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session
    
    def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """Get single record by ID."""
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> list[ModelType]:
        """Get multiple records with optional filtering."""
        query = self.session.query(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, **filters) -> int:
        """Count records with optional filtering."""
        query = self.session.query(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def create(self, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """Create new record."""
        obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        obj_data.update(kwargs)
        
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        **kwargs
    ) -> ModelType:
        """Update existing record."""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        obj_data.update(kwargs)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def delete(self, id: uuid.UUID) -> bool:
        """Delete record by ID."""
        db_obj = self.get(id)
        if db_obj:
            self.session.delete(db_obj)
            self.session.commit()
            return True
        return False
    
    def soft_delete(self, id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> bool:
        """Soft delete record if it supports soft deletion."""
        db_obj = self.get(id)
        if db_obj and hasattr(db_obj, 'soft_delete'):
            db_obj.soft_delete(user_id)
            self.session.commit()
            return True
        return False
    
    def exists(self, id: uuid.UUID) -> bool:
        """Check if record exists."""
        return self.session.query(
            self.session.query(self.model).filter(self.model.id == id).exists()
        ).scalar()
    
    def get_paginated(
        self,
        pagination: PaginationParams,
        **filters
    ) -> PaginatedResponse[ModelType]:
        """Get paginated results."""
        total = self.count(**filters)
        items = self.get_multi(
            skip=pagination.offset,
            limit=pagination.size,
            **filters
        )
        
        return PaginatedResponse[ModelType](
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size
        )


# Utility functions for model operations
def create_indexes(engine, model_class: Type[Base]) -> None:
    """Create indexes for a model class."""
    for index in model_class.__table__.indexes:
        try:
            index.create(engine, checkfirst=True)
        except Exception as e:
            print(f"Warning: Could not create index {index.name}: {e}")


def validate_decimal_precision(value: Decimal, max_digits: int, decimal_places: int) -> Decimal:
    """Validate decimal precision and scale."""
    if value is None:
        return value
    
    # Convert to string to check precision
    str_value = str(value)
    if '.' in str_value:
        integer_part, decimal_part = str_value.split('.')
        if len(decimal_part) > decimal_places:
            raise ValueError(f"Too many decimal places. Maximum {decimal_places} allowed.")
        if len(integer_part) + len(decimal_part) > max_digits:
            raise ValueError(f"Too many total digits. Maximum {max_digits} allowed.")
    else:
        if len(str_value) > max_digits:
            raise ValueError(f"Too many total digits. Maximum {max_digits} allowed.")
    
    return value


def generate_table_constraints() -> Dict[str, Any]:
    """Generate common table constraints."""
    return {
        'percentage_check': CheckConstraint(
            'percentage >= 0 AND percentage <= 1',
            name='valid_percentage'
        ),
        'positive_amount_check': CheckConstraint(
            'amount > 0',
            name='positive_amount'
        ),
        'leverage_check': CheckConstraint(
            'leverage >= 1 AND leverage <= 100',
            name='valid_leverage'
        ),
        'risk_score_check': CheckConstraint(
            'risk_score >= 0 AND risk_score <= 1',
            name='valid_risk_score'
        )
    }


# Export commonly used classes and functions
__all__ = [
    'Base',
    'BaseTable',
    'AuditMixin',
    'SoftDeleteMixin',
    'VersionMixin',
    'MetadataMixin',
    'BaseSchema',
    'TimestampSchema',
    'BaseCreateSchema',
    'BaseUpdateSchema',
    'BaseResponseSchema',
    'PaginationParams',
    'PaginatedResponse',
    'ErrorResponse',
    'HealthCheckResponse',
    'DatabaseManager',
    'BaseRepository',
    'create_indexes',
    'validate_decimal_precision',
    'generate_table_constraints'
]

