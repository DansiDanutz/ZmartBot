#!/usr/bin/env python3
"""
Minimal KingFisher server for testing
"""
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KingFisher Minimal Server",
    description="Minimal version for testing",
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "kingfisher",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "telegram": True,
            "image_processor": True,
            "liquidation": True
        }
    }

@app.get("/api/v1/telegram/status")
async def telegram_status():
    """Telegram status endpoint"""
    return {
        "connected": True,
        "monitoring": True,
        "status": "active"
    }

@app.post("/api/v1/telegram/test-connection")
async def test_telegram_connection():
    """Test Telegram connection"""
    return {
        "connected": True,
        "bot_token_valid": True,
        "chat_id_valid": True,
        "monitoring_ready": True,
        "automation_enabled": True
    }

@app.post("/api/v1/telegram/start-monitoring")
async def start_telegram_monitoring():
    """Start Telegram monitoring"""
    return {
        "success": True,
        "message": "Monitoring started successfully"
    }

@app.get("/api/v1/telegram/monitoring-status")
async def telegram_monitoring_status():
    """Get Telegram monitoring status"""
    return {
        "connected": True,
        "monitoring": True
    }

@app.get("/api/v1/airtable/status")
async def airtable_status():
    """Airtable status endpoint"""
    return {
        "connected": True,
        "status": "ready"
    }

@app.get("/api/v1/images/status")
async def images_status():
    """Image processing status endpoint"""
    return {
        "ready": True,
        "status": "active"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KingFisher Minimal Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100) 