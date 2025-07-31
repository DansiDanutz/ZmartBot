#!/usr/bin/env python3
"""
Multi-Model AI Analysis Agent
Integrates OpenAI, DeepSeek-Coder, and Phi-3/Phi-4 for comprehensive trading analysis
"""

import logging
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import requests
import subprocess
import tempfile
import os

from src.config.settings import settings
from src.services.historical_ai_analysis_agent import HistoricalAIAnalysisAgent
from src.services.cryptometer_endpoint_analyzer import CryptometerAnalysis

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Available AI models"""
    OPENAI_GPT4_MINI = "gpt-4o-mini"
    DEEPSEEK_CODER = "deepseek-coder"
    DEEPSEEK_R1_DISTILL = "deepseek-r1-distill-llama"
    PHI_3 = "phi-3"
    PHI_4 = "phi-4"

@dataclass
class ModelResponse:
    """Response from any AI model"""
    model_type: ModelType
    content: str
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class TradingPattern:
    """Structured trading pattern for local models"""
    symbol: str
    timeframe: str
    price_data: List[float]
    volume_data: List[float]
    rsi_values: List[float]
    ma_values: Dict[str, List[float]]
    liquidation_levels: Dict[str, float]
    support_resistance: Dict[str, List[float]]
    trend_direction: str
    volatility: float
    momentum_score: float

class MultiModelAIAgent:
    """
    Multi-Model AI Agent supporting OpenAI, DeepSeek, and Phi models
    """
    
    def __init__(self):
        """Initialize Multi-Model AI Agent"""
        self.historical_ai_agent = HistoricalAIAnalysisAgent()
        
        # Model availability status
        self.model_status = {
            ModelType.OPENAI_GPT4_MINI: self._check_openai_availability(),
            ModelType.DEEPSEEK_CODER: self._check_deepseek_availability(),
            ModelType.DEEPSEEK_R1_DISTILL: self._check_deepseek_r1_availability(),
            ModelType.PHI_3: self._check_phi3_availability(),
            ModelType.PHI_4: self._check_phi4_availability()
        }
        
        # Model priorities (fallback order)
        self.model_priority = [
            ModelType.OPENAI_GPT4_MINI,
            ModelType.DEEPSEEK_R1_DISTILL,
            ModelType.DEEPSEEK_CODER,
            ModelType.PHI_4,
            ModelType.PHI_3
        ]
        
        logger.info(f"Multi-Model AI Agent initialized with {sum(self.model_status.values())} available models")
    
    def _check_openai_availability(self) -> bool:
        """Check if OpenAI is available"""
        return bool(settings.OPENAI_API_KEY)
    
    def _check_deepseek_availability(self) -> bool:
        """Check if DeepSeek-Coder is available locally"""
        try:
            # Check if ollama is installed and has deepseek-coder
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return 'deepseek-coder' in result.stdout
        except:
            return False
    
    def _check_deepseek_r1_availability(self) -> bool:
        """Check if DeepSeek-R1 is available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return 'deepseek-r1' in result.stdout
        except:
            return False
    
    def _check_phi3_availability(self) -> bool:
        """Check if Phi-3 is available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return 'phi3' in result.stdout
        except:
            return False
    
    def _check_phi4_availability(self) -> bool:
        """Check if Phi-4 (or Phi-3 14B alternative) is available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return 'phi3:14b' in result.stdout
        except:
            return False
    
    async def generate_comprehensive_analysis(self, symbol: str, use_all_models: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive analysis using multiple AI models
        
        Args:
            symbol: Trading symbol
            use_all_models: Whether to use all available models for comparison
            
        Returns:
            Comprehensive analysis with multiple model perspectives
        """
        logger.info(f"Generating multi-model analysis for {symbol}")
        
        # Get base data
        try:
            cryptometer_analysis = await self.historical_ai_agent.cryptometer_analyzer.analyze_symbol_complete(symbol)
        except Exception as e:
            logger.warning(f"Cryptometer analysis failed: {e}, using fallback data")
            cryptometer_analysis = self._create_fallback_analysis(symbol)
        
        # Prepare structured data for local models
        trading_pattern = self._prepare_trading_pattern(symbol, cryptometer_analysis)
        
        # Generate analyses
        model_responses = {}
        
        if use_all_models:
            # Use all available models
            for model_type in self.model_priority:
                if self.model_status[model_type]:
                    try:
                        response = await self._generate_model_analysis(model_type, symbol, trading_pattern, cryptometer_analysis)
                        model_responses[model_type.value] = response
                    except Exception as e:
                        logger.error(f"Error with {model_type.value}: {e}")
        else:
            # Use best available model
            for model_type in self.model_priority:
                if self.model_status[model_type]:
                    try:
                        response = await self._generate_model_analysis(model_type, symbol, trading_pattern, cryptometer_analysis)
                        model_responses[model_type.value] = response
                        break  # Use first successful model
                    except Exception as e:
                        logger.error(f"Error with {model_type.value}: {e}")
                        continue
        
        # Aggregate results
        final_analysis = self._aggregate_model_responses(symbol, model_responses, trading_pattern)
        
        return final_analysis
    
    async def _generate_model_analysis(self, model_type: ModelType, symbol: str, 
                                     trading_pattern: TradingPattern, 
                                     cryptometer_analysis: CryptometerAnalysis) -> ModelResponse:
        """Generate analysis using specific model"""
        start_time = datetime.now()
        
        try:
            if model_type == ModelType.OPENAI_GPT4_MINI:
                content = await self._generate_openai_analysis(symbol, trading_pattern, cryptometer_analysis)
                confidence = 0.85
            
            elif model_type in [ModelType.DEEPSEEK_CODER, ModelType.DEEPSEEK_R1_DISTILL]:
                content = await self._generate_deepseek_analysis(model_type, symbol, trading_pattern)
                confidence = 0.80
            
            elif model_type in [ModelType.PHI_3, ModelType.PHI_4]:
                content = await self._generate_phi_analysis(model_type, symbol, trading_pattern)
                confidence = 0.75
            
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ModelResponse(
                model_type=model_type,
                content=content,
                confidence=confidence,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return ModelResponse(
                model_type=model_type,
                content="",
                confidence=0.0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _generate_openai_analysis(self, symbol: str, trading_pattern: TradingPattern, 
                                      cryptometer_analysis: CryptometerAnalysis) -> str:
        """Generate analysis using OpenAI"""
        # Use existing historical AI agent
        result = await self.historical_ai_agent.generate_historical_enhanced_report(symbol, store_prediction=False)
        return result['report_content']
    
    async def _generate_deepseek_analysis(self, model_type: ModelType, symbol: str, 
                                        trading_pattern: TradingPattern) -> str:
        """Generate analysis using DeepSeek models"""
        
        model_name = "deepseek-coder" if model_type == ModelType.DEEPSEEK_CODER else "deepseek-r1"
        
        # Prepare structured prompt for DeepSeek
        structured_data = {
            "symbol": trading_pattern.symbol,
            "timeframe": trading_pattern.timeframe,
            "technical_indicators": {
                "rsi_current": trading_pattern.rsi_values[-1] if trading_pattern.rsi_values else 50,
                "rsi_trend": "bullish" if len(trading_pattern.rsi_values) > 1 and trading_pattern.rsi_values[-1] > trading_pattern.rsi_values[-2] else "bearish",
                "ma_20": trading_pattern.ma_values.get("20", [0])[-1] if trading_pattern.ma_values.get("20") else 0,
                "ma_50": trading_pattern.ma_values.get("50", [0])[-1] if trading_pattern.ma_values.get("50") else 0,
                "price_vs_ma20": "above" if trading_pattern.price_data[-1] > trading_pattern.ma_values.get("20", [0])[-1] else "below",
                "volatility": trading_pattern.volatility,
                "momentum": trading_pattern.momentum_score
            },
            "liquidation_analysis": trading_pattern.liquidation_levels,
            "support_resistance": trading_pattern.support_resistance,
            "trend_direction": trading_pattern.trend_direction
        }
        
        prompt = f"""Analyze the following cryptocurrency trading data for {symbol}:

STRUCTURED DATA:
{json.dumps(structured_data, indent=2)}

PRICE DATA (last 20 points):
{trading_pattern.price_data[-20:] if len(trading_pattern.price_data) > 20 else trading_pattern.price_data}

VOLUME DATA (last 20 points):
{trading_pattern.volume_data[-20:] if len(trading_pattern.volume_data) > 20 else trading_pattern.volume_data}

Please provide:
1. Technical Analysis Summary
2. Trend Direction Assessment
3. Support/Resistance Levels
4. Risk Assessment
5. Trading Recommendation with Entry/Exit points
6. Confidence Level (0-100%)

Focus on logical, data-driven analysis based on the technical indicators provided."""

        # Execute DeepSeek analysis
        result = await self._execute_ollama_model(model_name, prompt)
        return result
    
    async def _generate_phi_analysis(self, model_type: ModelType, symbol: str, 
                                   trading_pattern: TradingPattern) -> str:
        """Generate analysis using Phi models"""
        
        model_name = "phi3:3.8b" if model_type == ModelType.PHI_3 else "phi3:14b"
        
        # Prepare concise prompt for Phi (optimized for compact models)
        prompt = f"""Trading Analysis for {symbol}:

Current Price: {trading_pattern.price_data[-1] if trading_pattern.price_data else 'N/A'}
RSI: {trading_pattern.rsi_values[-1] if trading_pattern.rsi_values else 'N/A'}
Trend: {trading_pattern.trend_direction}
Volatility: {trading_pattern.volatility:.2f}
Momentum: {trading_pattern.momentum_score:.2f}

Price History (last 10): {trading_pattern.price_data[-10:] if len(trading_pattern.price_data) > 10 else trading_pattern.price_data}

Liquidation Levels: {json.dumps(trading_pattern.liquidation_levels)}

Provide concise analysis:
1. Market Direction (BULLISH/BEARISH/NEUTRAL)
2. Key Levels (Support/Resistance)
3. Risk Level (LOW/MEDIUM/HIGH)
4. Trading Action (BUY/SELL/HOLD)
5. Confidence (0-100%)

Keep response under 500 words, focus on actionable insights."""

        # Execute Phi analysis
        result = await self._execute_ollama_model(model_name, prompt)
        return result
    
    async def _execute_ollama_model(self, model_name: str, prompt: str) -> str:
        """Execute local model via Ollama"""
        try:
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            # Execute ollama command
            cmd = ['ollama', 'run', model_name]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send prompt and get response
            stdout, stderr = process.communicate(input=prompt, timeout=60)
            
            # Clean up
            os.unlink(temp_file)
            
            if process.returncode == 0:
                return stdout.strip()
            else:
                raise Exception(f"Ollama error: {stderr}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("Model execution timeout")
        except Exception as e:
            raise Exception(f"Local model execution error: {e}")
    
    def _prepare_trading_pattern(self, symbol: str, cryptometer_analysis: CryptometerAnalysis) -> TradingPattern:
        """Prepare structured trading pattern data"""
        
        # Extract available data from cryptometer analysis
        price_data = []
        volume_data = []
        rsi_values = []
        
        # Generate synthetic data based on analysis (in production, use real historical data)
        base_price = 3000.0  # ETH example
        for i in range(50):
            price_variation = np.random.normal(0, base_price * 0.02)
            price_data.append(base_price + price_variation)
            volume_data.append(np.random.uniform(1000000, 5000000))
            rsi_values.append(np.random.uniform(30, 70))
        
        # Calculate moving averages
        ma_values = {
            "20": [float(np.mean(price_data[max(0, i-19):i+1])) for i in range(len(price_data))],
            "50": [float(np.mean(price_data[max(0, i-49):i+1])) for i in range(len(price_data))]
        }
        
        # Calculate support/resistance
        recent_prices = price_data[-20:]
        support_resistance = {
            "support": [min(recent_prices), float(np.percentile(recent_prices, 25))],
            "resistance": [float(np.percentile(recent_prices, 75)), max(recent_prices)]
        }
        
        # Liquidation levels (example)
        current_price = price_data[-1]
        liquidation_levels = {
            "long_liquidation": current_price * 0.85,
            "short_liquidation": current_price * 1.15,
            "major_support": current_price * 0.90,
            "major_resistance": current_price * 1.10
        }
        
        return TradingPattern(
            symbol=symbol,
            timeframe="1h",
            price_data=price_data,
            volume_data=volume_data,
            rsi_values=rsi_values,
            ma_values=ma_values,
            liquidation_levels=liquidation_levels,
            support_resistance=support_resistance,
            trend_direction=cryptometer_analysis.direction if hasattr(cryptometer_analysis, 'direction') else "NEUTRAL",
            volatility=float(np.std(price_data[-20:]) / np.mean(price_data[-20:])),
            momentum_score=cryptometer_analysis.calibrated_score / 100.0 if hasattr(cryptometer_analysis, 'calibrated_score') else 0.5
        )
    
    def _create_fallback_analysis(self, symbol: str) -> CryptometerAnalysis:
        """Create fallback analysis when Cryptometer fails"""
        from src.services.cryptometer_endpoint_analyzer import CryptometerAnalysis, EndpointScore
        from datetime import datetime
        
        return CryptometerAnalysis(
            symbol=symbol,
            endpoint_scores=[
                EndpointScore(
                    endpoint="fallback",
                    raw_data={"status": "fallback"},
                    score=50.0,
                    confidence=0.5,
                    patterns=["fallback_pattern"],
                    analysis="Fallback analysis due to API issues",
                    success=True
                )
            ],
            calibrated_score=50.0,
            confidence=0.5,
            direction="NEUTRAL",
            analysis_summary="Fallback analysis due to API issues",
            timestamp=datetime.now()
        )
    
    def _aggregate_model_responses(self, symbol: str, model_responses: Dict[str, ModelResponse], 
                                 trading_pattern: TradingPattern) -> Dict[str, Any]:
        """Aggregate responses from multiple models"""
        
        successful_responses = [r for r in model_responses.values() if r.success]
        
        if not successful_responses:
            return {
                "symbol": symbol,
                "error": "No models available for analysis",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate aggregate confidence
        avg_confidence = np.mean([r.confidence for r in successful_responses])
        
        # Get best response (highest confidence)
        best_response = max(successful_responses, key=lambda x: x.confidence)
        
        # Create comprehensive analysis
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "multi_model_analysis": {
                "primary_model": best_response.model_type.value,
                "primary_analysis": best_response.content,
                "aggregate_confidence": avg_confidence,
                "models_used": len(successful_responses),
                "total_processing_time": sum(r.processing_time for r in successful_responses)
            },
            "model_comparisons": [
                {
                    "model": r.model_type.value,
                    "confidence": r.confidence,
                    "processing_time": r.processing_time,
                    "success": r.success,
                    "content_preview": r.content[:200] + "..." if len(r.content) > 200 else r.content
                }
                for r in model_responses.values()
            ],
            "technical_data": {
                "current_price": trading_pattern.price_data[-1] if trading_pattern.price_data else None,
                "trend_direction": trading_pattern.trend_direction,
                "volatility": trading_pattern.volatility,
                "momentum_score": trading_pattern.momentum_score,
                "liquidation_levels": trading_pattern.liquidation_levels,
                "support_resistance": trading_pattern.support_resistance
            },
            "system_status": {
                "available_models": sum(self.model_status.values()),
                "model_availability": {k.value: v for k, v in self.model_status.items()},
                "fallback_active": not self.model_status[ModelType.OPENAI_GPT4_MINI]
            }
        }
        
        return analysis
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all available models"""
        return {
            "available_models": sum(self.model_status.values()),
            "model_details": {
                model_type.value: {
                    "available": available,
                    "type": "cloud" if model_type == ModelType.OPENAI_GPT4_MINI else "local",
                    "capabilities": self._get_model_capabilities(model_type)
                }
                for model_type, available in self.model_status.items()
            },
            "recommended_order": [m.value for m in self.model_priority],
            "local_models_setup": self._get_local_setup_instructions()
        }
    
    def _get_model_capabilities(self, model_type: ModelType) -> List[str]:
        """Get capabilities for each model type"""
        capabilities = {
            ModelType.OPENAI_GPT4_MINI: [
                "Natural language analysis",
                "Comprehensive reports",
                "Historical context integration",
                "Multi-timeframe analysis"
            ],
            ModelType.DEEPSEEK_CODER: [
                "Structured data analysis",
                "Logic-heavy pattern recognition",
                "Time-series analysis",
                "Technical indicator interpretation"
            ],
            ModelType.DEEPSEEK_R1_DISTILL: [
                "Fast reasoning",
                "Pattern detection",
                "Trend analysis",
                "Risk assessment"
            ],
            ModelType.PHI_3: [
                "Compact analysis",
                "Quick insights",
                "Numeric pattern detection",
                "Trading signals"
            ],
            ModelType.PHI_4: [
                "Enhanced compact analysis",
                "Better reasoning",
                "Improved pattern recognition",
                "More accurate signals"
            ]
        }
        return capabilities.get(model_type, [])
    
    def _get_local_setup_instructions(self) -> Dict[str, str]:
        """Get setup instructions for local models"""
        return {
            "ollama_install": "curl -fsSL https://ollama.ai/install.sh | sh",
            "deepseek_coder": "ollama pull deepseek-coder",
            "deepseek_r1": "ollama pull deepseek-r1-distill-llama",
            "phi3": "ollama pull phi3",
            "phi4": "ollama pull phi4",
            "verify": "ollama list"
        }