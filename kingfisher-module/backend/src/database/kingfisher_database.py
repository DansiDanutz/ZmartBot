#!/usr/bin/env python3
"""
KingFisher Comprehensive Database
Stores ALL valuable data extracted from images for business monetization
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KingFisherDatabase:
    """Comprehensive database for all KingFisher analysis data"""
    
    def __init__(self, db_path: str = "kingfisher_complete.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create all necessary tables for comprehensive data storage"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Main analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kingfisher_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_type TEXT,
                image_hash TEXT UNIQUE,
                
                -- Win rates for all timeframes
                win_rate_24h_long REAL,
                win_rate_24h_short REAL,
                win_rate_7d_long REAL,
                win_rate_7d_short REAL,
                win_rate_1m_long REAL,
                win_rate_1m_short REAL,
                
                -- Scores
                score_24h REAL,
                score_7d REAL,
                score_1m REAL,
                overall_score REAL,
                
                -- Market data
                current_price REAL,
                volume_24h REAL,
                price_change_24h REAL,
                market_cap REAL,
                
                -- Technical indicators
                lpi REAL,  -- Liquidation Pressure Index
                mbr REAL,  -- Market Balance Ratio
                ppi REAL,  -- Price Position Index
                rsi REAL,
                momentum_score REAL,
                volatility_index REAL,
                
                -- Sentiment and confidence
                overall_sentiment TEXT,
                retail_sentiment TEXT,
                institutional_sentiment TEXT,
                overall_confidence REAL,
                risk_level TEXT,
                risk_score REAL,
                
                -- Concentrations
                long_concentration REAL,
                short_concentration REAL,
                long_volume REAL,
                short_volume REAL,
                
                -- Trading recommendations
                recommendation TEXT,
                best_timeframe TEXT,
                best_position TEXT,
                position_size_recommendation TEXT,
                
                -- Professional report
                professional_report TEXT,
                executive_summary TEXT,
                
                -- Metadata
                data_quality TEXT,
                analysis_version TEXT,
                processing_time_ms INTEGER
            )
        ''')
        
        # Liquidation clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS liquidation_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                cluster_type TEXT,  -- 'support' or 'resistance'
                price_level REAL,
                cluster_size REAL,
                intensity REAL,
                distance_from_price REAL,
                distance_percentage REAL,
                
                timeframe TEXT,  -- '24h', '7d', '1m'
                risk_assessment TEXT,
                
                liquidation_count INTEGER,
                total_volume REAL,
                average_leverage REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES kingfisher_analysis(id)
            )
        ''')
        
        # Support and resistance levels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_resistance_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                level_type TEXT,  -- 'support' or 'resistance'
                price_level REAL,
                strength REAL,
                volume REAL,
                
                timeframe TEXT,  -- '24h', '7d', '1m'
                source TEXT,  -- 'liquidation', 'technical', 'psychological'
                
                times_tested INTEGER,
                last_test_date DATETIME,
                holding_probability REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES kingfisher_analysis(id)
            )
        ''')
        
        # Heat zones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS heat_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                zone_type TEXT,  -- 'hot', 'warm', 'cool', 'cold'
                price_start REAL,
                price_end REAL,
                intensity REAL,
                
                long_percentage REAL,
                short_percentage REAL,
                
                volume_concentration REAL,
                risk_level TEXT,
                
                FOREIGN KEY (analysis_id) REFERENCES kingfisher_analysis(id)
            )
        ''')
        
        # Trading targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                position_type TEXT,  -- 'long' or 'short'
                timeframe TEXT,  -- '24h', '7d', '1m'
                
                entry_price REAL,
                stop_loss REAL,
                target_1 REAL,
                target_2 REAL,
                target_3 REAL,
                
                risk_reward_ratio REAL,
                win_probability REAL,
                expected_value REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES kingfisher_analysis(id)
            )
        ''')
        
        # Market patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                pattern_type TEXT,  -- 'bullish_divergence', 'bearish_divergence', etc.
                pattern_strength REAL,
                confidence REAL,
                
                timeframe TEXT,
                description TEXT,
                
                expected_move REAL,
                expected_direction TEXT,
                
                FOREIGN KEY (analysis_id) REFERENCES kingfisher_analysis(id)
            )
        ''')
        
        # Historical performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                prediction_date DATETIME,
                resolution_date DATETIME,
                
                predicted_direction TEXT,
                predicted_score REAL,
                predicted_confidence REAL,
                
                actual_direction TEXT,
                actual_move REAL,
                
                was_correct BOOLEAN,
                profit_loss REAL,
                
                timeframe TEXT,
                notes TEXT
            )
        ''')
        
        # User queries table (for learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                user_satisfaction INTEGER,  -- 1-5 rating
                query_type TEXT,
                symbols_queried TEXT,
                
                response_time_ms INTEGER,
                data_sources_used TEXT
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON kingfisher_analysis(symbol, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clusters_symbol ON liquidation_clusters(symbol, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sr_levels ON support_resistance_levels(symbol, level_type, timeframe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_heat_zones ON heat_zones(symbol, zone_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_targets ON trading_targets(symbol, position_type, timeframe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns ON market_patterns(symbol, pattern_type)')
        
        self.conn.commit()
        logger.info("KingFisher database initialized with comprehensive schema")
    
    def store_complete_analysis(self, analysis_data: Dict[str, Any]) -> int:
        """Store complete analysis with all extracted data"""
        cursor = self.conn.cursor()
        
        try:
            # Insert main analysis  
            cursor.execute('''
                INSERT INTO kingfisher_analysis (
                    symbol, image_type, image_hash,
                    win_rate_24h_long, win_rate_24h_short,
                    win_rate_7d_long, win_rate_7d_short,
                    win_rate_1m_long, win_rate_1m_short,
                    score_24h, score_7d, score_1m, overall_score,
                    current_price, volume_24h, price_change_24h, market_cap,
                    lpi, mbr, ppi, rsi, momentum_score, volatility_index,
                    overall_sentiment, retail_sentiment, institutional_sentiment,
                    overall_confidence, risk_level, risk_score,
                    long_concentration, short_concentration,
                    long_volume, short_volume,
                    recommendation, best_timeframe, best_position,
                    position_size_recommendation,
                    professional_report, executive_summary,
                    data_quality, analysis_version, processing_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('symbol'),
                analysis_data.get('image_type'),
                analysis_data.get('image_hash'),
                
                # Win rates
                analysis_data.get('win_rate_24h_long'),
                analysis_data.get('win_rate_24h_short'),
                analysis_data.get('win_rate_7d_long'),
                analysis_data.get('win_rate_7d_short'),
                analysis_data.get('win_rate_1m_long'),
                analysis_data.get('win_rate_1m_short'),
                
                # Scores
                analysis_data.get('score_24h'),
                analysis_data.get('score_7d'),
                analysis_data.get('score_1m'),
                analysis_data.get('overall_score'),
                
                # Market data
                analysis_data.get('current_price'),
                analysis_data.get('volume_24h'),
                analysis_data.get('price_change_24h'),
                analysis_data.get('market_cap'),
                
                # Technical indicators
                analysis_data.get('lpi'),
                analysis_data.get('mbr'),
                analysis_data.get('ppi'),
                analysis_data.get('rsi'),
                analysis_data.get('momentum_score'),
                analysis_data.get('volatility_index'),
                
                # Sentiment
                analysis_data.get('overall_sentiment'),
                analysis_data.get('retail_sentiment'),
                analysis_data.get('institutional_sentiment'),
                analysis_data.get('overall_confidence'),
                analysis_data.get('risk_level'),
                analysis_data.get('risk_score'),
                
                # Concentrations
                analysis_data.get('long_concentration'),
                analysis_data.get('short_concentration'),
                analysis_data.get('long_volume'),
                analysis_data.get('short_volume'),
                
                # Recommendations
                analysis_data.get('recommendation'),
                analysis_data.get('best_timeframe'),
                analysis_data.get('best_position'),
                analysis_data.get('position_size_recommendation'),
                
                # Reports
                analysis_data.get('professional_report'),
                analysis_data.get('executive_summary'),
                
                # Metadata
                analysis_data.get('data_quality', 'premium'),
                analysis_data.get('analysis_version', '2.0'),
                analysis_data.get('processing_time_ms', 0)
            ))
            
            analysis_id = cursor.lastrowid
            
            # Store liquidation clusters
            for cluster in analysis_data.get('liquidation_clusters', []):
                self.store_liquidation_cluster(analysis_id, analysis_data['symbol'], cluster)
            
            # Store support/resistance levels
            for level in analysis_data.get('support_resistance_levels', []):
                self.store_support_resistance_level(analysis_id, analysis_data['symbol'], level)
            
            # Store heat zones
            for zone in analysis_data.get('heat_zones', []):
                self.store_heat_zone(analysis_id, analysis_data['symbol'], zone)
            
            # Store trading targets
            for target in analysis_data.get('trading_targets', []):
                self.store_trading_target(analysis_id, analysis_data['symbol'], target)
            
            # Store market patterns
            for pattern in analysis_data.get('market_patterns', []):
                self.store_market_pattern(analysis_id, analysis_data['symbol'], pattern)
            
            self.conn.commit()
            logger.info(f"Stored complete analysis for {analysis_data['symbol']} with ID {analysis_id}")
            return analysis_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error storing analysis: {e}")
            raise
    
    def store_liquidation_cluster(self, analysis_id: int, symbol: str, cluster: Dict[str, Any]):
        """Store liquidation cluster data"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO liquidation_clusters (
                analysis_id, symbol, cluster_type, price_level,
                cluster_size, intensity, distance_from_price,
                distance_percentage, timeframe, risk_assessment,
                liquidation_count, total_volume, average_leverage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            cluster.get('cluster_type'),
            cluster.get('price_level'),
            cluster.get('cluster_size'),
            cluster.get('intensity'),
            cluster.get('distance_from_price'),
            cluster.get('distance_percentage'),
            cluster.get('timeframe'),
            cluster.get('risk_assessment'),
            cluster.get('liquidation_count'),
            cluster.get('total_volume'),
            cluster.get('average_leverage')
        ))
    
    def store_support_resistance_level(self, analysis_id: int, symbol: str, level: Dict[str, Any]):
        """Store support/resistance level"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO support_resistance_levels (
                analysis_id, symbol, level_type, price_level,
                strength, volume, timeframe, source,
                times_tested, last_test_date, holding_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            level.get('level_type'),
            level.get('price_level'),
            level.get('strength'),
            level.get('volume'),
            level.get('timeframe'),
            level.get('source'),
            level.get('times_tested', 0),
            level.get('last_test_date'),
            level.get('holding_probability')
        ))
    
    def store_heat_zone(self, analysis_id: int, symbol: str, zone: Dict[str, Any]):
        """Store heat zone data"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO heat_zones (
                analysis_id, symbol, zone_type,
                price_start, price_end, intensity,
                long_percentage, short_percentage,
                volume_concentration, risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            zone.get('zone_type'),
            zone.get('price_start'),
            zone.get('price_end'),
            zone.get('intensity'),
            zone.get('long_percentage'),
            zone.get('short_percentage'),
            zone.get('volume_concentration'),
            zone.get('risk_level')
        ))
    
    def store_trading_target(self, analysis_id: int, symbol: str, target: Dict[str, Any]):
        """Store trading target"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trading_targets (
                analysis_id, symbol, position_type, timeframe,
                entry_price, stop_loss, target_1, target_2, target_3,
                risk_reward_ratio, win_probability, expected_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            target.get('position_type'),
            target.get('timeframe'),
            target.get('entry_price'),
            target.get('stop_loss'),
            target.get('target_1'),
            target.get('target_2'),
            target.get('target_3'),
            target.get('risk_reward_ratio'),
            target.get('win_probability'),
            target.get('expected_value')
        ))
    
    def store_market_pattern(self, analysis_id: int, symbol: str, pattern: Dict[str, Any]):
        """Store market pattern"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO market_patterns (
                analysis_id, symbol, pattern_type,
                pattern_strength, confidence,
                timeframe, description,
                expected_move, expected_direction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            pattern.get('pattern_type'),
            pattern.get('pattern_strength'),
            pattern.get('confidence'),
            pattern.get('timeframe'),
            pattern.get('description'),
            pattern.get('expected_move'),
            pattern.get('expected_direction')
        ))
    
    def get_latest_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest analysis for a symbol"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM kingfisher_analysis 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_win_rates(self, symbol: str, timeframe: str = '24h') -> Dict[str, float]:
        """Get win rates for a symbol and timeframe"""
        cursor = self.conn.cursor()
        
        if timeframe == '24h':
            cols = 'win_rate_24h_long, win_rate_24h_short'
        elif timeframe == '7d':
            cols = 'win_rate_7d_long, win_rate_7d_short'
        else:
            cols = 'win_rate_1m_long, win_rate_1m_short'
        
        cursor.execute(f'''
            SELECT {cols}, overall_confidence 
            FROM kingfisher_analysis 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}
    
    def get_support_resistance_levels(self, symbol: str, timeframe: str = None) -> List[Dict[str, Any]]:
        """Get support and resistance levels for a symbol"""
        cursor = self.conn.cursor()
        
        if timeframe:
            cursor.execute('''
                SELECT * FROM support_resistance_levels 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY strength DESC
            ''', (symbol, timeframe))
        else:
            cursor.execute('''
                SELECT * FROM support_resistance_levels 
                WHERE symbol = ?
                ORDER BY strength DESC
            ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_liquidation_clusters(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get liquidation clusters for a symbol"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM liquidation_clusters 
            WHERE symbol = ? 
            ORDER BY cluster_size DESC 
            LIMIT ?
        ''', (symbol, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trading_targets(self, symbol: str, position_type: str = None) -> List[Dict[str, Any]]:
        """Get trading targets for a symbol"""
        cursor = self.conn.cursor()
        
        if position_type:
            cursor.execute('''
                SELECT * FROM trading_targets 
                WHERE symbol = ? AND position_type = ?
                ORDER BY win_probability DESC
            ''', (symbol, position_type))
        else:
            cursor.execute('''
                SELECT * FROM trading_targets 
                WHERE symbol = ?
                ORDER BY win_probability DESC
            ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_market_patterns(self, symbol: str) -> List[Dict[str, Any]]:
        """Get detected market patterns for a symbol"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM market_patterns 
            WHERE symbol = ? 
            ORDER BY confidence DESC
        ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_heat_zones(self, symbol: str) -> List[Dict[str, Any]]:
        """Get heat zones for a symbol"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM heat_zones 
            WHERE symbol = ? 
            ORDER BY intensity DESC
        ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_analyses(self, **kwargs) -> List[Dict[str, Any]]:
        """Search analyses with flexible criteria"""
        conditions = []
        params = []
        
        if 'symbol' in kwargs:
            conditions.append('symbol = ?')
            params.append(kwargs['symbol'])
        
        if 'min_confidence' in kwargs:
            conditions.append('overall_confidence >= ?')
            params.append(kwargs['min_confidence'])
        
        if 'risk_level' in kwargs:
            conditions.append('risk_level = ?')
            params.append(kwargs['risk_level'])
        
        if 'sentiment' in kwargs:
            conditions.append('overall_sentiment = ?')
            params.append(kwargs['sentiment'])
        
        if 'start_date' in kwargs:
            conditions.append('timestamp >= ?')
            params.append(kwargs['start_date'])
        
        if 'end_date' in kwargs:
            conditions.append('timestamp <= ?')
            params.append(kwargs['end_date'])
        
        query = 'SELECT * FROM kingfisher_analysis'
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY timestamp DESC'
        
        if 'limit' in kwargs:
            query += f' LIMIT {kwargs["limit"]}'
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def store_user_query(self, query: str, response: str, query_type: str = None, 
                        symbols: List[str] = None, response_time_ms: int = 0):
        """Store user query for learning and optimization"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO user_queries (
                query, response, query_type,
                symbols_queried, response_time_ms
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            query, response, query_type,
            json.dumps(symbols) if symbols else None,
            response_time_ms
        ))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Create global instance
kingfisher_db = KingFisherDatabase()