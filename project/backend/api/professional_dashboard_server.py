#!/usr/bin/env python3
"""
ZmartBot Professional Dashboard Server
Serves the complete trading platform dashboard with all features
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot Professional Dashboard",
    description="Complete Trading Platform with DBI Coefficient",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths - point to the frontend dashboard directory
dashboard_root = Path(__file__).parent.parent.parent / "frontend" / "dashboard"
dashboard_root.mkdir(exist_ok=True)

# Use the compiled dist directory for serving
dist_dir = dashboard_root / "dist"
assets_dir = dist_dir / "assets"
static_dir = dashboard_root / "static"
fusioncharts_dir = dashboard_root / "fusioncharts"

# Backend URL for API proxying
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Test pages (from start_dashboard.py)
@app.get("/test-proxy.html")
async def serve_test_proxy():
    """Serve the proxy test page"""
    test_file = dashboard_root / "test-proxy.html"
    if test_file.exists():
        return FileResponse(test_file, media_type="text/html")
    return JSONResponse({"error": "test-proxy.html not found"}, status_code=404)

@app.get("/test-backend-proxy.html")
async def serve_test_backend():
    """Serve the backend proxy test page"""
    test_file = dashboard_root / "test-backend-proxy.html"
    if test_file.exists():
        return FileResponse(test_file, media_type="text/html")
    return JSONResponse({"error": "test-backend-proxy.html not found"}, status_code=404)

# Try to import API routes
routes_loaded = []
routes_failed = []

try:
    from src.routes.my_symbols import router as my_symbols_router
    app.include_router(my_symbols_router, prefix="/api/v1", tags=["My Symbols"])
    routes_loaded.append("My Symbols")
except ImportError as e:
    logger.warning(f"⚠️ My Symbols API routes temporarily disabled - {e}")
    routes_failed.append(f"My Symbols: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ My Symbols API routes temporarily disabled - {e}")
    routes_failed.append(f"My Symbols: {str(e)}")

try:
    from src.routes.futures_symbols import router as futures_symbols_router
    app.include_router(futures_symbols_router, tags=["Futures Symbols"])
    routes_loaded.append("Futures Symbols")
except ImportError as e:
    logger.warning(f"⚠️ Futures Symbols API routes temporarily disabled - {e}")
    routes_failed.append(f"Futures Symbols: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ Futures Symbols API routes temporarily disabled - {e}")
    routes_failed.append(f"Futures Symbols: {str(e)}")

try:
    from src.routes.cryptometer import router as cryptometer_router
    app.include_router(cryptometer_router, tags=["Cryptometer"])
    routes_loaded.append("Cryptometer")
except ImportError as e:
    logger.warning(f"⚠️ Cryptometer API routes temporarily disabled - {e}")
    routes_failed.append(f"Cryptometer: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ Cryptometer API routes temporarily disabled - {e}")
    routes_failed.append(f"Cryptometer: {str(e)}")

try:
    from src.routes.riskmetric import router as riskmetric_router
    app.include_router(riskmetric_router, tags=["RiskMetric"])
    routes_loaded.append("RiskMetric")
except ImportError as e:
    logger.warning(f"⚠️ RiskMetric API routes temporarily disabled - {e}")
    routes_failed.append(f"RiskMetric: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ RiskMetric API routes temporarily disabled - {e}")
    routes_failed.append(f"RiskMetric: {str(e)}")

try:
    from src.routes.chatgpt_alerts import router as chatgpt_alerts_router
    app.include_router(chatgpt_alerts_router, tags=["ChatGPT Alerts"])
    routes_loaded.append("ChatGPT Alerts")
except ImportError as e:
    logger.warning(f"⚠️ ChatGPT Alerts API routes temporarily disabled - {e}")
    routes_failed.append(f"ChatGPT Alerts: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ ChatGPT Alerts API routes temporarily disabled - {e}")
    routes_failed.append(f"ChatGPT Alerts: {str(e)}")

try:
    from src.routes.binance import router as binance_router
    app.include_router(binance_router, prefix="/api/v1/binance", tags=["Binance"])
    routes_loaded.append("Binance")
except ImportError as e:
    logger.warning(f"⚠️ Binance API routes temporarily disabled - {e}")
    routes_failed.append(f"Binance: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ Binance API routes temporarily disabled - {e}")
    routes_failed.append(f"Binance: {str(e)}")

try:
    from src.routes.coefficient import router as coefficient_router
    app.include_router(coefficient_router, tags=["DBI Coefficient"])
    routes_loaded.append("DBI Coefficient")
except ImportError as e:
    logger.warning(f"⚠️ Coefficient API routes temporarily disabled - {e}")
    routes_failed.append(f"DBI Coefficient: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ Coefficient API routes temporarily disabled - {e}")
    routes_failed.append(f"DBI Coefficient: {str(e)}")

try:
    from src.routes.kingfisher import router as kingfisher_router
    app.include_router(kingfisher_router, tags=["KingFisher"])
    routes_loaded.append("KingFisher")
except ImportError as e:
    logger.warning(f"⚠️ KingFisher API routes temporarily disabled - {e}")
    routes_failed.append(f"KingFisher: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ KingFisher API routes temporarily disabled - {e}")
    routes_failed.append(f"KingFisher: {str(e)}")

try:
    from src.routes.alerts import router as alerts_router
    app.include_router(alerts_router, tags=["Alerts"])
    routes_loaded.append("Alerts")
except ImportError as e:
    logger.warning(f"⚠️ Alerts API routes temporarily disabled - {e}")
    routes_failed.append(f"Alerts: {str(e)}")
except Exception as e:
    logger.warning(f"⚠️ Alerts API routes temporarily disabled - {e}")
    routes_failed.append(f"Alerts: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "professional-dashboard",
        "version": "2.0.0",
        "port": 3400,
        "routes_loaded": routes_loaded,
        "routes_failed": routes_failed,
        "timestamp": datetime.now().isoformat()
    }

# Dashboard routes - React app will be served by the main route below

@app.get("/scoring")
async def serve_scoring():
    """Serve the scoring page"""
    scoring_file = dashboard_root / "scoring.html"
    if scoring_file.exists():
        return FileResponse(scoring_file)
    
    # Try index.html with scoring route
    index_file = dashboard_root / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    return JSONResponse({"message": "Scoring page available at main dashboard"})

@app.get("/riskmetric")
async def serve_riskmetric():
    """Serve the RiskMetric page"""
    riskmetric_file = dashboard_root / "riskmetric.html"
    if riskmetric_file.exists():
        return FileResponse(riskmetric_file)
    
    # Try index.html with riskmetric route
    index_file = dashboard_root / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    return JSONResponse({"message": "RiskMetric page available at main dashboard"})

@app.get("/my-symbols")
async def serve_my_symbols():
    """Serve the My Symbols page"""
    symbols_file = dashboard_root / "my-symbols.html"
    if symbols_file.exists():
        return FileResponse(symbols_file)
    
    # Try index.html with symbols route
    index_file = dashboard_root / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    return JSONResponse({"message": "My Symbols page available at main dashboard"})

# API proxy for Binance - Now proxies to our backend API
@app.get("/api/binance/ticker/24hr")
async def proxy_binance_ticker(symbol: str):
    """Proxy Binance ticker API calls to our backend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/v1/binance/ticker/24hr",
                params={"symbol": symbol},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Binance ticker proxy error: {e}")
        # Return mock data if backend is down
        return {
            "symbol": symbol,
            "lastPrice": "67890.12",
            "priceChange": "1234.56",
            "priceChangePercent": "2.50",
            "volume": "1234567890",
            "quoteVolume": "84000000000"
        }

@app.get("/api/binance/klines")
async def proxy_binance_klines(symbol: str, interval: str = "1h", limit: int = 24):
    """Proxy Binance klines API calls to our backend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/v1/binance/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Binance klines proxy error: {e}")
        # Return mock data if backend is down
        import time
        current_time = int(time.time() * 1000)
        mock_klines = []
        for i in range(limit):
            timestamp = current_time - (i * 3600000)  # 1 hour intervals
            mock_klines.append([
                timestamp,           # Open time
                "67000.00",         # Open
                "68000.00",         # High
                "66000.00",         # Low
                "67890.12",         # Close
                "1234.56",          # Volume
                timestamp + 3599999, # Close time
                "84000000",         # Quote asset volume
                1000,               # Number of trades
                "600.00",           # Taker buy base asset volume
                "40000000",         # Taker buy quote asset volume
                "0"                 # Ignore
            ])
        return mock_klines

# API proxy for Cryptometer
@app.get("/cryptometer/symbol/{symbol}")
async def proxy_cryptometer(symbol: str):
    """Proxy Cryptometer API calls"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/v1/cryptometer/symbol/{symbol}",
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Cryptometer proxy error: {e}")
        # Return mock data if backend is down
        return {
            "symbol": symbol,
            "price": 67890.12,
            "change_24h": 2.5,
            "volume_24h": 1234567890,
            "market_cap": 1234567890000,
            "timestamp": datetime.now().isoformat()
        }

# API proxy for all other endpoints
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_api(request: Request, path: str):
    """Proxy API requests to backend"""
    try:
        async with httpx.AsyncClient() as client:
            # Build backend URL
            backend_url = f"{BACKEND_URL}/api/{path}"
            
            # Get query parameters
            query_params = dict(request.query_params)
            
            # Get request body if present
            body = None
            if request.method in ["POST", "PUT"]:
                body = await request.body()
            
            # Forward request
            response = await client.request(
                method=request.method,
                url=backend_url,
                params=query_params,
                content=body,
                headers={
                    "Content-Type": request.headers.get("Content-Type", "application/json")
                },
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"API proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"Backend error: {str(e)}")

# Mount static directories
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    logger.info(f"✅ Assets mounted from {assets_dir}")

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted from {static_dir}")

if fusioncharts_dir.exists():
    app.mount("/fusioncharts", StaticFiles(directory=str(fusioncharts_dir)), name="fusioncharts")
    logger.info(f"✅ FusionCharts mounted from {fusioncharts_dir}")

# Mount individual asset files
@app.get("/{filename:path}.css")
async def serve_css(filename: str):
    """Serve CSS files"""
    css_file = assets_dir / f"{filename}.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    css_file = dashboard_root / f"{filename}.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/{filename:path}.js")
async def serve_js(filename: str):
    """Serve JavaScript files"""
    js_file = assets_dir / f"{filename}.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    js_file = dashboard_root / f"{filename}.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS file not found")

@app.get("/{filename:path}.jsx")
async def serve_jsx(filename: str):
    """Serve JSX files"""
    jsx_file = dashboard_root / f"{filename}.jsx"
    if jsx_file.exists():
        return FileResponse(jsx_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JSX file not found")

@app.get("/api-proxy.js")
async def serve_api_proxy():
    """Serve API proxy JavaScript file"""
    proxy_file = dashboard_root / "api-proxy.js"
    if proxy_file.exists():
        return FileResponse(proxy_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="API proxy file not found")

@app.get("/{filename:path}.png")
async def serve_png(filename: str):
    """Serve PNG images"""
    for directory in [dashboard_root, assets_dir]:
        img_file = directory / f"{filename}.png"
        if img_file.exists():
            return FileResponse(img_file, media_type="image/png")
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/{filename:path}.jpg")
async def serve_jpg(filename: str):
    """Serve JPG images"""
    for directory in [dashboard_root, assets_dir]:
        img_file = directory / f"{filename}.jpg"
        if img_file.exists():
            return FileResponse(img_file, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/{filename:path}.jpeg")
async def serve_jpeg(filename: str):
    """Serve JPEG images"""
    for directory in [dashboard_root, assets_dir]:
        img_file = directory / f"{filename}.jpeg"
        if img_file.exists():
            return FileResponse(img_file, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Image not found")

# Main route for React app
@app.get("/")
async def serve_dashboard():
    """Serve the main React dashboard"""
    index_file = dist_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Dashboard not found")

# Fallback route for SPA - only for non-API routes
@app.get("/{full_path:path}")
async def serve_spa_fallback(full_path: str):
    """Fallback for SPA routing"""
    # Don't fallback for API routes, assets, or specific API endpoints
    if (full_path.startswith(("api/", "assets/", "static/", "fusioncharts/")) or 
        full_path.startswith(("my-symbols/", "futures-symbols/", "cryptometer/", "riskmetric/", 
                             "chatgpt-alerts/", "coefficient/", "kingfisher/", "alerts/")) or
        full_path in ["health", "test"]):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other routes
    index_file = dist_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    raise HTTPException(status_code=404, detail="Dashboard not found")

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 ZmartBot Professional Dashboard Server")
    print("=" * 60)
    print(f"📁 Dashboard root: {dashboard_root}")
    print(f"📁 Assets directory: {assets_dir}")
    print(f"🌐 Server URL: http://localhost:3400/")
    print(f"🏥 Health check: http://localhost:3400/health")
    print("=" * 60)
    print("✅ Routes loaded:", ", ".join(routes_loaded) if routes_loaded else "None")
    print("⚠️ Routes failed:", ", ".join(routes_failed) if routes_failed else "None")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=3400, log_level="info")