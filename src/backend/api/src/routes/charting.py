#!/usr/bin/env python3
"""
Charting Routes
Chart data and visualization endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta

from src.services.charting_service import get_charting_service, ChartData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/charting", tags=["charting"])

class ChartRequest(BaseModel):
    """Chart request model"""
    symbol: str
    interval: str = "1h"
    theme: str = "dark"
    indicators: Optional[List[str]] = None
    studies: Optional[List[str]] = None

class ChartResponse(BaseModel):
    """Chart response model"""
    symbol: str
    interval: str
    html: str
    data: Optional[Dict[str, Any]] = None

class MultiTimeframeRequest(BaseModel):
    """Multi-timeframe chart request"""
    symbol: str
    timeframes: List[str] = ["5m", "1h", "4h", "1d"]
    theme: str = "dark"

class PortfolioChartsRequest(BaseModel):
    """Portfolio charts request"""
    symbols: List[str]
    interval: str = "1h"
    theme: str = "dark"

@router.get("/basic/{symbol}")
async def get_basic_chart(
    symbol: str,
    interval: str = Query("1h", description="Chart interval"),
    theme: str = Query("dark", description="Chart theme")
) -> ChartResponse:
    """Get basic TradingView chart"""
    try:
        charting_service = get_charting_service()
        html = charting_service.get_basic_chart(symbol, interval, theme)
        
        return ChartResponse(
            symbol=symbol,
            interval=interval,
            html=html
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting basic chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading chart: {str(e)}")

@router.post("/advanced")
async def get_advanced_chart(request: ChartRequest) -> ChartResponse:
    """Get advanced TradingView chart with custom indicators"""
    try:
        charting_service = get_charting_service()
        html = charting_service.get_advanced_chart(
            request.symbol,
            request.interval,
            request.theme,
            request.indicators,
            request.studies
        )
        
        return ChartResponse(
            symbol=request.symbol,
            interval=request.interval,
            html=html
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting advanced chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading advanced chart: {str(e)}")

@router.post("/multi-timeframe")
async def get_multi_timeframe_charts(request: MultiTimeframeRequest) -> Dict[str, ChartResponse]:
    """Get multiple timeframe charts for a symbol"""
    try:
        charting_service = get_charting_service()
        charts = charting_service.get_multi_timeframe_charts(request.symbol, request.timeframes)
        
        responses = {}
        for timeframe, html in charts.items():
            responses[timeframe] = ChartResponse(
                symbol=request.symbol,
                interval=timeframe,
                html=html
            )
        
        return responses
        
    except Exception as e:
        logger.error(f"❌ Error getting multi-timeframe charts: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading multi-timeframe charts: {str(e)}")

@router.post("/portfolio")
async def get_portfolio_charts(request: PortfolioChartsRequest) -> Dict[str, ChartResponse]:
    """Get charts for multiple symbols in portfolio"""
    try:
        charting_service = get_charting_service()
        charts = charting_service.get_portfolio_charts(request.symbols, request.interval)
        
        responses = {}
        for symbol, html in charts.items():
            responses[symbol] = ChartResponse(
                symbol=symbol,
                interval=request.interval,
                html=html
            )
        
        return responses
        
    except Exception as e:
        logger.error(f"❌ Error getting portfolio charts: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading portfolio charts: {str(e)}")

@router.get("/technical/{symbol}")
async def get_technical_analysis_chart(
    symbol: str,
    indicators: Optional[List[str]] = Query(None, description="Technical indicators")
) -> ChartResponse:
    """Get chart with technical analysis indicators"""
    try:
        charting_service = get_charting_service()
        html = charting_service.get_technical_analysis_chart(symbol, indicators)
        
        return ChartResponse(
            symbol=symbol,
            interval="1h",
            html=html
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting technical analysis chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading technical analysis chart: {str(e)}")

@router.get("/signal/{symbol}")
async def get_signal_chart(symbol: str) -> ChartResponse:
    """Get chart with trading signals overlay"""
    try:
        charting_service = get_charting_service()
        html = charting_service.get_signal_chart(symbol)
        
        return ChartResponse(
            symbol=symbol,
            interval="1h",
            html=html
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting signal chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading signal chart: {str(e)}")

@router.get("/data/{symbol}")
async def get_chart_data(
    symbol: str,
    interval: str = Query("1h", description="Chart interval")
) -> Dict[str, Any]:
    """Get chart data with indicators and signals"""
    try:
        charting_service = get_charting_service()
        chart_data = charting_service.get_chart_data(symbol, interval)
        
        return {
            "symbol": chart_data.symbol,
            "timeframe": chart_data.timeframe,
            "indicators": chart_data.indicators,
            "signals": chart_data.signals,
            "timestamp": chart_data.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading chart data: {str(e)}")

@router.get("/test/{symbol}", response_class=HTMLResponse)
async def get_chart_test_page(symbol: str = "BTCUSDT") -> str:
    """Get test page for charting functionality"""
    try:
        charting_service = get_charting_service()
        html = charting_service.get_basic_chart(symbol, "1h", "dark")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ZmartBot Charting Test - {symbol}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background: #1a1a1a;
                    color: #fff;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .chart-container {{
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px 0;
                }}
                .controls {{
                    margin: 20px 0;
                    padding: 15px;
                    background: #2a2a2a;
                    border-radius: 5px;
                }}
                select, button {{
                    padding: 8px 12px;
                    margin: 5px;
                    border: none;
                    border-radius: 3px;
                    background: #4CAF50;
                    color: white;
                    cursor: pointer;
                }}
                button:hover {{
                    background: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 ZmartBot Charting Test</h1>
                    <h2>Symbol: {symbol}</h2>
                </div>
                
                <div class="controls">
                    <label>Symbol:</label>
                    <input type="text" id="symbol" value="{symbol}" style="padding: 8px; margin: 5px;">
                    
                    <label>Interval:</label>
                    <select id="interval">
                        <option value="1m">1m</option>
                        <option value="5m">5m</option>
                        <option value="15m">15m</option>
                        <option value="30m">30m</option>
                        <option value="1h" selected>1h</option>
                        <option value="4h">4h</option>
                        <option value="1d">1d</option>
                    </select>
                    
                    <label>Theme:</label>
                    <select id="theme">
                        <option value="dark" selected>Dark</option>
                        <option value="light">Light</option>
                    </select>
                    
                    <button onclick="loadChart()">Load Chart</button>
                    <button onclick="loadTechnical()">Technical Analysis</button>
                    <button onclick="loadSignals()">Signal Chart</button>
                </div>
                
                <div class="chart-container">
                    <div id="chart-container">
                        {html}
                    </div>
                </div>
            </div>
            
            <script>
                function loadChart() {{
                    const symbol = document.getElementById('symbol').value;
                    const interval = document.getElementById('interval').value;
                    const theme = document.getElementById('theme').value;
                    
                    fetch(`/api/v1/charting/basic/${{symbol}}?interval=${{interval}}&theme=${{theme}}`)
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('chart-container').innerHTML = data.html;
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            document.getElementById('chart-container').innerHTML = '<div>Error loading chart</div>';
                        }});
                }}
                
                function loadTechnical() {{
                    const symbol = document.getElementById('symbol').value;
                    
                    fetch(`/api/v1/charting/technical/${{symbol}}`)
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('chart-container').innerHTML = data.html;
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            document.getElementById('chart-container').innerHTML = '<div>Error loading technical chart</div>';
                        }});
                }}
                
                function loadSignals() {{
                    const symbol = document.getElementById('symbol').value;
                    
                    fetch(`/api/v1/charting/signal/${{symbol}}`)
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('chart-container').innerHTML = data.html;
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            document.getElementById('chart-container').innerHTML = '<div>Error loading signal chart</div>';
                        }});
                }}
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        logger.error(f"❌ Error generating test page: {e}")
        return f"<div>Error generating test page: {str(e)}</div>"

@router.get("/supported-symbols")
async def get_supported_symbols() -> Dict[str, Any]:
    """Get list of supported symbols"""
    try:
        charting_service = get_charting_service()
        symbols = list(charting_service.tradingview.supported_symbols.keys())
        
        return {
            "symbols": symbols,
            "count": len(symbols)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting supported symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting supported symbols: {str(e)}")

@router.get("/supported-timeframes")
async def get_supported_timeframes() -> Dict[str, Any]:
    """Get list of supported timeframes"""
    try:
        charting_service = get_charting_service()
        timeframes = list(charting_service.tradingview.supported_timeframes.keys())
        
        return {
            "timeframes": timeframes,
            "count": len(timeframes)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting supported timeframes: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting supported timeframes: {str(e)}") 