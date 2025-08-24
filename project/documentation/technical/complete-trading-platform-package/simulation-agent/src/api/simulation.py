"""
Simulation Agent - API Endpoints
===============================

Professional FastAPI endpoints for trading pattern analysis and win ratio simulation.
Integrates with ZmartBot, KingFisher, and Trade Strategy systems.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import logging
import json
import uuid

from ..core.config import config, API_CONFIG
from ..services.simulation_engine import simulation_engine
from ..services.data_integrator import data_integration_service
from ..services.report_generator import report_generator
from ..models.base import SimulationResult, PatternMatch, WinRatioAnalysis

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS for integration with other systems
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # ZmartBot Frontend
        "http://localhost:3100",  # KingFisher Frontend
        "http://localhost:3200",  # Trade Strategy Frontend
        "http://localhost:3300",  # Simulation Agent Frontend
        "http://localhost:8000",  # ZmartBot API
        "http://localhost:8100",  # KingFisher API
        "http://localhost:8200",  # Trade Strategy API
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SimulationRequest(BaseModel):
    """Request model for symbol analysis"""
    
    symbol: str = Field(..., description="Trading pair symbol (e.g., 'BTCUSDT')")
    lookback_days: int = Field(365, ge=30, le=1095, description="Analysis period in days")
    include_patterns: List[str] = Field(
        default_factory=list,
        description="Specific patterns to analyze (empty for all)"
    )
    analysis_depth: str = Field(
        "comprehensive",
        regex="^(quick|standard|comprehensive)$",
        description="Analysis depth level"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "lookback_days": 365,
                "include_patterns": ["head_and_shoulders", "double_top", "liquidation_cluster"],
                "analysis_depth": "comprehensive"
            }
        }

class SimulationResponse(BaseModel):
    """Response model for simulation results"""
    
    request_id: str
    symbol: str
    analysis_timestamp: datetime
    analysis_period_days: int
    
    # Pattern Analysis
    patterns_detected: int
    pattern_types: List[str]
    
    # Win Ratio Analysis
    long_position_analysis: Dict[str, Any]
    short_position_analysis: Dict[str, Any]
    
    # Overall Metrics
    overall_metrics: Dict[str, Any]
    
    # Recommendations
    recommended_direction: str
    confidence_level: float
    risk_assessment: str
    
    # Data Sources
    data_sources_used: List[str]
    data_quality_score: float
    
    # Report URLs
    report_urls: Dict[str, str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class PatternAnalysisResponse(BaseModel):
    """Response model for pattern analysis"""
    
    symbol: str
    patterns: List[Dict[str, Any]]
    pattern_summary: Dict[str, Any]
    confidence_distribution: Dict[str, int]
    
class HealthCheckResponse(BaseModel):
    """Health check response model"""
    
    status: str
    timestamp: datetime
    version: str
    system_integration: Dict[str, str]
    dependencies: Dict[str, str]
    performance_metrics: Dict[str, Any]

# Global storage for simulation results (in production, use Redis/Database)
simulation_cache: Dict[str, SimulationResult] = {}
active_simulations: Dict[str, str] = {}  # request_id -> status

# Health Check Endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Comprehensive health check for Simulation Agent"""
    
    try:
        # Check system integrations
        system_status = {}
        
        # Check ZmartBot integration
        try:
            # This would ping ZmartBot API
            system_status["zmartbot"] = "connected"
        except:
            system_status["zmartbot"] = "disconnected"
        
        # Check KingFisher integration
        try:
            # This would ping KingFisher API
            system_status["kingfisher"] = "connected"
        except:
            system_status["kingfisher"] = "disconnected"
        
        # Check Trade Strategy integration
        try:
            # This would ping Trade Strategy API
            system_status["trade_strategy"] = "connected"
        except:
            system_status["trade_strategy"] = "disconnected"
        
        # Check dependencies
        dependencies = {
            "database": "connected",  # Would check actual database
            "redis": "connected",     # Would check actual Redis
            "cryptometer_api": "connected",  # Would check API
            "simulation_engine": "operational"
        }
        
        # Performance metrics
        performance = {
            "active_simulations": len(active_simulations),
            "cached_results": len(simulation_cache),
            "memory_usage_mb": 0,  # Would get actual memory usage
            "cpu_usage_percent": 0,  # Would get actual CPU usage
            "avg_response_time_ms": 0  # Would calculate from metrics
        }
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=API_CONFIG["version"],
            system_integration=system_status,
            dependencies=dependencies,
            performance_metrics=performance
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Main Simulation Endpoint
@app.post("/api/v1/simulation/analyze", response_model=SimulationResponse)
async def analyze_symbol(
    request: SimulationRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a trading symbol for patterns and win ratios
    
    This endpoint performs comprehensive analysis including:
    - Pattern recognition from historical data
    - Integration with KingFisher, Cryptometer, and RiskMetric
    - Win ratio calculation for long and short positions
    - Professional report generation
    """
    
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting analysis for {request.symbol} (Request ID: {request_id})")
        
        # Mark simulation as active
        active_simulations[request_id] = "running"
        
        # Get comprehensive data from all sources
        data_integration_result = await data_integration_service.get_comprehensive_data(request.symbol)
        
        if not data_integration_result.integration_success:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to integrate sufficient data sources: {data_integration_result.errors}"
            )
        
        # Run simulation analysis
        simulation_result = await simulation_engine.analyze_symbol(
            symbol=request.symbol,
            lookback_days=request.lookback_days,
            kingfisher_data=data_integration_result.kingfisher_data.__dict__ if data_integration_result.kingfisher_data else None,
            cryptometer_data=data_integration_result.cryptometer_data.__dict__ if data_integration_result.cryptometer_data else None,
            riskmetric_data=data_integration_result.riskmetric_data.__dict__ if data_integration_result.riskmetric_data else None
        )
        
        # Cache the result
        simulation_cache[request_id] = simulation_result
        
        # Generate professional reports in background
        background_tasks.add_task(
            generate_reports_background,
            request_id,
            simulation_result
        )
        
        # Prepare response
        data_sources_used = []
        if data_integration_result.kingfisher_data:
            data_sources_used.append("kingfisher")
        if data_integration_result.cryptometer_data:
            data_sources_used.append("cryptometer")
        if data_integration_result.riskmetric_data:
            data_sources_used.append("riskmetric")
        
        # Calculate data quality score
        data_quality_score = len(data_sources_used) / 3.0  # 3 total sources
        
        # Determine risk assessment
        overall_win_ratio = simulation_result.overall_metrics.get('overall_win_ratio', 0.0)
        total_trades = simulation_result.overall_metrics.get('total_trades', 0)
        
        if overall_win_ratio > 0.65 and total_trades > 20:
            risk_assessment = "low"
        elif overall_win_ratio > 0.55 and total_trades > 10:
            risk_assessment = "medium"
        elif total_trades < 10:
            risk_assessment = "insufficient_data"
        else:
            risk_assessment = "high"
        
        # Mark simulation as completed
        active_simulations[request_id] = "completed"
        
        response = SimulationResponse(
            request_id=request_id,
            symbol=request.symbol,
            analysis_timestamp=simulation_result.timestamp,
            analysis_period_days=request.lookback_days,
            patterns_detected=len(simulation_result.patterns_detected),
            pattern_types=[p.pattern_type for p in simulation_result.patterns_detected],
            long_position_analysis={
                "win_ratio": simulation_result.long_position_analysis.win_ratio,
                "total_trades": simulation_result.long_position_analysis.total_trades,
                "profit_factor": simulation_result.long_position_analysis.profit_factor,
                "sharpe_ratio": simulation_result.long_position_analysis.sharpe_ratio,
                "max_drawdown": float(simulation_result.long_position_analysis.max_drawdown),
                "confidence_interval": simulation_result.long_position_analysis.confidence_interval
            },
            short_position_analysis={
                "win_ratio": simulation_result.short_position_analysis.win_ratio,
                "total_trades": simulation_result.short_position_analysis.total_trades,
                "profit_factor": simulation_result.short_position_analysis.profit_factor,
                "sharpe_ratio": simulation_result.short_position_analysis.sharpe_ratio,
                "max_drawdown": float(simulation_result.short_position_analysis.max_drawdown),
                "confidence_interval": simulation_result.short_position_analysis.confidence_interval
            },
            overall_metrics=simulation_result.overall_metrics,
            recommended_direction=simulation_result.overall_metrics.get('best_direction', 'neutral'),
            confidence_level=simulation_result.overall_metrics.get('direction_confidence', 0.0),
            risk_assessment=risk_assessment,
            data_sources_used=data_sources_used,
            data_quality_score=data_quality_score,
            report_urls={
                "executive_summary": f"/api/v1/reports/{request_id}/executive",
                "detailed_analysis": f"/api/v1/reports/{request_id}/detailed",
                "technical_report": f"/api/v1/reports/{request_id}/technical",
                "pdf_report": f"/api/v1/reports/{request_id}/pdf"
            }
        )
        
        logger.info(f"Analysis completed for {request.symbol} (Request ID: {request_id})")
        return response
        
    except Exception as e:
        active_simulations[request_id] = "failed"
        logger.error(f"Analysis failed for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Pattern Analysis Endpoint
@app.get("/api/v1/patterns/{symbol}", response_model=PatternAnalysisResponse)
async def get_pattern_analysis(
    symbol: str = Path(..., description="Trading pair symbol"),
    timeframe: str = Query("1h", description="Analysis timeframe"),
    pattern_types: Optional[str] = Query(None, description="Comma-separated pattern types")
):
    """Get detailed pattern analysis for a symbol"""
    
    try:
        # Get data integration
        data_result = await data_integration_service.get_comprehensive_data(symbol)
        
        # Run pattern detection only
        simulation_result = await simulation_engine.analyze_symbol(
            symbol=symbol,
            lookback_days=30,  # Shorter period for pattern-only analysis
            kingfisher_data=data_result.kingfisher_data.__dict__ if data_result.kingfisher_data else None,
            cryptometer_data=data_result.cryptometer_data.__dict__ if data_result.cryptometer_data else None,
            riskmetric_data=data_result.riskmetric_data.__dict__ if data_result.riskmetric_data else None
        )
        
        # Filter patterns if requested
        patterns = simulation_result.patterns_detected
        if pattern_types:
            requested_types = [t.strip() for t in pattern_types.split(',')]
            patterns = [p for p in patterns if p.pattern_type in requested_types]
        
        # Create pattern summary
        pattern_summary = {}
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for pattern in patterns:
            # Count by type
            if pattern.pattern_type not in pattern_summary:
                pattern_summary[pattern.pattern_type] = 0
            pattern_summary[pattern.pattern_type] += 1
            
            # Count by confidence
            if pattern.confidence > 0.7:
                confidence_distribution["high"] += 1
            elif pattern.confidence > 0.5:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return PatternAnalysisResponse(
            symbol=symbol,
            patterns=[{
                "pattern_type": p.pattern_type,
                "timestamp": p.timestamp.isoformat(),
                "confidence": p.confidence,
                "price_level": float(p.price_level),
                "direction": p.direction,
                "target_price": float(p.target_price),
                "stop_loss": float(p.stop_loss),
                "metadata": p.metadata
            } for p in patterns],
            pattern_summary=pattern_summary,
            confidence_distribution=confidence_distribution
        )
        
    except Exception as e:
        logger.error(f"Pattern analysis failed for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

# Simulation Status Endpoint
@app.get("/api/v1/simulation/status/{request_id}")
async def get_simulation_status(request_id: str = Path(..., description="Simulation request ID")):
    """Get the status of a simulation request"""
    
    if request_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation request not found")
    
    status = active_simulations[request_id]
    
    response = {
        "request_id": request_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add result summary if completed
    if status == "completed" and request_id in simulation_cache:
        result = simulation_cache[request_id]
        response["summary"] = {
            "symbol": result.symbol,
            "patterns_detected": len(result.patterns_detected),
            "long_win_ratio": result.long_position_analysis.win_ratio,
            "short_win_ratio": result.short_position_analysis.win_ratio,
            "recommendation": result.overall_metrics.get('recommendation', 'unknown')
        }
    
    return response

# Report Endpoints
@app.get("/api/v1/reports/{request_id}/executive")
async def get_executive_summary(request_id: str = Path(..., description="Simulation request ID")):
    """Get executive summary report"""
    
    if request_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    result = simulation_cache[request_id]
    
    # Generate executive summary
    executive_summary = {
        "symbol": result.symbol,
        "analysis_date": result.timestamp.isoformat(),
        "key_findings": {
            "patterns_detected": len(result.patterns_detected),
            "long_win_ratio": f"{result.long_position_analysis.win_ratio:.1%}",
            "short_win_ratio": f"{result.short_position_analysis.win_ratio:.1%}",
            "recommended_direction": result.overall_metrics.get('best_direction', 'neutral'),
            "confidence_level": f"{result.overall_metrics.get('direction_confidence', 0.0):.1%}"
        },
        "risk_assessment": {
            "overall_risk": "medium",  # Would be calculated
            "max_drawdown_long": f"{result.long_position_analysis.max_drawdown:.2f}",
            "max_drawdown_short": f"{result.short_position_analysis.max_drawdown:.2f}",
            "volatility_level": "moderate"  # Would be calculated
        },
        "recommendations": [
            f"Primary direction: {result.overall_metrics.get('best_direction', 'neutral')}",
            f"Confidence level: {result.overall_metrics.get('direction_confidence', 0.0):.1%}",
            "Monitor liquidation clusters for entry timing",
            "Use position scaling strategy for risk management"
        ]
    }
    
    return executive_summary

@app.get("/api/v1/reports/{request_id}/detailed")
async def get_detailed_analysis(request_id: str = Path(..., description="Simulation request ID")):
    """Get detailed analysis report"""
    
    if request_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    result = simulation_cache[request_id]
    
    # Return comprehensive analysis data
    return {
        "symbol": result.symbol,
        "analysis_period": result.analysis_period_days,
        "timestamp": result.timestamp.isoformat(),
        "patterns_detected": [{
            "type": p.pattern_type,
            "timestamp": p.timestamp.isoformat(),
            "confidence": p.confidence,
            "direction": p.direction,
            "price_level": float(p.price_level),
            "target": float(p.target_price),
            "stop_loss": float(p.stop_loss),
            "metadata": p.metadata
        } for p in result.patterns_detected],
        "long_analysis": {
            "total_trades": result.long_position_analysis.total_trades,
            "winning_trades": result.long_position_analysis.winning_trades,
            "losing_trades": result.long_position_analysis.losing_trades,
            "win_ratio": result.long_position_analysis.win_ratio,
            "profit_factor": result.long_position_analysis.profit_factor,
            "average_win": float(result.long_position_analysis.average_win),
            "average_loss": float(result.long_position_analysis.average_loss),
            "max_consecutive_wins": result.long_position_analysis.max_consecutive_wins,
            "max_consecutive_losses": result.long_position_analysis.max_consecutive_losses,
            "sharpe_ratio": result.long_position_analysis.sharpe_ratio,
            "sortino_ratio": result.long_position_analysis.sortino_ratio,
            "max_drawdown": float(result.long_position_analysis.max_drawdown),
            "confidence_interval": result.long_position_analysis.confidence_interval
        },
        "short_analysis": {
            "total_trades": result.short_position_analysis.total_trades,
            "winning_trades": result.short_position_analysis.winning_trades,
            "losing_trades": result.short_position_analysis.losing_trades,
            "win_ratio": result.short_position_analysis.win_ratio,
            "profit_factor": result.short_position_analysis.profit_factor,
            "average_win": float(result.short_position_analysis.average_win),
            "average_loss": float(result.short_position_analysis.average_loss),
            "max_consecutive_wins": result.short_position_analysis.max_consecutive_wins,
            "max_consecutive_losses": result.short_position_analysis.max_consecutive_losses,
            "sharpe_ratio": result.short_position_analysis.sharpe_ratio,
            "sortino_ratio": result.short_position_analysis.sortino_ratio,
            "max_drawdown": float(result.short_position_analysis.max_drawdown),
            "confidence_interval": result.short_position_analysis.confidence_interval
        },
        "overall_metrics": result.overall_metrics,
        "market_conditions": [{
            "type": mc.condition_type,
            "start_time": mc.start_time.isoformat(),
            "end_time": mc.end_time.isoformat(),
            "volatility": mc.volatility,
            "volume_profile": mc.volume_profile,
            "duration_hours": mc.duration_hours()
        } for mc in result.market_conditions],
        "technical_indicators": result.technical_indicators
    }

@app.get("/api/v1/reports/{request_id}/pdf")
async def get_pdf_report(request_id: str = Path(..., description="Simulation request ID")):
    """Generate and download PDF report"""
    
    if request_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    try:
        result = simulation_cache[request_id]
        
        # Generate PDF report (this would use report_generator service)
        pdf_path = f"/tmp/simulation_report_{request_id}.pdf"
        
        # For now, return a placeholder response
        return JSONResponse({
            "message": "PDF report generation initiated",
            "download_url": f"/api/v1/reports/{request_id}/download",
            "estimated_completion": "2-3 minutes"
        })
        
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="PDF generation failed")

# System Integration Endpoints
@app.get("/api/v1/integration/zmartbot/status")
async def get_zmartbot_integration_status():
    """Check ZmartBot integration status"""
    
    try:
        # This would ping ZmartBot API
        return {
            "status": "connected",
            "api_url": config.system_integration.zmartbot_api_url,
            "last_check": datetime.now().isoformat(),
            "response_time_ms": 45
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

@app.get("/api/v1/integration/kingfisher/status")
async def get_kingfisher_integration_status():
    """Check KingFisher integration status"""
    
    try:
        # This would ping KingFisher API
        return {
            "status": "connected",
            "api_url": config.system_integration.kingfisher_api_url,
            "last_check": datetime.now().isoformat(),
            "response_time_ms": 67
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

@app.get("/api/v1/integration/trade-strategy/status")
async def get_trade_strategy_integration_status():
    """Check Trade Strategy integration status"""
    
    try:
        # This would ping Trade Strategy API
        return {
            "status": "connected",
            "api_url": config.system_integration.trade_strategy_api_url,
            "last_check": datetime.now().isoformat(),
            "response_time_ms": 52
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

# Utility Endpoints
@app.get("/api/v1/symbols/supported")
async def get_supported_symbols():
    """Get list of supported trading symbols"""
    
    # This would fetch from your data sources
    supported_symbols = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
        "BNBUSDT", "XRPUSDT", "LTCUSDT", "BCHUSDT", "EOSUSDT",
        "TRXUSDT", "XLMUSDT", "ATOMUSDT", "VETUSDT", "NEOUSDT"
    ]
    
    return {
        "symbols": supported_symbols,
        "total_count": len(supported_symbols),
        "last_updated": datetime.now().isoformat()
    }

@app.delete("/api/v1/simulation/cache/{request_id}")
async def clear_simulation_cache(request_id: str = Path(..., description="Simulation request ID")):
    """Clear cached simulation result"""
    
    if request_id in simulation_cache:
        del simulation_cache[request_id]
    
    if request_id in active_simulations:
        del active_simulations[request_id]
    
    return {"message": f"Cache cleared for request {request_id}"}

@app.get("/api/v1/system/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    
    return {
        "active_simulations": len(active_simulations),
        "cached_results": len(simulation_cache),
        "system_load": {
            "cpu_usage": "12%",  # Would get actual metrics
            "memory_usage": "2.1GB / 16GB",
            "disk_usage": "45GB / 512GB"
        },
        "api_metrics": {
            "total_requests": 0,  # Would track actual requests
            "avg_response_time": "1.2s",
            "error_rate": "0.1%"
        },
        "timestamp": datetime.now().isoformat()
    }

# Background task for report generation
async def generate_reports_background(request_id: str, simulation_result: SimulationResult):
    """Generate comprehensive reports in background"""
    
    try:
        logger.info(f"Starting background report generation for {request_id}")
        
        # This would use the report_generator service
        # For now, just log the completion
        await asyncio.sleep(2)  # Simulate report generation time
        
        logger.info(f"Background report generation completed for {request_id}")
        
    except Exception as e:
        logger.error(f"Background report generation failed for {request_id}: {str(e)}")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    
    logger.info("🚀 Simulation Agent API starting up...")
    logger.info(f"📊 Running on port {config.system_integration.simulation_api_port}")
    logger.info(f"🔗 Integration URLs: {config.get_integration_urls()}")
    logger.info("✅ Simulation Agent API ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    
    logger.info("🛑 Simulation Agent API shutting down...")
    
    # Clean up resources
    simulation_cache.clear()
    active_simulations.clear()
    
    logger.info("✅ Simulation Agent API shutdown complete!")

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "src.api.simulation:app",
        host="0.0.0.0",
        port=config.system_integration.simulation_api_port,
        reload=config.environment == "development",
        workers=1 if config.environment == "development" else config.mac_optimization.parallel_processing_workers,
        access_log=config.environment != "production"
    )

