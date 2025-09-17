# Core Domain Context\n\n## main\n**File**: .cursor/rules/main.mdc\n**Relevance**: 100\n**Size**: 4787 bytes\n\n**Content**: # main.mdc
> Type: service | Version: 1.0.0 | Owner: zmartbot | Status: Discovery | Level: 1
Core service component of the ZmartBot ecosystem providing essential functionality.

## ...\n\n---\n\n## MainAPIServer\n**File**: .cursor/rules/MainAPIServer.mdc\n**Relevance**: 100\n**Size**: 17881 bytes\n\n**Summary**: # 🚀 Main API Server - Zmart Trading Bot Platform Core | > Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: 8000 | - **Enhanced Development**: AI-powered code generation and optimization | ```b...\n**Key Info**: 8000 | backend | 40+ API route modules with specialized trading functionality | High-performance async API framework with comprehensive middleware stack\n\n---\n\n## rules\n**File**: .cursor/rules/rules.mdc\n**Relevance**: 80\n**Size**: 41341 bytes\n\n**Summary**: # rules.mdc | > Type: service | Version: 1.0.0 | Owner: zmartbot | Status: Discovery | Level: 1 | - **Claude Code Integration**: AI-powered rules management and optimization\n**Key Info**: service | rule | System Architecture & Service Management | 30+ endpoints for workflow validation and service management | Complete API system for workflow guidance and validation\n\n---\n\n## rule_0_mandatory\n**File**: .cursor/rules/rule_0_mandatory.mdc\n**Relevance**: 100\n**Size**: 11227 bytes\n\n**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | - **Claude Code Integration**: AI-powered rule enforcement and optimization\n**Compressed**: \n\n---\n\n## integration-rules-ServiceLog\n**File**: .cursor/rules/integration/winners/integration-rules-ServiceLog.mdc\n**Relevance**: 100\n**Size**: 4338 bytes\n\n**Content**: # integration-rules-ServiceLog.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: rules + ServiceLog
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of ServiceLog and rules service could bring significant benefits to the cryptocurrency trading platform, including enhanced system monitoring, improved service management, and automated remediation. However, the integration process would need to be carefully managed to ensure data consistency, system stability, and security. Despite the medium implementation complexity, the expected ROI is high, making the integration a worthwhile investment.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: Service orchestration would be the best integration pattern. This approach would allow the services to interact in a coordinated manner, with the ServiceLog acting as the orchestrator that triggers and manages interactions with the rules service based on log analysis results.

## ...\n\n---\n\n## integration-CryptometerService-main\n**File**: .cursor/rules/integration/winners/integration-CryptometerService-main.mdc\n**Relevance**: 100\n**Size**: 3803 bytes\n\n**Content**: # integration-CryptometerService-main.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: CryptometerService + main
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of CryptometerService with ZmartBot is highly recommended due to the significant potential benefits. However, careful planning and execution are required to address the potential challenges and ensure a successful integration.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: API Gateway Integration Pattern would be suitable as it provides a single entry point for microservices, simplifying the client-side handling and allowing for centralized management of the integrated services.

## Key Benefits
- Real-time Market Data: The integration of CryptometerService with ZmartBot would provide real-time market data, which is crucial for the AI-driven trading system.
- Enhanced Trading Decisions: The technical indicators and multi-timeframe analysis provided by CryptometerService would significantly enhance the trading decisions made by ZmartBot.
- Optimized Performance: The intelligent caching and rate limiting features of CryptometerService would optimize the performance of ZmartBot, reducing latency and improving user experience.

## ...\n\n---\n\n## gammainc_data\n**File**: .cursor/rules/discovery/libraries/gammainc_data.mdc\n**Relevance**: 100\n**Size**: 2117 bytes\n\n**Content**: # gammainc_data.mdc
> Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: None

## Purpose
Service discovered at gammainc_data.py

## Overview
Auto-discovered service managed by MDC-Dashboard system. This service was identified during automated system scanning and requires manual review and enhancement.

## Critical Functions
- Auto-discovered service functionality (requires manual documentation)
- Service integration with ZmartBot ecosystem

## Architecture & Integration
- **Service Type:** backend
- **Dependencies:** To be determined
- **Env Vars:** To be determined  
- **Lifecycle:** start=`python3 /Users/dansidanutz/Desktop/ZmartBot/zmart-api/venv/lib/python3.9/site-packages/scipy/special/_precompute/gammainc_data.py` | stop=`pkill -f gammainc_data` | migrate=`n/a`

## API Endpoints
*Endpoints to be documented during manual review*

## Health & Readiness
- Liveness: To be configured
- Readiness: To be configured
- Timeouts: startup_grace=30s, http_timeout=30s

## Observability
- Metrics: To be configured
- Logs: format=python, level=info
- Tracing: To be configured

## Performance & SLO
- Baseline p95 (ms): To be measured
- Notes: Auto-discovered service requiring performance baseline establishment

## Failure Modes & Runbooks
*To be documented during manual review*

## Dependencies & Interfaces
- **Upstream:** To be discovered
- **Downstream:** To be discovered
- **Consumers:** To be discovered

## ...\n\n---\n\n## __main__\n**File**: .cursor/rules/discovery/libraries/__main__.mdc\n**Relevance**: 100\n**Size**: 1845 bytes\n\n**Content**: # __main__.mdc
> Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: None

## Purpose
Main entry point.

## Overview
Auto-discovered service managed by MDC-Dashboard system. This service was identified during automated system scanning and requires manual review and enhancement.

## Critical Functions
- Auto-discovered service functionality (requires manual documentation)
- Service integration with ZmartBot ecosystem

## Architecture & Integration
- **Service Type:** backend
- **Dependencies:** To be determined
- **Env Vars:** To be determined  
- **Lifecycle:** start=`python3 /Users/dansidanutz/Desktop/ZmartBot/zmart-api/venv/lib/python3.9/site-packages/platformdirs/__main__.py` | stop=`pkill -f __main__` | migrate=`n/a`

## API Endpoints
*Endpoints to be documented during manual review*

## Health & Readiness
- Liveness: To be configured
- Readiness: To be configured
- Timeouts: startup_grace=30s, http_timeout=30s

## Observability
- Metrics: To be configured
- Logs: format=python, level=info
- Tracing: To be configured

## Performance & SLO
- Baseline p95 (ms): To be measured
- Notes: Auto-discovered service requiring performance baseline establishment

## Failure Modes & Runbooks
*To be documented during manual review*

## Dependencies & Interfaces
- **Upstream:** To be discovered
- **Downstream:** To be discovered
- **Consumers:** To be discovered

## Notes & Todos
- Service functionality and dependencies need documentation

## ...\n\n---\n\n## gammainc_asy\n**File**: .cursor/rules/discovery/libraries/gammainc_asy.mdc\n**Relevance**: 100\n**Size**: 1890 bytes\n\n**Content**: # gammainc_asy.mdc
> Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: None

## Purpose
a_k from DLMF 5.11.6

## Overview
Auto-discovered service managed by MDC-Dashboard system. This service was identified during automated system scanning and requires manual review and enhancement.

## Critical Functions
- Auto-discovered service functionality (requires manual documentation)
- Service integration with ZmartBot ecosystem

## Architecture & Integration
- **Service Type:** backend
- **Dependencies:** To be determined
- **Env Vars:** To be determined  
- **Lifecycle:** start=`python3 /Users/dansidanutz/Desktop/ZmartBot/zmart-api/venv/lib/python3.9/site-packages/scipy/special/_precompute/gammainc_asy.py` | stop=`pkill -f gammainc_asy` | migrate=`n/a`

## API Endpoints
*Endpoints to be documented during manual review*

## Health & Readiness
- Liveness: To be configured
- Readiness: To be configured
- Timeouts: startup_grace=30s, http_timeout=30s

## Observability
- Metrics: To be configured
- Logs: format=python, level=info
- Tracing: To be configured

## Performance & SLO
- Baseline p95 (ms): To be measured
- Notes: Auto-discovered service requiring performance baseline establishment

## Failure Modes & Runbooks
*To be documented during manual review*

## Dependencies & Interfaces
- **Upstream:** To be discovered
- **Downstream:** To be discovered
- **Consumers:** To be discovered

## Notes & Todos
- Service functionality and dependencies need documentation

## ...\n\n---\n\n## winner-backtesting_server-rule_0_mandatory-20250827-164659\n**File**: .cursor/rules/discovery/integrations/winners/winner-backtesting_server-rule_0_mandatory-20250827-164659.mdc\n**Relevance**: 100\n**Size**: 7646 bytes\n\n**Summary**: # winner-backtesting_server-rule_0_mandatory-20250827-164659.mdc | ## 🏆 WINNER INTEGRATION - Official Selection | > Type: integration-winner | Version: 1.0.0 | Owner: zmartbot | Status: SELECTED\n**Compressed**: \n\n---\n\n## integration-backtesting_server-rule_0_mandatory\n**File**: .cursor/rules/discovery/integrations/winners/integration-backtesting_server-rule_0_mandatory.mdc\n**Relevance**: 100\n**Size**: 3131 bytes\n\n**Content**: # integration-backtesting_server-rule_0_mandatory.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: backtesting_server + rule_0_mandatory
> Winner: Selected from automated analysis (Score: 75)

## Purpose
The integration of the backtesting service with the mandatory core requirements could provide significant benefits in terms of security, service management, and trading strategy efficiency. However, due to the high implementation complexity, a detailed cost-benefit analysis should be conducted before proceeding with the integration.

## Integration Analysis
**Score**: 75/100
**Complexity**: High
**Pattern**: Service Orchestration

## Key Benefits
- Enhanced security and compliance with the integration of mandatory core requirements into the backtesting service
- Improved service management and observability through the service registry and master orchestration agent
- Potential for automated backtesting and strategy validation, leading to more efficient trading strategies and better investment decisions

## Implementation Details
**Complexity Reason**: The integration involves not only the connection of two services but also the enforcement of security and data protection measures, API key management, and the adherence to platform invariants. Additionally, the backtesting service requires a detailed manual review and enhancement.

## ...\n\n---\n\n