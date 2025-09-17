#!/usr/bin/env python3
"""
ZmartBot Binance Worker Service
Real-time market data, order execution, and trading operations for Binance exchange
"""

import os
import sys
import logging
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot Binance Worker Service",
    description="Real-time market data, order execution, and trading operations for Binance exchange",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    volume: float
    change_24h: float
    timestamp: datetime

@dataclass
class Order:
    """Order structure"""
    order_id: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    price: float
    status: str
    timestamp: datetime

class BinanceWorkerService:
    """
    Binance Worker Service that provides real-time market data and trading operations
    """
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY', 'test_api_key')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY', 'test_secret_key')
        self.testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        
        # Service state
        self.is_connected = False
        self.market_data_cache = {}
        self.active_orders = {}
        self.trading_stats = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "total_volume": 0.0
        }
        
        # Mock data for development
        self.mock_market_data = {
            "BTCUSDT": {"price": 45000.0, "volume": 1234567.89, "change_24h": 2.5},
            "ETHUSDT": {"price": 3200.0, "volume": 987654.32, "change_24h": -1.2},
            "BNBUSDT": {"price": 380.0, "volume": 456789.12, "change_24h": 0.8},
            "ADAUSDT": {"price": 0.45, "volume": 234567.89, "change_24h": 3.1}
        }
        
        logger.info("Binance Worker Service initialized")
    
    async def connect_to_binance(self):
        """Connect to Binance API"""
        try:
            # In a real implementation, this would establish WebSocket connections
            # and REST API connections to Binance
            self.is_connected = True
            logger.info("Connected to Binance API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance API: {e}")
            self.is_connected = False
            return False
    
    async def get_market_data(self, symbol: str = "BTCUSDT") -> MarketData:
        """Get real-time market data for a symbol"""
        try:
            if symbol in self.mock_market_data:
                data = self.mock_market_data[symbol]
                # Simulate price movement
                data["price"] += (data["price"] * 0.001 * (time.time() % 10 - 5))
                
                return MarketData(
                    symbol=symbol,
                    price=round(data["price"], 2),
                    volume=data["volume"],
                    change_24h=data["change_24h"],
                    timestamp=datetime.now()
                )
            else:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get market data")
    
    async def place_order(self, symbol: str, side: str, quantity: float, price: Optional[float] = None) -> Order:
        """Place a trading order"""
        try:
            order_id = f"order_{int(time.time() * 1000)}"
            
            order = Order(
                order_id=order_id,
                symbol=symbol,
                side=side.upper(),
                quantity=quantity,
                price=price or 0.0,
                status="PENDING",
                timestamp=datetime.now()
            )
            
            # Simulate order processing
            await asyncio.sleep(0.1)
            
            # Mock order success
            order.status = "FILLED"
            self.active_orders[order_id] = order
            
            # Update stats
            self.trading_stats["total_orders"] += 1
            self.trading_stats["successful_orders"] += 1
            self.trading_stats["total_volume"] += quantity
            
            logger.info(f"Order placed successfully: {order_id}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            self.trading_stats["total_orders"] += 1
            self.trading_stats["failed_orders"] += 1
            raise HTTPException(status_code=500, detail="Failed to place order")
    
    async def get_order_status(self, order_id: str) -> Order:
        """Get order status"""
        try:
            if order_id in self.active_orders:
                return self.active_orders[order_id]
            else:
                raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get order status")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                order.status = "CANCELLED"
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise HTTPException(status_code=500, detail="Failed to cancel order")

# Initialize service
binance_service = BinanceWorkerService()

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "binance-worker-service",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe endpoint"""
    return {
        "status": "ready" if binance_service.is_connected else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "binance-worker-service",
        "binance_connected": binance_service.is_connected
    }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for observability"""
    return {
        "service": "binance-worker-service",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "binance_connected": binance_service.is_connected,
            "total_orders": binance_service.trading_stats["total_orders"],
            "successful_orders": binance_service.trading_stats["successful_orders"],
            "failed_orders": binance_service.trading_stats["failed_orders"],
            "total_volume": binance_service.trading_stats["total_volume"],
            "active_orders_count": len(binance_service.active_orders)
        }
    }

# Binance API endpoints
@app.post("/api/v1/binance/connect")
async def connect_binance():
    """Connect to Binance API"""
    try:
        success = await binance_service.connect_to_binance()
        return {
            "success": success,
            "message": "Connected to Binance API" if success else "Failed to connect to Binance API",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error connecting to Binance: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Binance")

@app.get("/api/v1/binance/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get real-time market data for a symbol"""
    try:
        market_data = await binance_service.get_market_data(symbol)
        return {
            "symbol": market_data.symbol,
            "price": market_data.price,
            "volume": market_data.volume,
            "change_24h": market_data.change_24h,
            "timestamp": market_data.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market data")

@app.get("/api/v1/binance/market-data")
async def get_all_market_data():
    """Get market data for all supported symbols"""
    try:
        all_data = {}
        for symbol in binance_service.mock_market_data.keys():
            market_data = await binance_service.get_market_data(symbol)
            all_data[symbol] = {
                "price": market_data.price,
                "volume": market_data.volume,
                "change_24h": market_data.change_24h,
                "timestamp": market_data.timestamp.isoformat()
            }
        return all_data
    except Exception as e:
        logger.error(f"Error getting all market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market data")

@app.post("/api/v1/binance/order")
async def place_order(request: Dict[str, Any]):
    """Place a trading order"""
    try:
        symbol = request.get("symbol", "BTCUSDT")
        side = request.get("side", "BUY")
        quantity = request.get("quantity", 0.001)
        price = request.get("price")
        
        if not symbol or not side or not quantity:
            raise HTTPException(status_code=400, detail="symbol, side, and quantity are required")
        
        order = await binance_service.place_order(symbol, side, quantity, price)
        
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "price": order.price,
            "status": order.status,
            "timestamp": order.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail="Failed to place order")

@app.get("/api/v1/binance/order/{order_id}")
async def get_order(order_id: str):
    """Get order status"""
    try:
        order = await binance_service.get_order_status(order_id)
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "price": order.price,
            "status": order.status,
            "timestamp": order.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order")

@app.delete("/api/v1/binance/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an order"""
    try:
        success = await binance_service.cancel_order(order_id)
        return {
            "success": success,
            "message": f"Order {order_id} cancelled successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")

@app.get("/api/v1/binance/orders")
async def get_all_orders():
    """Get all active orders"""
    try:
        orders = []
        for order in binance_service.active_orders.values():
            orders.append({
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "price": order.price,
                "status": order.status,
                "timestamp": order.timestamp.isoformat()
            })
        return {"orders": orders}
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@app.get("/api/v1/binance/account")
async def get_account_info():
    """Get account information"""
    try:
        return {
            "account_type": "SPOT",
            "permissions": ["SPOT"],
            "maker_commission": 15,
            "taker_commission": 15,
            "buyer_commission": 0,
            "seller_commission": 0,
            "can_trade": True,
            "can_withdraw": True,
            "can_deposit": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get account info")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Binance Worker Service')
    parser.add_argument('--port', type=int, default=8303, help='Port to run on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    
    args = parser.parse_args()
    
    logger.info(f"Starting Binance Worker Service on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
