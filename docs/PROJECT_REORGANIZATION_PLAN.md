# ZmartBot Project Reorganization Plan

## Current Issues Identified

### Structural Problems
- Multiple overlapping directories (backend, zmart-platform, frontend, kingfisher-module)
- Missing package.json files in frontend directories
- Duplicate configuration files across modules
- Mixed documentation and source code at root level
- Inconsistent naming conventions

### Technical Debt
- Multiple server startup scripts with unclear purposes
- Missing dependency management in frontend
- Unclear module boundaries
- Inconsistent API route organization

## Proposed Architecture

```
ZmartBot/
├── docs/                          # Documentation
├── src/                           # Source code
│   ├── backend/                   # Backend services
│   │   ├── api/                   # Main API service
│   │   ├── kingfisher/            # KingFisher module
│   │   └── shared/                 # Shared backend utilities
│   ├── frontend/                  # Frontend applications
│   │   ├── dashboard/             # Main trading dashboard
│   │   └── kingfisher-ui/         # KingFisher dashboard
│   └── modules/                   # Business logic modules
│       ├── trading/               # Trading engine
│       ├── risk-analysis/         # Risk management
│       └── data-processing/       # Data processing
├── config/                        # Configuration files
├── scripts/                       # Build and deployment scripts
├── tests/                         # Test suites
└── deployments/                   # Deployment configurations
```

## Implementation Steps

### Phase 1: Foundation
1. Create proper directory structure
2. Move documentation to docs/ directory
3. Consolidate configuration files
4. Fix missing package.json files

### Phase 2: Backend Reorganization
1. Consolidate backend services
2. Standardize API structure
3. Fix dependency management
4. Create proper module boundaries

### Phase 3: Frontend Reorganization
1. Fix frontend project structure
2. Standardize build configurations
3. Create proper component organization
4. Fix missing dependencies

### Phase 4: Deployment & Documentation
1. Create unified deployment scripts
2. Update documentation
3. Create development guides
4. Set up proper testing structure