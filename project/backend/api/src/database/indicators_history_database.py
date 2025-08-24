#!/usr/bin/env python3
"""
Comprehensive Indicators History Database
Stores real-time snapshots of 21+ technical indicators for all symbols
Includes indicator screenshots and metadata for pattern analysis
"""

import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import base64
from PIL import Image
import io
import uuid

logger = logging.getLogger(__name__)

@dataclass
class IndicatorSnapshot:
    """Complete indicator snapshot for a symbol at a specific time"""
    id: str
    symbol: str
    timestamp: datetime
    timeframe: str
    
    # 21 Technical Indicators
    rsi: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    cci: Optional[float] = None
    williams_r: Optional[float] = None
    parabolic_sar: Optional[float] = None
    
    # Market data
    price: Optional[float] = None
    volume: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    
    # Pattern signals
    trend_direction: Optional[str] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    pattern_detected: Optional[str] = None
    signal_strength: Optional[float] = None
    
    # Screenshot data
    screenshot_path: Optional[str] = None
    screenshot_base64: Optional[str] = None
    screenshot_metadata: Optional[Dict] = None
    
    # Analysis metadata
    data_source: str = "real_time"
    analysis_version: str = "v1.0"
    created_at: datetime = None

@dataclass
class PatternAnalysisResult:
    """Pattern analysis result from historical data"""
    id: str
    symbol: str
    pattern_type: str
    timeframe: str
    start_timestamp: datetime
    end_timestamp: datetime
    confidence_score: float
    pattern_metadata: Dict[str, Any]
    related_snapshots: List[str]  # Snapshot IDs
    prediction_accuracy: Optional[float] = None
    created_at: datetime = None

class IndicatorsHistoryDatabase:
    """Comprehensive database for indicators history and screenshots"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "indicators_history.db"
        
        self.db_path = str(db_path)
        self.screenshots_dir = Path(self.db_path).parent / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Create database and tables
        self._create_database()
        
        logger.info(f"✅ Indicators History Database initialized: {self.db_path}")
    
    def _create_database(self):
        """Create database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main indicators snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indicator_snapshots (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    timeframe TEXT NOT NULL,
                    
                    -- Technical Indicators (21+)
                    rsi REAL,
                    rsi_14 REAL,
                    macd REAL,
                    macd_signal REAL,
                    macd_histogram REAL,
                    ema_9 REAL,
                    ema_21 REAL,
                    ema_50 REAL,
                    ema_200 REAL,
                    sma_20 REAL,
                    sma_50 REAL,
                    bollinger_upper REAL,
                    bollinger_middle REAL,
                    bollinger_lower REAL,
                    stochastic_k REAL,
                    stochastic_d REAL,
                    atr REAL,
                    adx REAL,
                    cci REAL,
                    williams_r REAL,
                    parabolic_sar REAL,
                    
                    -- Market Data
                    price REAL,
                    volume REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    
                    -- Pattern Analysis
                    trend_direction TEXT,
                    support_level REAL,
                    resistance_level REAL,
                    pattern_detected TEXT,
                    signal_strength REAL,
                    
                    -- Screenshot Data
                    screenshot_path TEXT,
                    screenshot_base64 TEXT,
                    screenshot_metadata TEXT,
                    
                    -- Metadata
                    data_source TEXT DEFAULT 'real_time',
                    analysis_version TEXT DEFAULT 'v1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Pattern analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pattern_analysis (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    start_timestamp TIMESTAMP NOT NULL,
                    end_timestamp TIMESTAMP NOT NULL,
                    confidence_score REAL NOT NULL,
                    pattern_metadata TEXT,
                    related_snapshots TEXT,
                    prediction_accuracy REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Symbols tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_symbols (
                    symbol TEXT PRIMARY KEY,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    last_snapshot TIMESTAMP,
                    total_snapshots INTEGER DEFAULT 0,
                    data_quality_score REAL DEFAULT 100.0
                )
            ''')
            
            # Performance tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collection_stats (
                    date TEXT PRIMARY KEY,
                    symbols_processed INTEGER DEFAULT 0,
                    snapshots_created INTEGER DEFAULT 0,
                    screenshots_captured INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    avg_processing_time REAL DEFAULT 0.0,
                    data_size_mb REAL DEFAULT 0.0
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_symbol_time ON indicator_snapshots(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timeframe ON indicator_snapshots(timeframe)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern_symbol ON pattern_analysis(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern_type ON pattern_analysis(pattern_type)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating database: {e}")
            raise
    
    def add_symbol(self, symbol: str) -> bool:
        """Add a new symbol to track"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO tracked_symbols (symbol, added_date, is_active)
                VALUES (?, ?, 1)
            ''', (symbol.upper(), datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Added symbol {symbol} to tracking")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding symbol {symbol}: {e}")
            return False
    
    def get_tracked_symbols(self) -> List[str]:
        """Get list of all tracked symbols"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT symbol FROM tracked_symbols WHERE is_active = 1')
            symbols = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return symbols
            
        except Exception as e:
            logger.error(f"❌ Error getting tracked symbols: {e}")
            return []
    
    def save_snapshot(self, snapshot: IndicatorSnapshot) -> bool:
        """Save indicator snapshot to database"""
        try:
            if not snapshot.id:
                snapshot.id = str(uuid.uuid4())
            
            if not snapshot.created_at:
                snapshot.created_at = datetime.now()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert screenshot metadata to JSON
            screenshot_metadata_json = json.dumps(snapshot.screenshot_metadata) if snapshot.screenshot_metadata else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO indicator_snapshots (
                    id, symbol, timestamp, timeframe,
                    rsi, rsi_14, macd, macd_signal, macd_histogram,
                    ema_9, ema_21, ema_50, ema_200,
                    sma_20, sma_50,
                    bollinger_upper, bollinger_middle, bollinger_lower,
                    stochastic_k, stochastic_d, atr, adx, cci, williams_r, parabolic_sar,
                    price, volume, volume_24h, market_cap,
                    trend_direction, support_level, resistance_level, pattern_detected, signal_strength,
                    screenshot_path, screenshot_base64, screenshot_metadata,
                    data_source, analysis_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.id, snapshot.symbol, snapshot.timestamp, snapshot.timeframe,
                snapshot.rsi, snapshot.rsi_14, snapshot.macd, snapshot.macd_signal, snapshot.macd_histogram,
                snapshot.ema_9, snapshot.ema_21, snapshot.ema_50, snapshot.ema_200,
                snapshot.sma_20, snapshot.sma_50,
                snapshot.bollinger_upper, snapshot.bollinger_middle, snapshot.bollinger_lower,
                snapshot.stochastic_k, snapshot.stochastic_d, snapshot.atr, snapshot.adx, 
                snapshot.cci, snapshot.williams_r, snapshot.parabolic_sar,
                snapshot.price, snapshot.volume, snapshot.volume_24h, snapshot.market_cap,
                snapshot.trend_direction, snapshot.support_level, snapshot.resistance_level,
                snapshot.pattern_detected, snapshot.signal_strength,
                snapshot.screenshot_path, snapshot.screenshot_base64, screenshot_metadata_json,
                snapshot.data_source, snapshot.analysis_version, snapshot.created_at
            ))
            
            # Update symbol tracking
            cursor.execute('''
                UPDATE tracked_symbols 
                SET last_snapshot = ?, total_snapshots = total_snapshots + 1
                WHERE symbol = ?
            ''', (snapshot.timestamp, snapshot.symbol))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved snapshot for {snapshot.symbol} at {snapshot.timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving snapshot: {e}")
            return False
    
    def get_snapshots(self, symbol: str = None, timeframe: str = None, 
                     start_time: datetime = None, end_time: datetime = None, 
                     limit: int = 100) -> List[IndicatorSnapshot]:
        """Get indicator snapshots with filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM indicator_snapshots WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol.upper())
            
            if timeframe:
                query += " AND timeframe = ?"
                params.append(timeframe)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            snapshots = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                
                # Parse screenshot metadata
                if row_dict['screenshot_metadata']:
                    row_dict['screenshot_metadata'] = json.loads(row_dict['screenshot_metadata'])
                
                # Convert timestamps
                row_dict['timestamp'] = datetime.fromisoformat(row_dict['timestamp'])
                if row_dict['created_at']:
                    row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'])
                
                snapshot = IndicatorSnapshot(**row_dict)
                snapshots.append(snapshot)
            
            conn.close()
            return snapshots
            
        except Exception as e:
            logger.error(f"❌ Error getting snapshots: {e}")
            return []
    
    def save_screenshot(self, symbol: str, timeframe: str, screenshot_data: bytes, 
                       metadata: Dict[str, Any] = None) -> str:
        """Save screenshot to file and return path"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_{timeframe}_{timestamp}.png"
            file_path = self.screenshots_dir / filename
            
            # Save screenshot file
            with open(file_path, 'wb') as f:
                f.write(screenshot_data)
            
            # Convert to base64 for database storage
            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            logger.info(f"✅ Saved screenshot: {filename}")
            return str(file_path), screenshot_base64
            
        except Exception as e:
            logger.error(f"❌ Error saving screenshot: {e}")
            return None, None
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove old data to manage database size"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Remove old snapshots
            cursor.execute('DELETE FROM indicator_snapshots WHERE timestamp < ?', (cutoff_date,))
            deleted_snapshots = cursor.rowcount
            
            # Remove old pattern analysis
            cursor.execute('DELETE FROM pattern_analysis WHERE created_at < ?', (cutoff_date,))
            deleted_patterns = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 Cleaned up {deleted_snapshots} snapshots and {deleted_patterns} patterns")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total counts
            cursor.execute('SELECT COUNT(*) FROM indicator_snapshots')
            total_snapshots = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tracked_symbols WHERE is_active = 1')
            active_symbols = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM pattern_analysis')
            total_patterns = cursor.fetchone()[0]
            
            # Get latest activity
            cursor.execute('SELECT MAX(timestamp) FROM indicator_snapshots')
            latest_snapshot = cursor.fetchone()[0]
            
            # Get data size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size_bytes = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_snapshots': total_snapshots,
                'active_symbols': active_symbols,
                'total_patterns': total_patterns,
                'latest_snapshot': latest_snapshot,
                'database_size_mb': round(db_size_bytes / (1024 * 1024), 2),
                'screenshots_directory': str(self.screenshots_dir),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {}

# Global instance
indicators_history_db = IndicatorsHistoryDatabase()

def get_indicators_database() -> IndicatorsHistoryDatabase:
    """Get the global indicators history database instance"""
    return indicators_history_db