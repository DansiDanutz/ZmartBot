# Monitoring Domain Context

## ProcessReaper
**File**: .cursor/rules/ProcessReaper.mdc
**Relevance**: 30
**Size**: 7480 bytes

**Content**:
```
# MAXIMUM UPGRADE: ProcessReaper.mdc

## Service Overview
- **Name**: ProcessReaper
- **Port**: Dynamic (Assigned by Port Manager)
- **Type**: Security and Cleanup Agent
- **Description**: ProcessReaper is a critical security and cleanup script that acts as the system's "immune system" for the ZmartBot project. It identifies, analyzes, and eliminates virus scripts, conflicting processes, and malicious code that are detected by the Port Manager or Master Orchestration Agent.
- **Service Classification**: Security
- **Business Impact**: If ProcessReaper fails, the system is exposed to potential security threats, including virus scripts, unauthorized processes, and conflicting code. This could lead to system instability, data corruption, and unauthorized access to sensitive data.

## Service Architecture
- **Key Features**: Virus Script Detection & Elimination, Process Conflict Resolution, Port Conflict Cleanup, System Integrity Protection
- **Supported Operations**: Threat detection, threat analysis, threat elimination, conflict resolution, system integrity protection
- **Integration Ecosystem**: ProcessReaper is integrated with the Port Manager and Master Orchestration Agent for threat detection and elimination. It also interacts with the system security for implementing security protocols and maintaining system integrity.

## CRITICAL SERVICE CHARACTERISTICS FOR MASTER ORCHESTRATION

### Service Dependencies
- **Required Modules**: Python's os, sys, subprocess, and shutil modules
- **Database Dependencies**: SQLite for logging and reporting
- **External Service Dependencies**: None
- **File System Dependencies**: Configuration files in /etc/doctor_kill, quarantine directory in /tmp/zmartbot_quarantine
- **Network Dependencies**: Dynamic port assigned by Port Manager

### Inter-Service Operation Patterns
- **Provides Services To**: Master Orchestration Agent, Port Manager
- **Depends On Services**: Port Manager, Master Orchestration Agent
- **Communication Patterns**
```

---

## MonitoringMDC
**File**: .cursor/rules/MonitoringMDC.mdc
**Relevance**: 30
**Size**: 14489 bytes

**Summary**: # MDC Monitoring System - Comprehensive Documentation @agent: MonitoringMDC

---

## diagnostics
**File**: .cursor/rules/diagnostics.mdc
**Relevance**: 30
**Size**: 3862 bytes

**Content**:
```
As an AI, I'm unable to generate the entire MDC file as requested due to the lack of specific information about the service. However, I can provide a template based on the requirements you've provided. You can fill in the details as per your service's specifics.

```markdown
# Masterpiece Documentation Content (MDC) for Diagnostics Service

## 1. Service Overview
- **Name**: Diagnostics
- **Service Classification**: 
- **Criticality Level**: 
- **Business Impact**: 
- **System Role**: 

## 2. Service Architecture
- **Technical Foundation**: 
- **Core Components**: 
- **Data Structures**: 
- **Integration Ecosystem**: 
- **Design Patterns**: 

## 3. Critical Service Characteristics for Master Orchestration

### Service Dependencies
- **Required Python Modules**: 
- **Database Dependencies**: 
- **External Service Dependencies**: 
- **File System Dependencies**: 
- **Network Dependencies**: 
- **Environment Dependencies**: 

### Inter-Service Operation Patterns
- **Provides Services To**: 
- **Depends On Services**: 
- **Communication Protocols**: 
- **Data Exchange Patterns**: 
- **Failure Impact Analysis**: 
- **Cascade Failure Patterns**: 
- **Recovery Coordination**: 

### Service Lifecycle Behavior
- **Startup Time**: 
- **Startup Dependencies**: 
- **Startup Sequence**: 
- **Initialization Checks**: 
- **Shutdown Behavior**: 
- **Shutdown Priority**: 
- **State Persistence**: 
- **Recovery Patterns**: 

### Runtime Characteristics
- **Memory Usage**: 
- **CPU Usage**: 
- **Network Usage**: 
- **Disk I/O**: 
- **Concurrency Model**: 
- **Performance Characteristics**: 
- **Resource Scaling**: 
- **Performance Optimization**: 

### Error Conditions & Recovery
- **Failure Modes**: 
- **Failure Detection**: 
- **Failure Impact**: 
- **Recovery Strategies**: 
- **Circuit Breaker Patterns**: 
- **Fallback Mechanisms**: 
- **Disaster Recovery**: 
- **Health Check Patterns**: 

### Monitoring & Observability
- **Health Check Endpoints**: 
- **Performance Metrics**: 
- *
```

---

