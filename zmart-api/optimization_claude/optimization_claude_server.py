#!/usr/bin/env python3
"""
OptimizationClaude Service - FastAPI Server
Advanced context optimization service with intelligent scheduling and performance monitoring
"""

import asyncio
import logging
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import threading

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the existing optimization service
try:
    from services.optimization_claude_service import OptimizationClaude, OptimizationResult, OptimizationAnalysis
except ImportError:
    # Fallback if import fails
    OptimizationClaude = None
    OptimizationResult = None
    OptimizationAnalysis = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="OptimizationClaude Service",
    description="Advanced context optimization service with intelligent scheduling and performance monitoring for CLAUDE.md",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
service_start_time = time.time()
optimization_service = None
optimization_active = True
scheduler_thread = None

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    service: str
    version: str
    optimization_active: bool

class OptimizationRequest(BaseModel):
    force_optimization: bool = False
    target_file: Optional[str] = None

class OptimizationStatusResponse(BaseModel):
    status: str
    last_optimization: Optional[str]
    next_scheduled: Optional[str]
    current_interval: int
    file_size: int
    performance_level: str
    metrics: Dict[str, Any]

class SystemProtectionRequest(BaseModel):
    service_name: str
    protected_files: List[str]
    protected_ports: List[int]
    backup_required: bool = True
    integrity_checks: List[str] = []

def initialize_optimization_service():
    """Initialize the optimization service"""
    global optimization_service
    
    try:
        if OptimizationClaude is None:
            logger.error("❌ OptimizationClaude service not available")
            return False
        
        # Configuration for the optimization service
        config = {
            'claude_md_path': str(project_root / 'CLAUDE.md'),
            'optimization_data_path': str(project_root / 'data' / 'optimization_history.json'),
            'default_interval': 2 * 60 * 60,  # 2 hours
            'min_interval': 30 * 60,  # 30 minutes
            'max_interval': 6 * 60 * 60,  # 6 hours
            'min_mdc_files': 50,
            'size_thresholds': {
                'optimal': 25000,
                'good': 30000,
                'fair': 35000,
                'large': 40000
            },
            'enable_aggressive_optimization': True,
            'enable_adaptive_scheduling': True,
            'enable_smart_skipping': True
        }
        
        optimization_service = OptimizationClaude(config)
        logger.info("✅ OptimizationClaude service initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize optimization service: {e}")
        return False

def register_with_system_protection():
    """Register this service with the System Protection Service"""
    try:
        import requests
        
        protection_config = {
            'service_name': 'optimization-claude-service',
            'protected_files': [
                'CLAUDE.md',
                'data/optimization_history.json',
                'services/optimization_claude_service.py'
            ],
            'protected_ports': [8998],
            'backup_required': True,
            'integrity_checks': ['file_size', 'optimization_history', 'service_health']
        }
        
        response = requests.post(
            'http://localhost:8999/api/system/register-service',
            json=protection_config,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Registered with System Protection Service")
            return True
        else:
            logger.warning(f"⚠️ Failed to register with System Protection Service: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Could not register with System Protection Service: {e}")
        return False

def start_optimization_scheduler():
    """Start the optimization scheduler thread"""
    global scheduler_thread
    
    def run_scheduler():
        while optimization_active and optimization_service:
            try:
                # Check if optimization is needed
                if optimization_service.should_optimize():
                    logger.info("🔄 Starting scheduled optimization")
                    result = optimization_service.optimize()
                    if result.success:
                        logger.info(f"✅ Scheduled optimization completed: {result.size_difference} chars saved")
                    else:
                        logger.warning(f"⚠️ Scheduled optimization failed: {result.error}")
                
                # Sleep for the current interval
                time.sleep(optimization_service.current_interval)
                
            except Exception as e:
                logger.error(f"Error in optimization scheduler: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("✅ Optimization scheduler started")

@app.on_event("startup")
async def startup_event():
    """Initialize the optimization service on startup"""
    logger.info("🚀 Starting OptimizationClaude Service")
    
    # Initialize optimization service
    if not initialize_optimization_service():
        logger.error("❌ Failed to initialize optimization service")
        return
    
    # Register with system protection
    register_with_system_protection()
    
    # Start optimization scheduler
    start_optimization_scheduler()
    
    logger.info("✅ OptimizationClaude Service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - service_start_time
    
    # Check if optimization service is healthy
    service_healthy = optimization_service is not None and optimization_active
    
    return HealthResponse(
        status="healthy" if service_healthy else "unhealthy",
        timestamp=time.time(),
        uptime=uptime,
        service="optimization-claude-service",
        version="1.0.0",
        optimization_active=optimization_active
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if optimization service is ready
        service_ready = (
            optimization_service is not None and 
            optimization_active and 
            scheduler_thread and 
            scheduler_thread.is_alive()
        )
        
        if service_ready:
            return {"status": "ready", "service": "optimization-claude-service", "optimization_active": True}
        else:
            return {"status": "not_ready", "service": "optimization-claude-service", "optimization_active": False}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    uptime = time.time() - service_start_time
    
    metrics = {
        "service": "optimization-claude-service",
        "uptime_seconds": uptime,
        "status": "running",
        "timestamp": time.time(),
        "optimization": {
            "active": optimization_active,
            "scheduler_running": scheduler_thread and scheduler_thread.is_alive() if scheduler_thread else False
        }
    }
    
    # Add optimization service metrics if available
    if optimization_service and hasattr(optimization_service, 'metrics'):
        metrics["optimization"].update(optimization_service.metrics)
    
    return metrics

@app.get("/api/optimization/status", response_model=OptimizationStatusResponse)
async def get_optimization_status():
    """Get current optimization status"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Optimization service not available")
        
        # Get current file size
        claude_md_path = Path(optimization_service.claude_md_path)
        file_size = claude_md_path.stat().st_size if claude_md_path.exists() else 0
        
        # Determine performance level
        performance_level = "optimal"
        for threshold_name, threshold_size in optimization_service.config['size_thresholds'].items():
            if file_size > threshold_size:
                performance_level = threshold_name
        
        # Get last optimization time
        last_optimization = None
        if hasattr(optimization_service, 'last_optimization_time'):
            last_optimization = optimization_service.last_optimization_time
        
        # Calculate next scheduled time
        next_scheduled = None
        if last_optimization and optimization_service.current_interval:
            next_time = datetime.fromisoformat(last_optimization) + timedelta(seconds=optimization_service.current_interval)
            next_scheduled = next_time.isoformat()
        
        return OptimizationStatusResponse(
            status="active" if optimization_active else "inactive",
            last_optimization=last_optimization,
            next_scheduled=next_scheduled,
            current_interval=optimization_service.current_interval,
            file_size=file_size,
            performance_level=performance_level,
            metrics=optimization_service.metrics if hasattr(optimization_service, 'metrics') else {}
        )
        
    except Exception as e:
        logger.error(f"Error getting optimization status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.post("/api/optimization/run")
async def run_optimization(request: OptimizationRequest):
    """Run optimization manually"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Optimization service not available")
        
        logger.info("🔄 Starting manual optimization")
        
        # Run optimization
        result = optimization_service.optimize()
        
        if result.success:
            return {
                "success": True,
                "message": "Optimization completed successfully",
                "result": {
                    "original_size": result.original_size,
                    "optimized_size": result.optimized_size,
                    "size_difference": result.size_difference,
                    "optimizations": result.optimizations,
                    "processing_time": result.processing_time,
                    "performance_level": result.performance_level,
                    "recommendations": result.recommendations
                }
            }
        else:
            raise HTTPException(status_code=500, detail=f"Optimization failed: {result.error}")
            
    except Exception as e:
        logger.error(f"Error running optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Error running optimization: {str(e)}")

@app.get("/api/optimization/analysis")
async def get_optimization_analysis():
    """Get optimization analysis"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Optimization service not available")
        
        # Analyze optimization needs
        analysis = optimization_service.analyze_optimization_needs()
        
        return {
            "success": True,
            "analysis": {
                "priority": analysis.priority,
                "urgency": analysis.urgency,
                "reasons": analysis.reasons,
                "size": analysis.size,
                "lines": analysis.lines,
                "estimated_savings": analysis.estimated_savings
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analysis: {str(e)}")

@app.get("/api/optimization/history")
async def get_optimization_history():
    """Get optimization history"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Optimization service not available")
        
        # Load optimization history
        history_path = Path(optimization_service.optimization_data_path)
        if history_path.exists():
            with open(history_path, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        return {
            "success": True,
            "history": history,
            "total_entries": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "OptimizationClaude Service",
        "version": "1.0.0",
        "status": "running",
        "priority": "HIGH",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "status": "/api/optimization/status",
            "run": "/api/optimization/run",
            "analysis": "/api/optimization/analysis",
            "history": "/api/optimization/history"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OptimizationClaude Service")
    parser.add_argument("--port", type=int, default=8998, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting OptimizationClaude Service on {args.host}:{args.port}")
    
    uvicorn.run(
        "optimization_claude_server:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="info" if not args.debug else "debug"
    )
