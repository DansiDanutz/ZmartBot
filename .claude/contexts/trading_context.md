# Trading Domain Context

## WhaleAlerts
**File**: .cursor/rules/WhaleAlerts.mdc
**Relevance**: 0
**Size**: 4012 bytes

**Content**: 
## Description
Core service component of the ZmartBot ecosystem providing essential functionality.




## ...

---

## MySymbolsDatabase
**File**: .cursor/rules/MySymbolsDatabase.mdc
**Relevance**: 0
**Size**: 31943 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | @agent: SymbolValidator | - **File Path**: `src/data/my_symbols.db` | - **Database Type**: SQLite...
**Key Info**: All database access requires valid API key | Backend validates request and permissions

---

## LiveAlerts
**File**: .cursor/rules/LiveAlerts.mdc
**Relevance**: 0
**Size**: 2071 bytes

**Content**: 
## Description
Core service component of the ZmartBot ecosystem providing essential functionality.




## ...

---

## MySymbolsService
**File**: .cursor/rules/MySymbolsService.mdc
**Relevance**: 0
**Size**: 3180 bytes

**Content**: # 🗄️ My Symbols Service - Portfolio Management Database


## Purpose
My Symbols service manages the core portfolio database, symbol tracking, and portfolio analytics for ZmartBot trading operations.

## Description
My Symbols service manages the core portfolio database, symbol tracking, and portfolio analytics ...

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

## ...

---

## MySymbols
**File**: .cursor/rules/MySymbols.mdc
**Relevance**: 0
**Size**: 22212 bytes

**Summary**: ## Description | Core service component of the ZmartBot ecosystem providing essential functionality. | @agent: SymbolValidator | - **Binance Futures**: Must be available on Binance Futures market

---

## MessiAlerts
**File**: .cursor/rules/MessiAlerts.mdc
**Relevance**: 0
**Size**: 2063 bytes

**Content**: 
## Description
Core service component of the ZmartBot ecosystem providing essential functionality.




## ...

---

## integration-NewService-MySymbolsDatabase
**File**: .cursor/rules/integration/winners/integration-NewService-MySymbolsDatabase.mdc
**Relevance**: 0
**Size**: 3149 bytes

**Content**: # integration-NewService-MySymbolsDatabase.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: NewService + MySymbolsDatabase
> Winner: Selected from automated analysis (Score: 90)

## Purpose
The integration of NewService and MySymbolsDatabase could provide significant benefits for the ZmartBot system, including unified service management, enhanced system stability, and improved service tracking and symbol management. However, the integration process would require careful planning and execution to ensure compliance with all rules and avoid system crashes. Despite the medium level of implementation complexity, the potential benefits make this integration highly recommended.

## Integration Analysis
**Score**: 90/100
**Complexity**: Medium
**Pattern**: Service Orchestration

## Key Benefits
- Unified service management and symbol database
- Enhanced system stability and reliability
- Improved service tracking and symbol management

## Implementation Details
**Complexity Reason**: While the services are well-defined and follow strict rules, the integration process will require careful planning and execution to ensure compliance with all rules and avoid system crashes. The need for port and passport assignments adds an extra layer of complexity.

## Potential Challenges
- Ensuring all rules are followed during integration
- Managing port and passport assignments
- Maintaining system stability during integration

## ...

---

## integration-driver-MySymbols
**File**: .cursor/rules/discovery/integrations/winners/integration-driver-MySymbols.mdc
**Relevance**: 0
**Size**: 3428 bytes

**Content**: # integration-driver-MySymbols.mdc
> Type: integration | Version: 1.0.0 | Owner: zmartbot | Components: driver + MySymbols
> Winner: Selected from automated analysis (Score: 75)

## Purpose
The integration of the driver and MySymbols services presents a promising opportunity to enhance the functionality and efficiency of the ZmartBot ecosystem. However, careful consideration should be given to the potential challenges and complexities involved in the integration process.

## Integration Analysis
**Score**: 75/100
**Complexity**: Medium
**Pattern**: API Gateway Integration Pattern would be best suited for this scenario. The driver service can act as a gateway for the MySymbols service, handling requests and responses between the service and the ZmartBot ecosystem.

## Key Benefits
- Increased efficiency in symbol validation and parsing
- Improved system observability and error handling through the integration of the driver's logging and notification systems
- Enhanced system scalability due to the microservice architecture

## Implementation Details
**Complexity Reason**: While the services seem to be designed with integration in mind, there are still areas that require manual review and configuration. Additionally, the driver service's dependencies and environment variables are yet to be determined, which could potentially complicate the integration process.

## ...

---

## winner-driver-MySymbols-20250827-160211
**File**: .cursor/rules/discovery/integrations/winners/winner-driver-MySymbols-20250827-160211.mdc
**Relevance**: 0
**Size**: 7556 bytes

**Summary**: # winner-driver-MySymbols-20250827-160211.mdc | ## 🏆 WINNER INTEGRATION - Official Selection | > Type: integration-winner | Version: 1.0.0 | Owner: zmartbot | Status: SELECTED
**Compressed**: 

---

## mysymbols_server
**File**: .cursor/rules/discovery/services/mysymbols_server.mdc
**Relevance**: 0
**Size**: 54235 bytes

**Summary**: # Mysymbols_Server - Merged MDC Configuration | ## 🔗 Merged from 3 duplicate files | Get database connection | - **Dependencies:** To be determined | - **Env Vars:** To be determined
**Key Info**: 8201 | backend

---

