#!/usr/bin/env python3
"""
Historical Pattern Database for Self-Learning AI
Stores and analyzes historical trading patterns with win rates across multiple timeframes
"""

import sqlite3
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """Supported timeframes for analysis"""
    H24_48 = "24h-48h"
    DAYS_7 = "7d" 
    MONTH_1 = "1m"

class Direction(Enum):
    """Trading directions"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

@dataclass
class HistoricalPattern:
    """Represents a historical trading pattern with outcome"""
    id: str
    symbol: str
    timestamp: datetime
    direction: Direction
    timeframe: TimeFrame
    
    # Endpoint data at the time of pattern
    endpoint_scores: Dict[str, float]
    endpoint_patterns: Dict[str, List[str]]
    
    # Market conditions
    price_at_entry: float
    volume_data: Dict[str, float]
    market_conditions: Dict[str, Any]
    
    # Outcome data
    price_changes: Dict[str, float]  # Price changes for each timeframe
    max_profit: float
    max_drawdown: float
    final_outcome: str  # 'WIN', 'LOSS', 'BREAKEVEN'
    win_rate_score: float  # 0.0 to 1.0
    
    # Pattern metadata
    confidence_at_entry: float
    patterns_identified: List[str]
    trigger_conditions: Dict[str, Any]

@dataclass
class PatternStatistics:
    """Statistics for a specific pattern type"""
    pattern_type: str
    symbol: str
    direction: Direction
    timeframe: TimeFrame
    
    total_occurrences: int
    successful_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    
    # Probability scores
    probability_score: float
    confidence_level: float
    reliability_rating: str  # 'HIGH', 'MEDIUM', 'LOW'
    
    last_updated: datetime

@dataclass
class TopPattern:
    """Top performing pattern for a symbol/direction/timeframe"""
    rank: int
    pattern_signature: str
    win_rate: float
    total_trades: int
    avg_profit_percent: float
    probability_score: float
    trigger_conditions: Dict[str, Any]
    last_success: datetime
    confidence_rating: str

class HistoricalPatternDatabase:
    """
    Advanced Historical Pattern Database for AI Learning
    Tracks successful patterns and calculates probability-based win rates
    """
    
    def __init__(self, db_path: str = "historical_patterns.db"):
        """Initialize the Historical Pattern Database"""
        self.db_path = db_path
        self.pattern_cache: Dict[str, List[TopPattern]] = {}
        
        # Initialize database
        self._init_database()
        
        # Load cached patterns
        self._load_pattern_cache()
        
        logger.info("Historical Pattern Database initialized")
    
    def _init_database(self):
        """Initialize SQLite database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Historical patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_patterns (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                direction TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                endpoint_scores TEXT NOT NULL,
                endpoint_patterns TEXT NOT NULL,
                price_at_entry REAL NOT NULL,
                volume_data TEXT NOT NULL,
                market_conditions TEXT NOT NULL,
                price_changes TEXT NOT NULL,
                max_profit REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                final_outcome TEXT NOT NULL,
                win_rate_score REAL NOT NULL,
                confidence_at_entry REAL NOT NULL,
                patterns_identified TEXT NOT NULL,
                trigger_conditions TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pattern statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_statistics (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                total_occurrences INTEGER NOT NULL,
                successful_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                avg_profit REAL NOT NULL,
                avg_loss REAL NOT NULL,
                profit_factor REAL NOT NULL,
                max_consecutive_wins INTEGER NOT NULL,
                max_consecutive_losses INTEGER NOT NULL,
                probability_score REAL NOT NULL,
                confidence_level REAL NOT NULL,
                reliability_rating TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(pattern_type, symbol, direction, timeframe)
            )
        ''')
        
        # Top patterns table (top 10 for each symbol/direction/timeframe)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_patterns (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                rank INTEGER NOT NULL,
                pattern_signature TEXT NOT NULL,
                win_rate REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                avg_profit_percent REAL NOT NULL,
                probability_score REAL NOT NULL,
                trigger_conditions TEXT NOT NULL,
                last_success TEXT NOT NULL,
                confidence_rating TEXT NOT NULL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, direction, timeframe, rank)
            )
        ''')
        
        # Endpoint performance by symbol and timeframe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS endpoint_historical_performance (
                id TEXT PRIMARY KEY,
                endpoint_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                direction TEXT NOT NULL,
                total_predictions INTEGER NOT NULL,
                successful_predictions INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                avg_accuracy_score REAL NOT NULL,
                reliability_score REAL NOT NULL,
                weight_multiplier REAL NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(endpoint_name, symbol, timeframe, direction)
            )
        ''')
        
        # Market conditions patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_condition_patterns (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_values TEXT NOT NULL,
                associated_outcomes TEXT NOT NULL,
                success_rate REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                confidence_score REAL NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(symbol, condition_type)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_symbol_timeframe ON historical_patterns(symbol, timeframe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_direction_outcome ON historical_patterns(direction, final_outcome)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_symbol_direction ON pattern_statistics(symbol, direction, timeframe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_top_patterns_lookup ON top_patterns(symbol, direction, timeframe)')
        
        conn.commit()
        conn.close()
        
        logger.info("Historical Pattern Database schema initialized")
    
    def store_historical_pattern(self, pattern: HistoricalPattern):
        """Store a historical pattern with its outcome"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO historical_patterns 
            (id, symbol, timestamp, direction, timeframe, endpoint_scores, endpoint_patterns,
             price_at_entry, volume_data, market_conditions, price_changes, max_profit,
             max_drawdown, final_outcome, win_rate_score, confidence_at_entry,
             patterns_identified, trigger_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.id,
            pattern.symbol,
            pattern.timestamp.isoformat(),
            pattern.direction.value,
            pattern.timeframe.value,
            json.dumps(pattern.endpoint_scores),
            json.dumps(pattern.endpoint_patterns),
            pattern.price_at_entry,
            json.dumps(pattern.volume_data),
            json.dumps(pattern.market_conditions),
            json.dumps(pattern.price_changes),
            pattern.max_profit,
            pattern.max_drawdown,
            pattern.final_outcome,
            pattern.win_rate_score,
            pattern.confidence_at_entry,
            json.dumps(pattern.patterns_identified),
            json.dumps(pattern.trigger_conditions)
        ))
        
        conn.commit()
        conn.close()
        
        # Update statistics and top patterns
        self._update_pattern_statistics(pattern)
        self._update_top_patterns(pattern.symbol, pattern.direction, pattern.timeframe)
        
        logger.info(f"Stored historical pattern {pattern.id} for {pattern.symbol}")
    
    def _update_pattern_statistics(self, pattern: HistoricalPattern):
        """Update pattern statistics based on new historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern_type in pattern.patterns_identified:
            # Get existing statistics
            cursor.execute('''
                SELECT * FROM pattern_statistics 
                WHERE pattern_type = ? AND symbol = ? AND direction = ? AND timeframe = ?
            ''', (pattern_type, pattern.symbol, pattern.direction.value, pattern.timeframe.value))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing statistics
                _, _, _, _, _, total_occ, successful, win_rate, avg_profit, avg_loss, profit_factor, max_wins, max_losses, _, _, _, _ = existing
                
                total_occ += 1
                if pattern.final_outcome == 'WIN':
                    successful += 1
                
                new_win_rate = successful / total_occ
                
                # Update averages using exponential moving average
                alpha = 0.1
                if pattern.final_outcome == 'WIN':
                    avg_profit = (1 - alpha) * avg_profit + alpha * pattern.max_profit
                else:
                    avg_loss = (1 - alpha) * avg_loss + alpha * abs(pattern.max_drawdown)
                
                new_profit_factor = avg_profit / max(avg_loss, 0.01)
                
                # Calculate probability score
                probability_score = self._calculate_probability_score(new_win_rate, total_occ, new_profit_factor)
                confidence_level = min(1.0, total_occ / 100.0)  # Confidence increases with sample size
                reliability_rating = self._get_reliability_rating(new_win_rate, total_occ)
                
                cursor.execute('''
                    UPDATE pattern_statistics 
                    SET total_occurrences = ?, successful_trades = ?, win_rate = ?,
                        avg_profit = ?, avg_loss = ?, profit_factor = ?,
                        probability_score = ?, confidence_level = ?, reliability_rating = ?,
                        last_updated = ?
                    WHERE pattern_type = ? AND symbol = ? AND direction = ? AND timeframe = ?
                ''', (
                    total_occ, successful, new_win_rate, avg_profit, avg_loss, new_profit_factor,
                    probability_score, confidence_level, reliability_rating, datetime.now().isoformat(),
                    pattern_type, pattern.symbol, pattern.direction.value, pattern.timeframe.value
                ))
            else:
                # Create new statistics entry
                win_rate = 1.0 if pattern.final_outcome == 'WIN' else 0.0
                avg_profit = pattern.max_profit if pattern.final_outcome == 'WIN' else 0.0
                avg_loss = abs(pattern.max_drawdown) if pattern.final_outcome == 'LOSS' else 0.0
                profit_factor = avg_profit / max(avg_loss, 0.01)
                
                probability_score = self._calculate_probability_score(win_rate, 1, profit_factor)
                confidence_level = 0.01  # Low confidence with single sample
                reliability_rating = 'LOW'
                
                cursor.execute('''
                    INSERT INTO pattern_statistics 
                    (id, pattern_type, symbol, direction, timeframe, total_occurrences,
                     successful_trades, win_rate, avg_profit, avg_loss, profit_factor,
                     max_consecutive_wins, max_consecutive_losses, probability_score,
                     confidence_level, reliability_rating, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"{pattern_type}_{pattern.symbol}_{pattern.direction.value}_{pattern.timeframe.value}",
                    pattern_type, pattern.symbol, pattern.direction.value, pattern.timeframe.value,
                    1, 1 if pattern.final_outcome == 'WIN' else 0, win_rate,
                    avg_profit, avg_loss, profit_factor, 1 if pattern.final_outcome == 'WIN' else 0,
                    1 if pattern.final_outcome == 'LOSS' else 0, probability_score,
                    confidence_level, reliability_rating, datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
    
    def _calculate_probability_score(self, win_rate: float, sample_size: int, profit_factor: float) -> float:
        """Calculate probability score based on win rate, sample size, and profit factor"""
        # Base score from win rate
        base_score = win_rate
        
        # Adjust for sample size (more samples = higher confidence)
        sample_confidence = min(1.0, sample_size / 50.0)
        
        # Adjust for profit factor
        profit_adjustment = min(1.5, max(0.5, profit_factor / 2.0))
        
        # Calculate final probability score
        probability_score = base_score * sample_confidence * profit_adjustment
        
        return min(1.0, max(0.0, probability_score))
    
    def _get_reliability_rating(self, win_rate: float, sample_size: int) -> str:
        """Get reliability rating based on win rate and sample size"""
        if sample_size < 5:
            return 'LOW'
        elif sample_size < 20:
            if win_rate >= 0.7:
                return 'MEDIUM'
            else:
                return 'LOW'
        else:
            if win_rate >= 0.8:
                return 'HIGH'
            elif win_rate >= 0.6:
                return 'MEDIUM'
            else:
                return 'LOW'
    
    def _update_top_patterns(self, symbol: str, direction: Direction, timeframe: TimeFrame):
        """Update top 10 patterns for a symbol/direction/timeframe combination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all patterns for this combination, ordered by probability score
        cursor.execute('''
            SELECT pattern_type, win_rate, total_occurrences, avg_profit, probability_score,
                   confidence_level, reliability_rating, last_updated
            FROM pattern_statistics 
            WHERE symbol = ? AND direction = ? AND timeframe = ?
            ORDER BY probability_score DESC, win_rate DESC, total_occurrences DESC
            LIMIT 10
        ''', (symbol, direction.value, timeframe.value))
        
        top_patterns = cursor.fetchall()
        
        # Clear existing top patterns for this combination
        cursor.execute('''
            DELETE FROM top_patterns 
            WHERE symbol = ? AND direction = ? AND timeframe = ?
        ''', (symbol, direction.value, timeframe.value))
        
        # Insert new top patterns
        for rank, (pattern_type, win_rate, total_trades, avg_profit, probability_score, confidence_level, reliability_rating, last_updated) in enumerate(top_patterns, 1):
            
            # Get trigger conditions for this pattern
            cursor.execute('''
                SELECT trigger_conditions FROM historical_patterns 
                WHERE symbol = ? AND direction = ? AND timeframe = ? 
                AND ? = ANY(json_extract(patterns_identified, '$[*]'))
                AND final_outcome = 'WIN'
                ORDER BY timestamp DESC LIMIT 1
            ''', (symbol, direction.value, timeframe.value, pattern_type))
            
            trigger_result = cursor.fetchone()
            trigger_conditions = json.loads(trigger_result[0]) if trigger_result else {}
            
            pattern_id = f"{symbol}_{direction.value}_{timeframe.value}_{rank}"
            
            cursor.execute('''
                INSERT INTO top_patterns 
                (id, symbol, direction, timeframe, rank, pattern_signature, win_rate,
                 total_trades, avg_profit_percent, probability_score, trigger_conditions,
                 last_success, confidence_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id, symbol, direction.value, timeframe.value, rank,
                pattern_type, win_rate, total_trades, avg_profit, probability_score,
                json.dumps(trigger_conditions), last_updated, reliability_rating
            ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        cache_key = f"{symbol}_{direction.value}_{timeframe.value}"
        self.pattern_cache[cache_key] = self._load_top_patterns(symbol, direction, timeframe)
        
        logger.info(f"Updated top {len(top_patterns)} patterns for {symbol} {direction.value} {timeframe.value}")
    
    def get_top_patterns(self, symbol: str, direction: Direction, timeframe: TimeFrame) -> List[TopPattern]:
        """Get top 10 patterns for a symbol/direction/timeframe"""
        cache_key = f"{symbol}_{direction.value}_{timeframe.value}"
        
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]
        
        return self._load_top_patterns(symbol, direction, timeframe)
    
    def _load_top_patterns(self, symbol: str, direction: Direction, timeframe: TimeFrame) -> List[TopPattern]:
        """Load top patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rank, pattern_signature, win_rate, total_trades, avg_profit_percent,
                   probability_score, trigger_conditions, last_success, confidence_rating
            FROM top_patterns 
            WHERE symbol = ? AND direction = ? AND timeframe = ?
            ORDER BY rank
        ''', (symbol, direction.value, timeframe.value))
        
        patterns = []
        for row in cursor.fetchall():
            rank, pattern_sig, win_rate, total_trades, avg_profit, prob_score, trigger_cond, last_success, confidence = row
            
            patterns.append(TopPattern(
                rank=rank,
                pattern_signature=pattern_sig,
                win_rate=win_rate,
                total_trades=total_trades,
                avg_profit_percent=avg_profit,
                probability_score=prob_score,
                trigger_conditions=json.loads(trigger_cond),
                last_success=datetime.fromisoformat(last_success),
                confidence_rating=confidence
            ))
        
        conn.close()
        return patterns
    
    def _load_pattern_cache(self):
        """Load all top patterns into cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT symbol, direction, timeframe FROM top_patterns')
        combinations = cursor.fetchall()
        
        for symbol, direction, timeframe in combinations:
            cache_key = f"{symbol}_{direction}_{timeframe}"
            self.pattern_cache[cache_key] = self._load_top_patterns(
                symbol, Direction(direction), TimeFrame(timeframe)
            )
        
        conn.close()
        logger.info(f"Loaded {len(self.pattern_cache)} pattern combinations into cache")
    
    def get_pattern_probability_score(self, symbol: str, patterns: List[str], direction: Direction, timeframe: TimeFrame) -> float:
        """Get probability score for a set of patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        probability_scores = []
        
        for pattern in patterns:
            cursor.execute('''
                SELECT probability_score, confidence_level FROM pattern_statistics
                WHERE pattern_type = ? AND symbol = ? AND direction = ? AND timeframe = ?
            ''', (pattern, symbol, direction.value, timeframe.value))
            
            result = cursor.fetchone()
            if result:
                prob_score, confidence = result
                # Weight by confidence level
                weighted_score = prob_score * confidence
                probability_scores.append(weighted_score)
        
        conn.close()
        
        if probability_scores:
            # Use weighted average of pattern probabilities
            return float(np.mean(probability_scores))
        
        return 0.5  # Default neutral probability
    
    def get_historical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive historical analysis for a symbol"""
        analysis = {
            'symbol': symbol,
            'timeframes': {},
            'overall_statistics': {},
            'top_patterns_summary': {},
            'reliability_assessment': {}
        }
        
        for timeframe in TimeFrame:
            timeframe_data = {
                'long_patterns': self.get_top_patterns(symbol, Direction.LONG, timeframe),
                'short_patterns': self.get_top_patterns(symbol, Direction.SHORT, timeframe),
                'statistics': self._get_timeframe_statistics(symbol, timeframe)
            }
            analysis['timeframes'][timeframe.value] = timeframe_data
        
        # Calculate overall statistics
        analysis['overall_statistics'] = self._calculate_overall_statistics(symbol)
        
        # Generate reliability assessment
        analysis['reliability_assessment'] = self._assess_symbol_reliability(symbol)
        
        return analysis
    
    def _get_timeframe_statistics(self, symbol: str, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get statistics for a specific timeframe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), AVG(win_rate), AVG(probability_score), AVG(confidence_level)
            FROM pattern_statistics 
            WHERE symbol = ? AND timeframe = ?
        ''', (symbol, timeframe.value))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                'total_patterns': result[0],
                'avg_win_rate': result[1],
                'avg_probability_score': result[2],
                'avg_confidence_level': result[3]
            }
        
        return {
            'total_patterns': 0,
            'avg_win_rate': 0.0,
            'avg_probability_score': 0.0,
            'avg_confidence_level': 0.0
        }
    
    def _calculate_overall_statistics(self, symbol: str) -> Dict[str, Any]:
        """Calculate overall statistics for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), AVG(win_rate_score), AVG(max_profit), AVG(ABS(max_drawdown))
            FROM historical_patterns 
            WHERE symbol = ?
        ''', (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                'total_historical_patterns': result[0],
                'overall_win_rate': result[1],
                'avg_profit': result[2],
                'avg_loss': result[3],
                'data_maturity': 'HIGH' if result[0] > 100 else 'MEDIUM' if result[0] > 20 else 'LOW'
            }
        
        return {
            'total_historical_patterns': 0,
            'overall_win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_loss': 0.0,
            'data_maturity': 'NONE'
        }
    
    def _assess_symbol_reliability(self, symbol: str) -> Dict[str, Any]:
        """Assess the reliability of historical data for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get reliability distribution
        cursor.execute('''
            SELECT reliability_rating, COUNT(*) 
            FROM pattern_statistics 
            WHERE symbol = ? 
            GROUP BY reliability_rating
        ''', (symbol,))
        
        reliability_dist = dict(cursor.fetchall())
        
        # Calculate reliability score
        total_patterns = sum(reliability_dist.values())
        if total_patterns == 0:
            reliability_score = 0.0
        else:
            high_weight = reliability_dist.get('HIGH', 0) * 1.0
            medium_weight = reliability_dist.get('MEDIUM', 0) * 0.6
            low_weight = reliability_dist.get('LOW', 0) * 0.2
            
            reliability_score = (high_weight + medium_weight + low_weight) / total_patterns
        
        conn.close()
        
        return {
            'reliability_score': reliability_score,
            'reliability_distribution': reliability_dist,
            'assessment': self._get_reliability_assessment(reliability_score),
            'recommendation': self._get_reliability_recommendation(reliability_score, total_patterns)
        }
    
    def _get_reliability_assessment(self, score: float) -> str:
        """Get reliability assessment based on score"""
        if score >= 0.8:
            return 'HIGHLY_RELIABLE'
        elif score >= 0.6:
            return 'MODERATELY_RELIABLE'
        elif score >= 0.3:
            return 'LOW_RELIABILITY'
        else:
            return 'INSUFFICIENT_DATA'
    
    def _get_reliability_recommendation(self, score: float, total_patterns: int) -> str:
        """Get recommendation based on reliability"""
        if total_patterns < 10:
            return 'Collect more historical data before making trading decisions'
        elif score >= 0.7:
            return 'Historical patterns show strong reliability for trading decisions'
        elif score >= 0.5:
            return 'Use historical patterns as supporting evidence with other analysis'
        else:
            return 'Historical patterns show low reliability, use with caution'
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Table sizes
        for table in ['historical_patterns', 'pattern_statistics', 'top_patterns', 'endpoint_historical_performance']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[f'{table}_count'] = cursor.fetchone()[0]
        
        # Symbol coverage
        cursor.execute('SELECT COUNT(DISTINCT symbol) FROM historical_patterns')
        stats['symbols_tracked'] = cursor.fetchone()[0]
        
        # Timeframe coverage
        cursor.execute('SELECT timeframe, COUNT(*) FROM historical_patterns GROUP BY timeframe')
        stats['timeframe_distribution'] = dict(cursor.fetchall())
        
        conn.close()
        
        return stats