#!/usr/bin/env python3
"""
GrokXAI Standalone Server
Level 3 Certified Service for Social Trading Intelligence
"""

import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.routes.grok_x import router as grok_x_router

# Create FastAPI app
app = FastAPI(
    title="GrokXAI - Social Trading Intelligence",
    description="Level 3 Certified AI-powered social media sentiment analysis and trading signal generation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include GrokX routes
app.include_router(grok_x_router, prefix="", tags=["grok-x"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GrokXAI",
        "version": "2.0.0",
        "status": "Level 3 CERTIFIED",
        "description": "AI-powered social media sentiment analysis and trading signal generation",
        "features": ["grok_ai", "x_api", "sentiment_analysis", "social_trading_signals"],
        "endpoints": {
            "health": "/grok-x/health",
            "analyze": "/grok-x/analyze",
            "signals": "/grok-x/signals",
            "monitor": "/grok-x/monitor",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "grok_x_server:app",
        host="0.0.0.0", 
        port=8113,
        reload=True,
        log_level="info"
    )