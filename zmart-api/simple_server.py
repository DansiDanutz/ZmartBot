#!/usr/bin/env python3
"""
Simple ZmartBot API Server for testing
"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="ZmartBot Simple API")

@app.get("/")
async def root():
    return {"message": "ZmartBot API is running!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
