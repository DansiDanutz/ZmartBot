#!/usr/bin/env python3
"""
My Symbols API Routes - ZmartBot Symbol Management
Provides RESTful API endpoints for symbol portfolio management
"""

import logging
import sqlite3
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from datetime import datetime
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Pydantic models for API requests/responses
class PortfolioEntryResponse(BaseModel):
    symbol: str
    position_rank: int
    inclusion_date: str
    current_score: float
    weight_percentage: float
    status: str
    is_replacement_candidate: bool
    replacement_priority: Optional[int]
    performance_since_inclusion: Optional[float]
    max_drawdown_since_inclusion: Optional[float]
    volatility_since_inclusion: Optional[float]

class SymbolScoreResponse(BaseModel):
    symbol: str
    technical_score: float
    fundamental_score: float
    market_structure_score: float
    risk_score: float
    composite_score: float
    confidence_level: float
    rank: int
    calculation_timestamp: str
    supporting_data: Dict[str, Any]

class ReplacementRecommendation(BaseModel):
    replace_symbol: str
    replace_score: float
    candidate_symbol: str
    candidate_score: float
    score_improvement: float
    recommendation_strength: float

class PortfolioAnalytics(BaseModel):
    portfolio_size: int
    average_score: float
    total_score: float
    average_performance: float
    max_drawdown: float
    average_volatility: float
    replacement_candidates: int
    top_performers: List[Dict[str, Any]]
    lowest_scorers: List[Dict[str, Any]]
    last_updated: str

class ReplacementRequest(BaseModel):
    replace_symbol: str
    candidate_symbol: str
    reason: Optional[str] = None

class SymbolDataRequest(BaseModel):
    symbol: str
    root_symbol: str
    base_currency: str
    quote_currency: str
    settle_currency: str
    contract_type: str
    lot_size: float
    tick_size: float
    max_order_qty: int
    max_price: float
    multiplier: float
    initial_margin: float
    maintain_margin: float
    max_leverage: int
    status: str = "Active"
    is_eligible_for_management: bool = True
    sector_category: Optional[str] = None
    market_cap_category: Optional[str] = None
    volatility_classification: Optional[str] = None
    liquidity_tier: Optional[str] = None

# Mock My Symbols service for now
class MockMySymbolsService:
    def __init__(self):
        self.portfolio = [
            {
                "symbol": "BTC/USDT:USDT",
                "position_rank": 1,
                "inclusion_date": "2025-01-01T00:00:00",
                "current_score": 0.85,
                "weight_percentage": 15.0,
                "status": "Active",
                "is_replacement_candidate": False,
                "replacement_priority": None,
                "performance_since_inclusion": 12.5,
                "max_drawdown_since_inclusion": -5.2,
                "volatility_since_inclusion": 8.3
            },
            {
                "symbol": "ETH/USDT:USDT",
                "position_rank": 2,
                "inclusion_date": "2025-01-01T00:00:00",
                "current_score": 0.78,
                "weight_percentage": 12.0,
                "status": "Active",
                "is_replacement_candidate": False,
                "replacement_priority": None,
                "performance_since_inclusion": 8.7,
                "max_drawdown_since_inclusion": -3.1,
                "volatility_since_inclusion": 6.2
            }
        ]
        
        self.symbol_scores = [
            {
                "symbol": "BTC/USDT:USDT",
                "technical_score": 0.85,
                "fundamental_score": 0.90,
                "market_structure_score": 0.80,
                "risk_score": 0.75,
                "composite_score": 0.85,
                "confidence_level": 0.88,
                "rank": 1,
                "calculation_timestamp": "2025-08-15T01:24:00",
                "supporting_data": {"volume": 1000000, "market_cap": 50000000000}
            },
            {
                "symbol": "ETH/USDT:USDT",
                "technical_score": 0.78,
                "fundamental_score": 0.85,
                "market_structure_score": 0.75,
                "risk_score": 0.70,
                "composite_score": 0.78,
                "confidence_level": 0.82,
                "rank": 2,
                "calculation_timestamp": "2025-08-15T01:24:00",
                "supporting_data": {"volume": 800000, "market_cap": 30000000000}
            }
        ]
    
    async def get_portfolio(self):
        return self.portfolio
    
    async def get_symbol_scores(self, limit=50):
        return self.symbol_scores[:limit]
    
    async def calculate_symbol_scores(self):
        return {"BTC/USDT:USDT": 0.85, "ETH/USDT:USDT": 0.78}
    
    async def evaluate_portfolio_replacement(self):
        return [
            {
                "replace_symbol": "ETH/USDT:USDT",
                "replace_score": 0.78,
                "candidate_symbol": "SOL/USDT:USDT",
                "candidate_score": 0.82,
                "score_improvement": 0.04,
                "recommendation_strength": 0.75
            }
        ]
    
    async def execute_portfolio_replacement(self, replace_symbol, candidate_symbol):
        return True
    
    async def get_portfolio_analytics(self):
        return {
            "portfolio_size": 2,
            "average_score": 0.815,
            "total_score": 1.63,
            "average_performance": 10.6,
            "max_drawdown": -5.2,
            "average_volatility": 7.25,
            "replacement_candidates": 1,
            "top_performers": [{"symbol": "BTC/USDT:USDT", "performance": 12.5}],
            "lowest_scorers": [{"symbol": "ETH/USDT:USDT", "score": 0.78}],
            "last_updated": datetime.now().isoformat()
        }
    
    async def add_symbol_to_portfolio(self, symbol, position_rank):
        if len(self.portfolio) >= 10:
            return False
        self.portfolio.append({
            "symbol": symbol,
            "position_rank": position_rank,
            "inclusion_date": datetime.now().isoformat(),
            "current_score": 0.75,
            "weight_percentage": 10.0,
            "status": "Active",
            "is_replacement_candidate": False,
            "replacement_priority": None,
            "performance_since_inclusion": 0.0,
            "max_drawdown_since_inclusion": 0.0,
            "volatility_since_inclusion": 0.0
        })
        return True

# Initialize real service
from src.services.my_symbols_service_v2 import get_my_symbols_service
my_symbols_service = get_my_symbols_service()

# API Endpoints

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for My Symbols module"""
    try:
        return {
            "status": "healthy",
            "module": "my_symbols",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/test", response_model=Dict[str, Any])
async def test_endpoint():
    """Test endpoint for My Symbols module"""
    return {
        "message": "My Symbols module is working!",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/portfolio", response_model=List[PortfolioEntryResponse])
async def get_portfolio():
    """Get current portfolio composition"""
    try:
        logger.info(f"📊 Getting portfolio")
        
        portfolio = await my_symbols_service.get_portfolio()
        
        # Convert to response format
        response = []
        for entry in portfolio:
            response.append(PortfolioEntryResponse(
                symbol=entry.symbol,
                position_rank=entry.position_rank,
                inclusion_date=entry.inclusion_date.isoformat(),
                current_score=entry.current_score,
                weight_percentage=entry.weight_percentage,
                status=entry.status,
                is_replacement_candidate=entry.is_replacement_candidate,
                replacement_priority=entry.replacement_priority,
                performance_since_inclusion=entry.performance_since_inclusion,
                max_drawdown_since_inclusion=entry.max_drawdown_since_inclusion,
                volatility_since_inclusion=entry.volatility_since_inclusion
            ))
        
        logger.info(f"✅ Retrieved portfolio with {len(response)} symbols")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

@router.get("/scores", response_model=List[SymbolScoreResponse])
async def get_symbol_scores(
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get symbol scores for all symbols"""
    try:
        logger.info(f"🏆 Getting symbol scores (limit: {limit})")
        
        scores = await my_symbols_service.get_symbol_scores(limit=limit)
        
        # Convert to response format
        response = []
        for score in scores:
            response.append(SymbolScoreResponse(
                symbol=score.symbol,
                technical_score=score.technical_score,
                fundamental_score=score.fundamental_score,
                market_structure_score=score.market_structure_score,
                risk_score=score.risk_score,
                composite_score=score.composite_score,
                confidence_level=score.confidence_level,
                rank=score.rank,
                calculation_timestamp=score.calculation_timestamp.isoformat(),
                supporting_data=score.supporting_data
            ))
        
        logger.info(f"✅ Retrieved {len(response)} symbol scores")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbol scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol scores: {str(e)}")

@router.post("/scores/calculate", response_model=Dict[str, float])
async def calculate_symbol_scores():
    """Calculate scores for all symbols"""
    try:
        logger.info(f"🧮 Calculating symbol scores")
        
        scores = await my_symbols_service.calculate_symbol_scores()
        
        logger.info(f"✅ Calculated scores for {len(scores)} symbols")
        return scores
        
    except Exception as e:
        logger.error(f"❌ Failed to calculate symbol scores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate symbol scores: {str(e)}")

@router.get("/replacements", response_model=List[ReplacementRecommendation])
async def get_replacement_recommendations():
    """Get portfolio replacement recommendations"""
    try:
        logger.info(f"🔄 Getting replacement recommendations")
        
        recommendations = await my_symbols_service.evaluate_portfolio_replacement()
        
        # Convert to response format
        response = []
        for rec in recommendations:
            response.append(ReplacementRecommendation(
                replace_symbol=rec["replace_symbol"],
                replace_score=rec["replace_score"],
                candidate_symbol=rec["candidate_symbol"],
                candidate_score=rec["candidate_score"],
                score_improvement=rec["score_improvement"],
                recommendation_strength=rec["recommendation_strength"]
            ))
        
        logger.info(f"✅ Retrieved {len(response)} replacement recommendations")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get replacement recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get replacement recommendations: {str(e)}")

@router.post("/replacements/execute", response_model=Dict[str, Any])
async def execute_replacement(request: ReplacementRequest):
    """Execute a portfolio replacement"""
    try:
        logger.info(f"🔄 Executing replacement: {request.replace_symbol} -> {request.candidate_symbol}")
        
        success = await my_symbols_service.execute_portfolio_replacement(
            request.replace_symbol,
            request.candidate_symbol
        )
        
        if success:
            logger.info(f"✅ Successfully executed replacement")
            return {
                "success": True,
                "message": f"Successfully replaced {request.replace_symbol} with {request.candidate_symbol}",
                "replace_symbol": request.replace_symbol,
                "candidate_symbol": request.candidate_symbol,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ Failed to execute replacement")
            raise HTTPException(status_code=400, detail="Failed to execute replacement")
        
    except Exception as e:
        logger.error(f"❌ Failed to execute replacement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute replacement: {str(e)}")

@router.get("/analytics", response_model=PortfolioAnalytics)
async def get_portfolio_analytics():
    """Get comprehensive portfolio analytics"""
    try:
        logger.info(f"📈 Getting portfolio analytics")
        
        analytics = await my_symbols_service.get_portfolio_analytics()
        
        # Convert to response format
        response = PortfolioAnalytics(
            portfolio_size=analytics["portfolio_size"],
            average_score=analytics["average_score"],
            total_score=analytics["total_score"],
            average_performance=analytics["average_performance"],
            max_drawdown=analytics["max_drawdown"],
            average_volatility=analytics["average_volatility"],
            replacement_candidates=analytics["replacement_candidates"],
            top_performers=analytics["top_performers"],
            lowest_scorers=analytics["lowest_scorers"],
            last_updated=analytics["last_updated"]
        )
        
        logger.info(f"✅ Retrieved portfolio analytics")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get portfolio analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio analytics: {str(e)}")

@router.get("/symbols", response_model=List[Dict[str, Any]])
async def get_all_symbols():
    """Get all available symbols"""
    try:
        logger.info(f"📋 Getting all symbols")
        
        # Get from KuCoin API
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/futures-symbols/kucoin/available")
            if response.status_code == 200:
                data = response.json()
                symbols = [
                    {
                        "symbol": symbol,
                        "name": symbol.replace("USDT", "").replace(":USDT", ""),
                        "status": "Active",
                        "score": 0.75  # Default score
                    }
                    for symbol in data.get("symbols", [])[:100]  # Limit to 100 for performance
                ]
            else:
                # Fallback to mock data
                symbols = [
                    {"symbol": "BTC/USDT:USDT", "name": "BTC", "status": "Active", "score": 0.85},
                    {"symbol": "ETH/USDT:USDT", "name": "ETH", "status": "Active", "score": 0.78},
                    {"symbol": "SOL/USDT:USDT", "name": "SOL", "status": "Active", "score": 0.82}
                ]
        
        logger.info(f"✅ Retrieved {len(symbols)} symbols")
        return symbols
        
    except Exception as e:
        logger.error(f"❌ Failed to get symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@router.post("/portfolio/add", response_model=Dict[str, Any])
async def add_symbol_to_portfolio(symbol: str = Body(..., embed=True)):
    """Add a symbol to the portfolio"""
    try:
        logger.info(f"➕ Adding {symbol} to portfolio")
        
        # Check current portfolio size
        portfolio = await my_symbols_service.get_portfolio()
        current_count = len(portfolio)
        
        if current_count >= 10:
            raise HTTPException(
                status_code=400, 
                detail=f"Portfolio is full! Current: {current_count}/10 symbols. Remove a symbol first."
            )
        
        # Find next available position rank
        occupied_ranks = [entry.position_rank for entry in portfolio]
        next_rank = 1
        while next_rank in occupied_ranks and next_rank <= 10:
            next_rank += 1
        
        if next_rank > 10:
            raise HTTPException(
                status_code=400,
                detail="No available position ranks"
            )
        
        # Add symbol to portfolio
        success = await my_symbols_service.add_symbol_to_portfolio(symbol, next_rank)
        
        if success:
            logger.info(f"✅ Successfully added {symbol} to portfolio at position {next_rank}")
            return {
                "success": True,
                "message": f"Successfully added {symbol} to portfolio at position {next_rank}",
                "symbol": symbol,
                "position_rank": next_rank,
                "portfolio_count": current_count + 1,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add {symbol} to portfolio"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to add {symbol} to portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add symbol to portfolio: {str(e)}")

@router.delete("/portfolio/remove/{symbol}", response_model=Dict[str, Any])
async def remove_symbol_from_portfolio(symbol: str):
    """Remove a symbol from the portfolio"""
    try:
        logger.info(f"🗑️ Removing {symbol} from portfolio")
        
        # Get current portfolio
        portfolio = await my_symbols_service.get_portfolio()
        current_count = len(portfolio)
        
        # Find the symbol in portfolio
        symbol_entry = None
        for entry in portfolio:
            if entry.symbol == symbol:
                symbol_entry = entry
                break
        
        if not symbol_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found in portfolio"
            )
        
        # Remove from portfolio using real service
        success = await my_symbols_service.remove_symbol_from_portfolio(symbol)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove {symbol} from portfolio"
            )
        
        logger.info(f"✅ Successfully removed {symbol} from portfolio")
        return {
            "success": True,
            "message": f"Successfully removed {symbol} from portfolio",
            "symbol": symbol,
            "portfolio_count": current_count - 1,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to remove {symbol} from portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove symbol from portfolio: {str(e)}")

@router.get("/configuration", response_model=Dict[str, Any])
async def get_configuration():
    """Get system configuration"""
    try:
        logger.info(f"⚙️ Getting configuration")
        
        config = {
            "max_portfolio_size": 10,
            "min_score_threshold": 0.6,
            "replacement_candidates": 2,
            "scoring_update_interval": 300,
            "portfolio_rebalance_interval": 3600,
            "signal_evaluation_timeout": 60,
            "risk_max_drawdown": 0.15,
            "risk_max_correlation": 0.7,
            "performance_tracking_days": 30
        }
        
        logger.info(f"✅ Retrieved configuration")
        return config
        
    except Exception as e:
        logger.error(f"❌ Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_module_status():
    """Get My Symbols module status"""
    try:
        logger.info(f"📊 Getting module status")
        
        # Get portfolio and analytics
        portfolio = await my_symbols_service.get_portfolio()
        analytics = await my_symbols_service.get_portfolio_analytics()
        
        status = {
            "module": "my_symbols",
            "status": "active",
            "portfolio_size": len(portfolio),
            "average_score": analytics["average_score"],
            "replacement_candidates": analytics["replacement_candidates"],
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        logger.info(f"✅ Retrieved module status")
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get module status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get module status: {str(e)}") 