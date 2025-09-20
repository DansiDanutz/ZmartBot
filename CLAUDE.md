# CLAUDE.md - Smart Context (Auto-Generated)

## 🎯 System Overview

**Last Updated**: 2025-09-21T02:40:50.358962
**Focus Domain**: Core
**Total MDC Files**: 246
**Current Task**: General Development

## 🚨 CRITICAL RULES (Always Active)

### main
# main.mdc
> Type: service | Version: 1.0.0 | Owner: zmartbot | Status: Discovery | Level: 1
Core service component of the ZmartBot ecosystem providing essential functionality.




## ...

### MainAPIServer
# 🚀 Main API Server - Zmart Trading Bot Platform Core
> Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: 8000


## Purpose
FastAPI-based core API server for the Zmart Trading Bot Platform, providing comprehensive trading capabilities, AI-powered signal processing, orchestration management, and complete cryptocurrency trading infrastructure with advanced security and monitoring.

## Description
FastAPI-based core API server for the Zmart Trading Bot Platform, providing comprehensive trading...

## Overview
ZmartBot Main API Server serving as the central backend hub for all trading operations, AI analysis, real-time market data, orchestration control, and comprehensive trading platform functionality with enterprise-grade security and performance.

## ...

### rule_0_mandatory

## Description
Core service component of the ZmartBot ecosystem providing essential functionality.


# Rule 0: ZmartBot Mandatory Core Requirements

## Summary
Core requirements that MUST be satisfied before any development work can proceed. These are non-negotiable foundational requirements for the ZmartBot orchestration system.

## ...

### integration-rules-ServiceLog
# integration-rules-ServiceLog.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: rules + ServiceLog
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of ServiceLog and rules service could bring significant benefits to the cryptocurrency trading platform, including enhanced system monitoring, improved service management, and automated remediation. However, the integration process would need to be carefully managed to ensure data consistency, system stability, and security. Despite the medium implementation complexity, the expected ROI is high, making the integration a worthwhile investment.

## ...

### integration-CryptometerService-main
# integration-CryptometerService-main.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: CryptometerService + main
> Winner: Selected from automated analysis (Score: 92)

## Purpose
The integration of CryptometerService with ZmartBot is highly recommended due to the significant potential benefits. However, careful planning and execution are required to address the potential challenges and ensure a successful integration.

## Integration Analysis
**Score**: 92/100
**Complexity**: Medium
**Pattern**: API Gateway Integration Pattern would be suitable as it provides a single entry point for microservices, simplifying the client-side handling and allowing for centralized management of the integrated services.

## ...

### gammainc_data
# gammainc_data.mdc
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

## ...

### __main__
# __main__.mdc
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

## ...

### gammainc_asy
# gammainc_asy.mdc
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

## ...

### winner-backtesting_server-rule_0_mandatory-20250827-164659
# winner-backtesting_server-rule_0_mandatory-20250827-164659.mdc
> Type: integration-winner | Version: 1.0.0 | Owner: zmartbot | Status: SELECTED

## 🏆 WINNER INTEGRATION - Official Selection

**Winner ID**: winner-backtesting_server-rule_0_mandatory-20250827-164659
**Services**: backtesting_server ↔ rule_0_mandatory
**Compatibility Score**: 75.0/100
**Integration Type**: automated_selection
**Selected**: 2025-08-27 16:46:59
**Status**: PENDING IMPLEMENTATION

## Purpose
This integration was officially selected as a winner from automated analysis cycles based on exceptional compatibility scores and strategic value for the ZmartBot platform.

## Overview
Advanced service integration between backtesting_server and rule_0_mandatory demonstrating the highest compatibility score in its selection cycle. This winner represents a priority implementation target with validated technical benefits.

## ...

### integration-backtesting_server-rule_0_mandatory
# integration-backtesting_server-rule_0_mandatory.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: backtesting_server + rule_0_mandatory
> Winner: Selected from automated analysis (Score: 75)

## Purpose
The integration of the backtesting service with the mandatory core requirements could provide significant benefits in terms of security, service management, and trading strategy efficiency. However, due to the high implementation complexity, a detailed cost-benefit analysis should be conducted before proceeding with the integration.

## Integration Analysis
**Score**: 75/100
**Complexity**: High
**Pattern**: Service Orchestration

## ...

### rules
# rules.mdc
> Type: service | Version: 1.0.0 | Owner: zmartbot | Status: Discovery | Level: 1
Core service component of the ZmartBot ecosystem providing essential functionality.


# Cursor Rules & System Architecture — Clear Action Guidelines
> Type: rule | Version: 1.2.0 | Owner: zmartbot | Purpose: System Architecture & Service Management

**CRITICAL UPDATE**: Added Rule 1.X - ZmartBot Service Architecture Workflow with Complete Certification Requirements - FORBIDDEN TO IGNORE

These rules clearly define what Cursor AI is ALLOWED to do and what is CRITICAL to follow.

## ...

## 🔥 High-Relevance Context

## 📚 Available Contexts

- **Core**: 11 files (see .claude/contexts/core_context.md)
- **Trading**: 10 files (see .claude/contexts/trading_context.md)
- **Monitoring**: 5 files (see .claude/contexts/monitoring_context.md)
- **Orchestration**: 7 files (see .claude/contexts/orchestration_context.md)
- **Services**: 9 files (see .claude/contexts/services_context.md)
- **Data**: 6 files (see .claude/contexts/data_context.md)
- **Backend**: 6 files (see .claude/contexts/backend_context.md)
- **Frontend**: 3 files (see .claude/contexts/frontend_context.md)

## 📊 System Status

- **CLAUDE.md Size**: 8898 characters
- **Size Limit**: 40000 characters
- **Performance**: ✅ Optimal

## 🔄 Context Management

This file is automatically optimized for performance. Full context available in:
- `.claude/contexts/` - Domain-specific contexts
- `.cursor/rules/` - Full MDC files
- Context updates every 120 seconds

**Generated**: 2025-09-21T02:40:50.359160
