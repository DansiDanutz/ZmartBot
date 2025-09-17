#!/usr/bin/env python3
"""
MDC Agent - Enhanced Automated MDC File Generation with Description, Triggers, Requirements
Monitors Python files and generates comprehensive MDC documentation with AI assistance
"""

import os
import re
import ast
import json
import time
import sqlite3
import asyncio
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from database.service_lifecycle_manager import ServiceLifecycleManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMDCTemplate:
    """Enhanced MDC template generator with Description, Triggers, and Requirements"""
    
    def __init__(self):
        self.templates = {
            'backend': self.backend_template,
            'agent': self.agent_template,
            'orchestration': self.orchestration_template,
            'database': self.database_template,
            'frontend': self.frontend_template,
            'integration': self.integration_template
        }
    
    def analyze_python_file(self, file_path: str) -> Dict:
        """Analyze Python file to extract metadata for template generation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for analysis
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Could not parse {file_path} - syntax errors")
                return self.basic_analysis(file_path, content)
            
            file_name = os.path.basename(file_path)
            analysis = {
                'file_path': file_path,
                'file_name': file_name,
                'service_name': self.extract_service_name(file_path),
                'imports': self.extract_imports(tree),
                'classes': self.extract_classes(tree),
                'functions': self.extract_functions(tree),
                'dependencies': self.extract_dependencies(content),
                'service_type': self.determine_service_type(content, tree),
                'port': self.extract_port_info(content),
                'description': self.generate_description(file_path, content),
                'triggers': self.generate_triggers(content, tree),
                'requirements': self.generate_requirements(content, tree),
                'has_main': '__name__ == "__main__"' in content,
                'has_fastapi': 'FastAPI' in content or 'fastapi' in content.lower(),
                'has_flask': 'Flask' in content or 'flask' in content.lower(),
                'has_database': any(db in content.lower() for db in ['sqlite', 'database', 'db']),
                'has_api': any(api in content.lower() for api in ['api', 'endpoint', 'route']),
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return self.basic_analysis(file_path, "")
    
    def basic_analysis(self, file_path: str, content: str) -> Dict:
        """Fallback basic analysis when AST parsing fails"""
        service_name = self.extract_service_name(file_path)
        file_name = os.path.basename(file_path)
        return {
            'file_path': file_path,
            'file_name': file_name,
            'service_name': service_name,
            'imports': [],
            'classes': [],
            'functions': [],
            'dependencies': [],
            'service_type': self.determine_service_type_basic(content),
            'port': self.extract_port_info(content),
            'description': f"Core service component of the ZmartBot ecosystem.",
            'triggers': ["System initialization", "External requests", "Scheduled tasks"],
            'requirements': ["Service implementation complete", "Health monitoring configured", "Documentation updated"],
            'has_main': '__name__ == "__main__"' in content,
            'has_fastapi': 'FastAPI' in content,
            'has_flask': 'Flask' in content,
            'has_database': 'database' in content.lower(),
            'has_api': 'api' in content.lower(),
        }
    
    def extract_service_name(self, file_path: str) -> str:
        """Extract service name from file path"""
        name = os.path.basename(file_path).replace('.py', '')
        # Keep underscores for compatibility, but ensure consistent naming
        service_name = name.replace('_server', '').replace('_service', '')
        # For test files, use the base name without modifications
        if 'test' in name.lower():
            return name
        return service_name
    
    def extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    
    def extract_classes(self, tree: ast.AST) -> List[str]:
        """Extract class names from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes
    
    def extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function names from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        return functions
    
    def extract_dependencies(self, content: str) -> List[str]:
        """Extract likely dependencies from content analysis"""
        deps = []
        dep_patterns = {
            'fastapi': ['fastapi', 'uvicorn'],
            'flask': ['flask'],
            'database': ['sqlite3', 'sqlalchemy', 'database'],
            'redis': ['redis'],
            'websocket': ['websocket', 'socketio'],
            'requests': ['requests', 'httpx'],
            'openai': ['openai', 'chatgpt']
        }
        
        content_lower = content.lower()
        for category, patterns in dep_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                deps.append(category)
        
        return deps
    
    def determine_service_type(self, content: str, tree: ast.AST) -> str:
        """Determine service type from analysis"""
        content_lower = content.lower()
        
        # Check for specific patterns
        if any(pattern in content_lower for pattern in ['fastapi', 'flask', 'uvicorn']):
            return 'backend'
        elif any(pattern in content_lower for pattern in ['agent', 'ai', 'chatgpt', 'openai']):
            return 'agent'
        elif any(pattern in content_lower for pattern in ['orchestration', 'workflow', 'master']):
            return 'orchestration'
        elif any(pattern in content_lower for pattern in ['database', 'sqlite', 'db']):
            return 'database'
        elif any(pattern in content_lower for pattern in ['frontend', 'react', 'vue', 'angular']):
            return 'frontend'
        elif any(pattern in content_lower for pattern in ['integration', 'connector', 'bridge']):
            return 'integration'
        else:
            return 'backend'  # Default
    
    def determine_service_type_basic(self, content: str) -> str:
        """Basic service type determination for fallback"""
        content_lower = content.lower()
        if 'fastapi' in content_lower or 'flask' in content_lower:
            return 'backend'
        elif 'agent' in content_lower:
            return 'agent'
        elif 'orchestration' in content_lower:
            return 'orchestration'
        else:
            return 'backend'
    
    def extract_port_info(self, content: str) -> Optional[int]:
        """Extract port number from content"""
        port_patterns = [
            r'port["\s]*[:=]["\s]*(\d+)',
            r'PORT["\s]*[:=]["\s]*(\d+)',
            r'\.run\([^)]*port["\s]*=[\s]*(\d+)',
            r'host["\s]*=.*port["\s]*=[\s]*(\d+)'
        ]
        
        for pattern in port_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def generate_description(self, file_path: str, content: str) -> str:
        """Generate intelligent description based on file analysis"""
        service_name = self.extract_service_name(file_path)
        content_lower = content.lower()
        
        # Analyze content for specific functionality
        if 'fastapi' in content_lower and 'database' in content_lower:
            return f"FastAPI-based {service_name} service providing database operations and API endpoints."
        elif 'agent' in content_lower and 'ai' in content_lower:
            return f"AI-powered {service_name} agent providing intelligent automation and decision-making."
        elif 'orchestration' in content_lower:
            return f"Orchestration {service_name} service managing workflow coordination and service lifecycle."
        elif 'dashboard' in content_lower or 'ui' in content_lower:
            return f"Dashboard {service_name} service providing user interface and visualization capabilities."
        elif 'websocket' in content_lower:
            return f"Real-time {service_name} service providing WebSocket communication and data streaming."
        elif 'database' in content_lower:
            return f"Database {service_name} service managing data persistence and query operations."
        else:
            return f"Core {service_name} service component providing essential functionality for the ZmartBot ecosystem."
    
    def generate_triggers(self, content: str, tree: ast.AST) -> List[str]:
        """Generate intelligent triggers based on file analysis"""
        content_lower = content.lower()
        triggers = []
        
        # Analyze for trigger patterns
        if 'fastapi' in content_lower or '@app.' in content:
            triggers.append("**API endpoint requests**")
        if 'schedule' in content_lower or 'cron' in content_lower:
            triggers.append("**Scheduled execution**")
        if 'websocket' in content_lower:
            triggers.append("**WebSocket connections**")
        if 'database' in content_lower or 'sqlite' in content_lower:
            triggers.append("**Database events**")
        if 'file' in content_lower and ('watch' in content_lower or 'monitor' in content_lower):
            triggers.append("**File system changes**")
        if 'workflow' in content_lower:
            triggers.append("**Workflow transitions**")
        if '__name__ == "__main__"' in content:
            triggers.append("**System startup**")
        if 'health' in content_lower:
            triggers.append("**Health check requests**")
        
        # Default triggers if none detected
        if not triggers:
            triggers = ["**System initialization**", "**External requests**", "**Scheduled tasks**"]
        
        return triggers[:5]  # Limit to 5 triggers
    
    def generate_requirements(self, content: str, tree: ast.AST) -> List[str]:
        """Generate intelligent requirements based on file analysis"""
        content_lower = content.lower()
        requirements = []
        
        # Analyze for requirement patterns
        if 'port' in content_lower or 'fastapi' in content_lower:
            requirements.append("✅ **Unique port assignment**")
        if 'database' in content_lower or 'sqlite' in content_lower:
            requirements.append("✅ **Database connectivity**")
        if 'passport' in content_lower:
            requirements.append("✅ **Valid service passport**")
        if 'mdc' in content_lower or 'documentation' in content_lower:
            requirements.append("✅ **Complete MDC documentation**")
        if 'health' in content_lower:
            requirements.append("✅ **Health endpoint implementation**")
        if 'orchestration' in content_lower:
            requirements.append("✅ **Master Orchestration integration**")
        if 'api' in content_lower:
            requirements.append("✅ **API endpoint configuration**")
        if 'test' in content_lower:
            requirements.append("✅ **Test coverage implementation**")
        
        # Default requirements if none detected
        if not requirements:
            requirements = [
                "✅ **Service implementation complete**",
                "✅ **Health monitoring configured**",
                "✅ **Documentation updated**"
            ]
        
        return requirements[:6]  # Limit to 6 requirements
    
    def backend_template(self, analysis: Dict) -> str:
        """Enhanced backend service template with Description, Triggers, Requirements"""
        service_name = analysis['service_name']
        port_info = f"Port: {analysis['port']}" if analysis['port'] else "Port: To be assigned"
        
        return f"""# {service_name.title()}.mdc
> Type: backend | Version: 1.0.0 | Owner: zmartbot | {port_info}

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} backend service providing comprehensive functionality within the ecosystem architecture.

## Critical Functions
- **API Management**: RESTful endpoint handling and request processing
- **Data Processing**: Business logic implementation and data transformation
- **Service Integration**: Communication with other ZmartBot services
- **Health Monitoring**: System health checks and status reporting

## Architecture & Integration
- **Service Type:** backend
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'To be determined'}
- **Env Vars:** To be configured
- **Lifecycle:** start=`python3 {analysis['file_name']}` | stop=`pkill -f {os.path.basename(analysis['file_path'])}` | migrate=`n/a`

## API Endpoints
*Endpoints to be documented during implementation*

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** To be configured
- **Readiness:** To be configured
- **Timeouts:** startup_grace=30s, http_timeout=30s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **WorkflowService**: Service lifecycle integration
- **Port Manager**: Port assignment and management
- **Service Registry**: Service registration and discovery

## Notes
- Service implementation follows ZmartBot backend architecture standards
- All API endpoints require proper authentication and validation
- Health monitoring is mandatory for production deployment

---

**This service provides essential backend functionality for the ZmartBot ecosystem.**
"""
    
    def agent_template(self, analysis: Dict) -> str:
        """Enhanced agent service template"""
        service_name = analysis['service_name']
        port_info = f"Port: {analysis['port']}" if analysis['port'] else "Port: 8951"
        
        return f"""# {service_name.title()}Agent.mdc
> Type: agent | Version: 1.0.0 | Owner: zmartbot | {port_info}

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} agent providing intelligent automation and decision-making capabilities within the ecosystem.

## Critical Functions
- **AI Processing**: Intelligent analysis and decision making
- **Automation**: Automated task execution and workflow management
- **Integration**: Seamless integration with ZmartBot services
- **Learning**: Adaptive learning and improvement capabilities

## Architecture & Integration
- **Service Type:** agent
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'AI-API, workflow-engine'}
- **Env Vars:** AI_API_KEY, AGENT_CONFIG_PATH
- **Lifecycle:** start=`python3 {analysis['file_name']}` | stop=`pkill -f {analysis['file_name']}` | migrate=`python3 setup_agent.py`

## API Endpoints
### Agent Control
- `POST /api/agent/start` - Start agent operations
- `POST /api/agent/stop` - Stop agent operations
- `GET /api/agent/status` - Get agent status
- `POST /api/agent/configure` - Update agent configuration

### AI Operations
- `POST /api/ai/analyze` - Perform AI analysis
- `GET /api/ai/results` - Get analysis results
- `POST /api/ai/learn` - Update learning model

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** http://127.0.0.1:{analysis['port'] or 8951}/health
- **Readiness:** http://127.0.0.1:{analysis['port'] or 8951}/api/agent/status
- **Timeouts:** startup_grace=45s, http_timeout=60s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **WorkflowService**: Agent lifecycle management
- **Master Orchestration Agent**: Decision coordination
- **AI Services**: Machine learning and analysis capabilities

## Notes
- Agent requires AI API credentials for operation
- Learning capabilities improve over time with usage
- Agent integrates with Master Orchestration for optimal decisions

---

**This agent provides intelligent automation for the ZmartBot ecosystem.**
"""
    
    def orchestration_template(self, analysis: Dict) -> str:
        """Enhanced orchestration service template"""
        service_name = analysis['service_name']
        port_info = f"Port: {analysis['port']}" if analysis['port'] else "Port: 8950"
        
        return f"""# {service_name.title()}Orchestration.mdc
> Type: orchestration | Version: 1.0.0 | Owner: zmartbot | {port_info}

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} orchestration service managing workflow coordination and service lifecycle within the ecosystem.

## Critical Functions
- **Workflow Management**: Service workflow coordination and execution
- **Lifecycle Control**: Service startup, shutdown, and transition management
- **Service Coordination**: Inter-service communication and dependency management
- **Decision Making**: Orchestration decisions based on system state

## Architecture & Integration
- **Service Type:** orchestration
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'workflow-engine, service-registry'}
- **Env Vars:** ORCHESTRATION_CONFIG, SERVICE_REGISTRY_URL
- **Lifecycle:** start=`python3 {analysis['file_name']}` | stop=`pkill -f {analysis['file_name']}` | migrate=`python3 setup_orchestration.py`

## API Endpoints
### Workflow Control
- `POST /api/workflow/start` - Start workflow execution
- `POST /api/workflow/stop` - Stop workflow execution
- `GET /api/workflow/status` - Get workflow status
- `POST /api/workflow/transition` - Execute service transition

### Service Management
- `GET /api/services/all` - Get all managed services
- `POST /api/services/register` - Register new service
- `DELETE /api/services/{{service_id}}` - Unregister service

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** http://127.0.0.1:{analysis['port'] or 8950}/health
- **Readiness:** http://127.0.0.1:{analysis['port'] or 8950}/api/workflow/status
- **Timeouts:** startup_grace=30s, http_timeout=30s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **Service Registry**: Service discovery and registration
- **WorkflowService**: Workflow validation and requirements
- **Master Orchestration Agent**: High-level orchestration coordination

## Notes
- Orchestration service is critical for system stability
- All service transitions must be validated before execution
- Service coordinates with Master Orchestration Agent for decisions

---

**This orchestration service ensures coordinated operation of the ZmartBot ecosystem.**
"""
    
    def database_template(self, analysis: Dict) -> str:
        """Enhanced database service template"""
        service_name = analysis['service_name']
        port_info = f"Port: {analysis['port']}" if analysis['port'] else "Port: 8900"
        
        return f"""# {service_name.title()}Database.mdc
> Type: database | Version: 1.0.0 | Owner: zmartbot | {port_info}

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} database service providing data persistence and query operations for the ecosystem.

## Critical Functions
- **Data Storage**: Persistent data storage and management
- **Query Processing**: Database query execution and optimization  
- **Data Integrity**: Data validation and consistency enforcement
- **Backup Management**: Database backup and recovery operations

## Architecture & Integration
- **Service Type:** database
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'sqlite3, database-engine'}
- **Env Vars:** DATABASE_PATH, BACKUP_PATH, DB_CONFIG
- **Lifecycle:** start=`python3 {analysis['file_name']}` | stop=`pkill -f {analysis['file_name']}` | migrate=`python3 migrate_database.py`

## API Endpoints
### Database Operations
- `GET /api/db/health` - Database health check
- `POST /api/db/query` - Execute database query
- `POST /api/db/transaction` - Execute database transaction
- `GET /api/db/schema` - Get database schema

### Data Management
- `POST /api/data/insert` - Insert data records
- `PUT /api/data/update` - Update data records
- `DELETE /api/data/delete` - Delete data records
- `GET /api/data/select` - Select data records

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** http://127.0.0.1:{analysis['port'] or 8900}/health
- **Readiness:** http://127.0.0.1:{analysis['port'] or 8900}/api/db/health
- **Timeouts:** startup_grace=45s, http_timeout=30s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **Service Registry**: Database service registration
- **Backup Service**: Database backup and recovery
- **Monitoring Service**: Database performance monitoring

## Notes
- Database service requires proper backup configuration
- All database operations should be logged for audit purposes
- Service provides critical data persistence for the ecosystem

---

**This database service provides essential data management for the ZmartBot ecosystem.**
"""
    
    def frontend_template(self, analysis: Dict) -> str:
        """Enhanced frontend service template"""
        service_name = analysis['service_name']
        port_info = f"Port: {analysis['port']}" if analysis['port'] else "Port: 3000"
        
        return f"""# {service_name.title()}Frontend.mdc
> Type: frontend | Version: 1.0.0 | Owner: zmartbot | {port_info}

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} frontend service providing user interface and visualization capabilities.

## Critical Functions
- **User Interface**: Interactive user interface components
- **Data Visualization**: Charts, graphs, and dashboard displays
- **User Experience**: Responsive design and user interaction handling
- **API Integration**: Frontend communication with backend services

## Architecture & Integration
- **Service Type:** frontend
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'react, api-client'}
- **Env Vars:** REACT_APP_API_URL, FRONTEND_CONFIG
- **Lifecycle:** start=`npm start` | stop=`pkill -f frontend` | migrate=`npm install`

## API Integration
### Backend Communication
- API endpoint connections to backend services
- Real-time data updates via WebSocket
- Authentication and authorization handling

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** http://127.0.0.1:{analysis['port'] or 3000}/health
- **Readiness:** http://127.0.0.1:{analysis['port'] or 3000}/
- **Timeouts:** startup_grace=30s, http_timeout=10s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **Backend API**: Data and functionality access
- **Authentication Service**: User authentication and session management
- **WebSocket Service**: Real-time data updates

## Notes
- Frontend service requires backend API connectivity
- User authentication is required for protected features
- Service provides responsive design for all device types

---

**This frontend service provides user interface capabilities for the ZmartBot ecosystem.**
"""
    
    def integration_template(self, analysis: Dict) -> str:
        """Enhanced integration service template"""
        service_name = analysis['service_name']
        
        return f"""# {service_name.title()}Integration.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Port: To be assigned

## Purpose
{analysis['description']}

## Description
{analysis['description']}

## Overview
ZmartBot {service_name} integration service providing connectivity and data exchange between systems.

## Critical Functions
- **System Integration**: Connecting external systems and services
- **Data Translation**: Format conversion and data mapping
- **Protocol Handling**: Communication protocol management
- **Error Recovery**: Integration failure handling and recovery

## Architecture & Integration
- **Service Type:** integration
- **Dependencies:** {', '.join(analysis['dependencies']) if analysis['dependencies'] else 'external-api, data-mapper'}
- **Env Vars:** INTEGRATION_CONFIG, EXTERNAL_API_KEYS
- **Lifecycle:** start=`python3 {analysis['file_name']}` | stop=`pkill -f {analysis['file_name']}` | migrate=`python3 setup_integration.py`

## API Endpoints
### Integration Control
- `POST /api/integration/start` - Start integration processes
- `POST /api/integration/stop` - Stop integration processes
- `GET /api/integration/status` - Get integration status
- `POST /api/integration/sync` - Force data synchronization

## Triggers
{chr(10).join(f"- {trigger}" for trigger in analysis['triggers'])}

## Health & Readiness
- **Liveness:** To be configured
- **Readiness:** To be configured
- **Timeouts:** startup_grace=45s, http_timeout=60s

## Requirements
{chr(10).join(f"- {req}" for req in analysis['requirements'])}

## Integration Dependencies
- **External APIs**: Third-party service connectivity
- **Data Processing**: Data transformation and validation
- **Error Handling**: Integration failure management

## Notes
- Integration service requires external API credentials
- Data synchronization should be monitored for consistency
- Service provides critical connectivity for ecosystem integration

---

**This integration service enables external system connectivity for the ZmartBot ecosystem.**
"""
    
    def generate_mdc(self, analysis: Dict) -> str:
        """Generate MDC content using appropriate template"""
        service_type = analysis['service_type']
        template_func = self.templates.get(service_type, self.templates['backend'])
        return template_func(analysis)

class PythonFileWatcher(FileSystemEventHandler):
    """File system watcher for Python files"""
    
    def __init__(self, mdc_agent):
        self.mdc_agent = mdc_agent
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"🔍 New Python file detected: {event.src_path}")
            self.mdc_agent.process_new_python_file(event.src_path)

class MDCAgent:
    """Enhanced MDC Agent with comprehensive template generation"""
    
    def __init__(self, port: int = 8951):
        self.port = port
        self.app = FastAPI(title="MDC Agent", version="1.0.0")
        self.template_generator = EnhancedMDCTemplate()
        self.observer = Observer()
        self.watch_directories = [
            "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/",
            "/Users/dansidanutz/Desktop/ZmartBot/services/",
            "/Users/dansidanutz/Desktop/ZmartBot/core/",
            "/Users/dansidanutz/Desktop/ZmartBot/agents/"
        ]
        
        # Initialize Service Lifecycle Manager for dynamic validation
        self.lifecycle_manager = ServiceLifecycleManager()
        self.exclude_patterns = [
            "*/venv/*", "*/node_modules/*", "*/__pycache__/*",
            "*/test_*.py", "*_test.py", "*/tests/*",
            "*/backup*", "*/tmp/*"
        ]
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "MDC Agent", "version": "1.0.0"}
        
        @self.app.post("/api/mdc/generate")
        async def generate_mdc(request: dict):
            """Generate MDC file for specific Python file"""
            try:
                python_file = request.get('python_file')
                if not python_file or not os.path.exists(python_file):
                    raise HTTPException(status_code=400, detail="Python file not found")
                
                result = self.process_new_python_file(python_file)
                return {"status": "success", "result": result}
                
            except Exception as e:
                logger.error(f"Error generating MDC: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/discovery/scan")
        async def scan_for_files():
            """Manual scan for Python files without MDC"""
            try:
                found_files = self.scan_for_unmdc_files()
                return {"status": "success", "found_files": found_files, "count": len(found_files)}
                
            except Exception as e:
                logger.error(f"Error scanning files: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/discovery/watch-status")
        async def get_watch_status():
            """Get file watcher status"""
            return {
                "status": "active" if self.observer.is_alive() else "inactive",
                "watch_directories": self.watch_directories,
                "exclude_patterns": self.exclude_patterns
            }
        
        @self.app.get("/api/lifecycle/validate")
        async def validate_lifecycle_integrity():
            """Validate service lifecycle integrity using dynamic manager"""
            try:
                validation_report = self.lifecycle_manager.validate_system_integrity()
                return validation_report
            except Exception as e:
                logger.error(f"Error validating lifecycle integrity: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/lifecycle/counts")
        async def get_dynamic_lifecycle_counts():
            """Get dynamic service lifecycle counts with duplicate detection"""
            try:
                unique_counts = self.lifecycle_manager.get_unique_service_counts()
                services_by_level = self.lifecycle_manager.get_all_services_by_level()
                duplicates = self.lifecycle_manager.find_duplicate_services()
                
                return {
                    "unique_counts": unique_counts,
                    "raw_counts": {
                        "discovery_raw": len(services_by_level['discovery']),
                        "passport_raw": len(services_by_level['passport']),
                        "certificate_raw": len(services_by_level['certificate'])
                    },
                    "violations": {
                        "has_duplicates": bool(duplicates),
                        "duplicates": duplicates,
                        "violation_count": sum(len(v) for v in duplicates.values())
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error getting dynamic lifecycle counts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def should_generate_mdc(self, python_file_path: str) -> bool:
        """Check if MDC should be generated for this Python file"""
        # Check if MDC file already exists
        mdc_path = python_file_path.replace('.py', '.mdc').replace('/zmart-api/', '/.cursor/rules/')
        if os.path.exists(mdc_path):
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.replace('*', '') in python_file_path:
                return False
        
        # Check file size
        if os.path.getsize(python_file_path) < 100:
            return False
        
        # Check for meaningful content
        try:
            with open(python_file_path, 'r') as f:
                content = f.read()
                if 'if __name__ == "__main__"' in content:
                    return True
                if any(indicator in content for indicator in ['FastAPI', 'Flask', 'class ', 'def ']):
                    return True
        except:
            return False
        
        return False
    
    def process_new_python_file(self, python_file_path: str) -> Dict:
        """Process new Python file and generate MDC"""
        try:
            if not self.should_generate_mdc(python_file_path):
                logger.info(f"⏭️ Skipping MDC generation for {python_file_path}")
                return {"status": "skipped", "reason": "Does not meet generation criteria"}
            
            logger.info(f"📝 Generating MDC for {python_file_path}")
            
            # Analyze Python file
            analysis = self.template_generator.analyze_python_file(python_file_path)
            
            # Generate MDC content
            mdc_content = self.template_generator.generate_mdc(analysis)
            
            # Determine MDC file path
            service_name = analysis['service_name']
            mdc_filename = f"{service_name}.mdc"
            mdc_path = f"/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/{mdc_filename}"
            
            # Write MDC file
            with open(mdc_path, 'w', encoding='utf-8') as f:
                f.write(mdc_content)
            
            logger.info(f"✅ Generated MDC file: {mdc_path}")
            
            # Register with discovery database
            self.register_with_discovery(analysis, mdc_path)
            
            return {
                "status": "generated",
                "python_file": python_file_path,
                "mdc_file": mdc_path,
                "service_name": service_name,
                "service_type": analysis['service_type']
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process {python_file_path}: {e}")
            return {"status": "failed", "error": str(e)}
    
    def register_with_discovery(self, analysis: Dict, mdc_path: str):
        """Register service with discovery database via WorkflowService"""
        try:
            logger.info(f"📋 Registering {analysis['service_name']} with WorkflowService discovery system")
            
            # Prepare service data for WorkflowService
            service_data = {
                "service_name": analysis['service_name'],
                "python_file": analysis['file_path'],
                "mdc_file": mdc_path,
                "service_type": analysis['service_type'],
                "port": analysis.get('port'),
                "has_main": analysis.get('has_main', False),
                "has_fastapi": analysis.get('has_fastapi', False),
                "has_database": analysis.get('has_database', False),
                "dependencies": analysis.get('dependencies', []),
                "action": "mdc_generated",
                "ready_for_discovery": True,
                "level": 1,
                "status": "DISCOVERED"
            }
            
            # Call WorkflowService API to trigger transition
            workflow_response = self.trigger_workflow_service(service_data)
            
            if workflow_response.get('success', False):
                logger.info(f"✅ Successfully registered {analysis['service_name']} with WorkflowService")
                
                # Also register directly with discovery database
                discovery_response = self.register_with_discovery_database(service_data)
                
                if discovery_response:
                    logger.info(f"✅ Service {analysis['service_name']} registered in discovery database")
                else:
                    logger.warning(f"⚠️ Failed to register in discovery database, but WorkflowService succeeded")
            else:
                logger.error(f"❌ Failed to register with WorkflowService: {workflow_response}")
                
        except Exception as e:
            logger.error(f"Failed to register with discovery: {e}")
    
    def trigger_workflow_service(self, service_data: Dict) -> Dict:
        """Trigger WorkflowService to handle new service registration"""
        try:
            workflow_url = "http://127.0.0.1:8950/api/workflow/trigger-transition"
            
            logger.info(f"🔄 Calling WorkflowService at {workflow_url}")
            
            response = requests.post(
                workflow_url,
                json=service_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ WorkflowService response: {result}")
                return {"success": True, "data": result}
            else:
                logger.error(f"❌ WorkflowService error {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to WorkflowService. Is it running on port 8950?")
            return {"success": False, "error": "WorkflowService not available"}
        except requests.exceptions.Timeout:
            logger.error("❌ WorkflowService request timed out")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Error calling WorkflowService: {e}")
            return {"success": False, "error": str(e)}
    
    def register_with_discovery_database(self, service_data: Dict) -> bool:
        """Register service directly with discovery database as backup"""
        try:
            discovery_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
            
            # Create discovery database if it doesn't exist
            if not os.path.exists(discovery_db_path):
                self.create_discovery_database(discovery_db_path)
            
            conn = sqlite3.connect(discovery_db_path)
            cursor = conn.cursor()
            
            # Check if service already exists
            cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", 
                          (service_data['service_name'],))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                # Insert new service
                cursor.execute("""
                    INSERT INTO discovery_services 
                    (service_name, service_type, python_file_path, mdc_file_path, port, 
                     has_mdc_file, has_python_file, status, discovered_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 1, 1, 'DISCOVERED', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    service_data['service_name'],
                    service_data['service_type'],
                    service_data['python_file'],
                    service_data['mdc_file'],
                    service_data.get('port')
                ))
                
                conn.commit()
                logger.info(f"✅ Inserted {service_data['service_name']} into discovery database")
                
                # Validate lifecycle integrity after discovery insertion
                try:
                    validation_report = self.lifecycle_manager.validate_system_integrity()
                    if validation_report['integrity_status'] == 'VIOLATIONS_FOUND':
                        logger.warning(f"⚠️ Lifecycle violations detected after adding {service_data['service_name']}: {validation_report['duplicates']}")
                    else:
                        logger.info(f"✅ Lifecycle integrity maintained after discovery insertion")
                except Exception as e:
                    logger.error(f"❌ Failed to validate lifecycle integrity: {e}")
                
            else:
                logger.info(f"ℹ️ Service {service_data['service_name']} already exists in discovery database")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register with discovery database: {e}")
            return False
    
    def create_discovery_database(self, db_path: str):
        """Create discovery database with proper schema"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discovery_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    service_type TEXT DEFAULT 'backend',
                    python_file_path TEXT,
                    mdc_file_path TEXT,
                    port INTEGER,
                    has_mdc_file BOOLEAN DEFAULT 0,
                    has_python_file BOOLEAN DEFAULT 1,
                    status TEXT DEFAULT 'DISCOVERED',
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Created discovery database at {db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create discovery database: {e}")
    
    def scan_for_unmdc_files(self) -> List[str]:
        """Scan for Python files without corresponding MDC files"""
        unmdc_files = []
        
        for watch_dir in self.watch_directories:
            if not os.path.exists(watch_dir):
                continue
                
            for root, dirs, files in os.walk(watch_dir):
                for file in files:
                    if file.endswith('.py'):
                        python_file_path = os.path.join(root, file)
                        if self.should_generate_mdc(python_file_path):
                            unmdc_files.append(python_file_path)
        
        return unmdc_files
    
    def start_file_watcher(self):
        """Start file system watcher"""
        logger.info("🔍 Starting file system watcher...")
        
        event_handler = PythonFileWatcher(self)
        
        for watch_dir in self.watch_directories:
            if os.path.exists(watch_dir):
                self.observer.schedule(event_handler, watch_dir, recursive=True)
                logger.info(f"📂 Watching directory: {watch_dir}")
            else:
                logger.warning(f"⚠️ Watch directory not found: {watch_dir}")
        
        self.observer.start()
        logger.info("✅ File watcher started successfully")
    
    def stop_file_watcher(self):
        """Stop file system watcher"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("⏹️ File watcher stopped")
    
    def run(self):
        """Run the MDC Agent service"""
        logger.info(f"🚀 Starting Enhanced MDC Agent on port {self.port}")
        
        # Start file watcher
        self.start_file_watcher()
        
        # Start FastAPI server
        try:
            uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        finally:
            self.stop_file_watcher()
            logger.info("✅ MDC Agent shutdown complete")

if __name__ == "__main__":
    agent = MDCAgent()
    agent.run()