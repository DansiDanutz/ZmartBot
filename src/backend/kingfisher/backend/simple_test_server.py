#!/usr/bin/env python3
"""
Simple test server to verify basic functionality
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="KingFisher Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Test server is running"}

@app.get("/")
async def root():
    return {"message": "KingFisher Test Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100) 