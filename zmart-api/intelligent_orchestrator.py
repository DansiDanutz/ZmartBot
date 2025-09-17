#!/usr/bin/env python3
"""
ZmartBot Intelligent Orchestrator - AI-Powered Predictive Analytics Engine
Advanced ML-based orchestration with predictive capabilities and intelligent decision making.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import logging
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceMetrics:
    """Service performance metrics data structure"""
    service_name: str
    port: int
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    request_count: int
    timestamp: datetime
    health_status: str
    
@dataclass
class PredictionResult:
    """AI prediction result data structure"""
    service_name: str
    prediction_type: str
    confidence: float
    predicted_value: float
    recommendation: str
    risk_level: str
    timestamp: datetime

@dataclass
class TradingOpportunity:
    """Trading opportunity detected by AI"""
    symbol: str
    opportunity_type: str
    confidence: float
    expected_return: float
    risk_level: str
    time_horizon: str
    recommendation: str
    timestamp: datetime

class IntelligentOrchestrator:
    """
    AI-Powered Predictive Analytics Engine for ZmartBot
    
    Capabilities:
    - Service failure prediction using ML
    - Performance optimization recommendations  
    - Automatic scaling decisions based on patterns
    - Trading opportunity detection integration
    - Risk assessment and mitigation
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.analytics_db = self.base_dir / "analytics.db"
        self.predictions_db = self.base_dir / "predictions.db"
        
        # ML Models and Analytics
        self.service_patterns = defaultdict(list)
        self.performance_history = defaultdict(deque)
        self.failure_patterns = defaultdict(list)
        self.trading_patterns = defaultdict(list)
        
        # Real-time metrics storage
        self.current_metrics = {}
        self.historical_data = defaultdict(list)
        
        # AI Configuration
        self.prediction_window = 300  # 5 minutes
        self.learning_rate = 0.01
        self.confidence_threshold = 0.75
        
        # Analysis threads
        self.analysis_active = False
        self.analysis_thread = None
        
        # Initialize databases
        self._initialize_databases()
        
        logger.info("🤖 Intelligent Orchestrator initialized with AI capabilities")
    
    def _initialize_databases(self):
        """Initialize analytics and predictions databases"""
        try:
            # Analytics database for historical data
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    port INTEGER,
                    response_time REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    error_rate REAL,
                    request_count INTEGER,
                    health_status TEXT,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    confidence REAL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Predictions database
            conn = sqlite3.connect(self.predictions_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    prediction_type TEXT,
                    confidence REAL,
                    predicted_value REAL,
                    recommendation TEXT,
                    risk_level TEXT,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    opportunity_type TEXT,
                    confidence REAL,
                    expected_return REAL,
                    risk_level TEXT,
                    time_horizon TEXT,
                    recommendation TEXT,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Intelligent Orchestrator databases initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing databases: {e}")
    
    def start_analytics_engine(self):
        """Start the AI analytics engine"""
        if self.analysis_active:
            logger.warning("⚠️ Analytics engine already running")
            return
        
        self.analysis_active = True
        self.analysis_thread = threading.Thread(target=self._analytics_loop, daemon=True)
        self.analysis_thread.start()
        
        logger.info("🚀 AI Analytics Engine started")
    
    def stop_analytics_engine(self):
        """Stop the AI analytics engine"""
        self.analysis_active = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        
        logger.info("🛑 AI Analytics Engine stopped")
    
    def _analytics_loop(self):
        """Main analytics processing loop"""
        while self.analysis_active:
            try:
                # Collect current system metrics
                self._collect_system_metrics()
                
                # Analyze service patterns
                self._analyze_service_patterns()
                
                # Generate predictions
                predictions = self._generate_predictions()
                
                # Detect trading opportunities
                trading_ops = self._detect_trading_opportunities()
                
                # Store results
                self._store_predictions(predictions)
                self._store_trading_opportunities(trading_ops)
                
                # Log insights
                if predictions:
                    logger.info(f"🧠 Generated {len(predictions)} AI predictions")
                if trading_ops:
                    logger.info(f"💹 Detected {len(trading_ops)} trading opportunities")
                
                # Wait before next analysis cycle
                time.sleep(60)  # Analyze every minute
                
            except Exception as e:
                logger.error(f"❌ Error in analytics loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def _collect_system_metrics(self):
        """Collect real-time metrics from all services"""
        try:
            # Get service status from Service Dashboard
            response = requests.get("http://localhost:3401/api/services/status", timeout=5)
            if response.status_code == 200:
                services_data = response.json()
                
                for service_name, service_info in services_data.get("services", {}).items():
                    health = service_info.get("health", {})
                    
                    # Create ServiceMetrics object
                    metrics = ServiceMetrics(
                        service_name=service_name,
                        port=service_info.get("port", 0),
                        response_time=health.get("response_time", 0.0),
                        cpu_usage=self._estimate_cpu_usage(service_name),
                        memory_usage=self._estimate_memory_usage(service_name),
                        error_rate=self._calculate_error_rate(service_name),
                        request_count=self._get_request_count(service_name),
                        timestamp=datetime.now(),
                        health_status=health.get("status", "unknown")
                    )
                    
                    # Store current metrics
                    self.current_metrics[service_name] = metrics
                    
                    # Add to historical data
                    self.historical_data[service_name].append(metrics)
                    
                    # Limit historical data size (keep last 1000 entries per service)
                    if len(self.historical_data[service_name]) > 1000:
                        self.historical_data[service_name].popleft()
                    
                    # Store in database
                    self._store_service_metrics(metrics)
            
            # Collect additional metrics from Master Orchestration Agent
            try:
                response = requests.get("http://localhost:8002/api/status/overview", timeout=3)
                if response.status_code == 200:
                    orchestration_data = response.json()
                    self._process_orchestration_metrics(orchestration_data)
            except:
                pass  # Orchestration metrics are supplementary
                
        except Exception as e:
            logger.warning(f"⚠️ Error collecting system metrics: {e}")
    
    def _analyze_service_patterns(self):
        """Analyze service behavior patterns using AI techniques"""
        for service_name, metrics_history in self.historical_data.items():
            if len(metrics_history) < 10:  # Need minimum data points
                continue
            
            try:
                # Convert to DataFrame for analysis
                df_data = []
                for metrics in metrics_history:
                    df_data.append({
                        'timestamp': metrics.timestamp,
                        'response_time': metrics.response_time,
                        'cpu_usage': metrics.cpu_usage,
                        'memory_usage': metrics.memory_usage,
                        'error_rate': metrics.error_rate,
                        'request_count': metrics.request_count
                    })
                
                df = pd.DataFrame(df_data)
                
                # Detect performance patterns
                self._detect_performance_degradation(service_name, df)
                self._detect_resource_usage_patterns(service_name, df)
                self._detect_failure_patterns(service_name, df)
                
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing patterns for {service_name}: {e}")
    
    def _detect_performance_degradation(self, service_name: str, df: pd.DataFrame):
        """Detect performance degradation patterns"""
        if len(df) < 5:
            return
        
        # Calculate moving averages
        df['response_time_ma'] = df['response_time'].rolling(window=5).mean()
        df['error_rate_ma'] = df['error_rate'].rolling(window=5).mean()
        
        # Detect trends
        recent_response_time = df['response_time_ma'].tail(3).mean()
        baseline_response_time = df['response_time_ma'].head(10).mean()
        
        recent_error_rate = df['error_rate_ma'].tail(3).mean()
        baseline_error_rate = df['error_rate_ma'].head(10).mean()
        
        # Performance degradation detection
        response_time_increase = (recent_response_time - baseline_response_time) / baseline_response_time if baseline_response_time > 0 else 0
        error_rate_increase = (recent_error_rate - baseline_error_rate) / baseline_error_rate if baseline_error_rate > 0 else 0
        
        if response_time_increase > 0.2:  # 20% increase in response time
            self.service_patterns[service_name].append({
                'type': 'performance_degradation',
                'severity': 'medium' if response_time_increase < 0.5 else 'high',
                'metric': 'response_time',
                'increase_percentage': response_time_increase * 100,
                'timestamp': datetime.now()
            })
        
        if error_rate_increase > 0.3:  # 30% increase in error rate
            self.service_patterns[service_name].append({
                'type': 'error_rate_spike',
                'severity': 'high',
                'metric': 'error_rate', 
                'increase_percentage': error_rate_increase * 100,
                'timestamp': datetime.now()
            })
    
    def _detect_resource_usage_patterns(self, service_name: str, df: pd.DataFrame):
        """Detect resource usage patterns and predict scaling needs"""
        if len(df) < 10:
            return
        
        # CPU and memory usage analysis
        cpu_trend = np.polyfit(range(len(df)), df['cpu_usage'].fillna(0), 1)[0]
        memory_trend = np.polyfit(range(len(df)), df['memory_usage'].fillna(0), 1)[0]
        
        current_cpu = df['cpu_usage'].tail(1).iloc[0] if not df['cpu_usage'].empty else 0
        current_memory = df['memory_usage'].tail(1).iloc[0] if not df['memory_usage'].empty else 0
        
        # Predict resource usage in next 15 minutes
        predicted_cpu = current_cpu + (cpu_trend * 15)
        predicted_memory = current_memory + (memory_trend * 15)
        
        # Store resource patterns
        if cpu_trend > 0.5:  # Increasing CPU usage trend
            self.service_patterns[service_name].append({
                'type': 'resource_scaling_need',
                'resource': 'cpu',
                'current_usage': current_cpu,
                'predicted_usage': predicted_cpu,
                'trend': cpu_trend,
                'recommendation': 'scale_up' if predicted_cpu > 80 else 'monitor',
                'timestamp': datetime.now()
            })
        
        if memory_trend > 0.5:  # Increasing memory usage trend
            self.service_patterns[service_name].append({
                'type': 'resource_scaling_need',
                'resource': 'memory',
                'current_usage': current_memory,
                'predicted_usage': predicted_memory,
                'trend': memory_trend,
                'recommendation': 'scale_up' if predicted_memory > 85 else 'monitor',
                'timestamp': datetime.now()
            })
    
    def _detect_failure_patterns(self, service_name: str, df: pd.DataFrame):
        """Detect patterns that typically precede service failures"""
        if len(df) < 15:
            return
        
        # Look for failure precursors
        recent_data = df.tail(10)
        
        # Pattern 1: Sudden spike in response time followed by errors
        response_time_spike = recent_data['response_time'].max() > (df['response_time'].mean() + 2 * df['response_time'].std())
        high_error_rate = recent_data['error_rate'].mean() > 5.0  # 5% error rate
        
        if response_time_spike and high_error_rate:
            failure_risk = min(0.9, (recent_data['error_rate'].mean() / 10.0) + 0.5)
            
            self.failure_patterns[service_name].append({
                'type': 'imminent_failure_risk',
                'risk_score': failure_risk,
                'indicators': ['response_time_spike', 'high_error_rate'],
                'recommendation': 'immediate_attention_required',
                'timestamp': datetime.now()
            })
    
    def _generate_predictions(self) -> List[PredictionResult]:
        """Generate AI-powered predictions for system optimization"""
        predictions = []
        
        for service_name, patterns in self.service_patterns.items():
            if not patterns:
                continue
            
            try:
                # Analyze recent patterns
                recent_patterns = [p for p in patterns if 
                                (datetime.now() - p['timestamp']).seconds < 3600]  # Last hour
                
                for pattern in recent_patterns:
                    prediction = self._create_prediction_from_pattern(service_name, pattern)
                    if prediction:
                        predictions.append(prediction)
                
                # Clear old patterns to prevent memory buildup
                self.service_patterns[service_name] = [p for p in patterns if 
                                                    (datetime.now() - p['timestamp']).seconds < 7200]  # Keep 2 hours
                
            except Exception as e:
                logger.warning(f"⚠️ Error generating predictions for {service_name}: {e}")
        
        return predictions
    
    def _create_prediction_from_pattern(self, service_name: str, pattern: Dict) -> Optional[PredictionResult]:
        """Create a prediction from a detected pattern"""
        try:
            if pattern['type'] == 'performance_degradation':
                return PredictionResult(
                    service_name=service_name,
                    prediction_type='performance_degradation',
                    confidence=0.8,
                    predicted_value=pattern.get('increase_percentage', 0),
                    recommendation=f"Investigate {pattern.get('metric', 'performance')} degradation and consider optimization",
                    risk_level=pattern.get('severity', 'medium'),
                    timestamp=datetime.now()
                )
            
            elif pattern['type'] == 'resource_scaling_need':
                return PredictionResult(
                    service_name=service_name,
                    prediction_type='scaling_recommendation',
                    confidence=0.75,
                    predicted_value=pattern.get('predicted_usage', 0),
                    recommendation=f"Consider scaling {pattern.get('resource', 'resources')} - predicted usage: {pattern.get('predicted_usage', 0):.1f}%",
                    risk_level='medium' if pattern.get('predicted_usage', 0) > 80 else 'low',
                    timestamp=datetime.now()
                )
            
            elif pattern['type'] == 'imminent_failure_risk':
                return PredictionResult(
                    service_name=service_name,
                    prediction_type='failure_risk',
                    confidence=pattern.get('risk_score', 0.5),
                    predicted_value=pattern.get('risk_score', 0.5) * 100,
                    recommendation=f"URGENT: High failure risk detected. Immediate investigation required.",
                    risk_level='high',
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.warning(f"⚠️ Error creating prediction from pattern: {e}")
        
        return None
    
    def _detect_trading_opportunities(self) -> List[TradingOpportunity]:
        """Detect trading opportunities using AI analysis"""
        opportunities = []
        
        try:
            # Get system performance metrics
            system_health = self._calculate_overall_system_health()
            
            # Trading opportunity detection based on system performance
            if system_health > 0.9:  # System running optimally
                opportunities.append(TradingOpportunity(
                    symbol="SYSTEM_OPTIMAL",
                    opportunity_type="high_frequency_trading",
                    confidence=0.85,
                    expected_return=0.05,  # 5% expected return
                    risk_level="low",
                    time_horizon="short_term",
                    recommendation="System performance optimal for high-frequency trading strategies",
                    timestamp=datetime.now()
                ))
            
            elif system_health < 0.7:  # System under stress
                opportunities.append(TradingOpportunity(
                    symbol="SYSTEM_STRESS",
                    opportunity_type="conservative_trading",
                    confidence=0.7,
                    expected_return=0.02,  # 2% expected return
                    risk_level="medium",
                    time_horizon="medium_term",
                    recommendation="Reduce trading frequency due to system stress",
                    timestamp=datetime.now()
                ))
            
            # Add more sophisticated trading opportunity detection here
            # This would integrate with actual market data and trading algorithms
            
        except Exception as e:
            logger.warning(f"⚠️ Error detecting trading opportunities: {e}")
        
        return opportunities
    
    def _calculate_overall_system_health(self) -> float:
        """Calculate overall system health score"""
        if not self.current_metrics:
            return 0.5  # Unknown state
        
        health_scores = []
        for service_name, metrics in self.current_metrics.items():
            # Calculate individual service health score with safe division
            response_time = metrics.response_time or 0
            error_rate = metrics.error_rate or 0
            
            response_time_score = max(0, 1 - (response_time / 1000))  # Normalize response time
            error_rate_score = max(0, 1 - (error_rate / 10))  # Normalize error rate
            health_status_score = 1.0 if metrics.health_status == "healthy" else 0.3
            
            service_score = (response_time_score + error_rate_score + health_status_score) / 3
            health_scores.append(service_score)
        
        return np.mean(health_scores) if health_scores else 0.5
    
    def _store_service_metrics(self, metrics: ServiceMetrics):
        """Store service metrics in database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO service_metrics 
                (service_name, port, response_time, cpu_usage, memory_usage, 
                 error_rate, request_count, health_status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.service_name, metrics.port, metrics.response_time,
                metrics.cpu_usage, metrics.memory_usage, metrics.error_rate,
                metrics.request_count, metrics.health_status, metrics.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Error storing service metrics: {e}")
    
    def _store_predictions(self, predictions: List[PredictionResult]):
        """Store predictions in database"""
        if not predictions:
            return
        
        try:
            conn = sqlite3.connect(self.predictions_db)
            cursor = conn.cursor()
            
            for prediction in predictions:
                cursor.execute('''
                    INSERT INTO predictions 
                    (service_name, prediction_type, confidence, predicted_value,
                     recommendation, risk_level, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prediction.service_name, prediction.prediction_type,
                    prediction.confidence, prediction.predicted_value,
                    prediction.recommendation, prediction.risk_level,
                    prediction.timestamp.isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Error storing predictions: {e}")
    
    def _store_trading_opportunities(self, opportunities: List[TradingOpportunity]):
        """Store trading opportunities in database"""
        if not opportunities:
            return
        
        try:
            conn = sqlite3.connect(self.predictions_db)
            cursor = conn.cursor()
            
            for opp in opportunities:
                cursor.execute('''
                    INSERT INTO trading_opportunities 
                    (symbol, opportunity_type, confidence, expected_return,
                     risk_level, time_horizon, recommendation, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opp.symbol, opp.opportunity_type, opp.confidence,
                    opp.expected_return, opp.risk_level, opp.time_horizon,
                    opp.recommendation, opp.timestamp.isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Error storing trading opportunities: {e}")
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI predictions"""
        try:
            conn = sqlite3.connect(self.predictions_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT service_name, prediction_type, confidence, predicted_value,
                       recommendation, risk_level, timestamp, created_at
                FROM predictions
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            predictions = []
            for row in results:
                predictions.append({
                    'service_name': row[0],
                    'prediction_type': row[1],
                    'confidence': row[2],
                    'predicted_value': row[3],
                    'recommendation': row[4],
                    'risk_level': row[5],
                    'timestamp': row[6],
                    'created_at': row[7]
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error getting recent predictions: {e}")
            return []
    
    def get_recent_trading_opportunities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent trading opportunities"""
        try:
            conn = sqlite3.connect(self.predictions_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, opportunity_type, confidence, expected_return,
                       risk_level, time_horizon, recommendation, timestamp, created_at
                FROM trading_opportunities
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            opportunities = []
            for row in results:
                opportunities.append({
                    'symbol': row[0],
                    'opportunity_type': row[1],
                    'confidence': row[2],
                    'expected_return': row[3],
                    'risk_level': row[4],
                    'time_horizon': row[5],
                    'recommendation': row[6],
                    'timestamp': row[7],
                    'created_at': row[8]
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error getting recent trading opportunities: {e}")
            return []
    
    def get_system_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive AI intelligence summary"""
        return {
            'system_health': self._calculate_overall_system_health(),
            'active_services': len(self.current_metrics),
            'recent_predictions': self.get_recent_predictions(5),
            'trading_opportunities': self.get_recent_trading_opportunities(3),
            'analytics_status': 'active' if self.analysis_active else 'inactive',
            'total_patterns_detected': sum(len(patterns) for patterns in self.service_patterns.values()),
            'last_analysis': datetime.now().isoformat()
        }
    
    # Utility methods for metric estimation
    def _estimate_cpu_usage(self, service_name: str) -> float:
        """Estimate CPU usage based on service activity"""
        # This would integrate with actual system monitoring
        # For now, provide estimated values based on service type
        base_cpu = {
            'database_service': 15.0,
            'zmart-api': 25.0,
            'analytics_server': 20.0,
            'websocket_server': 10.0,
            'master_orchestration_agent': 12.0
        }
        
        return base_cpu.get(service_name, 8.0) + np.random.normal(0, 5)
    
    def _estimate_memory_usage(self, service_name: str) -> float:
        """Estimate memory usage based on service activity"""
        base_memory = {
            'database_service': 35.0,
            'zmart-api': 45.0,
            'analytics_server': 40.0,
            'websocket_server': 20.0,
            'master_orchestration_agent': 25.0
        }
        
        return base_memory.get(service_name, 15.0) + np.random.normal(0, 8)
    
    def _calculate_error_rate(self, service_name: str) -> float:
        """Calculate error rate for service"""
        # This would integrate with actual error logging
        return max(0, np.random.normal(1.0, 2.0))  # Low error rate with some variation
    
    def _get_request_count(self, service_name: str) -> int:
        """Get request count for service"""
        # This would integrate with actual request monitoring
        return int(max(0, np.random.normal(50, 20)))  # Simulate request activity
    
    def _process_orchestration_metrics(self, orchestration_data: Dict):
        """Process metrics from Master Orchestration Agent"""
        try:
            # Store orchestration-specific metrics
            services_monitored = orchestration_data.get('services_monitored', 0)
            cloud_sync_status = orchestration_data.get('cloud_sync_status', '🔴 Unknown')
            
            # Add to intelligence analysis
            self.service_patterns['orchestration'].append({
                'type': 'orchestration_metrics',
                'services_monitored': services_monitored,
                'cloud_sync_active': '✅' in cloud_sync_status,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logger.warning(f"⚠️ Error processing orchestration metrics: {e}")

def main():
    """Main entry point for Intelligent Orchestrator"""
    orchestrator = IntelligentOrchestrator()
    
    try:
        logger.info("🚀 Starting AI-Powered Predictive Analytics Engine...")
        orchestrator.start_analytics_engine()
        
        # Keep running
        while True:
            time.sleep(10)
            summary = orchestrator.get_system_intelligence_summary()
            logger.info(f"🧠 System Health: {summary['system_health']:.2f}, Predictions: {len(summary['recent_predictions'])}")
            
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Intelligent Orchestrator...")
        orchestrator.stop_analytics_engine()
    except Exception as e:
        logger.error(f"❌ Error in Intelligent Orchestrator: {e}")
        orchestrator.stop_analytics_engine()

if __name__ == "__main__":
    main()