from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from decimal import Decimal
from typing import Optional, List
import uuid
from datetime import datetime

from models.database import User, CreditTransaction, CreditPackage, PaymentHistory
from core.config import get_settings

settings = get_settings()

class CreditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_credit_balance(self, user_id: uuid.UUID) -> Decimal:
        """Get current credit balance for a user"""
        result = await self.db.execute(
            select(User.credit_balance).where(User.id == user_id)
        )
        balance = result.scalar()
        return balance or Decimal('0.00')

    async def validate_sufficient_credits(self, user_id: uuid.UUID, required_credits: int) -> bool:
        """Check if user has sufficient credits for a request"""
        balance = await self.get_user_credit_balance(user_id)
        return balance >= required_credits

    async def deduct_credits(
        self, 
        user_id: uuid.UUID, 
        amount: int, 
        description: str, 
        reference_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Deduct credits from user account"""
        try:
            # Get current balance
            balance_before = await self.get_user_credit_balance(user_id)
            
            if balance_before < amount:
                return False
            
            balance_after = balance_before - amount
            
            # Update user balance
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(credit_balance=balance_after)
            )
            
            # Record transaction
            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type="usage",
                amount=-amount,  # Negative for deduction
                description=description,
                reference_id=reference_id,
                balance_before=balance_before,
                balance_after=balance_after
            )
            self.db.add(transaction)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise e

    async def add_credits(
        self, 
        user_id: uuid.UUID, 
        amount: int, 
        transaction_type: str = "purchase",
        description: str = "",
        reference_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Add credits to user account"""
        try:
            # Get current balance
            balance_before = await self.get_user_credit_balance(user_id)
            balance_after = balance_before + amount
            
            # Update user balance
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(credit_balance=balance_after)
            )
            
            # Record transaction
            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                reference_id=reference_id,
                balance_before=balance_before,
                balance_after=balance_after
            )
            self.db.add(transaction)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_credit_packages(self) -> List[CreditPackage]:
        """Get all available credit packages"""
        result = await self.db.execute(
            select(CreditPackage)
            .where(CreditPackage.is_active == True)
            .order_by(CreditPackage.sort_order, CreditPackage.price)
        )
        return result.scalars().all()

    async def get_user_transaction_history(
        self, 
        user_id: uuid.UUID, 
        limit: int = 50,
        offset: int = 0
    ) -> List[CreditTransaction]:
        """Get user's credit transaction history"""
        result = await self.db.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def calculate_request_cost(self, request_type: str, parameters: dict = None) -> int:
        """Calculate credit cost based on request type and complexity"""
        base_costs = settings.DEFAULT_CREDIT_COSTS
        
        if request_type not in base_costs:
            return base_costs["basic_query"]
        
        base_cost = base_costs[request_type]
        
        # Add complexity multipliers based on parameters
        if parameters:
            # Time frame complexity
            timeframe = parameters.get("timeframe", "1h")
            if timeframe in ["1m", "5m"]:
                base_cost *= 1.5
            elif timeframe in ["1w", "1M"]:
                base_cost *= 0.8
            
            # Multiple symbols
            symbols = parameters.get("symbols", [])
            if isinstance(symbols, list) and len(symbols) > 1:
                base_cost *= (1 + (len(symbols) - 1) * 0.3)
            
            # Advanced analysis
            if parameters.get("include_sentiment", False):
                base_cost *= 1.2
            if parameters.get("include_social_data", False):
                base_cost *= 1.3
            if parameters.get("backtesting_required", False):
                base_cost *= 2.0
        
        return max(1, int(base_cost))  # Minimum 1 credit

    async def process_credit_purchase(
        self, 
        user_id: uuid.UUID, 
        package_id: uuid.UUID,
        payment_intent_id: str
    ) -> bool:
        """Process credit purchase after successful payment"""
        try:
            # Get package details
            package_result = await self.db.execute(
                select(CreditPackage).where(CreditPackage.id == package_id)
            )
            package = package_result.scalar_one_or_none()
            
            if not package:
                return False
            
            # Record payment
            payment = PaymentHistory(
                user_id=user_id,
                package_id=package_id,
                amount=package.price,
                payment_intent_id=payment_intent_id,
                status="completed",
                credits_awarded=package.credits,
                completed_at=datetime.utcnow()
            )
            self.db.add(payment)
            
            # Add credits to user account
            success = await self.add_credits(
                user_id=user_id,
                amount=package.credits,
                transaction_type="purchase",
                description=f"Purchased {package.name} package",
                reference_id=payment.id
            )
            
            return success
            
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_credit_usage_stats(self, user_id: uuid.UUID, days: int = 30) -> dict:
        """Get user's credit usage statistics"""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total credits used in period
        usage_result = await self.db.execute(
            select(CreditTransaction)
            .where(
                CreditTransaction.user_id == user_id,
                CreditTransaction.transaction_type == "usage",
                CreditTransaction.created_at >= start_date
            )
        )
        usage_transactions = usage_result.scalars().all()
        
        total_used = sum(abs(t.amount) for t in usage_transactions)
        
        # Usage by request type
        usage_by_type = {}
        for transaction in usage_transactions:
            request_type = transaction.description.split(":")[0] if ":" in transaction.description else "other"
            usage_by_type[request_type] = usage_by_type.get(request_type, 0) + abs(transaction.amount)
        
        return {
            "total_credits_used": total_used,
            "usage_by_type": usage_by_type,
            "average_daily_usage": total_used / days if days > 0 else 0,
            "current_balance": await self.get_user_credit_balance(user_id)
        }