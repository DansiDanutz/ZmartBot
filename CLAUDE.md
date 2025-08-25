# CLAUDE.md - Smart Context (Auto-Generated)

## 🎯 System Overview

**Last Updated**: 2025-08-25T05:31:04.022586
**Focus Domain**: Core
**Total MDC Files**: 67
**Current Task**: General Development

## 🚨 CRITICAL RULES (Always Active)

### main


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

This file aggregates all ru

### rules
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
- Mass file operations (moving/delet

### rule_0_mandatory
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
- **

## 🔥 High-Relevance Context

## 📚 Available Contexts

- **Core**: 3 files (see .claude/contexts/core_context.md)
- **Trading**: 6 files (see .claude/contexts/trading_context.md)
- **Monitoring**: 3 files (see .claude/contexts/monitoring_context.md)
- **Orchestration**: 3 files (see .claude/contexts/orchestration_context.md)
- **Services**: 5 files (see .claude/contexts/services_context.md)
- **Data**: 3 files (see .claude/contexts/data_context.md)
- **Backend**: 4 files (see .claude/contexts/backend_context.md)
- **Frontend**: 2 files (see .claude/contexts/frontend_context.md)

## 📊 System Status

- **CLAUDE.md Size**: 3866 characters
- **Size Limit**: 40000 characters
- **Performance**: ✅ Optimal

## 🔄 Context Management

This file is automatically optimized for performance. Full context available in:
- `.claude/contexts/` - Domain-specific contexts
- `.cursor/rules/` - Full MDC files
- Context updates every 30 seconds

**Generated**: 2025-08-25T05:31:04.022701
