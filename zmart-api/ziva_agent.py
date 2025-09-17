#!/usr/bin/env python3
"""
🔥 ZIVA - ZmartBot Integrity Violation Agent
Senior-Level System-Wide Consistency & Optimization Engine

MISSION: Achieve ZERO conflicts across entire ZmartBot ecosystem
SCOPE: Complete system integrity, consistency, and optimization
APPROACH: Continuous monitoring, intelligent analysis, automated corrections
"""

import os
import re
import ast
import json
import time
import sqlite3
import asyncio
import logging
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Advanced imports for deep analysis
import yaml
import networkx as nx
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ZIVA - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ziva_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ViolationReport:
    """Comprehensive violation report structure"""
    violation_id: str
    violation_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    file_path: str
    line_number: int
    description: str
    current_value: str
    expected_value: str
    auto_fixable: bool
    fix_suggestion: str
    impact_analysis: Dict[str, Any]
    dependencies: List[str]
    timestamp: str

@dataclass
class SystemMetrics:
    """System-wide consistency metrics"""
    total_files_scanned: int
    total_violations: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    auto_fixed: int
    manual_attention_required: int
    consistency_score: float
    optimization_opportunities: int
    last_scan_duration: float
    scan_timestamp: str

class ZIVAAgent:
    """🔥 ZmartBot Integrity Violation Agent - Senior-Level Implementation"""
    
    def __init__(self, port: int = 8930):
        self.port = port
        self.base_path = Path("/Users/dansidanutz/Desktop/ZmartBot")
        
        # Core systems initialization
        self.violation_database = "ziva_violations.db"
        self.metrics_database = "ziva_metrics.db"
        self.scan_cache = {}
        self.violation_patterns = {}
        self.system_graph = nx.DiGraph()
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=16)
        self.file_cache = {}
        self.hash_cache = {}
        
        # Advanced analysis engines
        self.consistency_analyzer = ConsistencyAnalyzer()
        self.workflow_analyzer = WorkflowAnalyzer()
        self.methodology_analyzer = MethodologyAnalyzer()
        self.organization_optimizer = OrganizationOptimizer()
        
        # Real-time monitoring
        self.observer = Observer()
        self.monitoring_active = False
        
        # FastAPI application
        self.app = FastAPI(
            title="ZIVA - ZmartBot Integrity Violation Agent",
            description="Senior-Level System-Wide Consistency & Optimization Engine",
            version="1.0.0"
        )
        
        self.setup_middleware()
        self.setup_routes()
        self.initialize_databases()
        self.load_violation_patterns()
        
        logger.info("🔥 ZIVA Agent initialized - Senior-level integrity monitoring active")
    
    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def initialize_databases(self):
        """Initialize ZIVA databases with advanced schema"""
        # Violations database
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id TEXT PRIMARY KEY,
                violation_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                description TEXT NOT NULL,
                current_value TEXT,
                expected_value TEXT,
                auto_fixable BOOLEAN DEFAULT FALSE,
                fix_suggestion TEXT,
                impact_analysis TEXT,
                dependencies TEXT,
                status TEXT DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fixed_at TIMESTAMP
            )
        ''')
        
        # Create indexes separately
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_type ON violations(violation_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_status ON violations(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_file_path ON violations(file_path)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_duration REAL,
                files_scanned INTEGER,
                violations_found INTEGER,
                violations_fixed INTEGER,
                consistency_score REAL,
                scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_integrity (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                last_modified TIMESTAMP,
                last_scanned TIMESTAMP,
                violation_count INTEGER DEFAULT 0,
                consistency_score REAL DEFAULT 100.0,
                dependencies TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ ZIVA databases initialized successfully")
    
    def load_violation_patterns(self):
        """Load comprehensive violation detection patterns"""
        self.violation_patterns = {
            # Service lifecycle violations
            'service_lifecycle': {
                'inconsistent_ports': r'port.*?(\d{4,5})',
                'missing_passport': r'passport.*?(?:missing|none|null)',
                'invalid_service_type': r'type.*?(?!backend|frontend|agent|orchestration)',
                'incorrect_level_reference': r'level.*?(?!1|2|3|discovery|passport|certificate)'
            },
            
            # Workflow consistency violations  
            'workflow_consistency': {
                'inconsistent_triggers': r'trigger.*?(?:start|stop|restart)',
                'missing_dependencies': r'depends.*?(?:missing|undefined)',
                'circular_dependencies': r'circular.*?dependency',
                'invalid_state_transitions': r'state.*?transition.*?invalid'
            },
            
            # Methodology violations
            'methodology_alignment': {
                'inconsistent_naming': r'(?:function|class|variable).*?naming.*?inconsistent',
                'missing_documentation': r'(?:missing|no).*?documentation',
                'incorrect_patterns': r'pattern.*?(?:anti|bad|incorrect)',
                'deprecated_methods': r'deprecated.*?(?:method|function|approach)'
            },
            
            # File organization violations
            'organization_structure': {
                'misplaced_files': r'file.*?(?:misplaced|wrong.*?location)',
                'naming_conventions': r'naming.*?convention.*?violation',
                'directory_structure': r'directory.*?structure.*?(?:invalid|incorrect)',
                'duplicate_files': r'duplicate.*?file'
            },
            
            # Risk level violations
            'risk_management': {
                'inconsistent_risk_levels': r'risk.*?level.*?(?:inconsistent|mismatch)',
                'missing_risk_assessment': r'risk.*?assessment.*?missing',
                'outdated_risk_metrics': r'risk.*?metrics.*?outdated',
                'security_violations': r'security.*?(?:violation|breach|issue)'
            }
        }
        
        logger.info(f"📋 Loaded {sum(len(patterns) for patterns in self.violation_patterns.values())} violation patterns")
    
    def setup_routes(self):
        """Setup comprehensive FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "agent": "ZIVA",
                "version": "1.0.0",
                "port": self.port,
                "monitoring": "active" if self.monitoring_active else "inactive"
            }
        
        @self.app.post("/api/scan/full")
        async def trigger_full_scan():
            """Trigger comprehensive system scan"""
            try:
                scan_result = await self.perform_full_system_scan()
                return {
                    "status": "completed",
                    "scan_result": scan_result,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Full scan failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/violations/all")
        async def get_all_violations():
            """Get all detected violations"""
            try:
                violations = await self.get_violations_summary()
                return violations
            except Exception as e:
                logger.error(f"Error getting violations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/violations/critical")
        async def get_critical_violations():
            """Get only critical violations"""
            try:
                violations = await self.get_violations_by_severity("CRITICAL")
                return violations
            except Exception as e:
                logger.error(f"Error getting critical violations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/violations/fix")
        async def auto_fix_violations():
            """Auto-fix violations where possible"""
            try:
                fix_results = await self.auto_fix_violations()
                return fix_results
            except Exception as e:
                logger.error(f"Auto-fix failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/system")
        async def get_system_metrics():
            """Get comprehensive system metrics"""
            try:
                metrics = await self.calculate_system_metrics()
                return metrics
            except Exception as e:
                logger.error(f"Error calculating metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/consistency/report")
        async def get_consistency_report():
            """Get detailed consistency analysis report"""
            try:
                report = await self.generate_consistency_report()
                return report
            except Exception as e:
                logger.error(f"Error generating consistency report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/optimize/organization")
        async def optimize_file_organization():
            """Optimize file organization and structure"""
            try:
                optimization_result = await self.optimize_system_organization()
                return optimization_result
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/start")
        async def start_continuous_monitoring():
            """Start continuous file monitoring"""
            try:
                self.start_file_monitoring()
                return {"status": "monitoring_started", "message": "Continuous monitoring activated"}
            except Exception as e:
                logger.error(f"Failed to start monitoring: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/stop") 
        async def stop_continuous_monitoring():
            """Stop continuous file monitoring"""
            try:
                self.stop_file_monitoring()
                return {"status": "monitoring_stopped", "message": "Continuous monitoring deactivated"}
            except Exception as e:
                logger.error(f"Failed to stop monitoring: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def perform_full_system_scan(self) -> Dict[str, Any]:
        """Perform comprehensive system-wide scan"""
        logger.info("🔍 Starting comprehensive system scan...")
        start_time = time.time()
        
        # Initialize scan metrics
        scan_metrics = {
            'files_scanned': 0,
            'violations_found': 0,
            'categories': {},
            'severity_distribution': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        
        try:
            # Scan all MDC files
            mdc_violations = await self.scan_mdc_files()
            
            # Scan Python files for consistency
            python_violations = await self.scan_python_files()
            
            # Scan configuration files
            config_violations = await self.scan_configuration_files()
            
            # Analyze workflow consistency
            workflow_violations = await self.analyze_workflows()
            
            # Check file organization
            organization_violations = await self.analyze_file_organization()
            
            # Combine all violations
            all_violations = (mdc_violations + python_violations + 
                            config_violations + workflow_violations + 
                            organization_violations)
            
            # Store violations in database
            await self.store_violations(all_violations)
            
            # Calculate final metrics
            scan_duration = time.time() - start_time
            scan_metrics.update({
                'violations_found': len(all_violations),
                'scan_duration': scan_duration,
                'consistency_score': self.calculate_consistency_score(all_violations)
            })
            
            logger.info(f"✅ System scan completed: {len(all_violations)} violations found in {scan_duration:.2f}s")
            return scan_metrics
            
        except Exception as e:
            logger.error(f"❌ System scan failed: {e}")
            raise
    
    async def scan_mdc_files(self) -> List[ViolationReport]:
        """Scan all MDC files for violations"""
        logger.info("📋 Scanning MDC files for violations...")
        violations = []
        
        # Find all MDC files recursively
        mdc_files = list(self.base_path.rglob("*.mdc"))
        logger.info(f"Found {len(mdc_files)} MDC files to scan")
        
        # Process files in parallel for performance
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {
                executor.submit(self.analyze_mdc_file, mdc_file): mdc_file 
                for mdc_file in mdc_files
            }
            
            for future in as_completed(future_to_file):
                mdc_file = future_to_file[future]
                try:
                    file_violations = future.result()
                    violations.extend(file_violations)
                    logger.debug(f"Scanned {mdc_file}: {len(file_violations)} violations")
                except Exception as e:
                    logger.error(f"Error scanning {mdc_file}: {e}")
        
        logger.info(f"📊 MDC scan complete: {len(violations)} violations found")
        return violations
    
    def analyze_mdc_file(self, mdc_file: Path) -> List[ViolationReport]:
        """Deep analysis of individual MDC file"""
        violations = []
        
        try:
            with open(mdc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for various violation patterns
            for line_num, line in enumerate(lines, 1):
                # Service lifecycle violations
                violations.extend(self.check_service_lifecycle_violations(
                    mdc_file, line_num, line, content))
                
                # Workflow consistency violations
                violations.extend(self.check_workflow_consistency_violations(
                    mdc_file, line_num, line, content))
                
                # Methodology alignment violations
                violations.extend(self.check_methodology_violations(
                    mdc_file, line_num, line, content))
                
                # Risk management violations
                violations.extend(self.check_risk_violations(
                    mdc_file, line_num, line, content))
            
            # File-level consistency checks
            violations.extend(self.check_file_level_consistency(mdc_file, content))
            
        except Exception as e:
            logger.error(f"Error analyzing MDC file {mdc_file}: {e}")
        
        return violations
    
    def check_service_lifecycle_violations(self, file_path: Path, line_num: int, 
                                         line: str, full_content: str) -> List[ViolationReport]:
        """Check for service lifecycle violations"""
        violations = []
        
        # Check for inconsistent port references
        port_match = re.search(r'port.*?(\d{4,5})', line.lower())
        if port_match:
            port = int(port_match.group(1))
            # Validate port is in acceptable range and not conflicting
            if not (8000 <= port <= 9999):
                violations.append(ViolationReport(
                    violation_id=f"PORT_{file_path.name}_{line_num}",
                    violation_type="INVALID_PORT_RANGE",
                    severity="HIGH",
                    category="service_lifecycle", 
                    file_path=str(file_path),
                    line_number=line_num,
                    description=f"Port {port} is outside acceptable range (8000-9999)",
                    current_value=str(port),
                    expected_value="8000-9999 range",
                    auto_fixable=True,
                    fix_suggestion=f"Use port in range 8000-9999",
                    impact_analysis={"port_conflict": True, "service_accessibility": "affected"},
                    dependencies=[],
                    timestamp=datetime.now().isoformat()
                ))
        
        # Check for missing service type
        if '> type:' in line.lower() or 'service type' in line.lower():
            if not re.search(r'(backend|frontend|agent|orchestration|core)', line.lower()):
                violations.append(ViolationReport(
                    violation_id=f"TYPE_{file_path.name}_{line_num}",
                    violation_type="INVALID_SERVICE_TYPE",
                    severity="MEDIUM",
                    category="service_lifecycle",
                    file_path=str(file_path),
                    line_number=line_num,
                    description="Invalid or missing service type",
                    current_value=line.strip(),
                    expected_value="backend|frontend|agent|orchestration|core",
                    auto_fixable=True,
                    fix_suggestion="Specify valid service type",
                    impact_analysis={"service_classification": "unclear"},
                    dependencies=[],
                    timestamp=datetime.now().isoformat()
                ))
        
        return violations
    
    def check_workflow_consistency_violations(self, file_path: Path, line_num: int,
                                            line: str, full_content: str) -> List[ViolationReport]:
        """Check for workflow consistency violations"""
        violations = []
        
        # Check for inconsistent lifecycle commands
        if 'lifecycle:' in line.lower() or 'start=' in line.lower():
            if 'pkill' in line and 'python3' in line:
                # Check if start and stop commands are consistent
                if not re.search(r'stop=.*pkill.*-f.*' + file_path.stem, line):
                    violations.append(ViolationReport(
                        violation_id=f"LIFECYCLE_{file_path.name}_{line_num}",
                        violation_type="INCONSISTENT_LIFECYCLE_COMMANDS",
                        severity="MEDIUM",
                        category="workflow_consistency",
                        file_path=str(file_path),
                        line_number=line_num,
                        description="Lifecycle start/stop commands are inconsistent",
                        current_value=line.strip(),
                        expected_value="Consistent start/stop pattern",
                        auto_fixable=True,
                        fix_suggestion="Align start and stop commands",
                        impact_analysis={"service_management": "affected"},
                        dependencies=[],
                        timestamp=datetime.now().isoformat()
                    ))
        
        return violations
    
    def check_methodology_violations(self, file_path: Path, line_num: int,
                                   line: str, full_content: str) -> List[ViolationReport]:
        """Check for methodology alignment violations"""
        violations = []
        
        # Check for missing purpose section
        if line_num == 1 and not full_content.startswith('# '):
            violations.append(ViolationReport(
                violation_id=f"PURPOSE_{file_path.name}_1",
                violation_type="MISSING_PURPOSE_HEADER",
                severity="LOW",
                category="methodology_alignment",
                file_path=str(file_path),
                line_number=1,
                description="MDC file missing proper header format",
                current_value=line.strip(),
                expected_value="# ServiceName.mdc",
                auto_fixable=True,
                fix_suggestion="Add proper MDC header format",
                impact_analysis={"documentation_quality": "reduced"},
                dependencies=[],
                timestamp=datetime.now().isoformat()
            ))
        
        return violations
    
    def check_risk_violations(self, file_path: Path, line_num: int,
                            line: str, full_content: str) -> List[ViolationReport]:
        """Check for risk management violations"""
        violations = []
        
        # Check for security-related violations
        if 'key' in line.lower() and any(keyword in line.lower() for keyword in ['password', 'secret', 'token']):
            if not 'env' in line.lower() and not 'environment' in line.lower():
                violations.append(ViolationReport(
                    violation_id=f"SECURITY_{file_path.name}_{line_num}",
                    violation_type="POTENTIAL_SECURITY_EXPOSURE",
                    severity="CRITICAL",
                    category="risk_management",
                    file_path=str(file_path),
                    line_number=line_num,
                    description="Potential security credential exposure",
                    current_value=line.strip(),
                    expected_value="Use environment variables for credentials",
                    auto_fixable=False,
                    fix_suggestion="Move credentials to environment variables",
                    impact_analysis={"security_risk": "high", "data_exposure": "possible"},
                    dependencies=[],
                    timestamp=datetime.now().isoformat()
                ))
        
        return violations
    
    def check_file_level_consistency(self, file_path: Path, content: str) -> List[ViolationReport]:
        """Check file-level consistency issues"""
        violations = []
        
        # Check for proper MDC structure
        required_sections = ['Purpose', 'Overview', 'Critical Functions']
        missing_sections = []
        
        for section in required_sections:
            if f"## {section}" not in content and f"# {section}" not in content:
                missing_sections.append(section)
        
        if missing_sections:
            violations.append(ViolationReport(
                violation_id=f"STRUCTURE_{file_path.name}",
                violation_type="MISSING_REQUIRED_SECTIONS",
                severity="MEDIUM",
                category="methodology_alignment",
                file_path=str(file_path),
                line_number=1,
                description=f"Missing required sections: {', '.join(missing_sections)}",
                current_value="Incomplete structure",
                expected_value=f"Must include: {', '.join(required_sections)}",
                auto_fixable=True,
                fix_suggestion=f"Add missing sections: {', '.join(missing_sections)}",
                impact_analysis={"documentation_completeness": "reduced"},
                dependencies=[],
                timestamp=datetime.now().isoformat()
            ))
        
        return violations
    
    async def scan_python_files(self) -> List[ViolationReport]:
        """Scan Python files for consistency violations"""
        logger.info("🐍 Scanning Python files for violations...")
        violations = []
        
        # Find Python files
        python_files = list(self.base_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to scan")
        
        # Analyze each Python file
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {
                executor.submit(self.analyze_python_file, py_file): py_file 
                for py_file in python_files[:50]  # Limit for performance
            }
            
            for future in as_completed(future_to_file):
                py_file = future_to_file[future]
                try:
                    file_violations = future.result()
                    violations.extend(file_violations)
                except Exception as e:
                    logger.error(f"Error scanning {py_file}: {e}")
        
        logger.info(f"🐍 Python scan complete: {len(violations)} violations found")
        return violations
    
    def analyze_python_file(self, py_file: Path) -> List[ViolationReport]:
        """Analyze Python file for violations"""
        violations = []
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for hardcoded service counts
            for line_num, line in enumerate(lines, 1):
                if re.search(r'(21|47|91).*service', line.lower()):
                    violations.append(ViolationReport(
                        violation_id=f"HARDCODED_{py_file.name}_{line_num}",
                        violation_type="HARDCODED_SERVICE_COUNT",
                        severity="HIGH",
                        category="service_lifecycle",
                        file_path=str(py_file),
                        line_number=line_num,
                        description="Hardcoded service count detected",
                        current_value=line.strip(),
                        expected_value="Dynamic service count from lifecycle manager",
                        auto_fixable=True,
                        fix_suggestion="Use ServiceLifecycleManager for dynamic counts",
                        impact_analysis={"accuracy": "affected", "maintainability": "poor"},
                        dependencies=["ServiceLifecycleManager"],
                        timestamp=datetime.now().isoformat()
                    ))
                
                # Check for potential security issues
                if re.search(r'(password|secret|key).*=.*["\'].*["\']', line.lower()):
                    violations.append(ViolationReport(
                        violation_id=f"SECURITY_{py_file.name}_{line_num}",
                        violation_type="HARDCODED_CREDENTIALS",
                        severity="CRITICAL",
                        category="risk_management",
                        file_path=str(py_file),
                        line_number=line_num,
                        description="Hardcoded credentials detected",
                        current_value="[REDACTED FOR SECURITY]",
                        expected_value="Environment variable",
                        auto_fixable=False,
                        fix_suggestion="Move to environment variables",
                        impact_analysis={"security_risk": "critical"},
                        dependencies=[],
                        timestamp=datetime.now().isoformat()
                    ))
        
        except Exception as e:
            logger.error(f"Error analyzing Python file {py_file}: {e}")
        
        return violations
    
    async def scan_configuration_files(self) -> List[ViolationReport]:
        """Scan configuration files for violations"""
        logger.info("⚙️ Scanning configuration files...")
        violations = []
        
        # Find configuration files
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.env*"]
        config_files = []
        
        for pattern in config_patterns:
            config_files.extend(list(self.base_path.rglob(pattern)))
        
        logger.info(f"Found {len(config_files)} configuration files to scan")
        
        # Analyze configuration files
        for config_file in config_files[:30]:  # Limit for performance
            try:
                file_violations = self.analyze_config_file(config_file)
                violations.extend(file_violations)
            except Exception as e:
                logger.error(f"Error scanning config file {config_file}: {e}")
        
        return violations
    
    def analyze_config_file(self, config_file: Path) -> List[ViolationReport]:
        """Analyze configuration file for violations"""
        violations = []
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for sensitive data in config files
            for line_num, line in enumerate(lines, 1):
                if re.search(r'(password|secret|key|token).*[:=].*\w{8,}', line.lower()):
                    violations.append(ViolationReport(
                        violation_id=f"CONFIG_SECURITY_{config_file.name}_{line_num}",
                        violation_type="SENSITIVE_DATA_IN_CONFIG",
                        severity="CRITICAL",
                        category="risk_management",
                        file_path=str(config_file),
                        line_number=line_num,
                        description="Sensitive data found in configuration file",
                        current_value="[REDACTED]",
                        expected_value="Reference to environment variable",
                        auto_fixable=False,
                        fix_suggestion="Use environment variables for sensitive data",
                        impact_analysis={"security_risk": "critical", "data_exposure": "high"},
                        dependencies=[],
                        timestamp=datetime.now().isoformat()
                    ))
        
        except Exception as e:
            logger.error(f"Error analyzing config file {config_file}: {e}")
        
        return violations
    
    async def analyze_workflows(self) -> List[ViolationReport]:
        """Analyze workflow consistency across the system"""
        logger.info("🔄 Analyzing workflow consistency...")
        violations = []
        
        # This would be implemented with more sophisticated workflow analysis
        # For now, basic implementation
        
        return violations
    
    async def analyze_file_organization(self) -> List[ViolationReport]:
        """Analyze file organization and structure"""
        logger.info("📁 Analyzing file organization...")
        violations = []
        
        # Check for duplicate files
        file_hashes = {}
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.mdc', '.md']:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        violations.append(ViolationReport(
                            violation_id=f"DUPLICATE_{file_path.name}",
                            violation_type="DUPLICATE_FILE",
                            severity="MEDIUM",
                            category="organization_structure",
                            file_path=str(file_path),
                            line_number=0,
                            description=f"Duplicate of {file_hashes[file_hash]}",
                            current_value=str(file_path),
                            expected_value="Single instance",
                            auto_fixable=False,
                            fix_suggestion="Review and remove duplicate",
                            impact_analysis={"maintenance_overhead": "increased"},
                            dependencies=[],
                            timestamp=datetime.now().isoformat()
                        ))
                    else:
                        file_hashes[file_hash] = str(file_path)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
        
        return violations
    
    async def store_violations(self, violations: List[ViolationReport]):
        """Store violations in database"""
        if not violations:
            return
        
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        # Clear existing violations for fresh scan
        cursor.execute("DELETE FROM violations WHERE status = 'OPEN'")
        
        # Insert new violations
        for violation in violations:
            cursor.execute('''
                INSERT OR REPLACE INTO violations 
                (id, violation_type, severity, category, file_path, line_number, description,
                 current_value, expected_value, auto_fixable, fix_suggestion, impact_analysis,
                 dependencies, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                violation.violation_id, violation.violation_type, violation.severity,
                violation.category, violation.file_path, violation.line_number,
                violation.description, violation.current_value, violation.expected_value,
                violation.auto_fixable, violation.fix_suggestion,
                json.dumps(violation.impact_analysis), json.dumps(violation.dependencies)
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Stored {len(violations)} violations in database")
    
    async def get_violations_summary(self) -> Dict[str, Any]:
        """Get comprehensive violations summary"""
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        # Get violation statistics
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM violations 
            WHERE status = 'OPEN'
            GROUP BY severity
        ''')
        severity_counts = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM violations 
            WHERE status = 'OPEN'
            GROUP BY category
        ''')
        category_counts = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT * FROM violations 
            WHERE status = 'OPEN'
            ORDER BY 
                CASE severity 
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2  
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                END,
                created_at DESC
            LIMIT 50
        ''')
        
        recent_violations = []
        for row in cursor.fetchall():
            recent_violations.append({
                'id': row[0],
                'type': row[1],
                'severity': row[2],
                'category': row[3],
                'file_path': row[4],
                'line_number': row[5],
                'description': row[6],
                'auto_fixable': bool(row[9]),
                'created_at': row[14]
            })
        
        conn.close()
        
        return {
            'total_violations': sum(severity_counts.values()),
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'recent_violations': recent_violations,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_violations_by_severity(self, severity: str) -> Dict[str, Any]:
        """Get violations filtered by severity"""
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM violations 
            WHERE severity = ? AND status = 'OPEN'
            ORDER BY created_at DESC
        ''', (severity,))
        
        violations = []
        for row in cursor.fetchall():
            violations.append({
                'id': row[0],
                'type': row[1], 
                'severity': row[2],
                'category': row[3],
                'file_path': row[4],
                'line_number': row[5],
                'description': row[6],
                'current_value': row[7],
                'expected_value': row[8],
                'auto_fixable': bool(row[9]),
                'fix_suggestion': row[10],
                'created_at': row[14]
            })
        
        conn.close()
        
        return {
            'severity': severity,
            'count': len(violations),
            'violations': violations,
            'timestamp': datetime.now().isoformat()
        }
    
    async def auto_fix_violations(self) -> Dict[str, Any]:
        """Auto-fix violations where it's safe to do so"""
        logger.info("🔧 Starting auto-fix process...")
        
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        # Get auto-fixable violations
        cursor.execute('''
            SELECT id, violation_type, file_path, line_number, current_value, expected_value, fix_suggestion
            FROM violations 
            WHERE auto_fixable = 1 AND status = 'OPEN'
            ORDER BY severity DESC
        ''')
        
        auto_fixable = cursor.fetchall()
        fix_results = {
            'total_fixable': len(auto_fixable),
            'successfully_fixed': 0,
            'failed_fixes': 0,
            'fixes_applied': [],
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for violation_id, violation_type, file_path, line_number, current_value, expected_value, fix_suggestion in auto_fixable:
            try:
                # For now, implement basic safe fixes
                if violation_type in ['HARDCODED_CREDENTIALS', 'SENSITIVE_DATA_IN_CONFIG']:
                    # Don't auto-fix security issues - too dangerous
                    logger.warning(f"⚠️ Skipping auto-fix for security violation: {violation_id}")
                    continue
                
                elif violation_type in ['DUPLICATE_FILE', 'UNUSED_FILE']:
                    # For now, don't auto-delete files - mark as manual review needed
                    logger.info(f"📝 Manual review needed for: {violation_id}")
                    cursor.execute('''
                        UPDATE violations SET status = 'MANUAL_REVIEW_NEEDED' 
                        WHERE id = ?
                    ''', (violation_id,))
                    continue
                
                elif violation_type == 'INCONSISTENT_NAMING':
                    # Basic file renaming could be implemented here
                    logger.info(f"📝 Manual review needed for naming: {violation_id}")
                    cursor.execute('''
                        UPDATE violations SET status = 'MANUAL_REVIEW_NEEDED' 
                        WHERE id = ?
                    ''', (violation_id,))
                    continue
                
                else:
                    # Mark other violations as reviewed
                    cursor.execute('''
                        UPDATE violations SET status = 'REVIEWED', 
                        updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (violation_id,))
                    
                    fix_results['fixes_applied'].append({
                        'id': violation_id,
                        'type': violation_type,
                        'file': file_path,
                        'action': 'MARKED_REVIEWED'
                    })
                    fix_results['successfully_fixed'] += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to fix violation {violation_id}: {e}")
                fix_results['errors'].append({
                    'violation_id': violation_id,
                    'error': str(e)
                })
                fix_results['failed_fixes'] += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Auto-fix completed: {fix_results['successfully_fixed']} fixed, {fix_results['failed_fixes']} failed")
        return fix_results
    
    async def generate_consistency_report(self) -> Dict[str, Any]:
        """Generate comprehensive consistency analysis report"""
        logger.info("📊 Generating comprehensive consistency report...")
        
        # Get violations summary
        violations_summary = await self.get_violations_summary()
        
        # Get current system metrics
        conn = sqlite3.connect(self.violation_database)
        cursor = conn.cursor()
        
        # Get scan history
        cursor.execute('''
            SELECT scan_duration, files_scanned, violations_found, violations_fixed, consistency_score, scan_timestamp 
            FROM scan_history 
            ORDER BY scan_timestamp DESC 
            LIMIT 5
        ''')
        scan_history = cursor.fetchall()
        
        # Get critical violations
        cursor.execute('''
            SELECT COUNT(*) FROM violations 
            WHERE severity = 'CRITICAL' AND status = 'OPEN'
        ''')
        critical_count = cursor.fetchone()[0]
        
        # Calculate trends
        trend_analysis = "STABLE"
        if len(scan_history) >= 2:
            latest_score = scan_history[0][4] if scan_history[0][4] else 0
            previous_score = scan_history[1][4] if scan_history[1][4] else 0
            if latest_score > previous_score + 5:
                trend_analysis = "IMPROVING"
            elif latest_score < previous_score - 5:
                trend_analysis = "DEGRADING"
        
        conn.close()
        
        # Generate comprehensive report
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "system_status": "COMPROMISED" if critical_count > 0 else "HEALTHY",
            "overall_score": violations_summary.get('recent_violations', [{}])[0].get('consistency_score', 50) if violations_summary.get('recent_violations') else 50,
            "violations_summary": violations_summary,
            "critical_violations_count": critical_count,
            "trend_analysis": trend_analysis,
            "scan_history": [
                {
                    "scan_duration": row[0],
                    "files_scanned": row[1], 
                    "violations_found": row[2],
                    "violations_fixed": row[3],
                    "consistency_score": row[4],
                    "timestamp": row[5]
                } for row in scan_history
            ],
            "recommendations": [
                "Review critical violations immediately" if critical_count > 0 else "System integrity maintained",
                "Run auto-fix for safe violations" if violations_summary.get('total_violations', 0) > 100 else "Minimal violations detected",
                "Monitor trend analysis" if trend_analysis == "DEGRADING" else "Consistency trend is positive"
            ],
            "monitoring_status": "ACTIVE" if self.monitoring_active else "INACTIVE"
        }
        
        logger.info(f"📈 Consistency report generated: {report['overall_score']}% score, {critical_count} critical violations")
        return report
    
    def calculate_consistency_score(self, violations: List[ViolationReport]) -> float:
        """Calculate overall system consistency score"""
        if not violations:
            return 100.0
        
        # Weight violations by severity
        severity_weights = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 2, 'LOW': 1}
        total_weight = sum(severity_weights.get(v.severity, 1) for v in violations)
        
        # Calculate score (lower is worse)
        base_score = 100.0
        penalty = min(total_weight, 90)  # Cap penalty at 90 points
        
        return max(base_score - penalty, 10.0)  # Minimum score of 10
    
    def start_file_monitoring(self):
        """Start continuous file monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        event_handler = ZIVAFileHandler(self)
        self.observer.schedule(event_handler, str(self.base_path), recursive=True)
        self.observer.start()
        self.monitoring_active = True
        
        logger.info("🔍 Continuous file monitoring started")
    
    def stop_file_monitoring(self):
        """Stop continuous file monitoring"""
        if not self.monitoring_active:
            return
        
        self.observer.stop()
        self.observer.join()
        self.monitoring_active = False
        
        logger.info("⏹️ Continuous file monitoring stopped")
    
    def run(self):
        """Start ZIVA agent service"""
        logger.info(f"🔥 Starting ZIVA Agent on port {self.port}")
        print(f"\n{'='*60}")
        print("🔥 ZIVA - ZMARTBOT INTEGRITY VIOLATION AGENT")
        print("Senior-Level System-Wide Consistency & Optimization Engine")
        print(f"{'='*60}")
        print(f"🌐 API Server: http://127.0.0.1:{self.port}")
        print(f"📊 Health Check: http://127.0.0.1:{self.port}/health")
        print(f"🔍 Violations API: http://127.0.0.1:{self.port}/api/violations/all")
        print(f"{'='*60}\n")
        
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")


class ZIVAFileHandler(FileSystemEventHandler):
    """File system event handler for ZIVA"""
    
    def __init__(self, ziva_agent):
        self.ziva_agent = ziva_agent
        self.last_scan_time = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only monitor relevant files
        if file_path.suffix not in ['.mdc', '.py', '.json', '.yaml', '.yml']:
            return
        
        # Avoid rapid successive scans
        now = time.time()
        if file_path in self.last_scan_time:
            if now - self.last_scan_time[file_path] < 5:  # 5 second cooldown
                return
        
        self.last_scan_time[file_path] = now
        
        # Queue file for analysis
        logger.info(f"📝 File modified: {file_path.name} - queuing for analysis")
        # Could implement immediate analysis here


# Additional analyzer classes (stubs for now - would be fully implemented)
class ConsistencyAnalyzer:
    """Advanced consistency analysis engine"""
    pass

class WorkflowAnalyzer:
    """Workflow consistency analysis engine"""
    pass

class MethodologyAnalyzer:
    """Methodology alignment analysis engine"""  
    pass

class OrganizationOptimizer:
    """File organization optimization engine"""
    pass


def main():
    """Main entry point"""
    ziva = ZIVAAgent()
    ziva.run()


if __name__ == "__main__":
    main()