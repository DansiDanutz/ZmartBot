import openai
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import ZmartyRequest
from core.config import get_settings
from services.credit_service import CreditService

settings = get_settings()

class ZmartyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.credit_service = CreditService(db)
        self.client = openai.AsyncOpenAI(api_key=settings.ZMARTY_API_KEY)

    async def process_request(
        self, 
        user_id: uuid.UUID, 
        query: str, 
        request_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main method to process Zmarty requests"""
        
        # Calculate credit cost
        credit_cost = await self.credit_service.calculate_request_cost(request_type, parameters)
        
        # Validate user has sufficient credits
        if not await self.credit_service.validate_sufficient_credits(user_id, credit_cost):
            return {
                "success": False,
                "error": "insufficient_credits",
                "message": f"You need {credit_cost} credits for this request. Please purchase more credits.",
                "required_credits": credit_cost
            }
        
        # Create request record
        request_record = ZmartyRequest(
            user_id=user_id,
            request_type=request_type,
            query=query,
            parameters=json.dumps(parameters) if parameters else None,
            credits_cost=credit_cost,
            status="processing"
        )
        self.db.add(request_record)
        await self.db.commit()
        await self.db.refresh(request_record)
        
        try:
            # Deduct credits first
            deduction_success = await self.credit_service.deduct_credits(
                user_id=user_id,
                amount=credit_cost,
                description=f"{request_type}: {query[:100]}...",
                reference_id=request_record.id
            )
            
            if not deduction_success:
                request_record.status = "failed"
                await self.db.commit()
                return {
                    "success": False,
                    "error": "credit_deduction_failed",
                    "message": "Failed to deduct credits"
                }
            
            # Generate AI response based on request type
            start_time = datetime.utcnow()
            response = await self._generate_response(query, request_type, parameters)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update request record
            request_record.response = response
            request_record.status = "completed"
            request_record.processing_time = int(processing_time)
            request_record.completed_at = datetime.utcnow()
            await self.db.commit()
            
            return {
                "success": True,
                "request_id": request_record.id,
                "response": response,
                "credits_used": credit_cost,
                "processing_time": processing_time
            }
            
        except Exception as e:
            # Mark request as failed and potentially refund credits
            request_record.status = "failed"
            await self.db.commit()
            
            # Refund credits on system error
            await self.credit_service.add_credits(
                user_id=user_id,
                amount=credit_cost,
                transaction_type="refund",
                description=f"Refund for failed request: {request_record.id}",
                reference_id=request_record.id
            )
            
            return {
                "success": False,
                "error": "processing_failed",
                "message": f"Request processing failed: {str(e)}",
                "credits_refunded": credit_cost
            }

    async def _generate_response(
        self, 
        query: str, 
        request_type: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response based on request type"""
        
        # Create system prompt based on request type
        system_prompt = self._get_system_prompt(request_type)
        
        # Add context from parameters
        context = self._build_context(parameters) if parameters else ""
        
        # Enhance query with context
        enhanced_query = f"{context}\n\nUser Query: {query}" if context else query
        
        # Make OpenAI API call
        response = await self.client.chat.completions.create(
            model=settings.ZMARTY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_query}
            ],
            max_tokens=settings.ZMARTY_MAX_TOKENS,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def _get_system_prompt(self, request_type: str) -> str:
        """Get appropriate system prompt based on request type"""
        
        prompts = {
            "basic_query": """You are Zmarty, an expert cryptocurrency trading assistant. 
            Provide clear, concise answers about cryptocurrency markets, trading concepts, 
            and general market information. Keep responses informative but accessible.""",
            
            "market_analysis": """You are Zmarty, a professional cryptocurrency market analyst. 
            Provide detailed technical and fundamental analysis of cryptocurrency markets. 
            Include price trends, volume analysis, support/resistance levels, and market sentiment. 
            Use professional trading terminology and provide actionable insights.""",
            
            "trading_strategy": """You are Zmarty, an experienced cryptocurrency trading strategist. 
            Develop comprehensive trading strategies based on technical analysis, risk management, 
            and market conditions. Include entry/exit points, stop-loss levels, position sizing, 
            and risk assessment. Provide step-by-step implementation guidance.""",
            
            "ai_predictions": """You are Zmarty, an AI-powered cryptocurrency prediction specialist. 
            Analyze market data, trends, and patterns to provide informed predictions about 
            cryptocurrency price movements. Include confidence levels, time frames, 
            and key factors influencing your predictions. Always include risk disclaimers.""",
            
            "live_signals": """You are Zmarty, a real-time cryptocurrency trading signal provider. 
            Generate immediate trading signals based on current market conditions. 
            Include specific entry points, targets, stop-losses, and time-sensitive analysis. 
            Emphasize urgency and precision in your recommendations.""",
            
            "custom_research": """You are Zmarty, a comprehensive cryptocurrency research analyst. 
            Conduct deep-dive analysis combining technical analysis, fundamental research, 
            on-chain metrics, market sentiment, and regulatory factors. 
            Provide institutional-level research with detailed methodology and sources."""
        }
        
        return prompts.get(request_type, prompts["basic_query"])

    def _build_context(self, parameters: Dict[str, Any]) -> str:
        """Build context string from parameters"""
        context_parts = []
        
        if "symbol" in parameters:
            context_parts.append(f"Cryptocurrency: {parameters['symbol']}")
        
        if "timeframe" in parameters:
            context_parts.append(f"Timeframe: {parameters['timeframe']}")
        
        if "risk_level" in parameters:
            context_parts.append(f"Risk Level: {parameters['risk_level']}")
        
        if "portfolio_size" in parameters:
            context_parts.append(f"Portfolio Size: ${parameters['portfolio_size']}")
        
        if "trading_experience" in parameters:
            context_parts.append(f"Trading Experience: {parameters['trading_experience']}")
        
        if "market_conditions" in parameters:
            context_parts.append(f"Market Conditions: {parameters['market_conditions']}")
        
        return "Context:\n" + "\n".join(context_parts) if context_parts else ""

    async def get_user_requests(
        self, 
        user_id: uuid.UUID, 
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ZmartyRequest]:
        """Get user's request history"""
        from sqlalchemy import select
        
        query = select(ZmartyRequest).where(ZmartyRequest.user_id == user_id)
        
        if status:
            query = query.where(ZmartyRequest.status == status)
        
        query = query.order_by(ZmartyRequest.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_request_by_id(self, request_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ZmartyRequest]:
        """Get specific request by ID (user must own the request)"""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(ZmartyRequest).where(
                ZmartyRequest.id == request_id,
                ZmartyRequest.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def rate_response(
        self, 
        request_id: uuid.UUID, 
        user_id: uuid.UUID, 
        quality_score: float
    ) -> bool:
        """Allow user to rate the quality of a response"""
        from sqlalchemy import update
        
        try:
            await self.db.execute(
                update(ZmartyRequest)
                .where(
                    ZmartyRequest.id == request_id,
                    ZmartyRequest.user_id == user_id
                )
                .values(quality_score=quality_score)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def get_trending_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending queries across all users (anonymized)"""
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        
        # Get queries from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        result = await self.db.execute(
            select(
                ZmartyRequest.request_type,
                func.count(ZmartyRequest.id).label("count"),
                func.avg(ZmartyRequest.quality_score).label("avg_rating")
            )
            .where(
                ZmartyRequest.created_at >= week_ago,
                ZmartyRequest.status == "completed"
            )
            .group_by(ZmartyRequest.request_type)
            .order_by(func.count(ZmartyRequest.id).desc())
            .limit(limit)
        )
        
        return [
            {
                "request_type": row.request_type,
                "count": row.count,
                "avg_rating": float(row.avg_rating) if row.avg_rating else None
            }
            for row in result.all()
        ]