"""
MCP Registry for Zmarty Dashboard
Central registry and coordinator for all MCP adapters
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, asdict

# Import all MCP adapters
from .memory_mcp import MemoryAdapter, mcp_store_memory, mcp_retrieve_memories, mcp_get_context
from .sqlite_mcp import SQLiteMCPAdapter, mcp_execute_query, mcp_get_trading_signals, mcp_get_analytics_summary
from .filesystem_mcp import FilesystemMCPAdapter, mcp_list_directory, mcp_read_file, mcp_write_file, mcp_search_files
from .web_search_mcp import WebSearchMCPAdapter, mcp_search_web, mcp_search_news, mcp_extract_content, mcp_monitor_sentiment
from .time_mcp import TimeMCPAdapter, mcp_get_current_time, mcp_convert_timezone, mcp_schedule_event, mcp_is_market_open

logger = logging.getLogger(__name__)


@dataclass
class MCPAdapter:
    """MCP Adapter registration information"""
    name: str
    description: str
    version: str
    adapter_type: str
    instance: Any
    functions: Dict[str, Callable]
    capabilities: List[str]
    status: str = "inactive"  # inactive, active, error
    last_used: Optional[datetime] = None
    error_count: int = 0


class MCPRegistry:
    """
    Central registry and coordinator for all MCP adapters
    Provides unified access to all MCP capabilities
    """
    
    def __init__(self):
        self.adapters: Dict[str, MCPAdapter] = {}
        self.capabilities_index: Dict[str, List[str]] = {}
        self.function_registry: Dict[str, Callable] = {}
        self.initialized = False
        
        # Performance tracking
        self.usage_stats = {}
        self.error_logs = []
        
        logger.info("MCP Registry initialized")
    
    async def initialize(self):
        """Initialize all MCP adapters"""
        if self.initialized:
            return
        
        await self._register_all_adapters()
        await self._activate_adapters()
        
        self.initialized = True
        logger.info(f"MCP Registry fully initialized with {len(self.adapters)} adapters")
    
    async def _register_all_adapters(self):
        """Register all available MCP adapters"""
        
        # Memory Adapter
        memory_adapter = MemoryAdapter()
        await self._register_adapter(MCPAdapter(
            name="memory",
            description="Persistent conversation memory and context management",
            version="1.0.0",
            adapter_type="storage",
            instance=memory_adapter,
            functions={
                "store_memory": mcp_store_memory,
                "retrieve_memories": mcp_retrieve_memories,
                "get_context": mcp_get_context,
            },
            capabilities=[
                "conversation_memory", "context_storage", "user_preferences",
                "fact_extraction", "memory_search", "conversation_history"
            ]
        ))
        
        # SQLite Adapter
        sqlite_adapter = SQLiteMCPAdapter()
        await self._register_adapter(MCPAdapter(
            name="sqlite",
            description="SQLite database access for analytics and trading data",
            version="1.0.0",
            adapter_type="database",
            instance=sqlite_adapter,
            functions={
                "execute_query": mcp_execute_query,
                "get_trading_signals": mcp_get_trading_signals,
                "get_analytics_summary": mcp_get_analytics_summary,
            },
            capabilities=[
                "database_queries", "trading_signals", "analytics", 
                "user_tracking", "performance_metrics", "data_storage"
            ]
        ))
        
        # Filesystem Adapter
        filesystem_adapter = FilesystemMCPAdapter()
        await self._register_adapter(MCPAdapter(
            name="filesystem",
            description="Secure file system operations and document management",
            version="1.0.0",
            adapter_type="storage",
            instance=filesystem_adapter,
            functions={
                "list_directory": mcp_list_directory,
                "read_file": mcp_read_file,
                "write_file": mcp_write_file,
                "search_files": mcp_search_files,
            },
            capabilities=[
                "file_operations", "document_storage", "file_search",
                "data_export", "backup_management", "log_access"
            ]
        ))
        
        # Web Search Adapter
        web_search_adapter = WebSearchMCPAdapter()
        await self._register_adapter(MCPAdapter(
            name="web_search",
            description="Web search, news aggregation, and content extraction",
            version="1.0.0",
            adapter_type="external",
            instance=web_search_adapter,
            functions={
                "search_web": mcp_search_web,
                "search_news": mcp_search_news,
                "extract_content": mcp_extract_content,
                "monitor_sentiment": mcp_monitor_sentiment,
            },
            capabilities=[
                "web_search", "news_aggregation", "content_extraction",
                "sentiment_analysis", "market_research", "trend_monitoring"
            ]
        ))
        
        # Time Adapter
        time_adapter = TimeMCPAdapter()
        await self._register_adapter(MCPAdapter(
            name="time",
            description="Time management, scheduling, and temporal operations",
            version="1.0.0",
            adapter_type="utility",
            instance=time_adapter,
            functions={
                "get_current_time": mcp_get_current_time,
                "convert_timezone": mcp_convert_timezone,
                "schedule_event": mcp_schedule_event,
                "is_market_open": mcp_is_market_open,
            },
            capabilities=[
                "time_management", "timezone_conversion", "scheduling",
                "market_hours", "event_reminders", "temporal_analysis"
            ]
        ))
        
        logger.info(f"Registered {len(self.adapters)} MCP adapters")
    
    async def _register_adapter(self, adapter: MCPAdapter):
        """Register a single MCP adapter"""
        self.adapters[adapter.name] = adapter
        
        # Index capabilities
        for capability in adapter.capabilities:
            if capability not in self.capabilities_index:
                self.capabilities_index[capability] = []
            self.capabilities_index[capability].append(adapter.name)
        
        # Register functions
        for func_name, func in adapter.functions.items():
            full_func_name = f"{adapter.name}.{func_name}"
            self.function_registry[full_func_name] = func
        
        logger.debug(f"Registered MCP adapter: {adapter.name}")
    
    async def _activate_adapters(self):
        """Activate all registered adapters"""
        for name, adapter in self.adapters.items():
            try:
                # Initialize adapter if it has an initialize method
                if hasattr(adapter.instance, 'initialize'):
                    await adapter.instance.initialize()
                
                adapter.status = "active"
                logger.debug(f"Activated MCP adapter: {name}")
                
            except Exception as e:
                adapter.status = "error"
                adapter.error_count += 1
                logger.error(f"Failed to activate MCP adapter {name}: {e}")
    
    async def call_function(
        self,
        function_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Call a registered MCP function"""
        try:
            if function_name not in self.function_registry:
                return {
                    "error": f"Function not found: {function_name}",
                    "available_functions": list(self.function_registry.keys())
                }
            
            # Extract adapter name
            adapter_name = function_name.split('.')[0]
            
            # Update usage stats
            self._update_usage_stats(adapter_name, function_name)
            
            # Call the function
            func = self.function_registry[function_name]
            result = await func(*args, **kwargs)
            
            # Update adapter last used time
            if adapter_name in self.adapters:
                self.adapters[adapter_name].last_used = datetime.utcnow()
            
            return {
                "function": function_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }
            
        except Exception as e:
            # Log error
            self._log_error(function_name, str(e))
            
            return {
                "function": function_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "success": False
            }
    
    def get_adapters(self, adapter_type: Optional[str] = None) -> Dict[str, Any]:
        """Get information about registered adapters"""
        adapters_info = {}
        
        for name, adapter in self.adapters.items():
            if adapter_type and adapter.adapter_type != adapter_type:
                continue
            
            adapters_info[name] = {
                "name": adapter.name,
                "description": adapter.description,
                "version": adapter.version,
                "type": adapter.adapter_type,
                "status": adapter.status,
                "capabilities": adapter.capabilities,
                "functions": list(adapter.functions.keys()),
                "last_used": adapter.last_used.isoformat() if adapter.last_used else None,
                "error_count": adapter.error_count
            }
        
        return {
            "adapters": adapters_info,
            "count": len(adapters_info),
            "filter": adapter_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get all available capabilities and their providers"""
        return {
            "capabilities": dict(self.capabilities_index),
            "total_capabilities": len(self.capabilities_index),
            "total_adapters": len(self.adapters),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_functions(self, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all available functions"""
        functions = {}
        
        for func_name in self.function_registry.keys():
            parts = func_name.split('.')
            current_adapter = parts[0]
            
            if adapter_name and current_adapter != adapter_name:
                continue
            
            if current_adapter not in functions:
                functions[current_adapter] = []
            
            functions[current_adapter].append({
                "name": parts[1],
                "full_name": func_name,
                "adapter": current_adapter
            })
        
        return {
            "functions": functions,
            "filter": adapter_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        active_adapters = sum(1 for a in self.adapters.values() if a.status == "active")
        error_adapters = sum(1 for a in self.adapters.values() if a.status == "error")
        
        return {
            "registry_status": "initialized" if self.initialized else "not_initialized",
            "total_adapters": len(self.adapters),
            "active_adapters": active_adapters,
            "error_adapters": error_adapters,
            "total_functions": len(self.function_registry),
            "total_capabilities": len(self.capabilities_index),
            "usage_stats": dict(self.usage_stats),
            "recent_errors": self.error_logs[-10:],  # Last 10 errors
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def search_capabilities(self, query: str) -> Dict[str, Any]:
        """Search for capabilities by query"""
        matching_capabilities = []
        query_lower = query.lower()
        
        for capability, adapters in self.capabilities_index.items():
            if query_lower in capability.lower():
                matching_capabilities.append({
                    "capability": capability,
                    "adapters": adapters,
                    "relevance": 1.0 if query_lower == capability.lower() else 0.5
                })
        
        # Sort by relevance
        matching_capabilities.sort(key=lambda x: x["relevance"], reverse=True)
        
        return {
            "query": query,
            "matches": matching_capabilities,
            "count": len(matching_capabilities),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all adapters"""
        health_status = {}
        
        for name, adapter in self.adapters.items():
            try:
                # Basic status check
                status = {
                    "status": adapter.status,
                    "error_count": adapter.error_count,
                    "last_used": adapter.last_used.isoformat() if adapter.last_used else None
                }
                
                # Try to call a simple function if available
                if hasattr(adapter.instance, 'health_check'):
                    health_result = await adapter.instance.health_check()
                    status["health_check"] = health_result
                elif "get_current_time" in adapter.functions:
                    # Time adapter health check
                    await adapter.functions["get_current_time"]()
                    status["responsive"] = True
                
                health_status[name] = status
                
            except Exception as e:
                health_status[name] = {
                    "status": "error",
                    "error": str(e),
                    "error_count": adapter.error_count + 1
                }
                
                # Update error count
                adapter.error_count += 1
                if adapter.error_count > 5:
                    adapter.status = "error"
        
        overall_health = all(
            status.get("status") == "active" 
            for status in health_status.values()
        )
        
        return {
            "overall_health": "healthy" if overall_health else "degraded",
            "adapters": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_usage_stats(self, adapter_name: str, function_name: str):
        """Update usage statistics"""
        if adapter_name not in self.usage_stats:
            self.usage_stats[adapter_name] = {"calls": 0, "functions": {}}
        
        self.usage_stats[adapter_name]["calls"] += 1
        
        if function_name not in self.usage_stats[adapter_name]["functions"]:
            self.usage_stats[adapter_name]["functions"][function_name] = 0
        
        self.usage_stats[adapter_name]["functions"][function_name] += 1
    
    def _log_error(self, function_name: str, error_message: str):
        """Log error for debugging"""
        error_entry = {
            "function": function_name,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.error_logs.append(error_entry)
        
        # Keep only last 100 errors
        if len(self.error_logs) > 100:
            self.error_logs = self.error_logs[-100:]
        
        # Update adapter error count
        adapter_name = function_name.split('.')[0]
        if adapter_name in self.adapters:
            self.adapters[adapter_name].error_count += 1


# Global registry instance
mcp_registry = MCPRegistry()


# Convenience functions
async def get_mcp_registry() -> MCPRegistry:
    """Get the global MCP registry instance"""
    if not mcp_registry.initialized:
        await mcp_registry.initialize()
    return mcp_registry


async def call_mcp_function(function_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Convenience function to call MCP functions"""
    registry = await get_mcp_registry()
    return await registry.call_function(function_name, *args, **kwargs)


async def get_mcp_capabilities() -> Dict[str, Any]:
    """Get all available MCP capabilities"""
    registry = await get_mcp_registry()
    return registry.get_capabilities()


async def mcp_health_check() -> Dict[str, Any]:
    """Perform MCP health check"""
    registry = await get_mcp_registry()
    return await registry.health_check()