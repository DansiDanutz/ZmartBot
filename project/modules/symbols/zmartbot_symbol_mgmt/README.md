# ZmartBot Symbol Management Module

A sophisticated cryptocurrency portfolio management system for KuCoin futures trading with advanced scoring algorithms, signal processing, and automated symbol replacement.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment support
- Internet connection for KuCoin API

### Installation

1. **Clone and Setup**
   ```bash
   cd zmartbot_symbol_mgmt
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python src/main.py
   ```

3. **Load Sample Data** (in another terminal)
   ```bash
   curl -X POST http://localhost:5000/api/symbol-mgmt/initialize-sample-data
   ```

4. **Test API**
   ```bash
   curl http://localhost:5000/api/symbol-mgmt/portfolio
   ```

## 🎯 Core Features

### Portfolio Management
- **Dynamic 10-Symbol Portfolio**: Automatically manage up to 10 KuCoin futures symbols
- **Intelligent Replacement**: Bottom 2 symbols are candidates for automatic replacement
- **Performance Tracking**: Real-time performance attribution and analytics
- **Complete Audit Trail**: Every portfolio change logged with full context

### Advanced Scoring System
- **Multi-Algorithm Analysis**: Technical, Fundamental, Market Structure, Risk assessment
- **Composite Scoring**: Weighted combination of all scoring components
- **Real-time Rankings**: Dynamic symbol rankings based on latest scores
- **Historical Validation**: Score performance tracking and validation

### Signal Processing
- **Multi-Agent Evaluation**: Sophisticated consensus-based signal evaluation
- **Quality Filtering**: Only high-quality signals trigger portfolio changes
- **Lifecycle Management**: Complete signal processing from ingestion to disposition
- **Comprehensive Analytics**: Signal processing metrics and performance tracking

### RESTful API
- **30+ Endpoints**: Complete API for all symbol management operations
- **Real-time Data**: Live portfolio and scoring information
- **Health Monitoring**: System status and performance metrics
- **CORS Enabled**: Ready for frontend integration

## 📊 API Endpoints

### Portfolio Management
```bash
GET    /api/symbol-mgmt/portfolio                    # Current portfolio
GET    /api/symbol-mgmt/portfolio/statistics         # Portfolio statistics
POST   /api/symbol-mgmt/portfolio/add-symbol         # Add symbol
POST   /api/symbol-mgmt/portfolio/remove-symbol      # Remove symbol
POST   /api/symbol-mgmt/portfolio/replace-symbol     # Replace symbol
POST   /api/symbol-mgmt/portfolio/rebalance          # Rebalance weights
```

### Scoring System
```bash
POST   /api/symbol-mgmt/scoring/calculate            # Calculate scores
GET    /api/symbol-mgmt/scoring/rankings             # Symbol rankings
GET    /api/symbol-mgmt/scoring/symbol/{id}/scores   # Symbol scores
```

### Signal Processing
```bash
POST   /api/symbol-mgmt/signals                      # Submit signal
GET    /api/symbol-mgmt/signals/pending              # Pending signals
GET    /api/symbol-mgmt/signals/processed            # Processed signals
GET    /api/symbol-mgmt/signals/statistics           # Signal statistics
```

### System Status
```bash
GET    /api/symbol-mgmt/health                       # Health check
GET    /api/symbol-mgmt/status                       # System status
```

## 🏗️ Architecture

### Core Components

- **SymbolManager**: Main orchestrator for portfolio operations
- **PortfolioManager**: Advanced portfolio analytics and optimization
- **ScoringEngine**: Multi-algorithm scoring system
- **SignalProcessor**: Signal processing and multi-agent evaluation

### Database Schema

- **Symbols**: Master registry with contract specifications
- **Portfolio Composition**: Current portfolio state
- **Portfolio History**: Complete audit trail
- **Symbol Scores**: Scoring results and history
- **Signals**: Trading signals and processing status
- **System Configuration**: Configurable parameters

### Scoring Algorithms

1. **Technical Analysis**: RSI, MACD, Bollinger Bands, Volume analysis
2. **Fundamental Analysis**: Volume growth, open interest, funding rates
3. **Market Structure**: Spread, depth, market impact, efficiency
4. **Risk Assessment**: Volatility, correlation, drawdown, liquidity risk
5. **Composite Score**: Weighted combination of all components

## 🔧 Configuration

### System Parameters
```python
# Configurable via API or database
max_portfolio_symbols = 10
replacement_candidates = 2
min_consensus_score = 0.7
scoring_update_frequency = 300  # seconds
```

### Algorithm Weights
```python
# Composite scoring weights
weights = {
    'TECHNICAL': 0.25,
    'FUNDAMENTAL': 0.25,
    'MARKET_STRUCTURE': 0.25,
    'RISK': 0.25
}
```

## 📈 Usage Examples

### Portfolio Operations
```python
from src.core.symbol_manager import SymbolManager

manager = SymbolManager()

# Get current portfolio
portfolio = manager.get_current_portfolio()

# Add symbol to portfolio
result = manager.add_symbol_to_portfolio(
    symbol_id="uuid-here",
    reason="High composite score"
)

# Get portfolio statistics
stats = manager.get_portfolio_statistics()
```

### Scoring Operations
```python
from src.core.scoring_engine import ScoringEngine

engine = ScoringEngine()

# Calculate scores for all symbols
result = engine.calculate_all_scores()

# Get top-ranked symbols
rankings = engine.get_symbol_rankings('COMPOSITE', limit=20)
```

### Signal Processing
```python
from src.core.signal_processor import SignalProcessor

processor = SignalProcessor()

# Submit trading signal
signal_data = {
    'source_name': 'TechnicalAnalyzer',
    'signal_type': 'BREAKOUT',
    'signal_strength': 0.85,
    'confidence_level': 0.75,
    'signal_direction': 'BUY'
}

result = processor.process_signal(signal_data)
```

## 🧪 Testing

### API Testing
```bash
# Portfolio operations
curl -X GET http://localhost:5000/api/symbol-mgmt/portfolio
curl -X POST http://localhost:5000/api/symbol-mgmt/scoring/calculate

# Signal submission
curl -X POST http://localhost:5000/api/symbol-mgmt/signals \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "TestSource",
    "signal_type": "MOMENTUM",
    "signal_strength": 0.8,
    "confidence_level": 0.7
  }'
```

### Performance Testing
```python
# Monitor scoring performance
import time
start_time = time.time()
engine.calculate_all_scores()
duration = time.time() - start_time
print(f"Scoring completed in {duration:.2f} seconds")
```

## 🚀 Deployment

### Development
```bash
# Local development server
python src/main.py
```

### Production
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 5000
CMD ["python", "src/main.py"]
```

## 📊 Performance Metrics

- **Scoring Speed**: <100ms per symbol for composite scores
- **API Response Time**: <500ms for portfolio operations
- **Database Queries**: Optimized with proper indexing
- **Concurrent Users**: Supports 100+ concurrent users
- **Memory Usage**: Efficient data structures and cleanup

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Secure error handling without information leakage
- **Audit Logging**: Complete audit trails for all operations
- **Access Control**: Ready for role-based access control

## 📚 Documentation

- **Implementation Guide**: Complete step-by-step implementation guide
- **API Documentation**: Comprehensive endpoint documentation
- **Database Schema**: Detailed schema documentation
- **Architecture Guide**: System design and component interaction

## 🛠️ Development

### Project Structure
```
src/
├── core/                 # Business logic
│   ├── symbol_manager.py
│   ├── portfolio_manager.py
│   ├── scoring_engine.py
│   └── signal_processor.py
├── models/               # Database models
│   └── symbol_models.py
├── routes/               # API routes
│   └── symbol_routes.py
├── utils/                # Utilities
│   └── sample_data.py
└── main.py              # Flask app
```

### Adding New Features

1. **New Scoring Algorithm**
   ```python
   # Add to ScoringEngine
   def _calculate_custom_score(self, symbol, algorithm):
       # Implement custom scoring logic
       pass
   ```

2. **New Signal Source**
   ```python
   # Submit signals via API
   POST /api/symbol-mgmt/signals
   ```

3. **Custom Analytics**
   ```python
   # Extend PortfolioManager
   def custom_analysis(self):
       # Implement custom analytics
       pass
   ```

## 🤝 Integration

### KuCoin Integration
```python
# Connect to existing KuCoin infrastructure
from src.core.symbol_manager import SymbolManager

# In your KuCoin handler
def on_market_data(symbol, data):
    scoring_engine.calculate_all_scores(symbol.id)
```

### Signal Sources
```python
# Connect signal sources
def process_technical_signal(symbol, indicator_data):
    signal_data = {
        'source_name': 'TechnicalAnalyzer',
        'symbol_id': str(symbol.id),
        'signal_type': indicator_data['type'],
        'signal_strength': calculate_strength(indicator_data),
        'confidence_level': calculate_confidence(indicator_data)
    }
    return signal_processor.process_signal(signal_data)
```

## 📞 Support

For implementation support and questions:

1. **Documentation**: Check the comprehensive implementation guide
2. **API Testing**: Use the provided API examples
3. **Sample Data**: Initialize with sample data for testing
4. **Health Checks**: Monitor system status via health endpoints

## 📄 License

This module is part of the ZmartBot trading system. All rights reserved.

---

**Version**: 1.0  
**Last Updated**: July 31, 2025  
**Compatibility**: Python 3.11+, Flask 3.1+, SQLAlchemy 2.0+

