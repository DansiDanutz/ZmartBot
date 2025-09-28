"""
Unified Analytics Service for Cross-Project Data Analysis
Integrates ZmartyBrain and ZmartBot data for comprehensive insights
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import statistics
from supabase import create_client, Client
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    USER_ENGAGEMENT = "user_engagement"
    TRADING_PERFORMANCE = "trading_performance"
    RISK_ANALYSIS = "risk_analysis"
    MARKET_CORRELATION = "market_correlation"
    PREDICTIVE_INSIGHTS = "predictive_insights"

@dataclass
class AnalyticsResult:
    type: AnalyticsType
    user_id: str
    data: Dict[str, Any]
    confidence_score: float
    generated_at: datetime
    time_range: Tuple[datetime, datetime]

class UnifiedAnalyticsService:
    """
    Unified Analytics Service that combines data from both Supabase projects
    to provide comprehensive insights across user behavior and trading performance
    """
    
    def __init__(self):
        # ZmartyBrain configuration
        self.brain_url = "https://xhskmqsgtdhehzlvtuns.supabase.co"
        self.brain_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw"
        
        # ZmartBot configuration
        self.bot_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.bot_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        
        # Initialize clients
        self.brain_client: Optional[Client] = None
        self.bot_client: Optional[Client] = None
        
        # Analytics cache
        self.analytics_cache: Dict[str, AnalyticsResult] = {}
        self.cache_ttl = 300  # 5 minutes
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase clients for both projects"""
        try:
            self.brain_client = create_client(self.brain_url, self.brain_key)
            self.bot_client = create_client(self.bot_url, self.bot_key)
            logger.info("✅ Unified Analytics Service initialized with both Supabase clients")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase clients: {e}")
            raise
    
    async def get_user_engagement_analytics(self, user_id: str, days: int = 30) -> AnalyticsResult:
        """
        Analyze user engagement patterns from ZmartyBrain
        """
        try:
            cache_key = f"engagement_{user_id}_{days}"
            if cache_key in self.analytics_cache:
                cached_result = self.analytics_cache[cache_key]
                if (datetime.now() - cached_result.generated_at).seconds < self.cache_ttl:
                    return cached_result
            
            # Get user data from ZmartyBrain
            user_data = await self._get_brain_user_data(user_id)
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found in ZmartyBrain")
            
            # Calculate engagement metrics
            engagement_metrics = self._calculate_engagement_metrics(user_data, days)
            
            # Get trading activity correlation
            trading_correlation = await self._get_trading_engagement_correlation(user_id, days)
            
            result = AnalyticsResult(
                type=AnalyticsType.USER_ENGAGEMENT,
                user_id=user_id,
                data={
                    "engagement_score": user_data.get("engagement_score", 0.5),
                    "credits_balance": user_data.get("credits_balance", 0),
                    "subscription_tier": user_data.get("subscription_tier", "free"),
                    "last_active": user_data.get("last_active"),
                    "metrics": engagement_metrics,
                    "trading_correlation": trading_correlation,
                    "recommendations": self._generate_engagement_recommendations(engagement_metrics)
                },
                confidence_score=0.85,
                generated_at=datetime.now(),
                time_range=(datetime.now() - timedelta(days=days), datetime.now())
            )
            
            self.analytics_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get user engagement analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_trading_performance_analytics(self, user_id: str, days: int = 30) -> AnalyticsResult:
        """
        Analyze trading performance from ZmartBot
        """
        try:
            cache_key = f"trading_{user_id}_{days}"
            if cache_key in self.analytics_cache:
                cached_result = self.analytics_cache[cache_key]
                if (datetime.now() - cached_result.generated_at).seconds < self.cache_ttl:
                    return cached_result
            
            # Get trading data from ZmartBot
            trades = await self._get_bot_trading_data(user_id, days)
            portfolio = await self._get_bot_portfolio_data(user_id)
            strategies = await self._get_bot_strategies_data(user_id)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(trades, portfolio)
            
            # Get risk analysis
            risk_analysis = self._calculate_risk_metrics(trades, portfolio)
            
            # Get strategy effectiveness
            strategy_analysis = self._analyze_strategy_effectiveness(strategies, trades)
            
            result = AnalyticsResult(
                type=AnalyticsType.TRADING_PERFORMANCE,
                user_id=user_id,
                data={
                    "total_trades": len(trades),
                    "total_pnl": sum(trade.get("pnl", 0) for trade in trades),
                    "win_rate": self._calculate_win_rate(trades),
                    "performance_metrics": performance_metrics,
                    "risk_analysis": risk_analysis,
                    "strategy_analysis": strategy_analysis,
                    "recommendations": self._generate_trading_recommendations(performance_metrics, risk_analysis)
                },
                confidence_score=0.90,
                generated_at=datetime.now(),
                time_range=(datetime.now() - timedelta(days=days), datetime.now())
            )
            
            self.analytics_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get trading performance analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_cross_project_insights(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Generate insights that combine data from both projects
        """
        try:
            # Get analytics from both projects
            engagement_analytics = await self.get_user_engagement_analytics(user_id, days)
            trading_analytics = await self.get_trading_performance_analytics(user_id, days)
            
            # Cross-project correlation analysis
            correlation_analysis = self._analyze_cross_project_correlation(
                engagement_analytics, trading_analytics
            )
            
            # Predictive insights
            predictive_insights = self._generate_predictive_insights(
                engagement_analytics, trading_analytics
            )
            
            # Unified recommendations
            unified_recommendations = self._generate_unified_recommendations(
                engagement_analytics, trading_analytics, correlation_analysis
            )
            
            return {
                "user_id": user_id,
                "analysis_period": f"{days} days",
                "engagement_analytics": engagement_analytics.data,
                "trading_analytics": trading_analytics.data,
                "correlation_analysis": correlation_analysis,
                "predictive_insights": predictive_insights,
                "unified_recommendations": unified_recommendations,
                "generated_at": datetime.now().isoformat(),
                "confidence_score": min(engagement_analytics.confidence_score, trading_analytics.confidence_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get cross-project insights: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_brain_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from ZmartyBrain"""
        try:
            response = self.brain_client.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get brain user data: {e}")
            return None
    
    async def _get_bot_trading_data(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get trading data from ZmartBot"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = self.bot_client.table("trades").select("*").eq("user_id", user_id).gte("timestamp", cutoff_date).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Failed to get bot trading data: {e}")
            return []
    
    async def _get_bot_portfolio_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get portfolio data from ZmartBot"""
        try:
            response = self.bot_client.table("portfolios").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Failed to get bot portfolio data: {e}")
            return []
    
    async def _get_bot_strategies_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get strategies data from ZmartBot"""
        try:
            response = self.bot_client.table("trading_strategies").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Failed to get bot strategies data: {e}")
            return []
    
    def _calculate_engagement_metrics(self, user_data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Calculate engagement metrics from user data"""
        engagement_score = user_data.get("engagement_score", 0.5)
        credits_balance = user_data.get("credits_balance", 0)
        subscription_tier = user_data.get("subscription_tier", "free")
        
        # Calculate engagement level
        if engagement_score > 0.8:
            engagement_level = "high"
        elif engagement_score > 0.5:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        # Calculate tier value
        tier_values = {"free": 1, "premium": 2, "enterprise": 3}
        tier_value = tier_values.get(subscription_tier, 1)
        
        return {
            "engagement_level": engagement_level,
            "engagement_score": engagement_score,
            "credits_utilization": min(1.0, credits_balance / 1000),  # Assuming 1000 is max
            "tier_value": tier_value,
            "engagement_trend": "stable"  # Could be calculated from historical data
        }
    
    def _calculate_performance_metrics(self, trades: List[Dict[str, Any]], portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trading performance metrics"""
        if not trades:
            return {
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "volatility": 0,
                "profit_factor": 0
            }
        
        # Calculate returns
        returns = [trade.get("pnl", 0) for trade in trades]
        total_return = sum(returns)
        
        # Calculate Sharpe ratio
        if len(returns) > 1:
            avg_return = statistics.mean(returns)
            std_return = statistics.stdev(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(returns)
        
        # Calculate volatility
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # Calculate profit factor
        profits = [r for r in returns if r > 0]
        losses = [abs(r) for r in returns if r < 0]
        profit_factor = sum(profits) / sum(losses) if losses else float('inf')
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "volatility": volatility,
            "profit_factor": profit_factor
        }
    
    def _calculate_risk_metrics(self, trades: List[Dict[str, Any]], portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk metrics"""
        if not trades:
            return {"risk_score": 0.5, "risk_level": "medium"}
        
        # Calculate position sizes and leverage
        position_sizes = [trade.get("position_size", 0) for trade in trades]
        leverages = [trade.get("leverage", 1) for trade in trades]
        
        avg_position_size = statistics.mean(position_sizes) if position_sizes else 0
        avg_leverage = statistics.mean(leverages) if leverages else 1
        
        # Calculate risk score (0-1, higher is riskier)
        risk_score = min(1.0, (avg_position_size * avg_leverage) / 10000)
        
        if risk_score > 0.7:
            risk_level = "high"
        elif risk_score > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "avg_position_size": avg_position_size,
            "avg_leverage": avg_leverage
        }
    
    def _analyze_strategy_effectiveness(self, strategies: List[Dict[str, Any]], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze strategy effectiveness"""
        if not strategies:
            return {"active_strategies": 0, "strategy_performance": {}}
        
        active_strategies = [s for s in strategies if s.get("status") == "active"]
        
        # Group trades by strategy
        strategy_performance = {}
        for strategy in active_strategies:
            strategy_id = strategy.get("id")
            strategy_trades = [t for t in trades if t.get("strategy_id") == strategy_id]
            
            if strategy_trades:
                win_rate = len([t for t in strategy_trades if t.get("pnl", 0) > 0]) / len(strategy_trades)
                total_pnl = sum(t.get("pnl", 0) for t in strategy_trades)
                
                strategy_performance[strategy_id] = {
                    "name": strategy.get("name", "Unknown"),
                    "trades_count": len(strategy_trades),
                    "win_rate": win_rate,
                    "total_pnl": total_pnl
                }
        
        return {
            "active_strategies": len(active_strategies),
            "strategy_performance": strategy_performance
        }
    
    def _calculate_win_rate(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate win rate from trades"""
        if not trades:
            return 0.0
        
        winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
        return winning_trades / len(trades)
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        peak = returns[0]
        max_dd = 0.0
        
        for ret in returns:
            if ret > peak:
                peak = ret
            drawdown = (peak - ret) / peak if peak > 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd * 100  # Return as percentage
    
    async def _get_trading_engagement_correlation(self, user_id: str, days: int) -> Dict[str, Any]:
        """Analyze correlation between trading activity and engagement"""
        # This would analyze how trading activity affects user engagement
        # For now, return a placeholder
        return {
            "correlation_strength": 0.7,
            "trading_boosts_engagement": True,
            "recommendation": "Increase trading activity to boost engagement"
        }
    
    def _analyze_cross_project_correlation(self, engagement_analytics: AnalyticsResult, trading_analytics: AnalyticsResult) -> Dict[str, Any]:
        """Analyze correlation between engagement and trading performance"""
        engagement_score = engagement_analytics.data.get("engagement_score", 0.5)
        trading_pnl = trading_analytics.data.get("total_pnl", 0)
        win_rate = trading_analytics.data.get("win_rate", 0)
        
        # Simple correlation analysis
        correlation_strength = min(1.0, abs(engagement_score - 0.5) * 2 + abs(win_rate - 0.5) * 2)
        
        return {
            "engagement_trading_correlation": correlation_strength,
            "high_engagement_high_performance": engagement_score > 0.7 and win_rate > 0.6,
            "insights": [
                "Users with higher engagement tend to have better trading performance",
                "Trading success correlates with platform engagement"
            ]
        }
    
    def _generate_predictive_insights(self, engagement_analytics: AnalyticsResult, trading_analytics: AnalyticsResult) -> Dict[str, Any]:
        """Generate predictive insights based on current data"""
        engagement_score = engagement_analytics.data.get("engagement_score", 0.5)
        win_rate = trading_analytics.data.get("win_rate", 0)
        
        # Simple predictive model
        if engagement_score > 0.8 and win_rate > 0.6:
            prediction = "high_performance"
            confidence = 0.85
        elif engagement_score > 0.6 and win_rate > 0.5:
            prediction = "improving_performance"
            confidence = 0.70
        else:
            prediction = "needs_improvement"
            confidence = 0.60
        
        return {
            "predicted_performance": prediction,
            "confidence": confidence,
            "recommended_actions": self._get_prediction_actions(prediction)
        }
    
    def _get_prediction_actions(self, prediction: str) -> List[str]:
        """Get recommended actions based on prediction"""
        actions = {
            "high_performance": [
                "Continue current strategy",
                "Consider increasing position sizes",
                "Share success with community"
            ],
            "improving_performance": [
                "Focus on risk management",
                "Analyze winning trades",
                "Consider advanced strategies"
            ],
            "needs_improvement": [
                "Review trading strategy",
                "Focus on education",
                "Start with smaller positions"
            ]
        }
        return actions.get(prediction, [])
    
    def _generate_engagement_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate engagement recommendations"""
        recommendations = []
        
        if metrics["engagement_level"] == "low":
            recommendations.append("Increase platform usage to improve engagement")
            recommendations.append("Complete profile setup")
            recommendations.append("Join community discussions")
        
        if metrics["credits_utilization"] < 0.3:
            recommendations.append("Use more platform features to maximize value")
        
        return recommendations
    
    def _generate_trading_recommendations(self, performance_metrics: Dict[str, Any], risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations"""
        recommendations = []
        
        if performance_metrics["sharpe_ratio"] < 1.0:
            recommendations.append("Focus on improving risk-adjusted returns")
        
        if risk_analysis["risk_level"] == "high":
            recommendations.append("Consider reducing position sizes or leverage")
        
        if performance_metrics["max_drawdown"] > 20:
            recommendations.append("Implement better stop-loss strategies")
        
        return recommendations
    
    def _generate_unified_recommendations(self, engagement_analytics: AnalyticsResult, trading_analytics: AnalyticsResult, correlation_analysis: Dict[str, Any]) -> List[str]:
        """Generate unified recommendations combining both analyses"""
        recommendations = []
        
        # Engagement-based recommendations
        engagement_recommendations = self._generate_engagement_recommendations(engagement_analytics.data.get("metrics", {}))
        recommendations.extend(engagement_recommendations)
        
        # Trading-based recommendations
        trading_recommendations = self._generate_trading_recommendations(
            trading_analytics.data.get("performance_metrics", {}),
            trading_analytics.data.get("risk_analysis", {})
        )
        recommendations.extend(trading_recommendations)
        
        # Cross-project recommendations
        if correlation_analysis.get("high_engagement_high_performance"):
            recommendations.append("Maintain current engagement level for continued success")
        
        return list(set(recommendations))  # Remove duplicates

# FastAPI integration
app = FastAPI(title="Unified Analytics Service", version="1.0.0")
analytics_service = UnifiedAnalyticsService()

@app.get("/analytics/engagement/{user_id}")
async def get_engagement_analytics(user_id: str, days: int = 30):
    """Get user engagement analytics"""
    result = await analytics_service.get_user_engagement_analytics(user_id, days)
    return result.data

@app.get("/analytics/trading/{user_id}")
async def get_trading_analytics(user_id: str, days: int = 30):
    """Get trading performance analytics"""
    result = await analytics_service.get_trading_performance_analytics(user_id, days)
    return result.data

@app.get("/analytics/unified/{user_id}")
async def get_unified_analytics(user_id: str, days: int = 30):
    """Get unified cross-project analytics"""
    return await analytics_service.get_cross_project_insights(user_id, days)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8901)

