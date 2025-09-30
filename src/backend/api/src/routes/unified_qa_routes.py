#!/usr/bin/env python3
"""
🎓 Unified QA User Agent API Routes
Professional educational analysis with multi-timeframe win rates
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

from src.agents.unified_qa_user_agent import (
    unified_qa_user_agent,
    TimeFrame,
    TeachingStyle,
    AnalysisPackage
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/unified-qa",
    tags=["Unified QA"],
    responses={404: {"description": "Not found"}}
)

# Request/Response models
class AnalysisRequest(BaseModel):
    """Request model for unified analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTC, ETH)")
    question: str = Field(..., description="User's question or analysis request")
    teaching_style: Optional[str] = Field(
        default="intermediate",
        description="Teaching style: beginner, intermediate, advanced, expert"
    )
    package: Optional[str] = Field(
        default="standard",
        description="Analysis package: basic (1 credit), standard (3 credits), premium (5 credits), professional (10 credits)"
    )
    user_level: Optional[str] = Field(
        default=None,
        description="Optional user experience level for personalization"
    )

class WinRateData(BaseModel):
    """Win rate data model"""
    win_rate: str
    confidence: str
    signals_analyzed: int
    composite_score: float
    recommendation: str

class AnalysisResponse(BaseModel):
    """Response model for unified analysis"""
    success: bool
    symbol: str
    timestamp: str
    teaching_style: str
    package: str
    credits_used: int
    analysis: Dict[str, Any]
    recommendations: Dict[str, Any]
    learning_resources: List[Dict[str, str]]
    next_steps: List[str]

class QuickAnalysisRequest(BaseModel):
    """Request for quick analysis"""
    symbols: List[str] = Field(..., description="List of symbols to analyze")
    timeframe: Optional[str] = Field(default="1D-3D", description="Timeframe for analysis")

class InteractiveSessionRequest(BaseModel):
    """Request to start interactive learning session"""
    symbol: str
    topic: str = Field(..., description="Learning topic: basics, technical, risk, strategies")
    duration_minutes: int = Field(default=15, ge=5, le=60)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symbol(request: AnalysisRequest):
    """
    Get comprehensive analysis with educational content and win rates
    
    This endpoint combines data from all QA agents:
    - Cryptometer (market data)
    - RiskMetric (historical patterns)
    - KingFisher (liquidation analysis)
    - Grok & X (sentiment)
    - Whale (large transactions)
    - Blockchain (on-chain metrics)
    
    Returns professional analysis with win rates for 3 timeframes.
    """
    try:
        logger.info(f"Unified analysis request for {request.symbol}")
        
        # Convert string enums with null checks
        teaching_style_str = request.teaching_style or "intermediate"
        package_str = request.package or "standard"
        teaching_style = TeachingStyle[teaching_style_str.upper()]
        package = AnalysisPackage[package_str.upper()]
        
        # Perform analysis
        result = await unified_qa_user_agent.analyze_with_teaching(
            symbol=request.symbol.upper(),
            user_question=request.question,
            teaching_style=teaching_style,
            package=package,
            user_level=request.user_level
        )
        
        if result['success']:
            return AnalysisResponse(**result)
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Analysis failed')
            )
            
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in unified analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/win-rates/{symbol}")
async def get_win_rates(
    symbol: str,
    package: str = Query(default="standard", regex="^(basic|standard|premium|professional)$")
):
    """
    Get win rate predictions for all timeframes
    
    Timeframes analyzed:
    - SHORT (1H-4H): Quick trades
    - MEDIUM (1D-3D): Swing trades
    - LONG (1W-1M): Position trades
    
    Each includes confidence level and recommendations.
    """
    try:
        # Quick analysis focused on win rates
        package_enum = AnalysisPackage[package.upper()]
        
        result = await unified_qa_user_agent.analyze_with_teaching(
            symbol=symbol.upper(),
            user_question=f"What are the win rates for {symbol}?",
            teaching_style=TeachingStyle.INTERMEDIATE,
            package=package_enum
        )
        
        if result['success']:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'win_rates': result['analysis']['win_rates'],
                'recommendations': result['recommendations'],
                'credits_used': result['credits_used'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to calculate win rates"
            )
            
    except Exception as e:
        logger.error(f"Error getting win rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-analysis")
async def quick_analysis(request: QuickAnalysisRequest):
    """
    Get quick win rate analysis for multiple symbols
    
    Useful for:
    - Portfolio overview
    - Comparing opportunities
    - Market scanning
    """
    try:
        results = {}
        
        for symbol in request.symbols[:10]:  # Limit to 10 symbols
            try:
                result = await unified_qa_user_agent.analyze_with_teaching(
                    symbol=symbol.upper(),
                    user_question="Quick win rate check",
                    teaching_style=TeachingStyle.INTERMEDIATE,
                    package=AnalysisPackage.BASIC
                )
                
                if result['success']:
                    # Extract key data
                    win_rates = result['analysis']['win_rates']
                    timeframe_data = win_rates.get(request.timeframe, win_rates.get('1D-3D'))
                    
                    results[symbol] = {
                        'win_rate': timeframe_data.get('win_rate', 'N/A'),
                        'confidence': timeframe_data.get('confidence', 'N/A'),
                        'recommendation': timeframe_data.get('recommendation', 'N/A')
                    }
                else:
                    results[symbol] = {'error': 'Analysis failed'}
                    
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return {
            'success': True,
            'timeframe': request.timeframe,
            'results': results,
            'symbols_analyzed': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interactive-session")
async def start_interactive_session(request: InteractiveSessionRequest):
    """
    Start an interactive learning session
    
    Topics available:
    - basics: Trading fundamentals
    - technical: Technical analysis
    - risk: Risk management
    - strategies: Trading strategies
    """
    try:
        # Create personalized learning session
        session_id = f"session_{datetime.now().timestamp()}"
        
        # Get initial analysis for context
        analysis = await unified_qa_user_agent.analyze_with_teaching(
            symbol=request.symbol.upper(),
            user_question=f"Teach me about {request.topic} for {request.symbol}",
            teaching_style=TeachingStyle.BEGINNER if request.topic == "basics" else TeachingStyle.INTERMEDIATE,
            package=AnalysisPackage.STANDARD
        )
        
        if analysis['success']:
            return {
                'success': True,
                'session_id': session_id,
                'symbol': request.symbol.upper(),
                'topic': request.topic,
                'duration_minutes': request.duration_minutes,
                'initial_lesson': analysis['analysis']['educational_content'],
                'interactive_elements': analysis['analysis']['interactive_elements'],
                'learning_path': [
                    f"Introduction to {request.topic}",
                    f"Applying {request.topic} to {request.symbol}",
                    "Practice exercises",
                    "Q&A and review"
                ],
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to start learning session"
            )
            
    except Exception as e:
        logger.error(f"Error starting interactive session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-resources")
async def get_learning_resources(
    level: str = Query(default="intermediate", regex="^(beginner|intermediate|advanced|expert)$"),
    topic: Optional[str] = Query(default=None)
):
    """
    Get curated learning resources based on user level
    """
    try:
        teaching_style = TeachingStyle[level.upper()]
        
        # Get sample resources (would normally query from database)
        resources = {
            'beginner': [
                {
                    'title': 'Crypto Trading 101',
                    'type': 'video',
                    'duration': '15 min',
                    'description': 'Learn the basics of cryptocurrency trading'
                },
                {
                    'title': 'Understanding Market Orders',
                    'type': 'article',
                    'read_time': '5 min',
                    'description': 'Different order types explained simply'
                },
                {
                    'title': 'Risk Management for Beginners',
                    'type': 'interactive',
                    'duration': '20 min',
                    'description': 'Interactive guide to managing trading risks'
                }
            ],
            'intermediate': [
                {
                    'title': 'Technical Analysis Patterns',
                    'type': 'course',
                    'duration': '2 hours',
                    'description': 'Comprehensive guide to chart patterns'
                },
                {
                    'title': 'Position Sizing Calculator',
                    'type': 'tool',
                    'description': 'Calculate optimal position sizes'
                },
                {
                    'title': 'Multi-Timeframe Analysis',
                    'type': 'webinar',
                    'duration': '45 min',
                    'description': 'Learn to analyze multiple timeframes'
                }
            ],
            'advanced': [
                {
                    'title': 'Quantitative Trading Strategies',
                    'type': 'whitepaper',
                    'pages': 45,
                    'description': 'Advanced algorithmic trading approaches'
                },
                {
                    'title': 'Options and Derivatives',
                    'type': 'course',
                    'duration': '6 hours',
                    'description': 'Advanced derivatives trading'
                },
                {
                    'title': 'Market Microstructure',
                    'type': 'research',
                    'description': 'Understanding order flow and liquidity'
                }
            ],
            'expert': [
                {
                    'title': 'HFT Systems Architecture',
                    'type': 'technical',
                    'description': 'High-frequency trading infrastructure'
                },
                {
                    'title': 'Machine Learning for Trading',
                    'type': 'code',
                    'language': 'Python',
                    'description': 'ML models for price prediction'
                },
                {
                    'title': 'Market Making Strategies',
                    'type': 'simulation',
                    'description': 'Professional market making simulator'
                }
            ]
        }
        
        selected_resources = resources.get(level, resources['intermediate'])
        
        # Filter by topic if provided
        if topic:
            selected_resources = [
                r for r in selected_resources 
                if topic.lower() in r.get('title', '').lower() or 
                   topic.lower() in r.get('description', '').lower()
            ]
        
        return {
            'success': True,
            'level': level,
            'topic': topic,
            'resources': selected_resources,
            'total_resources': len(selected_resources),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_agent_statistics():
    """
    Get statistics about the Unified QA Agent performance
    """
    try:
        stats = unified_qa_user_agent.get_statistics()
        
        return {
            'success': True,
            'statistics': stats,
            'agent_status': {
                'active_agents': stats['active_agents'],
                'total_agents': stats['total_agents'],
                'health': 'healthy' if stats['active_agents'] > 3 else 'degraded'
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credit-packages")
async def get_credit_packages():
    """
    Get available credit packages and pricing
    (For future credit system implementation)
    """
    return {
        'success': True,
        'packages': [
            {
                'name': 'Basic',
                'credits_required': 1,
                'features': [
                    'Single timeframe analysis',
                    'Basic win rate calculation',
                    'Cryptometer data only'
                ]
            },
            {
                'name': 'Standard',
                'credits_required': 3,
                'features': [
                    'All timeframes analysis',
                    'Multiple data sources',
                    'AI-powered insights',
                    'Educational content'
                ]
            },
            {
                'name': 'Premium',
                'credits_required': 5,
                'features': [
                    'Full multi-agent analysis',
                    'Advanced AI predictions',
                    'Interactive learning',
                    'Whale & sentiment data'
                ]
            },
            {
                'name': 'Professional',
                'credits_required': 10,
                'features': [
                    'Institutional-grade analysis',
                    'All data sources',
                    'Custom reports',
                    'API access',
                    'Priority support'
                ]
            }
        ],
        'note': 'Credit system will be activated in production',
        'timestamp': datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the Unified QA service
    """
    try:
        stats = unified_qa_user_agent.get_statistics()
        
        return {
            'status': 'healthy' if stats['active_agents'] > 0 else 'unhealthy',
            'service': 'Unified QA User Agent',
            'active_agents': stats['active_agents'],
            'total_agents': stats['total_agents'],
            'analyses_performed': stats['total_analyses'],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'service': 'Unified QA User Agent',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export router
__all__ = ['router']