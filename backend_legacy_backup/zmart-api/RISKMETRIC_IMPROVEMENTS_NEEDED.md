# RiskMetric Module - Improvements Needed

## Missing Features to Add

### 1. **Service Lifecycle Methods**
- `async def start()` - Initialize connections, load data
- `async def stop()` - Cleanup resources, close connections
- `async def get_service_status()` - Return health/status info

### 2. **Comprehensive Screener**
- `async def get_comprehensive_screener()` - Return all symbols with current risk analysis
- Should include sorting by risk level, filtering by tradeable status

### 3. **Historical Data Integration**
- `async def get_historical_risk(symbol, days)` - Get risk history
- `async def record_outcome(symbol, actual_value, timestamp)` - For learning/tracking

### 4. **Real-Time Price Integration**
- Currently requires price to be passed in
- Should integrate with market data service to fetch current prices
- Add fallback to multiple price sources

### 5. **Caching Layer**
- Add Redis caching for frequently accessed data
- Cache risk calculations for recent prices
- TTL-based cache invalidation

### 6. **Advanced Analytics**
- `async def get_risk_momentum(symbol)` - Track risk direction/velocity
- `async def get_correlation_matrix()` - Cross-symbol risk correlations
- `async def get_market_risk_index()` - Overall market risk score

### 7. **Alert System**
- `async def check_risk_alerts(symbol)` - Check if risk crosses thresholds
- Risk band transition notifications
- Extreme risk warnings

### 8. **Batch Operations Enhancement**
- Parallel processing for batch operations
- Progress callbacks for long-running operations
- Chunked processing for large batches

### 9. **Data Validation & Error Handling**
- Input validation for all public methods
- Graceful degradation when data unavailable
- Detailed error messages with recovery suggestions

### 10. **Performance Monitoring**
- Method execution timing
- Query performance metrics
- Resource usage tracking

## Code Additions Needed

### 1. Add Service Lifecycle Methods
```python
async def start(self):
    """Initialize the RiskMetric service"""
    logger.info("Starting UnifiedRiskMetric service...")
    # Load any cached data
    # Verify database connection
    # Pre-calculate common values
    self._running = True
    logger.info("UnifiedRiskMetric service started")

async def stop(self):
    """Stop the RiskMetric service"""
    logger.info("Stopping UnifiedRiskMetric service...")
    self._running = False
    # Close database connections
    # Save any pending data
    logger.info("UnifiedRiskMetric service stopped")

async def get_service_status(self) -> Dict[str, Any]:
    """Get service status"""
    return {
        "status": "running" if hasattr(self, '_running') and self._running else "stopped",
        "symbols_count": len(self.SYMBOL_BOUNDS),
        "database_path": self.db_path,
        "last_update": datetime.now().isoformat()
    }
```

### 2. Add Comprehensive Screener
```python
async def get_comprehensive_screener(self) -> Dict[str, Any]:
    """Get comprehensive risk analysis for all symbols"""
    symbols = list(self.SYMBOL_BOUNDS.keys())
    assessments = await self.batch_assess(symbols)
    
    # Sort by risk value
    sorted_assessments = sorted(assessments, key=lambda x: x.risk_value)
    
    # Categorize by risk zones
    low_risk = [a for a in assessments if a.risk_value < 0.3]
    medium_risk = [a for a in assessments if 0.3 <= a.risk_value < 0.7]
    high_risk = [a for a in assessments if a.risk_value >= 0.7]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_symbols": len(assessments),
        "tradeable_count": sum(1 for a in assessments if a.tradeable),
        "risk_zones": {
            "low": len(low_risk),
            "medium": len(medium_risk),
            "high": len(high_risk)
        },
        "symbols": [asdict(a) for a in sorted_assessments],
        "top_opportunities": [asdict(a) for a in assessments if a.tradeable][:5]
    }
```

### 3. Add Market Data Integration
```python
async def get_current_price(self, symbol: str) -> Optional[float]:
    """Get current market price for symbol"""
    try:
        # Try primary source (would integrate with actual market data service)
        from src.services.market_data_service import get_price
        price = await get_price(symbol)
        if price:
            return price
    except:
        pass
    
    # Fallback to geometric mean of bounds
    bounds = self.SYMBOL_BOUNDS.get(symbol)
    if bounds:
        return math.sqrt(bounds['min'] * bounds['max'])
    
    return None
```

### 4. Add Caching
```python
def __init__(self, db_path: str = "data/unified_riskmetric.db"):
    # ... existing init code ...
    self._cache = {}  # Simple in-memory cache
    self._cache_ttl = 300  # 5 minutes

def _get_cache_key(self, symbol: str, price: float) -> str:
    """Generate cache key"""
    return f"{symbol}:{price:.2f}"

def _get_cached(self, key: str) -> Optional[Any]:
    """Get from cache if not expired"""
    if key in self._cache:
        data, timestamp = self._cache[key]
        if (datetime.now() - timestamp).seconds < self._cache_ttl:
            return data
    return None

def _set_cache(self, key: str, data: Any):
    """Set cache with timestamp"""
    self._cache[key] = (data, datetime.now())
```

### 5. Add Risk Momentum
```python
async def get_risk_momentum(self, symbol: str, days: int = 7) -> Dict[str, Any]:
    """Calculate risk momentum (direction and velocity)"""
    # This would query historical risk values
    # For now, return a placeholder
    return {
        "symbol": symbol,
        "momentum": 0.0,  # Positive = increasing risk
        "velocity": 0.0,  # Rate of change
        "trend": "neutral",  # up/down/neutral
        "days_analyzed": days
    }
```

## Priority Implementation Order

1. **High Priority** (Needed immediately):
   - Service lifecycle methods (start, stop, get_service_status)
   - Comprehensive screener
   - Current price integration

2. **Medium Priority** (Nice to have):
   - Caching layer
   - Risk momentum
   - Alert system

3. **Low Priority** (Future enhancements):
   - Correlation matrix
   - Advanced analytics
   - Performance monitoring

## Testing Requirements

Each new feature should include:
1. Unit tests
2. Integration tests
3. Performance benchmarks
4. Error case handling

## Documentation Needs

- API documentation for new methods
- Usage examples
- Performance characteristics
- Migration guide for systems using old implementations