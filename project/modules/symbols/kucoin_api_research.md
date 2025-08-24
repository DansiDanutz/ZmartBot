# KuCoin API Research for ZmartBot Symbol Management Module

## API Structure Overview

### Base URLs
- **Spot & Margin REST**: https://api.kucoin.com
- **Futures REST**: https://api-futures.kucoin.com
- **Broker REST**: https://api-broker.kucoin.com
- **Websocket**: Dynamic URLs obtained via token endpoints

### API Permissions Required
- **General**: Read-only operations (account info, order info)
- **Futures**: Required for futures trading operations
- **Withdrawal**: For asset transfers (requires IP restriction)
- **FlexTransfers**: For cross-account transfers

## Futures Trading API Endpoints

### WebSocket Public Channels

#### Get Ticker v2
- **Topic**: `/contractMarket/tickerV2:{symbol}`
- **Push Frequency**: Real-time
- **Data Provided**:
  - Symbol name
  - Best bid/ask prices and sizes
  - Timestamp (nanosecond precision)
- **Use Case**: Real-time price monitoring for scoring algorithms

**Sample Response**:
```json
{
  "subject": "tickerV2",
  "topic": "/contractMarket/tickerV2:XBTUSDTM",
  "data": {
    "symbol": "XBTUSDTM",
    "bestBidSize": 795,
    "bestBidPrice": 3200.0,
    "bestAskPrice": 3600.0,
    "bestAskSize": 284,
    "ts": 1553846081210004941
  }
}
```



#### Level2 - Market Data
- **Topic**: `/contractMarket/level2:{symbol}`
- **Push Frequency**: Real-time incremental updates
- **Data Provided**:
  - Full order book depth
  - Sequence numbers for data integrity
  - Price, side, and quantity changes
  - Timestamp information
- **Use Case**: Liquidity analysis, spread calculation, market depth scoring

**Key Features**:
- Incremental updates with sequence numbers
- Requires calibration with REST snapshot
- Real-time order book maintenance
- Size of "0" indicates price level removal

**Sample Response**:
```json
{
  "subject": "level2",
  "topic": "/contractMarket/level2:XBTUSDTM",
  "type": "message",
  "data": {
    "sequence": 18,
    "change": "5000.0,sell,83",
    "timestamp": 1551770400000
  }
}
```

**Calibration Process**:
1. Cache websocket Level2 data flow
2. Get REST Level2 snapshot
3. Playback cached data
4. Apply new updates based on sequence
5. Update local order book
6. Handle sequence gaps with REST requests


#### Match Execution Data
- **Topic**: `/contractMarket/execution:{symbol}`
- **Push Frequency**: Real-time per trade execution
- **Data Provided**:
  - Symbol name
  - Sequence number (increasing but not consecutive)
  - Trade side (buy/sell from taker perspective)
  - Filled quantity and price
  - Taker and maker order IDs
  - Trade ID and timestamp (nanosecond precision)
- **Use Case**: Volume analysis, momentum scoring, trade flow analysis

**Sample Response**:
```json
{
  "topic": "/contractMarket/execution:XBTUSDTM",
  "type": "message",
  "subject": "match",
  "sn": 1743169228057,
  "data": {
    "symbol": "XBTUSDTM",
    "sequence": 1743169228057,
    "side": "buy",
    "size": 5,
    "price": "72137.3",
    "takerOrderId": "166754573174730752",
    "makerOrderId": "166754559966867456",
    "tradeId": "1743169228057",
    "ts": 1712570590399000000
  }
}
```

### REST API Endpoints

#### Get Symbols List
- **Endpoint**: `GET /api/v1/contracts/active`
- **Base URL**: https://api-futures.kucoin.com
- **Rate Limit**: 3 weight units
- **Authentication**: Not required (public endpoint)

**Comprehensive Symbol Data Available**:
- Basic Info: symbol, rootSymbol, type, status
- Trading Specs: lotSize, tickSize, maxOrderQty, maxPrice
- Margin Requirements: initialMargin, maintainMargin, maxLeverage
- Fee Structure: makerFeeRate, takerFeeRate
- Risk Management: maxRiskLimit, minRiskLimit, riskStep
- Market Data: markPrice, indexPrice, lastTradePrice
- 24h Statistics: turnoverOf24h, volumeOf24h, highPrice, lowPrice, priceChg, priceChgPct
- Funding: fundingFeeRate, predictedFundingFeeRate, nextFundingRateTime
- Open Interest: openInterest
- Index Sources: sourceExchanges array
- Trading Limits: buyLimit, sellLimit

## Integration Notes for Existing KuCoin Implementation

Since KuCoin integration is already implemented, the Symbol Management module should:

1. **Leverage Existing Connections**: Use current API connections and authentication
2. **Build on Current Data Flows**: Extend existing data ingestion pipelines
3. **Integrate with Current Architecture**: Follow established patterns and conventions
4. **Enhance Current Capabilities**: Add scoring and management logic on top of existing data

## Key Data Sources for Symbol Management Module

### Real-time Data Streams (WebSocket)
1. **Ticker Data**: Price, bid/ask, volume updates
2. **Order Book**: Level2 market depth for liquidity analysis
3. **Trade Execution**: Real-time trade flow for momentum analysis

### Snapshot Data (REST API)
1. **Symbol Metadata**: Contract specifications, trading rules
2. **Market Statistics**: 24h volume, price changes, open interest
3. **Funding Information**: Rates, predictions, timing

### Derived Metrics for Scoring
1. **Liquidity Metrics**: Spread, depth, order book imbalance
2. **Volatility Metrics**: Price movement patterns, ATR
3. **Volume Metrics**: Trading activity, volume profile
4. **Momentum Metrics**: Price trends, breakout patterns
5. **Market Structure**: Funding rates, open interest changes

## Next Steps for Module Development

1. **Database Schema Design**: Tables for symbol management, scoring, history
2. **Core Management System**: Portfolio tracking, replacement logic
3. **Scoring Algorithms**: Multi-factor analysis and ranking
4. **Signal Processing**: Integration with Signal Center
5. **Multi-Agent Scanning**: Validation and consensus system
6. **Visualization Components**: Charts, dashboards, analytics
7. **Management Interface**: Configuration, monitoring, control

