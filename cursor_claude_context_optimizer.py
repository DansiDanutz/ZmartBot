#!/usr/bin/env python3
"""
Cursor-Claude Context Optimizer
Optimizes context management for Claude running inside Cursor IDE
Works with existing Claude-in-Cursor setup without modifications
"""

import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import yaml
import psutil
import subprocess
from collections import defaultdict, deque
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_claude_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContextSnapshot:
    """Snapshot of current context state"""
    timestamp: datetime
    project_path: str
    active_files: List[str]
    recent_changes: List[Dict[str, Any]]
    code_context: Dict[str, Any]
    project_metrics: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]

@dataclass
class ProjectIntelligence:
    """Intelligence about project structure and patterns"""
    project_type: str
    main_technologies: List[str]
    architecture_patterns: List[str]
    common_patterns: Dict[str, int]
    performance_bottlenecks: List[str]
    optimization_opportunities: List[str]

class CursorClaudeContextOptimizer:
    """Context optimizer for Claude running inside Cursor"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.db_path = os.path.join(self.project_root, '.cursor_claude_context.db')
        self.config_path = os.path.join(self.project_root, '.cursor_claude_optimizer.yaml')
        self.context_cache = deque(maxlen=100)
        self.project_intelligence = None
        self.is_running = False
        
        # Initialize
        self._init_database()
        self._load_config()
        self._analyze_project_intelligence()
        
    def _init_database(self):
        """Initialize SQLite database for context data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Context snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                project_path TEXT NOT NULL,
                active_files TEXT NOT NULL,
                context_data TEXT NOT NULL,
                optimization_score REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optimization suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                description TEXT NOT NULL,
                implementation TEXT NOT NULL,
                impact_score REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                context_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (context_id) REFERENCES context_snapshots (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_config(self):
        """Load configuration"""
        default_config = {
            'context_analysis_interval': 30,  # seconds
            'max_context_files': 50,
            'max_file_size_kb': 1000,  # 1MB
            'include_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.yaml', '.md'],
            'exclude_patterns': ['__pycache__', '.git', 'node_modules', '*.pyc', '*.log', '.DS_Store'],
            'optimization_thresholds': {
                'context_size': 0.8,
                'file_complexity': 0.7,
                'project_health': 0.6
            },
            'claude_context_limits': {
                'max_tokens': 200000,  # Claude's context limit
                'optimal_tokens': 150000,  # Optimal for performance
                'min_tokens': 50000  # Minimum for meaningful context
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
        """Save configuration"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
            
    def _analyze_project_intelligence(self):
        """Analyze project to understand its structure and patterns"""
        try:
            # Detect project type
            project_type = self._detect_project_type()
            
            # Identify main technologies
            main_technologies = self._identify_technologies()
            
            # Find architecture patterns
            architecture_patterns = self._find_architecture_patterns()
            
            # Analyze common patterns
            common_patterns = self._analyze_common_patterns()
            
            # Identify performance bottlenecks
            performance_bottlenecks = self._identify_performance_bottlenecks()
            
            # Find optimization opportunities
            optimization_opportunities = self._find_optimization_opportunities()
            
            self.project_intelligence = ProjectIntelligence(
                project_type=project_type,
                main_technologies=main_technologies,
                architecture_patterns=architecture_patterns,
                common_patterns=common_patterns,
                performance_bottlenecks=performance_bottlenecks,
                optimization_opportunities=optimization_opportunities
            )
            
            logger.info(f"Project intelligence analyzed: {project_type} with {len(main_technologies)} technologies")
            
        except Exception as e:
            logger.error(f"Error analyzing project intelligence: {e}")
            self.project_intelligence = ProjectIntelligence(
                project_type='unknown',
                main_technologies=[],
                architecture_patterns=[],
                common_patterns={},
                performance_bottlenecks=[],
                optimization_opportunities=[]
            )
            
    def _detect_project_type(self) -> str:
        """Detect the type of project"""
        # Check for common project indicators
        indicators = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'nodejs': ['package.json', 'yarn.lock', 'package-lock.json'],
            'react': ['src/App.js', 'src/App.tsx', 'public/index.html'],
            'vue': ['src/App.vue', 'vue.config.js'],
            'angular': ['angular.json', 'src/app/app.component.ts'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'application.py'],
            'fastapi': ['main.py', 'app.py'],
            'trading_bot': ['zmart', 'trading', 'bot', 'crypto'],
            'fullstack': ['frontend', 'backend', 'api']
        }
        
        project_files = []
        for root, dirs, files in os.walk(self.project_root):
            project_files.extend(files)
            
        scores = defaultdict(int)
        for project_type, files in indicators.items():
            for file in files:
                if file in project_files:
                    scores[project_type] += 1
                    
        # Check project name and structure
        project_name = os.path.basename(self.project_root).lower()
        for project_type in indicators.keys():
            if project_type in project_name:
                scores[project_type] += 2
                
        if scores:
            return max(scores, key=scores.get)
        return 'unknown'
        
    def _identify_technologies(self) -> List[str]:
        """Identify main technologies used in the project"""
        technologies = []
        
        # Check package files
        if os.path.exists(os.path.join(self.project_root, 'package.json')):
            technologies.append('nodejs')
            try:
                with open(os.path.join(self.project_root, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                    if 'dependencies' in package_data:
                        deps = package_data['dependencies']
                        if 'react' in deps:
                            technologies.append('react')
                        if 'vue' in deps:
                            technologies.append('vue')
                        if 'angular' in deps:
                            technologies.append('angular')
                        if 'express' in deps:
                            technologies.append('express')
            except:
                pass
                
        if os.path.exists(os.path.join(self.project_root, 'requirements.txt')):
            technologies.append('python')
            try:
                with open(os.path.join(self.project_root, 'requirements.txt'), 'r') as f:
                    content = f.read()
                    if 'django' in content:
                        technologies.append('django')
                    if 'flask' in content:
                        technologies.append('flask')
                    if 'fastapi' in content:
                        technologies.append('fastapi')
                    if 'pandas' in content:
                        technologies.append('pandas')
                    if 'numpy' in content:
                        technologies.append('numpy')
            except:
                pass
                
        # Check for specific files
        if os.path.exists(os.path.join(self.project_root, 'Dockerfile')):
            technologies.append('docker')
        if os.path.exists(os.path.join(self.project_root, 'docker-compose.yml')):
            technologies.append('docker-compose')
        if os.path.exists(os.path.join(self.project_root, '.git')):
            technologies.append('git')
            
        return list(set(technologies))
        
    def _find_architecture_patterns(self) -> List[str]:
        """Find architecture patterns in the project"""
        patterns = []
        
        # Check directory structure
        dirs = [d for d in os.listdir(self.project_root) if os.path.isdir(os.path.join(self.project_root, d))]
        
        if 'src' in dirs and 'tests' in dirs:
            patterns.append('src-tests-separation')
        if 'frontend' in dirs and 'backend' in dirs:
            patterns.append('frontend-backend-separation')
        if 'api' in dirs:
            patterns.append('api-layer')
        if 'services' in dirs:
            patterns.append('service-layer')
        if 'models' in dirs:
            patterns.append('model-layer')
        if 'controllers' in dirs:
            patterns.append('mvc-pattern')
        if 'components' in dirs:
            patterns.append('component-based')
        if 'utils' in dirs or 'helpers' in dirs:
            patterns.append('utility-functions')
            
        return patterns
        
    def _analyze_common_patterns(self) -> Dict[str, int]:
        """Analyze common code patterns"""
        patterns = defaultdict(int)
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.config['exclude_patterns'])]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.config['include_extensions']):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Analyze patterns
                                if 'async def' in content:
                                    patterns['async-functions'] += 1
                                if 'class ' in content:
                                    patterns['classes'] += 1
                                if 'def ' in content:
                                    patterns['functions'] += 1
                                if 'import ' in content:
                                    patterns['imports'] += 1
                                if 'try:' in content:
                                    patterns['error-handling'] += 1
                                if 'if __name__' in content:
                                    patterns['main-guards'] += 1
                                if 'logger' in content:
                                    patterns['logging'] += 1
                                if 'TODO' in content or 'FIXME' in content:
                                    patterns['todos'] += 1
                                    
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Error analyzing common patterns: {e}")
            
        return dict(patterns)
        
    def _identify_performance_bottlenecks(self) -> List[str]:
        """Identify potential performance bottlenecks"""
        bottlenecks = []
        
        try:
            # Check for large files
            large_files = []
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if size > self.config['max_file_size_kb'] * 1024:
                            large_files.append(file_path)
                    except:
                        pass
                        
            if large_files:
                bottlenecks.append(f"Large files detected: {len(large_files)} files over {self.config['max_file_size_kb']}KB")
                
            # Check for complex files (high line count)
            complex_files = []
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    if file.endswith('.py') or file.endswith('.js') or file.endswith('.ts'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                if lines > 500:
                                    complex_files.append((file_path, lines))
                        except:
                            pass
                            
            if complex_files:
                bottlenecks.append(f"Complex files detected: {len(complex_files)} files over 500 lines")
                
            # Check for potential issues
            if 'node_modules' in os.listdir(self.project_root):
                bottlenecks.append("Large node_modules directory")
            if '__pycache__' in os.listdir(self.project_root):
                bottlenecks.append("Python cache files present")
                
        except Exception as e:
            logger.error(f"Error identifying performance bottlenecks: {e}")
            
        return bottlenecks
        
    def _find_optimization_opportunities(self) -> List[str]:
        """Find optimization opportunities"""
        opportunities = []
        
        try:
            # Check for missing optimizations
            if not os.path.exists(os.path.join(self.project_root, '.gitignore')):
                opportunities.append("Add .gitignore file")
                
            if not os.path.exists(os.path.join(self.project_root, 'README.md')):
                opportunities.append("Add README.md documentation")
                
            # Check for code quality opportunities
            has_tests = False
            for root, dirs, files in os.walk(self.project_root):
                if 'test' in root.lower() or any('test' in f.lower() for f in files):
                    has_tests = True
                    break
                    
            if not has_tests:
                opportunities.append("Add unit tests")
                
            # Check for linting
            if not os.path.exists(os.path.join(self.project_root, '.eslintrc')) and not os.path.exists(os.path.join(self.project_root, 'pyproject.toml')):
                opportunities.append("Add code linting configuration")
                
            # Check for CI/CD
            if not os.path.exists(os.path.join(self.project_root, '.github')):
                opportunities.append("Add CI/CD pipeline")
                
        except Exception as e:
            logger.error(f"Error finding optimization opportunities: {e}")
            
        return opportunities
        
    def create_context_snapshot(self) -> ContextSnapshot:
        """Create a snapshot of current context"""
        try:
            # Get active files (recently modified)
            active_files = self._get_active_files()
            
            # Get recent changes
            recent_changes = self._get_recent_changes()
            
            # Analyze code context
            code_context = self._analyze_code_context(active_files)
            
            # Calculate project metrics
            project_metrics = self._calculate_project_metrics()
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions()
            
            snapshot = ContextSnapshot(
                timestamp=datetime.now(),
                project_path=self.project_root,
                active_files=active_files,
                recent_changes=recent_changes,
                code_context=code_context,
                project_metrics=project_metrics,
                optimization_suggestions=optimization_suggestions
            )
            
            # Store in cache and database
            self.context_cache.append(snapshot)
            self._store_context_snapshot(snapshot)
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error creating context snapshot: {e}")
            return None
            
    def _get_active_files(self) -> List[str]:
        """Get list of active files (recently modified)"""
        active_files = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.config['exclude_patterns'])]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.config['include_extensions']):
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            if datetime.fromtimestamp(stat.st_mtime) > cutoff_time:
                                active_files.append(file_path)
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Error getting active files: {e}")
            
        # Sort by modification time and limit
        active_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return active_files[:self.config['max_context_files']]
        
    def _get_recent_changes(self) -> List[Dict[str, Any]]:
        """Get recent changes in the project"""
        changes = []
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        try:
            # This would integrate with git to get actual changes
            # For now, we'll use file modification times
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        if datetime.fromtimestamp(stat.st_mtime) > cutoff_time:
                            changes.append({
                                'file_path': file_path,
                                'change_type': 'modified',
                                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'size': stat.st_size
                            })
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            
        return changes
        
    def _analyze_code_context(self, active_files: List[str]) -> Dict[str, Any]:
        """Analyze code context from active files"""
        context = {
            'total_files': len(active_files),
            'total_lines': 0,
            'languages': defaultdict(int),
            'imports': set(),
            'functions': [],
            'classes': [],
            'patterns': defaultdict(int)
        }
        
        try:
            for file_path in active_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        context['total_lines'] += len(lines)
                        
                        # Detect language
                        ext = os.path.splitext(file_path)[1]
                        context['languages'][ext] += 1
                        
                        # Analyze imports
                        for line in lines:
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                context['imports'].add(line.strip())
                                
                        # Analyze functions and classes
                        for line in lines:
                            if line.strip().startswith('def '):
                                context['functions'].append(line.strip())
                            elif line.strip().startswith('class '):
                                context['classes'].append(line.strip())
                                
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error analyzing code context: {e}")
            
        # Convert sets to lists for JSON serialization
        context['imports'] = list(context['imports'])
        context['languages'] = dict(context['languages'])
        context['patterns'] = dict(context['patterns'])
        
        return context
        
    def _calculate_project_metrics(self) -> Dict[str, Any]:
        """Calculate project metrics"""
        metrics = {
            'file_count': 0,
            'total_lines': 0,
            'languages': defaultdict(int),
            'complexity_score': 0.0,
            'maintainability_score': 0.0,
            'performance_score': 0.0
        }
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.config['exclude_patterns'])]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.config['include_extensions']):
                        file_path = os.path.join(root, file)
                        metrics['file_count'] += 1
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                metrics['total_lines'] += len(lines)
                                
                                # Count language
                                ext = os.path.splitext(file)[1]
                                metrics['languages'][ext] += 1
                                
                        except:
                            pass
                            
            # Calculate scores
            metrics['complexity_score'] = min(metrics['total_lines'] / 10000, 1.0)
            metrics['maintainability_score'] = max(0, 1.0 - (metrics['file_count'] / 1000))
            metrics['performance_score'] = (metrics['complexity_score'] + metrics['maintainability_score']) / 2
            
            # Convert defaultdict to dict
            metrics['languages'] = dict(metrics['languages'])
            
        except Exception as e:
            logger.error(f"Error calculating project metrics: {e}")
            
        return metrics
        
    def _generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on current context"""
        suggestions = []
        
        try:
            # Get current metrics
            metrics = self._calculate_project_metrics()
            
            # Performance suggestions
            if metrics['performance_score'] < 0.7:
                suggestions.append({
                    'type': 'performance',
                    'priority': 1,
                    'description': 'Optimize project performance',
                    'implementation': '''
                    - Break down large files into smaller modules
                    - Implement caching for expensive operations
                    - Optimize database queries
                    - Use async/await for I/O operations
                    ''',
                    'impact_score': 0.8
                })
                
            # Code quality suggestions
            if metrics['maintainability_score'] < 0.6:
                suggestions.append({
                    'type': 'maintainability',
                    'priority': 2,
                    'description': 'Improve code maintainability',
                    'implementation': '''
                    - Add comprehensive documentation
                    - Implement unit tests
                    - Use type hints (Python) or TypeScript
                    - Follow consistent coding standards
                    ''',
                    'impact_score': 0.7
                })
                
            # Architecture suggestions
            if self.project_intelligence and len(self.project_intelligence.architecture_patterns) < 3:
                suggestions.append({
                    'type': 'architecture',
                    'priority': 2,
                    'description': 'Improve project architecture',
                    'implementation': '''
                    - Implement separation of concerns
                    - Use design patterns (MVC, Repository, etc.)
                    - Create clear module boundaries
                    - Implement dependency injection
                    ''',
                    'impact_score': 0.6
                })
                
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            
        return suggestions
        
    def _store_context_snapshot(self, snapshot: ContextSnapshot):
        """Store context snapshot in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(snapshot)
            
            # Convert snapshot to dict and handle datetime serialization
            snapshot_dict = asdict(snapshot)
            snapshot_dict['timestamp'] = snapshot.timestamp.isoformat()
            
            cursor.execute('''
                INSERT INTO context_snapshots (timestamp, project_path, active_files, context_data, optimization_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                snapshot.timestamp.isoformat(),
                snapshot.project_path,
                json.dumps(snapshot.active_files),
                json.dumps(snapshot_dict),
                optimization_score
            ))
            
            context_id = cursor.lastrowid
            
            # Store optimization suggestions
            for suggestion in snapshot.optimization_suggestions:
                cursor.execute('''
                    INSERT INTO optimization_suggestions (suggestion_type, priority, description, implementation, impact_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    suggestion['type'],
                    suggestion['priority'],
                    suggestion['description'],
                    suggestion['implementation'],
                    suggestion['impact_score']
                ))
                
            # Store performance metrics
            for metric_name, metric_value in snapshot.project_metrics.items():
                if isinstance(metric_value, (int, float)):
                    cursor.execute('''
                        INSERT INTO performance_metrics (metric_name, metric_value, context_id)
                        VALUES (?, ?, ?)
                    ''', (metric_name, metric_value, context_id))
                    
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing context snapshot: {e}")
            
    def _calculate_optimization_score(self, snapshot: ContextSnapshot) -> float:
        """Calculate optimization score for the snapshot"""
        try:
            score = 1.0
            
            # File count factor
            if snapshot.project_metrics['file_count'] > 100:
                score *= 0.9
            elif snapshot.project_metrics['file_count'] > 500:
                score *= 0.8
                
            # Lines of code factor
            if snapshot.project_metrics['total_lines'] > 10000:
                score *= 0.9
            elif snapshot.project_metrics['total_lines'] > 50000:
                score *= 0.8
                
            # Performance score factor
            score *= snapshot.project_metrics.get('performance_score', 1.0)
            
            # Maintainability score factor
            score *= snapshot.project_metrics.get('maintainability_score', 1.0)
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 0.5
            
    def get_optimized_context_for_claude(self, max_tokens: int = None) -> Dict[str, Any]:
        """Get optimized context for Claude with token limits"""
        if max_tokens is None:
            max_tokens = self.config['claude_context_limits']['optimal_tokens']
            
        try:
            # Get latest snapshot
            if not self.context_cache:
                snapshot = self.create_context_snapshot()
            else:
                snapshot = self.context_cache[-1]
                
            if not snapshot:
                return {}
                
            # Build optimized context
            context = {
                'project_info': {
                    'type': self.project_intelligence.project_type if self.project_intelligence else 'unknown',
                    'technologies': self.project_intelligence.main_technologies if self.project_intelligence else [],
                    'architecture': self.project_intelligence.architecture_patterns if self.project_intelligence else []
                },
                'current_state': {
                    'active_files': snapshot.active_files[:10],  # Limit to 10 most recent
                    'recent_changes': snapshot.recent_changes[:5],  # Limit to 5 most recent
                    'metrics': snapshot.project_metrics
                },
                'optimization_suggestions': snapshot.optimization_suggestions[:3],  # Top 3 suggestions
                'context_summary': self._create_context_summary(snapshot)
            }
            
            # Estimate token usage and trim if necessary
            estimated_tokens = self._estimate_token_usage(context)
            if estimated_tokens > max_tokens:
                context = self._trim_context(context, max_tokens)
                
            return context
            
        except Exception as e:
            logger.error(f"Error getting optimized context: {e}")
            return {}
            
    def _create_context_summary(self, snapshot: ContextSnapshot) -> str:
        """Create a summary of the current context"""
        try:
            summary_parts = []
            
            # Project type and technologies
            if self.project_intelligence:
                summary_parts.append(f"Project Type: {self.project_intelligence.project_type}")
                if self.project_intelligence.main_technologies:
                    summary_parts.append(f"Technologies: {', '.join(self.project_intelligence.main_technologies)}")
                    
            # Current activity
            if snapshot.active_files:
                summary_parts.append(f"Active Files: {len(snapshot.active_files)} recently modified")
                
            if snapshot.recent_changes:
                summary_parts.append(f"Recent Changes: {len(snapshot.recent_changes)} files modified in last hour")
                
            # Metrics
            metrics = snapshot.project_metrics
            summary_parts.append(f"Total Files: {metrics.get('file_count', 0)}")
            summary_parts.append(f"Total Lines: {metrics.get('total_lines', 0)}")
            summary_parts.append(f"Performance Score: {metrics.get('performance_score', 0):.2f}")
            
            # Optimization opportunities
            if snapshot.optimization_suggestions:
                summary_parts.append(f"Optimization Opportunities: {len(snapshot.optimization_suggestions)} suggestions available")
                
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating context summary: {e}")
            return "Context summary unavailable"
            
    def _estimate_token_usage(self, context: Dict[str, Any]) -> int:
        """Estimate token usage for context (rough approximation)"""
        try:
            # Convert to JSON string and estimate tokens (rough: 1 token ≈ 4 characters)
            context_str = json.dumps(context, indent=2)
            return len(context_str) // 4
        except:
            return 1000  # Default estimate
            
    def _trim_context(self, context: Dict[str, Any], max_tokens: int) -> Dict[str, Any]:
        """Trim context to fit within token limits"""
        try:
            # Start with essential information
            trimmed = {
                'project_info': context.get('project_info', {}),
                'context_summary': context.get('context_summary', ''),
                'optimization_suggestions': context.get('optimization_suggestions', [])[:2]  # Keep only top 2
            }
            
            # Add current state if there's room
            estimated_tokens = self._estimate_token_usage(trimmed)
            if estimated_tokens < max_tokens * 0.8:  # Leave 20% buffer
                trimmed['current_state'] = {
                    'active_files': context.get('current_state', {}).get('active_files', [])[:5],
                    'metrics': context.get('current_state', {}).get('metrics', {})
                }
                
            return trimmed
            
        except Exception as e:
            logger.error(f"Error trimming context: {e}")
            return context
            
    def start_monitoring(self):
        """Start monitoring the project for context optimization"""
        if self.is_running:
            logger.warning("Context optimizer is already running")
            return
            
        self.is_running = True
        logger.info("Starting Cursor-Claude context optimizer...")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("Context optimizer started successfully")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("Context optimizer stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Create context snapshot
                snapshot = self.create_context_snapshot()
                if snapshot:
                    logger.info(f"Context snapshot created: {len(snapshot.active_files)} active files")
                    
                # Sleep for configured interval
                time.sleep(self.config['context_analysis_interval'])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
                
    def get_status_report(self) -> Dict[str, Any]:
        """Get current status report"""
        try:
            latest_snapshot = self.context_cache[-1] if self.context_cache else None
            
            return {
                'is_running': self.is_running,
                'project_type': self.project_intelligence.project_type if self.project_intelligence else 'unknown',
                'technologies': self.project_intelligence.main_technologies if self.project_intelligence else [],
                'last_snapshot': latest_snapshot.timestamp.isoformat() if latest_snapshot else None,
                'active_files_count': len(latest_snapshot.active_files) if latest_snapshot else 0,
                'optimization_score': self._calculate_optimization_score(latest_snapshot) if latest_snapshot else 0.0,
                'suggestions_count': len(latest_snapshot.optimization_suggestions) if latest_snapshot else 0,
                'cache_size': len(self.context_cache)
            }
            
        except Exception as e:
            logger.error(f"Error getting status report: {e}")
            return {'error': str(e)}

# CLI interface
def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor-Claude Context Optimizer')
    parser.add_argument('--project-root', default=os.getcwd(), help='Project root directory')
    parser.add_argument('--start', action='store_true', help='Start context optimizer')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--context', action='store_true', help='Get optimized context for Claude')
    parser.add_argument('--max-tokens', type=int, default=150000, help='Maximum tokens for context')
    
    args = parser.parse_args()
    
    optimizer = CursorClaudeContextOptimizer(args.project_root)
    
    if args.start:
        optimizer.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            optimizer.stop_monitoring()
    elif args.status:
        status = optimizer.get_status_report()
        print(json.dumps(status, indent=2))
    elif args.context:
        context = optimizer.get_optimized_context_for_claude(args.max_tokens)
        print(json.dumps(context, indent=2))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
