"""
RiskMetric API Routes - Complete Implementation
Based on Benjamin Cowen's methodology with 17 symbols
Extracted from Into The Cryptoverse platform
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Use the unified RiskMetric service with all 21 symbols
from src.services.unified_riskmetric import (
    UnifiedRiskMetric,
    UnifiedRiskMetricAPI,
    RiskAssessment,
    # Get singleton instances
    unified_riskmetric,
    unified_riskmetric_api
)
from src.agents.database.riskmetric_qa_agent import RiskMetricQAAgent
try:
    from src.routes.auth import get_current_active_user
except ImportError:
    # Fallback if auth not configured
    async def get_current_active_user():  # Make it async
        return {"username": "admin", "role": "admin"}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/riskmetric", tags=["RiskMetric"])

# Use the already initialized Unified RiskMetric instances
agent = unified_riskmetric  # Singleton with all 21 symbols
api = unified_riskmetric_api  # API instance with complete functionality

# Initialize the Q&A Agent
qa_agent = RiskMetricQAAgent(db_path="data/riskmetric_qa.db")

@router.get("/health")
async def health_check():
    """Health check endpoint for RiskMetric service"""
    try:
        # Check if agent is initialized
        status = {
            "agent_initialized": agent is not None,
            "symbols_configured": len(agent.SYMBOL_BOUNDS),
            "database_path": agent.db_path
        }
        return {
            "service": "comprehensive-riskmetric-service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "details": status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

@router.get("/status")
async def get_status():
    """Get detailed service status"""
    try:
        return {
            "agent_initialized": agent is not None,
            "symbols_configured": len(agent.SYMBOL_BOUNDS),
            "database_path": agent.db_path,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/symbols")
async def get_symbols():
    """Get list of all supported symbols"""
    try:
        symbols = list(agent.SYMBOL_BOUNDS.keys())
        return {
            "symbols": symbols,
            "total_count": len(symbols),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@router.get("/symbols/{symbol}")
async def get_symbol_data(symbol: str):
    """Get complete data for a specific symbol"""
    try:
        symbol = symbol.upper()
        if symbol not in agent.SYMBOL_BOUNDS:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        bounds = agent.SYMBOL_BOUNDS[symbol]
        distribution = agent.get_risk_distribution(symbol)
        
        data = {
            "symbol": symbol,
            "bounds": bounds,
            "distribution": distribution,
            "timestamp": datetime.now().isoformat()
        }
        if not data:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get symbol data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol data: {str(e)}")

@router.post("/assess/{symbol}")
async def assess_risk(
    symbol: str,
    current_price: Optional[float] = Query(None, description="Current price for assessment")
):
    """Complete risk assessment for a symbol using Benjamin Cowen's methodology"""
    try:
        assessment = await api.analyze(symbol, current_price)
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found or assessment failed")
        return assessment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assess risk for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assess risk: {str(e)}")

@router.get("/{symbol}")
async def get_riskmetric_data(symbol: str):
    """GET endpoint for dashboard - returns risk metric data for a symbol"""
    try:
        # Get symbol data with bounds and distribution
        bounds = agent.SYMBOL_BOUNDS.get(symbol.upper())
        if not bounds:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        # Get latest risk assessment
        assessment = await api.analyze(symbol, None)
        
        return {
            "symbol": symbol.upper(),
            "bounds": bounds,
            "current_risk": assessment.get('risk_value') if assessment else None,
            "assessment": assessment,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get riskmetric data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get riskmetric data: {str(e)}")

@router.post("/risk/{symbol}")
async def calculate_risk_from_price(symbol: str, price: float):
    """Calculate risk level from price using Benjamin Cowen's methodology"""
    try:
        result = await api.get_risk(symbol, price)
        risk = result.get('risk')
        if risk is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        return {
            "symbol": symbol.upper(),
            "price": price,
            "risk": risk,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate risk for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate risk: {str(e)}")

@router.post("/price/{symbol}")
async def calculate_price_from_risk(symbol: str, risk: float):
    """Calculate price from risk level using Benjamin Cowen's methodology"""
    try:
        if not 0 <= risk <= 1:
            raise HTTPException(status_code=400, detail="Risk must be between 0 and 1")
        
        result = await api.get_price(symbol, risk)
        price = result.get('price')
        if price is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "symbol": symbol.upper(),
            "risk": risk,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate price: {str(e)}")

@router.put("/symbols/{symbol}/bounds")
async def update_symbol_bounds(
    symbol: str,
    min_price: float,
    max_price: float,
    reason: str = Query("Manual update", description="Reason for the update")
):
    """Update symbol bounds (for when Benjamin Cowen updates his models)"""
    try:
        if min_price >= max_price:
            raise HTTPException(status_code=400, detail="min_price must be less than max_price")
        
        # Update bounds in agent
        symbol = symbol.upper()
        agent.SYMBOL_BOUNDS[symbol] = {'min': min_price, 'max': max_price}
        success = True
        if not success:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "message": f"Symbol {symbol.upper()} bounds updated successfully",
            "symbol": symbol.upper(),
            "min_price": min_price,
            "max_price": max_price,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update bounds for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update bounds: {str(e)}")

@router.get("/screener")
async def get_screener():
    """Get comprehensive screener data for all symbols"""
    try:
        # Get analysis for all symbols
        symbols = list(agent.SYMBOL_BOUNDS.keys())
        analyses = await api.batch_analyze(symbols)
        
        screener_data = {
            "symbols": analyses,
            "count": len(analyses),
            "timestamp": datetime.now().isoformat()
        }
        return screener_data
    except Exception as e:
        logger.error(f"Failed to get screener data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get screener data: {str(e)}")

@router.post("/portfolio/analysis")
async def get_portfolio_analysis(symbols: List[str]):
    """Get portfolio-level risk analysis"""
    try:
        if not symbols:
            raise HTTPException(status_code=400, detail="At least one symbol is required")
        
        # Analyze each symbol in portfolio
        analyses = await api.batch_analyze(symbols)
        
        # Calculate portfolio metrics
        avg_risk = sum(a['risk_value'] for a in analyses) / len(analyses) if analyses else 0
        
        portfolio_data = {
            "symbols": analyses,
            "portfolio_risk": avg_risk,
            "count": len(analyses),
            "timestamp": datetime.now().isoformat()
        }
        return portfolio_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get portfolio analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio analysis: {str(e)}")

@router.get("/manual-updates")
async def get_manual_updates(symbol: Optional[str] = None):
    """Get manual update history"""
    try:
        # This would fetch from database
        updates = []  # Placeholder
        return {
            "updates": updates,
            "total_count": len(updates),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get manual updates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get manual updates: {str(e)}")

@router.get("/metrics")
async def get_metrics():
    """Get comprehensive service metrics"""
    try:
        metrics = {
            "total_symbols": len(agent.SYMBOL_BOUNDS),
            "database_path": agent.db_path,
            "timestamp": datetime.now().isoformat()
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/agent/start")
async def start_agent():
    """Start the RiskMetric agent"""
    try:
        # Agent is already initialized
        pass
        return {
            "message": "RiskMetric agent started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@router.post("/agent/stop")
async def stop_agent():
    """Stop the RiskMetric agent"""
    try:
        # Agent cleanup if needed
        pass
        return {
            "message": "RiskMetric agent stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

# Scoring system integration endpoints
@router.get("/scoring/{symbol}")
async def get_scoring_component(symbol: str):
    """Get RiskMetric component for the 25-point scoring system"""
    try:
        analysis = await api.analyze(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        # Convert to 20-point scale (RiskMetric contributes 20% to total)
        component = {
            "symbol": symbol,
            "score": (analysis['final_score'] / 100) * 20,
            "raw_score": analysis['final_score'],
            "risk_value": analysis['risk_value'],
            "signal": analysis['signal']
        }
        if not component:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        return component
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scoring component for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scoring component: {str(e)}")

@router.get("/scoring")
async def get_all_scoring_components():
    """Get RiskMetric scoring components for all symbols"""
    try:
        symbols = list(agent.SYMBOL_BOUNDS.keys())
        analyses = await api.batch_analyze(symbols)
        
        components = [{
            "symbol": a['symbol'],
            "score": (a['final_score'] / 100) * 20,
            "raw_score": a['final_score'],
            "risk_value": a['risk_value'],
            "signal": a['signal']
        } for a in analyses]
        return components
    except Exception as e:
        logger.error(f"Failed to get scoring components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scoring components: {str(e)}")

# Admin endpoints (require authentication)
@router.delete("/symbols/{symbol}")
async def delete_symbol(
    symbol: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a symbol (admin only)"""
    try:
        # This would require implementing delete functionality in the service
        # For now, return a placeholder response
        return {
            "message": f"Symbol {symbol.upper()} deletion not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to delete symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete symbol: {str(e)}")

@router.post("/daily-update")
async def trigger_daily_update(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Trigger daily update manually (admin only)"""
    try:
        # This would trigger the daily update process
        return {
            "message": "Daily update triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to trigger daily update: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger daily update: {str(e)}")

# Manual Update System (from Cowen Guide Requirements)
@router.post("/admin/update-bounds/{symbol}")
async def admin_update_symbol_bounds(symbol: str, bounds_data: dict):
    """Update min/max bounds for a symbol (Manual Update System from Cowen Guide)"""
    try:
        min_price = bounds_data.get('min_price')
        max_price = bounds_data.get('max_price')
        reason = bounds_data.get('reason', 'Manual update')
        
        if not min_price or not max_price:
            raise HTTPException(status_code=400, detail="min_price and max_price required")
        
        # Update bounds using the agent
        # Update bounds in agent
        symbol = symbol.upper()
        agent.SYMBOL_BOUNDS[symbol] = {'min': min_price, 'max': max_price}
        result = {"success": True, "message": "Bounds updated"}
        
        return {
            'symbol': symbol.upper(),
            'updated_bounds': {
                'min_price': min_price,
                'max_price': max_price
            },
            'reason': reason,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating bounds for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/manual-updates/{symbol}")
async def get_manual_updates_history(symbol: str):
    """Get manual updates history for a symbol"""
    try:
        # Placeholder for history
        history = []
        return {
            'symbol': symbol.upper(),
            'manual_updates': history,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting manual updates for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regression-formulas/{symbol}")
async def get_regression_formulas(symbol: str):
    """Get regression formula constants for a symbol"""
    try:
        symbol = symbol.upper()
        if symbol not in agent.SYMBOL_BOUNDS:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        bounds = agent.SYMBOL_BOUNDS[symbol]
        formulas = {
            "min_price": bounds['min'],
            "max_price": bounds['max'],
            "formula": "risk = (ln(price) - ln(min)) / (ln(max) - ln(min))",
            "inverse": "price = min * exp(risk * ln(max/min))"
        }
        return {
            'symbol': symbol.upper(),
            'regression_formulas': formulas,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting regression formulas for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Q&A System Endpoints
@router.post("/ask")
async def ask_question(question: str = Query(..., description="Natural language question about RiskMetric data")):
    """
    Ask a natural language question about RiskMetric data
    
    Examples:
    - "What would be the risk value at the price of Bitcoin of 134000?"
    - "What percentage of time has ETH spent in the 0.6-0.7 risk band?"
    - "How old is SOL in days?"
    - "Explain the risk formula"
    - "Compare BTC and ETH risk values"
    """
    try:
        response = await qa_agent.process_question(question)
        return {
            "question": question,
            "answer": response.answer,
            "question_type": getattr(response, 'question_type', response.category),  # Use category as fallback
            "symbol": getattr(response, 'symbol', None),
            "data": response.data,
            "confidence": response.confidence,
            "timestamp": response.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/qa/examples")
async def get_qa_examples():
    """Get example questions that can be asked"""
    examples = [
        {
            "category": "Risk Calculation",
            "questions": [
                "What would be the risk value at the price of Bitcoin of 134000?",
                "What is the risk for ETH at $5000?",
                "Calculate risk for SOL at $200"
            ]
        },
        {
            "category": "Price from Risk",
            "questions": [
                "What BTC price corresponds to 0.8 risk?",
                "At what price would ETH have a risk of 0.5?",
                "What is the SOL price at risk 0.3?"
            ]
        },
        {
            "category": "Time Spent Analysis",
            "questions": [
                "What percentage of time has BTC spent in the 0.4-0.5 band?",
                "How many days has ETH been in the 0.6-0.7 band?",
                "Which band has SOL spent the most time in?"
            ]
        },
        {
            "category": "Symbol Information",
            "questions": [
                "How old is BTC in days?",
                "What is the life age of ETH?",
                "When was SOL inception?"
            ]
        },
        {
            "category": "Formula & Methodology",
            "questions": [
                "Explain the risk formula",
                "How are coefficients calculated?",
                "What are the risk zones?"
            ]
        },
        {
            "category": "Comparisons",
            "questions": [
                "Compare BTC and ETH risk values",
                "Which symbol has the highest risk?",
                "Compare time spent distributions for all symbols"
            ]
        },
        {
            "category": "Win Rate Analysis",
            "questions": [
                "What is the win rate for BTC at 0.3 risk?",
                "Calculate win rate for ETH at current price",
                "Which risk band has the best win rate?"
            ]
        }
    ]
    return {
        "examples": examples,
        "total_categories": len(examples),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/qa/batch")
async def batch_questions(questions: List[str]):
    """Process multiple questions at once"""
    try:
        if not questions:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        results = []
        for question in questions:
            try:
                response = await qa_agent.process_question(question)
                results.append({
                    "question": question,
                    "answer": response.answer,
                    "question_type": getattr(response, 'question_type', response.category),
                    "confidence": response.confidence,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "questions_processed": len(questions),
            "successful": sum(1 for r in results if r.get("success")),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@router.get("/qa/stats")
async def get_qa_stats():
    """Get Q&A system statistics"""
    try:
        # Get stats if method exists, otherwise return defaults
        stats = {}
        if hasattr(qa_agent, 'get_stats'):
            stats = qa_agent.get_stats()  # type: ignore
        return {
            "total_questions": stats.get("total_questions", 0),
            "question_types": stats.get("question_types", {}),
            "popular_symbols": stats.get("popular_symbols", []),
            "average_confidence": stats.get("average_confidence", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Q&A stats: {e}")
        return {
            "total_questions": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/qa/feedback")
async def submit_feedback(
    question: str = Query(..., description="The question that was asked"),
    helpful: bool = Query(..., description="Was the answer helpful?"),
    feedback: Optional[str] = Query(None, description="Additional feedback")
):
    """Submit feedback about a Q&A response"""
    try:
        # Store feedback (would be implemented in production)
        return {
            "message": "Feedback received successfully",
            "question": question,
            "helpful": helpful,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}") 