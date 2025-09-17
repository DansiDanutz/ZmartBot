from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from core.database import get_db_session
from services.credit_service import CreditService
from api.v1.auth import get_current_user_dependency
from schemas.credits import (
    CreditBalanceResponse,
    CreditPackageResponse, 
    CreditTransactionResponse,
    CreditUsageStatsResponse,
    CreditPurchaseRequest,
    CreditPurchaseResponse,
    ConfirmPurchaseRequest
)
from models.database import User

router = APIRouter()

@router.get("/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's current credit balance"""
    credit_service = CreditService(db)
    balance = await credit_service.get_user_credit_balance(current_user.id)
    
    return CreditBalanceResponse(
        balance=balance,
        tier=current_user.tier
    )

@router.get("/packages", response_model=List[CreditPackageResponse])
async def get_credit_packages(
    db: AsyncSession = Depends(get_db_session)
):
    """Get all available credit packages"""
    credit_service = CreditService(db)
    packages = await credit_service.get_credit_packages()
    
    return [
        CreditPackageResponse(
            id=pkg.id,
            name=pkg.name,
            description=pkg.description,
            credits=pkg.credits,
            price=pkg.price,
            currency=pkg.currency,
            discount_percentage=pkg.discount_percentage,
            is_active=pkg.is_active,
            sort_order=pkg.sort_order
        )
        for pkg in packages
    ]

@router.get("/transactions", response_model=List[CreditTransactionResponse])
async def get_credit_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's credit transaction history"""
    credit_service = CreditService(db)
    transactions = await credit_service.get_user_transaction_history(
        current_user.id, limit, offset
    )
    
    return [
        CreditTransactionResponse(
            id=txn.id,
            transaction_type=txn.transaction_type,
            amount=txn.amount,
            description=txn.description,
            balance_before=txn.balance_before,
            balance_after=txn.balance_after,
            created_at=txn.created_at
        )
        for txn in transactions
    ]

@router.get("/usage-stats", response_model=CreditUsageStatsResponse)
async def get_usage_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's credit usage statistics"""
    credit_service = CreditService(db)
    stats = await credit_service.get_credit_usage_stats(current_user.id, days)
    
    return CreditUsageStatsResponse(**stats)

@router.post("/purchase", response_model=CreditPurchaseResponse)
async def purchase_credits(
    purchase_data: CreditPurchaseRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Initiate credit purchase process"""
    import stripe
    from core.config import get_settings
    
    settings = get_settings()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    credit_service = CreditService(db)
    
    # Get package details
    from sqlalchemy import select
    from models.database import CreditPackage
    
    result = await db.execute(
        select(CreditPackage).where(
            CreditPackage.id == purchase_data.package_id,
            CreditPackage.is_active == True
        )
    )
    package = result.scalar_one_or_none()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found or inactive"
        )
    
    try:
        # Create Stripe Payment Intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(package.price * 100),  # Amount in cents
            currency=package.currency.lower(),
            metadata={
                "user_id": str(current_user.id),
                "package_id": str(package.id),
                "credits": package.credits
            }
        )
        
        return CreditPurchaseResponse(
            payment_intent_id=payment_intent.id,
            client_secret=payment_intent.client_secret,
            amount=package.price,
            currency=package.currency,
            credits=package.credits
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )

@router.post("/confirm-purchase")
async def confirm_purchase(
    confirm_data: ConfirmPurchaseRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Confirm credit purchase after successful payment"""
    import stripe
    from core.config import get_settings
    
    settings = get_settings()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    credit_service = CreditService(db)
    
    try:
        # Verify payment intent
        payment_intent = stripe.PaymentIntent.retrieve(confirm_data.payment_intent_id)
        
        if payment_intent.status != 'succeeded':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed"
            )
        
        # Verify user owns this payment
        if payment_intent.metadata.get('user_id') != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized payment"
            )
        
        # Process credit purchase
        success = await credit_service.process_credit_purchase(
            user_id=current_user.id,
            package_id=confirm_data.package_id,
            payment_intent_id=confirm_data.payment_intent_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process credit purchase"
            )
        
        # Get updated balance
        new_balance = await credit_service.get_user_credit_balance(current_user.id)
        
        return {
            "success": True,
            "message": "Credits purchased successfully",
            "new_balance": new_balance
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment verification error: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: bytes,
    stripe_signature: str = None
):
    """Handle Stripe webhooks"""
    import stripe
    from core.config import get_settings
    
    settings = get_settings()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        event = stripe.Webhook.construct_event(
            request, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Handle successful payment
            print(f"Payment succeeded: {payment_intent['id']}")
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Handle failed payment
            print(f"Payment failed: {payment_intent['id']}")
        
        return {"status": "success"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")