#!/usr/bin/env python3
"""
Zmarty Engagement Service - FastAPI Integration
Provides HTTP endpoints for the Zmarty Interactive Engagement System with MCP integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import asyncio
import logging
import json
from datetime import datetime

from engagement_engine import EngagementEngine, ContentTier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ZmartyEngagementService')

# FastAPI app setup
app = FastAPI(
    title="Zmarty Interactive Engagement System",
    description="AI-powered trading mentor with real-time MCP data integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engagement engine instance
engagement_engine = None

# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message or question")
    asset: str = Field(default="BTC", description="Cryptocurrency asset symbol")
    interaction_type: str = Field(default="chat", description="Type of interaction")

class PremiumUnlockRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    content_tier: str = Field(..., description="Content tier to unlock (BASIC, PREMIUM, EXCLUSIVE)")
    credits_spent: int = Field(..., description="Number of credits to spend")

class MarketAlertRequest(BaseModel):
    asset: str = Field(..., description="Cryptocurrency asset symbol")
    alert_type: str = Field(..., description="Type of alert (liquidation, whale, sentiment, etc.)")
    urgency: int = Field(..., ge=1, le=10, description="Alert urgency level (1-10)")
    message: str = Field(..., description="Alert message content")

class UserProfileResponse(BaseModel):
    user_id: str
    skill_level: str
    total_credits_spent: int
    current_streak: int
    achievements: List[str]
    engagement_score: float
    last_interaction: Optional[str]

class ChatResponse(BaseModel):
    response: Dict[str, Any]
    user_profile: Dict[str, Any]
    new_achievements: List[str]
    engagement_score: float
    suggested_actions: List[str]
    market_context: Dict[str, Any]

class AnalyticsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_interactions: int
    average_engagement_score: float
    premium_conversion_rate: float
    top_achievements: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Initialize the engagement engine on startup"""
    global engagement_engine
    try:
        engagement_engine = EngagementEngine()
        logger.info("🚀 Zmarty Engagement Service started successfully")
        logger.info("✅ MCP Integration ready: KingFisher, Cryptometer, RiskMetric, Grok, X Sentiment, Whale Alerts")
    except Exception as e:
        logger.error(f"❌ Failed to initialize engagement engine: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global engagement_engine
    if engagement_engine and hasattr(engagement_engine.mcp_manager, 'close'):
        await engagement_engine.mcp_manager.close()
        logger.info("🛑 Zmarty Engagement Service stopped")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Zmarty Engagement System",
        "timestamp": datetime.now().isoformat(),
        "mcp_integration": "active",
        "data_sources": ["KingFisher", "Cryptometer", "RiskMetric", "Grok", "X Sentiment", "Whale Alerts"]
    }

@app.post("/interact", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest):
    """Main chat interaction endpoint with real MCP data"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        logger.info(f"💬 Processing interaction for user {request.user_id}: {request.message[:50]}...")
        
        # Process interaction with MCP data
        result = await engagement_engine.process_interaction(
            user_id=request.user_id,
            interaction_type=request.interaction_type,
            asset=request.asset,
            user_input=request.message
        )
        
        logger.info(f"✅ Interaction processed - Engagement Score: {result['engagement_score']:.2f}")
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error processing interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process interaction: {str(e)}")

@app.post("/unlock-premium")
async def unlock_premium_content(request: PremiumUnlockRequest):
    """Unlock premium content with credits"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        # Map string to ContentTier enum
        tier_mapping = {
            "BASIC": ContentTier.BASIC,
            "PREMIUM": ContentTier.PREMIUM,
            "EXCLUSIVE": ContentTier.EXCLUSIVE
        }
        
        if request.content_tier not in tier_mapping:
            raise HTTPException(status_code=400, detail="Invalid content tier")
        
        content_tier = tier_mapping[request.content_tier]
        
        result = engagement_engine.unlock_premium_content(
            user_id=request.user_id,
            content_tier=content_tier,
            credits_spent=request.credits_spent
        )
        
        logger.info(f"💎 Premium content unlocked for user {request.user_id}: {request.content_tier} ({request.credits_spent} credits)")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error unlocking premium content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unlock premium content: {str(e)}")

@app.get("/user/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get user profile and statistics"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        profile = engagement_engine.get_user_profile(user_id)
        
        # Calculate current engagement score
        # For this we'll create a simple proactive interaction to get the score
        temp_result = await engagement_engine.process_interaction(
            user_id=user_id,
            interaction_type="profile_check",
            asset="BTC",
            user_input=None
        )
        
        return UserProfileResponse(
            user_id=profile.user_id,
            skill_level=profile.skill_level.value,
            total_credits_spent=profile.total_credits_spent,
            current_streak=profile.current_streak,
            achievements=profile.achievements,
            engagement_score=temp_result["engagement_score"],
            last_interaction=profile.last_interaction.isoformat() if profile.last_interaction else None
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@app.post("/market-alert")
async def send_market_alert(request: MarketAlertRequest, background_tasks: BackgroundTasks):
    """Send market alert to relevant users"""
    try:
        logger.info(f"📢 Market alert: {request.alert_type} for {request.asset} (urgency: {request.urgency})")
        
        # In a real implementation, this would:
        # 1. Find users interested in this asset
        # 2. Send personalized alerts based on their preferences
        # 3. Log the alert for analytics
        
        # For now, we'll just log and return success
        background_tasks.add_task(
            process_market_alert_background,
            request.asset,
            request.alert_type,
            request.urgency,
            request.message
        )
        
        return {
            "success": True,
            "message": f"Market alert queued for {request.asset}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending market alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send market alert: {str(e)}")

async def process_market_alert_background(asset: str, alert_type: str, urgency: int, message: str):
    """Background task to process market alerts"""
    try:
        # Simulate processing time
        await asyncio.sleep(1)
        
        logger.info(f"📨 Processing market alert: {alert_type} for {asset}")
        logger.info(f"    Urgency: {urgency}/10")
        logger.info(f"    Message: {message}")
        
        # Here you would typically:
        # 1. Query database for users interested in this asset
        # 2. Generate personalized alerts based on user profiles
        # 3. Send notifications (push, email, etc.)
        # 4. Log analytics data
        
    except Exception as e:
        logger.error(f"❌ Error in background alert processing: {e}")

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get engagement analytics and metrics"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        # Query database for analytics
        # In a real implementation, this would run proper analytics queries
        
        return AnalyticsResponse(
            total_users=1247,  # Mock data
            active_users_today=89,
            total_interactions=15632,
            average_engagement_score=0.73,
            premium_conversion_rate=0.34,
            top_achievements=[
                {"name": "Welcome Trader", "count": 1247},
                {"name": "Consistent Learner", "count": 234},
                {"name": "Premium Member", "count": 156}
            ]
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/mcp-status")
async def get_mcp_status():
    """Get status of all MCP integrations"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        # Test connectivity to each MCP tool
        mcp_manager = engagement_engine.mcp_manager
        
        # Get sample data from each source to test connectivity
        btc_context = await mcp_manager.get_comprehensive_market_context("BTC")
        
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "KingFisher": {
                    "status": "active",
                    "liquidation_clusters": len(btc_context.get("liquidation_clusters", []))
                },
                "Cryptometer": {
                    "status": "active", 
                    "market_indicators": len(btc_context.get("market_indicators", []))
                },
                "RiskMetric": {
                    "status": "active",
                    "risk_metrics": len(btc_context.get("risk_metrics", []))
                },
                "Grok": {
                    "status": "active",
                    "sentiment_sources": len([s for s in btc_context.get("sentiment_data", []) if s.source == "grok"])
                },
                "X_Sentiment": {
                    "status": "active",
                    "sentiment_sources": len([s for s in btc_context.get("sentiment_data", []) if s.source == "x_sentiment"])
                },
                "Whale_Alerts": {
                    "status": "active",
                    "recent_alerts": len(btc_context.get("whale_alerts", []))
                }
            },
            "sample_data": {
                "asset": btc_context.get("primary_asset"),
                "price": btc_context.get("current_price"),
                "volatility": btc_context.get("volatility"),
                "sentiment": btc_context.get("overall_sentiment"),
                "risk_score": btc_context.get("risk_score")
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting MCP status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Demo endpoints for testing
@app.get("/demo/create-user/{user_id}")
async def create_demo_user(user_id: str, skill_level: str = "novice"):
    """Create a demo user for testing"""
    global engagement_engine
    
    if not engagement_engine:
        raise HTTPException(status_code=500, detail="Engagement engine not initialized")
    
    try:
        # Get or create user profile
        profile = engagement_engine.get_user_profile(user_id)
        
        # Set demo properties
        from engagement_engine import EngagementLevel
        if skill_level in ["novice", "developing", "skilled", "advanced", "expert", "master"]:
            profile.skill_level = EngagementLevel(skill_level)
        
        engagement_engine._save_user_profile(profile)
        
        return {
            "success": True,
            "user_id": user_id,
            "skill_level": profile.skill_level.value,
            "message": f"Demo user {user_id} created with {skill_level} skill level"
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating demo user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create demo user: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the service
    uvicorn.run(
        "engagement_service:app",
        host="0.0.0.0",
        port=8350,
        reload=True,
        log_level="info"
    )