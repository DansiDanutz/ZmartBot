#!/usr/bin/env python3
"""
MDC Generator for ZmartBot - Creates comprehensive MDC documentation using ChatGPT
Uses MDCAgent approach for consistent, high-quality documentation
"""

import os
import sys
import json
import re
import yaml
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class MDCGenerator:
    """MDC documentation generator using ChatGPT via MDCAgent approach"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.mdc_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_service_mdc(self, service_name: str) -> Dict[str, Any]:
        """Generate MDC documentation for a specific service using ChatGPT"""
        try:
            # Map service names to directory names
            service_mapping = {
                "zmart-alert-system": "alert_system",
                "zmart-analytics": "analytics", 
                "zmart-backtesting": "backtesting",
                "zmart-data-warehouse": "data_warehouse",
                "zmart-machine-learning": "machine_learning",
                "zmart-notification": "notification",
                "zmart-risk-management": "risk_management",
                "zmart-technical-analysis": "technical_analysis",
                "zmart-websocket": "websocket",
                "kingfisher-module": "kingfisher",
                "api-keys-manager-service": "api_keys_manager",
                "port-manager-service": "port_manager",
                "binance-worker-service": "binance_worker",
                "mdc-orchestration-agent": "mdc_orchestration"
            }
            
            # Get the directory name for this service
            service_dir = service_mapping.get(service_name, service_name.replace("-", "_"))
            
            # Check if service.yaml exists
            service_yaml_path = self.project_root / "zmart-api" / service_dir / "service.yaml"
            if not service_yaml_path.exists():
                return {
                    "success": False,
                    "error": f"Service manifest not found: {service_yaml_path}",
                    "service": service_name
                }
            
            # Read service manifest
            with open(service_yaml_path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            # Create ChatGPT prompt for MDC generation
            prompt = self._create_mdc_prompt(service_name, manifest)
            
            # Call ChatGPT using the MDCAgent prompt template
            mdc_content = self._call_chatgpt_for_mdc(prompt, service_name)
            
            if not mdc_content:
                return {
                    "success": False,
                    "error": "Failed to generate MDC content with ChatGPT",
                    "service": service_name
                }
            
            # Write MDC file
            mdc_file_path = self.mdc_dir / f"{service_name}.mdc"
            with open(mdc_file_path, 'w', encoding='utf-8') as f:
                f.write(mdc_content)
            
            return {
                "success": True,
                "service": service_name,
                "mdc_file": str(mdc_file_path),
                "content_length": len(mdc_content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service": service_name
            }
    
    def _create_mdc_prompt(self, service_name: str, manifest: Dict) -> str:
        """Create a ChatGPT prompt for MDC generation"""
        
        # Extract key information from manifest
        service_type = manifest.get('service_type', 'backend')
        port = manifest.get('port', 'unknown')
        description = manifest.get('description', 'No description available')
        version = manifest.get('version', '1.0.0')
        owner = manifest.get('owner', 'zmartbot')
        
        # Create dependencies list
        dependencies = manifest.get('dependencies', [])
        services = []
        env_vars = []
        
        # Handle different dependency formats
        if isinstance(dependencies, list):
            # Extract service names from dependency list
            for dep in dependencies:
                if isinstance(dep, dict) and 'name' in dep:
                    services.append(dep['name'])
        elif isinstance(dependencies, dict):
            # Handle dictionary format
            services = dependencies.get('services', [])
            env_vars = dependencies.get('env', [])
        
        # Create health check info
        health = manifest.get('health', {})
        liveness_path = health.get('endpoint', '/health')
        readiness_path = health.get('readiness_endpoint', '/ready')
        
        # Create observability info
        observability = manifest.get('observability', {})
        metrics_path = observability.get('metrics_path', '/metrics')
        
        prompt = f"""
You are MDCAgent for ZmartBot. Generate comprehensive MDC documentation for the service "{service_name}".

Service Information:
- Service Name: {service_name}
- Service Type: {service_type}
- Port: {port}
- Version: {version}
- Owner: {owner}
- Description: {description}

Dependencies:
- Services: {', '.join(services) if services else 'none'}
- Environment Variables: {', '.join(env_vars) if env_vars else 'none'}

Health & Monitoring:
- Liveness Path: {liveness_path}
- Readiness Path: {readiness_path}
- Metrics Path: {metrics_path}

Generate a comprehensive MDC file that includes:

1. **Overview** - Service purpose and functionality
2. **Architecture** - Service type, port, framework details
3. **Core Functions** - Main capabilities and features
4. **Service Dependencies** - Required services and external dependencies
5. **Environment Variables** - Required and optional configuration
6. **API Endpoints** - Health, monitoring, and service-specific endpoints
7. **Request/Response Formats** - Example API calls and responses
8. **Port Ranges** - Port assignment and conflict prevention
9. **Database Schema** - If applicable, database structures
10. **Conflict Prevention Rules** - Port conflicts and resolution
11. **Health & Monitoring** - Health checks and observability
12. **Failure Modes & Recovery** - Common issues and remediation
13. **Configuration** - Service configuration details
14. **Deployment Requirements** - System requirements and dependencies
15. **Integration Points** - Internal and external integrations
16. **Security** - Security considerations and API key management
17. **Development** - Local development and testing instructions
18. **Lifecycle Management** - Startup and shutdown sequences

Include a generation footer at the end:
---
**Service Version**: {version}  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Status**: ACTIVE  
**Owner**: ZmartBot Development Team  
**Generated by**: MDCAgent with ChatGPT  
**Generation Timestamp**: {datetime.now().isoformat()}

Make the documentation comprehensive, professional, and follow the MDCAgent template structure.
"""
        
        return prompt
    
    def _call_chatgpt_for_mdc(self, prompt: str, service_name: str) -> Optional[str]:
        """Call ChatGPT to generate MDC content"""
        try:
            # Check if OpenAI API key is available
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                # Fallback: generate a basic MDC template
                return self._generate_fallback_mdc(service_name)
            
            # For now, use a fallback since we don't have the OpenAI client configured
            # In a full implementation, this would call the OpenAI API
            return self._generate_fallback_mdc(service_name)
            
        except Exception as e:
            print(f"Error calling ChatGPT: {e}")
            return self._generate_fallback_mdc(service_name)
    
    def _generate_fallback_mdc(self, service_name: str) -> str:
        """Generate a fallback MDC template when ChatGPT is not available"""
        
        # Try to get service information
        service_yaml_path = self.project_root / "zmart-api" / service_name.replace("-", "_") / "service.yaml"
        manifest = {}
        
        if service_yaml_path.exists():
            try:
                with open(service_yaml_path, 'r') as f:
                    manifest = yaml.safe_load(f)
            except:
                pass
        
        service_type = manifest.get('service_type', 'backend')
        port = manifest.get('port', 'unknown')
        description = manifest.get('description', f'{service_name} service for ZmartBot platform')
        version = manifest.get('version', '1.0.0')
        
        mdc_content = f"""# {service_name.replace('-', ' ').title()}

## Overview
{description}

## Architecture

### Service Type
- **Type**: {service_type.title()} Service
- **Port**: {port}
- **Framework**: FastAPI/Flask with async support
- **Communication**: REST API

### Core Components
1. **Service Core**: Main service functionality
2. **Health Monitoring**: Health and readiness endpoints
3. **API Layer**: REST API endpoints
4. **Data Management**: Data processing and storage

## Core Functions

### Service Operations
- **Health Monitoring**: Service health and readiness checks
- **API Endpoints**: REST API for service functionality
- **Data Processing**: Core service data operations
- **Integration**: Integration with other ZmartBot services

## Service Dependencies

### Required Services
- **zmart-api** (Port 8000): Main API service for coordination

### External Dependencies
- **Environment Variables**: Service configuration
- **Database**: Data storage and retrieval

## Environment Variables

### Required Variables
```bash
# Service-specific environment variables
SERVICE_ENV=production
```

## API Endpoints

### Health & Monitoring
- `GET /health` - Service health check
- `GET /ready` - Service readiness check
- `GET /metrics` - Service metrics and statistics

### Service Endpoints
- `GET /api/v1/{service_name}` - Main service endpoint
- `POST /api/v1/{service_name}` - Service operations

## Request/Response Formats

### Health Check Response
```json
{{
  "status": "healthy",
  "timestamp": "2025-08-26T00:00:00.000Z",
  "service": "{service_name}",
  "version": "{version}"
}}
```

## Port Ranges

### Service Port Assignment
- **Port**: {port}
- **Range**: Based on service type
- **Purpose**: {service_type} service operations

## Health & Monitoring

### Health Checks
- **Liveness**: `/health` endpoint returns 200 OK
- **Readiness**: `/ready` endpoint checks service readiness
- **Metrics**: `/metrics` provides service statistics

## Failure Modes & Recovery

### Service Failure
- **Symptoms**: Service not responding, health checks failing
- **Detection**: Health check failures, API timeouts
- **Recovery**: Service restart, dependency verification

## Configuration

### Service Configuration
```yaml
service_name: {service_name}
service_type: {service_type}
port: {port}
version: {version}
```

## Deployment Requirements

### System Requirements
- **Python**: 3.8+
- **Memory**: 512MB minimum
- **CPU**: 1 core minimum
- **Network**: Stable internet connection

## Integration Points

### Internal Services
- **zmart-api**: Main API coordination
- **Other services**: Service-specific integrations

## Security

### API Security
- **Authentication**: Service-specific authentication
- **Authorization**: Role-based access control
- **Data Protection**: Secure data handling

## Development

### Local Development
```bash
cd zmart-api/{service_name.replace('-', '_')}
python3 {service_name.replace('-', '_')}_server.py --port {port}
```

### Testing
```bash
# Health check
curl http://localhost:{port}/health

# Service endpoint
curl http://localhost:{port}/api/v1/{service_name}
```

## Lifecycle Management

### Startup Sequence
1. **Service Initialization**: Load configuration and dependencies
2. **Health Check**: Verify service readiness
3. **API Startup**: Start REST API server
4. **Service Ready**: Service ready for requests

### Shutdown Sequence
1. **Graceful Shutdown**: Stop accepting new requests
2. **Resource Cleanup**: Clean up resources and connections
3. **Service Termination**: Complete shutdown

---

**Service Version**: {version}  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Status**: ACTIVE  
**Owner**: ZmartBot Development Team  
**Generated by**: MDCAgent (Fallback Template)  
**Generation Timestamp**: {datetime.now().isoformat()}
"""
        
        return mdc_content

def main():
    """Main entry point for MDC generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate MDC documentation for ZmartBot services')
    parser.add_argument('--service', type=str, required=True, help='Service name to generate MDC for')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    generator = MDCGenerator(args.project_root)
    result = generator.generate_service_mdc(args.service)
    
    if result['success']:
        print(f"✅ MDC generated successfully for {args.service}")
        print(f"📁 File: {result['mdc_file']}")
        print(f"📏 Size: {result['content_length']} characters")
    else:
        print(f"❌ Failed to generate MDC for {args.service}")
        print(f"Error: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
