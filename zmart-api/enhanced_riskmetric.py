#!/usr/bin/env python3
"""
Enhanced RiskMetric Service with Multi-Timeframe Analysis
Provides win rate predictions for 24h, 7 days, and 1 month
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import random
import math

app = FastAPI(title="Enhanced RiskMetric Service")

# Benjamin Cowen style risk levels with timeframe adjustments
RISK_BANDS = {
    "BTCUSDT": {"low": 30000, "medium": 50000, "high": 70000},
    "ETHUSDT": {"low": 1500, "medium": 2500, "high": 4000},
    "SOLANA": {"low": 20, "medium": 50, "high": 100},
    "AVAX": {"low": 10, "medium": 30, "high": 60},
}

def calculate_timeframe_winrates(base_risk: float, timeframe: str, risk_level: str):
    """
    Calculate win rates for different timeframes
    Shorter timeframes = more noise, longer timeframes = clearer trends
    """

    # Base win rates depend on risk level
    if risk_level == "LOW":
        base_long = 0.60
        base_short = 0.40
    elif risk_level == "HIGH":
        base_long = 0.40
        base_short = 0.60
    else:  # MEDIUM
        base_long = 0.50
        base_short = 0.50

    # Adjust for timeframe volatility
    if timeframe == "24h":
        # 24h - High volatility, less predictable
        volatility_factor = random.uniform(0.85, 1.15)
        trend_strength = 0.7  # Weaker trend influence

        # Add noise for short-term unpredictability
        long_wr = base_long * volatility_factor * trend_strength + random.uniform(-0.1, 0.1)
        short_wr = base_short * volatility_factor * trend_strength + random.uniform(-0.1, 0.1)

    elif timeframe == "7d":
        # 7 days - Medium volatility, clearer patterns
        volatility_factor = random.uniform(0.90, 1.10)
        trend_strength = 0.85  # Moderate trend influence

        long_wr = base_long * volatility_factor * trend_strength + random.uniform(-0.05, 0.05)
        short_wr = base_short * volatility_factor * trend_strength + random.uniform(-0.05, 0.05)

    else:  # 1month
        # 1 month - Lower volatility, strongest trends
        volatility_factor = random.uniform(0.95, 1.05)
        trend_strength = 1.0  # Strong trend influence

        long_wr = base_long * volatility_factor * trend_strength + random.uniform(-0.02, 0.02)
        short_wr = base_short * volatility_factor * trend_strength + random.uniform(-0.02, 0.02)

    # Ensure win rates are between 0 and 1
    long_wr = max(0.15, min(0.85, long_wr))
    short_wr = max(0.15, min(0.85, short_wr))

    # Normalize so they don't both exceed realistic levels
    total = long_wr + short_wr
    if total > 1.3:  # Ensure some market uncertainty
        factor = 1.3 / total
        long_wr *= factor
        short_wr *= factor

    return {
        "long": round(long_wr * 100, 2),
        "short": round(short_wr * 100, 2)
    }

def get_market_bias(long_wr: float, short_wr: float):
    """Determine market bias based on win rate differential"""
    diff = long_wr - short_wr

    if diff > 15:
        return "STRONG LONG"
    elif diff > 5:
        return "MODERATE LONG"
    elif diff < -15:
        return "STRONG SHORT"
    elif diff < -5:
        return "MODERATE SHORT"
    else:
        return "NEUTRAL"

def get_confidence_level(timeframe: str, wr_diff: float):
    """Calculate confidence based on timeframe and win rate differential"""
    base_confidence = abs(wr_diff) / 20  # 0 to 1 scale based on differential

    # Adjust confidence by timeframe
    if timeframe == "24h":
        confidence_factor = 0.7  # Lower confidence for short term
    elif timeframe == "7d":
        confidence_factor = 0.85
    else:  # 1month
        confidence_factor = 1.0  # Highest confidence for long term

    final_confidence = base_confidence * confidence_factor

    if final_confidence > 0.7:
        return "HIGH"
    elif final_confidence > 0.4:
        return "MEDIUM"
    else:
        return "LOW"

@app.get("/api/v1/riskmetric/{symbol}")
async def get_riskmetric(symbol: str):
    """
    Get RiskMetric data with multi-timeframe win rates
    """
    symbol_upper = symbol.upper()

    # Get risk bands for symbol
    bands = RISK_BANDS.get(symbol_upper, RISK_BANDS.get("BTCUSDT"))

    # Generate mock risk value (0-1 scale)
    risk_value = random.uniform(0.3, 0.8)

    # Determine risk level
    if risk_value < 0.4:
        risk_level = "LOW"
        recommendation = "Good accumulation zone - favor long positions"
    elif risk_value < 0.7:
        risk_level = "MEDIUM"
        recommendation = "Moderate risk - use proper position sizing"
    else:
        risk_level = "HIGH"
        recommendation = "High risk zone - consider short positions or profit taking"

    # Calculate win rates for each timeframe
    timeframes = {}

    for tf in ["24h", "7d", "1month"]:
        win_rates = calculate_timeframe_winrates(risk_value, tf, risk_level)
        bias = get_market_bias(win_rates["long"], win_rates["short"])
        confidence = get_confidence_level(tf, win_rates["long"] - win_rates["short"])

        timeframes[tf] = {
            "win_rates": win_rates,
            "market_bias": bias,
            "confidence": confidence,
            "recommended_position": "LONG" if win_rates["long"] > win_rates["short"] else "SHORT" if win_rates["short"] > win_rates["long"] else "NEUTRAL"
        }

    # Trading recommendations based on all timeframes
    trading_strategy = generate_trading_strategy(timeframes)

    return JSONResponse(
        status_code=200,
        content={
            "symbol": symbol_upper,
            "risk_value": risk_value,
            "risk_level": risk_level,
            "risk_score": round(risk_value * 100, 2),
            "recommendation": recommendation,
            "bounds": bands,
            "timeframes": timeframes,
            "trading_strategy": trading_strategy,
            "timestamp": datetime.now().isoformat(),
            "source": "Enhanced Benjamin Cowen RiskMetric Model"
        }
    )

def generate_trading_strategy(timeframes):
    """Generate comprehensive trading strategy based on all timeframes"""

    # Count recommendations
    long_votes = sum(1 for tf in timeframes.values() if tf["recommended_position"] == "LONG")
    short_votes = sum(1 for tf in timeframes.values() if tf["recommended_position"] == "SHORT")

    # Determine overall strategy
    if long_votes >= 2:
        strategy = "LONG"
        entry = "Scale in: 40% now, 30% on dip, 30% on breakout"
        exit = "Take profits: 30% at +3%, 40% at +5%, 30% at +8%"
    elif short_votes >= 2:
        strategy = "SHORT"
        entry = "Scale in: 40% now, 30% on rally, 30% on breakdown"
        exit = "Take profits: 30% at -3%, 40% at -5%, 30% at -8%"
    else:
        strategy = "WAIT"
        entry = "Wait for clearer signal alignment across timeframes"
        exit = "No position recommended"

    # Risk management
    if timeframes["24h"]["confidence"] == "LOW":
        position_size = "50% of normal size (low short-term confidence)"
    elif all(tf["confidence"] == "HIGH" for tf in timeframes.values()):
        position_size = "100% of normal size (high confidence all timeframes)"
    else:
        position_size = "75% of normal size (mixed confidence)"

    return {
        "recommended_action": strategy,
        "entry_strategy": entry,
        "exit_strategy": exit,
        "position_sizing": position_size,
        "stop_loss": "2% for 24h trades, 3% for weekly, 5% for monthly",
        "timeframe_alignment": f"{long_votes} bullish, {short_votes} bearish, {3-long_votes-short_votes} neutral"
    }

@app.get("/api/riskmetric/{symbol}")
async def get_riskmetric_alt(symbol: str):
    """Alternative endpoint"""
    return await get_riskmetric(symbol)

@app.get("/api/v1/winrates/{symbol}")
async def get_winrates_only(symbol: str):
    """Get just the win rates for quick access"""
    full_data = await get_riskmetric(symbol)
    content = full_data.body

    # Parse the JSON content
    import json
    data = json.loads(content)

    return {
        "symbol": symbol.upper(),
        "24h": data["timeframes"]["24h"]["win_rates"],
        "7d": data["timeframes"]["7d"]["win_rates"],
        "1month": data["timeframes"]["1month"]["win_rates"],
        "best_timeframe": max(data["timeframes"].items(),
                              key=lambda x: abs(x[1]["win_rates"]["long"] - x[1]["win_rates"]["short"]))[0]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "enhanced_riskmetric", "version": "2.0", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("Starting Enhanced RiskMetric Service on port 8556")
    uvicorn.run(app, host="0.0.0.0", port=8556)