#!/usr/bin/env python3
"""
ServiceLog - Intelligent Log Analysis & Advice System for ZmartBot
Provides real-time log analysis, pattern detection, and prioritized advice generation
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import redis
import schedule
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Represents a log entry from a service"""
    service_name: str
    timestamp: datetime
    level: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self):
        return {
            'service_name': self.service_name,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'context': self.context,
            'metadata': self.metadata
        }

@dataclass 
class ServiceInfo:
    """Information about a registered service"""
    service_name: str
    service_type: str
    port: int
    criticality_level: str
    log_sources: List[str]
    health_endpoints: List[str]
    expected_patterns: List[str]
    alert_contacts: List[str]
    registration_time: datetime
    last_heartbeat: Optional[datetime] = None
    status: str = 'ACTIVE'

@dataclass
class Advice:
    """Represents generated advice for an issue"""
    advice_id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # ERROR, PERFORMANCE, SECURITY, COMPLIANCE
    affected_services: List[str]
    detection_time: datetime
    evidence: List[Dict]
    root_cause_analysis: str
    impact_assessment: Dict[str, str]
    resolution_steps: List[str]
    prevention_measures: str
    automated_remediation: Dict[str, Any]
    monitoring_recommendations: List[str]
    mdc_reference: str
    priority_score: float
    estimated_resolution_time: timedelta
    escalation_path: List[Dict]
    status: str = 'OPEN'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class LogAgent:
    """Base class for specialized log analysis agents"""
    
    def __init__(self, agent_type: str, config: Dict[str, Any]):
        self.agent_type = agent_type
        self.config = config
        self.pattern_cache = {}
        self.detection_history = deque(maxlen=1000)
        
    def analyze_logs(self, logs: List[LogEntry]) -> List[Advice]:
        """Analyze logs and generate advice. Override in subclasses."""
        raise NotImplementedError
        
    def calculate_confidence(self, pattern_matches: int, total_logs: int) -> float:
        """Calculate confidence score for pattern detection"""
        if total_logs == 0:
            return 0.0
        match_ratio = pattern_matches / total_logs
        return min(1.0, match_ratio * 2)  # Scale to 0-1 range

class ErrorLogAgent(LogAgent):
    """Specialized agent for error pattern detection"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("error_agent", config)
        self.error_patterns = [
            r"connection\s+(failed|refused|timeout)",
            r"database\s+(error|exception|timeout)",
            r"out\s+of\s+memory",
            r"stack\s+overflow",
            r"null\s+pointer",
            r"authentication\s+(failed|denied)",
            r"permission\s+denied",
            r"file\s+not\s+found",
            r"network\s+(unreachable|timeout)",
            r"ssl\s+(error|handshake\s+failed)"
        ]
        
    def analyze_logs(self, logs: List[LogEntry]) -> List[Advice]:
        advice_list = []
        error_logs = [log for log in logs if log.level in ['ERROR', 'CRITICAL', 'FATAL']]
        
        if not error_logs:
            return advice_list
            
        # Group errors by service and pattern
        error_groups = defaultdict(list)
        for log in error_logs:
            for pattern in self.error_patterns:
                import re
                if re.search(pattern, log.message, re.IGNORECASE):
                    key = f"{log.service_name}:{pattern}"
                    error_groups[key].append(log)
                    break
                    
        # Generate advice for significant error patterns
        for pattern_key, pattern_logs in error_groups.items():
            if len(pattern_logs) >= self.config.get('pattern_threshold', 5):
                service_name, pattern = pattern_key.split(':', 1)
                advice = self._create_error_advice(service_name, pattern, pattern_logs)
                if advice:
                    advice_list.append(advice)
                    
        return advice_list
        
    def _create_error_advice(self, service_name: str, pattern: str, logs: List[LogEntry]) -> Optional[Advice]:
        """Create advice for detected error pattern"""
        if not logs:
            return None
            
        advice_id = f"LogAdvice{int(time.time())}"
        severity = self._determine_severity(len(logs), pattern)
        confidence = self.calculate_confidence(len(logs), 100)
        
        if confidence < self.config.get('confidence_threshold', 0.7):
            return None
            
        return Advice(
            advice_id=advice_id,
            title=f"Error Pattern Detected: {pattern} in {service_name}",
            severity=severity,
            category="ERROR",
            affected_services=[service_name],
            detection_time=logs[0].timestamp,
            evidence=[log.to_dict() for log in logs[:5]],  # First 5 as evidence
            root_cause_analysis=f"Repeated {pattern} errors detected in {service_name}. "
                              f"Pattern occurred {len(logs)} times in recent analysis window.",
            impact_assessment={
                "service_impact": f"{service_name} experiencing error rate of {len(logs)} errors",
                "user_impact": "Potential service degradation or failures",
                "business_impact": "Service reliability affected"
            },
            resolution_steps=[
                f"1. Investigate {service_name} service logs for detailed error context",
                "2. Check service health endpoints and dependencies",
                "3. Review recent deployments or configuration changes",
                "4. Apply appropriate fixes based on error type",
                "5. Monitor for resolution and pattern recurrence"
            ],
            prevention_measures=f"Implement monitoring for {pattern} pattern, add circuit breakers, improve error handling",
            automated_remediation={
                "available": True,
                "script": "auto_fix_common_errors.sh",
                "approval_required": severity in ['CRITICAL', 'HIGH']
            },
            monitoring_recommendations=[
                f"Monitor {pattern} error frequency",
                f"Track {service_name} service health metrics",
                "Set up alerts for error rate thresholds"
            ],
            mdc_reference="LogAdvice001.mdc",
            priority_score=self._calculate_priority(severity, len(logs), confidence),
            estimated_resolution_time=timedelta(minutes=30),
            escalation_path=[
                {"level": 1, "contact": "ops-team@zmartbot.com", "threshold": "5 minutes"},
                {"level": 2, "contact": "backend-team@zmartbot.com", "threshold": "15 minutes"},
                {"level": 3, "contact": "eng-manager@zmartbot.com", "threshold": "30 minutes"}
            ],
            created_at=datetime.now()
        )
        
    def _determine_severity(self, error_count: int, pattern: str) -> str:
        """Determine severity based on error count and pattern type"""
        critical_patterns = ['out of memory', 'database error', 'authentication failed']
        
        if any(cp in pattern.lower() for cp in critical_patterns):
            if error_count >= 20:
                return 'CRITICAL'
            elif error_count >= 10:
                return 'HIGH'
            else:
                return 'MEDIUM'
        else:
            if error_count >= 50:
                return 'HIGH'
            elif error_count >= 20:
                return 'MEDIUM'
            else:
                return 'LOW'
                
    def _calculate_priority(self, severity: str, error_count: int, confidence: float) -> float:
        """Calculate priority score for advice"""
        severity_weights = {'CRITICAL': 40, 'HIGH': 30, 'MEDIUM': 20, 'LOW': 10}
        base_score = severity_weights.get(severity, 0)
        
        # Add frequency bonus
        frequency_bonus = min(30, error_count * 0.5)
        base_score += frequency_bonus
        
        # Apply confidence multiplier
        base_score *= confidence
        
        return min(100.0, base_score)

class PerformanceLogAgent(LogAgent):
    """Specialized agent for performance issue detection"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("performance_agent", config)
        self.response_time_threshold = config.get('response_time_threshold', 5000)
        self.cpu_threshold = config.get('cpu_threshold', 80)
        self.memory_threshold = config.get('memory_threshold', 85)
        
    def analyze_logs(self, logs: List[LogEntry]) -> List[Advice]:
        advice_list = []
        
        # Analyze response times
        slow_responses = self._find_slow_responses(logs)
        if slow_responses:
            advice = self._create_performance_advice("slow_response", slow_responses)
            if advice:
                advice_list.append(advice)
                
        # Analyze resource usage
        high_resource_logs = self._find_high_resource_usage(logs)
        if high_resource_logs:
            advice = self._create_performance_advice("high_resource", high_resource_logs)
            if advice:
                advice_list.append(advice)
                
        return advice_list
        
    def _find_slow_responses(self, logs: List[LogEntry]) -> List[LogEntry]:
        """Find logs indicating slow response times"""
        slow_logs = []
        for log in logs:
            if 'duration_ms' in log.context:
                duration = log.context.get('duration_ms', 0)
                if duration > self.response_time_threshold:
                    slow_logs.append(log)
                    
        return slow_logs
        
    def _find_high_resource_usage(self, logs: List[LogEntry]) -> List[LogEntry]:
        """Find logs indicating high resource usage"""
        resource_logs = []
        keywords = ['cpu', 'memory', 'disk', 'high usage', 'resource']
        
        for log in logs:
            if any(keyword in log.message.lower() for keyword in keywords):
                if log.level in ['WARN', 'ERROR']:
                    resource_logs.append(log)
                    
        return resource_logs
        
    def _create_performance_advice(self, issue_type: str, logs: List[LogEntry]) -> Optional[Advice]:
        """Create performance-related advice"""
        if not logs:
            return None
            
        service_names = list(set(log.service_name for log in logs))
        advice_id = f"LogAdvice{int(time.time())}P"
        
        if issue_type == "slow_response":
            title = f"Slow Response Times Detected: {', '.join(service_names)}"
            avg_duration = sum(log.context.get('duration_ms', 0) for log in logs) / len(logs)
            analysis = f"Average response time {avg_duration:.0f}ms exceeds threshold of {self.response_time_threshold}ms"
        else:
            title = f"High Resource Usage: {', '.join(service_names)}"
            analysis = f"Resource usage warnings detected across {len(service_names)} services"
            
        return Advice(
            advice_id=advice_id,
            title=title,
            severity="MEDIUM" if len(logs) < 20 else "HIGH",
            category="PERFORMANCE",
            affected_services=service_names,
            detection_time=logs[0].timestamp,
            evidence=[log.to_dict() for log in logs[:3]],
            root_cause_analysis=analysis,
            impact_assessment={
                "service_impact": "Degraded service performance",
                "user_impact": "Slower response times, potential timeouts",
                "business_impact": "Reduced user satisfaction, potential SLA breach"
            },
            resolution_steps=[
                "1. Analyze service resource utilization",
                "2. Identify performance bottlenecks",
                "3. Optimize queries or algorithms causing delays",
                "4. Consider scaling resources if needed",
                "5. Implement performance monitoring"
            ],
            prevention_measures="Regular performance testing, resource monitoring, capacity planning",
            automated_remediation={
                "available": False,
                "reason": "Performance issues require manual analysis"
            },
            monitoring_recommendations=[
                "Monitor response time percentiles",
                "Track resource utilization trends",
                "Set up performance alerts"
            ],
            mdc_reference="LogAdvice001.mdc",
            priority_score=self._calculate_priority("MEDIUM", len(logs), 0.8),
            estimated_resolution_time=timedelta(hours=2),
            escalation_path=[
                {"level": 1, "contact": "performance-team@zmartbot.com", "threshold": "30 minutes"},
                {"level": 2, "contact": "backend-team@zmartbot.com", "threshold": "2 hours"}
            ],
            created_at=datetime.now()
        )
        
    def _calculate_priority(self, severity: str, issue_count: int, confidence: float) -> float:
        """Calculate priority score for performance advice"""
        severity_weights = {'CRITICAL': 35, 'HIGH': 25, 'MEDIUM': 15, 'LOW': 8}
        base_score = severity_weights.get(severity, 0)
        base_score += min(20, issue_count * 0.3)
        return min(100.0, base_score * confidence)

class LogAgentManager:
    """Manages multiple specialized log analysis agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all configured agents"""
        agent_configs = self.config.get('log_agents', {})
        
        if agent_configs.get('error_agent', {}).get('enabled', True):
            self.agents['error'] = ErrorLogAgent(agent_configs.get('error_agent', {}))
            
        if agent_configs.get('performance_agent', {}).get('enabled', True):
            self.agents['performance'] = PerformanceLogAgent(agent_configs.get('performance_agent', {}))
            
        logger.info(f"Initialized {len(self.agents)} log analysis agents: {list(self.agents.keys())}")
        
    def analyze_logs(self, logs: List[LogEntry]) -> List[Advice]:
        """Run all agents on the logs and collect advice"""
        all_advice = []
        
        for agent_name, agent in self.agents.items():
            try:
                agent_advice = agent.analyze_logs(logs)
                all_advice.extend(agent_advice)
                logger.debug(f"Agent {agent_name} generated {len(agent_advice)} advice items")
            except Exception as e:
                logger.error(f"Error running agent {agent_name}: {e}")
                
        # Sort by priority score
        all_advice.sort(key=lambda x: x.priority_score, reverse=True)
        return all_advice

class ServiceLogDatabase:
    """Database operations for ServiceLog"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Services table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_name TEXT PRIMARY KEY,
                service_type TEXT NOT NULL,
                port INTEGER NOT NULL,
                criticality_level TEXT DEFAULT 'MEDIUM',
                log_sources TEXT,
                health_endpoints TEXT,
                expected_patterns TEXT,
                alert_contacts TEXT,
                registration_time TEXT NOT NULL,
                last_heartbeat TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        ''')
        
        # Log entries table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                context TEXT,
                metadata TEXT,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Advice queue table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS advice_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                advice_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                affected_services TEXT,
                detection_time TEXT NOT NULL,
                evidence TEXT,
                root_cause_analysis TEXT,
                impact_assessment TEXT,
                resolution_steps TEXT,
                prevention_measures TEXT,
                automated_remediation TEXT,
                monitoring_recommendations TEXT,
                mdc_reference TEXT,
                priority_score REAL NOT NULL,
                estimated_resolution_time TEXT,
                escalation_path TEXT,
                status TEXT DEFAULT 'OPEN',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT
            )
        ''')
        
        # Create indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_service_time ON log_entries(service_name, timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_advice_priority ON advice_queue(priority_score DESC)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_advice_status ON advice_queue(status)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def register_service(self, service: ServiceInfo) -> bool:
        """Register a new service"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT OR REPLACE INTO services 
                (service_name, service_type, port, criticality_level, log_sources, 
                 health_endpoints, expected_patterns, alert_contacts, registration_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service.service_name, service.service_type, service.port, 
                service.criticality_level, json.dumps(service.log_sources),
                json.dumps(service.health_endpoints), json.dumps(service.expected_patterns),
                json.dumps(service.alert_contacts), service.registration_time.isoformat(),
                service.status
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to register service {service.service_name}: {e}")
            return False
            
    def store_logs(self, logs: List[LogEntry]) -> bool:
        """Store log entries in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            for log in logs:
                conn.execute('''
                    INSERT INTO log_entries 
                    (service_name, timestamp, level, message, context, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    log.service_name, log.timestamp.isoformat(), log.level,
                    log.message, json.dumps(log.context), json.dumps(log.metadata)
                ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to store logs: {e}")
            return False
            
    def store_advice(self, advice: Advice) -> bool:
        """Store advice in queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT OR REPLACE INTO advice_queue
                (advice_id, title, severity, category, affected_services, detection_time,
                 evidence, root_cause_analysis, impact_assessment, resolution_steps,
                 prevention_measures, automated_remediation, monitoring_recommendations,
                 mdc_reference, priority_score, estimated_resolution_time, escalation_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                advice.advice_id, advice.title, advice.severity, advice.category,
                json.dumps(advice.affected_services), advice.detection_time.isoformat(),
                json.dumps(advice.evidence), advice.root_cause_analysis,
                json.dumps(advice.impact_assessment), json.dumps(advice.resolution_steps),
                advice.prevention_measures, json.dumps(advice.automated_remediation),
                json.dumps(advice.monitoring_recommendations), advice.mdc_reference,
                advice.priority_score, str(advice.estimated_resolution_time),
                json.dumps(advice.escalation_path), advice.status
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to store advice {advice.advice_id}: {e}")
            return False
            
    def get_priority_advice(self, limit: int = 10, status: str = 'OPEN') -> List[Dict]:
        """Get prioritized advice from queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM advice_queue 
                WHERE status = ? 
                ORDER BY priority_score DESC 
                LIMIT ?
            ''', (status, limit))
            
            advice_list = []
            for row in cursor.fetchall():
                advice_dict = dict(row)
                # Parse JSON fields
                for json_field in ['affected_services', 'evidence', 'impact_assessment', 
                                 'resolution_steps', 'automated_remediation', 
                                 'monitoring_recommendations', 'escalation_path']:
                    if advice_dict[json_field]:
                        advice_dict[json_field] = json.loads(advice_dict[json_field])
                advice_list.append(advice_dict)
                
            conn.close()
            return advice_list
        except Exception as e:
            logger.error(f"Failed to get priority advice: {e}")
            return []

class ServiceLog:
    """Main ServiceLog orchestrator"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.db = ServiceLogDatabase(self.config.get('database', {}).get('path', 'servicelog.db'))
        self.agent_manager = LogAgentManager(self.config)
        self.log_buffer = deque(maxlen=10000)
        self.advice_cache = {}
        self.redis_client = self._init_redis()
        
        # Flask app for REST API
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self._setup_routes()
        
        # Background processing
        self.processing_thread = None
        self.running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
            
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'core': {'port': 8750, 'log_level': 'INFO'},
            'log_agents': {
                'error_agent': {'enabled': True, 'pattern_threshold': 5},
                'performance_agent': {'enabled': True, 'response_time_threshold': 5000}
            },
            'advice_queue': {'max_size': 1000, 'retention_days': 90}
        }
        
    def _init_redis(self) -> Optional[Any]:
        """Initialize Redis connection"""
        try:
            import redis
            redis_config = self.config.get('database', {}).get('redis', {})
            client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('database', 0),
                password=redis_config.get('password'),
                decode_responses=True
            )
            client.ping()
            logger.info("Redis connection established")
            return client
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            return None
            
    def _setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'service': 'servicelog',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'agents': list(self.agent_manager.agents.keys()),
                'log_buffer_size': len(self.log_buffer),
                'advice_cache_size': len(self.advice_cache)
            })
            
        @self.app.route('/api/v1/services/register', methods=['POST'])
        def register_service():
            data = request.get_json()
            try:
                service = ServiceInfo(
                    service_name=data['service_name'],
                    service_type=data.get('service_type', 'unknown'),
                    port=data['port'],
                    criticality_level=data.get('criticality_level', 'MEDIUM'),
                    log_sources=data.get('log_sources', []),
                    health_endpoints=data.get('health_endpoints', []),
                    expected_patterns=data.get('expected_patterns', []),
                    alert_contacts=data.get('alert_contacts', []),
                    registration_time=datetime.now()
                )
                
                if self.db.register_service(service):
                    logger.info(f"Service registered: {service.service_name}")
                    return jsonify({'success': True, 'service_name': service.service_name})
                else:
                    return jsonify({'success': False, 'error': 'Database error'}), 500
                    
            except KeyError as e:
                return jsonify({'success': False, 'error': f'Missing required field: {e}'}), 400
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/v1/logs/ingest', methods=['POST'])
        def ingest_logs():
            data = request.get_json()
            try:
                logs = []
                log_entries = data.get('logs', [data])  # Handle single log or batch
                
                for log_data in log_entries:
                    log = LogEntry(
                        service_name=log_data['service_name'],
                        timestamp=datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00')),
                        level=log_data['level'],
                        message=log_data['message'],
                        context=log_data.get('context', {}),
                        metadata=log_data.get('metadata', {})
                    )
                    logs.append(log)
                    
                # Add to buffer for processing
                self.log_buffer.extend(logs)
                
                # Store in database
                self.db.store_logs(logs)
                
                return jsonify({
                    'success': True, 
                    'processed': len(logs),
                    'buffer_size': len(self.log_buffer)
                })
                
            except Exception as e:
                logger.error(f"Log ingestion error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/v1/advice', methods=['GET'])
        def get_advice():
            limit = request.args.get('limit', 10, type=int)
            status = request.args.get('status', 'OPEN')
            
            advice_list = self.db.get_priority_advice(limit=limit, status=status)
            return jsonify({
                'success': True,
                'advice': advice_list,
                'count': len(advice_list)
            })
            
        @self.app.route('/api/v1/advice/<advice_id>/resolve', methods=['POST'])
        def resolve_advice(advice_id):
            try:
                # Update advice status in database
                conn = sqlite3.connect(self.db.db_path)
                conn.execute('''
                    UPDATE advice_queue 
                    SET status = 'RESOLVED', resolved_at = ?, updated_at = ?
                    WHERE advice_id = ?
                ''', (datetime.now().isoformat(), datetime.now().isoformat(), advice_id))
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'advice_id': advice_id, 'status': 'RESOLVED'})
            except Exception as e:
                logger.error(f"Error resolving advice {advice_id}: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @self.app.route('/api/v1/advice/dashboard', methods=['GET'])
        def dashboard_summary():
            try:
                conn = sqlite3.connect(self.db.db_path)
                
                # Get advice statistics
                cursor = conn.execute('SELECT status, COUNT(*) FROM advice_queue GROUP BY status')
                status_counts = dict(cursor.fetchall())
                
                cursor = conn.execute('SELECT severity, COUNT(*) FROM advice_queue WHERE status = "OPEN" GROUP BY severity')
                severity_counts = dict(cursor.fetchall())
                
                cursor = conn.execute('SELECT AVG(priority_score) FROM advice_queue WHERE status = "OPEN"')
                avg_priority = cursor.fetchone()[0] or 0
                
                conn.close()
                
                return jsonify({
                    'success': True,
                    'summary': {
                        'status_distribution': status_counts,
                        'severity_distribution': severity_counts,
                        'average_priority': round(avg_priority, 2),
                        'total_services': len(self.agent_manager.agents),
                        'buffer_size': len(self.log_buffer)
                    }
                })
            except Exception as e:
                logger.error(f"Dashboard error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
                
    def start_background_processing(self):
        """Start background log processing"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_logs_continuously)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("Background log processing started")
        
    def _process_logs_continuously(self):
        """Continuously process logs from buffer"""
        while self.running:
            if len(self.log_buffer) >= 100:  # Process in batches
                # Get batch of logs
                batch = []
                for _ in range(min(100, len(self.log_buffer))):
                    try:
                        batch.append(self.log_buffer.popleft())
                    except IndexError:
                        break
                        
                if batch:
                    # Analyze logs with agents
                    advice_list = self.agent_manager.analyze_logs(batch)
                    
                    # Store generated advice
                    for advice in advice_list:
                        self.db.store_advice(advice)
                        
                    if advice_list:
                        logger.info(f"Generated {len(advice_list)} advice items from {len(batch)} logs")
                        
            time.sleep(5)  # Process every 5 seconds
            
    def run(self):
        """Run the ServiceLog service"""
        port = self.config.get('core', {}).get('port', 8750)
        
        # Start background processing
        self.start_background_processing()
        
        # Start cleanup scheduler
        schedule.every().day.do(self._cleanup_old_data)
        
        logger.info(f"🚀 ServiceLog starting on port {port}")
        logger.info(f"📊 Agents: {list(self.agent_manager.agents.keys())}")
        logger.info(f"💾 Database: {self.db.db_path}")
        
        # Run Flask app
        self.socketio.run(self.app, host='0.0.0.0', port=port, debug=False)
        
    def _cleanup_old_data(self):
        """Clean up old logs and resolved advice"""
        try:
            retention_days = self.config.get('advice_queue', {}).get('retention_days', 90)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            conn = sqlite3.connect(self.db.db_path)
            
            # Clean old logs
            conn.execute('DELETE FROM log_entries WHERE timestamp < ?', (cutoff_date.isoformat(),))
            
            # Clean resolved advice older than retention period
            conn.execute('DELETE FROM advice_queue WHERE status = "RESOLVED" AND resolved_at < ?', 
                        (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            logger.info(f"Cleanup completed: removed data older than {retention_days} days")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            
    def stop(self):
        """Stop the service gracefully"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
        logger.info("ServiceLog stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ServiceLog - Intelligent Log Analysis System')
    parser.add_argument('--config', default='servicelog_config.yaml', help='Configuration file path')
    parser.add_argument('--port', type=int, help='Override port from config')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    
    args = parser.parse_args()
    
    try:
        # Initialize ServiceLog
        servicelog = ServiceLog(args.config)
        
        # Override port if specified
        if args.port:
            servicelog.config['core']['port'] = args.port
            
        # Run the service
        servicelog.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down ServiceLog...")
    except Exception as e:
        logger.error(f"ServiceLog startup error: {e}")
        raise

if __name__ == '__main__':
    main()