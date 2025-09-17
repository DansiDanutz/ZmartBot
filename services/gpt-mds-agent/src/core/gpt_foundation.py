"""
GPT Foundation - Core OpenAI Integration Layer
=============================================
This is the heart of the GPT MDS Agent Service
"""

import os
import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog
from cachetools import TTLCache
import backoff

# Configure structured logging
logger = structlog.get_logger()

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    logger.error("OpenAI library not found. Install with: pip install openai")
    raise

class ModelType(Enum):
    """Available GPT models with capabilities"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_TURBO_PREVIEW = "gpt-4-turbo-preview"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_5 = "gpt-5"  # Future model placeholder
    
    @classmethod
    def get_capability_score(cls, model: str) -> int:
        """Get capability score for model selection"""
        scores = {
            cls.GPT_35_TURBO.value: 30,
            cls.GPT_4O_MINI.value: 50,
            cls.GPT_4O.value: 70,
            cls.GPT_4_TURBO.value: 90,
            cls.GPT_4_TURBO_PREVIEW.value: 85,
            cls.GPT_5.value: 100
        }
        return scores.get(model, 50)

@dataclass
class GPTConfig:
    """Configuration for GPT operations"""
    api_key: str
    org_id: Optional[str] = None
    primary_model: str = ModelType.GPT_4O.value
    fallback_model: str = ModelType.GPT_4O_MINI.value
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    enable_cache: bool = True
    cache_ttl: int = 3600
    rate_limit: int = 60  # requests per minute
    
@dataclass
class GPTResponse:
    """Structured response from GPT"""
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModelSelector:
    """Intelligent model selection based on task complexity"""
    
    def __init__(self):
        self.selection_history = []
    
    def select_model(self, 
                     content_length: int,
                     complexity_indicators: List[str],
                     required_capability: int = 50) -> str:
        """
        Select optimal model based on task requirements
        
        Args:
            content_length: Length of input content
            complexity_indicators: Keywords indicating complexity
            required_capability: Minimum capability score needed
            
        Returns:
            Selected model name
        """
        complexity_score = self._calculate_complexity(
            content_length, 
            complexity_indicators
        )
        
        # Model selection logic
        if complexity_score >= 80 or required_capability >= 80:
            model = ModelType.GPT_4_TURBO.value
        elif complexity_score >= 60 or required_capability >= 60:
            model = ModelType.GPT_4O.value
        elif complexity_score >= 40 or required_capability >= 40:
            model = ModelType.GPT_4O_MINI.value
        else:
            model = ModelType.GPT_35_TURBO.value
        
        # Log selection
        self.selection_history.append({
            "timestamp": datetime.now().isoformat(),
            "complexity_score": complexity_score,
            "selected_model": model
        })
        
        logger.info("Model selected", 
                   model=model, 
                   complexity=complexity_score)
        
        return model
    
    def _calculate_complexity(self, 
                             content_length: int,
                             indicators: List[str]) -> int:
        """Calculate task complexity score (0-100)"""
        score = 0
        
        # Length-based scoring
        if content_length > 10000:
            score += 30
        elif content_length > 5000:
            score += 20
        elif content_length > 2000:
            score += 10
        else:
            score += 5
        
        # Indicator-based scoring
        high_complexity_terms = [
            "orchestration", "integration", "distributed",
            "architecture", "optimization", "analysis",
            "machine learning", "complex", "advanced"
        ]
        
        for term in high_complexity_terms:
            if any(term in indicator.lower() for indicator in indicators):
                score += 10
        
        # Cap at 100
        return min(score, 100)

class GPTFoundation:
    """
    Core GPT integration foundation with advanced features
    """
    
    def __init__(self, config: GPTConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            organization=config.org_id
        )
        self.model_selector = ModelSelector()
        
        # Initialize cache if enabled
        if config.enable_cache:
            self.cache = TTLCache(
                maxsize=100,
                ttl=config.cache_ttl
            )
        else:
            self.cache = None
        
        # Metrics tracking
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
        
        # Rate limiting
        self.last_call_time = None
        self.calls_this_minute = 0
        
        logger.info("GPT Foundation initialized", 
                   model=config.primary_model)
    
    def _get_cache_key(self, prompt: str, system: str = "") -> str:
        """Generate cache key for prompt"""
        content = f"{system}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _check_rate_limit(self):
        """Implement rate limiting"""
        now = datetime.now()
        
        if self.last_call_time:
            time_diff = (now - self.last_call_time).total_seconds()
            if time_diff < 60:  # Within the same minute
                if self.calls_this_minute >= self.config.rate_limit:
                    wait_time = 60 - time_diff
                    logger.warning(f"Rate limit reached, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    self.calls_this_minute = 0
            else:
                self.calls_this_minute = 0
        
        self.calls_this_minute += 1
        self.last_call_time = now
    
    @backoff.on_exception(
        backoff.expo,
        (openai.APIError, openai.APITimeoutError),
        max_tries=3,
        max_time=60
    )
    async def call_gpt(self,
                       prompt: str,
                       system_message: str = "",
                       model_override: Optional[str] = None,
                       temperature_override: Optional[float] = None,
                       stream: bool = False) -> GPTResponse:
        """
        Core GPT calling function with all advanced features
        
        Args:
            prompt: User prompt
            system_message: System message for context
            model_override: Override model selection
            temperature_override: Override temperature
            stream: Enable streaming response
            
        Returns:
            GPTResponse object with results
        """
        start_time = datetime.now()
        
        # Check cache first
        if self.cache is not None and not stream:
            cache_key = self._get_cache_key(prompt, system_message)
            if cache_key in self.cache:
                self.metrics["cache_hits"] += 1
                cached_response = self.cache[cache_key]
                cached_response.cached = True
                logger.info("Cache hit", key=cache_key[:8])
                return cached_response
        
        # Rate limiting
        await self._check_rate_limit()
        
        # Model selection
        if model_override:
            model = model_override
        else:
            # Auto-select based on complexity
            complexity_indicators = [
                word for word in prompt.split() 
                if len(word) > 5
            ][:10]  # Top 10 long words as indicators
            
            model = self.model_selector.select_model(
                len(prompt),
                complexity_indicators
            )
        
        # Prepare messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        try:
            self.metrics["total_calls"] += 1
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature_override or self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                return await self._handle_stream(response, model, start_time)
            
            # Process regular response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            self.metrics["successful_calls"] += 1
            self.metrics["total_tokens"] += tokens_used
            self.metrics["total_cost"] += self._calculate_cost(
                model, tokens_used
            )
            
            # Create response object
            gpt_response = GPTResponse(
                content=content,
                model_used=model,
                tokens_used=tokens_used,
                response_time=response_time,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "prompt_length": len(prompt),
                    "temperature": temperature_override or self.config.temperature
                }
            )
            
            # Cache the response
            if self.cache is not None and not stream:
                cache_key = self._get_cache_key(prompt, system_message)
                self.cache[cache_key] = gpt_response
            
            logger.info("GPT call successful",
                       model=model,
                       tokens=tokens_used,
                       time=response_time)
            
            return gpt_response
            
        except Exception as e:
            self.metrics["failed_calls"] += 1
            logger.error("GPT call failed",
                        model=model,
                        error=str(e))
            
            # Try fallback model
            if model != self.config.fallback_model:
                logger.info("Trying fallback model",
                           fallback=self.config.fallback_model)
                return await self.call_gpt(
                    prompt,
                    system_message,
                    model_override=self.config.fallback_model,
                    temperature_override=temperature_override,
                    stream=stream
                )
            
            raise
    
    async def _handle_stream(self, 
                           response_stream,
                           model: str,
                           start_time: datetime) -> GPTResponse:
        """Handle streaming response from GPT"""
        content_parts = []
        total_tokens = 0
        
        async for chunk in response_stream:
            if chunk.choices[0].delta.content:
                content_parts.append(chunk.choices[0].delta.content)
        
        content = "".join(content_parts)
        response_time = (datetime.now() - start_time).total_seconds()
        
        return GPTResponse(
            content=content,
            model_used=model,
            tokens_used=total_tokens,
            response_time=response_time,
            metadata={
                "streamed": True,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate API cost based on model and tokens"""
        # Pricing per 1K tokens (approximate)
        pricing = {
            ModelType.GPT_35_TURBO.value: 0.002,
            ModelType.GPT_4O_MINI.value: 0.01,
            ModelType.GPT_4O.value: 0.03,
            ModelType.GPT_4_TURBO.value: 0.06,
            ModelType.GPT_5.value: 0.10  # Estimated
        }
        
        rate = pricing.get(model, 0.03)
        return (tokens / 1000) * rate
    
    async def validate_connection(self) -> bool:
        """Test GPT API connection"""
        try:
            response = await self.call_gpt(
                "Reply with OK",
                "You are a connection test. Reply only with 'OK'.",
                model_override=ModelType.GPT_35_TURBO.value
            )
            return "OK" in response.content
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            **self.metrics,
            "cache_size": len(self.cache) if self.cache else 0,
            "avg_cost_per_call": (
                self.metrics["total_cost"] / self.metrics["total_calls"]
                if self.metrics["total_calls"] > 0 else 0
            )
        }