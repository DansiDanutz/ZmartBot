# Integrations Discovery Index

**Category**: Auto-Discovered Integrations & Connections
**Count**: 19 MDC files
**Purpose**: Service integrations and external system connections detected

## 🔗 Integration Files

### API Integrations
1. `binance-api-integration.mdc` - Binance exchange API connection
2. `kucoin-api-integration.mdc` - KuCoin exchange API integration
3. `coinmarketcap-api.mdc` - CoinMarketCap data integration
4. `coingecko-api.mdc` - CoinGecko market data integration
5. `cryptometer-api.mdc` - Cryptometer service integration

### Database Integrations
6. `mysql-integration.mdc` - MySQL database connection
7. `postgresql-integration.mdc` - PostgreSQL database integration
8. `mongodb-integration.mdc` - MongoDB NoSQL integration
9. `redis-integration.mdc` - Redis cache integration
10. `sqlite-integration.mdc` - SQLite embedded database

### Message Queue & Communication
11. `rabbitmq-integration.mdc` - RabbitMQ message broker
12. `kafka-integration.mdc` - Apache Kafka streaming platform
13. `websocket-integration.mdc` - WebSocket real-time communication
14. `grpc-integration.mdc` - gRPC service communication

### Monitoring & Analytics
15. `prometheus-integration.mdc` - Prometheus monitoring integration
16. `grafana-integration.mdc` - Grafana dashboard integration
17. `elasticsearch-integration.mdc` - Elasticsearch search integration
18. `kibana-integration.mdc` - Kibana log visualization

### Cloud Services
19. `aws-integration.mdc` - Amazon Web Services integration

## 🎯 Integration Categories

### Exchange APIs (5 integrations)
**Purpose**: Cryptocurrency exchange connectivity
- **binance-api-integration.mdc**: Primary exchange for trading operations
- **kucoin-api-integration.mdc**: Secondary exchange for diversified trading
- **coinmarketcap-api.mdc**: Market capitalization and ranking data
- **coingecko-api.mdc**: Comprehensive market data and analytics
- **cryptometer-api.mdc**: Advanced crypto metrics and indicators

### Database Systems (5 integrations)
**Purpose**: Data persistence and storage solutions
- **mysql-integration.mdc**: Relational database for structured data
- **postgresql-integration.mdc**: Advanced relational database features
- **mongodb-integration.mdc**: Document-based NoSQL storage
- **redis-integration.mdc**: In-memory caching and session storage
- **sqlite-integration.mdc**: Embedded database for local operations

### Messaging & Communication (4 integrations)
**Purpose**: Inter-service communication and real-time data
- **rabbitmq-integration.mdc**: Reliable message queuing
- **kafka-integration.mdc**: High-throughput event streaming
- **websocket-integration.mdc**: Real-time bidirectional communication
- **grpc-integration.mdc**: High-performance RPC communication

### Monitoring & Observability (4 integrations)
**Purpose**: System monitoring, logging, and analytics
- **prometheus-integration.mdc**: Metrics collection and alerting
- **grafana-integration.mdc**: Metrics visualization and dashboards
- **elasticsearch-integration.mdc**: Full-text search and log analysis
- **kibana-integration.mdc**: Log visualization and exploration

### Cloud Infrastructure (1 integration)
**Purpose**: Cloud service integration and deployment
- **aws-integration.mdc**: Amazon Web Services cloud platform

## 🚀 Integration Patterns

### Data Flow Architecture
1. **Market Data**: Exchange APIs → Database Systems → Analytics
2. **Real-time Updates**: WebSocket → Message Queue → Services
3. **Monitoring**: Services → Prometheus → Grafana
4. **Logging**: Applications → Elasticsearch → Kibana

### Service Communication
1. **Synchronous**: gRPC for real-time service calls
2. **Asynchronous**: RabbitMQ/Kafka for event-driven communication
3. **Real-time**: WebSocket for live data streaming
4. **Caching**: Redis for high-speed data access

### Operational Workflow
1. **Development**: Local SQLite → Testing
2. **Staging**: PostgreSQL/MongoDB → Validation
3. **Production**: Distributed databases → Cloud deployment
4. **Monitoring**: Prometheus/Grafana → Operational oversight

---
*Auto-discovered service integrations organized for system architecture visibility*