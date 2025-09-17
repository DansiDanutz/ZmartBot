"""
MCP API Routes for Zmarty Dashboard
Provides HTTP endpoints for all MCP functionality
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging

from ...services.mcp_registry import get_mcp_registry, call_mcp_function, get_mcp_capabilities, mcp_health_check
from ...core.auth import get_current_user
from ...models.database import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/status")
async def get_mcp_status():
    """Get MCP registry status and health"""
    try:
        registry = await get_mcp_registry()
        stats = registry.get_stats()
        health = await mcp_health_check()
        
        return {
            "status": "ok",
            "registry_stats": stats,
            "health_check": health
        }
    except Exception as e:
        logger.error(f"MCP status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adapters")
async def list_mcp_adapters(
    adapter_type: Optional[str] = Query(None, description="Filter by adapter type")
):
    """List all available MCP adapters"""
    try:
        registry = await get_mcp_registry()
        adapters = registry.get_adapters(adapter_type)
        return adapters
    except Exception as e:
        logger.error(f"Failed to list MCP adapters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def list_mcp_capabilities():
    """List all available MCP capabilities"""
    try:
        capabilities = await get_mcp_capabilities()
        return capabilities
    except Exception as e:
        logger.error(f"Failed to list MCP capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/functions")
async def list_mcp_functions(
    adapter: Optional[str] = Query(None, description="Filter by adapter name")
):
    """List all available MCP functions"""
    try:
        registry = await get_mcp_registry()
        functions = registry.get_functions(adapter)
        return functions
    except Exception as e:
        logger.error(f"Failed to list MCP functions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities/search")
async def search_mcp_capabilities(
    query: str = Query(..., description="Search query for capabilities")
):
    """Search MCP capabilities"""
    try:
        registry = await get_mcp_registry()
        results = registry.search_capabilities(query)
        return results
    except Exception as e:
        logger.error(f"MCP capability search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/call/{function_name}")
async def call_mcp_function_endpoint(
    function_name: str,
    payload: Dict[str, Any] = Body({}),
    current_user: User = Depends(get_current_user)
):
    """Call an MCP function with parameters"""
    try:
        # Extract args and kwargs from payload
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        
        # Add user context to kwargs
        kwargs["user_id"] = str(current_user.id)
        
        result = await call_mcp_function(function_name, *args, **kwargs)
        return result
    except Exception as e:
        logger.error(f"MCP function call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory MCP Routes
@router.post("/memory/store")
async def store_memory(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Store a memory entry"""
    try:
        result = await call_mcp_function(
            "memory.store_memory",
            user_id=str(current_user.id),
            **payload
        )
        return result
    except Exception as e:
        logger.error(f"Memory storage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/retrieve")
async def retrieve_memories(
    conversation_id: Optional[str] = Query(None),
    memory_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Retrieve memories for the current user"""
    try:
        result = await call_mcp_function(
            "memory.retrieve_memories",
            user_id=str(current_user.id),
            conversation_id=conversation_id,
            memory_type=memory_type,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Memory retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/context/{conversation_id}")
async def get_memory_context(
    conversation_id: str,
    context_window: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get conversation context"""
    try:
        result = await call_mcp_function(
            "memory.get_context",
            user_id=str(current_user.id),
            conversation_id=conversation_id,
            context_window=context_window
        )
        return result
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SQLite MCP Routes
@router.post("/sqlite/query")
async def execute_sqlite_query(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Execute a safe SQLite query"""
    try:
        query = payload.get("query", "")
        params = payload.get("params")
        
        result = await call_mcp_function(
            "sqlite.execute_query",
            query=query,
            params=params
        )
        return result
    except Exception as e:
        logger.error(f"SQLite query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sqlite/trading-signals")
async def get_trading_signals(
    symbol: Optional[str] = Query(None),
    signal_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Get trading signals from SQLite"""
    try:
        result = await call_mcp_function(
            "sqlite.get_trading_signals",
            symbol=symbol,
            signal_type=signal_type,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Trading signals retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sqlite/analytics-summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary from SQLite"""
    try:
        result = await call_mcp_function("sqlite.get_analytics_summary")
        return result
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Filesystem MCP Routes
@router.get("/filesystem/list")
async def list_filesystem_directory(
    directory: str = Query("", description="Directory path to list"),
    include_hidden: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """List filesystem directory contents"""
    try:
        result = await call_mcp_function(
            "filesystem.list_directory",
            directory=directory,
            include_hidden=include_hidden
        )
        return result
    except Exception as e:
        logger.error(f"Filesystem listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filesystem/read")
async def read_filesystem_file(
    file_path: str = Query(..., description="File path to read"),
    encoding: str = Query("utf-8"),
    max_size: int = Query(1024*1024, le=10*1024*1024),
    current_user: User = Depends(get_current_user)
):
    """Read file from filesystem"""
    try:
        result = await call_mcp_function(
            "filesystem.read_file",
            file_path=file_path,
            encoding=encoding,
            max_size=max_size
        )
        return result
    except Exception as e:
        logger.error(f"File reading failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filesystem/write")
async def write_filesystem_file(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Write file to filesystem"""
    try:
        result = await call_mcp_function(
            "filesystem.write_file",
            **payload
        )
        return result
    except Exception as e:
        logger.error(f"File writing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filesystem/search")
async def search_filesystem_files(
    pattern: str = Query(..., description="Search pattern"),
    directory: str = Query(""),
    case_sensitive: bool = Query(False),
    file_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Search files in filesystem"""
    try:
        result = await call_mcp_function(
            "filesystem.search_files",
            pattern=pattern,
            directory=directory,
            case_sensitive=case_sensitive,
            file_type=file_type
        )
        return result
    except Exception as e:
        logger.error(f"File search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Web Search MCP Routes
@router.get("/web-search/search")
async def web_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    search_engine: str = Query("duckduckgo"),
    safe_search: bool = Query(True),
    region: str = Query("us-en"),
    current_user: User = Depends(get_current_user)
):
    """Search the web"""
    try:
        result = await call_mcp_function(
            "web_search.search_web",
            query=query,
            limit=limit,
            search_engine=search_engine,
            safe_search=safe_search,
            region=region
        )
        return result
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/web-search/news")
async def search_news(
    query: str = Query(..., description="News search query"),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query("business"),
    language: str = Query("en"),
    current_user: User = Depends(get_current_user)
):
    """Search for news articles"""
    try:
        result = await call_mcp_function(
            "web_search.search_news",
            query=query,
            limit=limit,
            category=category,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"News search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web-search/extract")
async def extract_web_content(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Extract content from a URL"""
    try:
        result = await call_mcp_function(
            "web_search.extract_content",
            **payload
        )
        return result
    except Exception as e:
        logger.error(f"Content extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/web-search/sentiment")
async def monitor_sentiment(
    query: str = Query(..., description="Query to monitor sentiment for"),
    current_user: User = Depends(get_current_user)
):
    """Monitor sentiment for a query"""
    try:
        result = await call_mcp_function(
            "web_search.monitor_sentiment",
            query=query
        )
        return result
    except Exception as e:
        logger.error(f"Sentiment monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Time MCP Routes
@router.get("/time/current")
async def get_current_time(
    timezone: str = Query("UTC", description="Timezone for current time")
):
    """Get current time in specified timezone"""
    try:
        result = await call_mcp_function(
            "time.get_current_time",
            timezone_str=timezone
        )
        return result
    except Exception as e:
        logger.error(f"Current time retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/time/convert")
async def convert_timezone(
    payload: Dict[str, Any] = Body(...)
):
    """Convert time between timezones"""
    try:
        result = await call_mcp_function(
            "time.convert_timezone",
            **payload
        )
        return result
    except Exception as e:
        logger.error(f"Timezone conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/time/schedule")
async def schedule_event(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Schedule a time-based event"""
    try:
        result = await call_mcp_function(
            "time.schedule_event",
            **payload
        )
        return result
    except Exception as e:
        logger.error(f"Event scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time/market-status")
async def get_market_status(
    exchange: str = Query("NYSE", description="Exchange to check")
):
    """Check if a market is currently open"""
    try:
        result = await call_mcp_function(
            "time.is_market_open",
            exchange=exchange
        )
        return result
    except Exception as e:
        logger.error(f"Market status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def mcp_health_endpoint():
    """MCP system health check endpoint"""
    try:
        health = await mcp_health_check()
        
        if health.get("overall_health") == "healthy":
            return JSONResponse(content=health, status_code=200)
        else:
            return JSONResponse(content=health, status_code=503)
            
    except Exception as e:
        logger.error(f"MCP health check failed: {e}")
        return JSONResponse(
            content={"status": "error", "error": str(e)},
            status_code=500
        )