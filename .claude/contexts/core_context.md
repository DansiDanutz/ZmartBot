# Core Domain Context

## main
**File**: .cursor/rules/main.mdc
**Relevance**: 130
**Size**: 2646 bytes

**Content**:
```


## ZmartBot Orchestration Entry Point

@include "2IndicatorsDatabase.mdc"
@include "API-Manager.mdc"
@include "Backend.mdc"
@include "BackendDoctorPack.mdc"
@include "ProcessReaper.mdc"
@include "LiveAlerts.mdc"
@include "IndicatorCard.mdc"
@include "MasterOrchestrationAgent.mdc"
@include "MesseiAlerts.mdc"
@include "MySymbols.mdc"
@include "MySymbolsDatabase.mdc"
@include "OrchestrationStart.mdc"
@include "Pele.mdc"
@include "PortManager.mdc"
@include "PortManagerDatabase.mdc"
@include "START_zmartbot.mdc"
@include "STOP_zmartbot.mdc"
@include "WhaleAlerts.mdc"
@include "ServiceRegistry.mdc"
@include "StartGuard.mdc"
@include "ControlUI.mdc"
@include "zmartbot.dynamic.test.mdc"
@include "BackendFrontendProtection.mdc"
@include "ClaudeMDCUpdate.mdc"
@include "ServiceDiscovery.mdc"
@include "rules.mdc"


### System Description

ZmartBot is an AI-driven crypto trading system using symbol selection, risk metrics, liquidity tracking, and orchestration agents.

This file aggregates all rule modules and should be used as the master entry point for orchestrating agents, symbol operations, and alerting logic.

### Core System Components

1. **Orchestration System**
   - Master Orchestration Agent coordinates all system components
   - Port Manager handles service port assignments
   - ProcessReaper utility resolves port conflicts and orphaned processes

2. **Trading Infrastructure**
   - Backend API (FastAPI) on port 8000
   - Professional Dashboard (React/Vite) on port 3400
   - MySymbols management (max 10 symbols)
   - 21 Technical Indicators with real-time updates

3. **Alert System**
   - Live Alerts with dynamic indicator updates
   - Special Alerts: Messi, Pele, Maradona, Whale Flow
   - Real-time market data integration

4. **Data Management**
   - SQLite databases for port registry and MySymbols
   - PostgreSQL, Redis, InfluxDB for various data types
   - API Keys Manager for secure credential management

### Operational Rules

- Each service runs on unique, perm
```

---

## rules
**File**: .cursor/rules/rules.mdc
**Relevance**: 130
**Size**: 5219 bytes

**Content**:
```
# Cursor Rules — Command Guardrails

These rules govern what Cursor (and any automation) may execute inside this workspace.

## Hard‑Blocked (NEVER RUN)
- Destructive filesystem:
  - `rm -rf /`, `sudo rm -rf /*`, `chmod -R 777 /`, `chown -R root /`
  - Any `rm -rf` outside the project root
- Blind remote execution:
  - `curl * | bash`, `wget * -O- | bash`
- Device/disk writes:
  - `dd if=/dev/* of=/dev/*`, raw disk formatting/partitioning utilities
- Unscoped process kills:
  - `pkill -f python`, `kill -9 -1`, anything that can affect non-Zmart processes
- Kernel / system config writes (outside containers):
  - writing to `/etc/*`, `/sys/*`, `/proc/*` without explicit task & approval
- Secrets exfiltration:
  - printing env vars wholesale, catting secret files, uploading tokens/keys

## Confirm‑Before‑Run (Require explicit human OK)
- `git push --force`, `git reset --hard`, `git clean -xfd`
- `docker system prune -a`, `docker rm -f $(docker ps -aq)`
- Mass file operations (moving/deleting >100 files)
- Package manager global installs that change toolchains (e.g., `npm i -g`, `pip install --break-system-packages`)
- Network/security tooling (nmap/iptables) in non‑isolated environments

## Allowed (Safe by default)
- `ls`, `pwd`, `cat`, `cp`, `mv` (inside repo), `mkdir`, `grep`, `sed`, `awk`
- `python -m ...` within the ZmartBot workspace
- Running project scripts that adhere to Rule 0 and start with `set -euo pipefail`

## Service Registration & Duplicate Prevention Rules

### MANDATORY Pre-Registration Checks
- **Port Conflict Detection**: ALWAYS check if port is already assigned before creating new service
- **Service Name Validation**: Check for existing services with similar names or same functionality
- **Registry Validation**: Verify service registry before creating new entries
- **MDC File Duplication**: Check for existing MDC files before creating new ones

### Service Name Mapping (Standardized)
- `zmart_orchestration` → `master_orchestration_agent` (Port 80
```

---

## rule_0_mandatory
**File**: .cursor/rules/rule_0_mandatory.mdc
**Relevance**: 130
**Size**: 8962 bytes

**Content**:
```
# Rule 0: ZmartBot Mandatory Core Requirements

## Summary
Core requirements that MUST be satisfied before any development work can proceed. These are non-negotiable foundational requirements for the ZmartBot orchestration system.

## Security & Secrets Management

### Secret Scanning
- **Requirement**: All commits MUST pass secret scanning before merge
- **Tools**: Use gitleaks, detect-secrets, or equivalent
- **Action**: Block commits containing API keys, passwords, tokens
- **Implementation**: Pre-commit hooks + CI/CD pipeline checks

### API Key Management
- **Storage**: All API keys in environment variables or secure vault
- **Rotation**: Automated key rotation every 90 days
- **Access Control**: Principle of least privilege for API access
- **Monitoring**: Log all API key usage and failed authentication attempts

### Data Protection
- **Encryption**: All sensitive data encrypted at rest and in transit
- **PII Handling**: Strict controls on personally identifiable information
- **Audit Trail**: Complete audit logs for all data access and modifications

## Platform Invariants

### Service Registry (Port 8610)
- **Requirement**: MUST be the single source of truth for all services
- **Contract**: All services MUST register with health endpoints
- **Discovery**: Dynamic service discovery through registry only
- **Consistency**: Registry state MUST be consistent across all operations

### Master Orchestration Agent (Port 8002)
- **Requirement**: MUST coordinate all service lifecycle operations
- **Intelligence**: MUST learn from service interactions and failures
- **Recovery**: MUST implement intelligent failure recovery strategies
- **Monitoring**: MUST provide real-time system health monitoring

### Snapshot Manager
- **State Snapshots**: MUST capture complete system state before major operations
- **Rollback Capability**: MUST enable instant rollback to previous states
- **Consistency**: Snapshots MUST maintain data consistency across services
- **Retention**: MU
```

---

