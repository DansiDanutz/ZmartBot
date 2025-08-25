#!/usr/bin/env python3
"""
Explainability Routes
AI-powered trading signal explanations and risk analysis
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime

from src.services.explainability_service import get_explainability_service, SignalExplanation, RiskExplanation, PortfolioExplanation

router = APIRouter()

# Pydantic models for request/response
class SignalExplanationRequest(BaseModel):
    signal_data: Dict[str, Any]

class RiskExplanationRequest(BaseModel):
    risk_data: Dict[str, Any]

class PortfolioExplanationRequest(BaseModel):
    portfolio_data: Dict[str, Any]

class SignalExplanationResponse(BaseModel):
    signal_id: str
    symbol: str
    direction: str
    confidence: float
    confidence_level: str
    factors: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    recommendation: str
    timestamp: datetime
    explanation_text: str

class RiskExplanationResponse(BaseModel):
    symbol: str
    risk_score: float
    risk_level: str
    factors: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    timestamp: datetime
    explanation_text: str

class PortfolioExplanationResponse(BaseModel):
    portfolio_id: str
    total_value: float
    risk_score: float
    diversification_score: float
    recommendations: List[Dict[str, Any]]
    timestamp: datetime
    explanation_text: str

@router.post("/explain/signal", response_model=SignalExplanationResponse)
async def explain_signal(request: SignalExplanationRequest):
    """Generate explanation for a trading signal"""
    try:
        explainability_service = get_explainability_service()
        explanation = explainability_service.explain_signal(request.signal_data)
        
        return SignalExplanationResponse(
            signal_id=explanation.signal_id,
            symbol=explanation.symbol,
            direction=explanation.direction,
            confidence=explanation.confidence,
            confidence_level=explanation.confidence_level.value,
            factors=explanation.factors,
            risk_assessment=explanation.risk_assessment,
            recommendation=explanation.recommendation,
            timestamp=explanation.timestamp,
            explanation_text=explanation.explanation_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining signal: {str(e)}")

@router.post("/explain/risk", response_model=RiskExplanationResponse)
async def explain_risk(request: RiskExplanationRequest):
    """Generate explanation for risk assessment"""
    try:
        explainability_service = get_explainability_service()
        explanation = explainability_service.explain_risk(request.risk_data)
        
        return RiskExplanationResponse(
            symbol=explanation.symbol,
            risk_score=explanation.risk_score,
            risk_level=explanation.risk_level.value,
            factors=explanation.factors,
            mitigation_strategies=explanation.mitigation_strategies,
            timestamp=explanation.timestamp,
            explanation_text=explanation.explanation_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining risk: {str(e)}")

@router.post("/explain/portfolio", response_model=PortfolioExplanationResponse)
async def explain_portfolio(request: PortfolioExplanationRequest):
    """Generate explanation for portfolio decisions"""
    try:
        explainability_service = get_explainability_service()
        explanation = explainability_service.explain_portfolio(request.portfolio_data)
        
        return PortfolioExplanationResponse(
            portfolio_id=explanation.portfolio_id,
            total_value=explanation.total_value,
            risk_score=explanation.risk_score,
            diversification_score=explanation.diversification_score,
            recommendations=explanation.recommendations,
            timestamp=explanation.timestamp,
            explanation_text=explanation.explanation_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining portfolio: {str(e)}")

@router.get("/test/signal")
async def test_signal_explanation():
    """Test endpoint for signal explanation"""
    try:
        explainability_service = get_explainability_service()
        
        # Create test signal data
        test_signal = {
            'id': 'test_signal_001',
            'symbol': 'BTCUSDT',
            'direction': 'BUY',
            'confidence': 0.85,
            'kingfisher_score': 0.8,
            'riskmetric_score': 0.7,
            'cryptometer_score': 0.9,
            'volatility': 0.6,
            'liquidity': 0.8,
            'market_correlation': 0.3,
            'position_size': 0.05
        }
        
        explanation = explainability_service.explain_signal(test_signal)
        
        return {
            "message": "Signal explanation test successful",
            "explanation": {
                "signal_id": explanation.signal_id,
                "symbol": explanation.symbol,
                "direction": explanation.direction,
                "confidence": explanation.confidence,
                "confidence_level": explanation.confidence_level.value,
                "recommendation": explanation.recommendation,
                "explanation_text": explanation.explanation_text
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/test/risk")
async def test_risk_explanation():
    """Test endpoint for risk explanation"""
    try:
        explainability_service = get_explainability_service()
        
        # Create test risk data
        test_risk = {
            'symbol': 'ETHUSDT',
            'risk_score': 0.65,
            'volatility': 0.7,
            'liquidity': 0.6,
            'market_correlation': 0.8
        }
        
        explanation = explainability_service.explain_risk(test_risk)
        
        return {
            "message": "Risk explanation test successful",
            "explanation": {
                "symbol": explanation.symbol,
                "risk_score": explanation.risk_score,
                "risk_level": explanation.risk_level.value,
                "explanation_text": explanation.explanation_text
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/test/portfolio")
async def test_portfolio_explanation():
    """Test endpoint for portfolio explanation"""
    try:
        explainability_service = get_explainability_service()
        
        # Create test portfolio data
        test_portfolio = {
            'id': 'test_portfolio_001',
            'total_value': 50000.0,
            'risk_score': 0.45,
            'diversification_score': 0.6,
            'rebalance_needed': True
        }
        
        explanation = explainability_service.explain_portfolio(test_portfolio)
        
        return {
            "message": "Portfolio explanation test successful",
            "explanation": {
                "portfolio_id": explanation.portfolio_id,
                "total_value": explanation.total_value,
                "risk_score": explanation.risk_score,
                "diversification_score": explanation.diversification_score,
                "explanation_text": explanation.explanation_text
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/health")
async def explainability_health():
    """Health check for explainability service"""
    try:
        explainability_service = get_explainability_service()
        
        # Test with minimal data
        test_signal = {
            'symbol': 'TEST',
            'direction': 'HOLD',
            'confidence': 0.0
        }
        
        explanation = explainability_service.explain_signal(test_signal)
        
        return {
            "status": "healthy",
            "service": "explainability",
            "timestamp": datetime.utcnow(),
            "test_successful": explanation.symbol == 'TEST'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") 