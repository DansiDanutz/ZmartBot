#!/usr/bin/env python3
"""
Cryptometer Comprehensive Database
Stores ALL valuable data from 17 Cryptometer endpoints for business monetization
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CryptometerDatabase:
    """Comprehensive database for all Cryptometer analysis data"""
    
    def __init__(self, db_path: str = "cryptometer_complete.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create all necessary tables for comprehensive Cryptometer data storage"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Main analysis table - stores complete analysis with AI predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cryptometer_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                -- Multi-timeframe scores (0-100)
                score_short_term REAL,     -- 24-48h
                score_medium_term REAL,     -- 1 week
                score_long_term REAL,       -- 1 month+
                overall_score REAL,
                
                -- AI Win Rate Predictions
                ai_win_rate_short REAL,
                ai_win_rate_medium REAL,
                ai_win_rate_long REAL,
                ai_confidence REAL,
                ai_model_used TEXT,
                
                -- Market Data
                current_price REAL,
                price_24h_change REAL,
                price_7d_change REAL,
                price_30d_change REAL,
                volume_24h REAL,
                volume_change_24h REAL,
                market_cap REAL,
                market_cap_rank INTEGER,
                
                -- Technical Analysis
                trend_strength REAL,
                trend_direction TEXT,
                momentum_score REAL,
                volatility_index REAL,
                rsi REAL,
                macd_signal TEXT,
                support_level REAL,
                resistance_level REAL,
                
                -- Sentiment Analysis
                overall_sentiment TEXT,
                sentiment_score REAL,
                social_volume REAL,
                news_sentiment TEXT,
                
                -- Long/Short Analysis
                long_short_ratio REAL,
                long_percentage REAL,
                short_percentage REAL,
                funding_rate REAL,
                
                -- Open Interest
                open_interest REAL,
                oi_change_24h REAL,
                oi_change_percentage REAL,
                
                -- Liquidation Data
                liquidations_24h REAL,
                long_liquidations REAL,
                short_liquidations REAL,
                largest_liquidation REAL,
                
                -- Risk Assessment
                risk_level TEXT,
                risk_score REAL,
                drawdown_risk REAL,
                volatility_risk REAL,
                
                -- Trading Recommendations
                recommendation TEXT,
                position_type TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profit_1 REAL,
                take_profit_2 REAL,
                take_profit_3 REAL,
                position_size_recommendation TEXT,
                
                -- Professional Reports
                professional_report TEXT,
                technical_summary TEXT,
                ai_analysis TEXT,
                executive_summary TEXT,
                
                -- Data Quality
                data_completeness REAL,
                endpoints_successful INTEGER,
                endpoints_failed INTEGER,
                analysis_version TEXT,
                processing_time_ms INTEGER
            )
        ''')
        
        # Endpoint data table - stores raw data from each endpoint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS endpoint_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                endpoint_name TEXT,
                endpoint_url TEXT,
                response_data TEXT,  -- JSON string
                response_status INTEGER,
                response_time_ms INTEGER,
                data_quality TEXT,
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # Trend indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                timeframe TEXT,  -- '1h', '4h', '1d', '1w'
                trend_type TEXT,  -- 'bullish', 'bearish', 'neutral'
                trend_strength REAL,
                trend_duration_hours INTEGER,
                
                ema_9 REAL,
                ema_21 REAL,
                ema_50 REAL,
                ema_200 REAL,
                
                macd_value REAL,
                macd_signal REAL,
                macd_histogram REAL,
                
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                bb_width REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # AI predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                model_name TEXT,
                model_version TEXT,
                
                prediction_timeframe TEXT,
                predicted_direction TEXT,
                predicted_price REAL,
                predicted_change_percent REAL,
                
                win_probability REAL,
                confidence_score REAL,
                
                pattern_detected TEXT,
                pattern_confidence REAL,
                
                reasoning TEXT,
                key_factors TEXT,  -- JSON array
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # Rapid movements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rapid_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                movement_type TEXT,  -- 'pump', 'dump', 'breakout', 'breakdown'
                price_start REAL,
                price_end REAL,
                change_percentage REAL,
                
                volume_spike REAL,
                duration_minutes INTEGER,
                
                trigger_event TEXT,
                follow_through_probability REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # Market patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                pattern_name TEXT,
                pattern_type TEXT,  -- 'reversal', 'continuation', 'consolidation'
                pattern_strength REAL,
                pattern_confidence REAL,
                
                timeframe TEXT,
                formation_time DATETIME,
                
                expected_move_percentage REAL,
                expected_direction TEXT,
                success_rate_historical REAL,
                
                description TEXT,
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                signal_type TEXT,  -- 'buy', 'sell', 'hold'
                signal_strength REAL,
                signal_source TEXT,  -- Which endpoint/indicator generated it
                
                timeframe TEXT,
                confidence REAL,
                
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                risk_reward_ratio REAL,
                
                FOREIGN KEY (analysis_id) REFERENCES cryptometer_analysis(id)
            )
        ''')
        
        # Historical performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                prediction_date DATETIME,
                resolution_date DATETIME,
                
                predicted_direction TEXT,
                predicted_score REAL,
                predicted_win_rate REAL,
                
                actual_direction TEXT,
                actual_price_change REAL,
                
                was_correct BOOLEAN,
                profit_loss REAL,
                
                timeframe TEXT,
                model_used TEXT,
                notes TEXT
            )
        ''')
        
        # User queries table (for Q&A learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                user_satisfaction INTEGER,
                query_type TEXT,
                symbols_queried TEXT,
                
                response_time_ms INTEGER,
                data_sources_used TEXT
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crypto_symbol_timestamp ON cryptometer_analysis(symbol, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_endpoint_data ON endpoint_data(symbol, endpoint_name, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends ON trend_indicators(symbol, timeframe, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_predictions ON ai_predictions(symbol, prediction_timeframe, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rapid_movements ON rapid_movements(symbol, movement_type, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns ON market_patterns(symbol, pattern_type, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals ON trading_signals(symbol, signal_type, timeframe)')
        
        self.conn.commit()
        logger.info("Cryptometer database initialized with comprehensive schema")
    
    def store_complete_analysis(self, analysis_data: Dict[str, Any]) -> int:
        """Store complete Cryptometer analysis with all extracted data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        try:
            # Insert main analysis
            cursor.execute('''
                INSERT INTO cryptometer_analysis (
                    symbol, score_short_term, score_medium_term, score_long_term, overall_score,
                    ai_win_rate_short, ai_win_rate_medium, ai_win_rate_long, ai_confidence, ai_model_used,
                    current_price, price_24h_change, price_7d_change, price_30d_change,
                    volume_24h, volume_change_24h, market_cap, market_cap_rank,
                    trend_strength, trend_direction, momentum_score, volatility_index,
                    rsi, macd_signal, support_level, resistance_level,
                    overall_sentiment, sentiment_score, social_volume, news_sentiment,
                    long_short_ratio, long_percentage, short_percentage, funding_rate,
                    open_interest, oi_change_24h, oi_change_percentage,
                    liquidations_24h, long_liquidations, short_liquidations, largest_liquidation,
                    risk_level, risk_score, drawdown_risk, volatility_risk,
                    recommendation, position_type, entry_price, stop_loss,
                    take_profit_1, take_profit_2, take_profit_3, position_size_recommendation,
                    professional_report, technical_summary, ai_analysis, executive_summary,
                    data_completeness, endpoints_successful, endpoints_failed,
                    analysis_version, processing_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('symbol'),
                analysis_data.get('score_short_term'),
                analysis_data.get('score_medium_term'),
                analysis_data.get('score_long_term'),
                analysis_data.get('overall_score'),
                
                # AI predictions
                analysis_data.get('ai_win_rate_short'),
                analysis_data.get('ai_win_rate_medium'),
                analysis_data.get('ai_win_rate_long'),
                analysis_data.get('ai_confidence'),
                analysis_data.get('ai_model_used'),
                
                # Market data
                analysis_data.get('current_price'),
                analysis_data.get('price_24h_change'),
                analysis_data.get('price_7d_change'),
                analysis_data.get('price_30d_change'),
                analysis_data.get('volume_24h'),
                analysis_data.get('volume_change_24h'),
                analysis_data.get('market_cap'),
                analysis_data.get('market_cap_rank'),
                
                # Technical
                analysis_data.get('trend_strength'),
                analysis_data.get('trend_direction'),
                analysis_data.get('momentum_score'),
                analysis_data.get('volatility_index'),
                analysis_data.get('rsi'),
                analysis_data.get('macd_signal'),
                analysis_data.get('support_level'),
                analysis_data.get('resistance_level'),
                
                # Sentiment
                analysis_data.get('overall_sentiment'),
                analysis_data.get('sentiment_score'),
                analysis_data.get('social_volume'),
                analysis_data.get('news_sentiment'),
                
                # Long/Short
                analysis_data.get('long_short_ratio'),
                analysis_data.get('long_percentage'),
                analysis_data.get('short_percentage'),
                analysis_data.get('funding_rate'),
                
                # Open Interest
                analysis_data.get('open_interest'),
                analysis_data.get('oi_change_24h'),
                analysis_data.get('oi_change_percentage'),
                
                # Liquidations
                analysis_data.get('liquidations_24h'),
                analysis_data.get('long_liquidations'),
                analysis_data.get('short_liquidations'),
                analysis_data.get('largest_liquidation'),
                
                # Risk
                analysis_data.get('risk_level'),
                analysis_data.get('risk_score'),
                analysis_data.get('drawdown_risk'),
                analysis_data.get('volatility_risk'),
                
                # Trading
                analysis_data.get('recommendation'),
                analysis_data.get('position_type'),
                analysis_data.get('entry_price'),
                analysis_data.get('stop_loss'),
                analysis_data.get('take_profit_1'),
                analysis_data.get('take_profit_2'),
                analysis_data.get('take_profit_3'),
                analysis_data.get('position_size_recommendation'),
                
                # Reports
                analysis_data.get('professional_report'),
                analysis_data.get('technical_summary'),
                analysis_data.get('ai_analysis'),
                analysis_data.get('executive_summary'),
                
                # Data quality
                analysis_data.get('data_completeness'),
                analysis_data.get('endpoints_successful'),
                analysis_data.get('endpoints_failed'),
                analysis_data.get('analysis_version', '2.0'),
                analysis_data.get('processing_time_ms', 0)
            ))
            
            analysis_id = cursor.lastrowid
            if analysis_id is None:
                raise RuntimeError("Failed to get analysis ID after insert")
            
            # Store endpoint data
            for endpoint in analysis_data.get('endpoint_data', []):
                self.store_endpoint_data(analysis_id, analysis_data['symbol'], endpoint)
            
            # Store trend indicators
            for trend in analysis_data.get('trend_indicators', []):
                self.store_trend_indicator(analysis_id, analysis_data['symbol'], trend)
            
            # Store AI predictions
            for prediction in analysis_data.get('ai_predictions', []):
                self.store_ai_prediction(analysis_id, analysis_data['symbol'], prediction)
            
            # Store rapid movements
            for movement in analysis_data.get('rapid_movements', []):
                self.store_rapid_movement(analysis_id, analysis_data['symbol'], movement)
            
            # Store market patterns
            for pattern in analysis_data.get('market_patterns', []):
                self.store_market_pattern(analysis_id, analysis_data['symbol'], pattern)
            
            # Store trading signals
            for signal in analysis_data.get('trading_signals', []):
                self.store_trading_signal(analysis_id, analysis_data['symbol'], signal)
            
            if self.conn is not None:
                self.conn.commit()
            logger.info(f"Stored complete Cryptometer analysis for {analysis_data['symbol']} with ID {analysis_id}")
            return analysis_id
            
        except Exception as e:
            if self.conn is not None:
                self.conn.rollback()
            logger.error(f"Error storing Cryptometer analysis: {e}")
            raise
    
    def store_endpoint_data(self, analysis_id: int, symbol: str, endpoint: Dict[str, Any]):
        """Store raw endpoint data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO endpoint_data (
                analysis_id, symbol, endpoint_name, endpoint_url,
                response_data, response_status, response_time_ms, data_quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            endpoint.get('endpoint_name'),
            endpoint.get('endpoint_url'),
            json.dumps(endpoint.get('response_data', {})),
            endpoint.get('response_status'),
            endpoint.get('response_time_ms'),
            endpoint.get('data_quality')
        ))
    
    def store_trend_indicator(self, analysis_id: int, symbol: str, trend: Dict[str, Any]):
        """Store trend indicator data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trend_indicators (
                analysis_id, symbol, timeframe, trend_type, trend_strength,
                trend_duration_hours, ema_9, ema_21, ema_50, ema_200,
                macd_value, macd_signal, macd_histogram,
                bb_upper, bb_middle, bb_lower, bb_width
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            trend.get('timeframe'),
            trend.get('trend_type'),
            trend.get('trend_strength'),
            trend.get('trend_duration_hours'),
            trend.get('ema_9'),
            trend.get('ema_21'),
            trend.get('ema_50'),
            trend.get('ema_200'),
            trend.get('macd_value'),
            trend.get('macd_signal'),
            trend.get('macd_histogram'),
            trend.get('bb_upper'),
            trend.get('bb_middle'),
            trend.get('bb_lower'),
            trend.get('bb_width')
        ))
    
    def store_ai_prediction(self, analysis_id: int, symbol: str, prediction: Dict[str, Any]):
        """Store AI prediction data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ai_predictions (
                analysis_id, symbol, model_name, model_version,
                prediction_timeframe, predicted_direction, predicted_price,
                predicted_change_percent, win_probability, confidence_score,
                pattern_detected, pattern_confidence, reasoning, key_factors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            prediction.get('model_name'),
            prediction.get('model_version'),
            prediction.get('prediction_timeframe'),
            prediction.get('predicted_direction'),
            prediction.get('predicted_price'),
            prediction.get('predicted_change_percent'),
            prediction.get('win_probability'),
            prediction.get('confidence_score'),
            prediction.get('pattern_detected'),
            prediction.get('pattern_confidence'),
            prediction.get('reasoning'),
            json.dumps(prediction.get('key_factors', []))
        ))
    
    def store_rapid_movement(self, analysis_id: int, symbol: str, movement: Dict[str, Any]):
        """Store rapid movement data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO rapid_movements (
                analysis_id, symbol, movement_type, price_start, price_end,
                change_percentage, volume_spike, duration_minutes,
                trigger_event, follow_through_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            movement.get('movement_type'),
            movement.get('price_start'),
            movement.get('price_end'),
            movement.get('change_percentage'),
            movement.get('volume_spike'),
            movement.get('duration_minutes'),
            movement.get('trigger_event'),
            movement.get('follow_through_probability')
        ))
    
    def store_market_pattern(self, analysis_id: int, symbol: str, pattern: Dict[str, Any]):
        """Store market pattern data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO market_patterns (
                analysis_id, symbol, pattern_name, pattern_type,
                pattern_strength, pattern_confidence, timeframe,
                formation_time, expected_move_percentage, expected_direction,
                success_rate_historical, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            pattern.get('pattern_name'),
            pattern.get('pattern_type'),
            pattern.get('pattern_strength'),
            pattern.get('pattern_confidence'),
            pattern.get('timeframe'),
            pattern.get('formation_time'),
            pattern.get('expected_move_percentage'),
            pattern.get('expected_direction'),
            pattern.get('success_rate_historical'),
            pattern.get('description')
        ))
    
    def store_trading_signal(self, analysis_id: int, symbol: str, signal: Dict[str, Any]):
        """Store trading signal data"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trading_signals (
                analysis_id, symbol, signal_type, signal_strength,
                signal_source, timeframe, confidence,
                entry_price, stop_loss, take_profit, risk_reward_ratio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, symbol,
            signal.get('signal_type'),
            signal.get('signal_strength'),
            signal.get('signal_source'),
            signal.get('timeframe'),
            signal.get('confidence'),
            signal.get('entry_price'),
            signal.get('stop_loss'),
            signal.get('take_profit'),
            signal.get('risk_reward_ratio')
        ))
    
    # Query methods for Q&A agent
    def get_latest_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest Cryptometer analysis for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM cryptometer_analysis 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_ai_predictions(self, symbol: str, timeframe: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get AI predictions for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        if timeframe:
            cursor.execute('''
                SELECT * FROM ai_predictions 
                WHERE symbol = ? AND prediction_timeframe = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (symbol, timeframe))
        else:
            cursor.execute('''
                SELECT * FROM ai_predictions 
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trend_indicators(self, symbol: str, timeframe: str = '1d') -> List[Dict[str, Any]]:
        """Get trend indicators for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM trend_indicators 
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (symbol, timeframe))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_rapid_movements(self, symbol: Optional[str] = None, movement_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get rapid market movements"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        if symbol and movement_type:
            cursor.execute('''
                SELECT * FROM rapid_movements 
                WHERE symbol = ? AND movement_type = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (symbol, movement_type))
        elif symbol:
            cursor.execute('''
                SELECT * FROM rapid_movements 
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (symbol,))
        else:
            cursor.execute('''
                SELECT * FROM rapid_movements 
                ORDER BY timestamp DESC
                LIMIT 20
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trading_signals(self, symbol: str, signal_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trading signals for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        if signal_type:
            cursor.execute('''
                SELECT * FROM trading_signals 
                WHERE symbol = ? AND signal_type = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (symbol, signal_type))
        else:
            cursor.execute('''
                SELECT * FROM trading_signals 
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_market_patterns(self, symbol: str) -> List[Dict[str, Any]]:
        """Get detected market patterns for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM market_patterns 
            WHERE symbol = ? 
            ORDER BY pattern_confidence DESC
            LIMIT 10
        ''', (symbol,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_analyses(self, **kwargs) -> List[Dict[str, Any]]:
        """Search analyses with flexible criteria"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        
        conditions = []
        params = []
        
        if 'symbol' in kwargs:
            conditions.append('symbol = ?')
            params.append(kwargs['symbol'])
        
        if 'min_score' in kwargs:
            conditions.append('overall_score >= ?')
            params.append(kwargs['min_score'])
        
        if 'risk_level' in kwargs:
            conditions.append('risk_level = ?')
            params.append(kwargs['risk_level'])
        
        if 'sentiment' in kwargs:
            conditions.append('overall_sentiment = ?')
            params.append(kwargs['sentiment'])
        
        if 'position_type' in kwargs:
            conditions.append('position_type = ?')
            params.append(kwargs['position_type'])
        
        if 'start_date' in kwargs:
            conditions.append('timestamp >= ?')
            params.append(kwargs['start_date'])
        
        if 'end_date' in kwargs:
            conditions.append('timestamp <= ?')
            params.append(kwargs['end_date'])
        
        query = 'SELECT * FROM cryptometer_analysis'
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY timestamp DESC'
        
        if 'limit' in kwargs:
            query += f' LIMIT {kwargs["limit"]}'
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_endpoint_data(self, symbol: str, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """Get latest endpoint data for a symbol"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM endpoint_data 
            WHERE symbol = ? AND endpoint_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (symbol, endpoint_name))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Parse JSON response data
            if result.get('response_data'):
                try:
                    result['response_data'] = json.loads(result['response_data'])
                except:
                    pass
            return result
        return None
    
    def store_user_query(self, query: str, response: str, query_type: Optional[str] = None, 
                        symbols: Optional[List[str]] = None, response_time_ms: int = 0):
        """Store user query for learning and optimization"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
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
        if self.conn is not None:
            self.conn.commit()
    
    def get_historical_performance(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical prediction performance"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        
        conditions = []
        params = []
        
        if symbol:
            conditions.append('symbol = ?')
            params.append(symbol)
        
        if timeframe:
            conditions.append('timeframe = ?')
            params.append(timeframe)
        
        query = 'SELECT * FROM historical_performance'
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY prediction_date DESC LIMIT 50'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Create global instance
cryptometer_db = CryptometerDatabase()