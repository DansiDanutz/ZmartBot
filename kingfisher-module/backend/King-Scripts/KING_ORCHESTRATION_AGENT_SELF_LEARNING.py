#!/usr/bin/env python3
"""
KING ORCHESTRATION AGENT - SELF-LEARNING EDITION
Intelligent orchestrator with machine learning capabilities for optimal automation
"""

import os
import sys
import time
import json
import pickle
import asyncio
import subprocess
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
import threading
import queue
from collections import defaultdict, deque
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import aiohttp
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import sqlite3
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
MD_REPORTS_DIR = DOWNLOADS_DIR / 'MD Reports'
HISTORY_DIR = BASE_DIR / 'HistoryData'
LEARNING_DIR = BASE_DIR / 'learning_data'
MODELS_DIR = LEARNING_DIR / 'models'
METRICS_DB = LEARNING_DIR / 'metrics.db'

# Ensure learning directories exist
LEARNING_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Step scripts
STEP_SCRIPTS = {
    1: "STEP1-Monitoring-Images-And-download.py",
    2: "STEP2-Sort-Images-With-AI.py",
    3: "STEP3-Remove-Duplicates.py",
    4: "STEP4-Analyze-And-Create-Reports.py",
    5: "STEP5-Extract-Liquidation-Clusters.py",
    6: "STEP6-Enhanced-Professional-Reports.py"
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KingOrchestratorML')


class StepStatus(Enum):
    """Status for each step execution"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    OPTIMIZED = "optimized"  # New status for ML-optimized execution


class TriggerType(Enum):
    """Trigger types for step execution"""
    NEW_IMAGE = "new_image"
    SORTED_IMAGES = "sorted_images"
    DUPLICATES_REMOVED = "duplicates_removed"
    REPORTS_CREATED = "reports_created"
    CLUSTERS_EXTRACTED = "clusters_extracted"
    TIMER = "timer"
    MANUAL = "manual"
    ML_PREDICTED = "ml_predicted"  # New trigger type for ML predictions


class LearningModule:
    """Machine learning module for pattern recognition and optimization"""
    
    def __init__(self):
        self.execution_patterns = defaultdict(list)
        self.performance_metrics = defaultdict(list)
        self.trigger_predictor = None
        self.anomaly_detector = None
        self.execution_optimizer = None
        self.pattern_clusters = None
        self.scaler = StandardScaler()
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2  # For exploration vs exploitation
        self.confidence_threshold = 0.75
        
        # Performance tracking
        self.success_rates = defaultdict(lambda: deque(maxlen=100))
        self.execution_times = defaultdict(lambda: deque(maxlen=100))
        self.resource_usage = defaultdict(lambda: deque(maxlen=100))
        
        # Pattern recognition
        self.time_patterns = defaultdict(list)  # Hour of day patterns
        self.sequence_patterns = []  # Common execution sequences
        self.failure_patterns = defaultdict(list)  # Common failure scenarios
        
        # Initialize database
        self._init_database()
        
        # Load existing models if available
        self._load_models()
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(METRICS_DB)
        cursor = conn.cursor()
        
        # Execution metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_num INTEGER,
                timestamp DATETIME,
                execution_time REAL,
                success BOOLEAN,
                trigger_type TEXT,
                file_count INTEGER,
                error_message TEXT,
                resource_usage REAL,
                confidence_score REAL
            )
        ''')
        
        # Pattern table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER,
                success_rate REAL,
                last_seen DATETIME
            )
        ''')
        
        # Optimization table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_type TEXT,
                parameters TEXT,
                improvement REAL,
                applied_at DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_execution(self, step_num: int, execution_time: float, 
                         success: bool, trigger_type: str, **kwargs):
        """Record execution metrics for learning"""
        conn = sqlite3.connect(METRICS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO execution_metrics 
            (step_num, timestamp, execution_time, success, trigger_type, 
             file_count, error_message, resource_usage, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            step_num,
            datetime.now(),
            execution_time,
            success,
            trigger_type,
            kwargs.get('file_count', 0),
            kwargs.get('error_message', ''),
            kwargs.get('resource_usage', 0),
            kwargs.get('confidence_score', 0)
        ))
        
        conn.commit()
        conn.close()
        
        # Update in-memory metrics
        self.success_rates[step_num].append(1 if success else 0)
        self.execution_times[step_num].append(execution_time)
        
        # Trigger learning if enough data
        if len(self.success_rates[step_num]) >= 10:
            self._update_models(step_num)
    
    def _update_models(self, step_num: int):
        """Update ML models based on recent data"""
        try:
            # Get recent metrics
            conn = sqlite3.connect(METRICS_DB)
            df = pd.read_sql_query(
                f"SELECT * FROM execution_metrics WHERE step_num = {step_num} "
                f"ORDER BY timestamp DESC LIMIT 100",
                conn
            )
            conn.close()
            
            if len(df) < 10:
                return
            
            # Feature engineering
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['time_since_last'] = pd.to_datetime(df['timestamp']).diff().dt.total_seconds()
            
            # Train execution time predictor
            features = ['hour', 'day_of_week', 'file_count']
            X = df[features].fillna(0)
            y = df['execution_time']
            
            if len(X) >= 20:
                self.execution_optimizer = RandomForestRegressor(n_estimators=50, random_state=42)
                self.execution_optimizer.fit(X, y)
                
                # Save model
                model_path = MODELS_DIR / f'step_{step_num}_optimizer.pkl'
                with open(model_path, 'wb') as f:
                    pickle.dump(self.execution_optimizer, f)
            
            # Train anomaly detector
            if len(X) >= 30:
                self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
                self.anomaly_detector.fit(X)
                
                # Save model
                model_path = MODELS_DIR / f'step_{step_num}_anomaly.pkl'
                with open(model_path, 'wb') as f:
                    pickle.dump(self.anomaly_detector, f)
            
            logger.info(f"Updated ML models for Step {step_num}")
            
        except Exception as e:
            logger.error(f"Error updating models: {e}")
    
    def predict_optimal_trigger_time(self, step_num: int) -> Optional[datetime]:
        """Predict the optimal time to trigger a step"""
        try:
            # Analyze historical patterns
            conn = sqlite3.connect(METRICS_DB)
            df = pd.read_sql_query(
                f"SELECT * FROM execution_metrics WHERE step_num = {step_num} "
                f"AND success = 1 ORDER BY timestamp DESC LIMIT 50",
                conn
            )
            conn.close()
            
            if len(df) < 10:
                return None
            
            # Find patterns in successful executions
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            
            # Find most successful hours
            success_by_hour = df.groupby('hour')['execution_time'].agg(['mean', 'count'])
            best_hours = success_by_hour.nsmallest(3, 'mean').index.tolist()
            
            # Get current hour
            current_hour = datetime.now().hour
            
            # Find next best hour
            for hour in sorted(best_hours):
                if hour > current_hour:
                    return datetime.now().replace(hour=hour, minute=0, second=0)
            
            # If no future hour today, use tomorrow's best hour
            if best_hours:
                tomorrow = datetime.now() + timedelta(days=1)
                return tomorrow.replace(hour=best_hours[0], minute=0, second=0)
            
        except Exception as e:
            logger.error(f"Error predicting trigger time: {e}")
        
        return None
    
    def detect_anomalies(self, step_num: int, current_metrics: Dict) -> bool:
        """Detect if current execution is anomalous"""
        try:
            model_path = MODELS_DIR / f'step_{step_num}_anomaly.pkl'
            
            if not model_path.exists():
                return False
            
            with open(model_path, 'rb') as f:
                detector = pickle.load(f)
            
            # Prepare features
            features = np.array([[
                current_metrics.get('hour', datetime.now().hour),
                current_metrics.get('day_of_week', datetime.now().weekday()),
                current_metrics.get('file_count', 0)
            ]])
            
            # Predict anomaly (-1 for anomaly, 1 for normal)
            prediction = detector.predict(features)
            
            return prediction[0] == -1
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return False
    
    def get_optimization_suggestions(self, step_num: int) -> Dict:
        """Get optimization suggestions based on learned patterns"""
        suggestions = {
            'optimal_trigger_time': None,
            'expected_execution_time': None,
            'confidence_score': 0,
            'recommendations': []
        }
        
        try:
            # Get optimal trigger time
            optimal_time = self.predict_optimal_trigger_time(step_num)
            if optimal_time:
                suggestions['optimal_trigger_time'] = optimal_time.isoformat()
            
            # Predict execution time
            if self.execution_optimizer:
                current_features = np.array([[
                    datetime.now().hour,
                    datetime.now().weekday(),
                    0  # Default file count
                ]])
                predicted_time = self.execution_optimizer.predict(current_features)[0]
                suggestions['expected_execution_time'] = round(predicted_time, 2)
            
            # Calculate confidence score
            if self.success_rates[step_num]:
                recent_success_rate = np.mean(list(self.success_rates[step_num]))
                suggestions['confidence_score'] = round(recent_success_rate * 100, 1)
            
            # Generate recommendations
            if suggestions['confidence_score'] < 70:
                suggestions['recommendations'].append(
                    "Low success rate detected. Consider reviewing error logs."
                )
            
            if self.execution_times[step_num]:
                avg_time = np.mean(list(self.execution_times[step_num]))
                if avg_time > 60:
                    suggestions['recommendations'].append(
                        f"Long execution time ({avg_time:.1f}s). Consider optimization."
                    )
            
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {e}")
        
        return suggestions
    
    def identify_patterns(self) -> List[Dict]:
        """Identify common execution patterns"""
        patterns = []
        
        try:
            conn = sqlite3.connect(METRICS_DB)
            
            # Pattern 1: Time-based patterns
            time_query = """
                SELECT strftime('%H', timestamp) as hour, 
                       COUNT(*) as count,
                       AVG(CASE WHEN success THEN 1 ELSE 0 END) as success_rate
                FROM execution_metrics
                GROUP BY hour
                HAVING count > 5
                ORDER BY success_rate DESC
            """
            time_patterns = pd.read_sql_query(time_query, conn)
            
            for _, row in time_patterns.iterrows():
                patterns.append({
                    'type': 'time_pattern',
                    'hour': int(row['hour']),
                    'frequency': int(row['count']),
                    'success_rate': round(row['success_rate'] * 100, 1)
                })
            
            # Pattern 2: Sequence patterns
            sequence_query = """
                SELECT step_num, 
                       LAG(step_num) OVER (ORDER BY timestamp) as prev_step,
                       COUNT(*) as count
                FROM execution_metrics
                GROUP BY step_num, prev_step
                HAVING count > 10
            """
            sequence_patterns = pd.read_sql_query(sequence_query, conn)
            
            for _, row in sequence_patterns.iterrows():
                if pd.notna(row['prev_step']):
                    patterns.append({
                        'type': 'sequence_pattern',
                        'sequence': f"Step {int(row['prev_step'])} -> Step {int(row['step_num'])}",
                        'frequency': int(row['count'])
                    })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
        
        return patterns
    
    def _load_models(self):
        """Load existing ML models"""
        try:
            for step_num in range(1, 7):
                # Load optimizer
                optimizer_path = MODELS_DIR / f'step_{step_num}_optimizer.pkl'
                if optimizer_path.exists():
                    with open(optimizer_path, 'rb') as f:
                        self.execution_optimizer = pickle.load(f)
                
                # Load anomaly detector
                anomaly_path = MODELS_DIR / f'step_{step_num}_anomaly.pkl'
                if anomaly_path.exists():
                    with open(anomaly_path, 'rb') as f:
                        self.anomaly_detector = pickle.load(f)
            
            logger.info("Loaded existing ML models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def adaptive_scheduling(self, step_num: int) -> float:
        """Calculate adaptive delay based on learned patterns"""
        base_delay = 10  # Base delay in seconds
        
        try:
            # Adjust based on success rate
            if self.success_rates[step_num]:
                success_rate = np.mean(list(self.success_rates[step_num]))
                if success_rate < 0.5:
                    # Low success rate, increase delay
                    base_delay *= 2
                elif success_rate > 0.9:
                    # High success rate, can decrease delay
                    base_delay *= 0.5
            
            # Adjust based on time patterns
            current_hour = datetime.now().hour
            if current_hour in [2, 3, 4, 5]:  # Low activity hours
                base_delay *= 3  # Check less frequently
            elif current_hour in [9, 10, 14, 15, 16]:  # High activity hours
                base_delay *= 0.7  # Check more frequently
            
            # Add some randomness for exploration
            if np.random.random() < self.exploration_rate:
                base_delay *= np.random.uniform(0.5, 1.5)
            
        except Exception as e:
            logger.error(f"Error in adaptive scheduling: {e}")
        
        return max(5, min(base_delay, 60))  # Keep between 5 and 60 seconds


class SelfLearningKingOrchestrator:
    """Self-learning orchestration agent with ML capabilities"""
    
    def __init__(self):
        self.step_status = {i: StepStatus.IDLE for i in range(1, 7)}
        self.last_execution = {i: None for i in range(1, 7)}
        self.execution_history = []
        self.is_running = False
        self.event_queue = queue.Queue()
        self.observer = None
        self.api_app = None
        self.api_thread = None
        
        # Initialize learning module
        self.learning_module = LearningModule()
        
        # Performance tracking
        self.performance_scores = defaultdict(float)
        self.optimization_enabled = True
        
        # Ensure all directories exist
        self._create_directories()
        
        # Initialize step dependencies
        self.step_dependencies = {
            1: [],
            2: [1],
            3: [2],
            4: [3],
            5: [4],
            6: [5],
        }
        
        # Step trigger conditions with ML enhancement
        self.step_triggers = {
            1: self._check_step1_trigger_ml,
            2: self._check_step2_trigger_ml,
            3: self._check_step3_trigger_ml,
            4: self._check_step4_trigger_ml,
            5: self._check_step5_trigger_ml,
            6: self._check_step6_trigger_ml,
        }
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            DOWNLOADS_DIR,
            MD_REPORTS_DIR,
            HISTORY_DIR,
            LEARNING_DIR,
            MODELS_DIR,
            DOWNLOADS_DIR / 'LiquidationMap',
            DOWNLOADS_DIR / 'LiquidationHeatmap',
            DOWNLOADS_DIR / 'ShortTermRatio',
            DOWNLOADS_DIR / 'LongTermRatio',
        ]
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _check_step1_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 1"""
        # Get ML suggestions
        suggestions = self.learning_module.get_optimization_suggestions(1)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        # Check basic conditions
        download_files = list(DOWNLOADS_DIR.glob('*.jpg')) + list(DOWNLOADS_DIR.glob('*.png'))
        
        # Apply ML optimization
        if self.optimization_enabled and confidence > 0.7:
            # Use ML prediction
            optimal_time = suggestions.get('optimal_trigger_time')
            if optimal_time:
                optimal_dt = datetime.fromisoformat(optimal_time)
                if datetime.now() >= optimal_dt:
                    return True, confidence
        
        # Fallback to traditional logic
        if len(download_files) == 0:
            return True, 1.0
        
        if self.last_execution[1]:
            # Adaptive timing based on learning
            adaptive_delay = self.learning_module.adaptive_scheduling(1)
            time_diff = (datetime.now() - self.last_execution[1]).total_seconds()
            if time_diff > adaptive_delay * 30:  # multiply by 30 for minutes
                return True, 0.8
        
        return False, 0.0
    
    def _check_step2_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 2"""
        suggestions = self.learning_module.get_optimization_suggestions(2)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        # Check for unsorted images
        unsorted_images = []
        for img in DOWNLOADS_DIR.glob('*.jpg'):
            if not any(img.name in str(f) for f in 
                      (DOWNLOADS_DIR / 'LiquidationMap').glob('*.jpg')):
                unsorted_images.append(img)
        
        if len(unsorted_images) > 0:
            # Check for anomalies
            is_anomaly = self.learning_module.detect_anomalies(2, {
                'file_count': len(unsorted_images)
            })
            
            if is_anomaly:
                logger.warning(f"Anomaly detected for Step 2 with {len(unsorted_images)} files")
                confidence *= 0.7  # Reduce confidence for anomalies
            
            return True, confidence
        
        return False, 0.0
    
    def _check_step3_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 3"""
        suggestions = self.learning_module.get_optimization_suggestions(3)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        folders = ['LiquidationMap', 'LiquidationHeatmap', 'ShortTermRatio', 'LongTermRatio']
        
        total_images = 0
        for folder in folders:
            folder_path = DOWNLOADS_DIR / folder
            if folder_path.exists():
                images = list(folder_path.glob('*.jpg'))
                total_images += len(images)
                if len(images) > 1:
                    return True, confidence
        
        # Learn from patterns
        if total_images > 0:
            self.learning_module.record_execution(
                3, 0, False, 'check_only',
                file_count=total_images
            )
        
        return False, 0.0
    
    def _check_step4_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 4"""
        suggestions = self.learning_module.get_optimization_suggestions(4)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        folders = ['LiquidationMap', 'LiquidationHeatmap']
        unanalyzed_count = 0
        
        for folder in folders:
            folder_path = DOWNLOADS_DIR / folder
            if folder_path.exists():
                images = list(folder_path.glob('*.jpg'))
                for img in images:
                    analyzed_path = IMAGES_ANALYSED_DIR / img.name
                    if not analyzed_path.exists():
                        unanalyzed_count += 1
        
        if unanalyzed_count > 0:
            # Batch optimization
            if unanalyzed_count > 5 and confidence > 0.8:
                logger.info(f"ML suggests batch processing {unanalyzed_count} images")
            return True, confidence
        
        return False, 0.0
    
    def _check_step5_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 5"""
        suggestions = self.learning_module.get_optimization_suggestions(5)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        md_files = list(MDFILES_DIR.glob('*.md'))
        unprocessed_count = 0
        
        for md_file in md_files:
            history_file = HISTORY_DIR / md_file.name
            if not history_file.exists():
                unprocessed_count += 1
        
        if unprocessed_count > 0:
            return True, confidence
        
        return False, 0.0
    
    def _check_step6_trigger_ml(self) -> Tuple[bool, float]:
        """ML-enhanced trigger check for Step 6"""
        suggestions = self.learning_module.get_optimization_suggestions(6)
        confidence = suggestions['confidence_score'] / 100.0 if suggestions['confidence_score'] else 0.5
        
        if self.last_execution[6]:
            # Use adaptive scheduling
            adaptive_delay = self.learning_module.adaptive_scheduling(6)
            time_diff = (datetime.now() - self.last_execution[6]).total_seconds()
            
            # ML-optimized timing
            if suggestions.get('optimal_trigger_time'):
                optimal_dt = datetime.fromisoformat(suggestions['optimal_trigger_time'])
                if datetime.now() >= optimal_dt:
                    return True, confidence
            
            if time_diff > adaptive_delay * 180:  # multiply by 180 for 30-minute base
                return True, confidence
        else:
            return True, 0.5
        
        return False, 0.0
    
    async def execute_step(self, step_num: int, confidence: float = 1.0) -> bool:
        """Execute a step with ML tracking"""
        if step_num not in STEP_SCRIPTS:
            logger.error(f"Invalid step number: {step_num}")
            return False
        
        # Check dependencies
        for dep in self.step_dependencies[step_num]:
            if self.step_status[dep] not in [StepStatus.COMPLETED, StepStatus.IDLE]:
                logger.warning(f"Step {step_num} waiting for dependency: Step {dep}")
                return False
        
        # Update status
        self.step_status[step_num] = StepStatus.RUNNING
        script_name = STEP_SCRIPTS[step_num]
        script_path = BASE_DIR / script_name
        
        logger.info(f"Executing Step {step_num}: {script_name} (Confidence: {confidence:.1%})")
        
        # Track execution start
        start_time = time.time()
        
        try:
            # Execute the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            if success:
                self.step_status[step_num] = StepStatus.COMPLETED
                self.last_execution[step_num] = datetime.now()
                logger.info(f"Step {step_num} completed in {execution_time:.2f}s")
                
                # Update performance score
                self.performance_scores[step_num] = (
                    self.performance_scores[step_num] * 0.9 + 1.0 * 0.1
                )
            else:
                self.step_status[step_num] = StepStatus.FAILED
                logger.error(f"Step {step_num} failed: {result.stderr}")
                
                # Update performance score
                self.performance_scores[step_num] = (
                    self.performance_scores[step_num] * 0.9 + 0.0 * 0.1
                )
            
            # Record execution for learning
            self.learning_module.record_execution(
                step_num,
                execution_time,
                success,
                'ml_triggered' if confidence > 0.7 else 'standard',
                error_message=result.stderr if not success else '',
                confidence_score=confidence
            )
            
            # Record in history
            self.execution_history.append({
                'step': step_num,
                'status': 'success' if success else 'failed',
                'timestamp': datetime.now().isoformat(),
                'execution_time': execution_time,
                'confidence': confidence
            })
            
            # Trigger next step if applicable
            if success:
                self._trigger_next_step(step_num)
            
            return success
                
        except subprocess.TimeoutExpired:
            self.step_status[step_num] = StepStatus.FAILED
            execution_time = time.time() - start_time
            logger.error(f"Step {step_num} timed out after {execution_time:.2f}s")
            
            # Record timeout
            self.learning_module.record_execution(
                step_num,
                execution_time,
                False,
                'timeout',
                error_message='Execution timeout'
            )
            
            return False
            
        except Exception as e:
            self.step_status[step_num] = StepStatus.FAILED
            execution_time = time.time() - start_time
            logger.error(f"Step {step_num} error: {e}")
            
            # Record error
            self.learning_module.record_execution(
                step_num,
                execution_time,
                False,
                'error',
                error_message=str(e)
            )
            
            return False
    
    def _trigger_next_step(self, completed_step: int):
        """Trigger next step with ML optimization"""
        next_step = completed_step + 1
        if next_step <= 6:
            # Check if next step should be triggered
            should_trigger, confidence = self.step_triggers[next_step]()
            if should_trigger:
                self.trigger_step(next_step, TriggerType.ML_PREDICTED, confidence)
    
    def trigger_step(self, step_num: int, trigger_type: TriggerType, confidence: float = 1.0):
        """Add step execution to queue with confidence"""
        self.event_queue.put({
            'step': step_num,
            'trigger': trigger_type,
            'timestamp': datetime.now(),
            'confidence': confidence
        })
    
    async def monitor_triggers(self):
        """Monitor triggers with ML optimization"""
        while self.is_running:
            try:
                # Adaptive monitoring interval
                base_interval = 10
                
                # Check each step's trigger conditions
                for step_num in range(1, 7):
                    if self.step_status[step_num] == StepStatus.IDLE:
                        should_trigger, confidence = self.step_triggers[step_num]()
                        if should_trigger:
                            logger.info(
                                f"ML Trigger detected for Step {step_num} "
                                f"(Confidence: {confidence:.1%})"
                            )
                            self.trigger_step(step_num, TriggerType.ML_PREDICTED, confidence)
                
                # Process event queue
                while not self.event_queue.empty():
                    event = self.event_queue.get()
                    await self.execute_step(
                        event['step'],
                        event.get('confidence', 1.0)
                    )
                
                # Adaptive interval based on overall performance
                avg_performance = np.mean(list(self.performance_scores.values())) if self.performance_scores else 0.5
                if avg_performance > 0.8:
                    base_interval = 8  # Check more frequently when performing well
                elif avg_performance < 0.5:
                    base_interval = 15  # Check less frequently when struggling
                
                # Wait before next check
                await asyncio.sleep(base_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
    
    def create_api(self):
        """Create Flask API with ML endpoints"""
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'service': 'King Orchestration Agent (Self-Learning)',
                'timestamp': datetime.now().isoformat(),
                'ml_enabled': self.optimization_enabled
            })
        
        @app.route('/status', methods=['GET'])
        def get_status():
            """Get current status with ML metrics"""
            status = {}
            for step_num in range(1, 7):
                suggestions = self.learning_module.get_optimization_suggestions(step_num)
                status[f'step_{step_num}'] = {
                    'status': self.step_status[step_num].value,
                    'last_execution': self.last_execution[step_num].isoformat() 
                                     if self.last_execution[step_num] else None,
                    'script': STEP_SCRIPTS[step_num],
                    'performance_score': round(self.performance_scores.get(step_num, 0), 2),
                    'ml_confidence': suggestions['confidence_score'],
                    'expected_time': suggestions['expected_execution_time']
                }
            
            return jsonify({
                'steps': status,
                'is_running': self.is_running,
                'history_count': len(self.execution_history),
                'ml_optimization': self.optimization_enabled
            })
        
        @app.route('/ml/patterns', methods=['GET'])
        def get_patterns():
            """Get identified patterns"""
            patterns = self.learning_module.identify_patterns()
            return jsonify({'patterns': patterns})
        
        @app.route('/ml/suggestions/<int:step_num>', methods=['GET'])
        def get_suggestions(step_num):
            """Get ML suggestions for a step"""
            suggestions = self.learning_module.get_optimization_suggestions(step_num)
            return jsonify(suggestions)
        
        @app.route('/ml/metrics', methods=['GET'])
        def get_metrics():
            """Get learning metrics"""
            metrics = {
                'total_executions': len(self.execution_history),
                'success_rates': {},
                'average_times': {},
                'performance_scores': dict(self.performance_scores)
            }
            
            for step_num in range(1, 7):
                if self.learning_module.success_rates[step_num]:
                    metrics['success_rates'][f'step_{step_num}'] = round(
                        np.mean(list(self.learning_module.success_rates[step_num])) * 100, 1
                    )
                if self.learning_module.execution_times[step_num]:
                    metrics['average_times'][f'step_{step_num}'] = round(
                        np.mean(list(self.learning_module.execution_times[step_num])), 2
                    )
            
            return jsonify(metrics)
        
        @app.route('/ml/toggle', methods=['POST'])
        def toggle_ml():
            """Toggle ML optimization"""
            self.optimization_enabled = not self.optimization_enabled
            return jsonify({
                'ml_optimization': self.optimization_enabled,
                'message': f"ML optimization {'enabled' if self.optimization_enabled else 'disabled'}"
            })
        
        @app.route('/trigger/<int:step_num>', methods=['POST'])
        def trigger_step_api(step_num):
            """Manually trigger a step"""
            if step_num not in STEP_SCRIPTS:
                return jsonify({'error': 'Invalid step number'}), 400
            
            self.trigger_step(step_num, TriggerType.MANUAL, 1.0)
            return jsonify({
                'message': f'Step {step_num} triggered',
                'step': STEP_SCRIPTS[step_num]
            })
        
        @app.route('/data/<symbol>', methods=['GET'])
        def get_symbol_data(symbol):
            """Get latest data for a symbol"""
            return asyncio.run(self._fetch_symbol_data(symbol))
        
        @app.route('/reports/<symbol>', methods=['GET'])
        def get_symbol_reports(symbol):
            """Get latest report for a symbol"""
            today = datetime.now().strftime("%Y-%m-%d")
            report_dir = MD_REPORTS_DIR / today
            
            if report_dir.exists():
                reports = list(report_dir.glob(f'report_{symbol}_*.md'))
                if reports:
                    latest_report = max(reports, key=lambda x: x.stat().st_mtime)
                    with open(latest_report, 'r') as f:
                        content = f.read()
                    
                    return jsonify({
                        'symbol': symbol,
                        'report': content,
                        'file': latest_report.name,
                        'timestamp': datetime.fromtimestamp(
                            latest_report.stat().st_mtime
                        ).isoformat()
                    })
            
            return jsonify({'error': 'No report found'}), 404
        
        @app.route('/history', methods=['GET'])
        def get_history():
            """Get execution history"""
            return jsonify({
                'history': self.execution_history[-100:],
                'total': len(self.execution_history)
            })
        
        self.api_app = app
        return app
    
    async def _fetch_symbol_data(self, symbol: str):
        """Fetch symbol data from Airtable"""
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        params = {
            "filterByFormula": f"{{Symbol}} = '{symbol}'",
            "maxRecords": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['records']:
                            return jsonify(data['records'][0]['fields'])
                    return jsonify({'error': 'Symbol not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start_api_server(self):
        """Start the Flask API server"""
        app = self.create_api()
        
        def run_server():
            app.run(host='0.0.0.0', port=5555, debug=False)
        
        self.api_thread = threading.Thread(target=run_server, daemon=True)
        self.api_thread.start()
        logger.info("API server started on port 5555 with ML endpoints")
    
    async def start(self):
        """Start the self-learning orchestrator"""
        logger.info("Starting Self-Learning King Orchestration Agent...")
        self.is_running = True
        
        # Start API server
        self.start_api_server()
        
        # Check initial state
        logger.info("Analyzing initial state with ML...")
        download_files = list(DOWNLOADS_DIR.glob('*.jpg'))
        
        if len(download_files) == 0:
            logger.info("Downloads folder empty - ML system learning optimal patterns...")
        else:
            logger.info(f"Found {len(download_files)} images - ML analyzing best approach...")
            # Trigger Step 2 with ML confidence
            _, confidence = self._check_step2_trigger_ml()
            if confidence > 0.5:
                self.trigger_step(2, TriggerType.ML_PREDICTED, confidence)
        
        # Start monitoring loop
        try:
            await self.monitor_triggers()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        self.is_running = False
        logger.info("Self-Learning King Orchestration Agent stopped")
        logger.info(f"Total executions: {len(self.execution_history)}")
        logger.info(f"Average performance: {np.mean(list(self.performance_scores.values())):.2%}")


async def main():
    """Main entry point"""
    orchestrator = SelfLearningKingOrchestrator()
    
    print("\n" + "="*60)
    print(" 🧠 SELF-LEARNING KING ORCHESTRATION AGENT")
    print("="*60)
    print("\n✨ Enhanced Features:")
    print("  ✅ Machine Learning optimization")
    print("  ✅ Pattern recognition and prediction")
    print("  ✅ Adaptive scheduling based on performance")
    print("  ✅ Anomaly detection for unusual conditions")
    print("  ✅ Performance tracking and improvement")
    print("  ✅ Confidence-based execution")
    print("\n📊 ML Capabilities:")
    print("  • Learns optimal trigger times")
    print("  • Predicts execution duration")
    print("  • Identifies success patterns")
    print("  • Adapts to system behavior")
    print("  • Improves over time")
    print("\n🌐 API Endpoints (http://localhost:5555):")
    print("  GET  /health              - Health check")
    print("  GET  /status              - Step status with ML metrics")
    print("  GET  /ml/patterns         - View learned patterns")
    print("  GET  /ml/suggestions/<n>  - Get ML suggestions for step")
    print("  GET  /ml/metrics          - View learning metrics")
    print("  POST /ml/toggle           - Toggle ML optimization")
    print("  POST /trigger/<step>      - Manual trigger")
    print("  GET  /data/<symbol>       - Symbol data")
    print("  GET  /reports/<symbol>    - Symbol reports")
    print("\n🎯 The system will learn and improve with each execution!")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())