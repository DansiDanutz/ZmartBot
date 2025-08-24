#!/usr/bin/env python3
"""
MDC Generator for ZmartBot - Creates comprehensive MDC documentation for key system components
Uses MDCAgent approach for consistent, high-quality documentation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class MDCGenerator:
    """MDC documentation generator using MDCAgent approach"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.mdc_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_orchestration_mdc(self):
        """Generate MDC for critical orchestration components"""
        
        # START_ZMARTBOT.sh
        start_zmartbot_mdc = """# 🚀 START_ZMARTBOT.sh - Official System Startup Orchestrator

## Purpose
Official ZmartBot system startup script with comprehensive orchestration, health checks, and automated service management.

## Critical Functions
- **Environment Validation**: Checks Python version, dependencies, and system requirements
- **Port Management**: Detects and resolves port conflicts automatically
- **Service Orchestration**: Starts backend API (port 8000) and frontend dashboard (port 3400)
- **Health Verification**: Validates all services are running correctly
- **Database Orchestration**: Initializes and manages all database connections
- **Rule #1 Compliance**: Ensures official startup procedure is followed

## Usage
```bash
# From project root directory
./START_ZMARTBOT.sh
```

## Key Features
- **One-Command Startup**: Complete system initialization
- **Automatic Conflict Resolution**: Handles port conflicts and process cleanup
- **Health Monitoring**: Real-time service health verification
- **Error Recovery**: Automatic retry mechanisms for failed services
- **Logging**: Comprehensive startup logging and status reporting

## Dependencies
- Python 3.11+
- Required Python packages (installed automatically)
- Port 8000 (backend API)
- Port 3400 (frontend dashboard)
- Database files and configurations

## Security
- Validates API keys and configurations
- Checks file permissions and security settings
- Ensures secure service startup

## Monitoring
- Real-time health checks for all services
- Performance metrics collection
- Error tracking and alerting

## Integration
- Orchestration Agent integration
- Database orchestrator startup
- Service registry management
- Port registry synchronization

## Error Handling
- Graceful failure recovery
- Automatic service restart
- Detailed error reporting
- Fallback mechanisms

## Status
✅ **ACTIVE** - Official startup method with orchestration integration
"""
        
        # STOP_ZMARTBOT.sh
        stop_zmartbot_mdc = """# 🛑 STOP_ZMARTBOT.sh - Official System Shutdown Orchestrator

## Purpose
Official ZmartBot system shutdown script with graceful service termination, cleanup, and resource management.

## Critical Functions
- **Graceful Shutdown**: Properly terminates all running services
- **Resource Cleanup**: Removes PID files and temporary resources
- **Database Protection**: Safely closes database connections
- **Port Release**: Frees all occupied ports
- **Orchestration Shutdown**: Stops orchestration agents and managers
- **Logging**: Records shutdown process and status

## Usage
```bash
# From project root directory
./STOP_ZMARTBOT.sh
```

## Key Features
- **Safe Termination**: Graceful shutdown of all services
- **Resource Management**: Complete cleanup of system resources
- **Database Safety**: Protected database shutdown procedures
- **Port Management**: Releases all occupied ports
- **Process Cleanup**: Removes all PID files and temporary processes

## Dependencies
- Running ZmartBot services
- PID files for service management
- Database connections to close
- Port registry for cleanup

## Security
- Secure credential cleanup
- Protected database shutdown
- Safe file handle closure
- Process isolation

## Monitoring
- Shutdown progress tracking
- Error detection and reporting
- Resource cleanup verification
- Status confirmation

## Integration
- Orchestration Agent shutdown
- Database orchestrator cleanup
- Service registry cleanup
- Port registry cleanup

## Error Handling
- Force termination if graceful shutdown fails
- Resource cleanup even on errors
- Error logging and reporting
- Fallback shutdown procedures

## Status
✅ **ACTIVE** - Official shutdown method with orchestration integration
"""
        
        # Master Orchestration Agent
        master_orchestration_mdc = """# 🎯 Master Orchestration Agent - System Orchestration Controller

## Purpose
Central orchestration controller for ZmartBot system, managing service lifecycle, dependencies, health monitoring, and automated operations.

## Critical Functions
- **Service Lifecycle Management**: Start, stop, restart, and monitor all services
- **Dependency Resolution**: Manages service dependencies and startup order
- **Health Monitoring**: Real-time health checks for all system components
- **Port Management**: Dynamic port assignment and conflict resolution
- **Database Orchestration**: Manages all database connections and operations
- **Error Recovery**: Automatic error detection and recovery mechanisms
- **Performance Optimization**: Resource optimization and load balancing

## Architecture
- **Central Controller**: Main orchestration logic and decision making
- **Service Registry**: Tracks all services and their states
- **Health Monitor**: Continuous health checking and alerting
- **Port Manager**: Dynamic port allocation and management
- **Database Orchestrator**: Database connection and operation management
- **Error Handler**: Error detection, logging, and recovery

## Key Features
- **Intelligent Startup**: Optimized service startup sequence
- **Real-time Monitoring**: Continuous health and performance monitoring
- **Automatic Recovery**: Self-healing capabilities for failed services
- **Resource Management**: Efficient resource allocation and cleanup
- **Scalability**: Support for multiple services and configurations
- **Logging**: Comprehensive logging and audit trails

## Service Management
- **Backend API Server**: Port 8000 management and monitoring
- **Frontend Dashboard**: Port 3400 management and monitoring
- **Database Services**: All database connections and operations
- **Monitoring Services**: Health checks and performance monitoring
- **Security Services**: Authentication and authorization management

## Health Monitoring
- **Service Health**: Real-time health status of all services
- **Performance Metrics**: CPU, memory, and resource usage
- **Error Tracking**: Error detection and alerting
- **Response Time**: Service response time monitoring
- **Availability**: Service availability tracking

## Error Recovery
- **Automatic Restart**: Failed service restart mechanisms
- **Fallback Procedures**: Alternative service configurations
- **Error Logging**: Comprehensive error logging and reporting
- **Alert System**: Error notification and alerting
- **Recovery Procedures**: Step-by-step recovery processes

## Integration Points
- **Service Registry**: Service discovery and registration
- **Port Registry**: Port allocation and management
- **Database Orchestrator**: Database operation management
- **Health Checker**: Health monitoring and validation
- **Logging System**: Centralized logging and monitoring

## Configuration
- **Service Configurations**: Individual service settings
- **Dependency Mappings**: Service dependency definitions
- **Health Check Rules**: Health monitoring configurations
- **Error Recovery Rules**: Error handling configurations
- **Performance Thresholds**: Performance monitoring settings

## Status
✅ **ACTIVE** - Core orchestration system with comprehensive management capabilities
"""
        
        # Write MDC files
        with open(self.mdc_dir / "START_ZMARTBOT.mdc", 'w', encoding='utf-8') as f:
            f.write(start_zmartbot_mdc)
            
        with open(self.mdc_dir / "STOP_ZMARTBOT.mdc", 'w', encoding='utf-8') as f:
            f.write(stop_zmartbot_mdc)
            
        with open(self.mdc_dir / "MasterOrchestrationAgent.mdc", 'w', encoding='utf-8') as f:
            f.write(master_orchestration_mdc)
    
    def generate_api_services_mdc(self):
        """Generate MDC for API services"""
        
        # Cryptometer Service
        cryptometer_mdc = """# 🔌 Cryptometer Service - Market Data API Integration

## Purpose
Cryptometer API integration service providing real-time market data, technical indicators, and comprehensive market analysis for ZmartBot trading operations.

## Critical Functions
- **Market Data Retrieval**: Real-time price data and market information
- **Technical Indicators**: 21+ technical indicators calculation and analysis
- **Multi-timeframe Analysis**: 15m, 1h, 4h, 1d timeframe support
- **Rate Limiting**: Intelligent API rate limiting and quota management
- **Data Caching**: Performance optimization through intelligent caching
- **Error Handling**: Robust error handling and fallback mechanisms

## API Endpoints
- **Market Data**: Real-time price and volume data
- **Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, etc.
- **Multi-timeframe**: Support for multiple timeframes
- **Symbol Information**: Comprehensive symbol metadata
- **Market Analysis**: Advanced market analysis and insights

## Key Features
- **Real-time Data**: Live market data with minimal latency
- **Comprehensive Indicators**: 21+ technical indicators
- **Multi-timeframe Support**: 15m, 1h, 4h, 1d timeframes
- **Intelligent Caching**: 5-minute cache with smart invalidation
- **Rate Limiting**: API quota management and optimization
- **Error Recovery**: Automatic retry and fallback mechanisms

## Data Processing
- **Price Data**: Real-time price feeds and historical data
- **Volume Analysis**: Volume-based analysis and insights
- **Technical Analysis**: Comprehensive technical indicator calculations
- **Market Sentiment**: Market sentiment analysis and scoring
- **Pattern Recognition**: Chart pattern identification and analysis

## Performance Optimization
- **Caching Strategy**: Intelligent data caching for performance
- **Rate Limiting**: API quota optimization and management
- **Batch Processing**: Efficient batch data processing
- **Memory Management**: Optimized memory usage and cleanup
- **Response Time**: Sub-second response times for critical data

## Error Handling
- **API Failures**: Graceful handling of API failures
- **Rate Limit Exceeded**: Intelligent rate limit management
- **Network Issues**: Network error recovery and retry logic
- **Data Validation**: Comprehensive data validation and sanitization
- **Fallback Mechanisms**: Alternative data sources when available

## Integration
- **Frontend Dashboard**: Real-time data display and visualization
- **Trading Engine**: Market data for trading decisions
- **Alert System**: Market condition alerts and notifications
- **Database**: Historical data storage and retrieval
- **Analytics**: Market analysis and reporting

## Configuration
- **API Keys**: Secure API key management
- **Rate Limits**: Configurable rate limiting settings
- **Cache Settings**: Cache duration and invalidation rules
- **Timeout Settings**: Request timeout configurations
- **Retry Logic**: Retry attempt and backoff settings

## Status
✅ **ACTIVE** - Core market data service with comprehensive API integration
"""
        
        # KuCoin Service
        kucoin_mdc = """# 🏦 KuCoin Service - Trading Platform Integration

## Purpose
KuCoin API integration service for trading operations, account management, and real-time market data access in the ZmartBot trading system.

## Critical Functions
- **Trading Operations**: Buy/sell order execution and management
- **Account Management**: Account information and balance tracking
- **Market Data**: Real-time market data and order book access
- **Portfolio Management**: Portfolio tracking and position management
- **Risk Management**: Position sizing and risk control
- **Order Management**: Order placement, modification, and cancellation

## API Endpoints
- **Trading**: Order placement and management
- **Account**: Account information and balances
- **Market Data**: Real-time market data feeds
- **Portfolio**: Portfolio and position management
- **Risk Management**: Risk control and position sizing

## Key Features
- **Real-time Trading**: Live order execution and management
- **Account Integration**: Full account access and management
- **Portfolio Tracking**: Real-time portfolio monitoring
- **Risk Controls**: Built-in risk management features
- **Order Management**: Comprehensive order lifecycle management
- **Market Data**: Real-time market data integration

## Trading Operations
- **Order Execution**: Market and limit order execution
- **Position Management**: Position tracking and management
- **Risk Control**: Position sizing and risk management
- **Order Modification**: Order modification and cancellation
- **Trade History**: Complete trade history and analysis

## Account Management
- **Balance Tracking**: Real-time balance monitoring
- **Account Information**: Account details and settings
- **API Key Management**: Secure API key handling
- **Permission Management**: API permission and scope management
- **Security**: Account security and protection

## Risk Management
- **Position Sizing**: Automatic position sizing calculations
- **Risk Limits**: Configurable risk limits and controls
- **Stop Loss**: Automatic stop loss management
- **Take Profit**: Take profit order management
- **Portfolio Risk**: Portfolio-level risk management

## Integration
- **Trading Engine**: Order execution and management
- **Portfolio Manager**: Portfolio tracking and analysis
- **Risk Manager**: Risk control and management
- **Alert System**: Trading alerts and notifications
- **Database**: Trade history and account data storage

## Configuration
- **API Keys**: Secure API key configuration
- **Trading Parameters**: Trading strategy parameters
- **Risk Settings**: Risk management configurations
- **Order Settings**: Order execution settings
- **Account Settings**: Account-specific configurations

## Status
✅ **ACTIVE** - Core trading platform integration with comprehensive functionality
"""
        
        # Write MDC files
        with open(self.mdc_dir / "CryptometerService.mdc", 'w', encoding='utf-8') as f:
            f.write(cryptometer_mdc)
            
        with open(self.mdc_dir / "KuCoinService.mdc", 'w', encoding='utf-8') as f:
            f.write(kucoin_mdc)
    
    def generate_database_services_mdc(self):
        """Generate MDC for database services"""
        
        # My Symbols Service
        my_symbols_mdc = """# 🗄️ My Symbols Service - Portfolio Management Database

## Purpose
My Symbols service manages the core portfolio database, symbol tracking, and portfolio analytics for ZmartBot trading operations.

## Critical Functions
- **Portfolio Management**: Symbol portfolio tracking and management
- **Symbol Data**: Comprehensive symbol information and metadata
- **Portfolio Analytics**: Portfolio performance and risk analysis
- **Data Persistence**: Reliable data storage and retrieval
- **Real-time Updates**: Live portfolio updates and synchronization
- **Historical Data**: Historical portfolio and symbol data

## Database Schema
- **Symbols Table**: Core symbol information and metadata
- **Portfolio Table**: Portfolio composition and tracking
- **Performance Table**: Performance metrics and analytics
- **Risk Table**: Risk metrics and position data
- **History Table**: Historical data and audit trails

## Key Features
- **Portfolio Tracking**: Real-time portfolio monitoring
- **Symbol Management**: Comprehensive symbol data management
- **Performance Analytics**: Portfolio performance analysis
- **Risk Management**: Portfolio risk metrics and monitoring
- **Data Integrity**: ACID compliance and data validation
- **Backup & Recovery**: Automated backup and recovery procedures

## Portfolio Management
- **Symbol Addition**: Add new symbols to portfolio
- **Symbol Removal**: Remove symbols from portfolio
- **Position Tracking**: Real-time position monitoring
- **Performance Tracking**: Portfolio performance metrics
- **Risk Monitoring**: Portfolio risk assessment

## Data Operations
- **CRUD Operations**: Create, read, update, delete operations
- **Bulk Operations**: Efficient bulk data operations
- **Query Optimization**: Optimized database queries
- **Indexing**: Strategic database indexing for performance
- **Caching**: Intelligent data caching strategies

## Analytics & Reporting
- **Performance Metrics**: Portfolio performance calculations
- **Risk Analytics**: Risk assessment and analysis
- **Trend Analysis**: Portfolio trend identification
- **Comparative Analysis**: Benchmark and comparison analysis
- **Reporting**: Automated report generation

## Integration
- **Trading Engine**: Portfolio data for trading decisions
- **Risk Manager**: Portfolio risk data integration
- **Analytics Engine**: Portfolio analytics and reporting
- **Frontend Dashboard**: Portfolio display and visualization
- **Alert System**: Portfolio-based alerts and notifications

## Configuration
- **Database Settings**: Database connection and configuration
- **Performance Settings**: Query optimization settings
- **Backup Settings**: Backup frequency and retention
- **Security Settings**: Database security and access control
- **Monitoring Settings**: Database monitoring and alerting

## Status
✅ **ACTIVE** - Core portfolio management service with comprehensive database functionality
"""
        
        # Write MDC file
        with open(self.mdc_dir / "MySymbolsService.mdc", 'w', encoding='utf-8') as f:
            f.write(my_symbols_mdc)
    
    def generate_monitoring_services_mdc(self):
        """Generate MDC for monitoring services"""
        
        # Health Check Service
        health_check_mdc = """# 📈 Health Check Service - System Health Monitoring

## Purpose
Comprehensive health monitoring service for ZmartBot system, providing real-time health checks, performance monitoring, and automated alerting.

## Critical Functions
- **Service Health Monitoring**: Real-time health status of all services
- **Performance Metrics**: CPU, memory, and resource usage tracking
- **Error Detection**: Automatic error detection and alerting
- **Response Time Monitoring**: Service response time tracking
- **Availability Tracking**: Service availability and uptime monitoring
- **Automated Recovery**: Automatic service recovery and restart

## Monitoring Components
- **Backend API**: Port 8000 health monitoring
- **Frontend Dashboard**: Port 3400 health monitoring
- **Database Services**: Database connection and performance monitoring
- **External APIs**: External API health and response monitoring
- **System Resources**: CPU, memory, and disk usage monitoring

## Key Features
- **Real-time Monitoring**: Continuous health status monitoring
- **Performance Tracking**: Comprehensive performance metrics
- **Error Alerting**: Immediate error notification and alerting
- **Automated Recovery**: Self-healing capabilities for failed services
- **Historical Data**: Health and performance historical data
- **Customizable Alerts**: Configurable alert thresholds and notifications

## Health Checks
- **Service Availability**: Service up/down status monitoring
- **Response Time**: Service response time measurement
- **Error Rate**: Error rate tracking and analysis
- **Resource Usage**: CPU, memory, and disk usage monitoring
- **Database Health**: Database connection and performance health
- **API Health**: External API health and availability

## Performance Metrics
- **Response Time**: Average, min, max response times
- **Throughput**: Requests per second and data throughput
- **Error Rate**: Error percentage and error types
- **Resource Usage**: CPU, memory, disk usage percentages
- **Availability**: Service uptime and availability percentages
- **Latency**: Network and service latency measurements

## Alerting System
- **Threshold Alerts**: Configurable threshold-based alerting
- **Error Alerts**: Immediate error notification
- **Performance Alerts**: Performance degradation alerts
- **Resource Alerts**: Resource usage alerts
- **Custom Alerts**: Custom alert conditions and notifications

## Integration
- **Orchestration Agent**: Health data for orchestration decisions
- **Alert System**: Health-based alerting and notifications
- **Dashboard**: Health status display and visualization
- **Logging System**: Health data logging and analysis
- **Recovery System**: Automated recovery and restart procedures

## Configuration
- **Health Check Intervals**: Configurable check frequencies
- **Alert Thresholds**: Customizable alert thresholds
- **Recovery Settings**: Recovery procedure configurations
- **Monitoring Scope**: Configurable monitoring scope
- **Notification Settings**: Alert notification configurations

## Status
✅ **ACTIVE** - Core health monitoring service with comprehensive system oversight
"""
        
        # Write MDC file
        with open(self.mdc_dir / "HealthCheckService.mdc", 'w', encoding='utf-8') as f:
            f.write(health_check_mdc)
    
    def generate_security_components_mdc(self):
        """Generate MDC for security components"""
        
        # Security Scan Service
        security_scan_mdc = """# 🔒 Security Scan Service - Comprehensive Security Monitoring

## Purpose
Comprehensive security scanning and monitoring service for ZmartBot system, providing secret detection, vulnerability scanning, and security compliance monitoring.

## Critical Functions
- **Secret Detection**: Automated detection of exposed secrets and credentials
- **Vulnerability Scanning**: Security vulnerability identification and assessment
- **Compliance Monitoring**: Security compliance and policy enforcement
- **Access Control**: API key and credential access management
- **Security Logging**: Comprehensive security event logging
- **Threat Detection**: Security threat identification and alerting

## Security Tools
- **Gitleaks**: Git repository secret detection
- **Detect-Secrets**: Comprehensive secret detection framework
- **Custom Scanners**: ZmartBot-specific security scanners
- **API Key Manager**: Secure API key management and rotation
- **Credential Protection**: Encrypted credential storage and access

## Key Features
- **Automated Scanning**: Continuous security scanning and monitoring
- **Secret Detection**: Real-time secret and credential detection
- **Vulnerability Assessment**: Comprehensive vulnerability scanning
- **Compliance Checking**: Security compliance validation
- **Access Control**: Secure access control and management
- **Security Logging**: Detailed security event logging

## Scanning Capabilities
- **Code Scanning**: Source code security analysis
- **Configuration Scanning**: Configuration file security analysis
- **Dependency Scanning**: Third-party dependency security analysis
- **API Scanning**: API endpoint security analysis
- **Database Scanning**: Database security configuration analysis

## Secret Detection
- **API Keys**: Detection of exposed API keys
- **Passwords**: Detection of hardcoded passwords
- **Tokens**: Detection of authentication tokens
- **Credentials**: Detection of database credentials
- **Private Keys**: Detection of private cryptographic keys

## Compliance Monitoring
- **Security Policies**: Security policy compliance checking
- **Access Controls**: Access control policy validation
- **Data Protection**: Data protection compliance monitoring
- **Audit Trails**: Security audit trail maintenance
- **Reporting**: Security compliance reporting

## Integration
- **CI/CD Pipeline**: Automated security scanning in deployment
- **Alert System**: Security alert notification system
- **Logging System**: Security event logging and analysis
- **Dashboard**: Security status display and visualization
- **Recovery System**: Security incident response and recovery

## Configuration
- **Scan Intervals**: Configurable scanning frequencies
- **Alert Thresholds**: Security alert threshold settings
- **Scan Scope**: Configurable scanning scope and targets
- **Compliance Rules**: Security compliance rule configurations
- **Notification Settings**: Security alert notification settings

## Status
✅ **ACTIVE** - Core security service with comprehensive protection capabilities
"""
        
        # Write MDC file
        with open(self.mdc_dir / "SecurityScanService.mdc", 'w', encoding='utf-8') as f:
            f.write(security_scan_mdc)
    
    def generate_all_mdc(self):
        """Generate all MDC documentation"""
        print("🚀 Generating comprehensive MDC documentation...")
        
        print("📋 Generating orchestration MDC...")
        self.generate_orchestration_mdc()
        
        print("🔌 Generating API services MDC...")
        self.generate_api_services_mdc()
        
        print("🗄️ Generating database services MDC...")
        self.generate_database_services_mdc()
        
        print("📈 Generating monitoring services MDC...")
        self.generate_monitoring_services_mdc()
        
        print("🔒 Generating security components MDC...")
        self.generate_security_components_mdc()
        
        print("✅ All MDC documentation generated successfully!")

def main():
    """Main entry point for MDC generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MDC Generator for ZmartBot System Documentation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--orchestration-only", action="store_true", help="Generate only orchestration MDC")
    parser.add_argument("--api-only", action="store_true", help="Generate only API services MDC")
    parser.add_argument("--database-only", action="store_true", help="Generate only database services MDC")
    parser.add_argument("--monitoring-only", action="store_true", help="Generate only monitoring services MDC")
    parser.add_argument("--security-only", action="store_true", help="Generate only security components MDC")
    
    args = parser.parse_args()
    
    generator = MDCGenerator(args.project_root)
    
    if args.orchestration_only:
        generator.generate_orchestration_mdc()
    elif args.api_only:
        generator.generate_api_services_mdc()
    elif args.database_only:
        generator.generate_database_services_mdc()
    elif args.monitoring_only:
        generator.generate_monitoring_services_mdc()
    elif args.security_only:
        generator.generate_security_components_mdc()
    else:
        generator.generate_all_mdc()

if __name__ == "__main__":
    main()
