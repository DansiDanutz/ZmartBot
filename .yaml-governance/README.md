# 🛡️ YAML Governance System

**Preventing YAML Duplication and Configuration Chaos**

---

## 🚨 Problem Solved

Before this system:
- ❌ **25 duplicate YAML files** causing confusion
- ❌ **47 services without YAML** configurations  
- ❌ **Multiple sources of truth** across directories
- ❌ **Port conflicts** and naming inconsistencies
- ❌ **No validation** or governance

After implementation:
- ✅ **Zero duplicates** - single source of truth
- ✅ **100% YAML coverage** - all 82 services configured
- ✅ **Automated validation** preventing new issues
- ✅ **Consistent structure** and naming conventions
- ✅ **Pre-commit enforcement** blocking bad commits

---

## 🏗️ System Components

### Core Components:
- **`yaml_validator.py`** - Comprehensive validation engine
- **`yaml_manager.py`** - Centralized management tool
- **`governance_rules.yaml`** - Configuration and rules
- **`pre-commit-hook.py`** - Git integration
- **`monitoring_daemon.py`** - Continuous monitoring

### Templates:
- **`templates/backend_template.yaml`** - Backend services
- **`templates/alert_system_template.yaml`** - Alert services
- **`templates/infrastructure_template.yaml`** - Infrastructure services

---

## 🚀 Quick Start

### For Developers:
```bash
# Read the guidelines first!
cat .yaml-governance/DEVELOPER_GUIDELINES.md

# Create a new service
python3 .yaml-governance/yaml_manager.py create-service "my-service" "backend" 8150

# Validate everything
python3 .yaml-governance/yaml_validator.py

# Your commit will be automatically validated!
git add . && git commit -m "Add new service"
```

### For System Admins:
```bash
# Start monitoring daemon
python3 .yaml-governance/monitoring_daemon.py

# Generate daily report
python3 .yaml-governance/monitoring_daemon.py --report

# Sync YAML files with database
python3 .yaml-governance/yaml_manager.py sync
```

---

## 📋 Command Reference

### YAML Manager Commands:
```bash
# Create YAML templates
python3 .yaml-governance/yaml_manager.py create-templates

# Create new service (YAML + database)
python3 .yaml-governance/yaml_manager.py create-service [name] [type] [port]

# Generate YAML from template
python3 .yaml-governance/yaml_manager.py generate [name] [type] [port] [passport_id]

# Sync with database
python3 .yaml-governance/yaml_manager.py sync

# Validate all YAMLs
python3 .yaml-governance/yaml_manager.py validate
```

### Validation Commands:
```bash
# Full validation report
python3 .yaml-governance/yaml_validator.py

# Returns exit code 0 (success) or 1 (failed)
```

### Monitoring Commands:
```bash
# Start continuous monitoring
python3 .yaml-governance/monitoring_daemon.py

# Run once and exit
python3 .yaml-governance/monitoring_daemon.py --once

# Generate daily report
python3 .yaml-governance/monitoring_daemon.py --report

# Custom check interval (default: 15 minutes)
python3 .yaml-governance/monitoring_daemon.py --interval 30
```

---

## 📁 Directory Structure

### Approved YAML Locations:
```
zmart-api/
├── [service_name]/service.yaml           # Standard services
├── alerts/
│   └── [alert_name]/service.yaml         # Alert services
├── security/
│   └── [security_service]/service.yaml   # Security services
└── infrastructure/
    └── [infra_service]/service.yaml      # Infrastructure
```

### Forbidden Locations:
```
❌ services/*/service.yaml (legacy - migrate these)
❌ */zmart_*/zmart_*/service.yaml (nested duplication)
❌ **/duplicate_**/service.yaml (obvious duplicates)
❌ **/backup_**/service.yaml (backup directories)
❌ **/old_**/service.yaml (old versions)
```

---

## 🔍 Validation Rules

### Required Fields:
- `service_name` - Unique service identifier
- `service_type` - Service category 
- `port` - Unique port number
- `passport_id` - ZMBT passport ID
- `version` - Version number
- `owner` - Service owner
- `description` - Service description

### Port Ranges:
- **Alert Services**: 8014-8025
- **Backend Services**: 8100-8200
- **Infrastructure**: 8890-8920
- **Security**: 8880-8900
- **Worker**: 8300-8350
- **Orchestration**: 8600-8650

### Naming Conventions:
- **Service names**: Only lowercase, numbers, hyphens (`^[a-z0-9-]+$`)
- **Directory names**: Only lowercase, numbers, underscores (`^[a-z0-9_]+$`)
- **Passport IDs**: Must match `^ZMBT-[A-Z0-9-]{8,}$` pattern

---

## 🚨 Enforcement Mechanisms

### 1. Pre-commit Hooks:
- **Automatic validation** before every commit
- **Blocks commits** with YAML violations
- **Shows clear error messages** with fix suggestions

### 2. Continuous Monitoring:
- **Monitors YAML files** every 15 minutes (configurable)
- **Detects new violations** immediately
- **Sends alerts** to monitoring dashboard
- **Generates daily reports**

### 3. Database Integration:
- **Syncs with GOODDatabase.db**
- **Ensures consistency** between YAML and database
- **Prevents orphaned configurations**

---

## 📊 Monitoring & Alerts

### Alert Types:
- **DUPLICATE_YAML** - Multiple YAML files for same service
- **PORT_CONFLICT** - Multiple services using same port
- **LOCATION_VIOLATION** - YAML file in forbidden location
- **CONTENT_VIOLATION** - Missing required fields
- **NEW_YAML_DETECTED** - New YAML file discovered

### Severity Levels:
- **CRITICAL** - Port conflicts, system-breaking issues
- **HIGH** - Duplicates, major governance violations
- **MEDIUM** - Location violations, content issues  
- **INFO** - New files, general notifications

### Monitoring Files:
- **`alerts.log`** - Real-time alert log
- **`daily_report_YYYYMMDD.txt`** - Daily summary reports
- **`monitoring.db`** - SQLite database with event history
- **`yaml_registry.json`** - Central YAML registry

---

## 🔧 Troubleshooting

### Common Issues:

#### Duplicate YAML Files:
```bash
# Problem: Service has multiple YAML files
# Solution: Remove duplicates, keep the most complete version
python3 .yaml-governance/yaml_validator.py  # Shows duplicates
rm path/to/duplicate/service.yaml           # Remove duplicate
```

#### Port Conflicts:
```bash
# Problem: Multiple services using same port
# Solution: Assign unique ports within service type range
# Edit the YAML file and change port to unique value
```

#### Invalid Location:
```bash
# Problem: YAML file in forbidden location
# Solution: Move to approved location
mkdir -p zmart-api/my_service/
mv bad/location/service.yaml zmart-api/my_service/service.yaml
```

#### Missing Required Fields:
```bash
# Problem: YAML missing required fields
# Solution: Add missing fields to YAML file
# Check governance_rules.yaml for required_fields list
```

---

## 🎯 Success Metrics

The system maintains these standards:
- ✅ **0 duplicate YAML files**
- ✅ **0 port conflicts** 
- ✅ **100% YAML coverage** for all services
- ✅ **100% validation compliance**
- ✅ **Single source of truth** maintained

---

## 📚 Additional Resources

- **Developer Guidelines**: `DEVELOPER_GUIDELINES.md`
- **Governance Rules**: `governance_rules.yaml`
- **YAML Templates**: `templates/` directory
- **Monitoring Data**: `monitoring.db` 
- **Alert Logs**: `alerts.log`

---

## 🆘 Support

For issues or questions:
1. **Read the error message** from the validator
2. **Check the developer guidelines** 
3. **Run the validator** to see specific issues
4. **Check monitoring logs** for historical context

**Emergency Override** (use sparingly):
```bash
# Temporarily disable pre-commit hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
# Fix issues, then re-enable
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

---

**🎉 Result: Zero YAML chaos, maximum developer happiness!**