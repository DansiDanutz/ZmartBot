from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

class CreditBalanceResponse(BaseModel):
    balance: Decimal
    tier: str

class CreditPackageResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    credits: int
    price: Decimal
    currency: str
    discount_percentage: Decimal
    is_active: bool
    sort_order: int

    class Config:
        from_attributes = True

class CreditTransactionResponse(BaseModel):
    id: uuid.UUID
    transaction_type: str
    amount: int
    description: Optional[str]
    balance_before: Decimal
    balance_after: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class CreditUsageStatsResponse(BaseModel):
    total_credits_used: int
    usage_by_type: Dict[str, int]
    average_daily_usage: float
    current_balance: Decimal

class CreditPurchaseRequest(BaseModel):
    package_id: uuid.UUID

class CreditPurchaseResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: Decimal
    currency: str
    credits: int

class ConfirmPurchaseRequest(BaseModel):
    payment_intent_id: str
    package_id: uuid.UUID