"""
SQLite MCP Adapter for Zmarty Dashboard
Provides secure database access and analytics through MCP
"""
import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteMCPAdapter:
    """
    MCP-compatible SQLite adapter for secure database operations
    Provides read-only access to trading data and analytics
    """
    
    def __init__(self, db_path: str = "data/zmarty_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database with trading analytics tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trading signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    price REAL NOT NULL,
                    volume REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Market data cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT
                )
            ''')
            
            # User analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    category TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trading_signals_timestamp ON trading_signals(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name)')
            
            conn.commit()
            logger.info("SQLite MCP database initialized successfully")
    
    def execute_safe_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a safe read-only query"""
        # Security: Only allow SELECT statements
        if not query.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        # Security: Block dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'EXEC']
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Dangerous keyword '{keyword}' not allowed")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"SQLite query error: {e}")
            raise
    
    def get_trading_signals(
        self, 
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get trading signals with optional filters"""
        query = "SELECT * FROM trading_signals WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
            
        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        return self.execute_safe_query(query, tuple(params))
    
    def get_market_data(
        self, 
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get market data with optional symbol filter"""
        if symbol:
            query = "SELECT * FROM market_data WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?"
            params = (symbol, limit)
        else:
            query = "SELECT * FROM market_data ORDER BY timestamp DESC LIMIT ?"
            params = (limit,)
        
        return self.execute_safe_query(query, params)
    
    def get_user_analytics(
        self, 
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get user analytics with optional filters"""
        query = "SELECT * FROM user_analytics WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
            
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        return self.execute_safe_query(query, tuple(params))
    
    def get_performance_metrics(
        self, 
        metric_name: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get performance metrics with optional filters"""
        query = "SELECT * FROM performance_metrics WHERE 1=1"
        params = []
        
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
            
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        return self.execute_safe_query(query, tuple(params))
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary statistics"""
        try:
            # Get trading signals summary
            signals_query = """
                SELECT 
                    COUNT(*) as total_signals,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    AVG(confidence) as avg_confidence,
                    MAX(timestamp) as latest_signal
                FROM trading_signals
            """
            signals_summary = self.execute_safe_query(signals_query)[0]
            
            # Get market data summary
            market_query = """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    MAX(timestamp) as latest_update
                FROM market_data
            """
            market_summary = self.execute_safe_query(market_query)[0]
            
            # Get user activity summary
            user_query = """
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT event_type) as event_types,
                    MAX(timestamp) as latest_activity
                FROM user_analytics
            """
            user_summary = self.execute_safe_query(user_query)[0]
            
            return {
                "trading_signals": signals_summary,
                "market_data": market_summary,
                "user_analytics": user_summary,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics summary: {e}")
            return {"error": str(e)}
    
    def store_trading_signal(
        self, 
        symbol: str,
        signal_type: str,
        direction: str,
        strength: float,
        confidence: float,
        price: float,
        volume: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Store a new trading signal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trading_signals 
                    (symbol, signal_type, direction, strength, confidence, price, volume, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, signal_type, direction, strength, confidence, price, 
                    volume, json.dumps(metadata) if metadata else None
                ))
                
                signal_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Stored trading signal {signal_id} for {symbol}")
                return signal_id
                
        except Exception as e:
            logger.error(f"Failed to store trading signal: {e}")
            raise
    
    def store_market_data(
        self,
        symbol: str,
        price: float,
        change_24h: Optional[float] = None,
        volume_24h: Optional[float] = None,
        market_cap: Optional[float] = None,
        source: str = "api"
    ) -> int:
        """Store market data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO market_data 
                    (symbol, price, change_24h, volume_24h, market_cap, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, price, change_24h, volume_24h, market_cap, source))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Stored market data {record_id} for {symbol}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to store market data: {e}")
            raise
    
    def store_user_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> int:
        """Store user analytics event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_analytics 
                    (user_id, event_type, event_data, session_id, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, event_type, 
                    json.dumps(event_data) if event_data else None,
                    session_id, ip_address, user_agent
                ))
                
                event_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Stored user event {event_id} for user {user_id}")
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to store user event: {e}")
            raise
    
    def store_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        category: Optional[str] = None
    ) -> int:
        """Store performance metric"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (metric_name, metric_value, metric_unit, category)
                    VALUES (?, ?, ?, ?)
                ''', (metric_name, metric_value, metric_unit, category))
                
                metric_id = cursor.lastrowid
                conn.commit()
                
                logger.debug(f"Stored performance metric {metric_id}: {metric_name} = {metric_value}")
                return metric_id
                
        except Exception as e:
            logger.error(f"Failed to store performance metric: {e}")
            raise


# Global instance
sqlite_mcp = SQLiteMCPAdapter()


# MCP-compatible interface functions
async def mcp_execute_query(query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
    """MCP-compatible query execution"""
    try:
        results = sqlite_mcp.execute_safe_query(query, params)
        return {
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def mcp_get_trading_signals(**kwargs) -> Dict[str, Any]:
    """MCP-compatible trading signals retrieval"""
    try:
        signals = sqlite_mcp.get_trading_signals(**kwargs)
        return {
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def mcp_get_analytics_summary() -> Dict[str, Any]:
    """MCP-compatible analytics summary"""
    return sqlite_mcp.get_analytics_summary()