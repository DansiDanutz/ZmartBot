#!/usr/bin/env python3
"""
Sentiment Analysis API Routes
Endpoints for Grok-X sentiment analysis integration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.services.sentiment_scoring_service import sentiment_scoring_service
from src.agents.sentiment.grok_x_sentiment_agent import grok_x_sentiment_agent

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/sentiment",
    tags=["sentiment"]
)

@router.get("/analyze/{symbol}")
async def analyze_sentiment(
    symbol: str,
    include_components: bool = Query(True, description="Include component breakdown")
) -> Dict[str, Any]:
    """
    Analyze sentiment for a specific symbol
    
    Args:
        symbol: Trading symbol (e.g., BTC, ETH)
        include_components: Whether to include detailed component scores
        
    Returns:
        Sentiment analysis results
    """
    try:
        # Get sentiment score
        score = await sentiment_scoring_service.get_sentiment_score(symbol.upper())
        
        response = {
            "success": True,
            "symbol": score.symbol,
            "sentiment": {
                "score": round(score.sentiment_score, 2),
                "raw_sentiment": round(score.raw_sentiment, 2),
                "confidence": round(score.confidence, 2),
                "label": score.signals.get('sentiment_label', 'NEUTRAL'),
                "action": score.signals.get('action', 'HOLD'),
                "strength": score.signals.get('strength', 'NEUTRAL')
            },
            "recommendation": sentiment_scoring_service.get_sentiment_recommendation(score),
            "signals": score.signals,
            "timestamp": score.timestamp.isoformat()
        }
        
        if include_components:
            response["components"] = {
                k: round(v, 2) for k, v in score.components.items()
            }
        
        # Add weighted contribution for scoring system
        response["scoring_contribution"] = {
            "weight": sentiment_scoring_service.SENTIMENT_WEIGHT,
            "contribution": round(
                sentiment_scoring_service.calculate_weighted_sentiment(score.sentiment_score), 
                2
            )
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/batch")
async def analyze_batch_sentiment(
    symbols: List[str],
    include_components: bool = Query(False, description="Include component breakdown")
) -> Dict[str, Any]:
    """
    Analyze sentiment for multiple symbols
    
    Args:
        symbols: List of trading symbols
        include_components: Whether to include detailed component scores
        
    Returns:
        Batch sentiment analysis results
    """
    try:
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed per request")
        
        # Process symbols
        symbols = [s.upper() for s in symbols]
        
        # Get sentiment scores
        scores = await sentiment_scoring_service.get_multiple_sentiments(symbols)
        
        results = {}
        for symbol, score in scores.items():
            result = {
                "sentiment_score": round(score.sentiment_score, 2),
                "raw_sentiment": round(score.raw_sentiment, 2),
                "confidence": round(score.confidence, 2),
                "label": score.signals.get('sentiment_label', 'NEUTRAL'),
                "action": score.signals.get('action', 'HOLD'),
                "recommendation": sentiment_scoring_service.get_sentiment_recommendation(score)
            }
            
            if include_components:
                result["components"] = {
                    k: round(v, 2) for k, v in score.components.items()
                }
            
            results[symbol] = result
        
        return {
            "success": True,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social/trending")
async def get_trending_sentiments(
    limit: int = Query(10, ge=1, le=50, description="Number of trending symbols")
) -> Dict[str, Any]:
    """
    Get trending symbols based on social sentiment
    
    Args:
        limit: Number of trending symbols to return
        
    Returns:
        Trending symbols with sentiment data
    """
    try:
        # Define top symbols to check (can be made dynamic)
        top_symbols = [
            "BTC", "ETH", "SOL", "BNB", "XRP", 
            "ADA", "DOGE", "AVAX", "DOT"
        ][:limit]
        
        # Get sentiment for top symbols
        scores = await sentiment_scoring_service.get_multiple_sentiments(top_symbols)
        
        # Sort by trending score
        trending = []
        for symbol, score in scores.items():
            trending.append({
                "symbol": symbol,
                "sentiment_score": round(score.raw_sentiment, 2),
                "trending_score": round(score.components.get('trending', 0), 2),
                "social_volume": score.signals.get('social_volume', 0),
                "action": score.signals.get('action', 'HOLD'),
                "key_topics": score.signals.get('key_topics', [])
            })
        
        # Sort by trending score
        trending.sort(key=lambda x: x['trending_score'], reverse=True)
        
        return {
            "success": True,
            "trending": trending,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending sentiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{symbol}")
async def get_sentiment_signals(symbol: str) -> Dict[str, Any]:
    """
    Get detailed sentiment signals for trading decisions
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Detailed sentiment signals
    """
    try:
        # Get full sentiment analysis
        signal = await grok_x_sentiment_agent.analyze_sentiment(symbol.upper())
        
        return {
            "success": True,
            "symbol": signal.symbol,
            "signals": {
                "sentiment_score": round(signal.sentiment_score, 2),
                "confidence": round(signal.confidence, 2),
                "sentiment_label": signal.sentiment_label,
                "grok_sentiment": round(signal.grok_sentiment, 2),
                "x_sentiment": round(signal.x_sentiment, 2),
                "influencer_sentiment": round(signal.influencer_sentiment, 2),
                "retail_sentiment": round(signal.retail_sentiment, 2),
                "whale_sentiment": round(signal.whale_sentiment, 2),
                "social_volume": signal.social_volume,
                "trending_score": round(signal.trending_score, 2),
                "key_topics": signal.key_topics
            },
            "trading_signal": {
                "action": "BUY" if signal.sentiment_score > 25 else "SELL" if signal.sentiment_score < -25 else "HOLD",
                "strength": abs(signal.sentiment_score) / 100,
                "confidence": signal.confidence / 100
            },
            "timestamp": signal.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def sentiment_health_check() -> Dict[str, Any]:
    """
    Check health status of sentiment analysis system
    
    Returns:
        Health status information
    """
    try:
        # Check if APIs are configured
        grok_configured = bool(grok_x_sentiment_agent.grok_api_key)
        x_configured = bool(grok_x_sentiment_agent.x_bearer_token)
        
        # Get rate limit status
        rate_limits = {
            'grok': {
                'calls': grok_x_sentiment_agent.rate_limiter['grok']['calls'],
                'max': grok_x_sentiment_agent.rate_limiter['grok']['max'],
                'remaining': grok_x_sentiment_agent.rate_limiter['grok']['max'] - 
                            grok_x_sentiment_agent.rate_limiter['grok']['calls']
            },
            'x': {
                'calls': grok_x_sentiment_agent.rate_limiter['x']['calls'],
                'max': grok_x_sentiment_agent.rate_limiter['x']['max'],
                'remaining': grok_x_sentiment_agent.rate_limiter['x']['max'] - 
                            grok_x_sentiment_agent.rate_limiter['x']['calls']
            }
        }
        
        return {
            "success": True,
            "status": "healthy",
            "apis": {
                "grok": {
                    "configured": grok_configured,
                    "status": "active" if grok_configured else "not_configured"
                },
                "x_twitter": {
                    "configured": x_configured,
                    "status": "active" if x_configured else "not_configured"
                }
            },
            "rate_limits": rate_limits,
            "cache_size": len(grok_x_sentiment_agent.sentiment_cache),
            "sentiment_weight": sentiment_scoring_service.SENTIMENT_WEIGHT,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment health check: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }