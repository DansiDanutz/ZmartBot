# Services Domain Context

## ServiceRegistry
**File**: .cursor/rules/ServiceRegistry.mdc
**Relevance**: 30
**Size**: 806 bytes

**Content**:
```
@agent: ServiceRegistryAgent

# Service Registry – Control Plane
Manages dynamic service discovery, unique ports, SAVE/UNDO profiles, and dependency-ordered startup.

## Endpoints (on 127.0.0.1:8610)
- GET /services
- GET /services/active
- GET /profiles/current
- GET /profiles/default
- POST /services/register (X-Token if REGISTRY_TOKEN set)
- POST /services/{name}/status
- POST /profiles/save
- POST /profiles/undo

## Contract
- Each service has a unique port (enforced by DB).
- STOP = SAVE: promote TESTED→ACTIVE and snapshot profile.
- UNDO: roll back to the previous profile.
- State snapshots include service configurations and cached data for smooth startup.
- Snapshot creation during STOP operations, loading and transition during START operations.

description:
globs:
alwaysApply: true
---

```

---

## PortManager
**File**: .cursor/rules/PortManager.mdc
**Relevance**: 30
**Size**: 13839 bytes

**Summary**: @datasource: PortRegistry # PortManager - Post-Startup Port Assignment Management ## Overview

---

## ServiceDiscovery
**File**: .cursor/rules/ServiceDiscovery.mdc
**Relevance**: 30
**Size**: 11362 bytes

**Summary**: @agent: ServiceDiscoveryAgent # Service Discovery & Port Assignment System ## Overview

---

## NewService
**File**: .cursor/rules/NewService.mdc
**Relevance**: 30
**Size**: 12005 bytes

**Summary**: # NewService.mdc > Purpose: Single source of truth to integrate any new service into ZmartBot — deterministically, safely, and repeatably. ## Scope

---

## PortManagerDatabase
**File**: .cursor/rules/PortManagerDatabase.mdc
**Relevance**: 30
**Size**: 15869 bytes

**Summary**: @datasource: PortRegistry # PortManagerDatabase - Service Port Registry ## Overview

---

