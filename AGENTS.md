# AGENTS.md - ZmartBot AI Agents & Orchestration System

## 🎯 Overview

The ZmartBot platform employs a sophisticated multi-agent architecture for autonomous cryptocurrency trading, market analysis, and system orchestration. This document provides comprehensive documentation of all AI agents, their capabilities, interactions, and management within the ZmartBot ecosystem.

**Last Updated**: 2025-09-09
**System Version**: 2.0.0
**Total Agents**: 25+
**Architecture**: Microservice-based Agent Orchestration

---

## 🏗️ Agent Architecture

### System Architecture Levels

```bash
Level 1: Discovery Service (Agent Detection & MDC Generation)
Level 2: Passport Service (Agent Validation & Authentication)
Level 3: Registration Service (Agent Registry & Lifecycle Management)
Level 4: Certification Service (Agent Certification & Quality Assurance)
```

### Agent Communication Flow

```text
Event Bus ← → Master Orchestration Agent
    ↓                    ↓
Service Discovery ← → Trading Agents
    ↓                    ↓
MDC System      ← → Analysis Agents
```

---

## 🤖 Core Orchestration Agents

### Master Orchestration Agent
**File**: `master_orchestration_agent.py`
**Port**: 8950
**Type**: Orchestration
**Status**: Production

**Purpose**: Central control system for all ZmartBot operations

- **Service Coordination**: Manages lifecycle of all microservices
- **Resource Allocation**: Dynamic resource distribution across agents
- **Health Monitoring**: System-wide health checks and recovery
- **Event Orchestration**: Coordinates complex multi-agent workflows

**Key Features**:

- Multi-service dependency management
- Automatic failure recovery and restart mechanisms
- Load balancing across agent instances
- Real-time performance monitoring

### MDC Orchestration Agent
**File**: `mdc_orchestration_agent.py`
**Port**: 8951
**Type**: Documentation
**Status**: Production

**Purpose**: Automated MDC (Microservice Documentation Configuration) management

- **Auto-Discovery**: Detects new Python services in the system
- **Documentation Generation**: Creates professional MDC files automatically
- **Service Registration**: Registers services in the Discovery database
- **Quality Assurance**: Validates MDC completeness and accuracy

**Workflow Integration**:

1. File Watcher → New .py file detected
2. Service Analysis → AI-powered capability detection
3. MDC Generation → Professional documentation creation
4. Database Registration → Service added to Discovery level

---

## 🧠 AI Analysis Agents

### Enhanced AI Analysis Agent
**File**: `src/services/enhanced_ai_analysis_agent.py`
**Type**: AI Analysis
**Capabilities**: Advanced market sentiment, technical indicators, risk assessment

**Features**:

- Multi-model AI ensemble for market prediction
- Real-time sentiment analysis from multiple sources
- Advanced technical indicator computation
- Risk-adjusted position sizing recommendations

### Multi-Model AI Agent
**File**: `src/services/multi_model_ai_agent.py`
**Type**: AI Analysis
**Capabilities**: Ensemble learning, model fusion, prediction aggregation

**Models Supported**:

- Transformer models for sequence prediction
- LSTM networks for time series analysis
- Random Forest for pattern recognition
- Gradient Boosting for risk assessment

### Historical AI Analysis Agent
**File**: `src/services/historical_ai_analysis_agent.py`
**Type**: AI Analysis
**Capabilities**: Historical pattern recognition, backtesting, strategy validation

**Functions**:

- Historical market data analysis
- Pattern recognition across multiple timeframes
- Strategy backtesting and validation
- Performance metric calculation and reporting

### Unified Analysis Agent
**File**: `src/services/unified_analysis_agent.py`
**Type**: AI Analysis
**Capabilities**: Consolidated analysis, decision synthesis, unified recommendations

**Integration Points**:

- Aggregates insights from all analysis agents
- Provides unified trading recommendations
- Risk-weighted decision making
- Real-time strategy adaptation

---

## 📈 Trading & Learning Agents

### Enhanced Learning Agent
**File**: `src/services/enhanced_learning_agent.py`
**Type**: Machine Learning
**Capabilities**: Adaptive learning, strategy optimization, performance improvement

**Learning Methods**:

- Reinforcement learning for strategy adaptation
- Online learning for real-time market changes
- Transfer learning for new market conditions
- Meta-learning for rapid strategy deployment

### Advanced Learning Agent
**File**: `src/services/advanced_learning_agent.py`
**Type**: Machine Learning
**Capabilities**: Deep learning, neural network training, advanced pattern recognition

**Architecture**:

- Deep neural networks for complex pattern detection
- Convolutional networks for chart pattern analysis
- Attention mechanisms for market focus
- Generative models for scenario simulation

### Trading Orchestration Agent
**File**: `trading_orchestration_agent.py`
**Type**: Trading
**Capabilities**: Trade execution, portfolio management, risk control

**Functions**:

- Multi-exchange trade execution
- Portfolio rebalancing and optimization
- Real-time risk monitoring and control
- Position sizing and capital allocation

---

## ⛓️ Blockchain & Integration Agents

### Blockchain Agent
**File**: `src/services/blockchain_agent.py`
**Type**: Blockchain
**Capabilities**: On-chain analysis, DeFi integration, blockchain monitoring

**Features**:

- On-chain transaction analysis
- Smart contract interaction
- DeFi protocol monitoring
- Cross-chain bridge management

### Kingfisher AI
**File**: Referenced in `KINGFISHER_AI.mdc`
**Type**: Advanced Analysis
**Capabilities**: Professional market analysis, whale tracking, institutional insights

**Specialized Functions**:

- Whale wallet monitoring and analysis
- Institutional trading pattern recognition
- Market manipulation detection
- Professional-grade technical analysis

---

## 🛠️ System & Utility Agents

### Background MDC Agent
**File**: `background_mdc_agent.py`
**Type**: Utility
**Capabilities**: Continuous documentation updates, system monitoring

**Operations**:

- Continuous file system monitoring
- Automatic MDC file updates
- Service health documentation
- System state tracking

### Cursor Sync Agent
**File**: `cursor_sync_agent.py`
**Type**: Development
**Capabilities**: Development environment synchronization

### Ziva Agent
**File**: `ziva_agent.py`
**Type**: Assistant
**Capabilities**: Intelligent assistant, query processing, user interaction

### GPT MDS Agent
**File**: `gpt_mds_agent.py`
**Type**: AI Documentation
**Capabilities**: AI-powered documentation generation, service analysis

---

## 🔄 Agent Management & Communication

### Agent Routes API
**File**: `src/routes/agents.py`
**Port**: 8000 (Main API)
**Type**: API Management

**Endpoints**:

- `GET /agents` - List all agents and their status
- `POST /agents` - Register new agent
- `PUT /agents/{agent_id}` - Update agent configuration
- `DELETE /agents/{agent_id}` - Deactivate agent
- `POST /agents/{agent_id}/tasks` - Assign task to agent
- `GET /agents/{agent_id}/status` - Get agent health status

**Agent Status Types**:

- `idle` - Agent available for tasks
- `active` - Agent currently processing
- `busy` - Agent at capacity
- `error` - Agent encountered error
- `maintenance` - Agent under maintenance

### Event Bus System

All agents communicate through a centralized event bus:

```python
EventType.AGENT_STARTED
EventType.AGENT_STOPPED
EventType.TASK_ASSIGNED
EventType.TASK_COMPLETED
EventType.TASK_FAILED
EventType.HEALTH_CHECK
```

---

## 📊 Agent Monitoring & Metrics

### Health Monitoring

Each agent provides:

- **Heartbeat**: Regular status updates
- **Performance Metrics**: Execution time, success rate, error count
- **Resource Usage**: CPU, memory, network utilization
- **Task Queue**: Pending, active, and completed task counts

### Logging & Audit
- **Centralized Logging**: All agent activities logged to central system
- **Audit Trail**: Complete record of agent decisions and actions
- **Performance Analytics**: Historical performance tracking and analysis
- **Alert System**: Automated alerts for agent failures or performance issues

---

## 🚀 Agent Deployment & Lifecycle

### Startup Sequence

1. **System Initialization**: Master Orchestration Agent starts first
2. **Core Services**: MDC Agent, Service Discovery, Health Monitor
3. **Analysis Agents**: AI analysis and learning agents
4. **Trading Agents**: Trading and portfolio management agents
5. **Utility Agents**: Background services and utilities

### Configuration Management

Agents are configured through:

- **Environment Variables**: Runtime configuration
- **MDC Files**: Service documentation and metadata
- **YAML Configuration**: Service-specific settings
- **Dynamic Configuration**: Runtime parameter updates

### Scripts & Automation
- `start_background_mdc_agent.sh` - Start background documentation agent
- `stop_background_mdc_agent.sh` - Stop background documentation agent
- `start_mdc_orchestration_agent.sh` - Start MDC orchestration system

---

## 🔐 Security & Access Control

### Agent Authentication
- **Service Tokens**: JWT-based authentication for agent-to-agent communication
- **Role-Based Access**: Agents have specific roles and permissions
- **API Key Management**: Secure API key storage and rotation
- **Encryption**: All inter-agent communication encrypted

### Security Monitoring
- **Anomaly Detection**: Unusual agent behavior monitoring
- **Access Auditing**: Complete audit trail of agent actions
- **Threat Detection**: Automated security threat identification
- **Compliance Monitoring**: Regulatory compliance verification

---

## 📚 Integration with MDC System

### MDC Documentation Workflow

1. **Discovery**: Agent files detected by file watchers
2. **Analysis**: AI-powered service capability analysis
3. **Documentation**: Professional MDC file generation
4. **Registration**: Service added to Discovery database
5. **Validation**: Quality assurance and completeness checks
6. **Certification**: Agent approved for production use

### Service Levels
- **Level 1 - Discovery**: Basic service detection and documentation
- **Level 2 - Passport**: Authentication and validation
- **Level 3 - Registration**: Service registry and lifecycle management
- **Level 4 - Certification**: Quality assurance and production readiness

---

## 🔧 Development & Testing

### Agent Development Guidelines

1. **Follow MDC Standards**: All agents must have proper MDC documentation
2. **Implement Health Checks**: Liveness and readiness probes required
3. **Error Handling**: Comprehensive error handling and recovery
4. **Logging Standards**: Structured logging with appropriate levels
5. **Testing Coverage**: Minimum 80% test coverage required

### Testing Framework
- **Unit Tests**: Individual agent functionality testing
- **Integration Tests**: Agent-to-agent communication testing
- **Load Tests**: Performance under high load
- **Chaos Testing**: Failure scenario testing

---

## 📈 Performance & Optimization

### Performance Metrics
- **Response Time**: Average agent response time
- **Throughput**: Tasks processed per second
- **Success Rate**: Percentage of successful task completions
- **Resource Utilization**: CPU, memory, and network usage
- **Availability**: Uptime percentage

### Optimization Strategies
- **Load Balancing**: Distribute tasks across multiple agent instances
- **Caching**: Cache frequently accessed data and results
- **Async Processing**: Non-blocking task execution
- **Resource Pooling**: Efficient resource allocation and reuse

---

## 🚨 Troubleshooting & Maintenance

### Common Issues

1. **Agent Unresponsive**: Check health endpoints, restart if necessary
2. **High Memory Usage**: Monitor for memory leaks, implement cleanup
3. **Communication Failures**: Verify network connectivity and certificates
4. **Performance Degradation**: Check resource utilization and load

### Maintenance Procedures
- **Regular Health Checks**: Automated health monitoring
- **Log Rotation**: Prevent log files from consuming excessive disk space
- **Configuration Updates**: Hot-reload capability for configuration changes
- **Version Updates**: Rolling updates without service interruption

---

## 📞 Support & Contact

For agent-related issues or questions:

- **System Logs**: Check centralized logging system
- **Health Dashboard**: Monitor agent status through web interface
- **Documentation**: Refer to individual MDC files for detailed service information
- **Development Team**: Contact ZmartBot development team for assistance

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-09
**Next Review**: 2025-10-09
