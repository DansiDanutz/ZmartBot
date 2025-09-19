# Services Domain Context

## ServiceRegistry
**File**: .cursor/rules/ServiceRegistry.mdc
**Relevance**: 0
**Size**: 5842 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | @agent: ServiceRegistryAgent | ```bash | ``` | ---
**Compressed**: 

---

## PortManager
**File**: .cursor/rules/PortManager.mdc
**Relevance**: 0
**Size**: 18937 bytes

**Summary**: @datasource: PortRegistry | ## 🤖 MCP (Model Context Protocol) Integration | ### **MCP Server Pairing** | - **Design Integration**: Seamless integration with UI design workflows | ```bash
**Key Info**: application | str | (8200, 8299), | (8100, 8199),

---

## ServiceDiscovery
**File**: .cursor/rules/ServiceDiscovery.mdc
**Relevance**: 0
**Size**: 27121 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | @agent: ServiceDiscoveryAgent
**Key Info**: application | - **`/api/analyzer-pairs`**: View all 15-minute analysis results | Access Winners Database | COMPLETE | ACTIVE

---

## NewService
**File**: .cursor/rules/NewService.mdc
**Relevance**: 0
**Size**: 26340 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | ```bash | ``` | --- | - **MANDATORY MDC**: Every .py file MUST have an associated MDC file
**Key Info**: application | Single source of truth to integrate any new service into ZmartBot — deterministically, safely, and repeatably. | 8200–8299 | API Services (MainAPIServer, API-Manager, etc.)

---

## PortManagerDatabase
**File**: .cursor/rules/PortManagerDatabase.mdc
**Relevance**: 0
**Size**: 17983 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | @datasource: PortRegistry | ```bash | ``` | --- | - **Type**: SQLite database | ```sql | id INTEG...
**Key Info**: str | Service | Port 8000 - FastAPI server

---

## integration-ServiceDiscovery-SmartContextOptimizer
**File**: .cursor/rules/integration/winners/integration-ServiceDiscovery-SmartContextOptimizer.mdc
**Relevance**: 0
**Size**: 3642 bytes

**Content**: # integration-ServiceDiscovery-SmartContextOptimizer.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: ServiceDiscovery + SmartContextOptimizer
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of the ServiceDiscovery system and the SmartContextOptimizer has the potential to significantly improve the performance and manageability of the cryptocurrency trading platform. Despite the medium complexity, the potential benefits make this integration highly recommended.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: Service Orchestration

## Key Benefits
- Enhanced Performance: The SmartContextOptimizer can improve the performance of the ServiceDiscovery system by optimizing the generation and management of MDC files.
- Real-Time Monitoring: The Enhanced MDC Monitor component of the SmartContextOptimizer can provide real-time monitoring for the ServiceDiscovery system, improving its reliability and responsiveness.
- Improved Service Management: The integration of these two services can streamline the management of services in the cryptocurrency trading platform, making it easier to add, monitor, and optimize services.

## ...

---

## integration-PortManagerDatabase-ServiceDiscovery
**File**: .cursor/rules/integration/winners/integration-PortManagerDatabase-ServiceDiscovery.mdc
**Relevance**: 0
**Size**: 2910 bytes

**Content**: # integration-PortManagerDatabase-ServiceDiscovery.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: PortManagerDatabase + ServiceDiscovery
> Winner: Selected from automated analysis (Score: 92)

## Purpose
Given the high integration score and the significant benefits, integrating the PortManagerDatabase and ServiceDiscovery services would be highly beneficial for the cryptocurrency trading platform. While the implementation complexity is medium, the potential return on investment makes this integration worthwhile.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: Service Orchestration

## Key Benefits
- Automated service discovery and port assignment
- Centralized port management
- Improved system scalability and resilience

## Implementation Details
**Complexity Reason**: While both services have well-defined functionalities and interfaces, the integration would require careful synchronization to ensure seamless operation. Additionally, handling potential edge cases such as service crashes or network issues could increase the complexity.

## Potential Challenges
- Ensuring data consistency between the two services
- Handling service failures and network issues
- Maintaining high availability and performance during peak loads

## ...

---

## integration-orchestration_learning_summary-NewService
**File**: .cursor/rules/integration/winners/integration-orchestration_learning_summary-NewService.mdc
**Relevance**: 0
**Size**: 3838 bytes

**Content**: # integration-orchestration_learning_summary-NewService.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: orchestration_learning_summary + NewService
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of Service A and Service B is highly recommended due to the potential benefits and the high return on investment. However, careful planning and execution is required to address the potential challenges and ensure a successful integration.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: Service Orchestration

## Key Benefits
- Enhanced System Intelligence: The integration of Service A and Service B would lead to a more intelligent system. Service A's intelligent orchestration and Service B's strict service architecture workflow would ensure a well-organized, efficient, and smart system.
- Improved Security: Service A's API Keys Manager and Service B's Passport Assignment would work together to provide a robust security system, ensuring that only authorized services have access to the system.
- Real-time Data Integration: Service A's real-time market data integration would be complemented by Service B's deterministic, safe, and repeatable service integration, leading to an efficient and reliable data flow within the system.

## ...

---

## PortManagerService
**File**: .cursor/rules/discovery/integrations/PortManagerService.mdc
**Relevance**: 0
**Size**: 25338 bytes

**Summary**: # Portmanagerservice - Merged MDC Configuration | ## 🔗 Merged from 3 duplicate files | - **Master Orchestration Agent**: High-level system coordination
**Key Info**: 8610 | 8610 | orchestration | frontend | Centralized port management service that prevents conflicts and ensures proper service isolation for all ZmartBot services.

---

