# 🛡️ YAML Governance - Developer Guidelines

## 🚨 CRITICAL: YAML Duplication Prevention System

**Created**: 2025-08-31  
**Purpose**: Prevent YAML duplication and configuration chaos  
**Status**: MANDATORY for all developers

---

## 🎯 Overview

The YAML Governance System prevents the chaos and duplication that previously plagued our YAML configurations. **ALL DEVELOPERS** must follow these guidelines.

### ⚠️ What Was Fixed:
- ✅ **25 duplicate YAML files removed**
- ✅ **47 missing YAML files created**  
- ✅ **100% YAML coverage achieved**
- ✅ **Single source of truth established**

---

## 🏗️ System Architecture

```
.yaml-governance/
├── yaml_validator.py          # Core validation engine
├── yaml_manager.py           # Centralized management tool
├── governance_rules.yaml     # Configuration rules
├── pre-commit-hook.py        # Pre-commit validation
├── monitoring_daemon.py      # Continuous monitoring
├── templates/               # YAML templates
│   ├── backend_template.yaml
│   ├── alert_system_template.yaml
│   └── infrastructure_template.yaml
├── yaml_registry.json       # Central registry
└── DEVELOPER_GUIDELINES.md  # This file
```

---

## 🚫 FORBIDDEN ACTIONS

### ❌ NEVER DO THESE:

1. **Don't create YAML files manually** without using the governance system
2. **Don't create duplicate YAML files** in multiple locations
3. **Don't use mixed naming conventions** (stick to hyphens OR underscores)
4. **Don't place YAML files in forbidden locations**:
   - `*/zmart_*/zmart_*/service.yaml` (nested duplication)
   - `**/duplicate_**/service.yaml` (obvious duplicates)
   - `**/backup_**/service.yaml` (backup directories)
   - `**/old_**/service.yaml` (old versions)

---

## ✅ REQUIRED ACTIONS

### 🎯 Before Creating Any Service:

1. **Use the YAML Manager**:
   ```bash
   python3 .yaml-governance/yaml_manager.py create-service [service_name] [service_type] [port]
   ```

2. **Validate your changes**:
   ```bash
   python3 .yaml-governance/yaml_validator.py
   ```

3. **Check pre-commit hook passes**:
   ```bash
   git add . && git commit -m "test"  # Should pass validation
   ```

---

## 📍 Allowed YAML Locations

### ✅ APPROVED LOCATIONS:

```
zmart-api/[service_name]/service.yaml                    # Standard services
zmart-api/alerts/[alert_name]/service.yaml              # Alert services  
zmart-api/security/[security_service]/service.yaml      # Security services
zmart-api/infrastructure/[infra_service]/service.yaml   # Infrastructure
```

### 📋 Examples:
```
✅ zmart-api/my_new_service/service.yaml
✅ zmart-api/alerts/whale/service.yaml  
✅ zmart-api/security/auth_middleware/service.yaml
✅ zmart-api/infrastructure/port_manager/service.yaml
```

---

## 🛠️ How to Create New Services

### Method 1: Using YAML Manager (RECOMMENDED)

```bash
# Create complete service with YAML + database entry
python3 .yaml-governance/yaml_manager.py create-service \
    "my-new-service" \
    "backend" \
    8150 \
    --description "My new service description"
```

### Method 2: Using Templates

```bash
# Create templates first
python3 .yaml-governance/yaml_manager.py create-templates

# Generate YAML from template
python3 .yaml-governance/yaml_manager.py generate \
    "my-service" \
    "backend" \
    8151 \
    "ZMBT-SERV-20250831-ABC123" \
    --description "Service description"
```

---

## 🔍 Validation Commands

### Daily Validation:
```bash
# Full validation check
python3 .yaml-governance/yaml_validator.py

# Quick check
python3 .yaml-governance/yaml_manager.py validate

# Sync with database
python3 .yaml-governance/yaml_manager.py sync
```

### Monitoring:
```bash
# Run continuous monitoring (for system admins)
python3 .yaml-governance/monitoring_daemon.py

# Generate daily report
python3 .yaml-governance/monitoring_daemon.py --report

# One-time check
python3 .yaml-governance/monitoring_daemon.py --once
```

---

## 📋 Required YAML Fields

Every `service.yaml` MUST contain:

```yaml
service_name: "my-service"           # Unique service name
service_type: "backend"              # Service category
version: "1.0.0"                     # Version
owner: "zmartbot"                    # Owner
description: "Service description"   # Clear description
port: 8150                          # Unique port
passport_id: "ZMBT-SERV-20250831-ABC123"  # Unique passport
status: "ACTIVE"                     # Status
registered_at: "2025-08-31"         # Registration date
health_url: "http://localhost:8150/health"  # Health endpoint
start_cmd: "python3 my_service.py --port 8150"  # Start command
stop_cmd: "pkill -f 'my_service.py'"  # Stop command
dependencies: ["zmart-api"]          # Dependencies
tags: ["backend", "my-service"]      # Tags
```

---

## 🚨 Pre-commit Hook Enforcement

The system **automatically blocks commits** with YAML violations:

```bash
🛡️ ZmartBot Pre-commit Governance Checks
🔍 Running YAML governance validation...
❌ PRE-COMMIT HOOK FAILED - YAML GOVERNANCE VIOLATIONS

🚫 COMMIT BLOCKED - Fix the following issues:
1. Remove duplicate YAML files
2. Resolve port conflicts  
3. Move YAML files to allowed locations
4. Fix content validation errors

💡 Run this command to see detailed issues:
   python3 .yaml-governance/yaml_validator.py
```

---

## 🎯 Service Type Guidelines

### Backend Services (Port: 8100-8200)
```yaml
service_type: "backend"
# Standard business logic services
```

### Alert Services (Port: 8014-8025) 
```yaml
service_type: "alert_system"
# Location: zmart-api/alerts/[name]/service.yaml
```

### Infrastructure Services (Port: 8890-8920)
```yaml
service_type: "infrastructure"  
# Location: zmart-api/infrastructure/[name]/service.yaml
```

### Security Services (Port: 8880-8900)
```yaml
service_type: "security"
# Location: zmart-api/security/[name]/service.yaml
```

---

## 🔧 Troubleshooting

### "Duplicate YAML detected"
```bash
# Find duplicates
python3 .yaml-governance/yaml_validator.py

# Remove the duplicate (keep the most complete version)
rm path/to/duplicate/service.yaml
```

### "Port conflict detected"  
```bash
# Check port usage
python3 .yaml-governance/yaml_validator.py

# Update port in YAML file to unique value
# Use appropriate port range for service type
```

### "Invalid location"
```bash
# Move YAML to approved location
mkdir -p zmart-api/my_service/
mv invalid/location/service.yaml zmart-api/my_service/service.yaml
```

---

## 📊 Monitoring Dashboard

Monitor YAML health at: `http://localhost:8090/yaml-governance`

View alerts: `.yaml-governance/alerts.log`

Daily reports: `.yaml-governance/daily_report_YYYYMMDD.txt`

---

## 🆘 Support & Escalation

### For Issues:
1. **Run validator**: `python3 .yaml-governance/yaml_validator.py`
2. **Check logs**: `tail -f .yaml-governance/alerts.log`
3. **Generate report**: `python3 .yaml-governance/monitoring_daemon.py --report`

### Emergency Override:
```bash
# Temporarily disable validation (EMERGENCY ONLY)
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# Re-enable after fixing issues
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

---

## 🎯 Success Metrics

✅ **Zero YAML duplicates**  
✅ **Zero port conflicts**  
✅ **100% YAML coverage**  
✅ **Single source of truth**  
✅ **Consistent naming conventions**  
✅ **Proper directory structure**

---

## 📚 Quick Reference

```bash
# Create new service
python3 .yaml-governance/yaml_manager.py create-service [name] [type] [port]

# Validate all YAMLs  
python3 .yaml-governance/yaml_validator.py

# Sync with database
python3 .yaml-governance/yaml_manager.py sync

# Monitor continuously
python3 .yaml-governance/monitoring_daemon.py
```

---

**Remember**: The governance system prevents chaos. Follow these rules and your commits will be smooth and your YAML files will be perfect! 🎯

**Questions?** Check the validation output or monitoring logs first.