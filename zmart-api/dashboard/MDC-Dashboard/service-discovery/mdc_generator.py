#!/usr/bin/env python3
"""
MDC File Generator for Service Discovery Recommendations
Creates complete, implementation-ready MDC files from approved AI recommendations
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class MDCFileGenerator:
    """
    Generates comprehensive MDC files for approved service integration recommendations
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.generated_dir = self.mdc_dir / "generated"
        
        # Ensure generated directory exists
        self.generated_dir.mkdir(exist_ok=True)
        
    def generate_integration_mdc(self, 
                               service_a: str, 
                               service_b: str, 
                               ai_analysis: str,
                               compatibility_score: float,
                               service_type_a: str = "unknown",
                               service_type_b: str = "unknown") -> str:
        """
        Generate complete MDC file for service integration
        """
        
        # Create integration service name
        integration_name = self._create_integration_name(service_a, service_b)
        
        # Determine port assignment
        port = self._assign_integration_port(service_type_a, service_type_b)
        
        # Parse AI analysis for structured information
        parsed_analysis = self._parse_ai_analysis(ai_analysis)
        
        # Generate comprehensive MDC content
        mdc_content = self._generate_mdc_content(
            integration_name=integration_name,
            service_a=service_a,
            service_b=service_b,
            service_type_a=service_type_a,
            service_type_b=service_type_b,
            port=port,
            compatibility_score=compatibility_score,
            parsed_analysis=parsed_analysis,
            ai_analysis=ai_analysis
        )
        
        # Write MDC file
        file_path = self._write_mdc_file(integration_name, mdc_content)
        
        return file_path
    
    def _create_integration_name(self, service_a: str, service_b: str) -> str:
        """Create a descriptive integration service name"""
        
        # Clean service names
        clean_a = re.sub(r'[^a-zA-Z0-9]', '', service_a)
        clean_b = re.sub(r'[^a-zA-Z0-9]', '', service_b)
        
        # Create integration name
        integration_name = f"{clean_a}{clean_b}Integration"
        
        return integration_name
    
    def _assign_integration_port(self, service_type_a: str, service_type_b: str) -> int:
        """Assign appropriate port based on service types"""
        
        # Port ranges for integration services
        port_ranges = {
            'api_integration': (8600, 8650),
            'database_integration': (8650, 8700),
            'frontend_integration': (3500, 3550),
            'monitoring_integration': (8750, 8800),
            'orchestration_integration': (8800, 8850),
            'general_integration': (8900, 8950)
        }
        
        # Determine integration type
        if 'api' in [service_type_a, service_type_b]:
            integration_type = 'api_integration'
        elif 'database' in [service_type_a, service_type_b]:
            integration_type = 'database_integration'
        elif 'frontend' in [service_type_a, service_type_b]:
            integration_type = 'frontend_integration'
        elif 'monitoring' in [service_type_a, service_type_b]:
            integration_type = 'monitoring_integration'
        elif 'orchestration' in [service_type_a, service_type_b]:
            integration_type = 'orchestration_integration'
        else:
            integration_type = 'general_integration'
        
        # Find available port in range
        start_port, end_port = port_ranges[integration_type]
        
        # Simple port assignment (in production, would check for conflicts)
        assigned_port = start_port + hash(f"{service_type_a}{service_type_b}") % (end_port - start_port)
        
        return assigned_port
    
    def _parse_ai_analysis(self, ai_analysis: str) -> Dict[str, Any]:
        """Parse AI analysis to extract structured information"""
        
        parsed = {
            'connection_potential': 7,  # default
            'implementation_steps': [],
            'benefits': [],
            'technical_requirements': [],
            'priority_level': 'Medium',
            'risks': [],
            'estimated_effort': 'Medium'
        }
        
        # Extract connection potential rating
        potential_match = re.search(r'[Cc]onnection [Pp]otential.*?(\d+)/10', ai_analysis)
        if potential_match:
            parsed['connection_potential'] = int(potential_match.group(1))
        
        # Extract implementation steps
        impl_section = re.search(r'Implementation Strategy.*?:(.*?)(?:\n\n|\*\*)', ai_analysis, re.DOTALL)
        if impl_section:
            steps_text = impl_section.group(1)
            steps = [step.strip() for step in re.findall(r'^\d+\.\s*(.+?)$', steps_text, re.MULTILINE)]
            parsed['implementation_steps'] = steps[:5]  # Limit to 5 steps
        
        # Extract benefits
        benefits_section = re.search(r'Benefits.*?:(.*?)(?:\n\n|\*\*)', ai_analysis, re.DOTALL)
        if benefits_section:
            benefits_text = benefits_section.group(1)
            benefits = [b.strip('- ').strip() for b in benefits_text.split('\n') if b.strip().startswith('-')]
            parsed['benefits'] = benefits[:5]
        
        # Extract technical requirements
        tech_section = re.search(r'Technical Requirements.*?:(.*?)(?:\n\n|\*\*)', ai_analysis, re.DOTALL)
        if tech_section:
            tech_text = tech_section.group(1)
            requirements = [r.strip('- ').strip() for r in tech_text.split('\n') if r.strip().startswith('-')]
            parsed['technical_requirements'] = requirements[:5]
        
        # Extract priority level
        priority_match = re.search(r'Priority Level.*?:\s*(\w+)', ai_analysis)
        if priority_match:
            parsed['priority_level'] = priority_match.group(1)
        
        # Extract risks
        risk_section = re.search(r'Risk Assessment.*?:(.*?)$', ai_analysis, re.DOTALL | re.MULTILINE)
        if risk_section:
            risk_text = risk_section.group(1)
            risks = [r.strip() for r in risk_text.split('\n') if r.strip() and not r.strip().startswith('*')]
            parsed['risks'] = risks[:3]
        
        return parsed
    
    def _generate_mdc_content(self,
                            integration_name: str,
                            service_a: str,
                            service_b: str,
                            service_type_a: str,
                            service_type_b: str,
                            port: int,
                            compatibility_score: float,
                            parsed_analysis: Dict[str, Any],
                            ai_analysis: str) -> str:
        """Generate complete MDC file content"""
        
        # Determine service category
        if 'api' in [service_type_a, service_type_b]:
            service_category = 'backend'
        elif 'frontend' in [service_type_a, service_type_b]:
            service_category = 'frontend'
        elif 'database' in [service_type_a, service_type_b]:
            service_category = 'backend'
        else:
            service_category = 'backend'
        
        # Generate implementation steps
        impl_steps = parsed_analysis.get('implementation_steps', [])
        if not impl_steps:
            impl_steps = [
                f"Create integration bridge between {service_a} and {service_b}",
                "Implement data synchronization mechanisms",
                "Add health monitoring and error handling",
                "Configure service discovery registration",
                "Deploy and test integration endpoints"
            ]
        
        # Generate benefits list
        benefits = parsed_analysis.get('benefits', [])
        if not benefits:
            benefits = [
                "Improved service coordination and data flow",
                "Enhanced system reliability and monitoring",
                "Reduced operational overhead",
                "Better resource utilization",
                "Increased system intelligence"
            ]
        
        # Generate technical requirements
        tech_requirements = parsed_analysis.get('technical_requirements', [])
        if not tech_requirements:
            tech_requirements = [
                "REST API endpoints for service communication",
                "Shared data models and serialization",
                "Health check integration",
                "Logging and monitoring infrastructure",
                "Configuration management system"
            ]
        
        # Create comprehensive MDC content
        mdc_content = f"""# {integration_name} - AI-Generated Service Integration
> Type: {service_category} | Version: 1.0.0 | Owner: zmartbot | Port: {port}

## 🤖 AI-Generated Integration Recommendation
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source Services**: {service_a} ({service_type_a}) ↔ {service_b} ({service_type_b})
**Compatibility Score**: {compatibility_score}/10
**Connection Potential**: {parsed_analysis.get('connection_potential')}/10
**Priority Level**: {parsed_analysis.get('priority_level')}

## Purpose
AI-recommended integration service bridging {service_a} and {service_b} to enhance system coordination, data flow, and operational efficiency within the ZmartBot ecosystem.

## Overview
This integration service was identified by the AI Discovery Workflow as a high-value connection opportunity. It creates intelligent communication channels between complementary services, enabling enhanced data sharing, coordinated operations, and improved system reliability.

## Critical Functions
- **Service Bridge Operations**: Seamless communication between {service_a} and {service_b}
- **Data Synchronization**: Real-time data coordination and consistency management
- **Health Monitoring**: Comprehensive monitoring of integration health and performance
- **Error Recovery**: Intelligent error handling and automatic recovery mechanisms
- **Performance Optimization**: Smart caching and request optimization

## Architecture & Integration
- **Service Type:** {service_category}
- **Dependencies:** {service_a}, {service_b}, service_registry
- **Env Vars:** SERVICE_A_URL, SERVICE_B_URL, INTEGRATION_MODE, LOG_LEVEL
- **Lifecycle:** start=`python3 {integration_name.lower()}_service.py --port {port}` | stop=`pkill -f {integration_name.lower()}` | migrate=`n/a`

## Implementation Roadmap

### Phase 1: Core Integration Setup
"""

        # Add implementation steps
        for i, step in enumerate(impl_steps, 1):
            mdc_content += f"- **Step {i}**: {step}\n"
        
        mdc_content += f"""
### Phase 2: Advanced Features
- **Intelligent Caching**: Implement smart caching based on usage patterns
- **Load Balancing**: Add load balancing for high-traffic scenarios
- **Analytics Integration**: Connect to analytics and monitoring systems
- **Security Hardening**: Implement authentication and authorization
- **Performance Tuning**: Optimize for production workloads

## Expected Benefits
"""
        
        # Add benefits
        for benefit in benefits:
            mdc_content += f"- ✅ {benefit}\n"
        
        mdc_content += f"""
## Technical Requirements
"""
        
        # Add technical requirements
        for requirement in tech_requirements:
            mdc_content += f"- 🔧 {requirement}\n"
        
        mdc_content += f"""
## API Endpoints

### GET /health
- Summary: Integration service health check
- Auth Required: No
- Responses:
  - 200: Service healthy with integration status
  - 503: Service unavailable

### POST /integrate
- Summary: Execute integration operation between services
- Auth Required: Yes
- Request Body: Integration parameters and data
- Responses:
  - 200: Integration successful
  - 400: Invalid parameters
  - 500: Integration failed

### GET /status
- Summary: Get detailed integration status and metrics
- Auth Required: No
- Responses:
  - 200: Detailed status with performance metrics

### POST /sync
- Summary: Force data synchronization between services
- Auth Required: Yes
- Responses:
  - 200: Synchronization completed
  - 500: Synchronization failed

## Health & Readiness
- Liveness: GET /health (checks integration bridge status)
- Readiness: GET /ready (validates service connections)
- Timeouts: startup_grace=45s, http_timeout=30s, integration_timeout=60s

## Observability
- Metrics: Integration success rate, response times, data flow rates
- Logs: format=json, level=info
- Tracing: Integration request tracing with correlation IDs
- Alerts: Integration failures, performance degradation, service disconnections

## Security & Compliance
- **Authentication**: Service-to-service authentication tokens
- **Authorization**: Role-based access control for integration operations
- **Data Privacy**: Sensitive data encryption in transit and at rest
- **Audit Logging**: Comprehensive audit trail for all integration operations

## Performance Characteristics
- **Throughput**: Target 1000+ requests/minute
- **Latency**: <100ms average response time
- **Availability**: 99.9% uptime target
- **Scalability**: Horizontal scaling supported

## Deployment Configuration

### Environment Variables
```bash
SERVICE_A_URL=http://localhost:{self._get_service_port(service_a)}
SERVICE_B_URL=http://localhost:{self._get_service_port(service_b)}
INTEGRATION_PORT={port}
INTEGRATION_MODE=production
LOG_LEVEL=info
HEALTH_CHECK_INTERVAL=30s
RETRY_ATTEMPTS=3
CACHE_TTL=300s
```

### Docker Configuration
```yaml
{integration_name.lower()}_integration:
  image: zmartbot/{integration_name.lower()}:latest
  ports:
    - "{port}:{port}"
  environment:
    - SERVICE_A_URL=${{SERVICE_A_URL}}
    - SERVICE_B_URL=${{SERVICE_B_URL}}
    - INTEGRATION_MODE=production
  depends_on:
    - {service_a.lower()}
    - {service_b.lower()}
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## Risk Assessment & Mitigation

### Identified Risks
"""
        
        # Add risks if available
        risks = parsed_analysis.get('risks', [
            "Service dependency failures could impact integration",
            "Network latency may affect performance",
            "Configuration complexity requires careful management"
        ])
        
        for risk in risks:
            mdc_content += f"- ⚠️ {risk}\n"
        
        mdc_content += f"""
### Mitigation Strategies
- **Circuit Breaker Pattern**: Implement circuit breakers to handle service failures
- **Graceful Degradation**: Design fallback mechanisms for service unavailability
- **Comprehensive Testing**: Extensive unit, integration, and performance testing
- **Monitoring & Alerting**: Proactive monitoring with automated alerting
- **Documentation**: Comprehensive operational documentation and runbooks

## Original AI Analysis
```
{ai_analysis}
```

## Implementation Status
- [x] **Planning Phase**: AI analysis complete, MDC file generated
- [ ] **Development Phase**: Service implementation pending
- [ ] **Testing Phase**: Integration testing required
- [ ] **Deployment Phase**: Production deployment pending
- [ ] **Monitoring Phase**: Operational monitoring setup required

## Next Steps
1. Review and approve this integration recommendation
2. Implement the integration service using this specification
3. Create comprehensive tests for the integration
4. Deploy to staging environment for validation
5. Monitor performance and optimize as needed
6. Deploy to production with full monitoring

---
*This MDC file was automatically generated by the AI Discovery Workflow system based on intelligent analysis of service compatibility and integration opportunities.*
"""
        
        return mdc_content
    
    def _get_service_port(self, service_name: str) -> str:
        """Get the port for a service (simplified - could read from actual MDC files)"""
        # This is a simplified implementation
        # In production, would read actual MDC files to get real ports
        port_mapping = {
            'AlertSystemServer': '8200',
            'ProfessionalDashboardServer': '3400',
            'KINGFISHER_AI': '8300',
            'OrchestrationStartWorkflow': '8002',
            'MDCOrchestrationAgent': '8500',
            'orchestration_learning_summary': '8501'
        }
        
        return port_mapping.get(service_name, '8XXX')
    
    def _write_mdc_file(self, integration_name: str, content: str) -> str:
        """Write MDC file to the generated directory"""
        
        filename = f"{integration_name}.mdc"
        file_path = self.generated_dir / filename
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def generate_from_winner_analysis(self, winner_analysis: Dict[str, Any]) -> str:
        """Generate MDC file from winner analysis data"""
        
        return self.generate_integration_mdc(
            service_a=winner_analysis['service_a'],
            service_b=winner_analysis['service_b'],
            ai_analysis=winner_analysis['ai_analysis'],
            compatibility_score=winner_analysis['compatibility_score'],
            service_type_a=winner_analysis.get('service_type_a', 'unknown'),
            service_type_b=winner_analysis.get('service_type_b', 'unknown')
        )
    
    def list_generated_files(self) -> List[str]:
        """List all generated MDC files"""
        
        generated_files = []
        if self.generated_dir.exists():
            for file_path in self.generated_dir.glob("*.mdc"):
                generated_files.append(str(file_path))
        
        return generated_files

def main():
    """Demo the MDC generator"""
    
    generator = MDCFileGenerator()
    
    # Demo with sample winner data
    sample_winner = {
        'service_a': 'orchestration_learning_summary',
        'service_b': 'ProfessionalDashboardServer',
        'service_type_a': 'database',
        'service_type_b': 'api',
        'compatibility_score': 9.5,
        'ai_analysis': '''
**Connection Analysis: orchestration_learning_summary ↔ ProfessionalDashboardServer**

**Connection Potential**: 8/10
These services show excellent potential for integration based on their complementary architectures.

**Implementation Strategy**:
1. Create intelligent dashboard data bridge
2. Implement orchestration intelligence API endpoints
3. Add real-time system status integration
4. Configure predictive analytics display
5. Enable smart data routing and optimization

**Benefits**:
- Enhanced dashboard intelligence with system awareness
- Real-time orchestration status visibility
- Predictive system health monitoring
- Optimized data fetching and caching
- Advanced system insights for users

**Technical Requirements**:
- REST API endpoints for orchestration data
- Real-time WebSocket connections for live updates
- Intelligent caching system
- Dashboard integration middleware
- Comprehensive error handling and recovery

**Priority Level**: High
Excellent business value with clear technical implementation path.

**Risk Assessment**: Low
Well-established integration patterns with clear architectural benefits.
        '''
    }
    
    # Generate MDC file
    file_path = generator.generate_from_winner_analysis(sample_winner)
    
    print(f"✅ Generated MDC file: {file_path}")
    print(f"📁 Generated files: {len(generator.list_generated_files())}")

if __name__ == "__main__":
    main()