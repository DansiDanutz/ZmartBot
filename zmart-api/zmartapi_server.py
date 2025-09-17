#!/usr/bin/env python3
"""
🚀 ZmartAPI Main Server - Core API Gateway
Central API hub for the ZmartBot trading platform
"""

from fastapi import FastAPI, HTTPException
import uvicorn
import sqlite3
import json
from datetime import datetime

app = FastAPI(
    title="ZmartBot Core API",
    description="Central API gateway for ZmartBot trading platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ZmartAPI",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ZmartAPI",
        "port": 8000,
        "level": "LEVEL_3_CERTIFIED",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/services")
async def list_services():
    """List all registered services"""
    try:
        from src.config.database_config import get_master_database_connection
        conn = get_master_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT service_name, port, status FROM service_registry")
        services = []
        for row in cursor.fetchall():
            services.append({
                "name": row[0],
                "port": row[1],
                "status": row[2]
            })
        conn.close()
        return {"services": services, "count": len(services)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)