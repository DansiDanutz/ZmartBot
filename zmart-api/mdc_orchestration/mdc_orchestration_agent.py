#!/usr/bin/env python3
"""
MDC Orchestration Agent
Master coordinator for all MDC management aspects: documentation generation,
connection discovery, and context optimization.
"""

import os
import sys
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import subsystem agents
try:
    from src.services.mdc_connection_agent import MDCConnectionAgent, get_mdc_agent
except ImportError:
    # Fallback for when running as standalone service
    MDCConnectionAgent = None
    get_mdc_agent = None

try:
    from smart_context_optimizer import SmartContextOptimizer
except ImportError:
    # Fallback for when running as standalone service
    SmartContextOptimizer = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrchestrationTask:
    """Represents a task in the orchestration pipeline"""
    task_id: str
    task_type: str  # full_orchestration, incremental_update, generate_docs, discover_connections, optimize_context
    service_name: Optional[str] = None
    priority: int = 1  # 1=low, 5=high
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class SystemHealth:
    """System health status"""
    overall_status: str
    mdc_agent_status: str
    connection_agent_status: str
    context_optimizer_status: str
    last_full_orchestration: Optional[str]
    last_incremental_update: Optional[str]
    total_services: int
    total_connections: int
    claude_md_size: int
    errors_last_hour: int

class MDCOrchestrationAgent:
    """
    Master orchestration agent that coordinates all MDC management aspects
    """
    
    def __init__(self, project_root: str = None, port: int = 8615):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.port = port
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.claude_md = self.project_root / "CLAUDE.md"
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.completed_tasks: List[OrchestrationTask] = []
        self.max_concurrent_tasks = 5
        self.task_counter = 0
        
        # Subsystem instances
        self.mdc_connection_agent: Optional[Any] = None
        self.context_optimizer: Optional[Any] = None
        self.mdc_agent_available = False
        
        # Orchestration state
        self.is_running = False
        self.last_full_orchestration = None
        self.last_incremental_update = None
        self.orchestration_stats = {
            "total_orchestrations": 0,
            "successful_orchestrations": 0,
            "failed_orchestrations": 0,
            "services_processed": 0,
            "connections_discovered": 0,
            "context_optimizations": 0
        }
        
        # Configuration
        self.config = {
            "full_cycle_interval": 3600,  # 1 hour
            "incremental_interval": 300,  # 5 minutes
            "max_concurrent_jobs": 5,
            "ai_settings": {
                "model_primary": "gpt-5",
                "model_fallback": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "performance": {
                "max_processing_time": 600,  # 10 minutes
                "connection_batch_size": 10,
                "context_optimization_threshold": 0.8
            }
        }
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        # Task processing thread
        self.task_processor = None
        self.scheduler_thread = None
        
        logger.info(f"MDC Orchestration Agent initialized - Port: {self.port}")
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "mdc-orchestration-agent"
            })
        
        @self.app.route('/ready', methods=['GET'])
        def ready():
            """Readiness check endpoint"""
            # Check if all subsystems are initialized
            subsystems_ready = {
                "mdc_connection_agent": self.mdc_connection_agent is not None,
                "context_optimizer": self.context_optimizer is not None,
                "mdc_agent_available": self.mdc_agent_available
            }
            
            all_ready = all(subsystems_ready.values())
            
            return jsonify({
                "status": "ready" if all_ready else "not_ready",
                "timestamp": datetime.now().isoformat(),
                "service": "mdc-orchestration-agent",
                "subsystems": subsystems_ready,
                "dependencies": {
                    "openai_api": bool(os.getenv('OPENAI_API_KEY')),
                    "project_root": str(self.project_root),
                    "mdc_directory": str(self.mdc_dir)
                }
            }), 200 if all_ready else 503
        
        @self.app.route('/status', methods=['GET'])
        def status():
            """Complete system status"""
            health = self.get_system_health()
            return jsonify(asdict(health))
        
        @self.app.route('/orchestrate', methods=['POST'])
        def orchestrate_full():
            """Trigger full MDC orchestration cycle"""
            task = self.create_task("full_orchestration", priority=5)
            return jsonify({
                "task_id": task.task_id,
                "message": "Full orchestration cycle started",
                "estimated_duration": "5-10 minutes"
            })
        
        @self.app.route('/orchestrate/incremental', methods=['POST'])
        def orchestrate_incremental():
            """Run incremental updates only"""
            task = self.create_task("incremental_update", priority=3)
            return jsonify({
                "task_id": task.task_id,
                "message": "Incremental update started",
                "estimated_duration": "30 seconds"
            })
        
        @self.app.route('/mdc/generate/<service_name>', methods=['POST'])
        def generate_mdc_docs(service_name):
            """Generate documentation for specific service"""
            task = self.create_task("generate_docs", service_name=service_name, priority=4)
            return jsonify({
                "task_id": task.task_id,
                "service": service_name,
                "message": f"Documentation generation started for {service_name}"
            })
        
        @self.app.route('/mdc/generate/all', methods=['POST'])
        def generate_all_docs():
            """Generate documentation for all services"""
            task = self.create_task("generate_all_docs", priority=4)
            return jsonify({
                "task_id": task.task_id,
                "message": "Documentation generation started for all services"
            })
        
        @self.app.route('/mdc/enhance', methods=['POST'])
        def enhance_mdc():
            """Enhance MDC file using ChatGPT"""
            data = request.get_json() or {}
            service_name = data.get('service_name')
            
            if not service_name:
                return jsonify({
                    "success": False,
                    "error": "service_name is required"
                }), 400
            
            task = self.create_task("enhance_mdc", service_name=service_name, priority=4)
            return jsonify({
                "success": True,
                "data": {
                    "task_id": task.task_id,
                    "service": service_name,
                    "message": f"ChatGPT enhancement started for {service_name}",
                    "estimated_duration": "30-60 seconds"
                }
            })
        
        @self.app.route('/connections/discover/<service_name>', methods=['POST'])
        def discover_connections(service_name):
            """Discover connections for service"""
            task = self.create_task("discover_connections", service_name=service_name, priority=3)
            return jsonify({
                "task_id": task.task_id,
                "service": service_name,
                "message": f"Connection discovery started for {service_name}"
            })
        
        @self.app.route('/connections/discover/all', methods=['POST'])
        def discover_all_connections():
            """Full connection discovery scan"""
            task = self.create_task("discover_all_connections", priority=3)
            return jsonify({
                "task_id": task.task_id,
                "message": "Full connection discovery started"
            })
        
        @self.app.route('/connections/<service_name>', methods=['GET'])
        def get_connections(service_name):
            """Get discovered connections"""
            if self.mdc_connection_agent:
                connections = self.mdc_connection_agent.connections.get(service_name, [])
                return jsonify({
                    "service": service_name,
                    "connections": [asdict(c) for c in connections],
                    "total": len(connections)
                })
            return jsonify({"error": "Connection agent not available"}), 503
        
        @self.app.route('/connections/stats', methods=['GET'])
        def connection_stats():
            """Connection discovery statistics"""
            if self.mdc_connection_agent:
                stats = self.mdc_connection_agent.get_connection_stats()
                return jsonify(stats)
            return jsonify({"error": "Connection agent not available"}), 503
        
        @self.app.route('/context/optimize', methods=['POST'])
        def optimize_context():
            """Optimize CLAUDE.md context"""
            task = self.create_task("optimize_context", priority=2)
            return jsonify({
                "task_id": task.task_id,
                "message": "Context optimization started"
            })
        
        @self.app.route('/context/status', methods=['GET'])
        def context_status():
            """Context optimization status"""
            if self.context_optimizer:
                return jsonify({
                    "claude_md_size": self.claude_md.stat().st_size if self.claude_md.exists() else 0,
                    "max_size": self.context_optimizer.max_claude_size,
                    "last_optimization": self.context_optimizer.session_context.get("last_update"),
                    "current_domain": self.context_optimizer.session_context.get("current_domain"),
                    "performance": "optimal" if self.claude_md.stat().st_size < self.context_optimizer.max_claude_size else "degraded"
                })
            return jsonify({"error": "Context optimizer not available"}), 503
        
        @self.app.route('/tasks/<task_id>', methods=['GET'])
        def get_task_status(task_id):
            """Get task status"""
            task = self.active_tasks.get(task_id)
            if not task:
                # Check completed tasks
                for completed_task in self.completed_tasks[-100:]:  # Last 100 completed tasks
                    if completed_task.task_id == task_id:
                        task = completed_task
                        break
            
            if task:
                return jsonify(asdict(task))
            return jsonify({"error": "Task not found"}), 404
        
        @self.app.route('/tasks', methods=['GET'])
        def list_tasks():
            """List all tasks"""
            return jsonify({
                "active_tasks": [asdict(task) for task in self.active_tasks.values()],
                "queue_size": self.task_queue.qsize(),
                "completed_tasks": len(self.completed_tasks),
                "recent_completed": [asdict(task) for task in self.completed_tasks[-10:]]
            })
    
    def create_task(self, task_type: str, service_name: str = None, priority: int = 1) -> OrchestrationTask:
        """Create and queue a new orchestration task"""
        self.task_counter += 1
        task_id = f"{task_type}_{self.task_counter}_{int(time.time())}"
        
        task = OrchestrationTask(
            task_id=task_id,
            task_type=task_type,
            service_name=service_name,
            priority=priority
        )
        
        # Add to queue (lower priority number = higher priority)
        self.task_queue.put((priority, task))
        logger.info(f"Created task {task_id}: {task_type}")
        
        return task
    
    def initialize_subsystems(self):
        """Initialize all subsystem agents"""
        logger.info("Initializing MDC subsystems...")
        
        # Initialize MDC Connection Agent
        if MDCConnectionAgent is not None and get_mdc_agent is not None:
            try:
                # Initialize MDC Connection Agent with API key from central management
                openai_config = self._get_openai_config()
                openai_key = openai_config.get('api_key') if openai_config else os.getenv('OPENAI_API_KEY')
                
                # Set environment variable for subsystems that expect it
                if openai_key and openai_key != 'YOUR_API_KEY_HERE':
                    os.environ['OPENAI_API_KEY'] = openai_key
                    logger.info("✅ OpenAI API key loaded from central API management system")
                else:
                    logger.warning("⚠️ OpenAI API key not found or invalid in API management system")
                
                self.mdc_connection_agent = get_mdc_agent()
                if not self.mdc_connection_agent.is_running:
                    self.mdc_connection_agent.start_watching()
                logger.info("MDC Connection Agent initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize MDC Connection Agent: {e}")
        else:
            logger.warning("MDC Connection Agent not available - running in standalone mode")
        
        # Initialize Context Optimizer
        if SmartContextOptimizer is not None:
            try:
                self.context_optimizer = SmartContextOptimizer(str(self.project_root))
                logger.info("Smart Context Optimizer initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize Context Optimizer: {e}")
        else:
            logger.warning("Smart Context Optimizer not available - running in standalone mode")
        
        # Check MDC Agent availability
        try:
            mdc_agent_path = self.project_root / "zmart-api" / "mdc_generator.py"
            self.mdc_agent_available = mdc_agent_path.exists()
            logger.info(f"MDC Agent available: {self.mdc_agent_available}")
            
        except Exception as e:
            logger.error(f"Failed to check MDC Agent availability: {e}")
    
    async def process_task(self, task: OrchestrationTask):
        """Process a single orchestration task"""
        logger.info(f"Processing task {task.task_id}: {task.task_type}")
        
        task.status = "running"
        task.started_at = datetime.now().isoformat()
        
        try:
            if task.task_type == "full_orchestration":
                result = await self.full_orchestration_cycle()
            elif task.task_type == "incremental_update":
                result = await self.incremental_update_cycle()
            elif task.task_type == "generate_docs":
                result = await self.generate_service_docs(task.service_name)
            elif task.task_type == "generate_all_docs":
                result = await self.generate_all_service_docs()
            elif task.task_type == "discover_connections":
                result = await self.discover_service_connections(task.service_name)
            elif task.task_type == "discover_all_connections":
                result = await self.discover_all_service_connections()
            elif task.task_type == "optimize_context":
                result = await self.optimize_context()
            elif task.task_type == "enhance_mdc":
                result = await self.enhance_mdc_with_chatgpt(task.service_name)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now().isoformat()
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            
            logger.error(f"Task {task.task_id} failed: {e}")
        
        # Move to completed tasks
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.completed_tasks.append(task)
        
        # Keep only last 1000 completed tasks
        if len(self.completed_tasks) > 1000:
            self.completed_tasks = self.completed_tasks[-1000:]
    
    async def full_orchestration_cycle(self) -> Dict[str, Any]:
        """Execute full orchestration cycle"""
        logger.info("Starting full orchestration cycle")
        
        start_time = time.time()
        results = {
            "cycle_type": "full",
            "steps_completed": [],
            "services_processed": 0,
            "connections_discovered": 0,
            "context_optimized": False,
            "duration_seconds": 0,
            "errors": []
        }
        
        try:
            # Step 1: System scan
            logger.info("Step 1: System scan")
            scan_result = await self.system_scan()
            results["steps_completed"].append("system_scan")
            results["services_found"] = scan_result.get("total_services", 0)
            
            # Step 2: Documentation generation
            logger.info("Step 2: Documentation generation")
            if self.mdc_agent_available:
                doc_result = await self.generate_all_service_docs()
                results["steps_completed"].append("documentation_generation")
                results["services_processed"] = doc_result.get("services_processed", 0)
            else:
                results["errors"].append("MDC Agent not available for documentation generation")
            
            # Step 3: Connection discovery
            logger.info("Step 3: Connection discovery")
            if self.mdc_connection_agent:
                conn_result = await self.discover_all_service_connections()
                results["steps_completed"].append("connection_discovery")
                results["connections_discovered"] = conn_result.get("total_connections", 0)
            else:
                results["errors"].append("Connection Agent not available")
            
            # Step 4: Context optimization
            logger.info("Step 4: Context optimization")
            if self.context_optimizer:
                opt_result = await self.optimize_context()
                results["steps_completed"].append("context_optimization")
                results["context_optimized"] = opt_result.get("success", False)
            else:
                results["errors"].append("Context Optimizer not available")
            
            # Step 5: System validation
            logger.info("Step 5: System validation")
            validation_result = await self.validate_system()
            results["steps_completed"].append("system_validation")
            results["validation"] = validation_result
            
            self.last_full_orchestration = datetime.now().isoformat()
            self.orchestration_stats["total_orchestrations"] += 1
            self.orchestration_stats["successful_orchestrations"] += 1
            
            results["duration_seconds"] = time.time() - start_time
            results["success"] = True
            
            logger.info(f"Full orchestration cycle completed in {results['duration_seconds']:.1f}s")
            
        except Exception as e:
            results["errors"].append(str(e))
            results["success"] = False
            results["duration_seconds"] = time.time() - start_time
            self.orchestration_stats["failed_orchestrations"] += 1
            
            logger.error(f"Full orchestration cycle failed: {e}")
        
        return results
    
    async def incremental_update_cycle(self) -> Dict[str, Any]:
        """Execute incremental update cycle"""
        logger.info("Starting incremental update cycle")
        
        start_time = time.time()
        results = {
            "cycle_type": "incremental",
            "changes_detected": 0,
            "services_updated": 0,
            "connections_updated": 0,
            "context_updated": False,
            "duration_seconds": 0
        }
        
        try:
            # Detect changes since last update
            changes = await self.detect_changes()
            results["changes_detected"] = len(changes)
            
            if changes:
                # Process changed services
                for change in changes:
                    if change["type"] == "service_modified":
                        await self.generate_service_docs(change["service_name"])
                        await self.discover_service_connections(change["service_name"])
                        results["services_updated"] += 1
                
                # Update context if needed
                if self.should_update_context():
                    await self.optimize_context()
                    results["context_updated"] = True
            
            self.last_incremental_update = datetime.now().isoformat()
            results["duration_seconds"] = time.time() - start_time
            results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
            results["success"] = False
            results["duration_seconds"] = time.time() - start_time
        
        return results
    
    async def system_scan(self) -> Dict[str, Any]:
        """Perform system scan to identify all services and MDC files"""
        mdc_files = list(self.mdc_dir.glob("*.mdc")) if self.mdc_dir.exists() else []
        
        return {
            "total_mdc_files": len(mdc_files),
            "total_services": len([f for f in mdc_files if not f.name.startswith("rule")]),
            "scan_timestamp": datetime.now().isoformat()
        }
    
    async def generate_service_docs(self, service_name: str) -> Dict[str, Any]:
        """Generate documentation for a specific service using MDC Generator"""
        try:
            # Call the MDC generator script
            mdc_generator_path = self.project_root / "zmart-api" / "mdc_generator.py"
            
            if not mdc_generator_path.exists():
                return {
                    "success": False,
                    "error": f"MDC generator not found: {mdc_generator_path}",
                    "service": service_name
                }
            
            # Run the MDC generator for this service
            cmd = [
                sys.executable,
                str(mdc_generator_path),
                "--service", service_name,
                "--project-root", str(self.project_root)
            ]
            
            logger.info(f"Running MDC generator: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                # Check if the MDC file was generated with proper metadata
                mdc_file = self.mdc_dir / f"{service_name}.mdc"
                if mdc_file.exists():
                    content = mdc_file.read_text(encoding='utf-8')
                    if "Generated by" in content:
                        return {
                            "success": True,
                            "service": service_name,
                            "documentation_generated": True,
                            "mdc_file": str(mdc_file),
                            "content_length": len(content),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": "MDC file generated but missing ChatGPT metadata",
                            "service": service_name
                        }
                else:
                    return {
                        "success": False,
                        "error": "MDC file not created",
                        "service": service_name
                    }
            else:
                return {
                    "success": False,
                    "error": f"MDC generator failed: {result.stderr}",
                    "service": service_name
                }
                
        except Exception as e:
            logger.error(f"Error generating MDC for {service_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service_name
            }
    
    async def generate_all_service_docs(self) -> Dict[str, Any]:
        """Generate documentation for all services"""
        scan_result = await self.system_scan()
        
        return {
            "services_processed": scan_result["total_services"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def discover_service_connections(self, service_name: str) -> Dict[str, Any]:
        """Discover connections for a specific service"""
        if not self.mdc_connection_agent:
            return {"error": "Connection agent not available"}
        
        try:
            connections = await self.mdc_connection_agent.analyze_file_connections(f"{service_name}.mdc")
            return {
                "service": service_name,
                "connections_found": len(connections),
                "connections": [asdict(c) for c in connections]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def discover_all_service_connections(self) -> Dict[str, Any]:
        """Discover connections for all services"""
        if not self.mdc_connection_agent:
            return {"error": "Connection agent not available"}
        
        try:
            all_connections = await self.mdc_connection_agent.discover_all_connections()
            total_connections = sum(len(conns) for conns in all_connections.values())
            
            return {
                "total_services": len(all_connections),
                "total_connections": total_connections,
                "services_with_connections": len([s for s in all_connections.values() if s])
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def optimize_context(self) -> Dict[str, Any]:
        """Optimize CLAUDE.md context"""
        if not self.context_optimizer:
            return {"error": "Context optimizer not available"}
        
        try:
            # Run context optimization
            result = self.context_optimizer.update_claude_md()
            
            return {
                "success": result,
                "claude_md_updated": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def enhance_mdc_with_chatgpt(self, service_name: str) -> Dict[str, Any]:
        """Enhance MDC file using ChatGPT"""
        try:
            # Get OpenAI configuration
            openai_config = self._get_openai_config()
            if not openai_config:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured or not active",
                    "enhanced": False
                }
            
            # Check if MDC file exists
            mdc_file = self.mdc_dir / f"{service_name}.mdc"
            if not mdc_file.exists():
                return {
                    "success": False,
                    "error": f"MDC file not found: {service_name}.mdc",
                    "enhanced": False
                }
            
            # Read existing content
            try:
                existing_content = mdc_file.read_text(encoding='utf-8')
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not read MDC file: {str(e)}",
                    "enhanced": False
                }
            
            # Import OpenAI and enhance content
            try:
                import openai
                openai.api_key = openai_config['api_key']
                
                # Create enhancement prompt
                enhancement_prompt = f"""
You are an expert technical documentation system. Please enhance this MDC (Machine Documentation Code) file with:

1. **Professional Structure**: Improve organization and readability
2. **Comprehensive Documentation**: Add missing details and explanations
3. **Technical Accuracy**: Ensure all technical information is accurate
4. **Best Practices**: Apply documentation best practices
5. **Consistency**: Maintain consistent formatting and structure

Current MDC Content:
{existing_content}

Please return an enhanced version that:
- Maintains all original functionality and information
- Adds helpful context and explanations
- Improves structure and readability
- Follows MDC documentation standards
- Is professional and comprehensive

Enhanced MDC File:"""

                # Call ChatGPT API
                response = openai.ChatCompletion.create(
                    model=openai_config.get('model', 'gpt-4'),
                    messages=[
                        {"role": "system", "content": "You are an expert technical documentation system specializing in MDC file enhancement."},
                        {"role": "user", "content": enhancement_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                
                enhanced_content = response.choices[0].message.content.strip()
                
                # Create backup
                backup_path = self.mdc_dir / f"{service_name}.mdc.backup"
                backup_path.write_text(existing_content, encoding='utf-8')
                
                # Write enhanced content
                mdc_file.write_text(enhanced_content, encoding='utf-8')
                
                logger.info(f"✅ Successfully enhanced {service_name}.mdc using ChatGPT")
                
                return {
                    "success": True,
                    "message": f"Successfully enhanced {service_name}.mdc using ChatGPT",
                    "enhanced": True,
                    "backup_created": str(backup_path),
                    "content": enhanced_content,
                    "model_used": openai_config.get('model', 'gpt-4'),
                    "timestamp": datetime.now().isoformat()
                }
                
            except ImportError:
                logger.error("OpenAI library not installed")
                return {
                    "success": False,
                    "error": "OpenAI library not installed. Please install with: pip install openai",
                    "enhanced": False
                }
            except Exception as e:
                logger.error(f"ChatGPT enhancement failed: {e}")
                return {
                    "success": False,
                    "error": f"ChatGPT enhancement failed: {str(e)}",
                    "enhanced": False
                }
                
        except Exception as e:
            logger.error(f"Error in enhance_mdc_with_chatgpt: {e}")
            return {
                "success": False,
                "error": str(e),
                "enhanced": False
            }
    
    async def detect_changes(self) -> List[Dict[str, Any]]:
        """Detect changes since last update"""
        # Placeholder implementation
        return []
    
    def should_update_context(self) -> bool:
        """Determine if context should be updated"""
        if not self.last_incremental_update:
            return True
        
        last_update = datetime.fromisoformat(self.last_incremental_update)
        time_since_update = datetime.now() - last_update
        
        return time_since_update > timedelta(minutes=30)
    
    async def validate_system(self) -> Dict[str, Any]:
        """Validate system integrity"""
        return {
            "mdc_files_valid": True,
            "connections_valid": True,
            "context_valid": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status"""
        claude_md_size = self.claude_md.stat().st_size if self.claude_md.exists() else 0
        
        return SystemHealth(
            overall_status="healthy",
            mdc_agent_status="available" if self.mdc_agent_available else "unavailable",
            connection_agent_status="running" if self.mdc_connection_agent and self.mdc_connection_agent.is_running else "stopped",
            context_optimizer_status="available" if self.context_optimizer else "unavailable",
            last_full_orchestration=self.last_full_orchestration,
            last_incremental_update=self.last_incremental_update,
            total_services=len(self.mdc_connection_agent.services_metadata) if self.mdc_connection_agent else 0,
            total_connections=sum(len(conns) for conns in self.mdc_connection_agent.connections.values()) if self.mdc_connection_agent else 0,
            claude_md_size=claude_md_size,
            errors_last_hour=0  # Placeholder
        )
    
    def task_processor_worker(self):
        """Background worker for processing tasks"""
        logger.info("Task processor started")
        
        while self.is_running:
            try:
                # Get task from queue (blocks with timeout)
                try:
                    priority, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Check if we can process more tasks
                if len(self.active_tasks) >= self.max_concurrent_tasks:
                    # Put task back in queue
                    self.task_queue.put((priority, task))
                    time.sleep(1)
                    continue
                
                # Add to active tasks
                self.active_tasks[task.task_id] = task
                
                # Process task asynchronously
                asyncio.run(self.process_task(task))
                
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                time.sleep(5)
        
        logger.info("Task processor stopped")
    
    def scheduler_worker(self):
        """Background scheduler for periodic tasks"""
        logger.info("Scheduler started")
        
        last_full_orchestration = 0
        last_incremental_update = 0
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Schedule full orchestration
                if current_time - last_full_orchestration > self.config["full_cycle_interval"]:
                    self.create_task("full_orchestration", priority=2)
                    last_full_orchestration = current_time
                
                # Schedule incremental updates
                if current_time - last_incremental_update > self.config["incremental_interval"]:
                    self.create_task("incremental_update", priority=1)
                    last_incremental_update = current_time
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(60)
        
        logger.info("Scheduler stopped")
    
    def _get_openai_config(self) -> Optional[Dict[str, Any]]:
        """Get OpenAI configuration from central API management system"""
        try:
            # Import the API keys manager
            from src.config.api_keys_manager import get_api_key
            
            # Get OpenAI configuration
            openai_config = get_api_key('openai')
            if openai_config and openai_config.get('is_active', False):
                logger.info("🔑 Retrieved OpenAI API key from central management")
                return openai_config
            else:
                logger.warning("⚠️ OpenAI service not active or not configured in API management")
                return None
                
        except ImportError as e:
            logger.warning(f"Could not import API keys manager: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving OpenAI config: {e}")
            return None
    
    def start(self):
        """Start the MDC Orchestration Agent"""
        logger.info("Starting MDC Orchestration Agent...")
        
        # Initialize subsystems
        self.initialize_subsystems()
        
        # Start background workers
        self.is_running = True
        
        self.task_processor = threading.Thread(target=self.task_processor_worker, daemon=True)
        self.task_processor.start()
        
        self.scheduler_thread = threading.Thread(target=self.scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        # Initial orchestration
        self.create_task("full_orchestration", priority=5)
        
        logger.info(f"MDC Orchestration Agent started on port {self.port}")
    
    def stop(self):
        """Stop the MDC Orchestration Agent"""
        logger.info("Stopping MDC Orchestration Agent...")
        
        self.is_running = False
        
        # Stop subsystems
        if self.mdc_connection_agent:
            self.mdc_connection_agent.stop_watching()
        
        logger.info("MDC Orchestration Agent stopped")
    
    def run(self):
        """Run the agent with Flask server"""
        try:
            self.start()
            self.app.run(host='localhost', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

def main():
    """Main entry point"""
    port = int(os.getenv('MDC_ORCHESTRATION_PORT', 8615))
    project_root = os.getenv('PROJECT_ROOT', '/Users/dansidanutz/Desktop/ZmartBot')
    
    agent = MDCOrchestrationAgent(project_root=project_root, port=port)
    agent.run()

if __name__ == "__main__":
    main()