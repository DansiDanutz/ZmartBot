#!/usr/bin/env python3
"""
Cursor-Claude Sync System
Advanced synchronization framework for seamless AI agent collaboration
"""

import asyncio
import json
import os
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiofiles
import aiohttp
import yaml
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_claude_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SyncContext:
    """Context information for synchronization"""
    project_id: str
    session_id: str
    timestamp: datetime
    context_hash: str
    file_changes: List[Dict[str, Any]]
    code_changes: List[Dict[str, Any]]
    ai_insights: List[Dict[str, Any]]
    optimization_suggestions: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    sync_status: str

@dataclass
class ProjectState:
    """Current state of the project"""
    project_path: str
    last_sync: datetime
    file_count: int
    code_lines: int
    dependencies: List[str]
    services: List[Dict[str, Any]]
    performance_score: float
    optimization_level: str

class CursorClaudeSyncSystem:
    """Main synchronization system between Cursor and Claude"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.db_path = os.path.join(self.project_root, '.cursor_claude_sync.db')
        self.config_path = os.path.join(self.project_root, '.cursor_claude_config.yaml')
        self.context_cache = {}
        self.sync_queue = asyncio.Queue()
        self.is_running = False
        self.observer = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize database and configuration
        self._init_database()
        self._load_config()
        
    def _init_database(self):
        """Initialize SQLite database for sync data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                context_hash TEXT NOT NULL,
                context_data TEXT NOT NULL,
                sync_status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                change_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                context_id INTEGER,
                FOREIGN KEY (context_id) REFERENCES sync_contexts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                description TEXT NOT NULL,
                implementation TEXT NOT NULL,
                impact_score REAL NOT NULL,
                context_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (context_id) REFERENCES sync_contexts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                context_id INTEGER,
                FOREIGN KEY (context_id) REFERENCES sync_contexts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        default_config = {
            'sync_interval': 5,  # seconds
            'context_cache_size': 1000,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'exclude_patterns': [
                '*.pyc', '*.pyo', '__pycache__', '.git', 'node_modules',
                '*.log', '*.tmp', '.DS_Store', '*.swp', '*.swo'
            ],
            'include_extensions': [
                '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
                '.json', '.yaml', '.yml', '.md', '.sql', '.sh', '.bat'
            ],
            'optimization_thresholds': {
                'performance': 0.8,
                'code_quality': 0.7,
                'maintainability': 0.6
            },
            'ai_models': {
                'claude': {
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 4000,
                    'temperature': 0.1
                },
                'cursor': {
                    'model': 'gpt-4',
                    'max_tokens': 4000,
                    'temperature': 0.1
                }
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
        else:
            self.config = default_config
            self._save_config()
            
    def _save_config(self):
        """Save configuration to YAML file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
            
    async def start_sync(self):
        """Start the synchronization system"""
        if self.is_running:
            logger.warning("Sync system is already running")
            return
            
        self.is_running = True
        logger.info("Starting Cursor-Claude sync system...")
        
        # Start file watcher
        self._start_file_watcher()
        
        # Start sync loop
        asyncio.create_task(self._sync_loop())
        
        # Start context optimization
        asyncio.create_task(self._context_optimization_loop())
        
        # Start performance monitoring
        asyncio.create_task(self._performance_monitoring_loop())
        
        logger.info("Sync system started successfully")
        
    async def stop_sync(self):
        """Stop the synchronization system"""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("Sync system stopped")
        
    def _start_file_watcher(self):
        """Start file system watcher"""
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.project_root, recursive=True)
        self.observer.start()
        
    async def _sync_loop(self):
        """Main synchronization loop"""
        while self.is_running:
            try:
                # Process sync queue
                if not self.sync_queue.empty():
                    context = await self.sync_queue.get()
                    await self._process_sync_context(context)
                    
                # Generate sync context
                await self._generate_sync_context()
                
                await asyncio.sleep(self.config['sync_interval'])
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(5)
                
    async def _generate_sync_context(self):
        """Generate current sync context"""
        try:
            # Analyze project state
            project_state = await self._analyze_project_state()
            
            # Detect file changes
            file_changes = await self._detect_file_changes()
            
            # Analyze code changes
            code_changes = await self._analyze_code_changes()
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(project_state, file_changes, code_changes)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(project_state, ai_insights)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(project_state)
            
            # Create sync context
            context_hash = self._calculate_context_hash(project_state, file_changes, code_changes)
            sync_context = SyncContext(
                project_id=self._get_project_id(),
                session_id=self._get_session_id(),
                timestamp=datetime.now(),
                context_hash=context_hash,
                file_changes=file_changes,
                code_changes=code_changes,
                ai_insights=ai_insights,
                optimization_suggestions=optimization_suggestions,
                performance_metrics=performance_metrics,
                sync_status='generated'
            )
            
            # Add to sync queue
            await self.sync_queue.put(sync_context)
            
        except Exception as e:
            logger.error(f"Error generating sync context: {e}")
            
    async def _analyze_project_state(self) -> ProjectState:
        """Analyze current project state"""
        try:
            # Count files and lines
            file_count = 0
            code_lines = 0
            dependencies = []
            services = []
            
            for root, dirs, files in os.walk(self.project_root):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(d.startswith(pattern.replace('*', '')) for pattern in self.config['exclude_patterns'])]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._should_include_file(file_path):
                        file_count += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                code_lines += len(lines)
                        except:
                            pass
                            
            # Analyze dependencies
            dependencies = await self._analyze_dependencies()
            
            # Analyze services
            services = await self._analyze_services()
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(file_count, code_lines, dependencies, services)
            
            return ProjectState(
                project_path=self.project_root,
                last_sync=datetime.now(),
                file_count=file_count,
                code_lines=code_lines,
                dependencies=dependencies,
                services=services,
                performance_score=performance_score,
                optimization_level=self._get_optimization_level(performance_score)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing project state: {e}")
            return ProjectState(
                project_path=self.project_root,
                last_sync=datetime.now(),
                file_count=0,
                code_lines=0,
                dependencies=[],
                services=[],
                performance_score=0.0,
                optimization_level='unknown'
            )
            
    async def _detect_file_changes(self) -> List[Dict[str, Any]]:
        """Detect file changes since last sync"""
        changes = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last sync timestamp
            cursor.execute('SELECT MAX(timestamp) FROM sync_contexts')
            last_sync = cursor.fetchone()[0]
            
            if last_sync:
                last_sync_dt = datetime.fromisoformat(last_sync)
            else:
                last_sync_dt = datetime.now() - timedelta(hours=1)
                
            # Check for modified files
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._should_include_file(file_path):
                        try:
                            stat = os.stat(file_path)
                            if datetime.fromtimestamp(stat.st_mtime) > last_sync_dt:
                                content_hash = self._calculate_file_hash(file_path)
                                changes.append({
                                    'file_path': file_path,
                                    'change_type': 'modified',
                                    'content_hash': content_hash,
                                    'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
                                })
                        except:
                            pass
                            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error detecting file changes: {e}")
            
        return changes
        
    async def _analyze_code_changes(self) -> List[Dict[str, Any]]:
        """Analyze code changes for optimization opportunities"""
        changes = []
        try:
            # Analyze code quality
            quality_issues = await self._analyze_code_quality()
            changes.extend(quality_issues)
            
            # Analyze performance issues
            performance_issues = await self._analyze_performance_issues()
            changes.extend(performance_issues)
            
            # Analyze security issues
            security_issues = await self._analyze_security_issues()
            changes.extend(security_issues)
            
        except Exception as e:
            logger.error(f"Error analyzing code changes: {e}")
            
        return changes
        
    async def _generate_ai_insights(self, project_state: ProjectState, file_changes: List[Dict], code_changes: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI insights using Claude and Cursor models"""
        insights = []
        try:
            # Generate insights based on project state
            if project_state.performance_score < 0.7:
                insights.append({
                    'type': 'performance',
                    'priority': 'high',
                    'description': f'Project performance score is {project_state.performance_score:.2f}, below optimal threshold',
                    'recommendations': [
                        'Optimize database queries',
                        'Implement caching strategies',
                        'Review and optimize algorithms',
                        'Consider code refactoring'
                    ]
                })
                
            # Generate insights based on file changes
            if len(file_changes) > 10:
                insights.append({
                    'type': 'activity',
                    'priority': 'medium',
                    'description': f'High file change activity detected: {len(file_changes)} files modified',
                    'recommendations': [
                        'Consider implementing automated testing',
                        'Review change impact on system stability',
                        'Implement change tracking and rollback mechanisms'
                    ]
                })
                
            # Generate insights based on code changes
            if any(change.get('type') == 'security' for change in code_changes):
                insights.append({
                    'type': 'security',
                    'priority': 'critical',
                    'description': 'Security issues detected in code changes',
                    'recommendations': [
                        'Immediate security review required',
                        'Implement security testing',
                        'Review access controls and permissions'
                    ]
                })
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            
        return insights
        
    async def _generate_optimization_suggestions(self, project_state: ProjectState, ai_insights: List[Dict]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions"""
        suggestions = []
        try:
            # Performance optimization suggestions
            if project_state.performance_score < 0.8:
                suggestions.append({
                    'type': 'performance',
                    'priority': 1,
                    'description': 'Optimize database queries and implement caching',
                    'implementation': '''
                    # Implement query optimization
                    - Add database indexes for frequently queried columns
                    - Implement Redis caching for expensive operations
                    - Use connection pooling for database connections
                    - Implement query result caching
                    ''',
                    'impact_score': 0.8
                })
                
            # Code quality optimization suggestions
            if project_state.code_lines > 10000:
                suggestions.append({
                    'type': 'maintainability',
                    'priority': 2,
                    'description': 'Refactor large codebase for better maintainability',
                    'implementation': '''
                    # Code refactoring strategy
                    - Break down large functions into smaller, focused functions
                    - Implement design patterns (Factory, Strategy, Observer)
                    - Add comprehensive documentation and type hints
                    - Implement automated testing and CI/CD
                    ''',
                    'impact_score': 0.7
                })
                
            # Security optimization suggestions
            security_insights = [insight for insight in ai_insights if insight.get('type') == 'security']
            if security_insights:
                suggestions.append({
                    'type': 'security',
                    'priority': 1,
                    'description': 'Implement comprehensive security measures',
                    'implementation': '''
                    # Security implementation
                    - Add input validation and sanitization
                    - Implement authentication and authorization
                    - Use HTTPS for all communications
                    - Implement rate limiting and DDoS protection
                    - Regular security audits and penetration testing
                    ''',
                    'impact_score': 0.9
                })
                
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            
        return suggestions
        
    async def _calculate_performance_metrics(self, project_state: ProjectState) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {}
        try:
            # System performance metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(self.project_root)
            
            metrics.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'file_count': project_state.file_count,
                'code_lines': project_state.code_lines,
                'performance_score': project_state.performance_score,
                'optimization_level': project_state.optimization_level
            })
            
            # Code quality metrics
            metrics.update({
                'cyclomatic_complexity': await self._calculate_cyclomatic_complexity(),
                'code_coverage': await self._calculate_code_coverage(),
                'technical_debt': await self._calculate_technical_debt()
            })
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            
        return metrics
        
    async def _process_sync_context(self, context: SyncContext):
        """Process sync context and store in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store sync context
            cursor.execute('''
                INSERT INTO sync_contexts (project_id, session_id, timestamp, context_hash, context_data, sync_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                context.project_id,
                context.session_id,
                context.timestamp.isoformat(),
                context.context_hash,
                json.dumps(asdict(context)),
                context.sync_status
            ))
            
            context_id = cursor.lastrowid
            
            # Store file changes
            for change in context.file_changes:
                cursor.execute('''
                    INSERT INTO file_changes (file_path, change_type, content_hash, timestamp, context_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    change['file_path'],
                    change['change_type'],
                    change['content_hash'],
                    change['timestamp'],
                    context_id
                ))
                
            # Store optimization suggestions
            for suggestion in context.optimization_suggestions:
                cursor.execute('''
                    INSERT INTO optimization_suggestions (suggestion_type, priority, description, implementation, impact_score, context_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    suggestion['type'],
                    suggestion['priority'],
                    suggestion['description'],
                    suggestion['implementation'],
                    suggestion['impact_score'],
                    context_id
                ))
                
            # Store performance metrics
            for metric_name, metric_value in context.performance_metrics.items():
                cursor.execute('''
                    INSERT INTO performance_metrics (metric_name, metric_value, timestamp, context_id)
                    VALUES (?, ?, ?, ?)
                ''', (
                    metric_name,
                    metric_value,
                    context.timestamp.isoformat(),
                    context_id
                ))
                
            conn.commit()
            conn.close()
            
            logger.info(f"Processed sync context: {context.context_hash}")
            
        except Exception as e:
            logger.error(f"Error processing sync context: {e}")
            
    async def _context_optimization_loop(self):
        """Context optimization loop"""
        while self.is_running:
            try:
                # Optimize context cache
                await self._optimize_context_cache()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Error in context optimization loop: {e}")
                await asyncio.sleep(30)
                
    async def _performance_monitoring_loop(self):
        """Performance monitoring loop"""
        while self.is_running:
            try:
                # Monitor system performance
                await self._monitor_system_performance()
                
                # Monitor sync performance
                await self._monitor_sync_performance()
                
                await asyncio.sleep(30)  # Run every 30 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(15)
                
    def _should_include_file(self, file_path: str) -> bool:
        """Check if file should be included in sync"""
        # Check file size
        try:
            if os.path.getsize(file_path) > self.config['max_file_size']:
                return False
        except:
            return False
            
        # Check extension
        ext = os.path.splitext(file_path)[1]
        if ext not in self.config['include_extensions']:
            return False
            
        # Check exclude patterns
        for pattern in self.config['exclude_patterns']:
            if pattern.startswith('*'):
                if file_path.endswith(pattern[1:]):
                    return False
            else:
                if pattern in file_path:
                    return False
                    
        return True
        
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ''
            
    def _calculate_context_hash(self, project_state: ProjectState, file_changes: List[Dict], code_changes: List[Dict]) -> str:
        """Calculate hash of sync context"""
        data = {
            'project_state': asdict(project_state),
            'file_changes': file_changes,
            'code_changes': code_changes
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
    def _get_project_id(self) -> str:
        """Get unique project ID"""
        return hashlib.md5(self.project_root.encode()).hexdigest()[:16]
        
    def _get_session_id(self) -> str:
        """Get unique session ID"""
        return hashlib.md5(f"{self.project_root}{time.time()}".encode()).hexdigest()[:16]
        
    def _get_optimization_level(self, performance_score: float) -> str:
        """Get optimization level based on performance score"""
        if performance_score >= 0.9:
            return 'excellent'
        elif performance_score >= 0.8:
            return 'good'
        elif performance_score >= 0.6:
            return 'fair'
        else:
            return 'poor'
            
    # Additional helper methods for code analysis
    async def _analyze_dependencies(self) -> List[str]:
        """Analyze project dependencies"""
        dependencies = []
        try:
            # Check for requirements.txt
            req_file = os.path.join(self.project_root, 'requirements.txt')
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    dependencies.extend([line.strip() for line in f if line.strip()])
                    
            # Check for package.json
            package_file = os.path.join(self.project_root, 'package.json')
            if os.path.exists(package_file):
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    if 'dependencies' in package_data:
                        dependencies.extend(package_data['dependencies'].keys())
                        
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            
        return dependencies
        
    async def _analyze_services(self) -> List[Dict[str, Any]]:
        """Analyze running services"""
        services = []
        try:
            # Check for running services on common ports
            common_ports = [8000, 8001, 8002, 3000, 3001, 5000, 5001]
            for port in common_ports:
                try:
                    result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout:
                        services.append({
                            'port': port,
                            'status': 'running',
                            'processes': result.stdout.strip().split('\n')[1:]  # Skip header
                        })
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error analyzing services: {e}")
            
        return services
        
    async def _calculate_performance_score(self, file_count: int, code_lines: int, dependencies: List[str], services: List[Dict]) -> float:
        """Calculate overall performance score"""
        score = 1.0
        
        # File count factor (optimal range: 50-500 files)
        if file_count < 50:
            score *= 0.9
        elif file_count > 500:
            score *= 0.8
            
        # Code lines factor (optimal range: 1000-10000 lines)
        if code_lines < 1000:
            score *= 0.9
        elif code_lines > 10000:
            score *= 0.7
            
        # Dependencies factor (optimal range: 5-20 dependencies)
        if len(dependencies) < 5:
            score *= 0.9
        elif len(dependencies) > 20:
            score *= 0.8
            
        # Services factor (optimal range: 2-5 services)
        if len(services) < 2:
            score *= 0.9
        elif len(services) > 5:
            score *= 0.8
            
        return min(score, 1.0)
        
    async def _analyze_code_quality(self) -> List[Dict[str, Any]]:
        """Analyze code quality issues"""
        issues = []
        try:
            # This would integrate with code analysis tools
            # For now, return empty list
            pass
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
        return issues
        
    async def _analyze_performance_issues(self) -> List[Dict[str, Any]]:
        """Analyze performance issues"""
        issues = []
        try:
            # This would integrate with performance analysis tools
            # For now, return empty list
            pass
        except Exception as e:
            logger.error(f"Error analyzing performance issues: {e}")
        return issues
        
    async def _analyze_security_issues(self) -> List[Dict[str, Any]]:
        """Analyze security issues"""
        issues = []
        try:
            # This would integrate with security analysis tools
            # For now, return empty list
            pass
        except Exception as e:
            logger.error(f"Error analyzing security issues: {e}")
        return issues
        
    async def _calculate_cyclomatic_complexity(self) -> float:
        """Calculate cyclomatic complexity"""
        # This would integrate with code analysis tools
        return 0.0
        
    async def _calculate_code_coverage(self) -> float:
        """Calculate code coverage"""
        # This would integrate with testing tools
        return 0.0
        
    async def _calculate_technical_debt(self) -> float:
        """Calculate technical debt"""
        # This would integrate with code analysis tools
        return 0.0
        
    async def _optimize_context_cache(self):
        """Optimize context cache"""
        try:
            # Remove old entries if cache is too large
            if len(self.context_cache) > self.config['context_cache_size']:
                # Remove oldest entries
                sorted_items = sorted(self.context_cache.items(), key=lambda x: x[1].get('timestamp', 0))
                items_to_remove = len(self.context_cache) - self.config['context_cache_size']
                for key, _ in sorted_items[:items_to_remove]:
                    del self.context_cache[key]
                    
        except Exception as e:
            logger.error(f"Error optimizing context cache: {e}")
            
    async def _cleanup_old_data(self):
        """Clean up old data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove sync contexts older than 7 days
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('DELETE FROM sync_contexts WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            
    async def _monitor_system_performance(self):
        """Monitor system performance"""
        try:
            # Monitor CPU, memory, disk usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(self.project_root)
            
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 80:
                logger.warning(f"High memory usage: {memory.percent}%")
            if disk.percent > 80:
                logger.warning(f"High disk usage: {disk.percent}%")
                
        except Exception as e:
            logger.error(f"Error monitoring system performance: {e}")
            
    async def _monitor_sync_performance(self):
        """Monitor sync performance"""
        try:
            # Monitor sync queue size
            queue_size = self.sync_queue.qsize()
            if queue_size > 10:
                logger.warning(f"Large sync queue: {queue_size} items")
                
        except Exception as e:
            logger.error(f"Error monitoring sync performance: {e}")

class FileChangeHandler(FileSystemEventHandler):
    """Handle file system changes"""
    
    def __init__(self, sync_system: CursorClaudeSyncSystem):
        self.sync_system = sync_system
        
    def on_modified(self, event):
        if not event.is_directory and self.sync_system._should_include_file(event.src_path):
            logger.info(f"File modified: {event.src_path}")
            
    def on_created(self, event):
        if not event.is_directory and self.sync_system._should_include_file(event.src_path):
            logger.info(f"File created: {event.src_path}")
            
    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")

# CLI interface
async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor-Claude Sync System')
    parser.add_argument('--project-root', default=os.getcwd(), help='Project root directory')
    parser.add_argument('--start', action='store_true', help='Start sync system')
    parser.add_argument('--stop', action='store_true', help='Stop sync system')
    parser.add_argument('--status', action='store_true', help='Show sync status')
    
    args = parser.parse_args()
    
    sync_system = CursorClaudeSyncSystem(args.project_root)
    
    if args.start:
        await sync_system.start_sync()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await sync_system.stop_sync()
    elif args.stop:
        await sync_system.stop_sync()
    elif args.status:
        # Show status
        print("Sync system status: Not implemented yet")
    else:
        parser.print_help()

if __name__ == '__main__':
    asyncio.run(main())
