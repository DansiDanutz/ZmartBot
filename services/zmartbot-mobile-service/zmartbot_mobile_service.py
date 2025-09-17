#!/usr/bin/env python3
"""
ZmartBot Mobile App Service
Port: 7777 (RESERVED - NO EXCEPTIONS)
Purpose: Mobile app backend service for React Native app integration
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import requests
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zmartbot_mobile_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Service Configuration
SERVICE_NAME = "zmartbot-mobile-service"
SERVICE_PORT = 7777  # RESERVED PORT - NO EXCEPTIONS
SERVICE_VERSION = "1.0.0"
SERVICE_OWNER = "zmartbot"

# ZmartBot Ecosystem Integration
ZMART_API_BASE_URL = "http://localhost:8000"
MASTER_ORCHESTRATION_URL = "http://localhost:8002"
PORT_MANAGER_URL = "http://localhost:8050"

class MobileAppConfig(BaseModel):
    """Mobile app service configuration"""
    service_name: str = SERVICE_NAME
    service_port: int = SERVICE_PORT
    service_version: str = SERVICE_VERSION
    service_owner: str = SERVICE_OWNER
    zmart_api_url: str = ZMART_API_BASE_URL
    master_orchestration_url: str = MASTER_ORCHESTRATION_URL
    port_manager_url: str = PORT_MANAGER_URL

class MarketDataRequest(BaseModel):
    """Market data request model"""
    symbols: List[str] = Field(default_factory=list)
    exchange: str = "binance"
    timeframe: str = "1h"
    limit: int = 100

class PortfolioRequest(BaseModel):
    """Portfolio request model"""
    user_id: Optional[str] = None
    include_positions: bool = True
    include_history: bool = False

class TradingSignalRequest(BaseModel):
    """Trading signal request model"""
    symbol: str
    timeframe: str = "1h"
    include_analysis: bool = True

class IoTDeviceRequest(BaseModel):
    """IoT device request model"""
    device_type: Optional[str] = None
    include_data: bool = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifecycle management"""
    logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
    
    # Register with Port Manager
    try:
        await register_with_port_manager()
        logger.info("✅ Successfully registered with Port Manager")
    except Exception as e:
        logger.error(f"❌ Failed to register with Port Manager: {e}")
    
    # Register with Master Orchestration
    try:
        await register_with_master_orchestration()
        logger.info("✅ Successfully registered with Master Orchestration")
    except Exception as e:
        logger.error(f"❌ Failed to register with Master Orchestration: {e}")
    
    yield
    
    logger.info(f"🛑 Shutting down {SERVICE_NAME}")

# Initialize FastAPI app
app = FastAPI(
    title=f"{SERVICE_NAME}",
    description=f"Mobile app backend service for ZmartBot ecosystem - Port {SERVICE_PORT}",
    version=SERVICE_VERSION,
    lifespan=lifespan
)

# Add CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service health endpoint
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "port": SERVICE_PORT,
        "version": SERVICE_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "zmart_api_connected": await check_zmart_api_connection()
    }

# Service info endpoint
@app.get("/")
async def service_info():
    """Service information"""
    return {
        "service": SERVICE_NAME,
        "description": "Mobile app backend service for ZmartBot ecosystem",
        "port": SERVICE_PORT,
        "version": SERVICE_VERSION,
        "owner": SERVICE_OWNER,
        "endpoints": {
            "health": "/health",
            "market_data": "/api/market-data",
            "portfolio": "/api/portfolio",
            "trading_signals": "/api/trading-signals",
            "iot_devices": "/api/iot-devices",
            "zmart_integration": "/api/zmart-integration"
        }
    }

async def check_zmart_api_connection() -> bool:
    """Check connection to main ZmartBot API"""
    try:
        response = requests.get(f"{ZMART_API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

async def register_with_port_manager():
    """Register service with Port Manager"""
    try:
        registration_data = {
            "service_name": SERVICE_NAME,
            "service_type": "mobile-backend",
            "port": SERVICE_PORT,
            "version": SERVICE_VERSION,
            "owner": SERVICE_OWNER,
            "endpoints": [
                f"http://localhost:{SERVICE_PORT}/health",
                f"http://localhost:{SERVICE_PORT}/"
            ]
        }
        
        response = requests.post(
            f"{PORT_MANAGER_URL}/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Port Manager registration successful: {response.json()}")
        else:
            logger.warning(f"⚠️ Port Manager registration returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Port Manager registration failed: {e}")
        raise

async def register_with_master_orchestration():
    """Register service with Master Orchestration Agent"""
    try:
        registration_data = {
            "service_name": SERVICE_NAME,
            "service_type": "mobile-backend",
            "port": SERVICE_PORT,
            "version": SERVICE_VERSION,
            "owner": SERVICE_OWNER,
            "capabilities": [
                "mobile_market_data",
                "mobile_portfolio",
                "mobile_trading_signals",
                "mobile_iot_integration"
            ]
        }
        
        response = requests.post(
            f"{MASTER_ORCHESTRATION_URL}/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Master Orchestration registration successful: {response.json()}")
        else:
            logger.warning(f"⚠️ Master Orchestration registration returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Master Orchestration registration failed: {e}")
        raise

# Mobile App API Endpoints

@app.get("/api/market-data")
async def get_market_data(request: MarketDataRequest = Depends()):
    """Get market data for mobile app"""
    try:
        # Integrate with zmart-api for real market data
        zmart_response = requests.get(
            f"{ZMART_API_BASE_URL}/api/market-data",
            params={
                "symbols": ",".join(request.symbols) if request.symbols else None,
                "exchange": request.exchange,
                "timeframe": request.timeframe,
                "limit": request.limit
            },
            timeout=10
        )
        
        if zmart_response.status_code == 200:
            market_data = zmart_response.json()
            return {
                "success": True,
                "data": market_data,
                "source": "zmart-api",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=zmart_response.status_code,
                detail="Failed to fetch market data from zmart-api"
            )
            
    except Exception as e:
        logger.error(f"Market data fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )

@app.get("/api/portfolio")
async def get_portfolio(request: PortfolioRequest = Depends()):
    """Get portfolio data for mobile app"""
    try:
        # Integrate with zmart-api for portfolio data
        zmart_response = requests.get(
            f"{ZMART_API_BASE_URL}/api/portfolio",
            params={
                "user_id": request.user_id,
                "include_positions": request.include_positions,
                "include_history": request.include_history
            },
            timeout=10
        )
        
        if zmart_response.status_code == 200:
            portfolio_data = zmart_response.json()
            return {
                "success": True,
                "data": portfolio_data,
                "source": "zmart-api",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=zmart_response.status_code,
                detail="Failed to fetch portfolio data from zmart-api"
            )
            
    except Exception as e:
        logger.error(f"Portfolio fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio data: {str(e)}"
        )

@app.get("/api/trading-signals")
async def get_trading_signals(request: TradingSignalRequest = Depends()):
    """Get trading signals for mobile app"""
    try:
        # Integrate with zmart-api for trading signals
        zmart_response = requests.get(
            f"{ZMART_API_BASE_URL}/api/trading-signals",
            params={
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "include_analysis": request.include_analysis
            },
            timeout=10
        )
        
        if zmart_response.status_code == 200:
            signals_data = zmart_response.json()
            return {
                "success": True,
                "data": signals_data,
                "source": "zmart-api",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=zmart_response.status_code,
                detail="Failed to fetch trading signals from zmart-api"
            )
            
    except Exception as e:
        logger.error(f"Trading signals fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trading signals: {str(e)}"
        )

@app.get("/api/iot-devices")
async def get_iot_devices(request: IoTDeviceRequest = Depends()):
    """Get IoT devices for mobile app"""
    try:
        # Integrate with zmart-api for IoT data
        zmart_response = requests.get(
            f"{ZMART_API_BASE_URL}/api/iot-devices",
            params={
                "device_type": request.device_type,
                "include_data": request.include_data
            },
            timeout=10
        )
        
        if zmart_response.status_code == 200:
            iot_data = zmart_response.json()
            return {
                "success": True,
                "data": iot_data,
                "source": "zmart-api",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=zmart_response.status_code,
                detail="Failed to fetch IoT data from zmart-api"
            )
            
    except Exception as e:
        logger.error(f"IoT data fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch IoT data: {str(e)}"
        )

@app.get("/api/zmart-integration")
async def get_zmart_integration_status():
    """Get ZmartBot ecosystem integration status"""
    try:
        # Check all ecosystem service connections
        zmart_api_status = await check_zmart_api_connection()
        
        # Check other services
        master_orchestration_status = False
        port_manager_status = False
        
        try:
            master_response = requests.get(f"{MASTER_ORCHESTRATION_URL}/health", timeout=5)
            master_orchestration_status = master_response.status_code == 200
        except:
            pass
            
        try:
            port_response = requests.get(f"{PORT_MANAGER_URL}/health", timeout=5)
            port_manager_status = port_response.status_code == 200
        except:
            pass
        
        return {
            "service": SERVICE_NAME,
            "port": SERVICE_PORT,
            "ecosystem_integration": {
                "zmart_api": zmart_api_status,
                "master_orchestration": master_orchestration_status,
                "port_manager": port_manager_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Integration status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check integration status: {str(e)}"
        )

if __name__ == "__main__":
    logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
    logger.info(f"📱 Mobile app service will be available at http://localhost:{SERVICE_PORT}")
    logger.info(f"🔗 Integrating with ZmartBot ecosystem at {ZMART_API_BASE_URL}")
    
    uvicorn.run(
        "zmartbot_mobile_service:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info"
    )
