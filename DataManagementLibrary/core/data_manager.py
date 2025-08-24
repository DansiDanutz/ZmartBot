#!/usr/bin/env python3
"""
📊 Data Manager - Central Data Management System
Organizes and manages all data sources in the ZmartBot ecosystem
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
import pickle
import hashlib
import logging
from collections import defaultdict
import asyncio
import aiofiles
import yaml

logger = logging.getLogger(__name__)

# ==================== Data Models ====================

class DataType(Enum):
    """Types of data in the system"""
    HISTORICAL_PRICE = "historical_price"
    LIQUIDATION_MAP = "liquidation_map"
    LIQUIDATION_HEATMAP = "liquidation_heatmap"
    RISK_METRIC = "risk_metric"
    CRYPTOMETER = "cryptometer"
    PATTERN = "pattern"
    WIN_RATE = "win_rate"
    TECHNICAL_INDICATOR = "technical_indicator"
    MARKET_SENTIMENT = "market_sentiment"
    AIRTABLE_RECORD = "airtable_record"
    PROFESSIONAL_REPORT = "professional_report"
    IMAGE = "image"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"

class DataSource(Enum):
    """Data sources"""
    COINMARKETCAP = "coinmarketcap"
    KINGFISHER = "kingfisher"
    CRYPTOMETER = "cryptometer"
    RISKMETRIC = "riskmetric"
    AIRTABLE = "airtable"
    KUCOIN = "kucoin"
    BINANCE = "binance"
    OPENAI = "openai"
    MANUAL = "manual"
    CALCULATED = "calculated"

@dataclass
class DataEntry:
    """Represents a single data entry"""
    id: str
    symbol: str
    data_type: DataType
    source: DataSource
    timestamp: datetime
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    checksum: Optional[str] = None
    version: int = 1
    tags: List[str] = field(default_factory=list)
    quality_score: float = 1.0

@dataclass
class DataCollection:
    """Collection of related data entries"""
    name: str
    description: str
    entries: List[DataEntry]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================== Main Data Manager ====================

class DataManager:
    """
    Central Data Management System
    Handles all data organization, storage, and retrieval
    """
    
    def __init__(self, base_path: str = None):
        """Initialize Data Manager"""
        
        # Set up paths
        self.base_path = Path(base_path) if base_path else Path.home() / "ZmartBot" / "DataLibrary"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        self.directories = {
            "historical": self.base_path / "historical",
            "realtime": self.base_path / "realtime",
            "patterns": self.base_path / "patterns",
            "reports": self.base_path / "reports",
            "images": self.base_path / "images",
            "cache": self.base_path / "cache",
            "indexes": self.base_path / "indexes",
            "backups": self.base_path / "backups",
            "exports": self.base_path / "exports"
        }
        
        for dir_path in self.directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.base_path / "data_library.db"
        self._init_database()
        
        # Initialize indexes
        self.indexes = {
            "symbol": defaultdict(list),
            "type": defaultdict(list),
            "source": defaultdict(list),
            "date": defaultdict(list),
            "tag": defaultdict(list)
        }
        
        # Load existing indexes
        self._load_indexes()
        
        # Data cache
        self.cache = {}
        self.cache_size = 100  # Maximum cache entries
        
        logger.info(f"📊 Data Manager initialized at {self.base_path}")
    
    def _init_database(self):
        """Initialize SQLite database for metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_entries (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                data_type TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                file_path TEXT,
                checksum TEXT,
                version INTEGER DEFAULT 1,
                quality_score REAL DEFAULT 1.0,
                metadata TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                entry_count INTEGER,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                relationship_type TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES data_entries(id),
                FOREIGN KEY (child_id) REFERENCES data_entries(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON data_entries(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON data_entries(data_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON data_entries(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON data_entries(timestamp)")
        
        conn.commit()
        conn.close()
    
    # ==================== Data Import Methods ====================
    
    async def import_historical_data(self, file_path: str, 
                                   symbol: str = None,
                                   data_type: DataType = DataType.HISTORICAL_PRICE) -> DataEntry:
        """Import historical data from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract symbol from filename if not provided
        if not symbol:
            symbol = self._extract_symbol_from_filename(file_path.name)
        
        # Determine file type and read data
        if file_path.suffix == '.csv':
            data = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif file_path.suffix == '.xlsx':
            data = pd.read_excel(file_path)
        else:
            # Read as text
            with open(file_path, 'r') as f:
                data = f.read()
        
        # Create data entry
        entry = DataEntry(
            id=self._generate_id(symbol, data_type, datetime.now()),
            symbol=symbol,
            data_type=data_type,
            source=DataSource.COINMARKETCAP,  # Default, can be overridden
            timestamp=datetime.now(),
            data=data,
            file_path=str(file_path),
            checksum=self._calculate_checksum(file_path),
            metadata={
                "original_filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "import_date": datetime.now().isoformat()
            }
        )
        
        # Store in appropriate directory
        target_path = self.directories["historical"] / symbol / file_path.name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path != target_path:
            import shutil
            shutil.copy2(file_path, target_path)
            entry.file_path = str(target_path)
        
        # Save to database
        self._save_entry(entry)
        
        # Update indexes
        self._update_indexes(entry)
        
        logger.info(f"✅ Imported {symbol} data from {file_path.name}")
        
        return entry
    
    def import_kingfisher_data(self, airtable_record: Dict[str, Any]) -> DataEntry:
        """Import Kingfisher data from Airtable record"""
        fields = airtable_record.get('fields', {})
        symbol = fields.get('Symbol', 'UNKNOWN')
        
        # Create comprehensive data package
        data_package = {
            "liquidation_map": fields.get('LiquidationMap'),
            "liquidation_heatmap": fields.get('LiquidationHeatmap'),
            "short_term_ratio": fields.get('ShortTermRatio'),
            "long_term_ratio": fields.get('LongTermRatio'),
            "clusters": {
                "cluster_minus_2": fields.get('Liqcluster-2'),
                "cluster_minus_1": fields.get('Liqcluster-1'),
                "cluster_plus_1": fields.get('Liqcluster+1'),
                "cluster_plus_2": fields.get('Liqcluster+2')
            },
            "win_rates": {
                "24h": fields.get('WinRate_24h'),
                "7d": fields.get('WinRate_7d'),
                "1m": fields.get('WinRate_1m')
            },
            "score": fields.get('Score'),
            "report": fields.get('Report'),
            "current_price": fields.get('CurrentPrice'),
            "last_updated": fields.get('LastUpdated')
        }
        
        entry = DataEntry(
            id=self._generate_id(symbol, DataType.AIRTABLE_RECORD, datetime.now()),
            symbol=symbol,
            data_type=DataType.AIRTABLE_RECORD,
            source=DataSource.KINGFISHER,
            timestamp=datetime.now(),
            data=data_package,
            metadata={
                "record_id": airtable_record.get('id'),
                "has_report": bool(fields.get('Report')),
                "has_win_rates": bool(fields.get('WinRate_24h'))
            },
            tags=["kingfisher", "liquidation", "airtable"]
        )
        
        self._save_entry(entry)
        self._update_indexes(entry)
        
        return entry
    
    def import_pattern_data(self, pattern_analysis: Dict[str, Any]) -> DataEntry:
        """Import pattern analysis data"""
        symbol = pattern_analysis.get('symbol', 'UNKNOWN')
        
        entry = DataEntry(
            id=self._generate_id(symbol, DataType.PATTERN, datetime.now()),
            symbol=symbol,
            data_type=DataType.PATTERN,
            source=DataSource.CALCULATED,
            timestamp=datetime.now(),
            data=pattern_analysis,
            metadata={
                "pattern_count": len(pattern_analysis.get('detected_patterns', [])),
                "pattern_score": pattern_analysis.get('pattern_score', 0),
                "confidence": pattern_analysis.get('confidence_level', 0)
            },
            tags=["pattern", "analysis", "unified"]
        )
        
        self._save_entry(entry)
        self._update_indexes(entry)
        
        return entry
    
    # ==================== Data Retrieval Methods ====================
    
    def get_latest(self, symbol: str, data_type: DataType = None) -> Optional[DataEntry]:
        """Get latest data entry for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if data_type:
            query = """
                SELECT * FROM data_entries 
                WHERE symbol = ? AND data_type = ?
                ORDER BY timestamp DESC LIMIT 1
            """
            cursor.execute(query, (symbol, data_type.value))
        else:
            query = """
                SELECT * FROM data_entries 
                WHERE symbol = ?
                ORDER BY timestamp DESC LIMIT 1
            """
            cursor.execute(query, (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_entry(row)
        return None
    
    def get_historical(self, symbol: str, 
                      start_date: datetime = None,
                      end_date: datetime = None,
                      data_type: DataType = None) -> List[DataEntry]:
        """Get historical data entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM data_entries WHERE symbol = ?"
        params = [symbol]
        
        if data_type:
            query += " AND data_type = ?"
            params.append(data_type.value)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def search(self, query: str = None,
              symbols: List[str] = None,
              data_types: List[DataType] = None,
              sources: List[DataSource] = None,
              tags: List[str] = None,
              start_date: datetime = None,
              end_date: datetime = None,
              limit: int = 100) -> List[DataEntry]:
        """Advanced search functionality"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if symbols:
            placeholders = ','.join(['?' for _ in symbols])
            conditions.append(f"symbol IN ({placeholders})")
            params.extend(symbols)
        
        if data_types:
            placeholders = ','.join(['?' for _ in data_types])
            conditions.append(f"data_type IN ({placeholders})")
            params.extend([dt.value for dt in data_types])
        
        if sources:
            placeholders = ','.join(['?' for _ in sources])
            conditions.append(f"source IN ({placeholders})")
            params.extend([s.value for s in sources])
        
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            conditions.append(f"({' OR '.join(tag_conditions)})")
        
        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date.isoformat())
        
        # Build query
        if conditions:
            query = f"SELECT * FROM data_entries WHERE {' AND '.join(conditions)}"
        else:
            query = "SELECT * FROM data_entries"
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    # ==================== Data Aggregation Methods ====================
    
    def create_collection(self, name: str, description: str,
                         entries: List[DataEntry]) -> DataCollection:
        """Create a collection of related data entries"""
        collection = DataCollection(
            name=name,
            description=description,
            entries=entries,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        collection_id = self._generate_id(name, "collection", datetime.now())
        
        cursor.execute("""
            INSERT INTO collections (id, name, description, entry_count, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            collection_id,
            name,
            description,
            len(entries),
            json.dumps(asdict(collection.metadata))
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Created collection '{name}' with {len(entries)} entries")
        
        return collection
    
    def aggregate_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """Aggregate all data for a symbol"""
        entries = self.search(symbols=[symbol])
        
        aggregated = {
            "symbol": symbol,
            "total_entries": len(entries),
            "data_types": {},
            "sources": {},
            "latest_update": None,
            "date_range": None
        }
        
        if entries:
            # Group by data type
            for entry in entries:
                dt = entry.data_type.value
                if dt not in aggregated["data_types"]:
                    aggregated["data_types"][dt] = []
                aggregated["data_types"][dt].append(entry)
            
            # Group by source
            for entry in entries:
                src = entry.source.value
                if src not in aggregated["sources"]:
                    aggregated["sources"][src] = []
                aggregated["sources"][src].append(entry)
            
            # Find date range
            timestamps = [e.timestamp for e in entries]
            aggregated["latest_update"] = max(timestamps)
            aggregated["date_range"] = (min(timestamps), max(timestamps))
        
        return aggregated
    
    # ==================== Data Export Methods ====================
    
    def export_to_csv(self, entries: List[DataEntry], 
                     output_path: str = None) -> str:
        """Export data entries to CSV"""
        if not output_path:
            output_path = self.directories["exports"] / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Convert entries to DataFrame
        data = []
        for entry in entries:
            data.append({
                "id": entry.id,
                "symbol": entry.symbol,
                "data_type": entry.data_type.value,
                "source": entry.source.value,
                "timestamp": entry.timestamp,
                "quality_score": entry.quality_score,
                "tags": ",".join(entry.tags) if entry.tags else ""
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        logger.info(f"✅ Exported {len(entries)} entries to {output_path}")
        
        return str(output_path)
    
    def export_to_json(self, entries: List[DataEntry],
                      output_path: str = None) -> str:
        """Export data entries to JSON"""
        if not output_path:
            output_path = self.directories["exports"] / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert entries to JSON-serializable format
        data = []
        for entry in entries:
            entry_dict = asdict(entry)
            # Convert enums to strings
            entry_dict["data_type"] = entry.data_type.value
            entry_dict["source"] = entry.source.value
            # Convert datetime to string
            entry_dict["timestamp"] = entry.timestamp.isoformat()
            data.append(entry_dict)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"✅ Exported {len(entries)} entries to {output_path}")
        
        return str(output_path)
    
    # ==================== Data Quality Methods ====================
    
    def validate_data(self, entry: DataEntry) -> Tuple[bool, List[str]]:
        """Validate data entry quality"""
        issues = []
        
        # Check required fields
        if not entry.symbol:
            issues.append("Missing symbol")
        
        if not entry.data:
            issues.append("No data content")
        
        # Check data integrity
        if entry.file_path and Path(entry.file_path).exists():
            current_checksum = self._calculate_checksum(Path(entry.file_path))
            if entry.checksum and current_checksum != entry.checksum:
                issues.append("Checksum mismatch - file may be corrupted")
        
        # Check timestamp validity
        if entry.timestamp > datetime.now():
            issues.append("Future timestamp detected")
        
        # Update quality score
        if issues:
            entry.quality_score = max(0.1, 1.0 - (len(issues) * 0.2))
        else:
            entry.quality_score = 1.0
        
        return len(issues) == 0, issues
    
    def cleanup_duplicates(self, symbol: str = None):
        """Remove duplicate data entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            query = """
                DELETE FROM data_entries 
                WHERE rowid NOT IN (
                    SELECT MIN(rowid) 
                    FROM data_entries 
                    WHERE symbol = ?
                    GROUP BY symbol, data_type, checksum
                )
            """
            cursor.execute(query, (symbol,))
        else:
            query = """
                DELETE FROM data_entries 
                WHERE rowid NOT IN (
                    SELECT MIN(rowid) 
                    FROM data_entries 
                    GROUP BY symbol, data_type, checksum
                )
            """
            cursor.execute(query)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"🧹 Removed {deleted} duplicate entries")
        
        return deleted
    
    # ==================== Helper Methods ====================
    
    def _generate_id(self, *args) -> str:
        """Generate unique ID"""
        content = "_".join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _extract_symbol_from_filename(self, filename: str) -> str:
        """Extract symbol from filename"""
        # Common patterns
        patterns = [
            r"([A-Z]+)[-_]",  # BTC-USDT or BTC_USDT
            r"^([A-Z]+)",     # BTC at start
            r"([A-Za-z]+)_"   # Bitcoin_
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1).upper()
        
        return "UNKNOWN"
    
    def _save_entry(self, entry: DataEntry):
        """Save data entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO data_entries 
            (id, symbol, data_type, source, timestamp, file_path, checksum, 
             version, quality_score, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.symbol,
            entry.data_type.value,
            entry.source.value,
            entry.timestamp.isoformat(),
            entry.file_path,
            entry.checksum,
            entry.version,
            entry.quality_score,
            json.dumps(entry.metadata),
            json.dumps(entry.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def _update_indexes(self, entry: DataEntry):
        """Update in-memory indexes"""
        self.indexes["symbol"][entry.symbol].append(entry.id)
        self.indexes["type"][entry.data_type.value].append(entry.id)
        self.indexes["source"][entry.source.value].append(entry.id)
        self.indexes["date"][entry.timestamp.date()].append(entry.id)
        
        for tag in entry.tags:
            self.indexes["tag"][tag].append(entry.id)
    
    def _load_indexes(self):
        """Load indexes from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, symbol, data_type, source, timestamp, tags FROM data_entries")
        
        for row in cursor.fetchall():
            entry_id, symbol, data_type, source, timestamp, tags_json = row
            
            self.indexes["symbol"][symbol].append(entry_id)
            self.indexes["type"][data_type].append(entry_id)
            self.indexes["source"][source].append(entry_id)
            
            # Parse timestamp
            ts = datetime.fromisoformat(timestamp)
            self.indexes["date"][ts.date()].append(entry_id)
            
            # Parse tags
            if tags_json:
                tags = json.loads(tags_json)
                for tag in tags:
                    self.indexes["tag"][tag].append(entry_id)
        
        conn.close()
    
    def _row_to_entry(self, row) -> DataEntry:
        """Convert database row to DataEntry"""
        # Assuming row has columns in order matching the table structure
        entry_data = {
            "id": row[0],
            "symbol": row[1],
            "data_type": DataType(row[2]),
            "source": DataSource(row[3]),
            "timestamp": datetime.fromisoformat(row[4]),
            "file_path": row[5],
            "checksum": row[6],
            "version": row[7],
            "quality_score": row[8],
            "metadata": json.loads(row[9]) if row[9] else {},
            "tags": json.loads(row[10]) if row[10] else [],
            "data": None  # Would need to load from file or cache
        }
        
        # Load actual data if file exists
        if entry_data["file_path"] and Path(entry_data["file_path"]).exists():
            # Load based on file type
            file_path = Path(entry_data["file_path"])
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    entry_data["data"] = json.load(f)
            elif file_path.suffix == '.csv':
                entry_data["data"] = pd.read_csv(file_path)
            else:
                with open(file_path, 'r') as f:
                    entry_data["data"] = f.read()
        
        return DataEntry(**entry_data)
    
    # ==================== Statistics Methods ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data library statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            "total_entries": 0,
            "symbols": [],
            "data_types": {},
            "sources": {},
            "date_range": None,
            "storage_size": 0
        }
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM data_entries")
        stats["total_entries"] = cursor.fetchone()[0]
        
        # Unique symbols
        cursor.execute("SELECT DISTINCT symbol FROM data_entries")
        stats["symbols"] = [row[0] for row in cursor.fetchall()]
        
        # Count by data type
        cursor.execute("SELECT data_type, COUNT(*) FROM data_entries GROUP BY data_type")
        stats["data_types"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count by source
        cursor.execute("SELECT source, COUNT(*) FROM data_entries GROUP BY source")
        stats["sources"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Date range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM data_entries")
        min_date, max_date = cursor.fetchone()
        if min_date and max_date:
            stats["date_range"] = (min_date, max_date)
        
        conn.close()
        
        # Calculate storage size
        for dir_path in self.directories.values():
            if dir_path.exists():
                size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                stats["storage_size"] += size
        
        return stats

# ==================== Quick Access Functions ====================

def get_data_manager(base_path: str = None) -> DataManager:
    """Get or create singleton DataManager instance"""
    if not hasattr(get_data_manager, "_instance"):
        get_data_manager._instance = DataManager(base_path)
    return get_data_manager._instance

async def quick_import(file_path: str, symbol: str = None) -> DataEntry:
    """Quick import function"""
    dm = get_data_manager()
    return await dm.import_historical_data(file_path, symbol)

def quick_search(symbol: str = None, data_type: DataType = None) -> List[DataEntry]:
    """Quick search function"""
    dm = get_data_manager()
    return dm.search(symbols=[symbol] if symbol else None, 
                    data_types=[data_type] if data_type else None)