#!/usr/bin/env python3
"""
Local AI Models Service
Integrates local models for enhanced KingFisher analysis
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import subprocess
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for local AI models"""
    name: str
    endpoint: str
    max_tokens: int
    temperature: float
    model_type: str
    capabilities: List[str]

@dataclass
class AnalysisRequest:
    """Request for AI model analysis"""
    symbol: str
    image_data: Optional[bytes]
    market_data: Dict[str, Any]
    analysis_type: str
    context: str

@dataclass
class AnalysisResponse:
    """Response from AI model analysis"""
    model_name: str
    analysis: str
    confidence: float
    reasoning: str
    recommendations: List[str]
    risk_score: float
    timestamp: datetime

class LocalAIModelsService:
    """Service for local AI models integration"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = {
            "deepseek-r1-distill-llama": ModelConfig(
                name="deepseek-r1-distill-llama",
                endpoint="http://localhost:11434/api/generate",
                max_tokens=2048,
                temperature=0.7,
                model_type="reasoning",
                capabilities=["strategy_simulation", "trade_analysis", "chain_of_thought"]
            ),
            "phi-4": ModelConfig(
                name="phi-4",
                endpoint="http://localhost:11435/api/generate",
                max_tokens=1024,
                temperature=0.5,
                model_type="reasoning",
                capabilities=["scoring_systems", "trade_logic", "indicators", "math"]
            )
        }
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize local AI models service"""
        try:
            logger.info("Initializing Local AI Models Service...")
            
            # Check if models are available
            await self._check_model_availability()
            
            # Initialize model connections
            await self._initialize_models()
            
            self.initialized = True
            logger.info("✅ Local AI Models Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Local AI Models Service: {e}")
            return False
    
    async def _check_model_availability(self):
        """Check if local models are available"""
        logger.info("Checking local model availability...")
        
        # Check deepseek-r1-distill-llama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                deepseek_available = any("deepseek" in model.get("name", "").lower() for model in models)
                if deepseek_available:
                    logger.info("✅ deepseek-r1-distill-llama is available")
                else:
                    logger.warning("⚠️ deepseek-r1-distill-llama not found in Ollama")
            else:
                logger.warning("⚠️ Ollama server not responding on port 11434")
        except Exception as e:
            logger.warning(f"⚠️ Could not check deepseek model: {e}")
        
        # Check phi-4
        try:
            response = requests.get("http://localhost:11435/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                phi_available = any("phi" in model.get("name", "").lower() for model in models)
                if phi_available:
                    logger.info("✅ phi-4 is available")
                else:
                    logger.warning("⚠️ phi-4 not found in Ollama")
            else:
                logger.warning("⚠️ Ollama server not responding on port 11435")
        except Exception as e:
            logger.warning(f"⚠️ Could not check phi-4 model: {e}")
    
    async def _initialize_models(self):
        """Initialize model connections"""
        for model_name, config in self.model_configs.items():
            try:
                # Test model connection
                test_response = await self._test_model_connection(config)
                if test_response:
                    self.models[model_name] = config
                    logger.info(f"✅ {model_name} initialized successfully")
                else:
                    logger.warning(f"⚠️ {model_name} not available")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize {model_name}: {e}")
    
    async def _test_model_connection(self, config: ModelConfig) -> bool:
        """Test connection to a specific model"""
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'OK' if you can see this."
            
            payload = {
                "model": config.name,
                "prompt": test_prompt,
                "stream": False,
                "options": {
                    "temperature": config.temperature,
                    "num_predict": 10
                }
            }
            
            response = requests.post(config.endpoint, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Model connection test failed for {config.name}: {e}")
            return False
    
    async def analyze_liquidation_data(self, symbol: str, image_data: bytes, market_data: Dict[str, Any]) -> Dict[str, AnalysisResponse]:
        """Analyze liquidation data using local AI models"""
        try:
            logger.info(f"Starting AI analysis for {symbol}")
            
            # Prepare analysis request
            request = AnalysisRequest(
                symbol=symbol,
                image_data=image_data,
                market_data=market_data,
                analysis_type="liquidation_analysis",
                context="KingFisher liquidation map analysis"
            )
            
            results = {}
            
            # Analyze with deepseek-r1-distill-llama
            if "deepseek-r1-distill-llama" in self.models:
                deepseek_result = await self._analyze_with_deepseek(request)
                results["deepseek"] = deepseek_result
            
            # Analyze with phi-4
            if "phi-4" in self.models:
                phi_result = await self._analyze_with_phi(request)
                results["phi-4"] = phi_result
            
            logger.info(f"✅ AI analysis completed for {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed for {symbol}: {e}")
            return {}
    
    async def _analyze_with_deepseek(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze using deepseek-r1-distill-llama"""
        try:
            # Prepare prompt for liquidation analysis
            prompt = self._build_deepseek_prompt(request)
            
            payload = {
                "model": "deepseek-r1-distill-llama",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2048,
                    "top_k": 40,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get("response", "")
                
                # Parse analysis results
                parsed_result = self._parse_deepseek_analysis(analysis_text)
                
                return AnalysisResponse(
                    model_name="deepseek-r1-distill-llama",
                    analysis=parsed_result.get("analysis", ""),
                    confidence=parsed_result.get("confidence", 0.0),
                    reasoning=parsed_result.get("reasoning", ""),
                    recommendations=parsed_result.get("recommendations", []),
                    risk_score=parsed_result.get("risk_score", 0.0),
                    timestamp=datetime.now()
                )
            else:
                logger.error(f"Deepseek API error: {response.status_code}")
                return self._create_error_response("deepseek-r1-distill-llama")
                
        except Exception as e:
            logger.error(f"Deepseek analysis error: {e}")
            return self._create_error_response("deepseek-r1-distill-llama")
    
    async def _analyze_with_phi(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze using phi-4"""
        try:
            # Prepare prompt for scoring and logic analysis
            prompt = self._build_phi_prompt(request)
            
            payload = {
                "model": "phi-4",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 1024,
                    "top_k": 30,
                    "top_p": 0.8
                }
            }
            
            response = requests.post(
                "http://localhost:11435/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get("response", "")
                
                # Parse analysis results
                parsed_result = self._parse_phi_analysis(analysis_text)
                
                return AnalysisResponse(
                    model_name="phi-4",
                    analysis=parsed_result.get("analysis", ""),
                    confidence=parsed_result.get("confidence", 0.0),
                    reasoning=parsed_result.get("reasoning", ""),
                    recommendations=parsed_result.get("recommendations", []),
                    risk_score=parsed_result.get("risk_score", 0.0),
                    timestamp=datetime.now()
                )
            else:
                logger.error(f"Phi-4 API error: {response.status_code}")
                return self._create_error_response("phi-4")
                
        except Exception as e:
            logger.error(f"Phi-4 analysis error: {e}")
            return self._create_error_response("phi-4")
    
    def _build_deepseek_prompt(self, request: AnalysisRequest) -> str:
        """Build prompt for deepseek-r1-distill-llama"""
        market_info = request.market_data
        
        prompt = f"""
You are an expert cryptocurrency trading analyst specializing in liquidation analysis. Analyze the following KingFisher liquidation data for {request.symbol}:

MARKET DATA:
- Symbol: {request.symbol}
- Current Price: {market_info.get('price', 'N/A')}
- 24h Volume: {market_info.get('volume_24h', 'N/A')}
- Market Cap: {market_info.get('market_cap', 'N/A')}
- Volatility: {market_info.get('volatility', 'N/A')}

ANALYSIS TASK:
Analyze the liquidation map image and provide:
1. Liquidation cluster analysis
2. Risk assessment
3. Trading recommendations
4. Chain-of-thought reasoning
5. Confidence score (0-100)

Please provide a structured analysis with clear reasoning and actionable insights.
"""
        return prompt
    
    def _build_phi_prompt(self, request: AnalysisRequest) -> str:
        """Build prompt for phi-4"""
        market_info = request.market_data
        
        prompt = f"""
You are a quantitative trading analyst. Analyze {request.symbol} liquidation data for scoring and logic:

MARKET DATA:
- Symbol: {request.symbol}
- Price: {market_info.get('price', 'N/A')}
- Volume: {market_info.get('volume_24h', 'N/A')}
- Market Cap: {market_info.get('market_cap', 'N/A')}

TASK:
1. Calculate risk score (0-100)
2. Analyze liquidation patterns
3. Provide mathematical scoring
4. Generate trade logic
5. Identify key indicators

Focus on quantitative analysis and mathematical reasoning.
"""
        return prompt
    
    def _parse_deepseek_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse deepseek analysis response"""
        try:
            # Extract key components from analysis
            analysis = analysis_text
            confidence = 0.0
            reasoning = ""
            recommendations = []
            risk_score = 0.0
            
            # Try to extract structured data
            if "confidence:" in analysis_text.lower():
                confidence_match = analysis_text.lower().split("confidence:")[1].split("\n")[0]
                try:
                    confidence = float(confidence_match.strip().replace("%", "")) / 100
                except:
                    confidence = 0.7
            
            if "risk score:" in analysis_text.lower():
                risk_match = analysis_text.lower().split("risk score:")[1].split("\n")[0]
                try:
                    risk_score = float(risk_match.strip().replace("%", "")) / 100
                except:
                    risk_score = 0.5
            
            # Extract recommendations
            if "recommendations:" in analysis_text.lower():
                recs_section = analysis_text.lower().split("recommendations:")[1]
                recs_lines = recs_section.split("\n")[:5]  # First 5 lines
                recommendations = [line.strip("- ").strip() for line in recs_lines if line.strip().startswith("-")]
            
            return {
                "analysis": analysis,
                "confidence": confidence,
                "reasoning": reasoning,
                "recommendations": recommendations,
                "risk_score": risk_score
            }
            
        except Exception as e:
            logger.error(f"Error parsing deepseek analysis: {e}")
            return {
                "analysis": analysis_text,
                "confidence": 0.7,
                "reasoning": "Analysis completed",
                "recommendations": ["Review liquidation patterns carefully"],
                "risk_score": 0.5
            }
    
    def _parse_phi_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse phi-4 analysis response"""
        try:
            # Extract key components from analysis
            analysis = analysis_text
            confidence = 0.0
            reasoning = ""
            recommendations = []
            risk_score = 0.0
            
            # Try to extract numerical scores
            if "risk score:" in analysis_text.lower():
                risk_match = analysis_text.lower().split("risk score:")[1].split("\n")[0]
                try:
                    risk_score = float(risk_match.strip().replace("%", "")) / 100
                except:
                    risk_score = 0.5
            
            if "confidence:" in analysis_text.lower():
                conf_match = analysis_text.lower().split("confidence:")[1].split("\n")[0]
                try:
                    confidence = float(conf_match.strip().replace("%", "")) / 100
                except:
                    confidence = 0.8
            
            # Extract mathematical indicators
            if "indicators:" in analysis_text.lower():
                indicators_section = analysis_text.lower().split("indicators:")[1]
                indicators_lines = indicators_section.split("\n")[:3]
                recommendations = [line.strip("- ").strip() for line in indicators_lines if line.strip().startswith("-")]
            
            return {
                "analysis": analysis,
                "confidence": confidence,
                "reasoning": reasoning,
                "recommendations": recommendations,
                "risk_score": risk_score
            }
            
        except Exception as e:
            logger.error(f"Error parsing phi-4 analysis: {e}")
            return {
                "analysis": analysis_text,
                "confidence": 0.8,
                "reasoning": "Quantitative analysis completed",
                "recommendations": ["Monitor key indicators"],
                "risk_score": 0.5
            }
    
    def _create_error_response(self, model_name: str) -> AnalysisResponse:
        """Create error response when model analysis fails"""
        return AnalysisResponse(
            model_name=model_name,
            analysis="Analysis failed - model unavailable",
            confidence=0.0,
            reasoning="Model connection failed",
            recommendations=["Check model availability"],
            risk_score=0.5,
            timestamp=datetime.now()
        )
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all local models"""
        status = {
            "service_initialized": self.initialized,
            "models": {}
        }
        
        for model_name, config in self.model_configs.items():
            try:
                available = model_name in self.models
                status["models"][model_name] = {
                    "available": available,
                    "endpoint": config.endpoint,
                    "capabilities": config.capabilities,
                    "model_type": config.model_type
                }
            except Exception as e:
                status["models"][model_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return status
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.initialized and len(self.models) > 0 