#!/usr/bin/env python3
"""
Comprehensive Data Pipeline System for Into The Cryptoverse Data Extraction
Designed for AI Agent Integration and Real-time Analysis

This system provides a complete data pipeline that extracts, processes, and serves
data from Into The Cryptoverse platform for AI Agent consumption.
"""

import asyncio
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataExtractionResult:
    """Standard data extraction result format"""
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    confidence_score: float = 1.0

class DatabaseManager:
    """Manages all database operations for the data pipeline"""
    
    def __init__(self, db_path: str = "cryptoverse_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for all data sources
        tables = [
            """
            CREATE TABLE IF NOT EXISTS crypto_risk_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                summary_risk REAL NOT NULL,
                price_risk REAL NOT NULL,
                onchain_risk REAL NOT NULL,
                social_risk REAL NOT NULL,
                risk_level TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS macro_recession_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                employment_risk REAL NOT NULL,
                national_income_product_risk REAL NOT NULL,
                production_business_risk REAL NOT NULL,
                overall_recession_risk REAL NOT NULL,
                recession_probability TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS screener_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                fiat_risk REAL NOT NULL,
                risk_band TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS dominance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                btc_dominance_with_stables REAL NOT NULL,
                btc_dominance_without_stables REAL NOT NULL,
                trend TEXT NOT NULL,
                market_phase TEXT NOT NULL,
                altcoin_season_probability REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS market_valuation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                current_market_cap REAL NOT NULL,
                trend_market_cap REAL NOT NULL,
                undervaluation_percent REAL NOT NULL,
                valuation_signal TEXT NOT NULL,
                fair_value_gap REAL NOT NULL,
                investment_action TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS supply_profit_loss (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                supply_in_profit_percent REAL NOT NULL,
                supply_in_loss_percent REAL NOT NULL,
                signal_strength TEXT NOT NULL,
                market_stage TEXT NOT NULL,
                historical_percentile INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS time_spent_risk_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                risk_band TEXT NOT NULL,
                percentage REAL NOT NULL,
                days_count INTEGER NOT NULL,
                coefficient REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS portfolio_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                performance_1d REAL NOT NULL,
                performance_7d REAL NOT NULL,
                performance_30d REAL NOT NULL,
                performance_ytd REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS crypto_heatmap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                performance_1d REAL NOT NULL,
                performance_7d REAL NOT NULL,
                performance_30d REAL NOT NULL,
                market_cap REAL NOT NULL,
                volume_24h REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logarithmic_regression (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                current_price REAL NOT NULL,
                lower_band REAL NOT NULL,
                upper_band REAL NOT NULL,
                position_in_band REAL NOT NULL,
                regression_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS workbench_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                formula TEXT NOT NULL,
                result REAL NOT NULL,
                confidence REAL NOT NULL,
                interpretation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                message TEXT NOT NULL,
                supporting_data TEXT,
                action_recommendation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_crypto_risk_timestamp ON crypto_risk_indicators(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_screener_symbol_timestamp ON screener_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_supply_symbol_timestamp ON supply_profit_loss(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_time_spent_symbol ON time_spent_risk_bands(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_heatmap_timestamp ON crypto_heatmap(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_ai_insights_timestamp ON ai_insights(timestamp)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert data into specified table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare insert statement
            columns = list(data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, list(data.values()))
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data into {table}: {e}")
            return False
    
    def get_latest_data(self, table: str, symbol: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get latest data from specified table"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if symbol:
                sql = f"SELECT * FROM {table} WHERE symbol = ? ORDER BY timestamp DESC LIMIT 1"
                cursor.execute(sql, (symbol,))
            else:
                sql = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1"
                cursor.execute(sql)
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting latest data from {table}: {e}")
            return None
    
    def get_historical_data(self, table: str, days: int = 30, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical data from specified table"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if symbol:
                sql = f"SELECT * FROM {table} WHERE symbol = ? AND timestamp >= ? ORDER BY timestamp DESC"
                cursor.execute(sql, (symbol, cutoff_date))
            else:
                sql = f"SELECT * FROM {table} WHERE timestamp >= ? ORDER BY timestamp DESC"
                cursor.execute(sql, (cutoff_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting historical data from {table}: {e}")
            return []

class DataExtractor:
    """Base class for all data extractors"""
    
    def __init__(self, session=None):
        self.session = session
        self.db_manager = DatabaseManager()
    
    def extract(self) -> DataExtractionResult:
        """Extract data - to be implemented by subclasses"""
        raise NotImplementedError
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted data"""
        return data is not None and len(data) > 0

class MockDataExtractor(DataExtractor):
    """Mock data extractor for testing and development"""
    
    def __init__(self, source_name: str):
        super().__init__()
        self.source_name = source_name
    
    def extract(self) -> DataExtractionResult:
        """Extract mock data for testing"""
        mock_data = self.generate_mock_data()
        
        return DataExtractionResult(
            source=self.source_name,
            timestamp=datetime.now(),
            data=mock_data,
            success=True,
            confidence_score=0.95
        )
    
    def generate_mock_data(self) -> Dict[str, Any]:
        """Generate realistic mock data based on source type"""
        import random
        
        if self.source_name == "crypto_risk_indicators":
            return {
                "timestamp": datetime.now().isoformat(),
                "summary_risk": round(random.uniform(0.1, 0.8), 3),
                "price_risk": round(random.uniform(0.1, 0.9), 3),
                "onchain_risk": round(random.uniform(0.1, 0.7), 3),
                "social_risk": round(random.uniform(0.01, 0.2), 3),
                "risk_level": random.choice(["Low", "Moderate", "High"])
            }
        
        elif self.source_name == "screener_data":
            symbols = ["BTC", "ETH", "XRP", "SOL", "BNB", "ADA", "DOGE"]
            return {
                "timestamp": datetime.now().isoformat(),
                "symbols": [
                    {
                        "symbol": symbol,
                        "price": round(random.uniform(100, 100000), 2),
                        "fiat_risk": round(random.uniform(0.1, 0.9), 3),
                        "risk_band": f"{random.randint(0, 9)}.{random.randint(0, 9)}-{random.randint(0, 9)}.{random.randint(0, 9)}",
                        "risk_level": random.choice(["Low", "Moderate", "High"])
                    }
                    for symbol in symbols
                ]
            }
        
        elif self.source_name == "dominance_data":
            return {
                "timestamp": datetime.now().isoformat(),
                "btc_dominance_with_stables": round(random.uniform(55, 70), 2),
                "btc_dominance_without_stables": round(random.uniform(60, 75), 2),
                "trend": random.choice(["increasing", "decreasing", "stable"]),
                "market_phase": random.choice(["btc_dominance_phase", "consolidation_phase", "altcoin_rotation_phase"]),
                "altcoin_season_probability": round(random.uniform(0.1, 0.9), 2)
            }
        
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "value": round(random.uniform(0, 100), 2),
                "status": "active"
            }

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.extractors = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        
        # Initialize extractors (using mock extractors for now)
        self.init_extractors()
        
        # Schedule data extraction
        self.schedule_extractions()
    
    def init_extractors(self):
        """Initialize all data extractors"""
        extractor_configs = [
            ("crypto_risk_indicators", 15),  # Every 15 minutes
            ("macro_recession_indicators", 60),  # Every hour
            ("screener_data", 5),  # Every 5 minutes
            ("dominance_data", 30),  # Every 30 minutes
            ("market_valuation", 60),  # Every hour
            ("supply_profit_loss", 30),  # Every 30 minutes
            ("time_spent_risk_bands", 1440),  # Daily
            ("portfolio_performance", 60),  # Every hour
            ("crypto_heatmap", 15),  # Every 15 minutes
            ("logarithmic_regression", 60),  # Every hour
            ("workbench_indicators", 30)  # Every 30 minutes
        ]
        
        for source_name, interval_minutes in extractor_configs:
            self.extractors[source_name] = {
                "extractor": MockDataExtractor(source_name),
                "interval": interval_minutes,
                "last_run": None
            }
            
            logger.info(f"Initialized extractor for {source_name} (interval: {interval_minutes} minutes)")
    
    def schedule_extractions(self):
        """Schedule all data extractions"""
        for source_name, config in self.extractors.items():
            interval = config["interval"]
            
            if interval <= 60:  # For frequent updates
                schedule.every(interval).minutes.do(self.extract_data, source_name)
            else:  # For daily updates
                schedule.every().day.do(self.extract_data, source_name)
            
            logger.info(f"Scheduled {source_name} extraction every {interval} minutes")
    
    def extract_data(self, source_name: str) -> bool:
        """Extract data from a specific source"""
        try:
            config = self.extractors.get(source_name)
            if not config:
                logger.error(f"No extractor found for {source_name}")
                return False
            
            extractor = config["extractor"]
            result = extractor.extract()
            
            if result.success:
                # Store data in database
                success = self.store_extraction_result(source_name, result)
                
                if success:
                    config["last_run"] = datetime.now()
                    logger.info(f"Successfully extracted and stored data for {source_name}")
                    
                    # Trigger AI analysis
                    self.trigger_ai_analysis(source_name, result.data)
                    
                    return True
                else:
                    logger.error(f"Failed to store data for {source_name}")
                    return False
            else:
                logger.error(f"Extraction failed for {source_name}: {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error in extract_data for {source_name}: {e}")
            return False
    
    def store_extraction_result(self, source_name: str, result: DataExtractionResult) -> bool:
        """Store extraction result in database"""
        try:
            if source_name == "screener_data":
                # Handle screener data with multiple symbols
                for symbol_data in result.data.get("symbols", []):
                    data_to_store = {
                        "timestamp": result.timestamp.isoformat(),
                        "symbol": symbol_data["symbol"],
                        "price": symbol_data["price"],
                        "fiat_risk": symbol_data["fiat_risk"],
                        "risk_band": symbol_data["risk_band"],
                        "risk_level": symbol_data["risk_level"]
                    }
                    self.db_manager.insert_data(source_name, data_to_store)
                return True
            else:
                # Handle single data point
                data_to_store = result.data.copy()
                data_to_store["timestamp"] = result.timestamp.isoformat()
                return self.db_manager.insert_data(source_name, data_to_store)
                
        except Exception as e:
            logger.error(f"Error storing extraction result for {source_name}: {e}")
            return False
    
    def trigger_ai_analysis(self, source_name: str, data: Dict[str, Any]):
        """Trigger AI analysis of extracted data"""
        try:
            # Submit AI analysis task to thread pool
            self.executor.submit(self.perform_ai_analysis, source_name, data)
            
        except Exception as e:
            logger.error(f"Error triggering AI analysis for {source_name}: {e}")
    
    def perform_ai_analysis(self, source_name: str, data: Dict[str, Any]):
        """Perform AI analysis on extracted data"""
        try:
            insights = self.generate_insights(source_name, data)
            
            for insight in insights:
                insight_data = {
                    "timestamp": datetime.now().isoformat(),
                    "insight_type": insight["type"],
                    "confidence": insight["confidence"],
                    "message": insight["message"],
                    "supporting_data": json.dumps(insight.get("supporting_data", {})),
                    "action_recommendation": insight.get("action", "none")
                }
                
                self.db_manager.insert_data("ai_insights", insight_data)
            
            logger.info(f"Generated {len(insights)} insights for {source_name}")
            
        except Exception as e:
            logger.error(f"Error in AI analysis for {source_name}: {e}")
    
    def generate_insights(self, source_name: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI insights from data"""
        insights = []
        
        try:
            if source_name == "crypto_risk_indicators":
                summary_risk = data.get("summary_risk", 0)
                
                if summary_risk < 0.3:
                    insights.append({
                        "type": "opportunity",
                        "confidence": 0.8,
                        "message": f"Low overall crypto risk ({summary_risk:.3f}) suggests favorable market conditions for accumulation",
                        "action": "buy",
                        "supporting_data": {"summary_risk": summary_risk}
                    })
                elif summary_risk > 0.7:
                    insights.append({
                        "type": "warning",
                        "confidence": 0.9,
                        "message": f"High overall crypto risk ({summary_risk:.3f}) indicates caution warranted",
                        "action": "reduce_exposure",
                        "supporting_data": {"summary_risk": summary_risk}
                    })
                
                # Check for risk component divergence
                price_risk = data.get("price_risk", 0)
                onchain_risk = data.get("onchain_risk", 0)
                
                if abs(price_risk - onchain_risk) > 0.2:
                    insights.append({
                        "type": "divergence",
                        "confidence": 0.7,
                        "message": f"Significant divergence between price risk ({price_risk:.3f}) and on-chain risk ({onchain_risk:.3f})",
                        "action": "monitor",
                        "supporting_data": {"price_risk": price_risk, "onchain_risk": onchain_risk}
                    })
            
            elif source_name == "dominance_data":
                btc_dom = data.get("btc_dominance_without_stables", 0)
                trend = data.get("trend", "stable")
                
                if btc_dom > 65 and trend == "increasing":
                    insights.append({
                        "type": "market_phase",
                        "confidence": 0.8,
                        "message": f"BTC dominance ({btc_dom:.1f}%) increasing - altcoin weakness expected",
                        "action": "focus_btc",
                        "supporting_data": {"btc_dominance": btc_dom, "trend": trend}
                    })
                elif btc_dom < 55 and trend == "decreasing":
                    insights.append({
                        "type": "market_phase",
                        "confidence": 0.8,
                        "message": f"BTC dominance ({btc_dom:.1f}%) decreasing - altcoin season potential",
                        "action": "consider_altcoins",
                        "supporting_data": {"btc_dominance": btc_dom, "trend": trend}
                    })
            
            elif source_name == "screener_data":
                symbols = data.get("symbols", [])
                if symbols:
                    high_risk_symbols = [s for s in symbols if s.get("fiat_risk", 0) > 0.7]
                    low_risk_symbols = [s for s in symbols if s.get("fiat_risk", 0) < 0.3]
                    
                    if len(high_risk_symbols) > len(symbols) * 0.6:
                        insights.append({
                            "type": "market_warning",
                            "confidence": 0.8,
                            "message": f"Majority of symbols ({len(high_risk_symbols)}/{len(symbols)}) showing high risk",
                            "action": "reduce_exposure",
                            "supporting_data": {"high_risk_count": len(high_risk_symbols), "total_symbols": len(symbols)}
                        })
                    
                    if len(low_risk_symbols) > len(symbols) * 0.4:
                        insights.append({
                            "type": "market_opportunity",
                            "confidence": 0.7,
                            "message": f"Multiple symbols ({len(low_risk_symbols)}/{len(symbols)}) showing low risk - accumulation opportunity",
                            "action": "accumulate",
                            "supporting_data": {"low_risk_count": len(low_risk_symbols), "total_symbols": len(symbols)}
                        })
            
        except Exception as e:
            logger.error(f"Error generating insights for {source_name}: {e}")
        
        return insights
    
    def start(self):
        """Start the data pipeline"""
        self.running = True
        logger.info("Data pipeline started")
        
        # Run initial extractions
        for source_name in self.extractors.keys():
            self.extract_data(source_name)
        
        # Start scheduler
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the data pipeline"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Data pipeline stopped")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        status = {
            "running": self.running,
            "extractors": {},
            "last_update": datetime.now().isoformat()
        }
        
        for source_name, config in self.extractors.items():
            status["extractors"][source_name] = {
                "interval_minutes": config["interval"],
                "last_run": config["last_run"].isoformat() if config["last_run"] else None,
                "next_run": self.calculate_next_run(source_name)
            }
        
        return status
    
    def calculate_next_run(self, source_name: str) -> Optional[str]:
        """Calculate next scheduled run for a source"""
        config = self.extractors.get(source_name)
        if not config or not config["last_run"]:
            return None
        
        next_run = config["last_run"] + timedelta(minutes=config["interval"])
        return next_run.isoformat()

# Flask API for data access
app = Flask(__name__)
CORS(app)

# Global pipeline instance
pipeline = None
db_manager = DatabaseManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pipeline_running": pipeline.running if pipeline else False
    })

@app.route('/api/pipeline/status', methods=['GET'])
def get_pipeline_status():
    """Get pipeline status"""
    if not pipeline:
        return jsonify({"error": "Pipeline not initialized"}), 500
    
    return jsonify({
        "status": "success",
        "data": pipeline.get_pipeline_status()
    })

@app.route('/api/crypto-risk-indicators', methods=['GET'])
def get_crypto_risk_indicators():
    """Get latest crypto risk indicators"""
    try:
        data = db_manager.get_latest_data("crypto_risk_indicators")
        if not data:
            return jsonify({"error": "No data available"}), 404
        
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        logger.error(f"Error in crypto risk indicators endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/screener', methods=['GET'])
def get_screener_data():
    """Get latest screener data"""
    try:
        # Get latest timestamp
        latest_data = db_manager.get_latest_data("screener_data")
        if not latest_data:
            return jsonify({"error": "No data available"}), 404
        
        latest_timestamp = latest_data["timestamp"]
        
        # Get all symbols for latest timestamp
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM screener_data WHERE timestamp = ? ORDER BY symbol",
            (latest_timestamp,)
        )
        
        symbols_data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "timestamp": latest_timestamp,
                "symbols": symbols_data,
                "total_symbols": len(symbols_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in screener endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/dominance', methods=['GET'])
def get_dominance_data():
    """Get latest dominance data"""
    try:
        data = db_manager.get_latest_data("dominance_data")
        if not data:
            return jsonify({"error": "No data available"}), 404
        
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        logger.error(f"Error in dominance endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/ai-insights', methods=['GET'])
def get_ai_insights():
    """Get latest AI insights"""
    try:
        # Get insights from last 24 hours
        cutoff_date = (datetime.now() - timedelta(hours=24)).isoformat()
        
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM ai_insights WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 50",
            (cutoff_date,)
        )
        
        insights = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse supporting_data JSON
        for insight in insights:
            if insight.get("supporting_data"):
                try:
                    insight["supporting_data"] = json.loads(insight["supporting_data"])
                except:
                    insight["supporting_data"] = {}
        
        return jsonify({
            "status": "success",
            "data": {
                "insights": insights,
                "total_count": len(insights),
                "timeframe": "24_hours"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in AI insights endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/historical/<table_name>', methods=['GET'])
def get_historical_data(table_name):
    """Get historical data for any table"""
    try:
        days = request.args.get('days', 30, type=int)
        symbol = request.args.get('symbol')
        
        data = db_manager.get_historical_data(table_name, days, symbol)
        
        return jsonify({
            "status": "success",
            "data": {
                "historical_data": data,
                "days": days,
                "symbol": symbol,
                "count": len(data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in historical data endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/extract/<source_name>', methods=['POST'])
def manual_extract(source_name):
    """Manually trigger data extraction for a source"""
    try:
        if not pipeline:
            return jsonify({"error": "Pipeline not initialized"}), 500
        
        if source_name not in pipeline.extractors:
            return jsonify({"error": f"Unknown source: {source_name}"}), 400
        
        success = pipeline.extract_data(source_name)
        
        return jsonify({
            "status": "success" if success else "failed",
            "source": source_name,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in manual extract endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

def start_pipeline():
    """Start the data pipeline in a separate thread"""
    global pipeline
    pipeline = DataPipeline()
    
    # Start pipeline in background thread
    pipeline_thread = threading.Thread(target=pipeline.start, daemon=True)
    pipeline_thread.start()
    
    logger.info("Data pipeline started in background thread")

if __name__ == '__main__':
    # Start the data pipeline
    start_pipeline()
    
    # Start the Flask API
    logger.info("Starting Flask API server...")
    app.run(host='0.0.0.0', port=5005, debug=False)

