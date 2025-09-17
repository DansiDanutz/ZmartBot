#!/usr/bin/env python3
"""
🧠 DYNAMIC TOKEN MANAGER - Intelligent LLM Router
Premium AI models orchestration with dynamic token usage optimization
"""

import os
import sys
import json
import logging
import argparse
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMModel:
    """Represents an available LLM model"""
    name: str
    port: int
    max_tokens: int
    cost_per_token: float
    quality_score: float
    specialization: List[str]
    current_load: float = 0.0
    available: bool = True
    response_time_avg: float = 1.0

@dataclass
class TokenUsageStats:
    """Token usage statistics"""
    model_name: str
    tokens_used: int
    requests_count: int
    total_cost: float
    avg_response_time: float
    success_rate: float

class DynamicTokenManager:
    """
    🧠 DYNAMIC TOKEN MANAGER
    
    Intelligent orchestration system that dynamically routes requests
    to the best available LLM based on:
    - Token requirements vs available capacity
    - Request complexity and specialization needs
    - Current model load and response times
    - Cost optimization strategies
    - Quality requirements
    """
    
    def __init__(self, project_root: str = None, port: int = 8015):
        self.project_root = Path(project_root) if project_root else Path("../.")
        self.port = port
        self.db_path = self.project_root / "zmart-api" / "token_manager_database.db"
        
        # Initialize available LLM models
        self.available_models = {
            "gemini_1_5_pro": LLMModel(
                name="Gemini 1.5 Pro",
                port=8013,
                max_tokens=2000000,  # 2M tokens - Ultimate capacity
                cost_per_token=0.000001,
                quality_score=0.98,
                specialization=["massive_context", "document_analysis", "multi_modal"]
            ),
            "claude_max": LLMModel(
                name="Claude Max",
                port=8010,
                max_tokens=200000,   # 200K tokens - Premium capacity
                cost_per_token=0.000003,
                quality_score=0.97,
                specialization=["advanced_reasoning", "trading_analysis", "streaming"]
            ),
            "gpt5_pro": LLMModel(
                name="GPT-5 Pro",
                port=8012,
                max_tokens=128000,   # 128K tokens - Professional capacity
                cost_per_token=0.000005,
                quality_score=0.96,
                specialization=["o1_reasoning", "complex_analysis", "professional_insights"]
            ),
            "deepseek_v3": LLMModel(
                name="DeepSeek V3",
                port=8016,
                max_tokens=64000,    # 64K tokens - FREE tier with generous limits!
                cost_per_token=0.000000,  # FREE!
                quality_score=0.94,
                specialization=["coding", "reasoning", "mathematics", "free_tier"]
            ),
            "grok_beta": LLMModel(
                name="Grok Beta", 
                port=8017,
                max_tokens=32000,    # 32K tokens - FREE tier
                cost_per_token=0.000000,  # FREE!
                quality_score=0.92,
                specialization=["real_time", "news_analysis", "humor", "free_tier"]
            ),
            "premium_ai": LLMModel(
                name="Premium AI",
                port=8009,
                max_tokens=32000,    # 32K tokens - Standard capacity
                cost_per_token=0.000002,
                quality_score=0.94,
                specialization=["vector_search", "memory_integration", "general_purpose"]
            )
        }
        
        # Initialize database
        self.init_database()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        # Performance metrics
        self.total_requests = 0
        self.total_tokens_saved = 0
        self.routing_decisions = 0
        
        logger.info(f"🧠 Dynamic Token Manager initialized - Port: {self.port}")
        logger.info(f"✅ Intelligent routing: 4 premium models")
        logger.info(f"✅ Token optimization: Active")
        logger.info(f"✅ Cost management: Enabled")
    
    def init_database(self):
        """Initialize the token management database"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Token usage tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    request_type TEXT NOT NULL,
                    tokens_requested INTEGER,
                    tokens_used INTEGER,
                    response_time REAL,
                    success BOOLEAN,
                    cost REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Model performance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    avg_response_time REAL,
                    success_rate REAL,
                    load_factor REAL,
                    quality_score REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Routing decisions log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routing_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_tokens INTEGER,
                    selected_model TEXT,
                    reason TEXT,
                    alternatives TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_model_time ON token_usage(model_name, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_routing_time ON routing_decisions(timestamp)")
            
            conn.commit()
            conn.close()
            logger.info("✅ Token management database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "🧠 dynamic_token_manager_ready",
                "version": "1.0.0-enterprise",
                "timestamp": datetime.now().isoformat(),
                "capabilities": {
                    "intelligent_routing": "✅ enabled",
                    "token_optimization": "✅ active",
                    "cost_management": "✅ enabled",
                    "multi_model_support": "✅ 4 premium models"
                },
                "models": {
                    model_id: {
                        "name": model.name,
                        "max_tokens": model.max_tokens,
                        "available": model.available,
                        "specialization": model.specialization
                    } for model_id, model in self.available_models.items()
                },
                "metrics": {
                    "total_requests": self.total_requests,
                    "tokens_saved": self.total_tokens_saved,
                    "routing_decisions": self.routing_decisions
                }
            })
        
        @self.app.route('/ai/smart-route', methods=['POST'])
        def smart_route():
            """Intelligent AI routing endpoint"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Extract request parameters
                message = data.get('message', '')
                context_type = data.get('context_type', 'general')
                user_id = data.get('user_id', 'anonymous')
                priority = data.get('priority', 'normal')  # low, normal, high, critical
                budget_limit = data.get('budget_limit', 0.01)  # Cost limit per request
                
                if not message:
                    return jsonify({"error": "Message is required"}), 400
                
                # Estimate token requirements
                estimated_tokens = self.estimate_tokens(message, context_type)
                
                # Select optimal model
                selected_model, routing_reason = self.select_optimal_model(
                    estimated_tokens, context_type, priority, budget_limit
                )
                
                if not selected_model:
                    return jsonify({
                        "error": "No suitable model available",
                        "reason": routing_reason
                    }), 503
                
                # Route request to selected model (synchronous version)
                response = self.route_to_model_sync(selected_model, data)
                
                # Log routing decision
                self.log_routing_decision(estimated_tokens, selected_model, routing_reason)
                
                # Update metrics
                self.total_requests += 1
                self.routing_decisions += 1
                
                return jsonify({
                    "response": response,
                    "model_used": selected_model.name,
                    "routing_reason": routing_reason,
                    "tokens_estimated": estimated_tokens,
                    "cost_estimated": estimated_tokens * selected_model.cost_per_token
                })
                
            except Exception as e:
                logger.error(f"Smart routing error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/ai/model-status', methods=['GET'])
        def model_status():
            """Get real-time status of all models"""
            try:
                status = {}
                for model_id, model in self.available_models.items():
                    # Check model health
                    health_status = asyncio.run(self.check_model_health(model))
                    status[model_id] = {
                        "name": model.name,
                        "port": model.port,
                        "max_tokens": model.max_tokens,
                        "available": health_status,
                        "current_load": model.current_load,
                        "response_time": model.response_time_avg,
                        "specialization": model.specialization
                    }
                
                return jsonify(status)
                
            except Exception as e:
                logger.error(f"Model status error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/ai/usage-analytics', methods=['GET'])
        def usage_analytics():
            """Get comprehensive usage analytics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get usage stats by model
                cursor.execute("""
                    SELECT 
                        model_name,
                        COUNT(*) as requests,
                        SUM(tokens_used) as total_tokens,
                        AVG(response_time) as avg_response_time,
                        SUM(cost) as total_cost,
                        AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                    FROM token_usage 
                    WHERE timestamp >= datetime('now', '-7 days')
                    GROUP BY model_name
                """)
                
                usage_stats = []
                for row in cursor.fetchall():
                    usage_stats.append(TokenUsageStats(
                        model_name=row[0],
                        requests_count=row[1],
                        tokens_used=row[2] or 0,
                        avg_response_time=row[3] or 0,
                        total_cost=row[4] or 0,
                        success_rate=row[5] or 0
                    ))
                
                # Get recent routing decisions
                cursor.execute("""
                    SELECT selected_model, reason, COUNT(*) as count
                    FROM routing_decisions 
                    WHERE timestamp >= datetime('now', '-24 hours')
                    GROUP BY selected_model, reason
                    ORDER BY count DESC
                """)
                
                routing_stats = cursor.fetchall()
                conn.close()
                
                return jsonify({
                    "usage_stats": [asdict(stat) for stat in usage_stats],
                    "routing_stats": [
                        {"model": row[0], "reason": row[1], "count": row[2]}
                        for row in routing_stats
                    ],
                    "total_requests_7days": sum(stat.requests_count for stat in usage_stats),
                    "total_tokens_7days": sum(stat.tokens_used for stat in usage_stats),
                    "total_cost_7days": sum(stat.total_cost for stat in usage_stats)
                })
                
            except Exception as e:
                logger.error(f"Usage analytics error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def estimate_tokens(self, message: str, context_type: str) -> int:
        """Estimate token requirements for a request"""
        base_tokens = len(message.split()) * 1.3  # Rough estimation
        
        # Context type multipliers
        multipliers = {
            'simple': 1.0,
            'general': 1.5,
            'crypto_analysis': 2.0,
            'complex_analysis': 3.0,
            'massive_document': 10.0,
            'multi_modal': 5.0
        }
        
        multiplier = multipliers.get(context_type, 1.5)
        estimated = int(base_tokens * multiplier)
        
        # Add safety margin
        return min(estimated * 1.2, 2000000)  # Cap at Gemini's max
    
    def select_optimal_model(self, tokens_needed: int, context_type: str, 
                           priority: str, budget_limit: float) -> Tuple[Optional[LLMModel], str]:
        """Select the optimal model based on requirements"""
        
        # Filter available models
        suitable_models = []
        
        for model_id, model in self.available_models.items():
            if not model.available:
                continue
                
            # Check token capacity
            if tokens_needed > model.max_tokens:
                continue
                
            # Check budget constraint
            estimated_cost = tokens_needed * model.cost_per_token
            if estimated_cost > budget_limit:
                continue
                
            # Calculate suitability score
            score = self.calculate_suitability_score(model, tokens_needed, context_type, priority)
            suitable_models.append((model, score, estimated_cost))
        
        if not suitable_models:
            return None, "No models meet the requirements"
        
        # Sort by suitability score (descending)
        suitable_models.sort(key=lambda x: x[1], reverse=True)
        
        # Select best model
        best_model, best_score, cost = suitable_models[0]
        
        # Generate routing reason
        reason = f"Selected {best_model.name} (score: {best_score:.2f}, cost: ${cost:.4f})"
        
        # Add specific reasoning
        if tokens_needed > 500000:
            reason += " - Massive context required"
        elif context_type in best_model.specialization:
            reason += f" - Specialized for {context_type}"
        elif priority == "high":
            reason += " - High priority routing"
        
        return best_model, reason
    
    def calculate_suitability_score(self, model: LLMModel, tokens: int, 
                                   context_type: str, priority: str) -> float:
        """Calculate model suitability score"""
        score = 0.0
        
        # Base quality score (0-100)
        score += model.quality_score * 100
        
        # Token efficiency (prefer models that aren't overkill)
        token_ratio = tokens / model.max_tokens
        if 0.1 <= token_ratio <= 0.8:  # Sweet spot
            score += 20
        elif token_ratio > 0.8:  # Near capacity - good utilization
            score += 15
        else:  # Under-utilization
            score += 5
        
        # Specialization bonus
        if context_type in model.specialization:
            score += 30
        
        # Load factor (prefer less loaded models)
        score += (1.0 - model.current_load) * 10
        
        # Response time bonus (prefer faster models)
        score += max(0, (3.0 - model.response_time_avg)) * 5
        
        # Priority adjustments
        if priority == "critical":
            if model.name == "Gemini 1.5 Pro":
                score += 50  # Always prefer Gemini for critical
        elif priority == "low":
            # Prefer cost-effective models for low priority
            score += (1.0 / model.cost_per_token) * 0.001
        
        return score
    
    async def check_model_health(self, model: LLMModel) -> bool:
        """Check if a model is healthy and available"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{model.port}/health"
                async with session.get(url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    def route_to_model_sync(self, model: LLMModel, request_data: Dict) -> Dict:
        """Route request to the selected model (synchronous version)"""
        try:
            import requests
            
            # Determine the appropriate endpoint based on model
            endpoints = {
                "Gemini 1.5 Pro": "/ai/gemini-massive-chat",
                "Claude Max": "/ai/claude-max-chat", 
                "GPT-5 Pro": "/ai/gpt5-pro-chat",
                "Premium AI": "/ai/premium-chat",
                "DeepSeek V3": "/ai/deepseek-chat",
                "Grok Beta": "/ai/grok-chat"
            }
            
            endpoint = endpoints.get(model.name, "/health")
            url = f"http://localhost:{model.port}{endpoint}"
            
            response = requests.post(url, json=request_data, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Model {model.name} returned status {response.status_code}"}
                        
        except Exception as e:
            logger.error(f"Error routing to {model.name}: {e}")
            return {"error": f"Failed to route to {model.name}: {str(e)}"}
    
    async def route_to_model(self, model: LLMModel, request_data: Dict) -> Dict:
        """Route request to the selected model"""
        try:
            # Determine the appropriate endpoint based on model
            endpoints = {
                "Gemini 1.5 Pro": "/ai/gemini-massive-chat",
                "Claude Max": "/ai/claude-max-chat", 
                "GPT-5 Pro": "/ai/gpt5-pro-chat",
                "Premium AI": "/ai/premium-chat"
            }
            
            endpoint = endpoints.get(model.name, "/health")
            url = f"http://localhost:{model.port}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Model {model.name} returned status {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error routing to {model.name}: {e}")
            return {"error": f"Failed to route to {model.name}: {str(e)}"}
    
    def log_routing_decision(self, tokens: int, model: LLMModel, reason: str):
        """Log routing decision for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get alternative models that were considered
            alternatives = [m.name for m in self.available_models.values() 
                          if m.available and m.name != model.name]
            
            cursor.execute("""
                INSERT INTO routing_decisions 
                (request_tokens, selected_model, reason, alternatives)
                VALUES (?, ?, ?, ?)
            """, (tokens, model.name, reason, json.dumps(alternatives)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log routing decision: {e}")
    
    def run(self):
        """Run the Dynamic Token Manager service"""
        logger.info(f"🧠 Starting Dynamic Token Manager on port {self.port}")
        logger.info(f"✅ Ready for intelligent AI orchestration")
        logger.info(f"✅ Managing 4 premium LLM models")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Dynamic Token Manager')
    parser.add_argument('--port', type=int, default=8015, help='Port to run on')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    
    args = parser.parse_args()
    
    # Create and run service
    service = DynamicTokenManager(
        project_root=args.project_root,
        port=args.port
    )
    
    service.run()

if __name__ == '__main__':
    main()