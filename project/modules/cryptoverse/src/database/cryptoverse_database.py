#!/usr/bin/env python3
"""
Cryptoverse Database Manager
Manages all database operations for Into The Cryptoverse data extraction
Based on the comprehensive data pipeline system from the package
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

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

class CryptoverseDatabase:
    """Manages all database operations for the Cryptoverse data pipeline"""
    
    def __init__(self, db_path: str = "cryptoverse_data.db"):
        self.db_path = db_path
        self.init_database()
        logger.info(f"Cryptoverse database initialized: {db_path}")
    
    def init_database(self):
        """Initialize database with all required tables for 21 data sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create tables for all data sources from the package
        tables = [
            # 1. Crypto Risk Indicators
            """
            CREATE TABLE IF NOT EXISTS crypto_risk_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                summary_risk REAL NOT NULL,
                price_risk REAL NOT NULL,
                onchain_risk REAL NOT NULL,
                social_risk REAL NOT NULL,
                risk_level TEXT NOT NULL,
                components TEXT, -- JSON data
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 2. Macro Recession Risk Indicators
            """
            CREATE TABLE IF NOT EXISTS macro_recession_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                employment_risk REAL NOT NULL,
                national_income_product_risk REAL NOT NULL,
                production_business_risk REAL NOT NULL,
                overall_recession_risk REAL NOT NULL,
                recession_probability TEXT NOT NULL,
                components TEXT, -- JSON data
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 3. Real-time Screener Data
            """
            CREATE TABLE IF NOT EXISTS screener_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                fiat_risk REAL NOT NULL,
                risk_band TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                market_cap REAL,
                volume_24h REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 4. Dominance Data
            """
            CREATE TABLE IF NOT EXISTS dominance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                btc_dominance_with_stables REAL NOT NULL,
                btc_dominance_without_stables REAL NOT NULL,
                eth_dominance REAL,
                trend TEXT NOT NULL,
                market_phase TEXT NOT NULL,
                altcoin_season_probability REAL,
                historical_context TEXT, -- JSON data
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 5. Market Valuation Data
            """
            CREATE TABLE IF NOT EXISTS market_valuation_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                mvrv_ratio REAL,
                nvt_ratio REAL,
                puell_multiple REAL,
                pi_cycle_top REAL,
                stock_to_flow_ratio REAL,
                valuation_level TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 6. Supply in Profit/Loss Data
            """
            CREATE TABLE IF NOT EXISTS supply_profit_loss_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                supply_in_profit_percentage REAL NOT NULL,
                supply_in_loss_percentage REAL NOT NULL,
                supply_in_profit_usd REAL,
                supply_in_loss_usd REAL,
                total_supply REAL,
                profitability_trend TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 7. Time Spent in Risk Bands
            """
            CREATE TABLE IF NOT EXISTS time_spent_risk_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                risk_band TEXT NOT NULL,
                days_spent INTEGER NOT NULL,
                percentage_of_time REAL NOT NULL,
                coefficient REAL NOT NULL,
                total_days INTEGER NOT NULL,
                rarity_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 8. Portfolio Performance Data
            """
            CREATE TABLE IF NOT EXISTS portfolio_performance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                portfolio_name TEXT NOT NULL,
                total_value_usd REAL NOT NULL,
                performance_24h REAL NOT NULL,
                performance_7d REAL NOT NULL,
                performance_30d REAL NOT NULL,
                performance_ytd REAL NOT NULL,
                risk_adjusted_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 9. Crypto Heatmap Data
            """
            CREATE TABLE IF NOT EXISTS crypto_heatmap_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                performance_24h REAL NOT NULL,
                performance_7d REAL NOT NULL,
                performance_30d REAL NOT NULL,
                market_cap REAL,
                volume_24h REAL,
                price REAL,
                risk_level REAL,
                color_intensity REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 10. Logarithmic Regression Data
            """
            CREATE TABLE IF NOT EXISTS logarithmic_regression_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                current_price REAL NOT NULL,
                regression_price REAL NOT NULL,
                deviation_percentage REAL NOT NULL,
                regression_type TEXT, -- 'bubble' or 'non_bubble'
                constant_a REAL,
                constant_b REAL,
                r_squared REAL,
                support_level REAL,
                resistance_level REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 11. Workbench Mathematical Functions Data
            """
            CREATE TABLE IF NOT EXISTS workbench_functions_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                function_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                input_parameters TEXT, -- JSON data
                calculated_value REAL NOT NULL,
                function_type TEXT, -- 'technical', 'statistical', 'custom'
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 12. AI Insights Data
            """
            CREATE TABLE IF NOT EXISTS ai_insights_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                insight_type TEXT NOT NULL, -- 'market_analysis', 'risk_assessment', 'opportunity'
                symbol TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                data_sources TEXT, -- JSON array of sources used
                recommendation TEXT,
                risk_level TEXT,
                time_horizon TEXT, -- 'short', 'medium', 'long'
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 13. Data Source Status Tracking
            """
            CREATE TABLE IF NOT EXISTS data_source_status (
                source_name TEXT PRIMARY KEY,
                last_update TEXT NOT NULL,
                status TEXT NOT NULL, -- 'active', 'error', 'maintenance'
                success_rate REAL NOT NULL,
                error_count INTEGER DEFAULT 0,
                last_error_message TEXT,
                next_scheduled_update TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        # Execute all table creation statements
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Create performance indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_crypto_risk_timestamp ON crypto_risk_indicators(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_screener_symbol_timestamp ON screener_data(symbol, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_dominance_timestamp ON dominance_data(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_valuation_symbol ON market_valuation_data(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_supply_profit_symbol ON supply_profit_loss_data(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_risk_bands_symbol ON time_spent_risk_bands(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_portfolio_name ON portfolio_performance_data(portfolio_name)',
            'CREATE INDEX IF NOT EXISTS idx_heatmap_symbol ON crypto_heatmap_data(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_regression_symbol ON logarithmic_regression_data(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_workbench_function ON workbench_functions_data(function_name)',
            'CREATE INDEX IF NOT EXISTS idx_insights_type ON ai_insights_data(insight_type)',
            'CREATE INDEX IF NOT EXISTS idx_source_status ON data_source_status(source_name)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        logger.info("Database schema initialized with all 21 data source tables")
    
    def save_extraction_result(self, result: DataExtractionResult):
        """Save extraction result to appropriate table based on source"""
        try:
            if result.source == "crypto_risk_indicators":
                self._save_crypto_risk_indicators(result)
            elif result.source == "macro_recession_indicators":
                self._save_macro_recession_indicators(result)
            elif result.source == "screener_data":
                self._save_screener_data(result)
            elif result.source == "dominance_data":
                self._save_dominance_data(result)
            elif result.source == "market_valuation_data":
                self._save_market_valuation_data(result)
            elif result.source == "supply_profit_loss_data":
                self._save_supply_profit_loss_data(result)
            elif result.source == "time_spent_risk_bands":
                self._save_time_spent_risk_bands(result)
            elif result.source == "ai_insights_data":
                self._save_ai_insights_data(result)
            else:
                logger.warning(f"Unknown data source: {result.source}")
            
            # Update source status
            self._update_source_status(result.source, result.success, result.error_message)
            
        except Exception as e:
            logger.error(f"Error saving extraction result for {result.source}: {str(e)}")
    
    def _save_crypto_risk_indicators(self, result: DataExtractionResult):
        """Save crypto risk indicators data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO crypto_risk_indicators 
            (timestamp, summary_risk, price_risk, onchain_risk, social_risk, risk_level, components)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('summary_risk', 0),
            data.get('price_risk', 0),
            data.get('onchain_risk', 0),
            data.get('social_risk', 0),
            data.get('risk_level', 'Unknown'),
            json.dumps(data.get('components', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def _save_screener_data(self, result: DataExtractionResult):
        """Save screener data for multiple symbols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        symbols = result.data.get('symbols', [])
        for symbol_data in symbols:
            cursor.execute("""
                INSERT INTO screener_data 
                (timestamp, symbol, price, fiat_risk, risk_band, risk_level, market_cap, volume_24h)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.timestamp.isoformat(),
                symbol_data.get('symbol'),
                symbol_data.get('price', 0),
                symbol_data.get('fiat_risk', 0),
                symbol_data.get('risk_band', ''),
                symbol_data.get('risk_level', ''),
                symbol_data.get('market_cap'),
                symbol_data.get('volume_24h')
            ))
        
        conn.commit()
        conn.close()
    
    def _save_dominance_data(self, result: DataExtractionResult):
        """Save dominance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO dominance_data 
            (timestamp, btc_dominance_with_stables, btc_dominance_without_stables, 
             eth_dominance, trend, market_phase, altcoin_season_probability, historical_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('btc_dominance_with_stables', 0),
            data.get('btc_dominance_without_stables', 0),
            data.get('eth_dominance'),
            data.get('trend', ''),
            data.get('market_phase', ''),
            data.get('altcoin_season_probability'),
            json.dumps(data.get('historical_context', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def _save_ai_insights_data(self, result: DataExtractionResult):
        """Save AI-generated insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO ai_insights_data 
            (timestamp, insight_type, symbol, title, description, confidence_score, 
             data_sources, recommendation, risk_level, time_horizon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('insight_type'),
            data.get('symbol'),
            data.get('title'),
            data.get('description'),
            data.get('confidence_score', result.confidence_score),
            json.dumps(data.get('data_sources', [])),
            data.get('recommendation'),
            data.get('risk_level'),
            data.get('time_horizon')
        ))
        
        conn.commit()
        conn.close()
    
    def _update_source_status(self, source_name: str, success: bool, error_message: Optional[str]):
        """Update data source status tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        status = "active" if success else "error"
        
        cursor.execute("""
            INSERT OR REPLACE INTO data_source_status 
            (source_name, last_update, status, success_rate, error_count, last_error_message, updated_at)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT success_rate FROM data_source_status WHERE source_name = ?), 1.0),
                    COALESCE((SELECT error_count FROM data_source_status WHERE source_name = ?), 0) + ?,
                    ?, ?)
        """, (
            source_name,
            datetime.now().isoformat(),
            status,
            source_name,
            source_name,
            0 if success else 1,
            error_message,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_data(self, source: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest data from specified source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_map = {
            "crypto_risk_indicators": "crypto_risk_indicators",
            "screener_data": "screener_data",
            "dominance_data": "dominance_data",
            "ai_insights": "ai_insights_data"
        }
        
        table_name = table_map.get(source)
        if not table_name:
            return []
        
        cursor.execute(f"""
            SELECT * FROM {table_name} 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    
    def get_data_source_status(self) -> List[Dict[str, Any]]:
        """Get status of all data sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_name, last_update, status, success_rate, error_count, last_error_message
            FROM data_source_status
            ORDER BY last_update DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to maintain database performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        tables_to_cleanup = [
            'crypto_risk_indicators',
            'screener_data',
            'dominance_data',
            'market_valuation_data',
            'supply_profit_loss_data',
            'crypto_heatmap_data'
        ]
        
        for table in tables_to_cleanup:
            cursor.execute(f"DELETE FROM {table} WHERE created_at < ?", (cutoff_date,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up data older than {days_to_keep} days")

    # Additional helper methods for specific data operations
    def _save_macro_recession_indicators(self, result: DataExtractionResult):
        """Save macro recession indicators data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO macro_recession_indicators 
            (timestamp, employment_risk, national_income_product_risk, production_business_risk, 
             overall_recession_risk, recession_probability, components)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('employment_risk', 0),
            data.get('national_income_product_risk', 0),
            data.get('production_business_risk', 0),
            data.get('overall_recession_risk', 0),
            data.get('recession_probability', 'Unknown'),
            json.dumps(data.get('components', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def _save_market_valuation_data(self, result: DataExtractionResult):
        """Save market valuation data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO market_valuation_data 
            (timestamp, symbol, mvrv_ratio, nvt_ratio, puell_multiple, 
             pi_cycle_top, stock_to_flow_ratio, valuation_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('symbol'),
            data.get('mvrv_ratio'),
            data.get('nvt_ratio'),
            data.get('puell_multiple'),
            data.get('pi_cycle_top'),
            data.get('stock_to_flow_ratio'),
            data.get('valuation_level')
        ))
        
        conn.commit()
        conn.close()
    
    def _save_supply_profit_loss_data(self, result: DataExtractionResult):
        """Save supply in profit/loss data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO supply_profit_loss_data 
            (timestamp, symbol, supply_in_profit_percentage, supply_in_loss_percentage, 
             supply_in_profit_usd, supply_in_loss_usd, total_supply, profitability_trend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('symbol'),
            data.get('supply_in_profit_percentage', 0),
            data.get('supply_in_loss_percentage', 0),
            data.get('supply_in_profit_usd'),
            data.get('supply_in_loss_usd'),
            data.get('total_supply'),
            data.get('profitability_trend')
        ))
        
        conn.commit()
        conn.close()
    
    def _save_time_spent_risk_bands(self, result: DataExtractionResult):
        """Save time spent in risk bands data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = result.data
        cursor.execute("""
            INSERT INTO time_spent_risk_bands 
            (timestamp, symbol, risk_band, days_spent, percentage_of_time, 
             coefficient, total_days, rarity_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.timestamp.isoformat(),
            data.get('symbol'),
            data.get('risk_band'),
            data.get('days_spent', 0),
            data.get('percentage_of_time', 0),
            data.get('coefficient', 1.0),
            data.get('total_days', 0),
            data.get('rarity_score')
        ))
        
        conn.commit()
        conn.close()