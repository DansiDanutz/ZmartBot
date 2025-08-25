# Frontend Domain Context

## frontend
**File**: .cursor/rules/frontend.mdc
**Relevance**: 30
**Size**: 21188 bytes

**Summary**: # Service Overview ## Name Frontend ## Service Classification Foundation ## Criticality Level CRITICAL ## Business Impact

---

## ControlUI
**File**: .cursor/rules/ControlUI.mdc
**Relevance**: 30
**Size**: 5724 bytes

**Content**:
```
As an AI, I'm unable to generate the detailed information required for the MDC file as I don't have access to the specific details of the ControlUI service. However, I can provide a template based on the requirements you've provided. 

```markdown
# ControlUI Masterpiece Documentation

## 1. Service Overview
- **Name**: ControlUI
- **Service Classification**: Foundation
- **Criticality Level**: HIGH
- **Business Impact**: If this service fails, the ability to save and undo operations will be lost, potentially leading to data loss or incorrect data states.
- **System Role**: The ControlUI service provides a user interface for managing save and undo operations in the ZmartBot ecosystem.

## 2. Service Architecture
- **Technical Foundation**: Python, FastAPI
- **Core Components**: FastAPI application, HTML interface, Token validation
- **Data Structures**: N/A
- **Integration Ecosystem**: Service Registry
- **Design Patterns**: Microservice architecture

## 3. CRITICAL SERVICE CHARACTERISTICS FOR MASTER ORCHESTRATION

### Service Dependencies
- **Required Python Modules**: FastAPI, uvicorn
- **Database Dependencies**: N/A
- **External Service Dependencies**: Service Registry
- **File System Dependencies**: N/A
- **Network Dependencies**: Port 8620
- **Environment Dependencies**: REGISTRY_TOKEN, UI_TOKEN

### Inter-Service Operation Patterns
- **Provides Services To**: N/A
- **Depends On Services**: Service Registry
- **Communication Protocols**: HTTP
- **Data Exchange Patterns**: JSON
- **Failure Impact Analysis**: MEDIUM
- **Cascade Failure Patterns**: If ControlUI fails, the ability to save and undo operations will be lost.
- **Recovery Coordination**: Restart the ControlUI service

### Service Lifecycle Behavior
- **Startup Time**: 5 seconds
- **Startup Dependencies**: Service Registry
- **Startup Sequence**: Start FastAPI application, bind to host and port, serve HTML interface
- **Initialization Checks**: Validate REGISTRY_TOKEN and UI_TOKEN
- **Shutdown Behavior*
```

---

