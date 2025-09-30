#!/usr/bin/env python3
"""
ZmartBot Reliable Server
Simple, stable server that bypasses all initialization issues
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot Reliable API",
    description="Stable API server for ZmartBot Trading Platform",
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

# Global health status
health_status = {
    "start_time": time.time(),
    "requests_processed": 0,
    "last_request": None
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZmartBot Trading Platform API",
        "version": "1.0.0",
        "status": "operational",
        "server": "reliable"
    }

@app.get("/health")
async def health():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "service": "zmart-reliable",
        "version": "1.0.0",
        "uptime": time.time() - health_status["start_time"],
        "requests_processed": health_status["requests_processed"],
        "last_request": health_status["last_request"],
        "timestamp": time.time()
    }

@app.get("/api/v1/test")
async def test_api():
    """Test API endpoint"""
    return {
        "message": "API is working",
        "status": "success",
        "timestamp": time.time()
    }

@app.get("/api/v1/status")
async def status():
    """System status endpoint"""
    return {
        "system": "ZmartBot Trading Platform",
        "status": "operational",
        "components": {
            "api_server": "healthy",
            "database": "development_mode",
            "monitoring": "enabled"
        },
        "timestamp": time.time()
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to track requests"""
    start_time = time.time()
    
    # Update health status
    health_status["requests_processed"] += 1
    health_status["last_request"] = start_time
    
    # Process request
    response = await call_next(request)
    
    # Add timing header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(f"Request: {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    print("🚀 Starting ZmartBot Reliable Server...")
    print("📍 Server: http://0.0.0.0:8000")
    print("📍 Health: http://0.0.0.0:8000/health")
    print("📍 Status: http://0.0.0.0:8000/api/v1/status")
    print("📍 Docs: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 