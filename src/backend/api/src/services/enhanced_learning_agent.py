#!/usr/bin/env python3
"""
Enhanced Self-Learning AI Analysis Agent
Specifically designed to understand and improve AVAX-style comprehensive reports
"""

import json
import sqlite3
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import re

from src.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class ReportStructureAnalysis:
    """Analysis of report structure quality and AVAX compliance"""
    symbol: str
    timestamp: datetime
    sections_found: List[str]
    avax_sections_found: List[str]
    missing_sections: List[str]
    structure_quality: float
    avax_compliant: bool
    win_rates_extracted: Dict[str, float]
    composite_scores: Dict[str, float]
    scoring_valid: bool
    report_length: int
    
@dataclass
class LearningPattern:
    """Enhanced learning pattern for AVAX-style reports"""
    pattern_id: str
    pattern_type: str  # 'structure', 'content', 'scoring', 'recommendation'
    success_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    confidence_level: float
    usage_count: int
    last_updated: datetime

@dataclass
class StructureTemplate:
    """Template for AVAX-style report structure"""
    required_sections: List[str]
    optional_sections: List[str]
    section_order: List[str]
    content_patterns: Dict[str, str]
    validation_rules: Dict[str, Any]

class EnhancedLearningAgent:
    """
    Enhanced Learning Agent specifically designed for AVAX-style comprehensive reports
    """
    
    def __init__(self, learning_db_path: str = "enhanced_learning_data.db"):
        """Initialize the Enhanced Learning Agent"""
        self.db_path = learning_db_path
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.structure_templates: Dict[str, StructureTemplate] = {}
        
        # Define AVAX structure template
        self.avax_template = self._create_avax_template()
        
        # Initialize database
        self._init_enhanced_database()
        
        # Load existing learning data
        self._load_enhanced_learning_data()
        
        logger.info("Enhanced Learning Agent initialized with AVAX structure understanding")
    
    def _create_avax_template(self) -> StructureTemplate:
        """Create the AVAX report structure template"""
        required_sections = [
            "🎯 WIN RATE SUMMARY",
            "📊 COMPOSITE SCORES", 
            "🔑 KEY MARKET METRICS",
            "📈 TRADING RECOMMENDATIONS",
            "⚠️ RISK FACTORS",
            "🎯 MARKET SCENARIOS"
        ]
        
        optional_sections = [
            "Range Trading Data",
            "Liquidation Data", 
            "Positioning Data",
            "💡 KEY INSIGHTS",
            "🚨 IMMEDIATE ACTION ITEMS",
            "📊 PROBABILITY-WEIGHTED RETURNS",
            "📈 FIBONACCI TARGETS",
            "🔍 VOLUME REQUIREMENTS"
        ]
        
        section_order = [
            "Quick Reference Guide",
            "🎯 WIN RATE SUMMARY",
            "📊 COMPOSITE SCORES",
            "🔑 KEY MARKET METRICS",
            "📈 TRADING RECOMMENDATIONS", 
            "⚠️ RISK FACTORS",
            "🎯 MARKET SCENARIOS",
            "💡 KEY INSIGHTS",
            "🚨 IMMEDIATE ACTION ITEMS",
            "📊 PROBABILITY-WEIGHTED RETURNS",
            "📈 FIBONACCI TARGETS",
            "🔍 VOLUME REQUIREMENTS"
        ]
        
        content_patterns = {
            "win_rate_pattern": r"(\d+\.?\d*)% win rate",
            "composite_score_pattern": r"(\d+\.?\d*)/100",
            "price_pattern": r"\$(\d+\.?\d*)",
            "percentage_pattern": r"([+-]?\d+\.?\d*)%",
            "timeframe_pattern": r"(24-48 Hours?|7 Days?|1 Month)"
        }
        
        validation_rules = {
            "min_sections": 6,
            "min_length": 3000,
            "composite_scores_sum": 100.0,
            "win_rates_range": (20.0, 80.0),
            "required_timeframes": ["24-48 Hours", "7 Days", "1 Month"]
        }
        
        return StructureTemplate(
            required_sections=required_sections,
            optional_sections=optional_sections,
            section_order=section_order,
            content_patterns=content_patterns,
            validation_rules=validation_rules
        )
    
    def _init_enhanced_database(self):
        """Initialize enhanced SQLite database for learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced structure analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_structures (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                timestamp TEXT,
                sections_found TEXT,
                avax_sections_found TEXT,
                missing_sections TEXT,
                structure_quality REAL,
                avax_compliant INTEGER,
                win_rates_extracted TEXT,
                composite_scores TEXT,
                scoring_valid INTEGER,
                report_length INTEGER
            )
        ''')
        
        # Learning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                success_metrics TEXT,
                improvement_suggestions TEXT,
                confidence_level REAL,
                usage_count INTEGER,
                last_updated TEXT
            )
        ''')
        
        # Structure improvement suggestions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_suggestions (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                suggestion_type TEXT,
                suggestion_text TEXT,
                priority INTEGER,
                implemented INTEGER,
                created_at TEXT
            )
        ''')
        
        # Performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                metric_type TEXT,
                metric_value REAL,
                benchmark_value REAL,
                improvement_percentage REAL,
                recorded_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Enhanced learning database initialized")
    
    def analyze_report_structure(self, symbol: str, report_content: str) -> ReportStructureAnalysis:
        """Analyze report structure against AVAX standards"""
        try:
            lines = report_content.split('\n')
            sections_found = []
            avax_sections_found = []
            win_rates = {}
            composite_scores = {}
            
            # Extract sections
            for line in lines:
                if line.startswith('##') and not line.startswith('###'):
                    sections_found.append(line.strip())
                
                # Check for AVAX sections
                for section in self.avax_template.required_sections + self.avax_template.optional_sections:
                    if section in line:
                        avax_sections_found.append(section)
            
            # Extract win rates using patterns
            win_rate_pattern = re.compile(self.avax_template.content_patterns["win_rate_pattern"])
            timeframe_pattern = re.compile(self.avax_template.content_patterns["timeframe_pattern"])
            
            current_position_type = None
            for line in lines:
                if "Long Positions" in line:
                    current_position_type = "long"
                elif "Short Positions" in line:
                    current_position_type = "short"
                
                if current_position_type and win_rate_pattern.search(line):
                    rate_match = win_rate_pattern.search(line)
                    timeframe_match = timeframe_pattern.search(line)
                    
                    if rate_match and timeframe_match:
                        rate = float(rate_match.group(1))
                        timeframe = timeframe_match.group(1)
                        
                        # Standardize timeframe names
                        if "24-48" in timeframe:
                            tf_key = "24_48h"
                        elif "7 Days" in timeframe:
                            tf_key = "7d"
                        elif "1 Month" in timeframe:
                            tf_key = "1m"
                        else:
                            continue
                            
                        win_rates[f"{current_position_type}_{tf_key}"] = rate
            
            # Extract composite scores
            composite_pattern = re.compile(self.avax_template.content_patterns["composite_score_pattern"])
            for line in lines:
                if "Long Position Score:" in line:
                    match = composite_pattern.search(line)
                    if match:
                        composite_scores["long_score"] = float(match.group(1))
                elif "Short Position Score:" in line:
                    match = composite_pattern.search(line)
                    if match:
                        composite_scores["short_score"] = float(match.group(1))
            
            # Calculate quality metrics
            required_found = len([s for s in self.avax_template.required_sections if s in avax_sections_found])
            total_required = len(self.avax_template.required_sections)
            structure_quality = required_found / total_required if total_required > 0 else 0.0
            
            # Check scoring validity
            scoring_valid = False
            if "long_score" in composite_scores and "short_score" in composite_scores:
                total = composite_scores["long_score"] + composite_scores["short_score"]
                scoring_valid = abs(total - 100.0) < 0.1
            
            # Determine missing sections
            missing_sections = [s for s in self.avax_template.required_sections if s not in avax_sections_found]
            
            # AVAX compliance check
            avax_compliant = (
                structure_quality >= 0.8 and
                scoring_valid and
                len(report_content) >= self.avax_template.validation_rules["min_length"] and
                len(win_rates) >= 4  # At least some win rates extracted
            )
            
            analysis = ReportStructureAnalysis(
                symbol=symbol,
                timestamp=datetime.now(),
                sections_found=sections_found,
                avax_sections_found=avax_sections_found,
                missing_sections=missing_sections,
                structure_quality=structure_quality,
                avax_compliant=avax_compliant,
                win_rates_extracted=win_rates,
                composite_scores=composite_scores,
                scoring_valid=scoring_valid,
                report_length=len(report_content)
            )
            
            # Store analysis in database
            self._store_structure_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing report structure for {symbol}: {e}")
            return ReportStructureAnalysis(
                symbol=symbol,
                timestamp=datetime.now(),
                sections_found=[],
                avax_sections_found=[],
                missing_sections=self.avax_template.required_sections,
                structure_quality=0.0,
                avax_compliant=False,
                win_rates_extracted={},
                composite_scores={},
                scoring_valid=False,
                report_length=len(report_content) if report_content else 0
            )
    
    def generate_improvement_suggestions(self, analysis: ReportStructureAnalysis) -> List[str]:
        """Generate specific improvement suggestions based on analysis"""
        suggestions = []
        
        # Structure improvements
        if analysis.structure_quality < 0.8:
            suggestions.append(f"Add missing required sections: {', '.join(analysis.missing_sections)}")
        
        # Scoring improvements
        if not analysis.scoring_valid:
            if analysis.composite_scores:
                total = sum(analysis.composite_scores.values())
                suggestions.append(f"Fix composite scores to total 100 (currently {total:.1f})")
            else:
                suggestions.append("Add composite scoring section with complementary Long/Short scores")
        
        # Content length
        if analysis.report_length < self.avax_template.validation_rules["min_length"]:
            suggestions.append(f"Expand report content (current: {analysis.report_length}, target: {self.avax_template.validation_rules['min_length']})")
        
        # Win rate data
        if len(analysis.win_rates_extracted) < 6:  # 3 timeframes × 2 positions
            suggestions.append("Include complete win rate data for all timeframes (24-48h, 7d, 1m) and both positions")
        
        # Section ordering
        if analysis.sections_found:
            expected_order = self.avax_template.section_order
            actual_sections = [s.replace('## ', '') for s in analysis.sections_found]
            
            # Check if sections follow expected order
            order_issues = []
            for i, section in enumerate(actual_sections):
                if section in expected_order:
                    expected_pos = expected_order.index(section)
                    if i > 0 and expected_pos < expected_order.index(actual_sections[i-1].replace('## ', '')):
                        order_issues.append(section)
            
            if order_issues:
                suggestions.append(f"Reorder sections to follow AVAX template: {', '.join(order_issues)}")
        
        # Store suggestions
        self._store_improvement_suggestions(analysis.symbol, suggestions)
        
        return suggestions
    
    def learn_from_report(self, symbol: str, report_content: str, user_feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Learn from a generated report and user feedback"""
        try:
            # Analyze structure
            analysis = self.analyze_report_structure(symbol, report_content)
            
            # Generate improvements
            suggestions = self.generate_improvement_suggestions(analysis)
            
            # Update learning patterns
            pattern_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            success_metrics = {
                "structure_quality": analysis.structure_quality,
                "avax_compliance": 1.0 if analysis.avax_compliant else 0.0,
                "scoring_validity": 1.0 if analysis.scoring_valid else 0.0,
                "content_completeness": min(analysis.report_length / self.avax_template.validation_rules["min_length"], 1.0)
            }
            
            # Incorporate user feedback if provided
            if user_feedback:
                if "quality_rating" in user_feedback:
                    success_metrics["user_rating"] = user_feedback["quality_rating"] / 5.0  # Normalize to 0-1
                if "specific_feedback" in user_feedback:
                    suggestions.extend(user_feedback["specific_feedback"])
            
            # Create learning pattern
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type="structure_analysis",
                success_metrics=success_metrics,
                improvement_suggestions=suggestions,
                confidence_level=analysis.structure_quality,
                usage_count=1,
                last_updated=datetime.now()
            )
            
            # Store pattern
            self.learning_patterns[pattern_id] = pattern
            self._store_learning_pattern(pattern)
            
            # Calculate overall improvement score
            improvement_score = np.mean(list(success_metrics.values()))
            
            logger.info(f"Learning completed for {symbol}: Quality={analysis.structure_quality:.2f}, Improvement={improvement_score:.2f}")
            
            return {
                "analysis": asdict(analysis),
                "suggestions": suggestions,
                "improvement_score": improvement_score,
                "learning_pattern_id": pattern_id,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error learning from report for {symbol}: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def get_adaptive_generation_params(self, symbol: str) -> Dict[str, Any]:
        """Get adaptive parameters for report generation based on learning"""
        try:
            # Get recent patterns for this symbol
            recent_patterns = self._get_recent_patterns(symbol, days=30)
            
            if not recent_patterns:
                # Return default AVAX-compliant parameters
                return {
                    "structure_template": "avax_comprehensive",
                    "required_sections": self.avax_template.required_sections,
                    "optional_sections": self.avax_template.optional_sections,
                    "section_order": self.avax_template.section_order,
                    "validation_rules": self.avax_template.validation_rules,
                    "confidence_boost": 1.0,
                    "quality_target": 0.85
                }
            
            # Calculate adaptive parameters based on learning
            avg_quality = np.mean([p.confidence_level for p in recent_patterns])
            common_suggestions = self._get_common_suggestions(recent_patterns)
            
            # Boost confidence for well-performing patterns
            confidence_boost = min(1.0 + (avg_quality - 0.5), 1.5)
            
            # Adjust quality target based on historical performance
            quality_target = max(0.8, min(avg_quality + 0.1, 0.95))
            
            return {
                "structure_template": "avax_comprehensive",
                "required_sections": self.avax_template.required_sections,
                "optional_sections": self.avax_template.optional_sections,
                "section_order": self.avax_template.section_order,
                "validation_rules": self.avax_template.validation_rules,
                "confidence_boost": confidence_boost,
                "quality_target": quality_target,
                "common_improvements": common_suggestions,
                "historical_performance": avg_quality,
                "pattern_count": len(recent_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error getting adaptive parameters for {symbol}: {e}")
            return self.get_adaptive_generation_params("default")  # Fallback
    
    def _store_structure_analysis(self, analysis: ReportStructureAnalysis):
        """Store structure analysis in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO report_structures 
                (id, symbol, timestamp, sections_found, avax_sections_found, missing_sections,
                 structure_quality, avax_compliant, win_rates_extracted, composite_scores,
                 scoring_valid, report_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"{analysis.symbol}_{analysis.timestamp.isoformat()}",
                analysis.symbol,
                analysis.timestamp.isoformat(),
                json.dumps(analysis.sections_found),
                json.dumps(analysis.avax_sections_found),
                json.dumps(analysis.missing_sections),
                analysis.structure_quality,
                1 if analysis.avax_compliant else 0,
                json.dumps(analysis.win_rates_extracted),
                json.dumps(analysis.composite_scores),
                1 if analysis.scoring_valid else 0,
                analysis.report_length
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing structure analysis: {e}")
    
    def _store_learning_pattern(self, pattern: LearningPattern):
        """Store learning pattern in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_patterns 
                (pattern_id, pattern_type, success_metrics, improvement_suggestions,
                 confidence_level, usage_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.pattern_type,
                json.dumps(pattern.success_metrics),
                json.dumps(pattern.improvement_suggestions),
                pattern.confidence_level,
                pattern.usage_count,
                pattern.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing learning pattern: {e}")
    
    def _store_improvement_suggestions(self, symbol: str, suggestions: List[str]):
        """Store improvement suggestions in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for i, suggestion in enumerate(suggestions):
                cursor.execute('''
                    INSERT INTO improvement_suggestions 
                    (id, symbol, suggestion_type, suggestion_text, priority, implemented, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    symbol,
                    "structure_improvement",
                    suggestion,
                    len(suggestions) - i,  # Higher number = higher priority
                    0,  # Not implemented yet
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing improvement suggestions: {e}")
    
    def _load_enhanced_learning_data(self):
        """Load existing enhanced learning data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load learning patterns
            cursor.execute('SELECT * FROM learning_patterns')
            rows = cursor.fetchall()
            
            for row in rows:
                pattern = LearningPattern(
                    pattern_id=row[0],
                    pattern_type=row[1],
                    success_metrics=json.loads(row[2]),
                    improvement_suggestions=json.loads(row[3]),
                    confidence_level=row[4],
                    usage_count=row[5],
                    last_updated=datetime.fromisoformat(row[6])
                )
                self.learning_patterns[pattern.pattern_id] = pattern
            
            conn.close()
            
            logger.info(f"Loaded {len(self.learning_patterns)} learning patterns")
            
        except Exception as e:
            logger.error(f"Error loading enhanced learning data: {e}")
    
    def _get_recent_patterns(self, symbol: str, days: int = 30) -> List[LearningPattern]:
        """Get recent learning patterns for a symbol"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            pattern for pattern in self.learning_patterns.values()
            if symbol in pattern.pattern_id and pattern.last_updated >= cutoff_date
        ]
    
    def _get_common_suggestions(self, patterns: List[LearningPattern]) -> List[str]:
        """Get most common improvement suggestions from patterns"""
        suggestion_counts = {}
        
        for pattern in patterns:
            for suggestion in pattern.improvement_suggestions:
                suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
        
        # Return top 5 most common suggestions
        sorted_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)
        return [suggestion for suggestion, count in sorted_suggestions[:5]]
    
    def get_learning_summary(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of learning progress"""
        try:
            patterns = list(self.learning_patterns.values())
            if symbol:
                patterns = [p for p in patterns if symbol in p.pattern_id]
            
            if not patterns:
                return {
                    "total_patterns": 0,
                    "avg_quality": 0.0,
                    "avax_compliance_rate": 0.0,
                    "top_improvements": [],
                    "learning_trend": "No data"
                }
            
            # Calculate metrics
            total_patterns = len(patterns)
            avg_quality = np.mean([p.confidence_level for p in patterns])
            
            # Calculate AVAX compliance rate
            avax_compliant = sum(1 for p in patterns if p.success_metrics.get("avax_compliance", 0) > 0.8)
            avax_compliance_rate = avax_compliant / total_patterns if total_patterns > 0 else 0.0
            
            # Get top improvements
            top_improvements = self._get_common_suggestions(patterns)
            
            # Determine learning trend
            if len(patterns) >= 5:
                recent_quality = np.mean([p.confidence_level for p in patterns[-5:]])
                older_quality = np.mean([p.confidence_level for p in patterns[:-5]])
                
                if recent_quality > older_quality + 0.05:
                    learning_trend = "Improving"
                elif recent_quality < older_quality - 0.05:
                    learning_trend = "Declining"
                else:
                    learning_trend = "Stable"
            else:
                learning_trend = "Insufficient data"
            
            return {
                "total_patterns": total_patterns,
                "avg_quality": avg_quality,
                "avax_compliance_rate": avax_compliance_rate,
                "top_improvements": top_improvements,
                "learning_trend": learning_trend,
                "symbol_filter": symbol
            }
            
        except Exception as e:
            logger.error(f"Error generating learning summary: {e}")
            return {"error": str(e)}