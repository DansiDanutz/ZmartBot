"""
MDC Connection Agent
Intelligent system for discovering, analyzing, and auto-connecting MDC files
Uses LLM analysis to understand service relationships and auto-inject connections
"""

import os
import re
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConnection:
    """Represents a connection between two services"""
    source_service: str
    target_service: str
    connection_type: str  # dependency, consumer, provider, event_subscriber, shared_resource
    purpose: str
    confidence: float  # 0.0 to 1.0
    auto_discovered: bool = True
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ServiceMetadata:
    """Metadata about a service extracted from MDC file"""
    name: str
    filename: str
    purpose: str
    category: str
    ports: List[int]
    endpoints: List[str]
    databases: List[str]
    events_published: List[str]
    events_subscribed: List[str]
    explicit_dependencies: List[str]
    explicit_consumers: List[str]

class MDCFileWatcher(FileSystemEventHandler):
    """Watches .cursor/rules directory for MDC file changes"""
    
    def __init__(self, agent):
        self.agent = agent
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            filename = os.path.basename(event.src_path)
            logger.info(f"MDC file modified: {filename}")
            try:
                # Use asyncio.run_coroutine_threadsafe for thread safety
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.agent.analyze_file_connections(filename), loop
                    )
                else:
                    asyncio.create_task(self.agent.analyze_file_connections(filename))
            except RuntimeError:
                # Fallback to synchronous processing
                logger.warning("No event loop running, skipping async processing")
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            filename = os.path.basename(event.src_path)
            logger.info(f"New MDC file created: {filename}")
            try:
                # Use asyncio.run_coroutine_threadsafe for thread safety
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.agent.discover_all_connections(), loop
                    )
                else:
                    asyncio.create_task(self.agent.discover_all_connections())
            except RuntimeError:
                # Fallback to synchronous processing
                logger.warning("No event loop running, skipping async processing")

class MDCConnectionAgent:
    """
    Intelligent agent for discovering and managing MDC file connections
    """
    
    def __init__(self, mdc_directory: str, openai_api_key: str = None):
        self.mdc_directory = Path(mdc_directory)
        self.openai_api_key = openai_api_key
        self.services_metadata: Dict[str, ServiceMetadata] = {}
        self.connections: Dict[str, List[ServiceConnection]] = {}
        self.observer = None
        self.is_running = False
        
        # OpenAI API key will be used when creating AsyncOpenAI client
        
        # Connection patterns for intelligent matching
        self.connection_patterns = {
            'alert_services': ['Alert', 'Notification', 'Telegram', 'Discord'],
            'data_services': ['Data', 'Market', 'Price', 'Symbol', 'Indicator'],
            'monitoring_services': ['Monitor', 'Health', 'Metrics', 'Log'],
            'infrastructure': ['Manager', 'Registry', 'Discovery', 'Gateway'],
            'trading_services': ['Trading', 'Position', 'Order', 'Risk'],
            'analytics': ['Analytics', 'Analysis', 'Report', 'Score']
        }
    
    def start_watching(self):
        """Start file system watcher"""
        if self.is_running:
            return
        
        self.observer = Observer()
        event_handler = MDCFileWatcher(self)
        self.observer.schedule(event_handler, str(self.mdc_directory), recursive=False)
        self.observer.start()
        self.is_running = True
        logger.info(f"Started watching MDC directory: {self.mdc_directory}")
    
    def stop_watching(self):
        """Stop file system watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("Stopped watching MDC directory")
    
    def get_mdc_files(self) -> List[str]:
        """Get list of all MDC files"""
        try:
            return [f.name for f in self.mdc_directory.glob("*.mdc")]
        except Exception as e:
            logger.error(f"Error getting MDC files: {e}")
            return []
    
    def read_mdc_file(self, filename: str) -> str:
        """Read content of MDC file"""
        try:
            file_path = self.mdc_directory / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return ""
    
    def extract_service_metadata(self, filename: str, content: str) -> ServiceMetadata:
        """Extract metadata from MDC file content"""
        try:
            service_name = filename.replace('.mdc', '')
            
            # Extract purpose from content
            purpose_match = re.search(r'purpose:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            purpose = purpose_match.group(1) if purpose_match else f"Manages {service_name.lower()}"
            
            # Categorize service
            category = self.categorize_service(service_name)
            
            # Extract ports
            ports = re.findall(r'port[:\s]+(\d+)', content, re.IGNORECASE)
            ports = [int(p) for p in ports]
            
            # Extract endpoints
            endpoints = re.findall(r'path:\s*["\']([^"\']+)["\']', content)
            
            # Extract databases
            databases = re.findall(r'database[s]?:\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE)
            
            # Extract events
            events_published = re.findall(r'publishes:[\s\S]*?name:\s*["\']([^"\']+)["\']', content)
            events_subscribed = re.findall(r'subscribes:[\s\S]*?name:\s*["\']([^"\']+)["\']', content)
            
            # Extract explicit dependencies and consumers
            explicit_deps = re.findall(r'depends?.*?service:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            explicit_consumers = re.findall(r'consumers?:\s*\[([^\]]+)\]', content)
            if explicit_consumers:
                explicit_consumers = [c.strip().strip('"\'') for c in explicit_consumers[0].split(',')]
            else:
                explicit_consumers = []
            
            return ServiceMetadata(
                name=service_name,
                filename=filename,
                purpose=purpose,
                category=category,
                ports=ports,
                endpoints=endpoints,
                databases=databases,
                events_published=events_published,
                events_subscribed=events_subscribed,
                explicit_dependencies=explicit_deps,
                explicit_consumers=explicit_consumers
            )
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filename}: {e}")
            return ServiceMetadata(
                name=filename.replace('.mdc', ''),
                filename=filename,
                purpose="Unknown service",
                category="Core System",
                ports=[],
                endpoints=[],
                databases=[],
                events_published=[],
                events_subscribed=[],
                explicit_dependencies=[],
                explicit_consumers=[]
            )
    
    def categorize_service(self, service_name: str) -> str:
        """Categorize service based on name patterns"""
        name_lower = service_name.lower()
        
        for category, patterns in self.connection_patterns.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    category_map = {
                        'alert_services': 'Trading & Alerts',
                        'data_services': 'Data & Analytics', 
                        'monitoring_services': 'Monitoring & Security',
                        'infrastructure': 'Infrastructure',
                        'trading_services': 'Trading & Alerts',
                        'analytics': 'Data & Analytics'
                    }
                    return category_map.get(category, 'Core System')
        
        if 'ui' in name_lower or 'frontend' in name_lower or 'dashboard' in name_lower:
            return 'Frontend & UI'
        
        return 'Core System'
    
    async def discover_connections_with_llm(self, source_service: ServiceMetadata, all_services: List[ServiceMetadata]) -> List[ServiceConnection]:
        """Use LLM to discover intelligent connections between services"""
        
        if not self.openai_api_key:
            logger.warning("No OpenAI API key provided, using rule-based connections only")
            return self.discover_connections_rule_based(source_service, all_services)
        
        try:
            # Prepare service context for LLM
            source_context = f"""
Service: {source_service.name}
Purpose: {source_service.purpose}
Category: {source_service.category}
Ports: {source_service.ports}
Endpoints: {source_service.endpoints}
Databases: {source_service.databases}
Events Published: {source_service.events_published}
Events Subscribed: {source_service.events_subscribed}
"""
            
            available_services = "\n".join([
                f"- {s.name}: {s.purpose} (Category: {s.category})"
                for s in all_services if s.name != source_service.name
            ])
            
            prompt = f"""
You are an expert system architect analyzing a ZmartBot crypto trading system. 
Analyze the source service and suggest intelligent connections to other services.

SOURCE SERVICE:
{source_context}

AVAILABLE SERVICES:
{available_services}

Based on the source service's purpose, category, and functionality, suggest connections to other services.
Consider these connection types:
1. DEPENDENCY: Services this service needs to function
2. CONSUMER: Services that use this service's outputs
3. PROVIDER: Services that provide data/functionality to this service
4. EVENT_SUBSCRIBER: Services this service should listen to for events
5. SHARED_RESOURCE: Services that share databases, queues, or resources

Respond in JSON format:
{{
  "connections": [
    {{
      "target_service": "service_name",
      "connection_type": "dependency|consumer|provider|event_subscriber|shared_resource",
      "purpose": "Why this connection makes sense",
      "confidence": 0.9
    }}
  ]
}}

Focus on logical, necessary connections based on the service architecture.
"""
            
            # Initialize OpenAI client with explicit configuration
            client_config = {
                "api_key": self.openai_api_key,
                "timeout": 30.0
            }
                
            client = openai.AsyncOpenAI(**client_config)
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            connections = []
            
            for conn_data in result.get("connections", []):
                connection = ServiceConnection(
                    source_service=source_service.name,
                    target_service=conn_data["target_service"],
                    connection_type=conn_data["connection_type"],
                    purpose=conn_data["purpose"],
                    confidence=float(conn_data["confidence"]),
                    auto_discovered=True
                )
                connections.append(connection)
            
            logger.info(f"LLM discovered {len(connections)} connections for {source_service.name}")
            return connections
            
        except Exception as e:
            logger.error(f"Error using LLM for connection discovery: {e}")
            return self.discover_connections_rule_based(source_service, all_services)
    
    def discover_connections_rule_based(self, source_service: ServiceMetadata, all_services: List[ServiceMetadata]) -> List[ServiceConnection]:
        """Discover connections using rule-based logic"""
        connections = []
        
        for target_service in all_services:
            if target_service.name == source_service.name:
                continue
            
            # Rule 1: Alert services depend on data services
            if 'alert' in source_service.name.lower():
                if any(pattern in target_service.name.lower() for pattern in ['data', 'market', 'price']):
                    connections.append(ServiceConnection(
                        source_service=source_service.name,
                        target_service=target_service.name,
                        connection_type="dependency",
                        purpose="Alert services need market data for triggering",
                        confidence=0.8
                    ))
            
            # Rule 2: UI services consume backend services
            if source_service.category == 'Frontend & UI':
                if target_service.category in ['Data & Analytics', 'Trading & Alerts']:
                    connections.append(ServiceConnection(
                        source_service=source_service.name,
                        target_service=target_service.name,
                        connection_type="consumer",
                        purpose="Frontend displays data from backend services",
                        confidence=0.7
                    ))
            
            # Rule 3: Shared database connections
            common_dbs = set(source_service.databases) & set(target_service.databases)
            if common_dbs:
                connections.append(ServiceConnection(
                    source_service=source_service.name,
                    target_service=target_service.name,
                    connection_type="shared_resource",
                    purpose=f"Both services use shared databases: {', '.join(common_dbs)}",
                    confidence=0.9
                ))
            
            # Rule 4: Event-based connections
            for event in source_service.events_published:
                if event in target_service.events_subscribed:
                    connections.append(ServiceConnection(
                        source_service=source_service.name,
                        target_service=target_service.name,
                        connection_type="event_subscriber",
                        purpose=f"Target service subscribes to {event} event",
                        confidence=0.95
                    ))
        
        logger.info(f"Rule-based discovery found {len(connections)} connections for {source_service.name}")
        return connections
    
    async def analyze_all_services(self) -> Dict[str, ServiceMetadata]:
        """Analyze all MDC files and extract service metadata"""
        mdc_files = self.get_mdc_files()
        services_metadata = {}
        
        for filename in mdc_files:
            content = self.read_mdc_file(filename)
            metadata = self.extract_service_metadata(filename, content)
            services_metadata[metadata.name] = metadata
        
        self.services_metadata = services_metadata
        logger.info(f"Analyzed {len(services_metadata)} services")
        return services_metadata
    
    async def discover_all_connections(self) -> Dict[str, List[ServiceConnection]]:
        """Discover all possible connections between services"""
        logger.info("Starting comprehensive connection discovery...")
        
        # First analyze all services
        await self.analyze_all_services()
        all_services = list(self.services_metadata.values())
        
        # Discover connections for each service
        all_connections = {}
        
        for service_name, service_metadata in self.services_metadata.items():
            logger.info(f"Discovering connections for {service_name}...")
            connections = await self.discover_connections_with_llm(service_metadata, all_services)
            all_connections[service_name] = connections
        
        self.connections = all_connections
        logger.info(f"Connection discovery complete. Found connections for {len(all_connections)} services")
        return all_connections
    
    async def analyze_file_connections(self, filename: str) -> List[ServiceConnection]:
        """Analyze connections for a specific file"""
        content = self.read_mdc_file(filename)
        service_metadata = self.extract_service_metadata(filename, content)
        
        # Get all other services if not already loaded
        if not self.services_metadata:
            await self.analyze_all_services()
        
        all_services = list(self.services_metadata.values())
        connections = await self.discover_connections_with_llm(service_metadata, all_services)
        
        self.connections[service_metadata.name] = connections
        return connections
    
    def format_connections_for_mdc(self, connections: List[ServiceConnection]) -> str:
        """Format connections as MDC YAML sections"""
        if not connections:
            return ""
        
        # Group connections by type
        dependencies = [c for c in connections if c.connection_type == "dependency"]
        consumers = [c for c in connections if c.connection_type == "consumer"] 
        providers = [c for c in connections if c.connection_type == "provider"]
        events = [c for c in connections if c.connection_type == "event_subscriber"]
        shared = [c for c in connections if c.connection_type == "shared_resource"]
        
        sections = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sections.append(f"## Auto-Generated Connections (Updated: {timestamp})")
        
        if dependencies:
            sections.append("\ndependencies:")
            sections.append("  requires:")
            for dep in dependencies:
                sections.append(f'    - service: "{dep.target_service}"')
                sections.append(f'      type: "data_source"')
                sections.append(f'      purpose: "{dep.purpose}"')
                sections.append(f'      confidence: {dep.confidence}')
        
        if consumers:
            sections.append("\nconsumers:")
            consumer_list = [f'"{c.target_service}"' for c in consumers]
            sections.append(f"  - {', '.join(consumer_list)}")
        
        if providers:
            sections.append("\nproviders:")
            for prov in providers:
                sections.append(f'  - service: "{prov.target_service}"')
                sections.append(f'    purpose: "{prov.purpose}"')
        
        if events:
            sections.append("\nevents:")
            sections.append("  subscribes_to:")
            for event in events:
                sections.append(f'    - service: "{event.target_service}"')
                sections.append(f'      purpose: "{event.purpose}"')
        
        if shared:
            sections.append("\nshared_resources:")
            for res in shared:
                sections.append(f'  - service: "{res.target_service}"')
                sections.append(f'    type: "database_shared"')
                sections.append(f'    details: "{res.purpose}"')
        
        return "\n".join(sections) + "\n"
    
    def inject_connections_to_file(self, filename: str, connections: List[ServiceConnection]) -> bool:
        """Inject discovered connections into MDC file"""
        try:
            file_path = self.mdc_directory / filename
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove existing auto-generated connections
            content = re.sub(
                r'## Auto-Generated Connections.*?(?=##|\Z)', 
                '', 
                content, 
                flags=re.DOTALL
            )
            
            # Format new connections
            connections_yaml = self.format_connections_for_mdc(connections)
            
            # Inject at the end of file
            updated_content = content.rstrip() + "\n\n" + connections_yaml
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"Injected {len(connections)} connections into {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error injecting connections into {filename}: {e}")
            return False
    
    async def auto_connect_service(self, filename: str) -> Dict[str, Any]:
        """Auto-connect a specific service (triggered by UI button)"""
        try:
            logger.info(f"Auto-connecting service: {filename}")
            
            # Discover connections for this service
            connections = await self.analyze_file_connections(filename)
            
            # Inject connections into file
            success = self.inject_connections_to_file(filename, connections)
            
            return {
                "success": success,
                "filename": filename,
                "connections_found": len(connections),
                "connections": [asdict(c) for c in connections],
                "message": f"Auto-connected {len(connections)} services to {filename}"
            }
            
        except Exception as e:
            logger.error(f"Error auto-connecting {filename}: {e}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e)
            }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about discovered connections"""
        total_connections = sum(len(conns) for conns in self.connections.values())
        
        return {
            "total_services": len(self.services_metadata),
            "total_connections": total_connections,
            "services_with_connections": len([s for s in self.connections.values() if s]),
            "average_connections": total_connections / max(len(self.services_metadata), 1),
            "connection_types": self._count_connection_types(),
            "last_analysis": datetime.now().isoformat()
        }
    
    def _count_connection_types(self) -> Dict[str, int]:
        """Count connections by type"""
        type_counts = {}
        for connections in self.connections.values():
            for conn in connections:
                type_counts[conn.connection_type] = type_counts.get(conn.connection_type, 0) + 1
        return type_counts

# Global agent instance
mdc_agent = None

def get_mdc_agent() -> MDCConnectionAgent:
    """Get or create global MDC agent instance"""
    global mdc_agent
    if mdc_agent is None:
        # Get OpenAI key from environment or config
        openai_key = os.getenv('OPENAI_API_KEY')
        mdc_directory = "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
        mdc_agent = MDCConnectionAgent(mdc_directory, openai_key)
        mdc_agent.start_watching()
    return mdc_agent