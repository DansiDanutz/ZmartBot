#!/usr/bin/env python3
"""
Multi-Model AI Analysis API Routes
Provides endpoints for analysis using OpenAI, DeepSeek, and Phi models
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..services.multi_model_ai_agent import MultiModelAIAgent, ModelType
from ..routes.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/multi-model-analysis", tags=["multi-model-analysis"])

# Initialize Multi-Model AI Agent
try:
    multi_model_agent = MultiModelAIAgent()
    logger.info("Multi-Model AI Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Multi-Model AI Agent: {e}")
    multi_model_agent = None

@router.get("/analyze/{symbol}")
async def analyze_with_multi_models(
    symbol: str,
    use_all_models: bool = Query(False, description="Use all available models for comparison"),
    preferred_model: Optional[str] = Query(None, description="Preferred model (gpt-4o-mini, deepseek-coder, etc.)"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate comprehensive analysis using multiple AI models
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        use_all_models: Whether to use all available models
        preferred_model: Preferred model to prioritize
        current_user: Authenticated user
    
    Returns:
        Multi-model analysis with fallback capabilities
    """
    if not multi_model_agent:
        raise HTTPException(
            status_code=503,
            detail="Multi-Model AI Agent not available"
        )
    
    try:
        logger.info(f"Generating multi-model analysis for {symbol}")
        
        # Adjust model priority if preferred model specified
        if preferred_model:
            try:
                preferred_model_type = ModelType(preferred_model)
                if multi_model_agent.model_status.get(preferred_model_type, False):
                    # Move preferred model to front of priority list
                    priority_list = [preferred_model_type] + [
                        m for m in multi_model_agent.model_priority 
                        if m != preferred_model_type
                    ]
                    multi_model_agent.model_priority = priority_list
                    logger.info(f"Prioritized {preferred_model} for analysis")
            except ValueError:
                logger.warning(f"Invalid preferred model: {preferred_model}")
        
        # Generate analysis
        analysis = await multi_model_agent.generate_comprehensive_analysis(
            symbol.upper(), 
            use_all_models=use_all_models
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "metadata": {
                "request_time": datetime.now().isoformat(),
                "user": current_user.get('username', 'unknown'),
                "models_requested": "all" if use_all_models else "best_available",
                "preferred_model": preferred_model,
                "fallback_active": not multi_model_agent.model_status.get(ModelType.OPENAI_GPT4_MINI, False)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in multi-model analysis for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate multi-model analysis: {str(e)}"
        )

@router.get("/compare-models/{symbol}")
async def compare_all_models(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compare analysis from all available models
    
    Args:
        symbol: Trading symbol
        current_user: Authenticated user
    
    Returns:
        Side-by-side comparison of all model analyses
    """
    if not multi_model_agent:
        raise HTTPException(
            status_code=503,
            detail="Multi-Model AI Agent not available"
        )
    
    try:
        logger.info(f"Generating model comparison for {symbol}")
        
        # Force use of all models
        analysis = await multi_model_agent.generate_comprehensive_analysis(
            symbol.upper(), 
            use_all_models=True
        )
        
        # Extract model comparisons
        model_comparisons = analysis.get('model_comparisons', [])
        successful_models = [m for m in model_comparisons if m['success']]
        failed_models = [m for m in model_comparisons if not m['success']]
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "comparison_results": {
                "successful_models": len(successful_models),
                "failed_models": len(failed_models),
                "total_models_tested": len(model_comparisons),
                "best_model": analysis['multi_model_analysis']['primary_model'],
                "aggregate_confidence": analysis['multi_model_analysis']['aggregate_confidence']
            },
            "detailed_comparisons": model_comparisons,
            "consensus_analysis": {
                "primary_analysis": analysis['multi_model_analysis']['primary_analysis'],
                "technical_data": analysis['technical_data'],
                "confidence_level": analysis['multi_model_analysis']['aggregate_confidence']
            },
            "performance_metrics": {
                "total_processing_time": analysis['multi_model_analysis']['total_processing_time'],
                "average_processing_time": analysis['multi_model_analysis']['total_processing_time'] / len(successful_models) if successful_models else 0,
                "fastest_model": min(successful_models, key=lambda x: x['processing_time'])['model'] if successful_models else None,
                "most_confident_model": max(successful_models, key=lambda x: x['confidence'])['model'] if successful_models else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error in model comparison for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare models: {str(e)}"
        )

@router.get("/model-status")
async def get_model_status(
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get status and availability of all AI models
    
    Returns:
        Comprehensive model status and capabilities
    """
    if not multi_model_agent:
        raise HTTPException(
            status_code=503,
            detail="Multi-Model AI Agent not available"
        )
    
    try:
        status = multi_model_agent.get_model_status()
        
        return {
            "success": True,
            "model_status": status,
            "recommendations": {
                "primary_model": status['recommended_order'][0] if status['recommended_order'] else None,
                "fallback_available": status['available_models'] > 1,
                "local_models_count": sum(
                    1 for model_info in status['model_details'].values() 
                    if model_info['available'] and model_info['type'] == 'local'
                ),
                "cloud_models_count": sum(
                    1 for model_info in status['model_details'].values() 
                    if model_info['available'] and model_info['type'] == 'cloud'
                )
            },
            "setup_instructions": {
                "local_models": status['local_models_setup'],
                "requirements": [
                    "Install Ollama for local models",
                    "Configure OpenAI API key for cloud models",
                    "Ensure sufficient system resources for local models"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model status: {str(e)}"
        )

@router.get("/local-models/install")
async def get_local_model_installation(
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get installation instructions for local models
    
    Returns:
        Step-by-step installation guide
    """
    return {
        "success": True,
        "installation_guide": {
            "step_1_ollama": {
                "description": "Install Ollama (local model runtime)",
                "command": "curl -fsSL https://ollama.ai/install.sh | sh",
                "alternative": "Download from https://ollama.ai/download"
            },
            "step_2_models": {
                "description": "Install recommended models",
                "commands": {
                    "deepseek_coder": "ollama pull deepseek-coder",
                    "deepseek_r1": "ollama pull deepseek-r1-distill-llama", 
                    "phi3": "ollama pull phi3",
                    "phi4": "ollama pull phi4"
                }
            },
            "step_3_verify": {
                "description": "Verify installation",
                "command": "ollama list",
                "expected_output": "List of installed models"
            },
            "step_4_test": {
                "description": "Test model functionality",
                "endpoint": "/api/v1/multi-model-analysis/model-status",
                "expected": "All local models should show as available"
            }
        },
        "model_recommendations": {
            "for_trading_analysis": "deepseek-r1-distill-llama (best reasoning)",
            "for_structured_data": "deepseek-coder (best for technical analysis)",
            "for_quick_insights": "phi4 (most compact and fast)",
            "for_comprehensive_reports": "gpt-4o-mini (cloud, best language)"
        },
        "system_requirements": {
            "minimum_ram": "8GB (for Phi-3/4)",
            "recommended_ram": "16GB (for DeepSeek models)",
            "disk_space": "5-10GB per model",
            "cpu": "Modern multi-core processor recommended"
        }
    }

@router.post("/analyze-with-model")
async def analyze_with_specific_model(
    request_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Analyze using a specific model with custom parameters
    
    Args:
        request_data: Analysis request with symbol, model, and parameters
        current_user: Authenticated user
    
    Returns:
        Analysis from specified model
    """
    if not multi_model_agent:
        raise HTTPException(
            status_code=503,
            detail="Multi-Model AI Agent not available"
        )
    
    symbol = request_data.get('symbol')
    model_type = request_data.get('model_type')
    parameters = request_data.get('parameters', {})
    
    if not symbol or not model_type:
        raise HTTPException(
            status_code=400,
            detail="Symbol and model_type are required"
        )
    
    try:
        # Validate model type
        try:
            model_enum = ModelType(model_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type: {model_type}"
            )
        
        # Check if model is available
        if not multi_model_agent.model_status.get(model_enum, False):
            raise HTTPException(
                status_code=400,
                detail=f"Model {model_type} is not available"
            )
        
        # Set model as priority
        multi_model_agent.model_priority = [model_enum]
        
        # Generate analysis
        analysis = await multi_model_agent.generate_comprehensive_analysis(
            symbol.upper(), 
            use_all_models=False
        )
        
        return {
            "success": True,
            "requested_model": model_type,
            "analysis": analysis,
            "parameters_used": parameters,
            "metadata": {
                "model_specific_analysis": True,
                "processing_time": analysis['multi_model_analysis']['total_processing_time'],
                "confidence": analysis['multi_model_analysis']['aggregate_confidence']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in specific model analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze with {model_type}: {str(e)}"
        )

@router.get("/status")
async def get_multi_model_status() -> Dict[str, Any]:
    """
    Get Multi-Model Analysis system status
    
    Returns:
        System status and capabilities
    """
    return {
        "success": True,
        "system_status": "available" if multi_model_agent else "unavailable",
        "capabilities": {
            "multi_model_analysis": multi_model_agent is not None,
            "model_comparison": multi_model_agent is not None,
            "fallback_support": multi_model_agent is not None,
            "local_model_support": True,
            "cloud_model_support": True
        },
        "supported_models": {
            "cloud": ["gpt-4o-mini"],
            "local": ["deepseek-coder", "deepseek-r1-distill-llama", "phi3", "phi4"]
        },
        "endpoints": {
            "analyze": "/multi-model-analysis/analyze/{symbol}",
            "compare": "/multi-model-analysis/compare-models/{symbol}",
            "model_status": "/multi-model-analysis/model-status",
            "install_guide": "/multi-model-analysis/local-models/install",
            "specific_model": "/multi-model-analysis/analyze-with-model",
            "system_status": "/multi-model-analysis/status"
        },
        "features": {
            "automatic_fallback": "Automatically uses best available model",
            "model_comparison": "Compare results from multiple models",
            "local_execution": "Run models locally for privacy and reliability",
            "structured_analysis": "Optimized for trading data analysis",
            "performance_tracking": "Track model performance and speed"
        }
    }