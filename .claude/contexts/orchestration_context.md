# Orchestration Domain Context

## MasterOrchestrationAgent
**File**: .cursor/rules/MasterOrchestrationAgent.mdc
**Relevance**: 50
**Size**: 26509 bytes

**Summary**: # 🎯 Master Orchestration Agent - System Orchestration Controller > Type: backend | Version: 1.0.0 | Owner: zmartbot | Port: 8002 ## Purpose

---

## START_zmartbot
**File**: .cursor/rules/START_zmartbot.mdc
**Relevance**: 30
**Size**: 1954 bytes

**Content**:
```
# 🚀 START_ZMARTBOT.sh - Official System Startup Orchestrator

## Purpose
Official ZmartBot system startup script with comprehensive orchestration, health checks, and automated service management.

## Critical Functions
- **Environment Validation**: Checks Python version, dependencies, and system requirements
- **Port Management**: Detects and resolves port conflicts automatically
- **Service Orchestration**: Starts backend API (port 8000) and frontend dashboard (port 3400)
- **Health Verification**: Validates all services are running correctly
- **Database Orchestration**: Initializes and manages all database connections
- **Rule #1 Compliance**: Ensures official startup procedure is followed

## Usage
```bash
# From project root directory
./START_ZMARTBOT.sh
```

## Key Features
- **One-Command Startup**: Complete system initialization
- **Automatic Conflict Resolution**: Handles port conflicts and process cleanup
- **Health Monitoring**: Real-time service health verification
- **Error Recovery**: Automatic retry mechanisms for failed services
- **Logging**: Comprehensive startup logging and status reporting

## Dependencies
- Python 3.11+
- Required Python packages (installed automatically)
- Port 8000 (backend API)
- Port 3400 (frontend dashboard)
- Database files and configurations

## Security
- Validates API keys and configurations
- Checks file permissions and security settings
- Ensures secure service startup

## Monitoring
- Real-time health checks for all services
- Performance metrics collection
- Error tracking and alerting

## Integration
- Orchestration Agent integration
- Database orchestrator startup
- Service registry management
- Port registry synchronization

## Error Handling
- Graceful failure recovery
- Automatic service restart
- Detailed error reporting
- Fallback mechanisms

## Status
✅ **ACTIVE** - Official startup method with orchestration integration

description:
globs:
alwaysApply: true
---

```

---

## OrchestrationStart
**File**: .cursor/rules/OrchestrationStart.mdc
**Relevance**: 30
**Size**: 13548 bytes

**Summary**: @step: orchestration_flow # OrchestrationStart - Project Startup Orchestration Process ## Overview

---

