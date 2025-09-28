# Backend Domain Context

## BackendDoctorPack
**File**: .cursor/rules/BackendDoctorPack.mdc
**Relevance**: 0
**Size**: 1198 bytes

**Content**: # BackendDoctorPack.mdc


**BackendDoctorPack and BackendDoctorAgent ensure ZmartBot system reliability through comprehensive health monitoring, intelligent diagnostics, automatic problem resolution, and continuous system protection. The BackendDoctorAgent provides real-time monitoring and auto-recovery capabilities for optimal system performance.**

## @step: report_status_to_registry (optional)
- When a service becomes healthy for the first time → POST /services/{name}/status {"status":"TESTED"}.
- On repeated failures beyond policy → optionally set "DISABLED" and log event.

@step: monitor_state_snapshots
- Monitor state snapshot creation and loading processes
- Verify cached data availability during startup
- Ensure smooth transition from cached to live data
- Report any snapshot-related issues to system logs
description:
globs:
alwaysApply: true

## Requirements
- ✅ **Unique port assignment**
- ✅ **Database connectivity**
- ✅ **Complete MDC documentation**
- ✅ **Health endpoint implementation**
- ✅ **Master Orchestration integration**


---
# Test update Sun Aug 24 01:22:52 EEST 2025


## Triggers
- **API endpoint requests**
- **Database events**
- **Health check requests**


---

## BackendFrontendProtection
**File**: .cursor/rules/BackendFrontendProtection.mdc
**Relevance**: 0
**Size**: 345 bytes

**Content**: 
## Description
Core backend service component of the ZmartBot ecosystem providing essential functionality.

@agent: BackendFrontendProtectionAgent

description:
globs:
alwaysApply: true

## Requirements
- ✅ **Unique port assignment**
- ✅ **Complete MDC documentation**


---


## Triggers
- **API endpoint requests**
- **Workflow transitions**


---

## Backend
**File**: .cursor/rules/Backend.mdc
**Relevance**: 0
**Size**: 224 bytes

**Content**: 
## Description
Core backend service component of the ZmartBot ecosystem providing essential functionality.

@agent: BackendService


## Triggers
- **API endpoint requests**
- **Database events**
- **Health check requests**


---

## API-Manager
**File**: .cursor/rules/API-Manager.mdc
**Relevance**: 0
**Size**: 10830 bytes

**Summary**: @agent: APIHandler | # API Manager - External Service Integration System | ## Overview | - **Access Control**: Centralized management prevents credential exposure
**Compressed**: 

---

## start_backend_safe
**File**: .cursor/rules/discovery/tools/start_backend_safe.mdc
**Relevance**: 0
**Size**: 3686 bytes

**Content**: # start_backend_safe.mdc
> Type: frontend | Version: 1.0.0 | Owner: zmartbot | Port: 8000

## Purpose
ZmartBot Main API Server
Provides trading, market data, and system management endpoints

## Overview
Auto-discovered service managed by MDC-Dashboard system. This service was identified during automated system scanning and requires manual review and enhancement.

## Critical Functions
- Auto-discovered service functionality (requires manual documentation)
- Service integration with ZmartBot ecosystem

## Architecture & Integration
- **Service Type:** frontend
- **Dependencies:** To be determined
- **Env Vars:** To be determined  
- **Lifecycle:** start=`python3 /Users/dansidanutz/Desktop/ZmartBot/zmart-api/system_backups/initial_startup_backup/system_backups/initial_startup_backup/start_backend_safe.py.py` | stop=`pkill -f start_backend_safe` | migrate=`n/a`

## API Endpoints
*Endpoints to be documented during manual review*

## Health & Readiness
- Liveness: To be configured
- Readiness: To be configured
- Timeouts: startup_grace=30s, http_timeout=30s

## Observability
- Metrics: To be configured
- Logs: format=python-logging
- Dashboards: To be created



## ...

---

## winner-test_risk_management_server-test_BackendDoctorPack-20250827-160211
**File**: .cursor/rules/discovery/integrations/winners/winner-test_risk_management_server-test_BackendDoctorPack-20250827-160211.mdc
**Relevance**: 0
**Size**: 6263 bytes

**Summary**: # winner-test_risk_management_server-test_BackendDoctorPack-20250827-160211.mdc | ## 🏆 WINNER INTEGRATION - Official Selection
**Compressed**: 

---

