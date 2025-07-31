#!/usr/bin/env python3
"""
Simple test server for ZmartBot API
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="ZmartBot Test API")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "zmart-test"}

@app.get("/")
async def root():
    return {"message": "ZmartBot API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 