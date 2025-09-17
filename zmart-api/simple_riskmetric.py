#!/usr/bin/env python3
"""
Simple RiskMetric Service for Testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import random

app = FastAPI(title="Simple RiskMetric Service")

# Benjamin Cowen style risk levels
RISK_BANDS = {
    "BTCUSDT": {"low": 30000, "medium": 50000, "high": 70000},
    "ETHUSDT": {"low": 1500, "medium": 2500, "high": 4000},
    "BTC": {"low": 30000, "medium": 50000, "high": 70000},
    "ETH": {"low": 1500, "medium": 2500, "high": 4000},
    "SOLANA": {"low": 20, "medium": 50, "high": 100},
    "AVAX": {"low": 10, "medium": 30, "high": 60},
}

@app.get("/api/v1/riskmetric/{symbol}")
async def get_riskmetric(symbol: str):
    """
    Get RiskMetric data for a symbol
    """
    symbol_upper = symbol.upper()

    # Check if symbol exists
    bands = RISK_BANDS.get(symbol_upper, RISK_BANDS.get("BTCUSDT"))

    # Generate mock risk value (0-1 scale)
    risk_value = random.uniform(0.3, 0.8)

    # Determine risk level
    if risk_value < 0.4:
        risk_level = "LOW"
        recommendation = "Good accumulation zone"
    elif risk_value < 0.7:
        risk_level = "MEDIUM"
        recommendation = "Moderate risk, consider partial positions"
    else:
        risk_level = "HIGH"
        recommendation = "High risk zone, consider taking profits"

    return JSONResponse(
        status_code=200,
        content={
            "symbol": symbol_upper,
            "risk_value": risk_value,
            "risk_level": risk_level,
            "risk_score": round(risk_value * 100, 2),
            "recommendation": recommendation,
            "bounds": bands,
            "timestamp": datetime.now().isoformat(),
            "source": "Benjamin Cowen RiskMetric Model"
        }
    )

@app.get("/api/riskmetric/{symbol}")
async def get_riskmetric_alt(symbol: str):
    """Alternative endpoint"""
    return await get_riskmetric(symbol)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "riskmetric", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("Starting Simple RiskMetric Service on port 8556")
    uvicorn.run(app, host="0.0.0.0", port=8556)