"""
Engagement System Integration Router
Proxies requests to the engagement system service and provides unified API access
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import aiohttp
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Service configuration
ENGAGEMENT_SERVICE_URL = "http://localhost:8350"

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

async def proxy_request(method: str, endpoint: str, json_data: Dict = None, timeout: int = 30) -> Dict:
    """Proxy request to engagement service"""
    url = f"{ENGAGEMENT_SERVICE_URL}{endpoint}"
    
    try:
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise HTTPException(status_code=response.status, detail=error_text)
            
            elif method.upper() == "POST":
                async with session.post(url, json=json_data, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise HTTPException(status_code=response.status, detail=error_text)
                        
    except aiohttp.ClientTimeout:
        raise HTTPException(status_code=504, detail="Engagement service timeout")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=503, detail=f"Engagement service unavailable: {str(e)}")

@router.get("/engagement/health")
async def engagement_health():
    """Check engagement system health"""
    try:
        result = await proxy_request("GET", "/health")
        return {
            "service": "engagement-proxy",
            "upstream": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "service": "engagement-proxy", 
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/engagement/interact")
async def chat_interaction(request: ChatRequest):
    """Chat interaction with Zmarty AI mentor"""
    try:
        result = await proxy_request("POST", "/interact", request.dict())
        
        # Log the interaction for analytics
        logger.info(f"Engagement interaction - User: {request.user_id}, Asset: {request.asset}, Score: {result.get('engagement_score', 0):.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Engagement interaction failed: {e}")
        raise

@router.post("/engagement/unlock-premium")
async def unlock_premium_content(request: PremiumUnlockRequest):
    """Unlock premium content with credits"""
    try:
        result = await proxy_request("POST", "/unlock-premium", request.dict())
        
        # Log premium unlock for analytics
        logger.info(f"Premium unlock - User: {request.user_id}, Tier: {request.content_tier}, Credits: {request.credits_spent}")
        
        return result
        
    except Exception as e:
        logger.error(f"Premium unlock failed: {e}")
        raise

@router.get("/engagement/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user engagement profile"""
    try:
        result = await proxy_request("GET", f"/user/{user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        raise

@router.post("/engagement/market-alert")
async def send_market_alert(request: MarketAlertRequest, background_tasks: BackgroundTasks):
    """Send market alert through engagement system"""
    try:
        result = await proxy_request("POST", "/market-alert", request.dict())
        
        # Log market alert
        logger.info(f"Market alert sent - Asset: {request.asset}, Type: {request.alert_type}, Urgency: {request.urgency}")
        
        return result
        
    except Exception as e:
        logger.error(f"Market alert failed: {e}")
        raise

@router.get("/engagement/analytics")
async def get_engagement_analytics():
    """Get engagement system analytics"""
    try:
        result = await proxy_request("GET", "/analytics")
        return result
        
    except Exception as e:
        logger.error(f"Get analytics failed: {e}")
        raise

@router.get("/engagement/mcp-status")
async def get_mcp_status():
    """Get MCP integration status"""
    try:
        result = await proxy_request("GET", "/mcp-status")
        return result
        
    except Exception as e:
        logger.error(f"Get MCP status failed: {e}")
        raise

@router.get("/engagement/demo/create-user/{user_id}")
async def create_demo_user(user_id: str, skill_level: str = "novice"):
    """Create demo user for testing"""
    try:
        result = await proxy_request("GET", f"/demo/create-user/{user_id}?skill_level={skill_level}")
        return result
        
    except Exception as e:
        logger.error(f"Create demo user failed: {e}")
        raise

# Integration endpoints for connecting with existing zmart services
@router.post("/engagement/integrate/signal")
async def integrate_with_signal(signal_data: Dict[str, Any]):
    """Integrate engagement system with trading signals"""
    try:
        # Extract relevant info from signal
        asset = signal_data.get("symbol", "BTC").replace("USDT", "")
        signal_type = signal_data.get("type", "unknown")
        score = signal_data.get("score", 0)
        
        # Create alert request
        alert_request = MarketAlertRequest(
            asset=asset,
            alert_type=f"trading_signal_{signal_type}",
            urgency=min(10, max(1, int(score * 10))),  # Convert score to urgency
            message=f"New {signal_type} signal for {asset} with score {score}"
        )
        
        # Send to engagement system
        result = await proxy_request("POST", "/market-alert", alert_request.dict())
        
        return {
            "success": True,
            "message": "Signal integrated with engagement system",
            "alert_sent": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Signal integration failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "alert_sent": False
        }

@router.post("/engagement/integrate/pool-update")
async def integrate_with_pool_update(pool_data: Dict[str, Any]):
    """Integrate engagement system with pool updates"""
    try:
        pool_id = pool_data.get("id")
        status = pool_data.get("status")
        symbol = pool_data.get("symbol", "BTC")
        
        if status in ["expired", "liquidated", "closed"]:
            alert_request = MarketAlertRequest(
                asset=symbol,
                alert_type=f"pool_{status}",
                urgency=7 if status == "liquidated" else 5,
                message=f"Pool {pool_id} has been {status}"
            )
            
            result = await proxy_request("POST", "/market-alert", alert_request.dict())
            
            return {
                "success": True,
                "message": f"Pool {status} integrated with engagement system",
                "result": result
            }
        
        return {
            "success": True,
            "message": "Pool update noted, no engagement action needed"
        }
        
    except Exception as e:
        logger.error(f"Pool integration failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }