#!/usr/bin/env python3
"""
Local AI Models API Routes
Provides endpoints for local AI model integration
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
import json

from src.services.local_ai_models import LocalAIModelsService, AnalysisRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
local_ai_service = LocalAIModelsService()

@router.get("/status")
async def get_model_status():
    """Get status of all local AI models"""
    try:
        status = await local_ai_service.get_model_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.post("/analyze")
async def analyze_liquidation_data(
    symbol: str,
    market_data: Dict[str, Any],
    image_file: Optional[UploadFile] = File(None)
):
    """Analyze liquidation data using local AI models"""
    try:
        logger.info(f"Starting AI analysis for {symbol}")
        
        # Get image data if provided
        image_data = None
        if image_file:
            image_data = await image_file.read()
        
        # Perform analysis
        results = await local_ai_service.analyze_liquidation_data(
            symbol=symbol,
            image_data=image_data if image_data else b"",
            market_data=market_data
        )
        
        return {
            "status": "success",
            "symbol": symbol,
            "analysis_results": {
                model: {
                    "analysis": result.analysis,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "recommendations": result.recommendations,
                    "risk_score": result.risk_score,
                    "timestamp": result.timestamp.isoformat()
                }
                for model, result in results.items()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing liquidation data: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-deepseek")
async def analyze_with_deepseek(
    symbol: str,
    market_data: Dict[str, Any],
    image_file: Optional[UploadFile] = File(None)
):
    """Analyze using deepseek-r1-distill-llama specifically"""
    try:
        logger.info(f"Starting deepseek analysis for {symbol}")
        
        # Get image data if provided
        image_data = None
        if image_file:
            image_data = await image_file.read()
        
        # Create analysis request
        request = AnalysisRequest(
            symbol=symbol,
            image_data=image_data,
            market_data=market_data,
            analysis_type="liquidation_analysis",
            context="KingFisher liquidation map analysis"
        )
        
        # Perform deepseek analysis
        result = await local_ai_service._analyze_with_deepseek(request)
        
        return {
            "status": "success",
            "symbol": symbol,
            "model": "deepseek-r1-distill-llama",
            "analysis": result.analysis,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "recommendations": result.recommendations,
            "risk_score": result.risk_score,
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in deepseek analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Deepseek analysis failed: {str(e)}")

@router.post("/analyze-phi")
async def analyze_with_phi(
    symbol: str,
    market_data: Dict[str, Any],
    image_file: Optional[UploadFile] = File(None)
):
    """Analyze using phi-4 specifically"""
    try:
        logger.info(f"Starting phi-4 analysis for {symbol}")
        
        # Get image data if provided
        image_data = None
        if image_file:
            image_data = await image_file.read()
        
        # Create analysis request
        request = AnalysisRequest(
            symbol=symbol,
            image_data=image_data,
            market_data=market_data,
            analysis_type="liquidation_analysis",
            context="KingFisher liquidation map analysis"
        )
        
        # Perform phi-4 analysis
        result = await local_ai_service._analyze_with_phi(request)
        
        return {
            "status": "success",
            "symbol": symbol,
            "model": "phi-4",
            "analysis": result.analysis,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "recommendations": result.recommendations,
            "risk_score": result.risk_score,
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in phi-4 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Phi-4 analysis failed: {str(e)}")

@router.post("/test-connection")
async def test_model_connections():
    """Test connections to all local models"""
    try:
        logger.info("Testing local model connections")
        
        # Test deepseek connection
        deepseek_status = "unavailable"
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                deepseek_available = any("deepseek" in model.get("name", "").lower() for model in models)
                deepseek_status = "available" if deepseek_available else "not_found"
            else:
                deepseek_status = "server_unreachable"
        except Exception as e:
            deepseek_status = f"error: {str(e)}"
        
        # Test phi-4 connection
        phi_status = "unavailable"
        try:
            response = requests.get("http://localhost:11435/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                phi_available = any("phi" in model.get("name", "").lower() for model in models)
                phi_status = "available" if phi_available else "not_found"
            else:
                phi_status = "server_unreachable"
        except Exception as e:
            phi_status = f"error: {str(e)}"
        
        return {
            "status": "success",
            "connections": {
                "deepseek-r1-distill-llama": {
                    "status": deepseek_status,
                    "endpoint": "http://localhost:11434/api/generate"
                },
                "phi-4": {
                    "status": phi_status,
                    "endpoint": "http://localhost:11435/api/generate"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing model connections: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.get("/capabilities")
async def get_model_capabilities():
    """Get capabilities of all local models"""
    try:
        capabilities = {
            "deepseek-r1-distill-llama": {
                "model_type": "reasoning",
                "capabilities": [
                    "strategy_simulation",
                    "trade_analysis", 
                    "chain_of_thought",
                    "liquidation_analysis",
                    "risk_assessment",
                    "trading_recommendations"
                ],
                "description": "Fast, optimized model for reasoning, code, and structured logic. Ideal for strategy simulation and analysis.",
                "endpoint": "http://localhost:11434/api/generate"
            },
            "phi-4": {
                "model_type": "reasoning",
                "capabilities": [
                    "scoring_systems",
                    "trade_logic",
                    "indicators",
                    "math",
                    "quantitative_analysis",
                    "mathematical_reasoning"
                ],
                "description": "Microsoft's compact but strong reasoning model. Excellent at code, math, and logic for scoring systems and trade logic.",
                "endpoint": "http://localhost:11435/api/generate"
            }
        }
        
        return {
            "status": "success",
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@router.post("/initialize")
async def initialize_models():
    """Initialize local AI models service"""
    try:
        logger.info("Initializing local AI models service")
        
        success = await local_ai_service.initialize()
        
        return {
            "status": "success" if success else "failed",
            "initialized": success,
            "message": "Local AI models service initialized successfully" if success else "Failed to initialize local AI models service",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}") 