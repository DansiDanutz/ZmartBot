from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

from services.enhanced_analysis_service import enhanced_analysis_service, ComprehensiveAnalysis
from services.enhanced_airtable_service import enhanced_airtable_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze-image")
async def analyze_image_comprehensive(
    symbol: str = Form(...),
    image_data: str = Form(...)
) -> Dict[str, Any]:
    """Analyze an image with comprehensive professional analysis"""
    
    try:
        # Parse image data
        image_data_dict = json.loads(image_data)
        
        # Generate comprehensive analysis
        analysis = await enhanced_analysis_service.analyze_image_comprehensive(image_data_dict, symbol)
        
        # Store in Airtable
        storage_result = await enhanced_airtable_service.store_comprehensive_analysis(analysis)
        
        if storage_result["success"]:
            return {
                "success": True,
                "message": f"Comprehensive analysis completed for {symbol}",
                "analysis": {
                    "symbol": analysis.symbol,
                    "timestamp": analysis.timestamp,
                    "overall_sentiment": analysis.overall_sentiment,
                    "overall_confidence": f"{analysis.overall_confidence:.1%}",
                    "current_price": analysis.current_price,
                    "timeframes": {
                        tf: {
                            "long_ratio": f"{tf_analysis.long_ratio:.1%}",
                            "short_ratio": f"{tf_analysis.short_ratio:.1%}",
                            "win_rate": f"{tf_analysis.win_rate:.1%}",
                            "confidence": f"{tf_analysis.confidence:.1%}",
                            "sentiment": tf_analysis.sentiment,
                            "risk_score": f"{tf_analysis.risk_score:.1%}",
                            "key_levels": tf_analysis.key_levels
                        }
                        for tf, tf_analysis in analysis.timeframes.items()
                    },
                    "liquidation_analysis": analysis.liquidation_analysis,
                    "rsi_analysis": analysis.rsi_analysis,
                    "risk_assessment": analysis.risk_assessment,
                    "technical_summary": analysis.technical_summary,
                    "trading_recommendations": analysis.trading_recommendations
                },
                "storage": storage_result
            }
        else:
            return {
                "success": False,
                "message": "Analysis completed but storage failed",
                "analysis": {
                    "symbol": analysis.symbol,
                    "timestamp": analysis.timestamp,
                    "overall_sentiment": analysis.overall_sentiment,
                    "overall_confidence": f"{analysis.overall_confidence:.1%}",
                    "error": storage_result.get("error", "Unknown storage error")
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/process-kingfisher-image")
async def process_kingfisher_image(
    symbol: str = Form(...),
    image_id: str = Form(...),
    significance_score: float = Form(...),
    market_sentiment: str = Form(...),
    total_clusters: int = Form(default=2),
    total_flow_area: int = Form(default=2400),
    liquidation_map_image: Optional[UploadFile] = File(None),
    liquidation_heatmap_image: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:
    """Process a KingFisher image with comprehensive analysis"""
    
    try:
        # Create image data structure
        image_data = {
            "id": image_id,
            "significance_score": significance_score,
            "market_sentiment": market_sentiment,
            "total_clusters": total_clusters,
            "total_flow_area": total_flow_area,
            "confidence": 0.8,
            "liquidation_map_image": liquidation_map_image,
            "liquidation_heatmap_image": liquidation_heatmap_image
        }
        
        # Generate comprehensive analysis
        analysis = await enhanced_analysis_service.analyze_image_comprehensive(image_data, symbol)
        
        # Store in Airtable
        storage_result = await enhanced_airtable_service.store_comprehensive_analysis(analysis)
        
        return {
            "success": True,
            "message": f"KingFisher image processed for {symbol}",
            "analysis": {
                "symbol": analysis.symbol,
                "timestamp": analysis.timestamp,
                "overall_sentiment": analysis.overall_sentiment,
                "overall_confidence": f"{analysis.overall_confidence:.1%}",
                "current_price": analysis.current_price,
                "timeframes": {
                    tf: {
                        "long_ratio": f"{tf_analysis.long_ratio:.1%}",
                        "short_ratio": f"{tf_analysis.short_ratio:.1%}",
                        "win_rate": f"{tf_analysis.win_rate:.1%}",
                        "confidence": f"{tf_analysis.confidence:.1%}",
                        "sentiment": tf_analysis.sentiment,
                        "risk_score": f"{tf_analysis.risk_score:.1%}"
                    }
                    for tf, tf_analysis in analysis.timeframes.items()
                },
                "liquidation_analysis": {
                    "total_clusters": analysis.liquidation_analysis.get("total_clusters", 0),
                    "cascade_risk": analysis.liquidation_analysis.get("cascade_risk", "0%"),
                    "market_sentiment": analysis.liquidation_analysis.get("market_sentiment", "neutral")
                },
                "rsi_analysis": analysis.rsi_analysis,
                "risk_assessment": analysis.risk_assessment,
                "technical_summary": analysis.technical_summary,
                "trading_recommendations": analysis.trading_recommendations
            },
            "storage": storage_result
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing KingFisher image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/analyses/{symbol}")
async def get_symbol_analyses(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """Get comprehensive analyses for a specific symbol"""
    
    try:
        result = await enhanced_airtable_service.get_comprehensive_analyses(symbol, limit)
        return result
        
    except Exception as e:
        logger.error(f"❌ Error retrieving analyses for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@router.get("/analyses")
async def get_all_analyses(limit: int = 10) -> Dict[str, Any]:
    """Get all comprehensive analyses"""
    
    try:
        result = await enhanced_airtable_service.get_comprehensive_analyses(limit=limit)
        return result
        
    except Exception as e:
        logger.error(f"❌ Error retrieving all analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@router.get("/latest/{symbol}")
async def get_latest_analysis(symbol: str) -> Dict[str, Any]:
    """Get the latest comprehensive analysis for a symbol"""
    
    try:
        analysis = enhanced_analysis_service.get_latest_analysis(symbol)
        
        if analysis:
            return {
                "success": True,
                "analysis": {
                    "symbol": analysis.symbol,
                    "timestamp": analysis.timestamp,
                    "overall_sentiment": analysis.overall_sentiment,
                    "overall_confidence": f"{analysis.overall_confidence:.1%}",
                    "current_price": analysis.current_price,
                    "timeframes": {
                        tf: {
                            "long_ratio": f"{tf_analysis.long_ratio:.1%}",
                            "short_ratio": f"{tf_analysis.short_ratio:.1%}",
                            "win_rate": f"{tf_analysis.win_rate:.1%}",
                            "confidence": f"{tf_analysis.confidence:.1%}",
                            "sentiment": tf_analysis.sentiment,
                            "risk_score": f"{tf_analysis.risk_score:.1%}"
                        }
                        for tf, tf_analysis in analysis.timeframes.items()
                    },
                    "liquidation_analysis": analysis.liquidation_analysis,
                    "rsi_analysis": analysis.rsi_analysis,
                    "risk_assessment": analysis.risk_assessment,
                    "technical_summary": analysis.technical_summary,
                    "trading_recommendations": analysis.trading_recommendations
                }
            }
        else:
            return {
                "success": False,
                "message": f"No analysis found for {symbol}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving latest analysis for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@router.get("/statistics")
async def get_analysis_statistics() -> Dict[str, Any]:
    """Get analysis statistics"""
    
    try:
        analyses = enhanced_analysis_service.get_analysis_history()
        
        if not analyses:
            return {
                "success": True,
                "statistics": {
                    "total_analyses": 0,
                    "symbols_analyzed": [],
                    "average_confidence": 0.0,
                    "sentiment_distribution": {"bullish": 0, "bearish": 0, "neutral": 0}
                }
            }
        
        # Calculate statistics
        symbols = list(set(analysis.symbol for analysis in analyses))
        avg_confidence = sum(analysis.overall_confidence for analysis in analyses) / len(analyses)
        
        sentiment_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
        for analysis in analyses:
            sentiment_counts[analysis.overall_sentiment] += 1
        
        return {
            "success": True,
            "statistics": {
                "total_analyses": len(analyses),
                "symbols_analyzed": symbols,
                "average_confidence": f"{avg_confidence:.1%}",
                "sentiment_distribution": sentiment_counts,
                "latest_analysis": analyses[-1].timestamp if analyses else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating analysis statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.post("/test-comprehensive")
async def test_comprehensive_analysis() -> Dict[str, Any]:
    """Test comprehensive analysis with sample data"""
    
    try:
        # Create sample image data
        sample_image_data = {
            "id": "test_image_001",
            "significance_score": 0.75,
            "market_sentiment": "bullish",
            "total_clusters": 3,
            "total_flow_area": 2800,
            "confidence": 0.8
        }
        
        # Generate analysis for ETHUSDT
        analysis = await enhanced_analysis_service.analyze_image_comprehensive(sample_image_data, "ETHUSDT")
        
        return {
            "success": True,
            "message": "Comprehensive analysis test completed",
            "analysis": {
                "symbol": analysis.symbol,
                "timestamp": analysis.timestamp.isoformat(),
                "overall_sentiment": analysis.overall_sentiment,
                "overall_confidence": f"{analysis.overall_confidence:.1%}",
                "current_price": analysis.current_price,
                "timeframes": {
                    tf: {
                        "long_ratio": f"{tf_analysis.long_ratio:.1%}",
                        "short_ratio": f"{tf_analysis.short_ratio:.1%}",
                        "win_rate": f"{tf_analysis.win_rate:.1%}",
                        "confidence": f"{tf_analysis.confidence:.1%}",
                        "sentiment": tf_analysis.sentiment,
                        "risk_score": f"{tf_analysis.risk_score:.1%}"
                    }
                    for tf, tf_analysis in analysis.timeframes.items()
                },
                "liquidation_analysis": {
                    "total_clusters": analysis.liquidation_analysis.get("total_clusters", 0),
                    "cascade_risk": f"{analysis.liquidation_analysis.get('cascade_risk', 0):.1%}",
                    "market_sentiment": analysis.liquidation_analysis.get("market_sentiment", "neutral")
                },
                "rsi_analysis": analysis.rsi_analysis,
                "risk_assessment": analysis.risk_assessment,
                "technical_summary": analysis.technical_summary,
                "trading_recommendations": analysis.trading_recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive analysis test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}") 